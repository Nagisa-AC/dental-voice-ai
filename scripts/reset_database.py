#!/usr/bin/env python3
"""
Database Reset Script for Healthcare Voice AI

This script helps reset the database during development by:
1. Dropping all tables
2. Running migrations from scratch
3. Optionally seeding with test data

Usage:
    python scripts/reset_database.py [--seed]
"""

import asyncio
import sys
import os
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))

from backend.core.database import db_manager
from backend.db.models.database_models import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def reset_database(seed_data: bool = False):
    """Reset the database by dropping and recreating all tables."""
    
    try:
        logger.info("🔄 Initializing database manager...")
        db_manager.initialize()
        
        logger.info("🗑️  Dropping all tables...")
        await db_manager.drop_tables()
        
        logger.info("🏗️  Creating all tables...")
        await db_manager.create_tables()
        
        if seed_data:
            logger.info("🌱 Seeding database with test data...")
            await seed_test_data()
        
        logger.info("✅ Database reset completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Database reset failed: {e}")
        raise
    finally:
        await db_manager.close()


async def seed_test_data():
    """Seed the database with test data."""
    from backend.db.models.database_models import User, Clinic, UserRole, ClinicStatus, HealthcareIndustry
    from backend.core.security import hash_password
    
    async with db_manager.get_async_session() as session:
        # Create test admin user
        admin_user = User(
            username="admin",
            email="admin@healthcarevoiceai.com",
            password_hash=get_password_hash("admin123"),
            role=UserRole.SUPER_ADMIN.value,
            is_active=True,
            is_verified=True
        )
        session.add(admin_user)
        
        # Create test clinic
        test_clinic = Clinic(
            tenant_id="test-clinic-001",
            name="Test Dental Practice",
            industry_type=HealthcareIndustry.DENTAL.value,
            status=ClinicStatus.APPROVED.value,
            phone="(555) 123-4567",
            email="info@testdental.com",
            address="123 Main St, Chicago, IL 60601",
            website="https://testdental.com",
            business_hours={
                "monday": {"open": "09:00", "close": "17:00"},
                "tuesday": {"open": "09:00", "close": "17:00"},
                "wednesday": {"open": "09:00", "close": "17:00"},
                "thursday": {"open": "09:00", "close": "17:00"},
                "friday": {"open": "09:00", "close": "15:00"},
                "saturday": {"open": "09:00", "close": "12:00"},
                "sunday": {"closed": True}
            },
            services=[
                {"name": "General Checkup", "duration_minutes": 60, "price": 150.00},
                {"name": "Teeth Cleaning", "duration_minutes": 45, "price": 120.00},
                {"name": "Cavity Filling", "duration_minutes": 90, "price": 200.00}
            ],
            policies={
                "cancellation_policy": "24 hours notice required",
                "no_show_policy": "Fee may apply for missed appointments",
                "payment_policy": "Payment due at time of service"
            },
            faq_content="""# Frequently Asked Questions

## What are your office hours?
We're open Monday through Friday 9 AM to 5 PM, Saturday 9 AM to 12 PM.

## Do you accept insurance?
Yes, we accept most major dental insurance plans.

## How do I schedule an appointment?
You can call us at (555) 123-4567 or use our online booking system.""",
            approved_by=admin_user.id,
            approved_at=admin_user.created_at
        )
        session.add(test_clinic)
        
        await session.commit()
        logger.info("✅ Test data seeded successfully!")


def main():
    """Main function to handle command line arguments and run the reset."""
    parser = argparse.ArgumentParser(description="Reset the Healthcare Voice AI database")
    parser.add_argument(
        "--seed", 
        action="store_true", 
        help="Seed the database with test data after reset"
    )
    parser.add_argument(
        "--confirm", 
        action="store_true", 
        help="Skip confirmation prompt (use with caution!)"
    )
    
    args = parser.parse_args()
    
    if not args.confirm:
        print("⚠️  WARNING: This will completely reset the database!")
        print("   All existing data will be lost!")
        response = input("Are you sure you want to continue? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("❌ Database reset cancelled.")
            return
    
    try:
        asyncio.run(reset_database(seed_data=args.seed))
    except KeyboardInterrupt:
        print("\n❌ Database reset cancelled by user.")
    except Exception as e:
        print(f"❌ Database reset failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

