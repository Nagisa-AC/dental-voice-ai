"""
Database Migration: Add Encryption Support

This migration adds encryption support for sensitive data fields.
Note: This is a complex migration that requires careful handling of existing data.
"""

import logging
from typing import Dict, Any
from sqlalchemy import text
from alembic import op
import sqlalchemy as sa

from .services.encryption_service import encryption_service

logger = logging.getLogger(__name__)


def upgrade():
    """
    Upgrade database to support encryption.
    
    This migration:
    1. Adds new encrypted columns
    2. Migrates existing data to encrypted format
    3. Drops old unencrypted columns
    """
    logger.info("Starting encryption support migration")
    
    # Add new encrypted columns to users table
    op.add_column('users', sa.Column('email_encrypted', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('password_hash_encrypted', sa.Text(), nullable=True))
    
    # Add new encrypted columns to clinics table
    op.add_column('clinics', sa.Column('phone_encrypted', sa.Text(), nullable=True))
    op.add_column('clinics', sa.Column('email_encrypted', sa.Text(), nullable=True))
    op.add_column('clinics', sa.Column('address_encrypted', sa.Text(), nullable=True))
    op.add_column('clinics', sa.Column('assistant_config_encrypted', sa.Text(), nullable=True))
    op.add_column('clinics', sa.Column('faq_content_encrypted', sa.Text(), nullable=True))
    op.add_column('clinics', sa.Column('admin_notes_encrypted', sa.Text(), nullable=True))
    
    # Migrate existing data to encrypted format
    migrate_users_data()
    migrate_clinics_data()
    
    # Drop old unencrypted columns
    op.drop_column('users', 'email')
    op.drop_column('users', 'password_hash')
    op.drop_column('clinics', 'phone')
    op.drop_column('clinics', 'email')
    op.drop_column('clinics', 'address')
    op.drop_column('clinics', 'assistant_config')
    op.drop_column('clinics', 'faq_content')
    op.drop_column('clinics', 'admin_notes')
    
    # Rename encrypted columns to original names
    op.alter_column('users', 'email_encrypted', new_column_name='email')
    op.alter_column('users', 'password_hash_encrypted', new_column_name='password_hash')
    op.alter_column('clinics', 'phone_encrypted', new_column_name='phone')
    op.alter_column('clinics', 'email_encrypted', new_column_name='email')
    op.alter_column('clinics', 'address_encrypted', new_column_name='address')
    op.alter_column('clinics', 'assistant_config_encrypted', new_column_name='assistant_config')
    op.alter_column('clinics', 'faq_content_encrypted', new_column_name='faq_content')
    op.alter_column('clinics', 'admin_notes_encrypted', new_column_name='admin_notes')
    
    logger.info("Encryption support migration completed")


def downgrade():
    """
    Downgrade database to remove encryption support.
    
    WARNING: This will decrypt all data and remove encryption.
    This should only be used for development/testing.
    """
    logger.warning("Downgrading encryption support - this will decrypt all data")
    
    # Add back unencrypted columns
    op.add_column('users', sa.Column('email_unencrypted', sa.String(100), nullable=True))
    op.add_column('users', sa.Column('password_hash_unencrypted', sa.String(255), nullable=True))
    op.add_column('clinics', sa.Column('phone_unencrypted', sa.String(20), nullable=True))
    op.add_column('clinics', sa.Column('email_unencrypted', sa.String(100), nullable=True))
    op.add_column('clinics', sa.Column('address_unencrypted', sa.Text(), nullable=True))
    op.add_column('clinics', sa.Column('assistant_config_unencrypted', sa.JSON(), nullable=True))
    op.add_column('clinics', sa.Column('faq_content_unencrypted', sa.Text(), nullable=True))
    op.add_column('clinics', sa.Column('admin_notes_unencrypted', sa.Text(), nullable=True))
    
    # Decrypt and migrate data back
    decrypt_users_data()
    decrypt_clinics_data()
    
    # Drop encrypted columns
    op.drop_column('users', 'email')
    op.drop_column('users', 'password_hash')
    op.drop_column('clinics', 'phone')
    op.drop_column('clinics', 'email')
    op.drop_column('clinics', 'address')
    op.drop_column('clinics', 'assistant_config')
    op.drop_column('clinics', 'faq_content')
    op.drop_column('clinics', 'admin_notes')
    
    # Rename unencrypted columns back to original names
    op.alter_column('users', 'email_unencrypted', new_column_name='email')
    op.alter_column('users', 'password_hash_unencrypted', new_column_name='password_hash')
    op.alter_column('clinics', 'phone_unencrypted', new_column_name='phone')
    op.alter_column('clinics', 'email_unencrypted', new_column_name='email')
    op.alter_column('clinics', 'address_unencrypted', new_column_name='address')
    op.alter_column('clinics', 'assistant_config_unencrypted', new_column_name='assistant_config')
    op.alter_column('clinics', 'faq_content_unencrypted', new_column_name='faq_content')
    op.alter_column('clinics', 'admin_notes_unencrypted', new_column_name='admin_notes')
    
    logger.info("Encryption support downgrade completed")


def migrate_users_data():
    """Migrate users data to encrypted format."""
    logger.info("Migrating users data to encrypted format")
    
    connection = op.get_bind()
    
    # Get all users
    users = connection.execute(text("SELECT id, email, password_hash FROM users")).fetchall()
    
    for user in users:
        user_id, email, password_hash = user
        
        try:
            # Encrypt email and password hash
            encrypted_email = encryption_service.encrypt_field(email, 'email') if email else None
            encrypted_password_hash = encryption_service.encrypt_field(password_hash, 'password_hash') if password_hash else None
            
            # Update user with encrypted data
            connection.execute(
                text("UPDATE users SET email_encrypted = :email, password_hash_encrypted = :password_hash WHERE id = :id"),
                {
                    'email': encrypted_email,
                    'password_hash': encrypted_password_hash,
                    'id': user_id
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to encrypt user {user_id}: {e}")
            # Continue with other users
    
    logger.info(f"Migrated {len(users)} users to encrypted format")


def migrate_clinics_data():
    """Migrate clinics data to encrypted format."""
    logger.info("Migrating clinics data to encrypted format")
    
    connection = op.get_bind()
    
    # Get all clinics
    clinics = connection.execute(text("""
        SELECT id, phone, email, address, assistant_config, faq_content, admin_notes 
        FROM clinics
    """)).fetchall()
    
    for clinic in clinics:
        clinic_id, phone, email, address, assistant_config, faq_content, admin_notes = clinic
        
        try:
            # Encrypt sensitive fields
            encrypted_phone = encryption_service.encrypt_field(phone, 'phone') if phone else None
            encrypted_email = encryption_service.encrypt_field(email, 'email') if email else None
            encrypted_address = encryption_service.encrypt_field(address, 'address') if address else None
            encrypted_assistant_config = encryption_service.encrypt_json_field(assistant_config, 'assistant_config') if assistant_config else None
            encrypted_faq_content = encryption_service.encrypt_field(faq_content, 'faq_content') if faq_content else None
            encrypted_admin_notes = encryption_service.encrypt_field(admin_notes, 'admin_notes') if admin_notes else None
            
            # Update clinic with encrypted data
            connection.execute(
                text("""
                    UPDATE clinics SET 
                        phone_encrypted = :phone,
                        email_encrypted = :email,
                        address_encrypted = :address,
                        assistant_config_encrypted = :assistant_config,
                        faq_content_encrypted = :faq_content,
                        admin_notes_encrypted = :admin_notes
                    WHERE id = :id
                """),
                {
                    'phone': encrypted_phone,
                    'email': encrypted_email,
                    'address': encrypted_address,
                    'assistant_config': encrypted_assistant_config,
                    'faq_content': encrypted_faq_content,
                    'admin_notes': encrypted_admin_notes,
                    'id': clinic_id
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to encrypt clinic {clinic_id}: {e}")
            # Continue with other clinics
    
    logger.info(f"Migrated {len(clinics)} clinics to encrypted format")


def decrypt_users_data():
    """Decrypt users data (for downgrade)."""
    logger.info("Decrypting users data")
    
    connection = op.get_bind()
    
    # Get all users
    users = connection.execute(text("SELECT id, email, password_hash FROM users")).fetchall()
    
    for user in users:
        user_id, email, password_hash = user
        
        try:
            # Decrypt email and password hash
            decrypted_email = encryption_service.decrypt_field(email, 'email') if email else None
            decrypted_password_hash = encryption_service.decrypt_field(password_hash, 'password_hash') if password_hash else None
            
            # Update user with decrypted data
            connection.execute(
                text("UPDATE users SET email_unencrypted = :email, password_hash_unencrypted = :password_hash WHERE id = :id"),
                {
                    'email': decrypted_email,
                    'password_hash': decrypted_password_hash,
                    'id': user_id
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to decrypt user {user_id}: {e}")
            # Continue with other users
    
    logger.info(f"Decrypted {len(users)} users")


def decrypt_clinics_data():
    """Decrypt clinics data (for downgrade)."""
    logger.info("Decrypting clinics data")
    
    connection = op.get_bind()
    
    # Get all clinics
    clinics = connection.execute(text("""
        SELECT id, phone, email, address, assistant_config, faq_content, admin_notes 
        FROM clinics
    """)).fetchall()
    
    for clinic in clinics:
        clinic_id, phone, email, address, assistant_config, faq_content, admin_notes = clinic
        
        try:
            # Decrypt sensitive fields
            decrypted_phone = encryption_service.decrypt_field(phone, 'phone') if phone else None
            decrypted_email = encryption_service.decrypt_field(email, 'email') if email else None
            decrypted_address = encryption_service.decrypt_field(address, 'address') if address else None
            decrypted_assistant_config = encryption_service.decrypt_json_field(assistant_config, 'assistant_config') if assistant_config else None
            decrypted_faq_content = encryption_service.decrypt_field(faq_content, 'faq_content') if faq_content else None
            decrypted_admin_notes = encryption_service.decrypt_field(admin_notes, 'admin_notes') if admin_notes else None
            
            # Update clinic with decrypted data
            connection.execute(
                text("""
                    UPDATE clinics SET 
                        phone_unencrypted = :phone,
                        email_unencrypted = :email,
                        address_unencrypted = :address,
                        assistant_config_unencrypted = :assistant_config,
                        faq_content_unencrypted = :faq_content,
                        admin_notes_unencrypted = :admin_notes
                    WHERE id = :id
                """),
                {
                    'phone': decrypted_phone,
                    'email': decrypted_email,
                    'address': decrypted_address,
                    'assistant_config': decrypted_assistant_config,
                    'faq_content': decrypted_faq_content,
                    'admin_notes': decrypted_admin_notes,
                    'id': clinic_id
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to decrypt clinic {clinic_id}: {e}")
            # Continue with other clinics
    
    logger.info(f"Decrypted {len(clinics)} clinics")

