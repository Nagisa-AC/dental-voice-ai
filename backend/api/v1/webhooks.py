from fastapi import APIRouter, Request, HTTPException, Depends
import logging
import time
from typing import Dict, Any, Optional
import requests
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth import get_current_user, AuthUser
from core.database import get_db_session
from db.models.database_models import (
    Call, Patient, Assistant, PhoneNumber, AuditLog, 
    AuditAction, AuditResource
)

# Configure logging
logger = logging.getLogger(__name__)

# Pydantic models for appointment requests
class AppointmentRequest(BaseModel):
    patient_name: str
    patient_phone: str
    service_type: str
    appointment_date: str  # Format: "2025-08-30"
    appointment_time: str  # Format: "09:00 AM"
    duration: int = 60  # Default 60 minutes
    notes: Optional[str] = None


class AppointmentResponse(BaseModel):
    status: str
    appointment_id: str
    message: str
    calendar_event_id: Optional[str] = None


router = APIRouter()


@router.get("/incoming_call")
async def webhook_availability():
    """
    VAPI availability check endpoint (public, no auth required).
    """
    return {"status": "available", "message": "Dental Voice AI webhook is ready"}


@router.post("/test")
async def test_webhook():
    """
    Simple test endpoint to verify webhook functionality.
    """
    logger.info("🧪 Test webhook endpoint called")
    return {"status": "success", "message": "Test webhook is working"}


@router.get("/calls")
async def get_calls(db: AsyncSession = Depends(get_db_session)):
    """
    Get all stored call records from the database.
    """
    try:
        from sqlalchemy import select
        result = await db.execute(select(Call).order_by(Call.created_at.desc()).limit(10))
        calls = result.scalars().all()
        
        call_data = []
        for call in calls:
            call_data.append({
                "id": call.id,
                "vapi_call_id": call.vapi_call_id,
                "customer_phone": call.customer_phone,
                "customer_name": call.customer_name,
                "status": call.status,
                "duration_seconds": call.duration_seconds,
                "cost": call.cost,
                "started_at": call.started_at.isoformat() if call.started_at else None,
                "ended_at": call.ended_at.isoformat() if call.ended_at else None,
                "created_at": call.created_at.isoformat() if call.created_at else None
            })
        
        return {
            "status": "success",
            "count": len(call_data),
            "calls": call_data
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting calls: {e}")
        return {"status": "error", "message": str(e)}


@router.post("/incoming_call")
async def handle_vapi_webhook(request: Request, db: AsyncSession = Depends(get_db_session)):
    """
    Handle incoming VAPI webhook calls and store call data in database.
    """
    try:
        logger.info("📞 VAPI webhook endpoint called")
        
        # Get the raw request body
        body = await request.body()
        logger.info(f"📞 Received VAPI webhook: {len(body)} bytes")
        
        # Parse JSON if possible
        try:
            import json
            webhook_data = json.loads(body)
            logger.info(f"📋 Webhook data parsed successfully")
            logger.info(f"📋 Webhook data keys: {list(webhook_data.keys())}")
            
            # Log the webhook event
            webhook_type = webhook_data.get('message', {}).get('type', 'unknown')
            logger.info(f"🎯 VAPI Webhook received - Type: {webhook_type}")
            
            # Extract call ID if available
            call_data = webhook_data.get('message', {}).get('call', {})
            vapi_call_id = call_data.get('id', 'unknown')
            logger.info(f"📞 Call ID: {vapi_call_id}")
            logger.info(f"📞 Call data keys: {list(call_data.keys())}")
            
            # Store call data in database
            logger.info(f"💾 Attempting to store call data for ID: {vapi_call_id}")
            await store_call_data(db, webhook_data, webhook_type)
            logger.info(f"✅ Call data storage completed for ID: {vapi_call_id}")
            
        except Exception as parse_error:
            logger.error(f"❌ Error parsing webhook JSON: {parse_error}")
            webhook_data = {"raw_data": body.decode('utf-8', errors='ignore')}
        
        # Return success response
        return {"status": "success", "message": "Webhook processed and call data stored"}
        
    except Exception as e:
        logger.error(f"❌ Error processing VAPI webhook: {e}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return {"status": "error", "message": str(e)}


async def store_call_data(db: AsyncSession, webhook_data: dict, event_type: str):
    """
    Store call data and populate all related tables in the database.
    """
    try:
        # Extract call data from VAPI webhook format
        message_data = webhook_data.get('message', {})
        call_data = message_data.get('call', {})
        vapi_call_id = call_data.get('id')
        
        if not vapi_call_id:
            logger.warning("No VAPI call ID found in webhook data")
            return
        
        # Check if call already exists using SQLAlchemy ORM
        from sqlalchemy import select
        result = await db.execute(
            select(Call).where(Call.vapi_call_id == vapi_call_id)
        )
        existing_call = result.scalar_one_or_none()
        
        if existing_call:
            # Update existing call
            await update_existing_call(db, existing_call, webhook_data, event_type)
        else:
            # Create new call record and populate related tables
            await create_new_call(db, webhook_data, event_type)
            
        # Populate related tables (with error handling) - Use separate session
        try:
            # Create a new database session for related tables to avoid transaction conflicts
            from core.database import get_db_session
            async for related_db in get_db_session():
                await populate_related_tables(related_db, webhook_data, vapi_call_id)
                break
        except Exception as e:
            logger.warning(f"⚠️ Warning: Could not populate all related tables: {e}")
            # Continue with the main call record even if related tables fail
        
        # Create audit log entry (with error handling) - TEMPORARILY DISABLED
        # try:
        #     await create_audit_log(db, webhook_data, event_type, vapi_call_id)
        # except Exception as e:
        #     logger.warning(f"⚠️ Warning: Could not create audit log: {e}")
        #     # Continue without audit log
        logger.info("📋 Audit log creation temporarily disabled")
            
        await db.commit()
        logger.info(f"✅ Call data and related tables populated successfully for call {vapi_call_id}")
        
    except Exception as e:
        logger.error(f"❌ Error storing call data: {e}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        await db.rollback()
        raise


async def create_new_call(db: AsyncSession, webhook_data: dict, event_type: str):
    """
    Create a new call record in the database.
    """
    message_data = webhook_data.get('message', {})
    call_data = message_data.get('call', {})
    customer_data = call_data.get('customer', {})
    assistant_data = call_data.get('assistant', {})
    
    # Extract call information
    vapi_call_id = call_data.get('id')
    customer_phone = customer_data.get('number', '')
    customer_name = customer_data.get('name', '')
    assistant_id = assistant_data.get('id', '')
    
    # Extract additional call details
    started_at = call_data.get('startedAt')
    ended_at = call_data.get('endedAt')
    duration_seconds = call_data.get('durationSeconds')
    cost = call_data.get('cost')
    currency = call_data.get('currency', 'USD')
    
    # Extract transcript and summary from artifact
    artifact = message_data.get('artifact', {})
    transcript = artifact.get('transcript', '')
    summary = artifact.get('summary', '')
    
    # Extract recording URL
    recording_url = artifact.get('recordingUrl', '')
    
    # Extract additional data from analysis if available
    analysis = message_data.get('analysis', {})
    outcome = analysis.get('summary', '') if analysis else ''
    
    # Determine tenant_id from assistant or use default
    tenant_id = "default_tenant"  # TODO: Extract from assistant or webhook context
    
    # Parse timestamps
    started_at_dt = None
    ended_at_dt = None
    
    if started_at:
        try:
            from dateutil import parser
            started_at_dt = parser.parse(started_at)
        except:
            started_at_dt = datetime.utcnow()
    else:
        started_at_dt = datetime.utcnow()
    
    if ended_at:
        try:
            from dateutil import parser
            ended_at_dt = parser.parse(ended_at)
        except:
            ended_at_dt = None
    
    # Create new call record
    new_call = Call(
        tenant_id=tenant_id,
        assistant_id=assistant_id,
        vapi_call_id=vapi_call_id,
        customer_phone=customer_phone,
        customer_name=customer_name,
        status=event_type,
        duration_seconds=duration_seconds,
        started_at=started_at_dt,
        ended_at=ended_at_dt,
        transcript=transcript,
        summary=summary,
        outcome=outcome,
        recording_url=recording_url,
        cost=cost,
        currency=currency,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(new_call)
    logger.info(f"📝 Created new call record: {vapi_call_id}")


async def update_existing_call(db: AsyncSession, existing_call, webhook_data: dict, event_type: str):
    """
    Update an existing call record in the database.
    """
    message_data = webhook_data.get('message', {})
    call_data = message_data.get('call', {})
    vapi_call_id = call_data.get('id')
    
    # Update call status and other fields based on event type
    if event_type == 'ended':
        # Update call end time and duration
        ended_at = call_data.get('endedAt')
        duration_seconds = call_data.get('durationSeconds')
        cost = call_data.get('cost')
        
        ended_at_dt = None
        if ended_at:
            try:
                from dateutil import parser
                ended_at_dt = parser.parse(ended_at)
            except:
                ended_at_dt = datetime.utcnow()
        else:
            ended_at_dt = datetime.utcnow()
        
        # Update using SQLAlchemy ORM
        existing_call.status = "ended"
        existing_call.ended_at = ended_at_dt
        existing_call.duration_seconds = duration_seconds
        existing_call.cost = cost
        existing_call.updated_at = datetime.utcnow()
        
    elif event_type == 'speech_update':
        # Update transcript
        speech = message_data.get('speech', {})
        transcript = speech.get('transcript', '')
        if transcript:
            existing_call.transcript = transcript
            existing_call.updated_at = datetime.utcnow()
    
    elif event_type == 'conversation_update':
        # Update transcript and summary from artifact
        artifact = message_data.get('artifact', {})
        transcript = artifact.get('transcript', '')
        summary = artifact.get('summary', '')
        
        if transcript or summary:
            if transcript:
                existing_call.transcript = transcript
            if summary:
                existing_call.summary = summary
            existing_call.updated_at = datetime.utcnow()
    
    elif event_type == 'status_update':
        # Update call status
        status = call_data.get('status', event_type)
        existing_call.status = status
        existing_call.updated_at = datetime.utcnow()
    
    logger.info(f"📝 Updated call record: {vapi_call_id}")


async def populate_related_tables(db: AsyncSession, webhook_data: dict, vapi_call_id: str):
    """
    Populate related tables (patients, assistants, phone_numbers) from webhook data.
    """
    try:
        logger.info(f"🔄 Starting related tables population for call {vapi_call_id}")
        
        message_data = webhook_data.get('message', {})
        call_data = message_data.get('call', {})
        customer_data = call_data.get('customer', {})
        assistant_data = call_data.get('assistant', {})
        phone_data = call_data.get('phoneNumber', {})
        
        logger.info(f"📋 Customer data: {customer_data}")
        logger.info(f"📋 Assistant data: {assistant_data}")
        logger.info(f"📋 Phone data: {phone_data}")
        
        # Populate patients table
        logger.info(f"👤 Creating/updating patient...")
        await create_or_update_patient(db, customer_data, vapi_call_id)
        logger.info(f"✅ Patient created/updated successfully")
        
        # Populate assistants table
        logger.info(f"🤖 Creating/updating assistant...")
        await create_or_update_assistant(db, assistant_data, vapi_call_id)
        logger.info(f"✅ Assistant created/updated successfully")
        
        # Populate phone_numbers table
        logger.info(f"📞 Creating/updating phone number...")
        await create_or_update_phone_number(db, phone_data, vapi_call_id)
        logger.info(f"✅ Phone number created/updated successfully")
        
        logger.info(f"✅ All related tables populated for call {vapi_call_id}")
        
    except Exception as e:
        logger.error(f"❌ Error populating related tables: {e}")
        logger.error(f"❌ Error type: {type(e).__name__}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        raise


async def create_or_update_patient(db: AsyncSession, customer_data: dict, vapi_call_id: str):
    """
    Create or update patient record from customer data.
    """
    try:
        if not customer_data:
            return
            
        customer_phone = customer_data.get('number', '')
        customer_name = customer_data.get('name', '')
        
        if not customer_phone:
            return
            
        # Check if patient already exists
        from sqlalchemy import select
        result = await db.execute(
            select(Patient).where(Patient.phone == customer_phone)
        )
        existing_patient = result.scalar_one_or_none()
        
        if existing_patient:
            # Update existing patient
            if customer_name and not existing_patient.first_name:
                # Split name into first and last name
                name_parts = customer_name.split(' ', 1)
                existing_patient.first_name = name_parts[0]
                if len(name_parts) > 1:
                    existing_patient.last_name = name_parts[1]
            existing_patient.updated_at = datetime.utcnow()
            logger.info(f"📝 Updated patient record for phone {customer_phone}")
        else:
            # Split name into first and last name
            name_parts = (customer_name or f"Patient {customer_phone}").split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ""
            
            # Create new patient with default clinic
            new_patient = Patient(
                tenant_id="default_tenant",
                clinic_id="default_clinic",
                first_name=first_name,
                last_name=last_name,
                phone=customer_phone,
                email=None,
                date_of_birth=None,
                address=None,
                insurance_provider=None,
                insurance_number=None,
                emergency_contact_name=None,
                emergency_contact_phone=None,
                preferred_communication=None,
                notes=None,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(new_patient)
            logger.info(f"👤 Created new patient record for phone {customer_phone}")
            
    except Exception as e:
        logger.error(f"❌ Error creating/updating patient: {e}")
        raise


async def create_or_update_assistant(db: AsyncSession, assistant_data: dict, vapi_call_id: str):
    """
    Create or update assistant record from assistant data.
    """
    try:
        if not assistant_data:
            return
            
        assistant_id = assistant_data.get('id', '')
        assistant_name = assistant_data.get('name', '')
        
        if not assistant_id:
            return
            
        # Check if assistant already exists
        from sqlalchemy import select
        result = await db.execute(
            select(Assistant).where(Assistant.vapi_assistant_id == assistant_id)
        )
        existing_assistant = result.scalar_one_or_none()
        
        if existing_assistant:
            # Update existing assistant
            if assistant_name and not existing_assistant.name:
                existing_assistant.name = assistant_name
            existing_assistant.updated_at = datetime.utcnow()
            logger.info(f"📝 Updated assistant record for ID {assistant_id}")
        else:
            # Create new assistant (simplified - no clinic_id)
            new_assistant = Assistant(
                tenant_id="default_tenant",
                name=assistant_name or f"Assistant {assistant_id}",
                vapi_assistant_id=assistant_id,
                model_id="gpt-4o",  # Default model
                voice_id="default-voice",  # Default voice
                status="active",
                config=None,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(new_assistant)
            logger.info(f"🤖 Created new assistant record for ID {assistant_id}")
            
    except Exception as e:
        logger.error(f"❌ Error creating/updating assistant: {e}")
        raise


async def create_or_update_phone_number(db: AsyncSession, phone_data: dict, vapi_call_id: str):
    """
    Create or update phone number record from phone data.
    """
    try:
        if not phone_data:
            return
            
        phone_id = phone_data.get('id', '')
        phone_number = phone_data.get('number', '')
        phone_name = phone_data.get('name', '')
        
        if not phone_id or not phone_number:
            return
            
        # Check if phone number already exists
        from sqlalchemy import select
        result = await db.execute(
            select(PhoneNumber).where(PhoneNumber.vapi_phone_id == phone_id)
        )
        existing_phone = result.scalar_one_or_none()
        
        if existing_phone:
            # Update existing phone number
            existing_phone.updated_at = datetime.utcnow()
            logger.info(f"📝 Updated phone number record for ID {phone_id}")
        else:
            # Create new phone number
            new_phone = PhoneNumber(
                tenant_id="default_tenant",
                assistant_id=None,  # TODO: Link to assistant if available
                phone_number=phone_number,
                vapi_phone_id=phone_id,
                status="active",
                provider="vapi",
                monthly_cost=None,
                setup_cost=None,
                activated_at=datetime.utcnow(),
                deactivated_at=None,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(new_phone)
            logger.info(f"📞 Created new phone number record for {phone_number}")
            
    except Exception as e:
        logger.error(f"❌ Error creating/updating phone number: {e}")
        raise


async def create_audit_log(db: AsyncSession, webhook_data: dict, event_type: str, vapi_call_id: str):
    """
    Create audit log entry for webhook event.
    """
    try:
        audit_log = AuditLog(
            user_id=None,  # System event
            clinic_id=None,  # System event
            action=AuditAction.CREATE if event_type == 'call-started' else AuditAction.UPDATE,
            resource_type=AuditResource.SYSTEM,
            resource_id=vapi_call_id,
            details={
                "webhook_type": event_type,
                "vapi_call_id": vapi_call_id,
                "resource_type": "call",
                "timestamp": datetime.utcnow().isoformat()
            },
            ip_address="127.0.0.1",  # Webhook source
            user_agent="VAPI-Webhook",
            created_at=datetime.utcnow()
        )
        db.add(audit_log)
        logger.info(f"📋 Created audit log for webhook event {event_type}")
        
    except Exception as e:
        logger.error(f"❌ Error creating audit log: {e}")
        raise


@router.get("/availability")
async def get_availability(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    service_type: Optional[str] = None,
    current_user: AuthUser = Depends(get_current_user)
):
    """Get available appointment slots. Uses mock data when Google Calendar is not configured."""
    try:
        # Check if Google Calendar is configured
        from backend.core.config import settings
        access_token = getattr(settings, 'GOOGLE_CALENDAR_ACCESS_TOKEN', None)
        
        if not access_token:
            # Return mock availability data when Google Calendar is not configured
            logger.info("📅 Google Calendar not configured, returning mock availability data")
            return {
                "status": "success",
                "message": "Using mock availability data (Google Calendar not configured)",
                "available_slots": generate_mock_availability_slots(date_from, date_to, service_type)
            }
        
        # Google Calendar FreeBusy API endpoint
        url = "https://www.googleapis.com/calendar/v3/freeBusy"
        
        # Request payload
        payload = {
            "timeMin": date_from or "2025-08-30T04:00:00Z",
            "timeMax": date_to or "2025-08-31T03:59:59Z",
            "timeZone": "America/New_York",
            "items": [
                {"id": "primary"}
            ]
        }
        
        # Headers including the Bearer token
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Make the request to Google Calendar API
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            calendar_data = response.json()
            return {
                "status": "success",
                "calendar_data": calendar_data,
                "available_slots": process_calendar_response(calendar_data)
            }
        else:
            logger.error(f"Google Calendar API error: {response.status_code} - {response.text}")
            # Fallback to mock data on API error
            return {
                "status": "success",
                "message": "Google Calendar API error, using mock data",
                "available_slots": generate_mock_availability_slots(date_from, date_to, service_type)
            }
            
    except Exception as e:
        logger.error(f"Error getting availability: {e}")
        # Fallback to mock data on any error
        return {
            "status": "success",
            "message": "Error occurred, using mock availability data",
            "available_slots": generate_mock_availability_slots(date_from, date_to, service_type)
        }


@router.post("/appointments")
async def create_appointment(
    appointment_data: AppointmentRequest,
    current_user: AuthUser = Depends(get_current_user)
):
    """Create a new appointment and add it to Google Calendar."""
    try:
        # Step 1: Check for conflicts before creating appointment
        logger.info(f"🔍 Checking availability for {appointment_data.appointment_date} at {appointment_data.appointment_time}")
        
        # Get current calendar data to check for conflicts
        from datetime import datetime, timedelta
        from zoneinfo import ZoneInfo
        
        # Calculate the time range for the appointment date
        est_tz = ZoneInfo("America/New_York")
        appointment_date = datetime.strptime(appointment_data.appointment_date, "%Y-%m-%d")
        appointment_date = appointment_date.replace(tzinfo=est_tz)
        
        # Convert to UTC for Google Calendar API query
        utc_date = appointment_date.astimezone(ZoneInfo("UTC"))
        time_min = utc_date.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        time_max = (utc_date + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        
        # Query Google Calendar for busy times on this date
        from backend.core.config import settings
        access_token = getattr(settings, 'GOOGLE_CALENDAR_ACCESS_TOKEN', None)
        
        if not access_token:
            # Use mock appointment creation when Google Calendar is not configured
            logger.info("📅 Google Calendar not configured, creating mock appointment")
            import uuid
            appointment_id = str(uuid.uuid4())
            
            return AppointmentResponse(
                status="success",
                appointment_id=appointment_id,
                message=f"Mock appointment created for {appointment_data.patient_name} on {appointment_data.appointment_date} at {appointment_data.appointment_time} (Google Calendar not configured)",
                calendar_event_id=f"mock_event_{appointment_id}"
            )
        
        # Google Calendar FreeBusy API endpoint
        freebusy_url = "https://www.googleapis.com/calendar/v3/freeBusy"
        
        freebusy_payload = {
            "timeMin": time_min,
            "timeMax": time_max,
            "timeZone": "America/New_York",
            "items": [{"id": "primary"}]
        }
        
        freebusy_headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Check for conflicts
        freebusy_response = requests.post(freebusy_url, json=freebusy_payload, headers=freebusy_headers)
        
        if freebusy_response.status_code == 200:
            calendar_data = freebusy_response.json()
            busy_times = calendar_data.get("calendars", {}).get("primary", {}).get("busy", [])
            
            # Check if the requested slot conflicts with existing appointments
            slot_availability = check_slot_availability(
                appointment_data.appointment_date, 
                appointment_data.appointment_time, 
                busy_times
            )
            
            if not slot_availability["available"]:
                logger.warning(f"⚠️  Conflict detected: {slot_availability['conflict_reason']}")
                raise HTTPException(
                    status_code=409, 
                    detail={
                        "error": "Slot not available",
                        "conflict_reason": slot_availability["conflict_reason"],
                        "conflicting_appointment": slot_availability["conflicting_appointment"],
                        "requested_slot": f"{appointment_data.appointment_date} {appointment_data.appointment_time}"
                    }
                )
            
            logger.info(f"✅ Slot availability confirmed - no conflicts detected")
        else:
            logger.error(f"❌ Failed to check availability: {freebusy_response.status_code}")
            raise HTTPException(status_code=500, detail="Failed to check appointment availability")
        
        # Step 2: Create the appointment (slot is confirmed available)
        # Google Calendar Events API endpoint
        url = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
        
        # Convert appointment date/time to proper format
        from datetime import datetime, timedelta
        from zoneinfo import ZoneInfo


        # Parse the appointment date and time
        date_str = appointment_data.appointment_date
        time_str = appointment_data.appointment_time
        
        # Convert to EST datetime
        est_tz = ZoneInfo("America/New_York")
        appointment_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %I:%M %p")
        appointment_datetime = appointment_datetime.replace(tzinfo=est_tz)
        
        # Convert to UTC for Google Calendar API
        utc_datetime = appointment_datetime.astimezone(ZoneInfo("UTC"))
        end_datetime = utc_datetime + timedelta(minutes=appointment_data.duration)
        
        # Format for Google Calendar API (RFC3339)
        start_time_rfc3339 = utc_datetime.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        end_time_rfc3339 = end_datetime.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        
        # Create the event payload
        event_payload = {
            "summary": f"Dental Appointment - {appointment_data.patient_name}",
            "description": f"Service: {appointment_data.service_type}\nPhone: {appointment_data.patient_phone}\nNotes: {appointment_data.notes or 'No additional notes'}",
            "start": {
                "dateTime": start_time_rfc3339,
                "timeZone": "America/New_York"
            },
            "end": {
                "dateTime": end_time_rfc3339,
                "timeZone": "America/New_York"
            },
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "email", "minutes": 24 * 60},  # 24 hours before
                    {"method": "popup", "minutes": 60}  # 1 hour before
                ]
            }
        }
        
        # Headers for the request
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Make the request to create the event
        response = requests.post(url, json=event_payload, headers=headers)
        
        if response.status_code == 200:
            event_data = response.json()
            calendar_event_id = event_data.get("id")
            
            # Generate a unique appointment ID
            import uuid
            appointment_id = str(uuid.uuid4())
            
            logger.info(f"✅ Appointment created successfully: {appointment_id}")
            logger.info(f"📅 Google Calendar Event ID: {calendar_event_id}")
            logger.info(f"👤 Patient: {appointment_data.patient_name}")
            logger.info(f"📅 Date/Time: {appointment_data.appointment_date} {appointment_data.appointment_time}")
            
            return AppointmentResponse(
                status="success",
                appointment_id=appointment_id,
                message=f"Appointment created successfully for {appointment_data.patient_name} on {appointment_data.appointment_date} at {appointment_data.appointment_time}",
                calendar_event_id=calendar_event_id
            )
        else:
            logger.error(f"❌ Failed to create Google Calendar event: {response.status_code} - {response.text}")
            raise HTTPException(status_code=500, detail="Failed to create appointment in Google Calendar")
            
    except Exception as e:
        logger.error(f"Error creating appointment: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create appointment: {str(e)}")


def process_calendar_response(calendar_data):
    """Convert Google Calendar FreeBusy response to available slots."""
    try:
        from datetime import datetime
        from zoneinfo import ZoneInfo
        
        # Extract time range and convert to EST
        time_min = calendar_data.get("timeMin", "")
        time_max = calendar_data.get("timeMax", "")
        
        # Convert UTC to EST
        if time_min and time_max:
            # Parse UTC time and convert to EST
            utc_min = datetime.fromisoformat(time_min.replace('Z', '+00:00'))
            utc_max = datetime.fromisoformat(time_max.replace('Z', '+00:00'))
            
            est_tz = ZoneInfo("America/New_York")
            est_min = utc_min.astimezone(est_tz)
            est_max = utc_max.astimezone(est_tz)
            
            logger.info(f"📅 Calendar query: {est_min.strftime('%Y-%m-%d %I:%M %p %Z')} to {est_max.strftime('%Y-%m-%d %I:%M %p %Z')}")
        
        # Process calendars
        calendars = calendar_data.get("calendars", {})
        
        for calendar_id, calendar_info in calendars.items():
            logger.info(f"📋 Processing calendar: {calendar_id}")
            
            busy_times = calendar_info.get("busy", [])
            
            if not busy_times:
                logger.info(f"✅ Calendar {calendar_id} has no busy times - all slots available!")
            else:
                logger.info(f"🚫 Calendar {calendar_id} has {len(busy_times)} busy periods:")
                for busy_period in busy_times:
                    start_time = busy_period.get("start", "")
                    end_time = busy_period.get("end", "")
                    
                    if start_time and end_time:
                        # Convert busy times to EST
                        utc_start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                        utc_end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                        
                        est_start = utc_start.astimezone(est_tz)
                        est_end = utc_end.astimezone(est_tz)
                        
                        logger.info(f"🕐 Busy: {est_start.strftime('%Y-%m-%d %I:%M %p %Z')} to {est_end.strftime('%Y-%m-%d %I:%M %p %Z')}")
        
        # Generate real available slots for the date range, excluding busy times
        available_slots = generate_available_slots_for_date_range(time_min, time_max, busy_times)
        
        return available_slots
        
    except Exception as e:
        logger.error(f"Error processing calendar response: {e}")
        return generate_available_slots_for_date_range(time_min, time_max, [])


def check_slot_availability(appointment_date: str, appointment_time: str, busy_times: list = None) -> dict:
    """Check if a specific slot is available, given busy times."""
    try:
        from datetime import datetime, timedelta
        from zoneinfo import ZoneInfo
        
        # Convert to EST timezone
        est_tz = ZoneInfo("America/New_York")
        
        # Parse the appointment date and time
        appointment_datetime = datetime.strptime(f"{appointment_date} {appointment_time}", "%Y-%m-%d %I:%M %p")
        appointment_datetime = appointment_datetime.replace(tzinfo=est_tz)
        
        # Calculate slot end time
        slot_end_time = appointment_datetime + timedelta(hours=1)
        
        # Parse busy times to EST for comparison
        if busy_times:
            for busy_period in busy_times:
                start_time = busy_period.get("start", "")
                end_time = busy_period.get("end", "")
                
                if start_time and end_time:
                    # Handle both Z and -04:00 formats
                    if start_time.endswith('Z'):
                        start_time = start_time.replace('Z', '+00:00')
                    if end_time.endswith('Z'):
                        end_time = end_time.replace('Z', '+00:00')
                    
                    try:
                        utc_start = datetime.fromisoformat(start_time)
                        utc_end = datetime.fromisoformat(end_time)
                        
                        est_start = utc_start.astimezone(est_tz)
                        est_end = utc_end.astimezone(est_tz)
                        
                        # Check if there's any overlap between slot and busy period
                        if (appointment_datetime < est_end and slot_end_time > est_start):
                            return {
                                "available": False,
                                "conflict_reason": f"Conflicts with existing appointment: {est_start.strftime('%I:%M %p')} - {est_end.strftime('%I:%M %p')}",
                                "conflicting_appointment": {
                                    "start": est_start.strftime("%I:%M %p"),
                                    "end": est_end.strftime("%I:%M %p")
                                }
                            }
                    except Exception as e:
                        logger.error(f"Error parsing busy time: {e}")
        
        # If no conflicts found, slot is available
        return {
            "available": True,
            "conflict_reason": None,
            "conflicting_appointment": None
        }
        
    except Exception as e:
        logger.error(f"Error checking slot availability: {e}")
        return {
            "available": False,
            "conflict_reason": f"Error checking availability: {str(e)}",
            "conflicting_appointment": None
        }


def generate_available_slots_for_date_range(time_min: str, time_max: str, busy_times: list = None) -> list:
    """Generate available appointment slots for the given date range, excluding busy times."""
    try:
        from datetime import datetime, timedelta
        from zoneinfo import ZoneInfo
        
        # Parse the time range
        start_date = datetime.fromisoformat(time_min.replace('Z', '+00:00'))
        end_date = datetime.fromisoformat(time_max.replace('Z', '+00:00'))
        
        # Convert to EST timezone
        est_tz = ZoneInfo("America/New_York")
        start_date_est = start_date.astimezone(est_tz)
        end_date_est = end_date.astimezone(est_tz)
        
        # Business hours: 9 AM - 5 PM EST
        business_start_hour = 9
        business_end_hour = 17
        
        available_slots = []
        slot_id_counter = 1
        
        # Parse busy times to EST for comparison
        busy_periods_est = []
        if busy_times:
            for busy_period in busy_times:
                start_time = busy_period.get("start", "")
                end_time = busy_period.get("end", "")
                
                if start_time and end_time:
                    # Handle both Z and -04:00 formats
                    if start_time.endswith('Z'):
                        start_time = start_time.replace('Z', '+00:00')
                    if end_time.endswith('Z'):
                        end_time = end_time.replace('Z', '+00:00')
                    
                    try:
                        utc_start = datetime.fromisoformat(start_time)
                        utc_end = datetime.fromisoformat(end_time)
                        
                        est_start = utc_start.astimezone(est_tz)
                        est_end = utc_end.astimezone(est_tz)
                        
                        busy_periods_est.append((est_start, est_end))
                        logger.info(f"🚫 Busy period: {est_start.strftime('%Y-%m-%d %I:%M %p %Z')} to {est_end.strftime('%Y-%m-%d %I:%M %p %Z')}")
                    except Exception as e:
                        logger.error(f"Error parsing busy time: {e}")
        
        # Generate slots for each day in the range
        current_date = start_date_est.replace(hour=business_start_hour, minute=0, second=0, microsecond=0)
        
        while current_date <= end_date_est:
            # Process all days (including weekends for now)
            day_name = current_date.strftime("%A")
            logger.info(f"📅 Processing {current_date.strftime('%Y-%m-%d')} ({day_name})")
            
            # Generate hourly slots for this day
            for hour in range(business_start_hour, business_end_hour):
                slot_time = current_date.replace(hour=hour)
                slot_end_time = slot_time + timedelta(hours=1)
                
                # Check if this slot conflicts with any busy period
                is_available = True
                conflict_reason = None
                
                for busy_start, busy_end in busy_periods_est:
                    # Check if there's any overlap between slot and busy period
                    if (slot_time < busy_end and slot_end_time > busy_start):
                        is_available = False
                        conflict_reason = f"Conflicts with existing appointment: {busy_start.strftime('%I:%M %p')} - {busy_end.strftime('%I:%M %p')}"
                        logger.info(f"   ⚠️  Slot {slot_time.strftime('%I:%M %p')} conflicts with busy period")
                        break
                
                available_slots.append({
                    "slot_id": f"slot_{slot_id_counter}",
                    "date": slot_time.strftime("%Y-%m-%d"),
                    "time": slot_time.strftime("%I:%M %p"),
                    "duration": 60,
                    "available": is_available,
                    "timezone": "EST",
                    "day_of_week": day_name,
                    "conflict_reason": conflict_reason
                })
                slot_id_counter += 1
            
            # Move to next day
            current_date += timedelta(days=1)
        
        # Count available vs unavailable slots
        available_count = sum(1 for slot in available_slots if slot["available"])
        unavailable_count = len(available_slots) - available_count
        
        logger.info(f"🎯 Generated {len(available_slots)} total slots: {available_count} available, {unavailable_count} unavailable")
        return available_slots
        
    except Exception as e:
        logger.error(f"Error generating available slots: {e}")
        # Fallback to sample data
        return [
            {
                "slot_id": "slot_1",
                "date": "2025-08-30",
                "time": "9:00 AM",
                "duration": 60,
                "available": True,
                "timezone": "EST"
            }
        ]


def generate_mock_availability_slots(date_from: Optional[str] = None, date_to: Optional[str] = None, service_type: Optional[str] = None):
    """Generate mock availability slots when Google Calendar is not configured."""
    from datetime import datetime, timedelta
    
    # Default to next 7 days if no date range specified
    if not date_from:
        date_from = datetime.now().strftime("%Y-%m-%d")
    if not date_to:
        date_to = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    
    # Parse dates
    start_date = datetime.strptime(date_from, "%Y-%m-%d")
    end_date = datetime.strptime(date_to, "%Y-%m-%d")
    
    # Business hours (9 AM to 5 PM)
    business_hours = [9, 10, 11, 12, 13, 14, 15, 16]  # 9 AM to 4 PM (last slot starts at 4 PM)
    
    available_slots = []
    slot_id = 1
    
    current_date = start_date
    while current_date <= end_date:
        # Skip weekends for mock data
        if current_date.weekday() < 5:  # Monday = 0, Friday = 4
            for hour in business_hours:
                slot_time = current_date.replace(hour=hour, minute=0, second=0, microsecond=0)
                
                available_slots.append({
                    "slot_id": f"mock_slot_{slot_id}",
                    "date": slot_time.strftime("%Y-%m-%d"),
                    "time": slot_time.strftime("%I:%M %p"),
                    "duration": 60,
                    "available": True,
                    "timezone": "EST",
                    "service_type": service_type or "General Checkup"
                })
                slot_id += 1
        
        current_date += timedelta(days=1)
    
    logger.info(f"📅 Generated {len(available_slots)} mock availability slots")
    return available_slots