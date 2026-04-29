"""Pydantic models for data validation"""

from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime


class BolnaWebhookPayload(BaseModel):
    """Incoming webhook payload from Bolna when call ends"""
    event: str = Field(..., description="Event type (e.g., 'call.ended')")
    call_id: str = Field(..., description="Unique call identifier")
    timestamp: datetime = Field(..., description="Event timestamp")
    agent_id: Optional[str] = Field(None, description="Agent identifier")
    metadata: Optional[dict[str, Any]] = Field(None, description="Additional metadata")


class TranscriptMessage(BaseModel):
    """Single message in conversation transcript"""
    role: str = Field(..., description="Speaker role (user/agent)")
    message: str = Field(..., description="Message content")
    timestamp: datetime = Field(..., description="Message timestamp")


class BolnaCallDetails(BaseModel):
    """Complete call details from Bolna API"""
    id: str = Field(..., description="Unique call identifier")
    agent_id: str = Field(..., description="Agent that handled the call")
    duration: int = Field(..., description="Call duration in seconds")
    status: str = Field(..., description="Call status")
    transcript: List[TranscriptMessage] = Field(
        default_factory=list,
        description="Conversation transcript"
    )
    created_at: datetime = Field(..., description="Call start time")
    ended_at: datetime = Field(..., description="Call end time")


class SlackField(BaseModel):
    """Slack message field for structured data"""
    type: str = Field(default="mrkdwn", description="Field type")
    text: str = Field(..., description="Field text content")


class SlackBlock(BaseModel):
    """Slack message block"""
    type: str = Field(..., description="Block type")
    text: Optional[dict[str, str]] = Field(None, description="Text content")
    fields: Optional[List[SlackField]] = Field(None, description="Field list")


class SlackMessage(BaseModel):
    """Complete Slack message payload"""
    text: str = Field(..., description="Fallback text")
    blocks: List[dict[str, Any]] = Field(..., description="Message blocks")

# Made with Bob
