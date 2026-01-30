"""
FastAPI routes for WhatsApp webhook handling.
"""

from fastapi import APIRouter, Request, Response, Form, HTTPException
from fastapi.responses import PlainTextResponse
import logging

from app.agent.graph import process_message

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "StockPulse WhatsApp Agent",
        "version": "1.0.0"
    }


@router.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",
        "agent": "ready"
    }


@router.post("/whatsapp")
async def whatsapp_webhook(
    Body: str = Form(...),
    From: str = Form(...),
    To: str = Form(None),
    MessageSid: str = Form(None),
):
    """
    Handle incoming WhatsApp messages from Twilio.
    
    Twilio sends POST requests with form data containing:
    - Body: The message text
    - From: The sender's WhatsApp number (e.g., whatsapp:+1234567890)
    - To: The Twilio WhatsApp number
    - MessageSid: Unique message identifier
    """
    try:
        # Extract phone number (remove 'whatsapp:' prefix)
        user_phone = From.replace("whatsapp:", "")
        message_text = Body.strip()
        
        logger.info(f"Received message from {user_phone}: {message_text[:50]}...")
        
        # Process the message through the agent
        response_text = await process_message(user_phone, message_text)
        
        logger.info(f"Sending response to {user_phone}: {response_text[:50]}...")
        
        # Return TwiML response
        twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{escape_xml(response_text)}</Message>
</Response>"""
        
        return Response(
            content=twiml_response,
            media_type="application/xml"
        )
        
    except Exception as e:
        logger.error(f"Error processing WhatsApp message: {str(e)}")
        
        # Return error response
        error_twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>Sorry, I encountered an error. Please try again later.</Message>
</Response>"""
        
        return Response(
            content=error_twiml,
            media_type="application/xml"
        )


@router.get("/whatsapp")
async def whatsapp_webhook_verify(request: Request):
    """
    Handle Twilio webhook verification (if needed).
    """
    return PlainTextResponse("StockPulse WhatsApp Webhook is active")


def escape_xml(text: str) -> str:
    """Escape special XML characters in the response text."""
    if not text:
        return ""
    return (
        text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )
