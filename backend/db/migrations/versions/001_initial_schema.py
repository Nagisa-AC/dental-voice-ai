"""Initial database schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2025-01-24 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Create initial database schema with all tables."""
    
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create refresh_tokens table
    op.create_table('refresh_tokens',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('token_hash', sa.String(length=255), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_revoked', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token_hash')
    )
    
    # Create clinics table
    op.create_table('clinics',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('industry_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('address', sa.Text(), nullable=False),
        sa.Column('website', sa.String(length=200), nullable=True),
        sa.Column('business_hours', sa.JSON(), nullable=True),
        sa.Column('services', sa.JSON(), nullable=True),
        sa.Column('policies', sa.JSON(), nullable=True),
        sa.Column('vapi_assistant_id', sa.String(length=100), nullable=True),
        sa.Column('assistant_config', sa.JSON(), nullable=True),
        sa.Column('faq_content', sa.Text(), nullable=True),
        sa.Column('faq_filename', sa.String(length=255), nullable=True),
        sa.Column('admin_notes', sa.Text(), nullable=True),
        sa.Column('approved_by', sa.String(), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id')
    )
    
    # Create assistants table
    op.create_table('assistants',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('clinic_id', sa.String(), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('vapi_assistant_id', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('model_id', sa.String(length=50), nullable=False),
        sa.Column('voice_id', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('config', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['clinic_id'], ['clinics.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('vapi_assistant_id')
    )
    
    # Create audit_logs table
    op.create_table('audit_logs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('clinic_id', sa.String(), nullable=True),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=False),
        sa.Column('resource_id', sa.String(length=100), nullable=True),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('request_id', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['clinic_id'], ['clinics.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create file_uploads table
    op.create_table('file_uploads',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('clinic_id', sa.String(), nullable=True),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('secure_filename', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('file_hash', sa.String(length=64), nullable=False),
        sa.Column('file_type', sa.String(length=50), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('is_quarantined', sa.Boolean(), nullable=False),
        sa.Column('quarantine_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['clinic_id'], ['clinics.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('secure_filename')
    )
    
    # Create csrf_tokens table
    op.create_table('csrf_tokens',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('token_hash', sa.String(length=255), nullable=False),
        sa.Column('is_used', sa.Boolean(), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('used_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token_hash')
    )
    
    # Create rate_limits table
    op.create_table('rate_limits',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('key', sa.String(length=255), nullable=False),
        sa.Column('endpoint', sa.String(length=200), nullable=False),
        sa.Column('method', sa.String(length=10), nullable=False),
        sa.Column('count', sa.Integer(), nullable=False),
        sa.Column('window_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('window_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for users table
    op.create_index('idx_users_email_active', 'users', ['email', 'is_active'])
    op.create_index('idx_users_role_active', 'users', ['role', 'is_active'])
    op.create_index('idx_users_tenant_active', 'users', ['tenant_id', 'is_active'])
    op.create_index('idx_users_created_at', 'users', ['created_at'])
    op.create_index('idx_users_last_login', 'users', ['last_login'])
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_index(op.f('ix_users_role'), 'users', ['role'])
    op.create_index(op.f('ix_users_tenant_id'), 'users', ['tenant_id'])
    
    # Create indexes for refresh_tokens table
    op.create_index('idx_refresh_tokens_user_expires', 'refresh_tokens', ['user_id', 'expires_at'])
    op.create_index('idx_refresh_tokens_expires_revoked', 'refresh_tokens', ['expires_at', 'is_revoked'])
    op.create_index('idx_refresh_tokens_token_hash', 'refresh_tokens', ['token_hash'])
    op.create_index('idx_refresh_tokens_created_at', 'refresh_tokens', ['created_at'])
    op.create_index(op.f('ix_refresh_tokens_user_id'), 'refresh_tokens', ['user_id'])
    op.create_index(op.f('ix_refresh_tokens_expires_at'), 'refresh_tokens', ['expires_at'])
    op.create_index(op.f('ix_refresh_tokens_is_revoked'), 'refresh_tokens', ['is_revoked'])
    op.create_index(op.f('ix_refresh_tokens_token_hash'), 'refresh_tokens', ['token_hash'], unique=True)
    
    # Create indexes for clinics table
    op.create_index('idx_clinics_tenant_status', 'clinics', ['tenant_id', 'status'])
    op.create_index('idx_clinics_industry_status', 'clinics', ['industry_type', 'status'])
    op.create_index('idx_clinics_phone_email', 'clinics', ['phone', 'email'])
    op.create_index('idx_clinics_created_status', 'clinics', ['created_at', 'status'])
    op.create_index('idx_clinics_updated_at', 'clinics', ['updated_at'])
    op.create_index('idx_clinics_approved_by', 'clinics', ['approved_by'])
    op.create_index('idx_clinics_vapi_assistant_id', 'clinics', ['vapi_assistant_id'])
    op.create_index(op.f('ix_clinics_tenant_id'), 'clinics', ['tenant_id'], unique=True)
    op.create_index(op.f('ix_clinics_name'), 'clinics', ['name'])
    op.create_index(op.f('ix_clinics_industry_type'), 'clinics', ['industry_type'])
    op.create_index(op.f('ix_clinics_status'), 'clinics', ['status'])
    op.create_index(op.f('ix_clinics_phone'), 'clinics', ['phone'])
    op.create_index(op.f('ix_clinics_email'), 'clinics', ['email'])
    op.create_index(op.f('ix_clinics_vapi_assistant_id'), 'clinics', ['vapi_assistant_id'])
    
    # Create indexes for assistants table
    op.create_index('idx_assistants_clinic_status', 'assistants', ['clinic_id', 'status'])
    op.create_index('idx_assistants_tenant_status', 'assistants', ['tenant_id', 'status'])
    op.create_index('idx_assistants_vapi_id', 'assistants', ['vapi_assistant_id'])
    op.create_index('idx_assistants_created', 'assistants', ['created_at'])
    op.create_index('idx_assistants_updated_at', 'assistants', ['updated_at'])
    op.create_index('idx_assistants_name', 'assistants', ['name'])
    op.create_index(op.f('ix_assistants_clinic_id'), 'assistants', ['clinic_id'])
    op.create_index(op.f('ix_assistants_tenant_id'), 'assistants', ['tenant_id'])
    op.create_index(op.f('ix_assistants_vapi_assistant_id'), 'assistants', ['vapi_assistant_id'], unique=True)
    op.create_index(op.f('ix_assistants_name'), 'assistants', ['name'])
    op.create_index(op.f('ix_assistants_status'), 'assistants', ['status'])
    
    # Create indexes for audit_logs table
    op.create_index('idx_audit_logs_user_action', 'audit_logs', ['user_id', 'action'])
    op.create_index('idx_audit_logs_clinic_action', 'audit_logs', ['clinic_id', 'action'])
    op.create_index('idx_audit_logs_resource', 'audit_logs', ['resource_type', 'resource_id'])
    op.create_index('idx_audit_logs_created_action', 'audit_logs', ['created_at', 'action'])
    op.create_index('idx_audit_logs_ip_created', 'audit_logs', ['ip_address', 'created_at'])
    op.create_index('idx_audit_logs_user_created', 'audit_logs', ['user_id', 'created_at'])
    op.create_index('idx_audit_logs_clinic_created', 'audit_logs', ['clinic_id', 'created_at'])
    op.create_index('idx_audit_logs_action_resource', 'audit_logs', ['action', 'resource_type'])
    op.create_index(op.f('ix_audit_logs_user_id'), 'audit_logs', ['user_id'])
    op.create_index(op.f('ix_audit_logs_clinic_id'), 'audit_logs', ['clinic_id'])
    op.create_index(op.f('ix_audit_logs_action'), 'audit_logs', ['action'])
    op.create_index(op.f('ix_audit_logs_resource_type'), 'audit_logs', ['resource_type'])
    op.create_index(op.f('ix_audit_logs_resource_id'), 'audit_logs', ['resource_id'])
    op.create_index(op.f('ix_audit_logs_ip_address'), 'audit_logs', ['ip_address'])
    op.create_index(op.f('ix_audit_logs_request_id'), 'audit_logs', ['request_id'])
    op.create_index(op.f('ix_audit_logs_created_at'), 'audit_logs', ['created_at'])
    
    # Create indexes for file_uploads table
    op.create_index('idx_file_uploads_user_status', 'file_uploads', ['user_id', 'status'])
    op.create_index('idx_file_uploads_clinic_status', 'file_uploads', ['clinic_id', 'status'])
    op.create_index('idx_file_uploads_hash', 'file_uploads', ['file_hash'])
    op.create_index('idx_file_uploads_type_status', 'file_uploads', ['file_type', 'status'])
    op.create_index('idx_file_uploads_quarantined', 'file_uploads', ['is_quarantined', 'created_at'])
    op.create_index(op.f('ix_file_uploads_user_id'), 'file_uploads', ['user_id'])
    op.create_index(op.f('ix_file_uploads_clinic_id'), 'file_uploads', ['clinic_id'])
    op.create_index(op.f('ix_file_uploads_secure_filename'), 'file_uploads', ['secure_filename'], unique=True)
    op.create_index(op.f('ix_file_uploads_file_hash'), 'file_uploads', ['file_hash'])
    op.create_index(op.f('ix_file_uploads_file_type'), 'file_uploads', ['file_type'])
    op.create_index(op.f('ix_file_uploads_status'), 'file_uploads', ['status'])
    op.create_index(op.f('ix_file_uploads_is_quarantined'), 'file_uploads', ['is_quarantined'])
    
    # Create indexes for csrf_tokens table
    op.create_index('idx_csrf_tokens_user_expires', 'csrf_tokens', ['user_id', 'expires_at'])
    op.create_index('idx_csrf_tokens_expires_used', 'csrf_tokens', ['expires_at', 'is_used'])
    op.create_index('idx_csrf_tokens_created', 'csrf_tokens', ['created_at'])
    op.create_index(op.f('ix_csrf_tokens_user_id'), 'csrf_tokens', ['user_id'])
    op.create_index(op.f('ix_csrf_tokens_token_hash'), 'csrf_tokens', ['token_hash'], unique=True)
    op.create_index(op.f('ix_csrf_tokens_is_used'), 'csrf_tokens', ['is_used'])
    op.create_index(op.f('ix_csrf_tokens_expires_at'), 'csrf_tokens', ['expires_at'])
    
    # Create indexes for rate_limits table
    op.create_index('idx_rate_limits_key_endpoint', 'rate_limits', ['key', 'endpoint'])
    op.create_index('idx_rate_limits_window', 'rate_limits', ['window_start', 'window_end'])
    op.create_index('idx_rate_limits_created', 'rate_limits', ['created_at'])
    op.create_index(op.f('ix_rate_limits_key'), 'rate_limits', ['key'])
    op.create_index(op.f('ix_rate_limits_endpoint'), 'rate_limits', ['endpoint'])
    op.create_index(op.f('ix_rate_limits_method'), 'rate_limits', ['method'])
    op.create_index(op.f('ix_rate_limits_window_start'), 'rate_limits', ['window_start'])
    op.create_index(op.f('ix_rate_limits_window_end'), 'rate_limits', ['window_end'])


def downgrade():
    """Drop all tables and indexes."""
    
    # Drop indexes first
    op.drop_index(op.f('ix_rate_limits_window_end'), table_name='rate_limits')
    op.drop_index(op.f('ix_rate_limits_window_start'), table_name='rate_limits')
    op.drop_index(op.f('ix_rate_limits_method'), table_name='rate_limits')
    op.drop_index(op.f('ix_rate_limits_endpoint'), table_name='rate_limits')
    op.drop_index(op.f('ix_rate_limits_key'), table_name='rate_limits')
    op.drop_index('idx_rate_limits_created', table_name='rate_limits')
    op.drop_index('idx_rate_limits_window', table_name='rate_limits')
    op.drop_index('idx_rate_limits_key_endpoint', table_name='rate_limits')
    
    op.drop_index(op.f('ix_csrf_tokens_expires_at'), table_name='csrf_tokens')
    op.drop_index(op.f('ix_csrf_tokens_is_used'), table_name='csrf_tokens')
    op.drop_index(op.f('ix_csrf_tokens_token_hash'), table_name='csrf_tokens')
    op.drop_index(op.f('ix_csrf_tokens_user_id'), table_name='csrf_tokens')
    op.drop_index('idx_csrf_tokens_created', table_name='csrf_tokens')
    op.drop_index('idx_csrf_tokens_expires_used', table_name='csrf_tokens')
    op.drop_index('idx_csrf_tokens_user_expires', table_name='csrf_tokens')
    
    op.drop_index(op.f('ix_file_uploads_is_quarantined'), table_name='file_uploads')
    op.drop_index(op.f('ix_file_uploads_status'), table_name='file_uploads')
    op.drop_index(op.f('ix_file_uploads_file_type'), table_name='file_uploads')
    op.drop_index(op.f('ix_file_uploads_file_hash'), table_name='file_uploads')
    op.drop_index(op.f('ix_file_uploads_secure_filename'), table_name='file_uploads')
    op.drop_index(op.f('ix_file_uploads_clinic_id'), table_name='file_uploads')
    op.drop_index(op.f('ix_file_uploads_user_id'), table_name='file_uploads')
    op.drop_index('idx_file_uploads_quarantined', table_name='file_uploads')
    op.drop_index('idx_file_uploads_type_status', table_name='file_uploads')
    op.drop_index('idx_file_uploads_hash', table_name='file_uploads')
    op.drop_index('idx_file_uploads_clinic_status', table_name='file_uploads')
    op.drop_index('idx_file_uploads_user_status', table_name='file_uploads')
    
    op.drop_index(op.f('ix_audit_logs_created_at'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_request_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_ip_address'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_resource_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_resource_type'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_action'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_clinic_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_audit_logs_user_id'), table_name='audit_logs')
    op.drop_index('idx_audit_logs_action_resource', table_name='audit_logs')
    op.drop_index('idx_audit_logs_clinic_created', table_name='audit_logs')
    op.drop_index('idx_audit_logs_user_created', table_name='audit_logs')
    op.drop_index('idx_audit_logs_ip_created', table_name='audit_logs')
    op.drop_index('idx_audit_logs_created_action', table_name='audit_logs')
    op.drop_index('idx_audit_logs_resource', table_name='audit_logs')
    op.drop_index('idx_audit_logs_clinic_action', table_name='audit_logs')
    op.drop_index('idx_audit_logs_user_action', table_name='audit_logs')
    
    op.drop_index(op.f('ix_assistants_status'), table_name='assistants')
    op.drop_index(op.f('ix_assistants_name'), table_name='assistants')
    op.drop_index(op.f('ix_assistants_vapi_assistant_id'), table_name='assistants')
    op.drop_index(op.f('ix_assistants_tenant_id'), table_name='assistants')
    op.drop_index(op.f('ix_assistants_clinic_id'), table_name='assistants')
    op.drop_index('idx_assistants_name', table_name='assistants')
    op.drop_index('idx_assistants_updated_at', table_name='assistants')
    op.drop_index('idx_assistants_created', table_name='assistants')
    op.drop_index('idx_assistants_vapi_id', table_name='assistants')
    op.drop_index('idx_assistants_tenant_status', table_name='assistants')
    op.drop_index('idx_assistants_clinic_status', table_name='assistants')
    
    op.drop_index(op.f('ix_clinics_vapi_assistant_id'), table_name='clinics')
    op.drop_index(op.f('ix_clinics_email'), table_name='clinics')
    op.drop_index(op.f('ix_clinics_phone'), table_name='clinics')
    op.drop_index(op.f('ix_clinics_status'), table_name='clinics')
    op.drop_index(op.f('ix_clinics_industry_type'), table_name='clinics')
    op.drop_index(op.f('ix_clinics_name'), table_name='clinics')
    op.drop_index(op.f('ix_clinics_tenant_id'), table_name='clinics')
    op.drop_index('idx_clinics_vapi_assistant_id', table_name='clinics')
    op.drop_index('idx_clinics_approved_by', table_name='clinics')
    op.drop_index('idx_clinics_updated_at', table_name='clinics')
    op.drop_index('idx_clinics_created_status', table_name='clinics')
    op.drop_index('idx_clinics_phone_email', table_name='clinics')
    op.drop_index('idx_clinics_industry_status', table_name='clinics')
    op.drop_index('idx_clinics_tenant_status', table_name='clinics')
    
    op.drop_index(op.f('ix_refresh_tokens_token_hash'), table_name='refresh_tokens')
    op.drop_index(op.f('ix_refresh_tokens_expires_at'), table_name='refresh_tokens')
    op.drop_index(op.f('ix_refresh_tokens_is_revoked'), table_name='refresh_tokens')
    op.drop_index(op.f('ix_refresh_tokens_user_id'), table_name='refresh_tokens')
    op.drop_index('idx_refresh_tokens_created_at', table_name='refresh_tokens')
    op.drop_index('idx_refresh_tokens_token_hash', table_name='refresh_tokens')
    op.drop_index('idx_refresh_tokens_expires_revoked', table_name='refresh_tokens')
    op.drop_index('idx_refresh_tokens_user_expires', table_name='refresh_tokens')
    
    op.drop_index(op.f('ix_users_tenant_id'), table_name='users')
    op.drop_index(op.f('ix_users_role'), table_name='users')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index('idx_users_last_login', table_name='users')
    op.drop_index('idx_users_created_at', table_name='users')
    op.drop_index('idx_users_tenant_active', table_name='users')
    op.drop_index('idx_users_role_active', table_name='users')
    op.drop_index('idx_users_email_active', table_name='users')
    
    # Drop tables
    op.drop_table('rate_limits')
    op.drop_table('csrf_tokens')
    op.drop_table('file_uploads')
    op.drop_table('audit_logs')
    op.drop_table('assistants')
    op.drop_table('clinics')
    op.drop_table('refresh_tokens')
    op.drop_table('users')
