"""
SSL/TLS Configuration Service for Healthcare Voice AI

Provides comprehensive SSL/TLS configuration and security hardening.
"""

import os
import ssl
import logging
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

from healthcare_voice_ai.core.config import settings
from healthcare_voice_ai.core.errors import ConfigurationError

logger = logging.getLogger(__name__)


class SSLService:
    """
    Service for SSL/TLS configuration and security hardening.
    
    Provides secure SSL/TLS configuration for production deployments.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ssl_context = None
        self._initialize_ssl_context()
    
    def _initialize_ssl_context(self):
        """Initialize SSL context with secure defaults."""
        try:
            # Create SSL context with secure defaults
            self.ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            
            # Configure secure SSL/TLS settings
            self._configure_secure_ssl()
            
            self.logger.info("SSL context initialized with secure defaults")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize SSL context: {e}")
            raise ConfigurationError(f"SSL initialization failed: {str(e)}")
    
    def _configure_secure_ssl(self):
        """Configure SSL context with security hardening."""
        if not self.ssl_context:
            return
        
        # Disable weak protocols (SSL 2.0, SSL 3.0, TLS 1.0, TLS 1.1)
        self.ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
        self.ssl_context.maximum_version = ssl.TLSVersion.TLSv1_3
        
        # Disable weak cipher suites
        self.ssl_context.set_ciphers(
            'ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS'
        )
        
        # Enable certificate verification
        self.ssl_context.check_hostname = True
        self.ssl_context.verify_mode = ssl.CERT_REQUIRED
        
        # Enable OCSP stapling (if supported)
        try:
            self.ssl_context.post_handshake_auth = True
        except AttributeError:
            # post_handshake_auth not available in this Python version
            pass
        
        # Apply SSL options (with compatibility checks)
        ssl_option_names = [
            'OP_NO_TICKET',             # Disable session tickets
            'OP_NO_COMPRESSION',        # Disable compression to prevent CRIME attacks
            'OP_SECURE_RENEGOTIATION',  # Enable secure renegotiation
            'OP_NO_RENEGOTIATION',      # Disable renegotiation (Python 3.7+)
            'OP_SINGLE_DH_USE',         # Single DH use (if available)
            'OP_SINGLE_ECDH_USE'        # Single ECDH use (if available)
        ]
        
        # Apply all available SSL options
        for option_name in ssl_option_names:
            if hasattr(ssl, option_name):
                try:
                    option_value = getattr(ssl, option_name)
                    self.ssl_context.options |= option_value
                except (AttributeError, TypeError):
                    # Option not available in this Python/OpenSSL version
                    pass
    
    def get_ssl_context(self) -> ssl.SSLContext:
        """Get configured SSL context."""
        return self.ssl_context
    
    def configure_server_ssl(self, cert_file: str, key_file: str, 
                           ca_file: Optional[str] = None) -> ssl.SSLContext:
        """
        Configure SSL context for server mode.
        
        Args:
            cert_file: Path to SSL certificate file
            key_file: Path to SSL private key file
            ca_file: Path to CA certificate file (optional)
            
        Returns:
            Configured SSL context for server
        """
        try:
            # Create server SSL context
            server_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            
            # Load certificate and key
            server_context.load_cert_chain(cert_file, key_file)
            
            # Load CA file if provided
            if ca_file and os.path.exists(ca_file):
                server_context.load_verify_locations(ca_file)
            
            # Apply security hardening
            self._configure_secure_ssl()
            
            # Copy secure settings to server context
            server_context.minimum_version = self.ssl_context.minimum_version
            server_context.maximum_version = self.ssl_context.maximum_version
            server_context.set_ciphers(self.ssl_context.get_ciphers())
            server_context.options = self.ssl_context.options
            
            self.logger.info(f"Server SSL context configured with cert: {cert_file}")
            return server_context
            
        except Exception as e:
            self.logger.error(f"Failed to configure server SSL: {e}")
            raise ConfigurationError(f"Server SSL configuration failed: {str(e)}")
    
    def validate_ssl_certificate(self, cert_file: str) -> Dict[str, Any]:
        """
        Validate SSL certificate.
        
        Args:
            cert_file: Path to SSL certificate file
            
        Returns:
            Dictionary with certificate validation results
        """
        try:
            import OpenSSL.crypto
            
            with open(cert_file, 'rb') as f:
                cert_data = f.read()
            
            cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert_data)
            
            # Get certificate information
            subject = cert.get_subject()
            issuer = cert.get_issuer()
            
            # Check expiration
            not_after = cert.get_notAfter().decode('utf-8')
            not_before = cert.get_notBefore().decode('utf-8')
            
            # Parse dates
            from datetime import datetime
            expire_date = datetime.strptime(not_after, '%Y%m%d%H%M%SZ')
            start_date = datetime.strptime(not_before, '%Y%m%d%H%M%SZ')
            now = datetime.utcnow()
            
            # Calculate days until expiration
            days_until_expiry = (expire_date - now).days
            
            # Check if certificate is valid
            is_valid = start_date <= now <= expire_date
            is_expired = now > expire_date
            is_not_yet_valid = now < start_date
            
            return {
                'valid': is_valid,
                'expired': is_expired,
                'not_yet_valid': is_not_yet_valid,
                'days_until_expiry': days_until_expiry,
                'subject': {
                    'common_name': subject.commonName,
                    'organization': subject.organizationName,
                    'country': subject.countryName
                },
                'issuer': {
                    'common_name': issuer.commonName,
                    'organization': issuer.organizationName,
                    'country': issuer.countryName
                },
                'serial_number': cert.get_serial_number(),
                'version': cert.get_version(),
                'signature_algorithm': cert.get_signature_algorithm().decode('utf-8'),
                'not_before': not_before,
                'not_after': not_after
            }
            
        except ImportError:
            self.logger.warning("pyOpenSSL not available for certificate validation")
            return {'error': 'pyOpenSSL not available'}
        except Exception as e:
            self.logger.error(f"Certificate validation failed: {e}")
            return {'error': str(e)}
    
    def get_ssl_configuration(self) -> Dict[str, Any]:
        """
        Get current SSL configuration information.
        
        Returns:
            Dictionary with SSL configuration details
        """
        if not self.ssl_context:
            return {'error': 'SSL context not initialized'}
        
        try:
            return {
                'minimum_version': self.ssl_context.minimum_version.name,
                'maximum_version': self.ssl_context.maximum_version.name,
                'cipher_suites': self.ssl_context.get_ciphers(),
                'options': [opt.name for opt in ssl.Options if self.ssl_context.options & opt.value],
                'verify_mode': self.ssl_context.verify_mode.name,
                'check_hostname': self.ssl_context.check_hostname,
                'protocol': ssl.PROTOCOL_TLS.name
            }
        except Exception as e:
            self.logger.error(f"Failed to get SSL configuration: {e}")
            return {'error': str(e)}
    
    def generate_self_signed_certificate(self, hostname: str = "localhost", 
                                       output_dir: str = ".") -> Tuple[str, str]:
        """
        Generate self-signed certificate for development.
        
        Args:
            hostname: Hostname for the certificate
            output_dir: Directory to save certificate files
            
        Returns:
            Tuple of (cert_file_path, key_file_path)
        """
        try:
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import rsa
            from datetime import datetime, timedelta
            
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
            )
            
            # Create certificate
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "California"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Healthcare Voice AI"),
                x509.NameAttribute(NameOID.COMMON_NAME, hostname),
            ])
            
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.utcnow()
            ).not_valid_after(
                datetime.utcnow() + timedelta(days=365)
            ).add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName(hostname),
                    x509.DNSName("localhost"),
                    x509.IPAddress("127.0.0.1"),
                ]),
                critical=False,
            ).sign(private_key, hashes.SHA256())
            
            # Save certificate
            cert_path = os.path.join(output_dir, f"{hostname}.crt")
            with open(cert_path, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
            
            # Save private key
            key_path = os.path.join(output_dir, f"{hostname}.key")
            with open(key_path, "wb") as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            # Set proper permissions
            os.chmod(cert_path, 0o644)
            os.chmod(key_path, 0o600)
            
            self.logger.info(f"Self-signed certificate generated: {cert_path}, {key_path}")
            return cert_path, key_path
            
        except ImportError:
            self.logger.error("cryptography library not available for certificate generation")
            raise ConfigurationError("cryptography library required for certificate generation")
        except Exception as e:
            self.logger.error(f"Failed to generate self-signed certificate: {e}")
            raise ConfigurationError(f"Certificate generation failed: {str(e)}")
    
    def check_ssl_requirements(self) -> Dict[str, Any]:
        """
        Check SSL/TLS requirements and configuration.
        
        Returns:
            Dictionary with SSL requirements check results
        """
        results = {
            'ssl_available': True,
            'tls_versions': [],
            'cipher_suites': [],
            'recommendations': [],
            'warnings': []
        }
        
        try:
            # Check available TLS versions
            for version in [ssl.TLSVersion.TLSv1_2, ssl.TLSVersion.TLSv1_3]:
                try:
                    context = ssl.create_default_context()
                    context.minimum_version = version
                    context.maximum_version = version
                    results['tls_versions'].append(version.name)
                except:
                    pass
            
            # Check cipher suites
            context = ssl.create_default_context()
            results['cipher_suites'] = [cipher['name'] for cipher in context.get_ciphers()]
            
            # Security recommendations
            if ssl.TLSVersion.TLSv1_3 not in [v for v in ssl.TLSVersion]:
                results['recommendations'].append("Upgrade to OpenSSL 1.1.1+ for TLS 1.3 support")
            
            if not results['cipher_suites']:
                results['warnings'].append("No cipher suites available")
            
            # Check for weak ciphers
            weak_ciphers = ['RC4', 'DES', 'MD5', 'SHA1']
            for cipher in results['cipher_suites']:
                for weak in weak_ciphers:
                    if weak in cipher:
                        results['warnings'].append(f"Weak cipher detected: {cipher}")
            
        except Exception as e:
            results['ssl_available'] = False
            results['error'] = str(e)
        
        return results


# Global SSL service instance
ssl_service = SSLService()


def get_ssl_context() -> ssl.SSLContext:
    """Get configured SSL context."""
    return ssl_service.get_ssl_context()


def configure_server_ssl(cert_file: str, key_file: str, ca_file: str = None) -> ssl.SSLContext:
    """Configure SSL context for server mode."""
    return ssl_service.configure_server_ssl(cert_file, key_file, ca_file)


def validate_ssl_certificate(cert_file: str) -> Dict[str, Any]:
    """Validate SSL certificate."""
    return ssl_service.validate_ssl_certificate(cert_file)


def get_ssl_configuration() -> Dict[str, Any]:
    """Get current SSL configuration."""
    return ssl_service.get_ssl_configuration()


def check_ssl_requirements() -> Dict[str, Any]:
    """Check SSL/TLS requirements."""
    return ssl_service.check_ssl_requirements()
