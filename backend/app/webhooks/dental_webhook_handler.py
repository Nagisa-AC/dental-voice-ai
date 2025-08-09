from fastapi import APIRouter, Request, HTTPException
from app.database.database_operations import supabase, safe_supabase_insert
from app.ai_processing.dental_faq_matcher import (
    faq_matcher, 
    create_practice_config_from_db_record,
    identify_practice_from_vapi_data
)
from app.models.webhook_schemas import IntentType, WebhookResponse, IntentAnalysisRequest, IntentAnalysisResponse
import logging
import json
import time

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()


def _extract_vapi_call_data(payload: dict) -> dict:
    """
    Extract comprehensive call data from VAPI webhook payload.
    
    Args:
        payload: Raw VAPI webhook payload
        
    Returns:
        dict: Extracted and normalized call data
    """
    message_data = payload.get("message", {}) if isinstance(payload.get("message"), dict) else {}
    call_data = message_data.get("call", {})
    customer_data = message_data.get("customer", {})
    
    # Check if this is a VAPI function call (different format)
    if "function" in payload and "arguments" in payload.get("function", {}):
        # This is a VAPI function call with nested arguments
        try:
            function_data = payload.get("function", {})
            arguments_str = function_data.get("arguments", "{}")
            arguments = json.loads(arguments_str)
            
            extracted_data = {
                "call_id": payload.get("call_id", "function_call"),
                "event_type": "function-call",
                "caller_number": arguments.get("caller_number") or arguments.get("phone_number"),
                "called_number": arguments.get("phone_number"),
                "assistant_id": arguments.get("assistant_id"),
                "transcript": arguments.get("query", ""),
                "started_at": None,
                "ended_at": None,
                "duration_seconds": None,
                "ended_reason": None,
                "cost": None,
                "currency": "USD",
                "call_type": "function_call",
                "analysis": {},
                "summary": None,
                "sentiment": None,
                "recording_url": None,
                "artifacts": [],
                "error": None,
                "warnings": []
            }
        except json.JSONDecodeError:
            # Fallback to empty transcript if JSON parsing fails
            extracted_data = {
                "call_id": payload.get("call_id", "function_call"),
                "event_type": "function-call",
                "caller_number": None,
                "called_number": None,
                "assistant_id": None,
                "transcript": "",
                "started_at": None,
                "ended_at": None,
                "duration_seconds": None,
                "ended_reason": None,
                "cost": None,
                "currency": "USD",
                "call_type": "function_call",
                "analysis": {},
                "summary": None,
                "sentiment": None,
                "recording_url": None,
                "artifacts": [],
                "error": None,
                "warnings": []
            }
    elif "query" in payload or "phone_number" in payload or "caller_number" in payload:
        # This is a direct VAPI function call (alternative format)
        extracted_data = {
            "call_id": payload.get("call_id", "function_call"),
            "event_type": "function-call",
            "caller_number": payload.get("caller_number") or payload.get("phone_number"),
            "called_number": payload.get("phone_number"),
            "assistant_id": payload.get("assistant_id"),
            "transcript": payload.get("query", ""),
            "started_at": None,
            "ended_at": None,
            "duration_seconds": None,
            "ended_reason": None,
            "cost": None,
            "currency": "USD",
            "call_type": "function_call",
            "analysis": {},
            "summary": None,
            "sentiment": None,
            "recording_url": None,
            "artifacts": [],
            "error": None,
            "warnings": []
        }
    else:
        # Standard VAPI webhook format
        extracted_data = {
            "call_id": call_data.get("id") or payload.get("call_id"),
            "event_type": message_data.get("type") or payload.get("event") or "unknown",
            "caller_number": customer_data.get("number") or payload.get("from"),
            "called_number": call_data.get("phoneNumber") or call_data.get("phoneNumberId"),
            "assistant_id": call_data.get("assistantId"),
            "transcript": message_data.get("transcript") or payload.get("transcript") or 
                         (payload.get("message") if isinstance(payload.get("message"), str) else ""),
            "started_at": call_data.get("startedAt") or message_data.get("startedAt"),
            "ended_at": call_data.get("endedAt") or message_data.get("endedAt"),
            "duration_seconds": call_data.get("durationSeconds") or message_data.get("durationSeconds"),
            "ended_reason": call_data.get("endedReason") or message_data.get("endedReason"),
            "cost": call_data.get("cost") or message_data.get("cost"),
            "currency": call_data.get("costBreakdown", {}).get("currency") or "USD",
            "call_type": call_data.get("type"),
            "analysis": message_data.get("analysis", {}),
            "summary": message_data.get("summary"),
            "sentiment": message_data.get("sentiment"),
            "recording_url": message_data.get("recordingUrl") or call_data.get("recordingUrl"),
            "artifacts": message_data.get("artifacts", []),
            "error": message_data.get("error") or call_data.get("error"),
            "warnings": message_data.get("warnings", []) or call_data.get("warnings", [])
        }
    
    return extracted_data


def _insert_call_record(insert_data, request_id, record_type="call"):
    """
    Insert call record into database using enhanced Supabase error handling.
    
    Args:
        insert_data (dict): Data to insert into the calls table
        request_id (str): Unique request identifier for tracking
        record_type (str): Type of record being inserted (for logging)
    
    Returns:
        dict: Database response or None if failed
    """
    try:
        response = safe_supabase_insert("calls", insert_data, request_id)
        
        if response and hasattr(response, 'data') and response.data:
            record_id = response.data[0].get('id', 'unknown') if response.data else 'unknown'
            logger.info(f"✅ [{request_id}] {record_type.title()} record inserted successfully")
            logger.info(f"   - Record ID: {record_id}")
            logger.info(f"   - Caller: {insert_data.get('caller_number', 'unknown')}")
            logger.info(f"   - Status: {insert_data.get('status', 'unknown')}")
            logger.info(f"   - Intent: {insert_data.get('intent', 'unknown')}")
            return response
        else:
            logger.error(f"🔴 [{request_id}] Failed to insert {record_type} record - No data returned")
            return None
            
    except Exception as e:
        logger.error(f"🔴 [{request_id}] Database insertion failed for {record_type}: {e}")
        return None


async def _get_practice_config(practice_identifier: str, request_id: str):
    """
    Retrieve practice configuration from database based on identifier.
    
    Args:
        practice_identifier: Phone number, assistant ID, or other identifier
        request_id: Unique request identifier for tracking
        
    Returns:
        PracticeConfig object or None if not found
    """
    try:
        if not practice_identifier:
            # Default to first practice if no identifier provided
            practice_response = supabase.table("tenants").select("*").limit(1).execute()
        elif practice_identifier.startswith("+") or practice_identifier.replace("-", "").replace(" ", "").isdigit():
            # Phone number identifier
            practice_response = supabase.table("tenants").select("*").eq("phone_number", practice_identifier).execute()
        else:
            # Assistant ID or other identifier
            practice_response = supabase.table("tenants").select("*").limit(1).execute()
        
        if practice_response and practice_response.data:
            practice_record = practice_response.data[0]
            practice_config = create_practice_config_from_db_record(practice_record)
            logger.info(f"📋 [{request_id}] Found practice: {practice_config.name}")
            return practice_config
        else:
            logger.warning(f"⚠️ [{request_id}] No practice found for identifier: {practice_identifier}")
            return None
            
    except Exception as e:
        logger.error(f"🔴 [{request_id}] Error fetching practice config: {e}")
        return None


async def _analyze_transcript_and_generate_response(
    transcript: str, 
    request_id: str, 
    vapi_call_data: dict = None
) -> dict:
    """
    Analyze transcript for intent recognition and generate appropriate text response.
    
    Args:
        transcript: The conversation transcript to analyze
        request_id: Unique request identifier for tracking
        vapi_call_data: Full VAPI webhook data for context
        
    Returns:
        Dictionary containing intent analysis and text response for VAPI
    """
    try:
        logger.info(f"🧠 [{request_id}] Analyzing transcript for enhanced intent recognition")
        
        # Identify practice from VAPI data
        practice_identifier = identify_practice_from_vapi_data(vapi_call_data or {})
        practice_config = await _get_practice_config(practice_identifier, request_id)
        
        # Analyze transcript for intent with practice context
        intent_result = await faq_matcher.analyze_transcript(
            transcript, 
            practice_config,
            vapi_call_data
        )
        
        logger.info(f"🎯 [{request_id}] Intent identified: {intent_result.intent.value}")
        logger.info(f"   - Confidence: {intent_result.confidence:.2f}")
        logger.info(f"   - Practice-specific: {intent_result.tenant_specific}")
        logger.info(f"   - Matched keywords: {intent_result.matched_keywords}")
        
        if intent_result.extracted_entities:
            logger.info(f"   - Entities: {intent_result.extracted_entities}")
        
        if intent_result.faq_matched:
            logger.info(f"   - FAQ matched: {intent_result.faq_matched}")
        
        # Prepare comprehensive response for VAPI
        response_data = {
            "intent_analysis": {
                "intent": intent_result.intent.value,
                "confidence": intent_result.confidence,
                "matched_keywords": intent_result.matched_keywords,
                "extracted_entities": intent_result.extracted_entities,
                "tenant_specific": intent_result.tenant_specific,
                "faq_matched": intent_result.faq_matched
            },
            "response": {
                "text": intent_result.suggested_response,
                "should_speak": True,
                "end_call": False
            },
            "practice_info": {
                "identified": practice_config is not None,
                "name": practice_config.name if practice_config else None,
                "practice_id": practice_config.practice_id if practice_config else None
            }
        }
        
        # Add special handling for certain intents
        if intent_result.intent == IntentType.EMERGENCY:
            response_data["response"]["priority"] = "urgent"
            response_data["response"]["end_call"] = False
        elif intent_result.intent == IntentType.UNKNOWN:
            response_data["response"]["escalate"] = True
        
        logger.info(f"✅ [{request_id}] Enhanced intent analysis completed successfully")
        return response_data
        
    except Exception as e:
        logger.error(f"🔴 [{request_id}] Intent analysis failed: {e}")
        logger.exception(f"🔴 [{request_id}] Intent analysis error details:")
        
        # Return default error response
        return {
            "intent_analysis": {
                "intent": IntentType.UNKNOWN.value,
                "confidence": 0.0,
                "matched_keywords": [],
                "extracted_entities": {},
                "tenant_specific": False,
                "faq_matched": None
            },
            "response": {
                "text": "I apologize, but I'm experiencing technical difficulties. Please try again later or contact our office directly.",
                "should_speak": True,
                "end_call": False
            },
            "practice_info": {
                "identified": False,
                "name": None,
                "practice_id": None,
                "error": "Failed to process practice information"
            }
        }


@router.post("/incoming_call")
async def vapi_webhook(request: Request):
    """
    Handles incoming VAPI webhook events for call management.
    
    Processes function calls and end-of-call-report events to store complete call transcripts
    and metadata in the database.
    """
    request_id = id(request)
    
    # Parse payload
    try:
        payload = await request.json()
        logger.info(f"📞 [{request_id}] Incoming VAPI webhook received")
    except Exception as e:
        error_msg = f"Failed to parse JSON payload: {str(e)}"
        logger.error(f"🔴 [{request_id}] {error_msg}")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    
    try:
        # Database availability check
        if supabase is None:
            error_msg = "Database client not initialized - check Supabase configuration"
            logger.error(f"🔴 [{request_id}] {error_msg}")
            raise HTTPException(status_code=500, detail="Database not available")

        # Validate payload structure
        if not isinstance(payload, dict):
            error_msg = f"Expected dict payload, got {type(payload)}"
            logger.error(f"🔴 [{request_id}] {error_msg}")
            raise HTTPException(status_code=400, detail="Invalid payload format")

        # Extract comprehensive call data from VAPI payload
        vapi_data = _extract_vapi_call_data(payload)
        
        # Get key fields from extracted data
        event_type = vapi_data["event_type"]
        call_id = vapi_data["call_id"] or "unknown"
        caller = vapi_data["caller_number"]
        called_number = vapi_data["called_number"]
        transcript = vapi_data["transcript"]
        
        logger.info(f"📋 [{request_id}] Event type: {event_type}")
        
        # Process events based on type and available data
        if event_type == "end-of-call-report":
            if not caller:
                error_msg = f"Missing caller number in end-of-call-report for call {call_id}"
                logger.error(f"🔴 [{request_id}] {error_msg}")
                raise HTTPException(status_code=400, detail="Missing caller information")
            
            if not transcript:
                logger.warning(f"⚠️ [{request_id}] No transcript available for completed call {call_id}")
                transcript = ""
            
            logger.info(f"✅ [{request_id}] Processing completed call: {call_id} from {caller}")
            
            # Analyze transcript with enhanced intent recognition
            analysis_result = await _analyze_transcript_and_generate_response(
                transcript, 
                str(request_id), 
                payload
            )
            
            # Ensure we have the complete response text
            response_text = analysis_result["response"]["text"]
            if len(response_text) > 1000:
                response_text = response_text[:997] + "..."
                logger.warning(f"⚠️ [{request_id}] Response text truncated for database storage")
            
            # Prepare comprehensive database record
            insert_data = {
                "tenant_id": analysis_result["practice_info"].get("practice_id"),
                "caller_number": caller,
                "status": "completed",
                "transcript": transcript or "",
                "intent": analysis_result["intent_analysis"]["intent"],
                "intent_confidence": analysis_result["intent_analysis"]["confidence"],
                "faq_matched": analysis_result["intent_analysis"]["faq_matched"],
                "response_text": response_text,
            }
            
            _insert_call_record(insert_data, request_id, "completed call")
            
        elif event_type == "function-call":
            # Handle real-time function calls during conversation
            start_time = time.time()
            logger.info(f"🔧 [{request_id}] Processing function call: {call_id}")
            
            if transcript:
                # Analyze transcript for real-time response
                analysis_result = await _analyze_transcript_and_generate_response(
                    transcript, 
                    str(request_id), 
                    payload
                )
                
                processing_time = time.time() - start_time
                logger.info(f"🔧 [{request_id}] Analysis completed in {processing_time:.2f} seconds")
                
                # Store function call data in database for tracking
                insert_data = {
                    "tenant_id": analysis_result["practice_info"].get("practice_id"),
                    "caller_number": caller or "function_call",
                    "status": "in_progress",
                    "transcript": transcript or "",
                    "intent": analysis_result["intent_analysis"]["intent"],
                    "intent_confidence": analysis_result["intent_analysis"]["confidence"],
                    "faq_matched": analysis_result["intent_analysis"]["faq_matched"],
                    "response_text": analysis_result["response"]["text"],
                }
                
                _insert_call_record(insert_data, request_id, "function call")
                
                # Return proper VAPI response format
                response_text = analysis_result["response"]["text"]
                
                # Extract tool call ID from payload
                tool_call_id = "unknown"
                if "toolCalls" in payload:
                    tool_calls = payload.get("toolCalls", [])
                    if tool_calls and len(tool_calls) > 0:
                        tool_call_id = tool_calls[0].get("id", "unknown")
                elif "id" in payload:
                    tool_call_id = payload.get("id")
                
                result = {
                    "results": [
                        {
                            "toolCallId": tool_call_id,
                            "result": response_text.replace('\n', ' ')  # Single line for VAPI
                        }
                    ]
                }
                
                logger.info(f"📤 [{request_id}] Returning response to VAPI")
                return result
            else:
                # No transcript in function call - return error
                error_msg = "No transcript provided in function call"
                logger.error(f"🔴 [{request_id}] {error_msg}")
                raise HTTPException(status_code=400, detail="Invalid function call data: Missing query")
            
        elif caller and transcript and event_type not in ["conversation-update", "speech-update", "status-update"]:
            logger.info(f"🧪 [{request_id}] Processing test/manual call: {call_id} from {caller}")
            
            # Handle test calls or non-standard webhook events
            analysis_result = await _analyze_transcript_and_generate_response(
                transcript, 
                str(request_id), 
                payload
            )
            
            insert_data = {
                "tenant_id": analysis_result["practice_info"].get("practice_id"),
                "caller_number": caller,
                "status": "in_progress",
                "transcript": transcript or "",
                "intent": analysis_result["intent_analysis"]["intent"],
                "intent_confidence": analysis_result["intent_analysis"]["confidence"],
                "faq_matched": analysis_result["intent_analysis"]["faq_matched"],
                "response_text": analysis_result["response"]["text"],
            }
            
            _insert_call_record(insert_data, request_id, "test call")
            
        else:
            # Log and skip intermediate or incomplete events
            if event_type in ["conversation-update", "speech-update", "status-update"]:
                logger.info(f"⏩ [{request_id}] Skipping intermediate event: {event_type}")
            elif not caller:
                logger.warning(f"⚠️ [{request_id}] Event {event_type} missing caller information - skipping")
            elif not transcript and event_type != "unknown":
                logger.warning(f"⚠️ [{request_id}] Event {event_type} missing transcript - skipping")
            else:
                logger.info(f"ℹ️ [{request_id}] No actionable data for event: {event_type}")

        logger.info(f"✅ [{request_id}] Webhook processed successfully")
        
        # Prepare comprehensive response with all extracted data
        response = {
            "status": "logged", 
            "call_id": call_id,
            "event_type": event_type,
            "processed": event_type == "end-of-call-report" and caller and transcript,
        }
        
        return response
        
    except HTTPException as http_exc:
        # Log HTTP exceptions but re-raise them as-is for FastAPI
        logger.error(f"🔴 [{request_id}] HTTP Exception: {http_exc.status_code} - {http_exc.detail}")
        raise
        
    except Exception as e:
        # Catch-all for unexpected errors
        error_msg = f"Unexpected webhook processing error: {str(e)}"
        logger.error(f"🔴 [{request_id}] {error_msg}")
        logger.exception(f"🔴 [{request_id}] Full exception details:")
        
        # For VAPI function calls, return a fallback response instead of throwing an error
        if "function" in payload and "arguments" in payload.get("function", {}):
            logger.warning(f"⚠️ [{request_id}] Returning fallback response for VAPI function call")
            tool_call_id = payload.get("id", "unknown")
            return {
                "results": [
                    {
                        "toolCallId": tool_call_id,
                        "result": "I apologize, but I'm experiencing technical difficulties accessing the information right now. Please try again later or contact our office directly."
                    }
                ]
            }
        
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/analyze_intent")
async def analyze_intent(request: Request):
    """
    Standalone endpoint for analyzing transcript intent and generating responses.
    
    Useful for testing intent recognition or processing individual transcripts.
    """
    request_id = id(request)
    
    try:
        payload = await request.json()
        
        # Validate required fields
        if "transcript" not in payload:
            raise HTTPException(status_code=400, detail="Missing required field: transcript")
        
        transcript = payload["transcript"]
        
        if not transcript or not transcript.strip():
            raise HTTPException(status_code=400, detail="Transcript cannot be empty")
        
        # Analyze transcript with enhanced intent recognition
        analysis_result = await _analyze_transcript_and_generate_response(
            transcript, 
            str(request_id)
        )
        
        return {
            "status": "analyzed",
            "request_id": request_id,
            "transcript_length": len(transcript),
            "intent_analysis": analysis_result["intent_analysis"],
            "response": analysis_result["response"],
            "practice_info": analysis_result["practice_info"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"🔴 [{request_id}] Intent analysis endpoint error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")