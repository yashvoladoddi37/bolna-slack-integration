"""Webhook endpoints for receiving Bolna execution events"""

from fastapi import APIRouter, BackgroundTasks, Request
from app.models import BolnaExecutionPayload
from app.services.slack_client import SlackClient, SlackAPIError
from app.config import settings
from app.utils.logger import setup_logger, log_with_context


logger = setup_logger(__name__, settings.log_level)
router = APIRouter(prefix="/webhook", tags=["webhooks"])

slack_client = SlackClient()

# Statuses that mean a call is truly finished
TERMINAL_STATUSES = {
    "completed",
    "call-disconnected",
    "failed",
    "no-answer",
    "busy",
    "canceled",
    "stopped",
    "error",
    "balance-low",
}


async def _send_slack_alert(payload: BolnaExecutionPayload) -> None:
    """
    Background task: format execution data and post to Slack.
    Called only for terminal-status payloads that have an execution id.
    """
    try:
        log_with_context(
            logger, "info",
            "Sending Slack alert for completed call",
            call_id=payload.id,
            agent_id=payload.agent_id,
            status=payload.status,
        )
        await slack_client.send_call_alert(payload)
        log_with_context(
            logger, "info",
            "Slack alert sent successfully",
            call_id=payload.id,
        )
    except SlackAPIError as e:
        log_with_context(
            logger, "error",
            "Failed to send Slack alert",
            call_id=payload.id,
            error=str(e),
        )
    except Exception as e:
        log_with_context(
            logger, "error",
            "Unexpected error in Slack alert task",
            call_id=payload.id,
            error=str(e),
        )


@router.post("/bolna/call-ended")
async def handle_bolna_webhook(
    payload: BolnaExecutionPayload,
    background_tasks: BackgroundTasks,
    request: Request,
) -> dict:
    """
    Receives Bolna webhook POSTs.

    Bolna sends the full execution object to this URL every time a call
    status changes (queued → initiated → in-progress → completed …).
    We only act on terminal statuses so we alert exactly once per call.
    """
    log_with_context(
        logger, "info",
        "Webhook received",
        call_id=payload.id,
        agent_id=payload.agent_id,
        status=payload.status,
        client_ip=request.client.host if request.client else "unknown",
    )

    is_terminal = payload.status in TERMINAL_STATUSES

    if is_terminal and payload.id:
        background_tasks.add_task(_send_slack_alert, payload)
        return {
            "status": "accepted",
            "message": f"Processing call-ended alert for {payload.id}",
            "call_id": payload.id,
        }

    # Non-terminal or missing id — acknowledge but do nothing
    return {
        "status": "ignored",
        "message": f"Status '{payload.status}' is not terminal — no alert sent",
        "call_id": payload.id,
    }


@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint"""
    return {"status": "healthy", "service": "bolna-slack-integration"}
