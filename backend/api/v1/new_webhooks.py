"""
Updated webhook endpoints for the new clean schema
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database import get_db_session
from db.models.database_models import (
    Call, Patient, Assistant, Clinic, Tenant, AuditLog, AuditAction, CommunicationPref
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/webhooks/incoming_call")
async def handle_vapi_webhook(request: Request):
    """
    Handle incoming VAPI webhook calls with the new clean schema.
    """
    try:
        # Read the request body
        body = await request.body()
        webhook_data = json.loads(body)
        
        logger.info(f"📞 Received VAPI webhook: {webhook_data.get('message', {}).get('type', 'unknown')}")
        
        # Get database session
        async for db in get_db_session():
            await store_call_data(db, webhook_data)
            break
        
        return {"status": "success", "message": "Webhook processed and call data stored"}
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON decode error: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        logger.error(f"❌ Webhook processing error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def store_call_data(db: AsyncSession, webhook_data: Dict[str, Any]):
    """
    Store call data using the new clean schema.
    """
    try:
        message_data = webhook_data.get('message', {})
        call_data = message_data.get('call', {})
        artifact_data = message_data.get('artifact', {})
        
        # Extract call information
        vapi_call_id = call_data.get('id', '')
        customer_data = call_data.get('customer', {})
        assistant_data = call_data.get('assistant', {})
        phone_data = call_data.get('phoneNumber', {})
        
        # Get default clinic and assistant IDs
        default_clinic_id = "00000000-0000-0000-0000-000000000001"  # From schema
        default_assistant_id = "00000000-0000-0000-0000-000000000002"  # From schema
        
        # Create or find patient
        patient_id = await create_or_find_patient(
            db, customer_data, default_clinic_id
        )
        
        # Create new call record
        new_call = Call(
            assistant_id=default_assistant_id,
            patient_id=patient_id,
            clinic_id=default_clinic_id,
            started_at=datetime.fromisoformat(
                call_data.get('startedAt', datetime.utcnow().isoformat()).replace('Z', '+00:00')
            ),
            ended_at=datetime.fromisoformat(
                call_data.get('endedAt', '').replace('Z', '+00:00')
            ) if call_data.get('endedAt') else None,
            reason_for_call=artifact_data.get('summary', ''),
            transcript=artifact_data.get('transcript', ''),
            recording_url=artifact_data.get('recordingUrl', ''),
            summary=artifact_data.get('summary', '')
        )
        
        db.add(new_call)
        await db.commit()
        
        logger.info(f"✅ Call data stored successfully for call {vapi_call_id}")
        
    except Exception as e:
        logger.error(f"❌ Error storing call data: {e}")
        await db.rollback()
        raise


async def create_or_find_patient(
    db: AsyncSession, 
    customer_data: Dict[str, Any], 
    clinic_id: str
) -> str:
    """
    Create or find patient record.
    """
    try:
        customer_phone = customer_data.get('number', '')
        customer_name = customer_data.get('name', '')
        
        if not customer_phone:
            logger.warning("⚠️ No customer phone number provided")
            return None
        
        # Check if patient already exists
        result = await db.execute(
            select(Patient).where(
                Patient.clinic_id == clinic_id,
                Patient.phone_number == customer_phone,
                Patient.deleted_at.is_(None)
            )
        )
        existing_patient = result.scalar_one_or_none()
        
        if existing_patient:
            # Update existing patient if name is provided
            if customer_name and not existing_patient.name:
                existing_patient.name = customer_name
                await db.commit()
            logger.info(f"📝 Found existing patient: {existing_patient.id}")
            return existing_patient.id
        else:
            # Create new patient using raw SQL to avoid enum issues
            from sqlalchemy import text
            result = await db.execute(
                text("INSERT INTO patients (id, clinic_id, name, phone_number, is_new, communication_pref) VALUES (:id, :clinic_id, :name, :phone_number, :is_new, :communication_pref) RETURNING id"),
                {
                    "id": str(uuid.uuid4()),
                    "clinic_id": clinic_id,
                    "name": customer_name or f"Patient {customer_phone}",
                    "phone_number": customer_phone,
                    "is_new": True,
                    "communication_pref": "phone"
                }
            )
            patient_id = result.scalar()
            await db.commit()
            logger.info(f"👤 Created new patient: {patient_id}")
            return patient_id
            
    except Exception as e:
        logger.error(f"❌ Error creating/finding patient: {e}")
        raise


@router.get("/webhooks/calls")
async def get_calls():
    """
    Get all stored calls for verification.
    """
    try:
        async for db in get_db_session():
            result = await db.execute(
                select(Call).where(Call.deleted_at.is_(None))
                .order_by(Call.created_at.desc())
                .limit(50)
            )
            calls = result.scalars().all()
            
            calls_data = []
            for call in calls:
                calls_data.append({
                    "id": call.id,
                    "assistant_id": call.assistant_id,
                    "patient_id": call.patient_id,
                    "clinic_id": call.clinic_id,
                    "started_at": call.started_at.isoformat() if call.started_at else None,
                    "ended_at": call.ended_at.isoformat() if call.ended_at else None,
                    "reason_for_call": call.reason_for_call,
                    "transcript": call.transcript[:100] + "..." if call.transcript and len(call.transcript) > 100 else call.transcript,
                    "summary": call.summary,
                    "created_at": call.created_at.isoformat()
                })
            
            return {
                "count": len(calls_data),
                "calls": calls_data
            }
            
    except Exception as e:
        logger.error(f"❌ Error retrieving calls: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/webhooks/test-enum")
async def test_enum():
    """Test endpoint to check enum values in database."""
    try:
        async for db in get_db_session():
            # Try to insert a patient with raw SQL to test enum values
            from sqlalchemy import text
            result = await db.execute(
                text("INSERT INTO patients (id, clinic_id, name, phone_number, is_new, communication_pref) VALUES (:id, :clinic_id, :name, :phone_number, :is_new, :communication_pref) RETURNING id"),
                {
                    "id": "550e8400-e29b-41d4-a716-446655440999",  # valid UUID
                    "clinic_id": "00000000-0000-0000-0000-000000000001",  # default clinic
                    "name": "Test Enum Patient",
                    "phone_number": "+1999999999",
                    "is_new": True,
                    "communication_pref": "phone"  # lowercase
                }
            )
            patient_id = result.scalar()
            await db.commit()
            
            return {
                "status": "success",
                "message": f"Patient created with ID: {patient_id}",
                "enum_value_used": "phone"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "error_type": type(e).__name__
        }

@router.get("/webhooks/patients")
async def get_patients():
    """
    Get all stored patients for verification.
    """
    try:
        async for db in get_db_session():
            result = await db.execute(
                select(Patient).where(Patient.deleted_at.is_(None))
                .order_by(Patient.created_at.desc())
                .limit(50)
            )
            patients = result.scalars().all()
            
            patients_data = []
            for patient in patients:
                patients_data.append({
                    "id": patient.id,
                    "clinic_id": patient.clinic_id,
                    "name": patient.name,
                    "phone_number": patient.phone_number,
                    "insurance_type": patient.insurance_type,
                    "is_new": patient.is_new,
                    "communication_pref": patient.communication_pref,
                    "created_at": patient.created_at.isoformat()
                })
            
            return {
                "count": len(patients_data),
                "patients": patients_data
            }
            
    except Exception as e:
        logger.error(f"❌ Error retrieving patients: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/webhooks/assistants")
async def get_assistants():
    """Get all assistants."""
    try:
        async for db in get_db_session():
            result = await db.execute(
                select(Assistant).order_by(Assistant.created_at.desc()).limit(50)
            )
            assistants = result.scalars().all()
            
            assistants_data = []
            for assistant in assistants:
                assistants_data.append({
                    "id": str(assistant.id),
                    "clinic_id": str(assistant.clinic_id),
                    "name": assistant.name,
                    "phone_number": assistant.phone_number,
                    "active": assistant.active,
                    "created_at": assistant.created_at.isoformat(),
                    "deleted_at": assistant.deleted_at.isoformat() if assistant.deleted_at else None,
                })
            
            return {
                "count": len(assistants_data),
                "assistants": assistants_data
            }
            
    except Exception as e:
        logger.error(f"❌ Error retrieving assistants: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/webhooks/audit-logs")
async def get_audit_logs():
    """Get all audit logs."""
    try:
        async for db in get_db_session():
            result = await db.execute(
                select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(50)
            )
            audit_logs = result.scalars().all()
            
            audit_logs_data = []
            for audit_log in audit_logs:
                audit_logs_data.append({
                    "id": str(audit_log.id),
                    "tenant_id": str(audit_log.tenant_id) if audit_log.tenant_id else None,
                    "user_id": str(audit_log.user_id) if audit_log.user_id else None,
                    "table_name": audit_log.table_name,
                    "record_id": str(audit_log.record_id) if audit_log.record_id else None,
                    "action": audit_log.action.value,
                    "timestamp": audit_log.timestamp.isoformat(),
                    "details": audit_log.details,
                })
            
            return {
                "count": len(audit_logs_data),
                "audit_logs": audit_logs_data
            }
            
    except Exception as e:
        logger.error(f"❌ Error retrieving audit logs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/webhooks/db-status")
async def get_db_status():
    """Get database status and counts."""
    try:
        async for db in get_db_session():
            # Get counts for each table
            tenant_result = await db.execute(select(Tenant))
            clinic_result = await db.execute(select(Clinic))
            assistant_result = await db.execute(select(Assistant))
            patient_result = await db.execute(select(Patient))
            call_result = await db.execute(select(Call))
            audit_result = await db.execute(select(AuditLog))
            
            return {
                "status": "healthy",
                "table_counts": {
                    "tenants": len(tenant_result.scalars().all()),
                    "clinics": len(clinic_result.scalars().all()),
                    "assistants": len(assistant_result.scalars().all()),
                    "patients": len(patient_result.scalars().all()),
                    "calls": len(call_result.scalars().all()),
                    "audit_logs": len(audit_result.scalars().all()),
                }
            }
            
    except Exception as e:
        logger.error(f"❌ Error getting database status: {e}")
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__
        }
