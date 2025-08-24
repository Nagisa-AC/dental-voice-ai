from fastapi import APIRouter, Request, HTTPException
import logging
import time
from typing import Dict, Any

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/incoming_call")
async def webhook_availability():
    """
    VAPI availability check endpoint.
    """
    return {"status": "available", "message": "Dental Voice AI webhook is ready"}
