# apps/backend/alembic/versions/001_initial_schema.py
"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2025-01-15 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('ix_users_email', 'users', ['email'])
    
    # Categories table
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['parent_id'], ['categories.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_categories_user_id', 'categories', ['user_id'])
    
    # Accounts table
    op.create_table(
        'accounts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('institution', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('currency', sa.String(), nullable=False),
        sa.Column('last_sync_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_accounts_user_id', 'accounts', ['user_id'])
    
    # Budgets table
    op.create_table(
        'budgets',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('period', sa.String(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('start_month', sa.Date(), nullable=False),
        sa.Column('end_month', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_budgets_user_id', 'budgets', ['user_id'])
    
    # Transactions table
    op.create_table(
        'transactions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('account_id', sa.Integer(), nullable=False),
        sa.Column('txn_date', sa.Date(), nullable=False),
        sa.Column('posted_at', sa.DateTime(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('raw_payload', postgresql.JSONB(), nullable=True),
        sa.Column('source', sa.String(), nullable=False),
        sa.Column('merchant', sa.String(), nullable=True),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('subcategory_id', sa.Integer(), nullable=True),
        sa.Column('payment_method', sa.String(), nullable=True),
        sa.Column('is_transfer', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('hash_dedupe', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id']),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id']),
        sa.ForeignKeyConstraint(['subcategory_id'], ['categories.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('hash_dedupe')
    )
    op.create_index('ix_transactions_user_id', 'transactions', ['user_id'])
    op.create_index('ix_transactions_account_id', 'transactions', ['account_id'])
    op.create_index('ix_transactions_txn_date', 'transactions', ['txn_date'])
    op.create_index('ix_transactions_category_id', 'transactions', ['category_id'])
    op.create_index('ix_transactions_hash_dedupe', 'transactions', ['hash_dedupe'])
    op.create_index('ix_transactions_created_at', 'transactions', ['created_at'])
    
    # Rules table
    op.create_table(
        'rules',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('pattern', sa.String(), nullable=False),
        sa.Column('field', sa.String(), nullable=False),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('value', sa.String(), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_rules_user_id', 'rules', ['user_id'])

def downgrade() -> None:
    op.drop_table('rules')
    op.drop_table('transactions')
    op.drop_table('budgets')
    op.drop_table('accounts')
    op.drop_table('categories')
    op.drop_table('users')
