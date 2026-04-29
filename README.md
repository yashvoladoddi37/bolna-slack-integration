# Bolna-Slack Integration

A FastAPI-based integration that automatically sends Slack alerts when Bolna calls end, including call details and full transcripts.

## 🎯 Features

- ✅ Receives webhooks from Bolna when calls end
- ✅ Fetches complete call details (ID, agent ID, duration, transcript)
- ✅ Sends formatted Slack alerts with rich message blocks
- ✅ Async/await for high performance
- ✅ Automatic retry logic with exponential backoff
- ✅ Comprehensive error handling and logging
- ✅ Docker support for easy deployment
- ✅ Health check endpoints for monitoring

## 📋 Prerequisites

- Python 3.9 or higher
- Bolna account with API access
- Slack workspace with webhook permissions

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd bolna-ie
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```bash
# Bolna API Configuration
BOLNA_API_KEY=your_bolna_api_key_here
BOLNA_API_BASE_URL=https://api.bolna.dev

# Slack Configuration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Server Configuration (optional)
PORT=8000
LOG_LEVEL=INFO
```

### 4. Run the Application

**Development mode:**
```bash
python -m uvicorn app.main:app --reload --port 8000
```

**Production mode:**
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The server will start at `http://localhost:8000`

## 🔧 Configuration

### Bolna Setup

1. Log in to your Bolna dashboard
2. Navigate to Settings → API Keys
3. Generate a new API key
4. Copy the API key to your `.env` file

### Configure Webhook in Bolna

1. Go to Bolna Settings → Webhooks
2. Add a new webhook endpoint: `http://your-server:8000/webhook/bolna/call-ended`
3. Select event: `call.ended`
4. Save the webhook configuration

### Slack Setup

#### Option 1: Incoming Webhooks (Recommended)

1. Go to https://api.slack.com/apps
2. Create a new app or select existing
3. Navigate to "Incoming Webhooks"
4. Activate Incoming Webhooks
5. Click "Add New Webhook to Workspace"
6. Select the channel for alerts
7. Copy the webhook URL to your `.env` file

## 📁 Project Structure

```
bolna-ie/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── models.py            # Pydantic data models
│   ├── routes/
│   │   └── webhooks.py      # Webhook endpoints
│   ├── services/
│   │   ├── bolna_client.py  # Bolna API client
│   │   └── slack_client.py  # Slack API client
│   └── utils/
│       ├── logger.py        # Logging configuration
│       └── formatters.py    # Data formatting utilities
├── tests/                   # Unit tests
├── docker/
│   ├── Dockerfile          # Docker image definition
│   └── docker-compose.yml  # Docker Compose configuration
├── requirements.txt        # Python dependencies
└── README.md              # This file

## 🐳 Docker Deployment

### Build and Run with Docker Compose

```bash
# Build the image
docker-compose -f docker/docker-compose.yml build

# Run the container
docker-compose -f docker/docker-compose.yml up -d

# View logs
docker-compose -f docker/docker-compose.yml logs -f

# Stop the container
docker-compose -f docker/docker-compose.yml down
```

### Build and Run with Docker

```bash
# Build the image
docker build -f docker/Dockerfile -t bolna-slack-integration .

# Run the container
docker run -d \
  --name bolna-slack-integration \
  -p 8000:8000 \
  --env-file .env \
  bolna-slack-integration
```

## 🔍 API Endpoints

### Webhook Endpoint

**POST** `/webhook/bolna/call-ended`

Receives Bolna call ended events.

**Request Body:**
```json
{
  "event": "call.ended",
  "call_id": "uuid-string",
  "timestamp": "2026-04-29T05:30:00Z",
  "agent_id": "agent-uuid"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Webhook received and processing",
  "call_id": "uuid-string"
}
```

### Health Check

**GET** `/health`

Returns service health status.

### API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📊 Slack Message Format

The integration sends rich formatted messages to Slack with:
- Call ID and Agent ID
- Call duration (human-readable format)
- Call status
- Complete conversation transcript
- Timestamp

## 🧪 Testing

Run the test suite:

```bash
pytest tests/ -v
```

## 🔒 Security

- Never commit `.env` file
- Use environment variables for sensitive data
- Enable HTTPS in production
- Implement rate limiting for production deployments

## 📝 Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `BOLNA_API_KEY` | Yes | - | Bolna API authentication key |
| `BOLNA_API_BASE_URL` | No | https://api.bolna.dev | Bolna API base URL |
| `SLACK_WEBHOOK_URL` | Yes | - | Slack incoming webhook URL |
| `PORT` | No | 8000 | Server port |
| `HOST` | No | 0.0.0.0 | Server host |
| `LOG_LEVEL` | No | INFO | Logging level |
| `MAX_RETRIES` | No | 3 | Maximum API retry attempts |
| `REQUEST_TIMEOUT` | No | 30 | HTTP request timeout (seconds) |

## 🐛 Troubleshooting

### Webhook not receiving events
- Verify webhook URL is accessible from Bolna servers
- Check firewall/security group settings
- Ensure the endpoint is configured correctly in Bolna dashboard

### Slack messages not sending
- Verify Slack webhook URL is correct
- Check Slack app permissions
- Review application logs for errors

### API errors
- Verify Bolna API key is valid
- Check API base URL is correct
- Review retry logic in logs

## 📄 License

This project is provided as-is for the Bolna integration assignment.

## 🤝 Support

For issues or questions, please refer to:
- Bolna API Docs: https://www.bolna.ai/docs
- Slack API Docs: https://api.slack.com
