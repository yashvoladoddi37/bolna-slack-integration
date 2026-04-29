# Bolna → Slack Integration

A **FastAPI** webhook server that automatically posts a Slack alert whenever a Bolna call ends,
including the call **ID**, **agent ID**, **duration**, and full **transcript**.

---

## How it works

```
Bolna call ends
     │
     ▼  POST (full execution payload)
Webhook server  ──────────────────────────────────────────►  Slack channel
  /webhook/bolna/call-ended                                  (rich Block Kit message)
```

Bolna sends the **full execution object** to your webhook URL every time a call status changes.
The server only forwards the alert for **terminal statuses** (`completed`, `failed`, `no-answer`, etc.),
so you receive exactly one Slack message per finished call.

---

## Quick start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env`:

```ini
BOLNA_API_KEY=bn-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx   # from Bolna dashboard → API Keys
BOLNA_API_BASE_URL=https://api.bolna.ai             # do not change
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/… # Slack Incoming Webhook URL
```

### 3. Run the server

```bash
# development (auto-reload)
uvicorn app.main:app --reload --port 8000

# production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 4. Expose it publicly (for Bolna to reach)

Bolna must be able to POST to your server. Use **ngrok** for local testing:

```bash
ngrok http 8000
# copy the https://xxxxx.ngrok.io URL
```

### 5. Configure the Bolna agent webhook

1. Open [platform.bolna.ai](https://platform.bolna.ai) → your agent → **Analytics** tab
2. Under **"Push all execution data to webhook"** enter:
   ```
   https://your-public-url/webhook/bolna/call-ended
   ```
3. Click **Save agent**

---

## Slack message format

Each alert contains:

| Field | Source |
|-------|--------|
| **Call ID** | `id` from execution payload |
| **Agent ID** | `agent_id` from execution payload |
| **Duration** | `telephony_data.duration` (seconds → human-readable) |
| **Status** | `status` field |
| **Transcript** | `transcript` (plain text, truncated at 3000 chars) |

---

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/webhook/bolna/call-ended` | Main Bolna webhook receiver |
| `GET`  | `/webhook/health` | Health check |
| `GET`  | `/health` | Root health check |
| `GET`  | `/docs` | Swagger UI |

---

## Smoke test

With the server running locally:

```bash
python test_integration.py
```

This sends a realistic Bolna payload and verifies:
1. The webhook returns `200 accepted`
2. Non-terminal statuses (e.g. `in-progress`) are correctly ignored
3. A real Slack message is posted to your channel

---

## Environment variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `BOLNA_API_KEY` | ✅ | — | Bolna API key (Bearer token) |
| `BOLNA_API_BASE_URL` | | `https://api.bolna.ai` | Bolna API base URL |
| `SLACK_WEBHOOK_URL` | ✅ | — | Slack Incoming Webhook URL |
| `PORT` | | `8000` | Server port |
| `LOG_LEVEL` | | `INFO` | Logging level |
| `MAX_RETRIES` | | `3` | Retry attempts for API calls |
| `REQUEST_TIMEOUT` | | `30` | HTTP timeout in seconds |
| `MAX_TRANSCRIPT_LENGTH` | | `3000` | Max transcript chars in Slack |

---

## Docker

```bash
docker-compose -f docker/docker-compose.yml up -d
```

---

## Project structure

```
bolna-ie/
├── app/
│   ├── main.py                  # FastAPI app, middleware
│   ├── config.py                # Settings (pydantic-settings)
│   ├── models.py                # BolnaExecutionPayload, SlackMessage
│   ├── routes/
│   │   └── webhooks.py          # POST /webhook/bolna/call-ended
│   ├── services/
│   │   ├── bolna_client.py      # Optional: fetch execution by ID
│   │   └── slack_client.py      # Build & post Slack Block Kit message
│   └── utils/
│       ├── formatters.py        # format_duration, truncate_text
│       └── logger.py            # Structured JSON logger
├── test_integration.py          # End-to-end smoke test
├── requirements.txt
└── .env.example
```

---

## References

- [Bolna API docs — Webhooks](https://www.bolna.ai/docs/polling-call-status-webhooks.md)
- [Bolna API docs — Execution schema](https://www.bolna.ai/docs/api-reference/executions/get_execution.md)
- [Slack Incoming Webhooks](https://docs.slack.dev/messaging/sending-messages/sending-messages-using-incoming-webhooks)
