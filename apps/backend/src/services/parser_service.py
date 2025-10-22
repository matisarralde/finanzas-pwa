# apps/backend/src/services/parser.py
import re
import yaml
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TransactionParser:
    def __init__(self):
        self.providers = self._load_providers()
    
    def _load_providers(self) -> Dict:
        """Load provider configurations from YAML files"""
        providers = {}
        providers_dir = Path(__file__).parent.parent / "providers"
        
        if not providers_dir.exists():
            logger.warning(f"Providers directory not found: {providers_dir}")
            return providers
        
        for yaml_file in providers_dir.glob("*.yaml"):
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    provider_name = yaml_file.stem
                    providers[provider_name] = config
                    logger.info(f"Loaded provider config: {provider_name}")
            except Exception as e:
                logger.error(f"Error loading {yaml_file}: {e}")
        
        return providers
    
    def parse_email(self, email_data: Dict) -> Optional[Dict]:
        """Parse email and extract transaction data"""
        subject = email_data.get('subject', '')
        body = email_data.get('body', '')
        from_addr = email_data.get('from', '').lower()
        
        # Try each provider
        for provider_name, config in self.providers.items():
            if self._matches_provider(from_addr, subject, config):
                return self._extract_transaction(subject, body, config, provider_name)
        
        logger.debug(f"No provider matched for email from {from_addr}")
        return None
    
    def _matches_provider(self, from_addr: str, subject: str, config: Dict) -> bool:
        """Check if email matches provider patterns"""
        # Check sender domain
        sender_patterns = config.get('sender_patterns', [])
        if not any(re.search(pattern, from_addr) for pattern in sender_patterns):
            return False
        
        # Check subject pattern
        subject_patterns = config.get('subject_patterns', [])
        if subject_patterns and not any(re.search(pattern, subject, re.IGNORECASE) for pattern in subject_patterns):
            return False
        
        return True
    
    def _extract_transaction(self, subject: str, body: str, config: Dict, provider: str) -> Optional[Dict]:
        """Extract transaction details from email content"""
        text = f"{subject}\n{body}"
        
        # Extract amount (CLP)
        amount = None
        amount_patterns = config.get('amount_patterns', [])
        for pattern in amount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace('.', '').replace(',', '.')
                try:
                    amount = float(amount_str)
                    break
                except ValueError:
                    continue
        
        if not amount:
            logger.debug(f"Could not extract amount from {provider}")
            return None
        
        # Extract date
        txn_date = None
        date_patterns = config.get('date_patterns', [])
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    date_str = match.group(1)
                    # Try multiple date formats
                    for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d']:
                        try:
                            txn_date = datetime.strptime(date_str, fmt).date()
                            break
                        except ValueError:
                            continue
                    if txn_date:
                        break
                except Exception as e:
                    logger.debug(f"Error parsing date: {e}")
                    continue
        
        # Extract merchant
        merchant = None
        merchant_patterns = config.get('merchant_patterns', [])
        for pattern in merchant_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                merchant = match.group(1).strip()
                break
        
        # Extract card tail (last 4 digits)
        card_tail = None
        card_patterns = config.get('card_patterns', [])
        for pattern in card_patterns:
            match = re.search(pattern, text)
            if match:
                card_tail = match.group(1)
                break
        
        return {
            'amount': amount,
            'date': txn_date,
            'merchant': merchant,
            'card_tail': card_tail,
            'provider': provider,
            'description': subject[:200]
        }
    
