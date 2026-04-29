"""Pydantic models matching the actual Bolna execution API schema"""

from pydantic import BaseModel, Field
from typing import Any, Optional


class TelephonyData(BaseModel):
    """Telephony call data from Bolna execution"""
    model_config = {"extra": "allow"}

    duration: Optional[str] = Field(None, description="Call duration in seconds (as string)")
    to_number: Optional[str] = None
    from_number: Optional[str] = None
    recording_url: Optional[str] = None
    call_type: Optional[str] = None
    provider: Optional[str] = None
    hangup_by: Optional[str] = None
    hangup_reason: Optional[str] = None


class BolnaExecutionPayload(BaseModel):
    """
    Full Bolna execution payload — sent both as webhook POST body
    and returned by GET /executions/{execution_id}.

    All fields are Optional so the model tolerates partial payloads
    sent mid-call (queued → in-progress → completed).
    """
    model_config = {"extra": "allow"}

    id: Optional[str] = Field(None, description="Execution / call ID")
    agent_id: Optional[str] = Field(None, description="Agent ID")
    status: Optional[str] = Field(None, description="Call status (completed, failed, …)")
    conversation_time: Optional[float] = Field(
        None, description="Conversation duration in seconds"
    )
    transcript: Optional[str] = Field(None, description="Full plain-text transcript")
    telephony_data: Optional[TelephonyData] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    error_message: Optional[str] = None
    extracted_data: Optional[Any] = None
    context_details: Optional[Any] = None

    @property
    def duration_seconds(self) -> Optional[int]:
        """
        Return duration in seconds, preferring telephony_data.duration
        (exact telephony time) and falling back to conversation_time.
        """
        if self.telephony_data and self.telephony_data.duration:
            try:
                return int(self.telephony_data.duration)
            except (ValueError, TypeError):
                pass
        if self.conversation_time is not None:
            return int(self.conversation_time)
        return None


# ---------------------------------------------------------------------------
# Slack message types (kept for the Slack client)
# ---------------------------------------------------------------------------

class SlackMessage(BaseModel):
    """Complete Slack incoming-webhook message payload"""
    text: str = Field(..., description="Fallback text shown in notifications")
    blocks: list[dict[str, Any]] = Field(..., description="Slack Block Kit blocks")
