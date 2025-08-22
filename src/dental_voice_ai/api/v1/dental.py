from fastapi import APIRouter, Request, HTTPException
from dental_voice_ai.core.database import supabase, safe_supabase_insert
from dental_voice_ai.intelligence.dental_faq_matcher import (
    DentalFAQMatcher,
    create_practice_config_from_db_record,
    identify_practice_from_vapi_data
)
from dental_voice_ai.core.schemas import IntentType, WebhookResponse, IntentAnalysisRequest, IntentAnalysisResponse, IntentAnalysisResult, ResponseData, PracticeInfo
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()


async def _fetch_available_slots(
    tenant_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    request_id: str = "unknown"
) -> Dict[str, Any]:
    """
    Fetch available appointment slots from the database.
    
    Args:
        tenant_id: UUID of the dental practice
        start_date: Start date for search (YYYY-MM-DD)
        end_date: End date for search (YYYY-MM-DD)
        request_id: Unique request identifier for tracking
        
    Returns:
        Dict with available slots information
    """
    try:
        logger.info(f"📅 [{request_id}] Fetching available slots")
        
        # Set default date range if not provided
        if not start_date:
            start_date = datetime.now().date().isoformat()
        if not end_date:
            end_date = (datetime.now().date() + timedelta(days=7)).isoformat()
        
        # Build query
        query = supabase.table("office_availabilities").select("*")
        
        # Skip tenant_id filter if it's a placeholder or invalid
        if tenant_id and tenant_id != "{{tenant_id}}" and tenant_id != "NULL" and len(tenant_id) > 10:
            try:
                query = query.eq("tenant_id", tenant_id)
                logger.info(f"🔍 [{request_id}] Filtering by tenant_id: {tenant_id}")
            except Exception as e:
                logger.warning(f"⚠️ [{request_id}] Invalid tenant_id format, skipping filter: {tenant_id}")
        else:
            logger.info(f"🔍 [{request_id}] No valid tenant_id provided, showing all available slots")
        
        query = query.eq("available", True)
        query = query.gte("date", start_date)
        query = query.lte("date", end_date)
        query = query.order("date", desc=False)
        query = query.order("start_time", desc=False)
        
        response = query.execute()
        
        if response and response.data:
            # Format available slots for display
            available_slots = []
            for slot in response.data:
                date_obj = datetime.strptime(slot["date"], "%Y-%m-%d")
                formatted_date = date_obj.strftime("%A, %B %d")
                formatted_time = slot["start_time"]
                
                available_slots.append(f"{formatted_date} at {formatted_time}")
            
            slots_text = ", ".join(available_slots)
            
            logger.info(f"✅ [{request_id}] Found {len(available_slots)} available slots")
            
            result = {
                "success": True,
                "available_slots": f"Available slots: {slots_text}",
                "message": f"Found {len(available_slots)} available appointment times"
            }
            
            # Log the result structure
            logger.info(f"🔍 [{request_id}] Result structure: {json.dumps(result, indent=2)}")
            
            return result
        else:
            logger.warning(f"⚠️ [{request_id}] No available slots found")
            return {
                "success": False,
                "available_slots": "No available slots found for the requested dates",
                "message": "No available appointments in the selected date range"
            }
            
    except Exception as e:
        logger.error(f"🔴 [{request_id}] Error fetching available slots: {e}")
        return {
            "success": False,
            "available_slots": "Error retrieving available slots",
            "message": "Unable to fetch appointment availability"
        }


@router.get("/availability")
async def get_appointment_availability(
    tenant_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    GET endpoint for retrieving available appointment slots.
    
    Args:
        tenant_id: UUID of the dental practice
        start_date: Start date for search (YYYY-MM-DD)
        end_date: End date for search (YYYY-MM-DD)
        
    Returns:
        Available appointment slots information
    """
    request_id = f"availability_{int(time.time())}"
    
    try:
        result = await _fetch_available_slots(
            tenant_id=tenant_id,
            start_date=start_date,
            end_date=end_date,
            request_id=request_id
        )
        
        # Log the result being returned
        logger.info(f"🔍 [{request_id}] API Response being returned: {json.dumps(result, indent=2)}")
        
        return result
        
    except Exception as e:
        logger.error(f"🔴 [{request_id}] Error in availability endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/appointment_store")
async def store_appointment(request: Request):
    """
    POST endpoint for storing appointment data from VAPI.
    
    Accepts VAPI function call format with appointment data in function.arguments.
    """
    request_id = f"store_appointment_{int(time.time())}"
    try:
        payload = await request.json()
        logger.info(f"📝 [{request_id}] Processing appointment storage request")
        appointment_data = {}
        if "function" in payload and "arguments" in payload.get("function", {}):
            try:
                arguments_str = payload["function"]["arguments"]
                arguments = json.loads(arguments_str)
                appointment_data = arguments
                logger.info(f"📋 [{request_id}] Extracted data from function arguments: {appointment_data}")
            except json.JSONDecodeError as e:
                logger.warning(f"⚠️ [{request_id}] Failed to parse function arguments: {e}")
                logger.warning(f"⚠️ [{request_id}] Raw arguments string: {arguments_str}")
        logger.info(f"🔍 [{request_id}] Full payload structure: {json.dumps(payload, indent=2)}")
        logger.info(f"🔍 [{request_id}] Extracted appointment_data: {appointment_data}")

        if not appointment_data:
            direct_fields = ["patient_name", "phone_number", "appointment_date", "appointment_time", "reason"]
            if any(field in payload for field in direct_fields):
                appointment_data = {field: payload.get(field) for field in direct_fields if payload.get(field)}
                logger.info(f"📋 [{request_id}] Extracted data directly from payload: {appointment_data}")

        required_fields = [
            ("patient_name",),
            ("phone_number",),
            ("appointment_date",),
            ("appointment_time",)
        ]
        missing_fields = []
        for field_group in required_fields:
            field_found = False
            for field in field_group:
                if appointment_data.get(field):
                    field_found = True
                    break
            if not field_found:
                missing_fields.append(field_group[0])

        if missing_fields:
            error_msg = f"Missing required fields: {', '.join(missing_fields)}"
            logger.error(f"🔴 [{request_id}] {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)

        patient_name = appointment_data.get("patient_name")
        phone_number = appointment_data.get("phone_number")
        appointment_date = appointment_data.get("appointment_date")
        appointment_time = appointment_data.get("appointment_time")
        reason = appointment_data.get("reason", "Dental appointment")
        tenant_id = appointment_data.get("tenant_id", "5f26e6b8-0c41-4e84-9a22-560dcb1dd8a3")
        notes = appointment_data.get("notes", "")

        try:
            if appointment_date and appointment_time:
                datetime_formats = [
                    "%Y-%m-%d %H:%M",
                    "%Y-%m-%d %H:%M:%S",
                    "%A, %B %d %H:%M:%S",
                    "%A, %B %d %H:%M"
                ]
                datetime_str = f"{appointment_date} {appointment_time}"
                appointment_datetime = None
                for fmt in datetime_formats:
                    try:
                        appointment_datetime = datetime.strptime(datetime_str, fmt)
                        logger.info(f"✅ [{request_id}] Parsed datetime using format: {fmt}")
                        break
                    except ValueError:
                        continue
                if not appointment_datetime:
                    raise ValueError(f"Could not parse datetime: {datetime_str}")
            else:
                raise ValueError("Missing date or time")
        except ValueError as e:
            error_msg = f"Invalid appointment date/time format: {e}"
            logger.error(f"🔴 [{request_id}] {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)

        appointment_record = {
            "tenant_id": tenant_id,
            "caller_name": patient_name,
            "caller_number": phone_number,
            "appointment_time": appointment_datetime.isoformat(),
            "reason": reason,
            "status": "scheduled",
            "created_at": datetime.utcnow().isoformat()
        }

        inserted_record = safe_supabase_insert("appointment_requests", appointment_record, request_id)

        if inserted_record:
            appointment_id = inserted_record.get('id', 'unknown')
            logger.info(f"✅ [{request_id}] Appointment stored successfully")
            logger.info(f"   - Appointment ID: {appointment_id}")
            logger.info(f"   - Patient: {patient_name}")
            logger.info(f"   - Date: {appointment_date} at {appointment_time}")

            result = {
                "success": True,
                "message": f"Appointment stored successfully. Appointment ID: {appointment_id}",
                "appointment_id": appointment_id,
                "patient_name": patient_name,
                "appointment_date": appointment_date,
                "appointment_time": appointment_time
            }
            return result
        else:
            logger.error(f"🔴 [{request_id}] Failed to store appointment")
            return {
                "success": False,
                "message": "Failed to store appointment in database"
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"🔴 [{request_id}] Error storing appointment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/incoming_call")
async def vapi_webhook(request: Request) -> WebhookResponse:
    """
    VAPI webhook handler for incoming dental calls.
    
    Processes call transcripts and returns AI-generated responses.
    """
    request_id = f"webhook_{int(time.time())}"
    
    try:
        payload = await request.json()
        logger.info(f"📞 [{request_id}] Processing VAPI webhook")
        
        # Extract call data
        call_data = _extract_vapi_call_data(payload, request_id)
        
        # Identify practice
        practice_config = None
        if call_data.get("phone_number"):
            practice_config = await _get_practice_config(call_data["phone_number"], request_id)
        
        # Analyze intent
        intent_result = await faq_matcher.analyze_transcript(
            call_data["transcript"], 
            practice_config
        )
        
        # Generate response
        final_response_text = intent_result.suggested_response
        
        # Prepare comprehensive response for VAPI
        response = WebhookResponse(
            status="processed",
            call_id=call_data.get("call_id") or "unknown",
            event_type="incoming_call",
            processed=True,
            intent_analysis=IntentAnalysisResult(
                intent=intent_result.intent,
                confidence=intent_result.confidence,
                matched_keywords=intent_result.matched_keywords,
                extracted_entities=intent_result.extracted_entities,
                tenant_specific=intent_result.tenant_specific,
                faq_matched=intent_result.faq_matched
            ),
            practice_info=PracticeInfo(
                identified=bool(practice_config),
                name=practice_config.name if practice_config else None,
                practice_id=practice_config.practice_id if practice_config else None
            )
        )
        
        # Log call data
        await _log_call_data(call_data, intent_result, final_response_text, request_id)
        
        logger.info(f"✅ [{request_id}] Webhook processed successfully")
        return response
        
    except Exception as e:
        logger.error(f"🔴 [{request_id}] Webhook processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/incoming_call")
async def webhook_availability():
    """
    VAPI availability check endpoint.
    """
    return {"status": "available", "message": "Dental Voice AI webhook is ready"}


@router.post("/analyze_intent")
async def analyze_intent(request: IntentAnalysisRequest) -> IntentAnalysisResponse:
    """
    Standalone intent analysis endpoint.
    """
    request_id = f"intent_{int(time.time())}"
    
    try:
        # Get practice config if tenant_id provided
        practice_config = None
        if request.tenant_id:
            practice_config = await _get_practice_config_by_id(request.tenant_id, request_id)
        
        # Analyze intent
        intent_result = await faq_matcher.analyze_transcript(
            request.transcript, 
            practice_config
        )
        
        # Create response
        response = IntentAnalysisResponse(
            status="analyzed",
            request_id=request_id,
            transcript_length=len(request.transcript),
            intent_analysis=IntentAnalysisResult(
                intent=intent_result.intent,
                confidence=intent_result.confidence,
                matched_keywords=intent_result.matched_keywords,
                extracted_entities=intent_result.extracted_entities,
                tenant_specific=intent_result.tenant_specific,
                faq_matched=intent_result.faq_matched
            ),
            response=ResponseData(
                text=intent_result.suggested_response,
                should_speak=True,
                end_call=False
            ),
            practice_info=PracticeInfo(
                identified=bool(practice_config),
                name=practice_config.name if practice_config else None,
                practice_id=practice_config.practice_id if practice_config else None
            )
        )
        
        logger.info(f"✅ [{request_id}] Intent analysis completed")
        return response
        
    except Exception as e:
        logger.error(f"🔴 [{request_id}] Intent analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _extract_vapi_call_data(payload: Dict[str, Any], request_id: str) -> Dict[str, Any]:
    """Extract call data from VAPI webhook payload."""
    try:
        # Extract from messages if available
        messages = payload.get("messages", [])
        transcript = ""
        tool_call_id = None
        
        for message in messages:
            if message.get("type") == "user":
                transcript = message.get("content", "")
            elif message.get("type") == "tool-call":
                tool_call_id = message.get("toolCallId")
        
        # Extract metadata
        call_data = {
            "transcript": transcript,
            "tool_call_id": tool_call_id,
            "phone_number": payload.get("phoneNumber"),
            "assistant_id": payload.get("assistantId"),
            "call_id": payload.get("id")
        }
        
        logger.info(f"📋 [{request_id}] Extracted call data: {call_data}")
        return call_data
        
    except Exception as e:
        logger.error(f"🔴 [{request_id}] Error extracting call data: {e}")
        return {"transcript": "", "tool_call_id": None}


async def _get_practice_config(phone_number: str, request_id: str) -> Optional[Any]:
    """Get practice configuration by phone number."""
    try:
        # Query database for practice by phone number
        response = supabase.table("tenants").select("*").eq("phone_number", phone_number).execute()
        
        if response and response.data:
            practice_record = response.data[0]
            practice_config = create_practice_config_from_db_record(practice_record)
            logger.info(f"🏥 [{request_id}] Found practice: {practice_config.name}")
            return practice_config
        else:
            logger.warning(f"⚠️ [{request_id}] No practice found for phone: {phone_number}")
            return None
            
    except Exception as e:
        logger.error(f"🔴 [{request_id}] Error getting practice config: {e}")
        return None


async def _get_practice_config_by_id(tenant_id: str, request_id: str) -> Optional[Any]:
    """Get practice configuration by tenant ID."""
    try:
        response = supabase.table("tenants").select("*").eq("id", tenant_id).execute()
        
        if response and response.data:
            practice_record = response.data[0]
            practice_config = create_practice_config_from_db_record(practice_record)
            logger.info(f"🏥 [{request_id}] Found practice by ID: {practice_config.name}")
            return practice_config
        else:
            logger.warning(f"⚠️ [{request_id}] No practice found for ID: {tenant_id}")
            return None
            
    except Exception as e:
        logger.error(f"🔴 [{request_id}] Error getting practice config by ID: {e}")
        return None


async def _log_call_data(
    call_data: Dict[str, Any], 
    intent_result: Any, 
    response_text: str, 
    request_id: str
):
    """Log call data to database."""
    try:
        log_record = {
            "tenant_id": None,  # Will be updated if practice found
            "caller_number": call_data.get("phone_number", ""),
            "status": "completed",
            "transcript": call_data.get("transcript", ""),
            "intent": intent_result.intent.value,
            "intent_confidence": intent_result.confidence,
            "faq_matched": intent_result.faq_matched,
            "response_text": response_text,
            "created_at": datetime.utcnow().isoformat()
        }
        
        safe_supabase_insert("calls", log_record, request_id)
        logger.info(f"📝 [{request_id}] Call data logged successfully")
        
    except Exception as e:
        logger.error(f"🔴 [{request_id}] Error logging call data: {e}")


# Initialize FAQ matcher
faq_matcher = DentalFAQMatcher()
