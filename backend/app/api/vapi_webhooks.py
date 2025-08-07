from fastapi import APIRouter, Request, HTTPException
from app.core.supabase_client import supabase

router = APIRouter()

# @router.post("/incoming_call")
# async def vapi_webhook(request: Request):
#     """Handles both call start events and conversation messages if Vapi sends them to one webhook."""
#     payload = await request.json()
#     print("\n📞 Incoming Vapi Webhook Event:")
#     print(payload)

#     # Extract basic fields
#     call_id = payload.get("call_id")
#     caller = payload.get("from")
#     called = payload.get("to")
#     event_type = payload.get("event")  # Vapi might send 'call_started', 'message', etc.
#     sender = payload.get("sender")     # 'caller' or 'operator'
#     message = payload.get("message")   # Transcript text if available

#     # --- 1️⃣ Handle Call Start ---
#     if event_type in ["call_started", None]:  # Some APIs just send the initial POST without event_type
#         if not caller:
#             raise HTTPException(status_code=400, detail="Missing caller number")

#         print(f"--- Call Started: {call_id} from {caller} ---")

#         # Insert call row in Supabase
#         try:
#             response = supabase.table("calls").insert({
#                 "tenant_id": 1,  # Default tenant ID (integer)
#                 "caller_number": caller,
#                 "status": "in_progress"
#             }).execute()
#             print("✅ Inserted call into Supabase:", response.data)
#         except Exception as e:
#             print(f"❌ Error inserting call into database: {e}")
#             raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

#     # --- 2️⃣ Handle Conversation Messages ---
#     if sender and message:
#         role = "👤 Caller" if sender == "caller" else "🤖 Operator"
#         print(f"{role}: {message}")

#     return {"status": "logged", "call_id": call_id}


@router.post("/incoming_call")
async def vapi_webhook(request: Request):
    payload = await request.json()
    print("\n📞 Incoming Vapi Webhook Event:")
    print(payload)

    call_id = payload.get("call_id")
    caller = payload.get("from")
    event_type = payload.get("event")
    sender = payload.get("sender")
    message = payload.get("message")

    # --- Call Start Insert ---
    if event_type in ["call_started", "incoming_call", None]:
        print(f"--- Call Started: {call_id} from {caller} ---")

        # Attempt insert
        insert_data = {
            "tenant_id": None,   # safer for now
            "caller_number": caller,
            "status": "in_progress"
        }
        response = supabase.table("calls").insert(insert_data).execute()

        print("🔹 Insert attempt data:", insert_data)
        print("🔹 Supabase response:", response)

        # If no rows returned, print error explicitly
        if not response.data:
            print("❌ Insert failed or returned empty data!")

    # --- Log conversation if present ---
    if sender and message:
        role = "👤 Caller" if sender == "caller" else "🤖 Operator"
        print(f"{role}: {message}")

    return {"status": "logged", "call_id": call_id}