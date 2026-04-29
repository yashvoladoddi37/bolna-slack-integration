"""Slack client — sends call-ended alerts via Incoming Webhooks"""

import httpx
from typing import Any
from datetime import datetime, timezone

from app.config import settings
from app.models import BolnaExecutionPayload, SlackMessage
from app.utils.logger import setup_logger, log_with_context
from app.utils.formatters import format_duration, truncate_text


logger = setup_logger(__name__, settings.log_level)


class SlackAPIError(Exception):
    """Raised when a Slack Incoming Webhook call fails"""
    pass


class SlackClient:
    """Sends messages to Slack via Incoming Webhooks"""

    def __init__(self):
        self.webhook_url = settings.slack_webhook_url
        self.timeout = settings.request_timeout
        self.max_transcript_length = settings.max_transcript_length
        logger.info("Slack client initialized")

    # ------------------------------------------------------------------
    # Message formatting
    # ------------------------------------------------------------------

    def _build_message(self, data: BolnaExecutionPayload) -> SlackMessage:
        """Build a rich Block-Kit Slack message from an execution payload."""

        # ---- Duration ---------------------------------------------------
        duration_secs = data.duration_seconds
        duration_str = format_duration(duration_secs) if duration_secs is not None else "N/A"

        # ---- Transcript -------------------------------------------------
        raw_transcript = data.transcript or "No transcript available"
        transcript_str = truncate_text(
            raw_transcript,
            max_length=self.max_transcript_length,
            suffix="\n…(truncated)",
        )

        # ---- Timestamp --------------------------------------------------
        ts_raw = data.updated_at or data.created_at
        if ts_raw:
            try:
                # Parse ISO-8601; replace Z → +00:00 for older Pythons
                dt = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
                ts_str = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
            except ValueError:
                ts_str = ts_raw
        else:
            ts_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        # ---- Blocks -----------------------------------------------------
        blocks: list[dict[str, Any]] = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📞 Bolna Call Ended",
                    "emoji": True,
                },
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Call ID:*\n`{data.id or 'N/A'}`",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Agent ID:*\n`{data.agent_id or 'N/A'}`",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Duration:*\n{duration_str}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Status:*\n{(data.status or 'unknown').replace('-', ' ').title()}",
                    },
                ],
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Transcript:*\n```\n{transcript_str}\n```",
                },
            },
            {"type": "divider"},
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Call ended at {ts_str}",
                    }
                ],
            },
        ]

        return SlackMessage(
            text=f"Bolna Call Ended — ID: {data.id}",
            blocks=blocks,
        )

    # ------------------------------------------------------------------
    # Send
    # ------------------------------------------------------------------

    async def send_call_alert(self, data: BolnaExecutionPayload) -> bool:
        """Post a formatted call-ended alert to Slack.

        Returns True on success, raises SlackAPIError on failure.
        """
        message = self._build_message(data)

        log_with_context(
            logger, "info",
            "Posting to Slack webhook",
            call_id=data.id,
            agent_id=data.agent_id,
        )

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.webhook_url,
                    json=message.model_dump(),
                    headers={"Content-Type": "application/json"},
                )

            if response.status_code == 200 and response.text == "ok":
                log_with_context(
                    logger, "info",
                    "Slack alert posted successfully",
                    call_id=data.id,
                )
                return True

            # Slack returns plain text "ok" on success; anything else is an error
            raise SlackAPIError(
                f"Slack returned HTTP {response.status_code}: {response.text}"
            )

        except SlackAPIError:
            raise

        except httpx.RequestError as e:
            raise SlackAPIError(f"Network error posting to Slack: {e}") from e

        except Exception as e:
            raise SlackAPIError(f"Unexpected error: {e}") from e
