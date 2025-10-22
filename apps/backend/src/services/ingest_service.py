# apps/backend/src/services/ingest.py
from sqlmodel import Session, select
from typing import List, Dict
import hashlib
import logging
from datetime import datetime

from src.services.gmail_client import GmailClient
from src.services.parser import TransactionParser
from src.models.models import Transaction, TransactionSource, Account
from src.core.errors import ValidationError

logger = logging.getLogger(__name__)

class IngestService:
    def __init__(self, session: Session):
        self.session = session
        self.parser = TransactionParser()
    
    def process_emails(
        self, 
        user_id: str, 
        gmail_credentials: Dict,
        history_id: Optional[str] = None
    ) -> Dict:
        """Process emails and create transactions"""
        gmail_client = GmailClient(gmail_credentials)
        
        # Fetch messages
        messages = gmail_client.get_messages(history_id=history_id)
        logger.info(f"Fetched {len(messages)} messages for user {user_id}")
        
        stats = {
            'processed': 0,
            'created': 0,
            'duplicates': 0,
            'failed': 0
        }
        
        for message in messages:
            stats['processed'] += 1
            
            try:
                # Parse message
                email_data = gmail_client.parse_message(message)
                txn_data = self.parser.parse_email(email_data)
                
                if not txn_data:
                    logger.debug(f"Could not parse message {message['id']}")
                    continue
                
                # Create transaction
                created = self._create_transaction(user_id, txn_data, email_data)
                
                if created:
                    stats['created'] += 1
                else:
                    stats['duplicates'] += 1
                    
            except Exception as e:
                logger.error(f"Error processing message {message.get('id')}: {e}")
                stats['failed'] += 1
        
        # Update history_id for next sync
        try:
            new_history_id = gmail_client.get_latest_history_id()
            logger.info(f"New history_id: {new_history_id}")
        except Exception as e:
            logger.error(f"Could not get history_id: {e}")
            new_history_id = None
        
        return {
            **stats,
            'history_id': new_history_id
        }
    
    def _create_transaction(
        self, 
        user_id: str, 
        txn_data: Dict,
        email_data: Dict
    ) -> bool:
        """Create transaction from parsed data with deduplication"""
        # Get or create default account for this provider
        account = self._get_or_create_account(user_id, txn_data['provider'])
        
        # Generate dedupe hash
        hash_input = (
            f"{txn_data['date']}|"
            f"{txn_data['amount']}|"
            f"{txn_data.get('merchant', '')}|"
            f"{txn_data.get('card_tail', '')}|"
            f"{txn_data['provider']}"
        )
        hash_dedupe = hashlib.sha256(hash_input.encode()).hexdigest()
        
        # Check for duplicate
        existing = self.session.exec(
            select(Transaction).where(Transaction.hash_dedupe == hash_dedupe)
        ).first()
        
        if existing:
            logger.debug(f"Duplicate transaction: {hash_dedupe}")
            return False
        
        # Create transaction
        txn = Transaction(
            user_id=user_id,
            account_id=account.id,
            txn_date=txn_data['date'] or datetime.utcnow().date(),
            amount=txn_data['amount'],
            currency='CLP',
            description=txn_data['description'],
            merchant=txn_data.get('merchant'),
            source=TransactionSource.EMAIL,
            payment_method=txn_data.get('card_tail'),
            hash_dedupe=hash_dedupe,
            raw_payload={
                'email_id': email_data['message_id'],
                'subject': email_data['subject'],
                'from': email_data['from']
            }
        )
        
        self.session.add(txn)
        self.session.commit()
        
        logger.info(f"Created transaction: {txn.id} for {txn.amount} CLP")
        return True
    
    def _get_or_create_account(self, user_id: str, provider: str) -> Account:
        """Get or create account for provider"""
        account = self.session.exec(
            select(Account).where(
                Account.user_id == user_id,
                Account.institution == provider
            )
        ).first()
        
        if not account:
            account = Account(
                user_id=user_id,
                name=f"Cuenta {provider}",
                institution=provider,
                type="credit",
                currency="CLP"
            )
            self.session.add(account)
            self.session.commit()
            self.session.refresh(account)
            logger.info(f"Created account for provider {provider}")
        
        return account
