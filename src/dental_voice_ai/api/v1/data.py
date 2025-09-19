"""
Data API endpoints for Dental Voice AI

Provides endpoints for retrieving and managing structured data for VAPI integration.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from dental_voice_ai.core.data_service import get_data_service, DataService
from dental_voice_ai.core.vapi_service import get_vapi_service, VAPIService
# ErrorResponse import removed as it's not used
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/knowledge-base")
async def get_knowledge_base(
    data_service: DataService = Depends(get_data_service)
):
    """
    Get the complete dental knowledge base.
    """
    try:
        knowledge_base = data_service.get_dental_knowledge_base()
        formatted_kb = data_service.format_for_vapi("knowledge_base", knowledge_base)
        
        return {
            "status": "success",
            "data": knowledge_base,
            "formatted_for_vapi": formatted_kb,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get knowledge base: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get knowledge base: {str(e)}")


@router.get("/availability/{date}")
async def get_availability(
    date: str,
    service_type: Optional[str] = Query(None, description="Type of service"),
    data_service: DataService = Depends(get_data_service)
):
    """
    Get appointment availability for a specific date.
    """
    try:
        availability = data_service.get_appointment_availability(date, service_type)
        formatted_availability = data_service.format_for_vapi("availability", availability)
        
        return {
            "status": "success",
            "data": availability,
            "formatted_for_vapi": formatted_availability,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get availability for {date}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get availability: {str(e)}")


@router.get("/patient/{patient_id}")
async def get_patient_info(
    patient_id: str,
    data_service: DataService = Depends(get_data_service)
):
    """
    Get patient information by ID.
    """
    try:
        patient_info = data_service.get_patient_info(patient_id)
        formatted_patient = data_service.format_for_vapi("patient", patient_info)
        
        return {
            "status": "success",
            "data": patient_info,
            "formatted_for_vapi": formatted_patient,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get patient info for {patient_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get patient info: {str(e)}")


@router.get("/appointment/{appointment_id}")
async def get_appointment_details(
    appointment_id: str,
    data_service: DataService = Depends(get_data_service)
):
    """
    Get appointment details by ID.
    """
    try:
        appointment_details = data_service.get_appointment_details(appointment_id)
        formatted_appointment = data_service.format_for_vapi("appointment", appointment_details)
        
        return {
            "status": "success",
            "data": appointment_details,
            "formatted_for_vapi": formatted_appointment,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get appointment details for {appointment_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get appointment details: {str(e)}")


@router.get("/appointments/search")
async def search_appointments(
    patient_name: Optional[str] = Query(None, description="Patient name to search"),
    phone: Optional[str] = Query(None, description="Phone number to search"),
    date: Optional[str] = Query(None, description="Date to search"),
    data_service: DataService = Depends(get_data_service)
):
    """
    Search appointments by various criteria.
    """
    try:
        appointments = data_service.search_appointments(patient_name, phone, date)
        
        return {
            "status": "success",
            "data": appointments,
            "count": len(appointments),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to search appointments: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search appointments: {str(e)}")


@router.get("/service/{service_name}")
async def get_service_info(
    service_name: str,
    data_service: DataService = Depends(get_data_service)
):
    """
    Get detailed information about a specific service.
    """
    try:
        service_info = data_service.get_service_information(service_name)
        
        return {
            "status": "success",
            "data": service_info,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get service info for {service_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get service info: {str(e)}")


@router.post("/assistant/{assistant_id}/update-data")
async def update_assistant_with_data(
    assistant_id: str,
    data_type: str,
    vapi_service: VAPIService = Depends(get_vapi_service),
    data_service: DataService = Depends(get_data_service)
):
    """
    Update an assistant with specific data from the database.
    """
    try:
        # Get the data based on type
        if data_type == "knowledge_base":
            data = data_service.get_dental_knowledge_base()
            formatted_data = data_service.format_for_vapi("knowledge_base", data)
            
        elif data_type == "availability":
            # This would need date parameter in request body
            raise HTTPException(status_code=400, detail="Availability updates require date parameter")
            
        elif data_type == "patient":
            # This would need patient_id parameter in request body
            raise HTTPException(status_code=400, detail="Patient updates require patient_id parameter")
            
        elif data_type == "appointment":
            # This would need appointment_id parameter in request body
            raise HTTPException(status_code=400, detail="Appointment updates require appointment_id parameter")
            
        else:
            raise HTTPException(status_code=400, detail=f"Unknown data type: {data_type}")
        
        # Update the assistant
        updated_assistant = vapi_service.update_assistant_with_data(assistant_id, data_type)
        
        return {
            "status": "success",
            "assistant_id": assistant_id,
            "data_type": data_type,
            "formatted_data": formatted_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to update assistant {assistant_id} with {data_type}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update assistant: {str(e)}")


@router.get("/structured-data/{data_type}")
async def get_structured_data(
    data_type: str,
    vapi_service: VAPIService = Depends(get_vapi_service)
):
    """
    Get structured data formatted for VAPI consumption.
    """
    try:
        formatted_data = vapi_service.get_structured_data(data_type)
        
        return {
            "status": "success",
            "data_type": data_type,
            "formatted_data": formatted_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get structured data for {data_type}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get structured data: {str(e)}")


@router.get("/")
async def root():
    """
    Root endpoint for data API.
    """
    return {
        "service": "Dental Voice AI - Data API",
        "version": "2.0.0",
        "status": "healthy",
        "endpoints": {
            "knowledge_base": "/knowledge-base",
            "availability": "/availability/{date}",
            "patient": "/patient/{patient_id}",
            "appointment": "/appointment/{appointment_id}",
            "search": "/appointments/search",
            "service": "/service/{service_name}",
            "update_assistant": "/assistant/{assistant_id}/update-data",
            "structured_data": "/structured-data/{data_type}"
        }
    }
