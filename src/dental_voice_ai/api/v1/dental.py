from fastapi import APIRouter, Request, HTTPException
import logging
import time
from typing import Dict, Any, Optional
import requests
from pydantic import BaseModel

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
    VAPI availability check endpoint.
    """
    return {"status": "available", "message": "Dental Voice AI webhook is ready"}


@router.get("/availability")
async def get_availability(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    service_type: Optional[str] = None
):
    """Get available appointment slots by calling Google Calendar FreeBusy API."""
    try:
        # Your Google Calendar API credentials
        access_token = "ya29.A0AS3H6NxeHBNkffvqn01rl3M6mqXhkd24hgY26ptl9X7b3tbOyybJNyA4X8Xc8b9xIm0yX3TSxxoGGtLo5xUrYs4t0fOZq5l9hdYtkQQP_MEfBekE6BwmHzDwlgDTaUD-uFDi4O6qp_yUDzhG-2YZLLcWCjK56oc4BC2tixkMaMNK_-0rB6onxJINXb3gr9qIsYL83bYaCgYKAWQSARISFQHGX2MiSZ20daXRLe107NGeOsfJCA0206"
        
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
            raise HTTPException(status_code=500, detail="Failed to get calendar data")
            
    except Exception as e:
        logger.error(f"Error getting availability: {e}")
        raise HTTPException(status_code=500, detail="Failed to get availability")


@router.post("/appointments")
async def create_appointment(appointment_data: AppointmentRequest):
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
        access_token = "ya29.A0AS3H6NxeHBNkffvqn01rl3M6mqXhkd24hgY26ptl9X7b3tbOyybJNyA4X8Xc8b9xIm0yX3TSxxoGGtLo5xUrYs4t0fOZq5l9hdYtkQQP_MEfBekE6BwmHzDwlgDTaUD-uFDi4O6qp_yUDzhG-2YZLLcWCjK56oc4BC2tixkMaMNK_-0rB6onxJINXb3gr9qIsYL83bYaCgYKAWQSARISFQHGX2MiSZ20daXRLe107NGeOsfJCA0206"
        
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