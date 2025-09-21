"""Add performance indexes for database optimization

Revision ID: add_performance_indexes
Revises: 
Create Date: 2025-01-24 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_performance_indexes'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Add performance indexes for better query performance."""
    
    # Users table indexes (only for existing columns)
    op.create_index('idx_users_created_at', 'users', ['created_at'])
    op.create_index('idx_users_last_login', 'users', ['last_login'])
    
    # Refresh tokens indexes (only for existing columns)
    op.create_index('idx_refresh_tokens_created_at', 'refresh_tokens', ['created_at'])
    
    # Audit logs indexes for HIPAA compliance (only for existing columns)
    op.create_index('idx_audit_logs_user_timestamp', 'audit_logs', ['user_id', 'timestamp'])
    op.create_index('idx_audit_logs_action_resource', 'audit_logs', ['action', 'resource_type'])


def downgrade():
    """Remove performance indexes."""
    
    # Users table indexes
    op.drop_index('idx_users_created_at', table_name='users')
    op.drop_index('idx_users_last_login', table_name='users')
    
    # Refresh tokens indexes
    op.drop_index('idx_refresh_tokens_created_at', table_name='refresh_tokens')
    
    # Audit logs indexes
    op.drop_index('idx_audit_logs_user_timestamp', table_name='audit_logs')
    op.drop_index('idx_audit_logs_action_resource', table_name='audit_logs')
