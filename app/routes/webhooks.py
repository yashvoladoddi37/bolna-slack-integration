"""Webhook endpoints for receiving Bolna events"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from app.models import BolnaWebhookPayload
from app.services.bolna_client import BolnaClient, BolnaAPIError
from app.services.slack_client import SlackClient, SlackAPIError
from app.config import settings
from app.utils.logger import setup_logger, log_with_context


logger = setup_logger(__name__, settings.log_level)
router = APIRouter(prefix="/webhook", tags=["webhooks"])

# Initialize clients
bolna_client = BolnaClient()
slack_client = SlackClient()


async def process_call_ended(call_id: str) -> None:
    """
    Background task to process call ended event
    
    Args:
        call_id: Unique call identifier
    """
    try:
        # Fetch call details from Bolna API
        log_with_context(
            logger, "info",
            "Processing call ended event",
            call_id=call_id
        )
        
        call_details = await bolna_client.get_call_details(call_id)
        
        # Send alert to Slack
        await slack_client.send_call_alert(call_details)
        
        log_with_context(
            logger, "info",
            "Call ended event processed successfully",
            call_id=call_id
        )
        
    except BolnaAPIError as e:
        log_with_context(
            logger, "error",
            "Failed to fetch call details from Bolna",
            call_id=call_id,
            error=str(e)
        )
        
    except SlackAPIError as e:
        log_with_context(
            logger, "error",
            "Failed to send Slack alert",
            call_id=call_id,
            error=str(e)
        )
        
    except Exception as e:
        log_with_context(
            logger, "error",
            "Unexpected error processing call ended event",
            call_id=call_id,
            error=str(e)
        )


@router.post("/bolna/call-ended")
async def handle_call_ended(
    payload: BolnaWebhookPayload,
    background_tasks: BackgroundTasks,
    request: Request
) -> dict[str, str]:
    """
    Webhook endpoint for Bolna call ended events
    
    This endpoint:
    1. Receives webhook from Bolna when a call ends
    2. Validates the payload
    3. Extracts the call ID
    4. Processes the event in the background (fetch details + send Slack alert)
    5. Returns immediate response to Bolna
    
    Args:
        payload: Webhook payload from Bolna
        background_tasks: FastAPI background tasks
        request: HTTP request object
    
    Returns:
        Success response
    
    Raises:
        HTTPException: If payload validation fails
    """
    log_with_context(
        logger, "info",
        "Received webhook",
        event=payload.event,
        call_id=payload.call_id,
        agent_id=payload.agent_id,
        client_ip=request.client.host if request.client else "unknown"
    )
    
    # Validate event type
    if payload.event != "call.ended":
        log_with_context(
            logger, "warning",
            "Received unexpected event type",
            event=payload.event,
            call_id=payload.call_id
        )
        raise HTTPException(
            status_code=400,
            detail=f"Unexpected event type: {payload.event}"
        )
    
    # Validate call_id
    if not payload.call_id:
        log_with_context(
            logger, "error",
            "Missing call_id in webhook payload",
            event=payload.event
        )
        raise HTTPException(
            status_code=400,
            detail="Missing call_id in payload"
        )
    
    # Process in background to avoid blocking the webhook response
    background_tasks.add_task(process_call_ended, payload.call_id)
    
    # Return immediate success response
    return {
        "status": "success",
        "message": "Webhook received and processing",
        "call_id": payload.call_id
    }


@router.get("/health")
async def health_check() -> dict[str, str]:
    """
    Health check endpoint
    
    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "service": "bolna-slack-integration"
    }

# Made with Bob
