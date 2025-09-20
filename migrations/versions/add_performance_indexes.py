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
    
    # Users table indexes
    op.create_index('idx_users_created_at', 'users', ['created_at'])
    op.create_index('idx_users_last_login', 'users', ['last_login'])
    
    # Refresh tokens indexes
    op.create_index('idx_refresh_tokens_token_hash', 'refresh_tokens', ['token_hash'])
    op.create_index('idx_refresh_tokens_created_at', 'refresh_tokens', ['created_at'])
    
    # Clinics table indexes
    op.create_index('idx_clinics_updated_at', 'clinics', ['updated_at'])
    op.create_index('idx_clinics_approved_by', 'clinics', ['approved_by'])
    op.create_index('idx_clinics_vapi_assistant_id', 'clinics', ['vapi_assistant_id'])
    
    # Assistants table indexes
    op.create_index('idx_assistants_updated_at', 'assistants', ['updated_at'])
    op.create_index('idx_assistants_name', 'assistants', ['name'])
    
    # Audit logs indexes for HIPAA compliance
    op.create_index('idx_audit_logs_user_created', 'audit_logs', ['user_id', 'created_at'])
    op.create_index('idx_audit_logs_clinic_created', 'audit_logs', ['clinic_id', 'created_at'])
    op.create_index('idx_audit_logs_action_resource', 'audit_logs', ['action', 'resource_type'])
    
    # File uploads indexes
    op.create_index('idx_file_uploads_user_created', 'file_uploads', ['user_id', 'created_at'])
    op.create_index('idx_file_uploads_clinic_created', 'file_uploads', ['clinic_id', 'created_at'])
    op.create_index('idx_file_uploads_status_created', 'file_uploads', ['status', 'created_at'])


def downgrade():
    """Remove performance indexes."""
    
    # Users table indexes
    op.drop_index('idx_users_created_at', table_name='users')
    op.drop_index('idx_users_last_login', table_name='users')
    
    # Refresh tokens indexes
    op.drop_index('idx_refresh_tokens_token_hash', table_name='refresh_tokens')
    op.drop_index('idx_refresh_tokens_created_at', table_name='refresh_tokens')
    
    # Clinics table indexes
    op.drop_index('idx_clinics_updated_at', table_name='clinics')
    op.drop_index('idx_clinics_approved_by', table_name='clinics')
    op.drop_index('idx_clinics_vapi_assistant_id', table_name='clinics')
    
    # Assistants table indexes
    op.drop_index('idx_assistants_updated_at', table_name='assistants')
    op.drop_index('idx_assistants_name', table_name='assistants')
    
    # Audit logs indexes
    op.drop_index('idx_audit_logs_user_created', table_name='audit_logs')
    op.drop_index('idx_audit_logs_clinic_created', table_name='audit_logs')
    op.drop_index('idx_audit_logs_action_resource', table_name='audit_logs')
    
    # File uploads indexes
    op.drop_index('idx_file_uploads_user_created', table_name='file_uploads')
    op.drop_index('idx_file_uploads_clinic_created', table_name='file_uploads')
    op.drop_index('idx_file_uploads_status_created', table_name='file_uploads')
