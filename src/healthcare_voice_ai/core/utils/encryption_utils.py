"""
Encryption Utilities for Healthcare Voice AI

Provides utilities for encryption key management and data migration.
"""

import os
import base64
import logging
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

from healthcare_voice_ai.core.services.encryption_service import encryption_service

logger = logging.getLogger(__name__)


def generate_master_key() -> str:
    """
    Generate a new master encryption key.
    
    Returns:
        Base64-encoded master key
    """
    key = Fernet.generate_key()
    return base64.b64encode(key).decode('utf-8')


def generate_rsa_key_pair(key_size: int = 2048) -> Dict[str, str]:
    """
    Generate RSA key pair for asymmetric encryption.
    
    Args:
        key_size: RSA key size in bits
        
    Returns:
        Dictionary with 'private_key' and 'public_key' (PEM format)
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=default_backend()
    )
    
    public_key = private_key.public_key()
    
    # Serialize private key
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    # Serialize public key
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    return {
        'private_key': private_pem.decode('utf-8'),
        'public_key': public_pem.decode('utf-8')
    }


def save_rsa_keys(private_key_path: str, public_key_path: str, key_size: int = 2048):
    """
    Generate and save RSA key pair to files.
    
    Args:
        private_key_path: Path to save private key
        public_key_path: Path to save public key
        key_size: RSA key size in bits
    """
    keys = generate_rsa_key_pair(key_size)
    
    # Save private key
    with open(private_key_path, 'w') as f:
        f.write(keys['private_key'])
    os.chmod(private_key_path, 0o600)  # Read/write for owner only
    
    # Save public key
    with open(public_key_path, 'w') as f:
        f.write(keys['public_key'])
    os.chmod(public_key_path, 0o644)  # Read for all, write for owner
    
    logger.info(f"RSA keys saved to {private_key_path} and {public_key_path}")


def validate_encryption_setup() -> Dict[str, Any]:
    """
    Validate encryption setup and configuration.
    
    Returns:
        Dictionary with validation results
    """
    results = {
        'master_key_configured': False,
        'rsa_keys_configured': False,
        'encryption_service_working': False,
        'errors': []
    }
    
    try:
        # Check master key
        master_key = os.getenv('ENCRYPTION_MASTER_KEY')
        if master_key:
            results['master_key_configured'] = True
        else:
            results['errors'].append('ENCRYPTION_MASTER_KEY not configured')
        
        # Check RSA keys
        private_key_path = os.getenv('RSA_PRIVATE_KEY_PATH')
        public_key_path = os.getenv('RSA_PUBLIC_KEY_PATH')
        
        if private_key_path and public_key_path:
            if os.path.exists(private_key_path) and os.path.exists(public_key_path):
                results['rsa_keys_configured'] = True
            else:
                results['errors'].append('RSA key files not found')
        else:
            results['errors'].append('RSA key paths not configured')
        
        # Test encryption service
        test_data = "test_encryption_data"
        encrypted = encryption_service.encrypt_field(test_data, 'test')
        decrypted = encryption_service.decrypt_field(encrypted, 'test')
        
        if decrypted == test_data:
            results['encryption_service_working'] = True
        else:
            results['errors'].append('Encryption service test failed')
    
    except Exception as e:
        results['errors'].append(f'Encryption validation error: {str(e)}')
    
    return results


def encrypt_existing_data(data: Dict[str, Any], fields_to_encrypt: list = None) -> Dict[str, Any]:
    """
    Encrypt existing data dictionary.
    
    Args:
        data: Data dictionary to encrypt
        fields_to_encrypt: List of fields to encrypt
        
    Returns:
        Dictionary with encrypted fields
    """
    if fields_to_encrypt is None:
        fields_to_encrypt = [
            'email', 'phone', 'address', 'password_hash', 'ssn', 'date_of_birth',
            'faq_content', 'assistant_config', 'policies', 'notes', 'description'
        ]
    
    return encryption_service.encrypt_dict(data, fields_to_encrypt)


def decrypt_existing_data(data: Dict[str, Any], fields_to_decrypt: list = None) -> Dict[str, Any]:
    """
    Decrypt existing data dictionary.
    
    Args:
        data: Data dictionary to decrypt
        fields_to_decrypt: List of fields to decrypt
        
    Returns:
        Dictionary with decrypted fields
    """
    if fields_to_decrypt is None:
        fields_to_decrypt = [
            'email', 'phone', 'address', 'password_hash', 'ssn', 'date_of_birth',
            'faq_content', 'assistant_config', 'policies', 'notes', 'description'
        ]
    
    return encryption_service.decrypt_dict(data, fields_to_decrypt)


def get_encryption_info() -> Dict[str, Any]:
    """
    Get comprehensive encryption information.
    
    Returns:
        Dictionary with encryption configuration info
    """
    return {
        'service_info': encryption_service.get_encryption_info(),
        'validation': validate_encryption_setup(),
        'environment': {
            'master_key_configured': bool(os.getenv('ENCRYPTION_MASTER_KEY')),
            'rsa_private_key_path': os.getenv('RSA_PRIVATE_KEY_PATH'),
            'rsa_public_key_path': os.getenv('RSA_PUBLIC_KEY_PATH'),
        }
    }


def create_development_keys(output_dir: str = "."):
    """
    Create development encryption keys and configuration.
    
    Args:
        output_dir: Directory to save keys and configuration
    """
    logger.info("Creating development encryption keys")
    
    # Generate master key
    master_key = generate_master_key()
    
    # Generate RSA keys
    rsa_keys = generate_rsa_key_pair()
    
    # Save keys
    private_key_path = os.path.join(output_dir, 'rsa_private_key.pem')
    public_key_path = os.path.join(output_dir, 'rsa_public_key.pem')
    
    with open(private_key_path, 'w') as f:
        f.write(rsa_keys['private_key'])
    os.chmod(private_key_path, 0o600)
    
    with open(public_key_path, 'w') as f:
        f.write(rsa_keys['public_key'])
    os.chmod(public_key_path, 0o644)
    
    # Create .env file with encryption settings
    env_content = f"""# Encryption Configuration (Development)
ENCRYPTION_MASTER_KEY={master_key}
RSA_PRIVATE_KEY_PATH={private_key_path}
RSA_PUBLIC_KEY_PATH={public_key_path}
"""
    
    env_path = os.path.join(output_dir, '.env.encryption')
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    logger.info(f"Development encryption keys created in {output_dir}")
    logger.info(f"Add the contents of {env_path} to your .env file")
    
    return {
        'master_key': master_key,
        'private_key_path': private_key_path,
        'public_key_path': public_key_path,
        'env_file': env_path
    }


if __name__ == "__main__":
    # CLI interface for encryption utilities
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python encryption_utils.py <command>")
        print("Commands:")
        print("  generate-keys [output_dir] - Generate development keys")
        print("  validate - Validate encryption setup")
        print("  info - Show encryption information")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "generate-keys":
        output_dir = sys.argv[2] if len(sys.argv) > 2 else "."
        create_development_keys(output_dir)
    
    elif command == "validate":
        results = validate_encryption_setup()
        print("Encryption Validation Results:")
        for key, value in results.items():
            print(f"  {key}: {value}")
    
    elif command == "info":
        info = get_encryption_info()
        print("Encryption Information:")
        import json
        print(json.dumps(info, indent=2))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
