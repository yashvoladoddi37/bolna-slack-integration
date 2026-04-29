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
    conversation_duration: Optional[float] = Field(
        None, description="Conversation duration in seconds (actual Bolna field name)"
    )
    conversation_time: Optional[float] = Field(
        None, description="Conversation duration in seconds (alias, may not be sent)"
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
        Return duration in seconds. Checks all known Bolna duration fields:
        1. telephony_data.duration  — phone calls via Twilio/Exotel
        2. conversation_duration    — actual field name sent by Bolna (web + phone calls)
        3. conversation_time        — alias, kept for safety
        """
        if self.telephony_data and self.telephony_data.duration:
            try:
                return int(self.telephony_data.duration)
            except (ValueError, TypeError):
                pass
        for val in (self.conversation_duration, self.conversation_time):
            if val is not None:
                return int(val)
        return None


# ---------------------------------------------------------------------------
# Slack message types (kept for the Slack client)
# ---------------------------------------------------------------------------

class SlackMessage(BaseModel):
    """Complete Slack incoming-webhook message payload"""
    text: str = Field(..., description="Fallback text shown in notifications")
    blocks: list[dict[str, Any]] = Field(..., description="Slack Block Kit blocks")
