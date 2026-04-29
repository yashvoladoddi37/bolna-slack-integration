"""Slack API client for sending alerts"""

import httpx
from typing import Any
from app.config import settings
from app.models import BolnaCallDetails, SlackMessage
from app.utils.logger import setup_logger, log_with_context
from app.utils.formatters import format_duration, format_transcript


logger = setup_logger(__name__, settings.log_level)


class SlackAPIError(Exception):
    """Custom exception for Slack API errors"""
    pass


class SlackClient:
    """Client for sending messages to Slack via Incoming Webhooks"""
    
    def __init__(self):
        """Initialize Slack client"""
        self.webhook_url = settings.slack_webhook_url
        self.timeout = settings.request_timeout
        self.max_transcript_length = settings.max_transcript_length
        
        logger.info("Slack client initialized")
    
    def _format_message(self, call_data: BolnaCallDetails) -> SlackMessage:
        """
        Format call data into Slack message with blocks
        
        Args:
            call_data: Complete call details
        
        Returns:
            Formatted Slack message
        """
        # Format duration
        duration_str = format_duration(call_data.duration)
        
        # Format transcript
        transcript_str = format_transcript(
            call_data.transcript,
            self.max_transcript_length
        )
        
        # Build Slack blocks
        blocks: list[dict[str, Any]] = [
            # Header
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📞 Bolna Call Ended",
                    "emoji": True
                }
            },
            # Call details section
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Call ID:*\n`{call_data.id}`"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Agent ID:*\n`{call_data.agent_id}`"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Duration:*\n{duration_str}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Status:*\n{call_data.status.capitalize()}"
                    }
                ]
            },
            # Divider
            {
                "type": "divider"
            },
            # Transcript section
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Transcript:*\n```\n{transcript_str}\n```"
                }
            },
            # Footer divider
            {
                "type": "divider"
            },
            # Context/footer
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Call ended at {call_data.ended_at.strftime('%Y-%m-%d %H:%M:%S UTC')}"
                    }
                ]
            }
        ]
        
        # Create message
        message = SlackMessage(
            text=f"Bolna Call Ended - {call_data.id}",  # Fallback text
            blocks=blocks
        )
        
        return message
    
    async def send_call_alert(self, call_data: BolnaCallDetails) -> bool:
        """
        Send formatted call alert to Slack
        
        Args:
            call_data: Complete call details
        
        Returns:
            True if message sent successfully, False otherwise
        
        Raises:
            SlackAPIError: If Slack API request fails
        """
        log_with_context(
            logger, "info",
            "Sending Slack alert",
            call_id=call_data.id,
            agent_id=call_data.agent_id
        )
        
        try:
            # Format message
            message = self._format_message(call_data)
            
            # Send to Slack
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.webhook_url,
                    json=message.model_dump(),
                    headers={"Content-Type": "application/json"}
                )
                
                # Check response
                if response.status_code == 200:
                    log_with_context(
                        logger, "info",
                        "Slack alert sent successfully",
                        call_id=call_data.id,
                        status_code=response.status_code
                    )
                    return True
                else:
                    log_with_context(
                        logger, "error",
                        "Failed to send Slack alert",
                        call_id=call_data.id,
                        status_code=response.status_code,
                        response=response.text
                    )
                    raise SlackAPIError(
                        f"Slack API returned status {response.status_code}: {response.text}"
                    )
                    
        except httpx.RequestError as e:
            log_with_context(
                logger, "error",
                "Network error sending Slack alert",
                call_id=call_data.id,
                error=str(e)
            )
            raise SlackAPIError(f"Failed to send Slack message: {str(e)}")
        
        except Exception as e:
            log_with_context(
                logger, "error",
                "Unexpected error sending Slack alert",
                call_id=call_data.id,
                error=str(e)
            )
            raise SlackAPIError(f"Unexpected error: {str(e)}")

# Made with Bob
