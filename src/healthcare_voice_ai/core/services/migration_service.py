
class DatabaseError(Exception):
    """Database-related error."""
    pass


class ValidationError(Exception):
    """Validation-related error."""
    pass


class AuthenticationError(Exception):
    """Authentication-related error."""
    pass


class EncryptionError(Exception):
    """Encryption-related error."""
    pass


class AuthorizationError(Exception):
    """Authorization-related error."""
    pass



"""
Database Migration Service

Service for managing database migrations with Alembic.
"""

import os
import subprocess
import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from datetime import datetime

from ..config import settings

logger = logging.getLogger(__name__)


class MigrationService:
    """Service for managing database migrations with Alembic."""
    
    def __init__(self):
        """Initialize migration service."""
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.migrations_dir = self.project_root / "migrations"
        self.alembic_ini = self.project_root / "alembic.ini"
        
        # Ensure migrations directory exists
        self.migrations_dir.mkdir(exist_ok=True)
        self.versions_dir = self.migrations_dir / "versions"
        self.versions_dir.mkdir(exist_ok=True)
    
    def _run_alembic_command(self, command: List[str], capture_output: bool = True) -> Tuple[int, str, str]:
        """
        Run alembic command.
        
        Args:
            command: Alembic command as list
            capture_output: Whether to capture output
            
        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        try:
            # Change to project root directory
            original_cwd = os.getcwd()
            os.chdir(self.project_root)
            
            # Set environment variables
            env = os.environ.copy()
            env["PYTHONPATH"] = str(self.project_root / "src")
            
            # Run command
            result = subprocess.run(
                ["alembic"] + command,
                capture_output=capture_output,
                text=True,
                env=env,
                cwd=self.project_root
            )
            
            return result.returncode, result.stdout, result.stderr
            
        except Exception as e:
            logger.error(f"Error running alembic command: {e}")
            raise DatabaseError(f"Failed to run alembic command: {e}")
        finally:
            os.chdir(original_cwd)
    
    def get_current_revision(self) -> Optional[str]:
        """
        Get current database revision.
        
        Returns:
            Current revision ID or None if no migrations applied
        """
        try:
            returncode, stdout, stderr = self._run_alembic_command(["current"])
            
            if returncode != 0:
                logger.error(f"Error getting current revision: {stderr}")
                return None
            
            # Parse output to get revision
            lines = stdout.strip().split('\n')
            for line in lines:
                if line.strip() and not line.startswith('INFO'):
                    # Extract revision from line like "Rev: abc123 (head)"
                    parts = line.split()
                    if len(parts) >= 2 and parts[0] == "Rev:":
                        return parts[1]
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting current revision: {e}")
            return None
    
    def get_head_revision(self) -> Optional[str]:
        """
        Get head revision (latest migration).
        
        Returns:
            Head revision ID or None if no migrations exist
        """
        try:
            returncode, stdout, stderr = self._run_alembic_command(["heads"])
            
            if returncode != 0:
                logger.error(f"Error getting head revision: {stderr}")
                return None
            
            # Parse output to get head revision
            lines = stdout.strip().split('\n')
            for line in lines:
                if line.strip() and not line.startswith('INFO'):
                    return line.strip()
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting head revision: {e}")
            return None
    
    def get_migration_history(self) -> List[Dict[str, Any]]:
        """
        Get migration history.
        
        Returns:
            List of migration information
        """
        try:
            returncode, stdout, stderr = self._run_alembic_command(["history", "--verbose"])
            
            if returncode != 0:
                logger.error(f"Error getting migration history: {stderr}")
                return []
            
            migrations = []
            current_migration = {}
            
            for line in stdout.split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                if line.startswith('Rev:'):
                    if current_migration:
                        migrations.append(current_migration)
                    current_migration = {
                        "revision": line.split()[1],
                        "description": "",
                        "date": "",
                        "branches": []
                    }
                elif line.startswith('Parent:'):
                    current_migration["parent"] = line.split()[1]
                elif line.startswith('Path:'):
                    current_migration["path"] = line.split()[1]
                elif line.startswith('Branches:'):
                    current_migration["branches"] = line.split()[1:]
                else:
                    # Description line
                    if current_migration and not current_migration["description"]:
                        current_migration["description"] = line
            
            if current_migration:
                migrations.append(current_migration)
            
            return migrations
            
        except Exception as e:
            logger.error(f"Error getting migration history: {e}")
            return []
    
    def create_migration(self, message: str, autogenerate: bool = True) -> Optional[str]:
        """
        Create a new migration.
        
        Args:
            message: Migration message
            autogenerate: Whether to autogenerate from model changes
            
        Returns:
            Created revision ID or None if failed
        """
        try:
            command = ["revision"]
            if autogenerate:
                command.append("--autogenerate")
            command.extend(["-m", message])
            
            returncode, stdout, stderr = self._run_alembic_command(command)
            
            if returncode != 0:
                logger.error(f"Error creating migration: {stderr}")
                return None
            
            # Parse output to get revision ID
            for line in stdout.split('\n'):
                if "Generating" in line and "revision" in line:
                    # Extract revision ID from line like "Generating /path/to/migration.py ... done"
                    parts = line.split()
                    for part in parts:
                        if part.startswith("revision"):
                            return part.split("=")[1].strip()
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating migration: {e}")
            return None
    
    def upgrade_database(self, revision: str = "head") -> bool:
        """
        Upgrade database to specified revision.
        
        Args:
            revision: Target revision (default: "head")
            
        Returns:
            True if successful, False otherwise
        """
        try:
            returncode, stdout, stderr = self._run_alembic_command(["upgrade", revision])
            
            if returncode != 0:
                logger.error(f"Error upgrading database: {stderr}")
                return False
            
            logger.info(f"Database upgraded to revision: {revision}")
            return True
            
        except Exception as e:
            logger.error(f"Error upgrading database: {e}")
            return False
    
    def downgrade_database(self, revision: str) -> bool:
        """
        Downgrade database to specified revision.
        
        Args:
            revision: Target revision
            
        Returns:
            True if successful, False otherwise
        """
        try:
            returncode, stdout, stderr = self._run_alembic_command(["downgrade", revision])
            
            if returncode != 0:
                logger.error(f"Error downgrading database: {stderr}")
                return False
            
            logger.info(f"Database downgraded to revision: {revision}")
            return True
            
        except Exception as e:
            logger.error(f"Error downgrading database: {e}")
            return False
    
    def stamp_database(self, revision: str) -> bool:
        """
        Stamp database with specified revision without running migrations.
        
        Args:
            revision: Revision to stamp
            
        Returns:
            True if successful, False otherwise
        """
        try:
            returncode, stdout, stderr = self._run_alembic_command(["stamp", revision])
            
            if returncode != 0:
                logger.error(f"Error stamping database: {stderr}")
                return False
            
            logger.info(f"Database stamped with revision: {revision}")
            return True
            
        except Exception as e:
            logger.error(f"Error stamping database: {e}")
            return False
    
    def check_migration_status(self) -> Dict[str, Any]:
        """
        Check migration status.
        
        Returns:
            Migration status information
        """
        try:
            current_revision = self.get_current_revision()
            head_revision = self.get_head_revision()
            
            status = {
                "current_revision": current_revision,
                "head_revision": head_revision,
                "is_up_to_date": current_revision == head_revision,
                "needs_upgrade": current_revision != head_revision,
                "migration_count": len(self.get_migration_history()),
                "checked_at": datetime.utcnow().isoformat()
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Error checking migration status: {e}")
            return {
                "error": str(e),
                "checked_at": datetime.utcnow().isoformat()
            }
    
    def initialize_migrations(self) -> bool:
        """
        Initialize migrations for the first time.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if migrations already exist
            if (self.versions_dir / "versions").exists() and list(self.versions_dir.glob("*.py")):
                logger.info("Migrations already initialized")
                return True
            
            # Create initial migration
            revision = self.create_migration("Initial migration", autogenerate=True)
            
            if not revision:
                logger.error("Failed to create initial migration")
                return False
            
            # Stamp database with initial revision
            if not self.stamp_database(revision):
                logger.error("Failed to stamp database with initial revision")
                return False
            
            logger.info("Migrations initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing migrations: {e}")
            return False
    
    def validate_migration_files(self) -> List[Dict[str, Any]]:
        """
        Validate migration files for syntax errors.
        
        Returns:
            List of validation results
        """
        validation_results = []
        
        try:
            for migration_file in self.versions_dir.glob("*.py"):
                try:
                    # Try to compile the file
                    with open(migration_file, 'r') as f:
                        compile(f.read(), migration_file, 'exec')
                    
                    validation_results.append({
                        "file": migration_file.name,
                        "status": "valid",
                        "error": None
                    })
                    
                except SyntaxError as e:
                    validation_results.append({
                        "file": migration_file.name,
                        "status": "invalid",
                        "error": f"Syntax error: {e}"
                    })
                except Exception as e:
                    validation_results.append({
                        "file": migration_file.name,
                        "status": "error",
                        "error": str(e)
                    })
            
        except Exception as e:
            logger.error(f"Error validating migration files: {e}")
            validation_results.append({
                "file": "validation_error",
                "status": "error",
                "error": str(e)
            })
        
        return validation_results


# Global migration service instance
migration_service = MigrationService()


def get_migration_service() -> MigrationService:
    """Get the global migration service instance."""
    return migration_service


def get_current_revision() -> Optional[str]:
    """Get current database revision."""
    return migration_service.get_current_revision()


def get_head_revision() -> Optional[str]:
    """Get head revision."""
    return migration_service.get_head_revision()


def create_migration(message: str, autogenerate: bool = True) -> Optional[str]:
    """Create a new migration."""
    return migration_service.create_migration(message, autogenerate)


def upgrade_database(revision: str = "head") -> bool:
    """Upgrade database to specified revision."""
    return migration_service.upgrade_database(revision)


def downgrade_database(revision: str) -> bool:
    """Downgrade database to specified revision."""
    return migration_service.downgrade_database(revision)


def check_migration_status() -> Dict[str, Any]:
    """Check migration status."""
    return migration_service.check_migration_status()


def initialize_migrations() -> bool:
    """Initialize migrations for the first time."""
    return migration_service.initialize_migrations()

