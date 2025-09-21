#!/usr/bin/env python3
"""
Setup script to create a VAPI phone number for testing
"""

import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from healthcare_voice_ai.core.services.async_vapi_service import AsyncVAPIService
from healthcare_voice_ai.core.config import settings

async def setup_phone_number():
    """Set up a phone number for testing."""
    print("🚀 Setting up VAPI phone number for testing...")
    
    # Initialize VAPI service
    vapi_service = AsyncVAPIService()
    
    try:
        # Create a simple dental assistant first
        print("📞 Creating dental assistant...")
        assistant_id = await vapi_service.create_dental_assistant(
            name="Dental Test Assistant",
            prompt="You are a helpful dental office assistant. Greet callers professionally and help them with appointment scheduling.",
            voice_id="sarah"  # Default voice
        )
        print(f"✅ Created assistant: {assistant_id}")
        
        # Create a phone number
        print("📱 Creating phone number...")
        phone_number_id = await vapi_service.create_phone_number(
            assistant_id=assistant_id,
            area_code="415"  # San Francisco area code
        )
        print(f"✅ Created phone number ID: {phone_number_id}")
        
        # Get phone number details
        print("🔍 Getting phone number details...")
        phone_details = await vapi_service.get_phone_number(phone_number_id)
        phone_number = phone_details.get("number", "Unknown")
        
        print("\n" + "="*50)
        print("🎉 SETUP COMPLETE!")
        print("="*50)
        print(f"📞 Phone Number: {phone_number}")
        print(f"🤖 Assistant ID: {assistant_id}")
        print(f"🔗 Phone Number ID: {phone_number_id}")
        print(f"🌐 Webhook URL: http://67.173.189.116:8000/webhooks/incoming_call")
        print("\n📱 You can now call this number to test your voice AI!")
        print("="*50)
        
        return phone_number, assistant_id, phone_number_id
        
    except Exception as e:
        print(f"❌ Error setting up phone number: {e}")
        return None, None, None

async def list_existing_phone_numbers():
    """List existing phone numbers."""
    print("📋 Listing existing phone numbers...")
    
    vapi_service = AsyncVAPIService()
    
    try:
        phone_numbers = await vapi_service.list_phone_numbers()
        print(f"✅ Found {len(phone_numbers.get('data', []))} phone numbers")
        
        for phone in phone_numbers.get('data', []):
            print(f"📞 {phone.get('number', 'Unknown')} - ID: {phone.get('id', 'Unknown')}")
            
        return phone_numbers.get('data', [])
        
    except Exception as e:
        print(f"❌ Error listing phone numbers: {e}")
        return []

async def main():
    """Main function."""
    print("🏥 Healthcare Voice AI - Phone Setup")
    print("="*40)
    
    # Check if VAPI is configured
    if not settings.VAPI_API_KEY:
        print("❌ VAPI_API_KEY not configured!")
        print("Please set VAPI_API_KEY environment variable")
        return
    
    print(f"✅ VAPI API Key configured: {settings.VAPI_API_KEY[:8]}...")
    
    # List existing phone numbers first
    existing_phones = await list_existing_phone_numbers()
    
    if existing_phones:
        print(f"\n📱 Found {len(existing_phones)} existing phone numbers:")
        for phone in existing_phones:
            print(f"   📞 {phone.get('number', 'Unknown')}")
        
        choice = input("\nDo you want to use an existing number? (y/n): ").lower()
        if choice == 'y':
            print("✅ Using existing phone numbers above")
            return
    
    # Create new phone number
    phone_number, assistant_id, phone_number_id = await setup_phone_number()
    
    if phone_number:
        print(f"\n🎯 Ready for testing! Call: {phone_number}")

if __name__ == "__main__":
    asyncio.run(main())

