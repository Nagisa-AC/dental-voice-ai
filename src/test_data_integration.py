#!/usr/bin/env python3
"""
Test Data Integration with VAPI

This script demonstrates how to retrieve structured data from the database
and integrate it with VAPI assistants.
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Load environment variables
load_dotenv()

from dental_voice_ai.core.data_service import DataService
from dental_voice_ai.core.vapi_service import VAPIService


def test_data_integration():
    """Test data integration with VAPI."""
    print("🧪 Testing Data Integration with VAPI")
    print("=" * 60)
    
    try:
        # Initialize services
        data_service = DataService()
        vapi_service = VAPIService()
        print("✅ Services initialized")
        
        # Test 1: Get Knowledge Base
        print("\n📚 Test 1: Dental Knowledge Base")
        print("-" * 40)
        knowledge_base = data_service.get_dental_knowledge_base()
        formatted_kb = data_service.format_for_vapi("knowledge_base", knowledge_base)
        print(f"✅ Knowledge base retrieved: {len(formatted_kb)} characters")
        print(f"   Practice: {knowledge_base['practice_info']['name']}")
        print(f"   Phone: {knowledge_base['practice_info']['phone']}")
        print(f"   Services: {len(knowledge_base['services']['general_dentistry'])} general services")
        
        # Test 2: Get Appointment Availability
        print("\n📅 Test 2: Appointment Availability")
        print("-" * 40)
        availability = data_service.get_appointment_availability("2024-04-15")
        formatted_availability = data_service.format_for_vapi("availability", availability)
        print(f"✅ Availability retrieved for 2024-04-15")
        print(f"   Available slots: {availability['total_available']}")
        print(f"   Next available: {availability['next_available_date']}")
        
        # Test 3: Get Patient Information
        print("\n👤 Test 3: Patient Information")
        print("-" * 40)
        patient_info = data_service.get_patient_info("PAT123")
        formatted_patient = data_service.format_for_vapi("patient", patient_info)
        print(f"✅ Patient info retrieved: {patient_info['name']}")
        print(f"   Phone: {patient_info['phone']}")
        print(f"   Insurance: {patient_info['insurance']['provider']}")
        
        # Test 4: Get Service Information
        print("\n🦷 Test 4: Service Information")
        print("-" * 40)
        service_info = data_service.get_service_information("dental_cleaning")
        print(f"✅ Service info retrieved: {service_info['name']}")
        print(f"   Duration: {service_info['duration']}")
        print(f"   Price: {service_info['price']}")
        
        # Test 5: Get Structured Data for VAPI
        print("\n🔗 Test 5: Structured Data for VAPI")
        print("-" * 40)
        structured_data = vapi_service.get_structured_data("knowledge_base")
        print(f"✅ Structured data retrieved: {len(structured_data)} characters")
        print("   Sample: " + structured_data[:100] + "...")
        
        # Test 6: Create Assistant with Structured Data
        print("\n🤖 Test 6: Create Assistant with Structured Data")
        print("-" * 40)
        assistant_id = vapi_service.create_dental_assistant("Data-Integrated Sam")
        print(f"✅ Assistant created with structured data: {assistant_id}")
        
        print("\n🎉 All data integration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def main():
    """Main function."""
    print("Dental Voice AI - Data Integration Test")
    print("=" * 60)
    
    success = test_data_integration()
    
    if success:
        print("\n✅ Data integration test completed successfully!")
        print("\n💡 Key Features:")
        print("   - Structured data retrieval from database")
        print("   - VAPI-formatted data output")
        print("   - Assistant integration with real data")
        print("   - Ready for calendar integration")
    else:
        print("\n❌ Data integration test failed!")
        print("\n🔧 Troubleshooting:")
        print("   - Check VAPI API key")
        print("   - Verify data service initialization")
        print("   - Check network connectivity")


if __name__ == "__main__":
    main()
