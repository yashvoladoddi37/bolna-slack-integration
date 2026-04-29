# API Integration Details

## Bolna API Integration

### Base Information
- **Documentation**: https://www.bolna.ai/docs
- **Base URL**: `https://api.bolna.dev` (to be confirmed from docs)
- **Authentication**: API Key in headers

### Webhook Event: Call Ended

When a call ends, Bolna sends a webhook POST request to your configured endpoint.

**Expected Webhook Payload Structure**:
```json
{
  "event": "call.ended",
  "call_id": "uuid-string",
  "timestamp": "2026-04-29T05:30:00Z",
  "agent_id": "agent-uuid",
  "metadata": {
    "duration": 120,
    "status": "completed"
  }
}
```

### API Endpoint: Get Call Details

**Endpoint**: `GET /call/{call_id}`

**Headers**:
```
Authorization: Bearer {BOLNA_API_KEY}
Content-Type: application/json
```

**Response Structure**:
```json
{
  "id": "call-uuid",
  "agent_id": "agent-uuid",
  "duration": 120,
  "status": "completed",
  "transcript": [
    {
      "role": "user",
      "message": "Hello, I need help",
      "timestamp": "2026-04-29T05:28:00Z"
    },
    {
      "role": "agent",
      "message": "Hello! How can I assist you today?",
      "timestamp": "2026-04-29T05:28:02Z"
    }
  ],
  "created_at": "2026-04-29T05:28:00Z",
  "ended_at": "2026-04-29T05:30:00Z"
}
```

### Required Data Fields
- `id`: Unique call identifier
- `agent_id`: Agent that handled the call
- `duration`: Call duration in seconds
- `transcript`: Array of conversation messages

---

## Slack API Integration

### Base Information
- **Documentation**: https://api.slack.com/messaging/webhooks
- **Method**: Incoming Webhooks (simplest approach)
- **Authentication**: Webhook URL contains authentication token

### Incoming Webhook Setup

1. Go to https://api.slack.com/apps
2. Create new app or select existing
3. Enable "Incoming Webhooks"
4. Add webhook to workspace
5. Copy webhook URL (format: `https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXX`)

### Message Format

**Basic Message**:
```json
{
  "text": "Bolna Call Ended",
  "blocks": [
    {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": "📞 Bolna Call Ended"
      }
    },
    {
      "type": "section",
      "fields": [
        {
          "type": "mrkdwn",
          "text": "*Call ID:*\ncall-uuid"
        },
        {
          "type": "mrkdwn",
          "text": "*Agent ID:*\nagent-uuid"
        },
        {
          "type": "mrkdwn",
          "text": "*Duration:*\n2m 0s"
        },
        {
          "type": "mrkdwn",
          "text": "*Status:*\nCompleted"
        }
      ]
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Transcript:*\n```\nUser: Hello, I need help\nAgent: Hello! How can I assist you today?\n```"
      }
    },
    {
      "type": "divider"
    }
  ]
}
```

### Message Formatting Guidelines

1. **Header**: Clear indication of event type
2. **Fields**: Key-value pairs for structured data
3. **Transcript**: Formatted as code block for readability
4. **Duration**: Convert seconds to human-readable format (e.g., "2m 30s")
5. **Truncation**: Limit transcript length if too long (>3000 chars)

---

## Data Models (Pydantic)

### Webhook Models

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class BolnaWebhookPayload(BaseModel):
    """Incoming webhook from Bolna when call ends"""
    event: str
    call_id: str
    timestamp: datetime
    agent_id: Optional[str] = None
    metadata: Optional[dict] = None

class TranscriptMessage(BaseModel):
    """Single message in conversation transcript"""
    role: str  # "user" or "agent"
    message: str
    timestamp: datetime

class BolnaCallDetails(BaseModel):
    """Complete call details from Bolna API"""
    id: str
    agent_id: str
    duration: int  # seconds
    status: str
    transcript: List[TranscriptMessage]
    created_at: datetime
    ended_at: datetime

class SlackField(BaseModel):
    """Slack message field"""
    type: str = "mrkdwn"
    text: str

class SlackBlock(BaseModel):
    """Slack message block"""
    type: str
    text: Optional[dict] = None
    fields: Optional[List[SlackField]] = None

class SlackMessage(BaseModel):
    """Complete Slack message payload"""
    text: str
    blocks: List[dict]
```

---

## Error Handling Strategy

### Bolna API Errors
- **401 Unauthorized**: Invalid API key
- **404 Not Found**: Call ID doesn't exist
- **429 Rate Limited**: Too many requests
- **500 Server Error**: Bolna service issue

**Strategy**: Retry with exponential backoff (max 3 attempts)

### Slack API Errors
- **400 Bad Request**: Invalid message format
- **404 Not Found**: Invalid webhook URL
- **500 Server Error**: Slack service issue

**Strategy**: Log error and alert via alternative channel

### Webhook Validation
- Verify webhook signature (if Bolna provides)
- Validate payload structure
- Check required fields exist
- Return appropriate HTTP status codes

---

## Configuration Requirements

### Environment Variables

```bash
# Bolna Configuration
BOLNA_API_KEY=your_bolna_api_key_here
BOLNA_API_BASE_URL=https://api.bolna.dev
BOLNA_WEBHOOK_SECRET=optional_webhook_secret

# Slack Configuration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Server Configuration
PORT=8000
HOST=0.0.0.0
LOG_LEVEL=INFO
ENVIRONMENT=development

# Optional: Retry Configuration
MAX_RETRIES=3
RETRY_DELAY=1
TIMEOUT=30
```

### Security Considerations

1. **Never commit `.env` file** - Use `.env.example` as template
2. **Validate webhook signatures** - Prevent unauthorized requests
3. **Use HTTPS in production** - Encrypt data in transit
4. **Implement rate limiting** - Prevent abuse
5. **Sanitize transcript data** - Remove sensitive information if needed

---

## Testing Strategy

### Unit Tests
- Test Bolna client with mocked responses
- Test Slack client with mocked webhook
- Test data model validation
- Test message formatting

### Integration Tests
- Test webhook endpoint with sample payloads
- Test end-to-end flow with test credentials
- Test error handling scenarios

### Manual Testing
1. Configure test agent in Bolna
2. Make test call
3. Verify webhook received
4. Verify Slack message sent
5. Check message formatting

---

## Monitoring & Logging

### Key Metrics
- Webhook requests received
- Successful Slack alerts sent
- Failed API calls
- Average processing time
- Error rates by type

### Log Levels
- **DEBUG**: Detailed request/response data
- **INFO**: Successful operations
- **WARNING**: Retries, degraded performance
- **ERROR**: Failed operations, exceptions
- **CRITICAL**: System failures

### Log Format
```json
{
  "timestamp": "2026-04-29T05:30:00Z",
  "level": "INFO",
  "message": "Slack alert sent successfully",
  "call_id": "call-uuid",
  "duration_ms": 150,
  "context": {
    "agent_id": "agent-uuid",
    "call_duration": 120
  }
}