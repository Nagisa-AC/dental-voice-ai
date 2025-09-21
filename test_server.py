#!/usr/bin/env python3
"""
Simple test server for Healthcare Voice AI phone call testing
This is a minimal version to get you started quickly
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import json
from datetime import datetime
from typing import Dict, Any

# Create FastAPI app
app = FastAPI(
    title="Healthcare Voice AI - Test Server",
    description="Simple test server for phone call testing",
    version="1.0.0"
)

# Store for test data
test_data = {
    "calls": [],
    "webhooks": [],
    "appointments": []
}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Healthcare Voice AI Test Server",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "health": "/health",
            "webhooks": "/webhooks/vapi",
            "calls": "/calls",
            "appointments": "/appointments"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "healthcare-voice-ai-test"
    }

@app.post("/webhooks/vapi")
async def vapi_webhook(request: Request):
    """VAPI webhook endpoint for phone calls"""
    try:
        # Get the webhook data
        webhook_data = await request.json()
        
        # Log the webhook
        webhook_entry = {
            "timestamp": datetime.now().isoformat(),
            "data": webhook_data,
            "headers": dict(request.headers)
        }
        test_data["webhooks"].append(webhook_entry)
        
        print(f"📞 VAPI Webhook received: {json.dumps(webhook_data, indent=2)}")
        
        # Handle different webhook types
        if webhook_data.get("type") == "call-started":
            print("🚀 Call started!")
            return {"status": "success", "message": "Call started webhook received"}
        
        elif webhook_data.get("type") == "call-ended":
            print("📞 Call ended!")
            return {"status": "success", "message": "Call ended webhook received"}
        
        elif webhook_data.get("type") == "function-call":
            print("🔧 Function call received!")
            return {"status": "success", "message": "Function call webhook received"}
        
        else:
            print(f"❓ Unknown webhook type: {webhook_data.get('type')}")
            return {"status": "success", "message": "Webhook received"}
    
    except Exception as e:
        print(f"❌ Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/calls")
async def get_calls():
    """Get all call data"""
    return {
        "calls": test_data["calls"],
        "total": len(test_data["calls"])
    }

@app.get("/webhooks")
async def get_webhooks():
    """Get all webhook data"""
    return {
        "webhooks": test_data["webhooks"],
        "total": len(test_data["webhooks"])
    }

@app.get("/appointments")
async def get_appointments():
    """Get all appointment data"""
    return {
        "appointments": test_data["appointments"],
        "total": len(test_data["appointments"])
    }

@app.post("/appointments")
async def create_appointment(request: Request):
    """Create a new appointment"""
    try:
        appointment_data = await request.json()
        appointment_entry = {
            "id": len(test_data["appointments"]) + 1,
            "timestamp": datetime.now().isoformat(),
            "data": appointment_data
        }
        test_data["appointments"].append(appointment_entry)
        
        print(f"📅 Appointment created: {json.dumps(appointment_data, indent=2)}")
        
        return {
            "status": "success",
            "appointment": appointment_entry
        }
    
    except Exception as e:
        print(f"❌ Error creating appointment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test")
async def test_endpoint():
    """Test endpoint to verify server is working"""
    return {
        "message": "Test server is working!",
        "timestamp": datetime.now().isoformat(),
        "ngrok_url": "Use your ngrok URL to access this server from the internet"
    }

if __name__ == "__main__":
    print("🚀 Starting Healthcare Voice AI Test Server...")
    print("📞 This server will handle VAPI webhooks for phone call testing")
    print("🌐 Your ngrok URL: https://5d0b04a89443.ngrok-free.app")
    print("🔗 VAPI Webhook URL: https://5d0b04a89443.ngrok-free.app/webhooks/vapi")
    print("=" * 60)
    
    uvicorn.run(
        "test_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
