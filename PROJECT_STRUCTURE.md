# Project Structure Plan

## Directory Layout

```
bolna-ie/
├── .env                          # Environment variables (not in git)
├── .env.example                  # Environment template
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Python dependencies
├── README.md                     # Setup and usage instructions
├── ARCHITECTURE.md               # System design documentation
├── PROJECT_STRUCTURE.md          # This file
├── app/
│   ├── __init__.py              # App initialization
│   ├── main.py                  # FastAPI application entry point
│   ├── config.py                # Configuration management
│   ├── models.py                # Pydantic data models
│   ├── routes/
│   │   ├── __init__.py
│   │   └── webhooks.py          # Webhook endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── bolna_client.py      # Bolna API client
│   │   └── slack_client.py      # Slack API client
│   └── utils/
│       ├── __init__.py
│       ├── logger.py            # Logging configuration
│       └── formatters.py        # Message formatting utilities
├── tests/
│   ├── __init__.py
│   ├── test_webhooks.py         # Webhook endpoint tests
│   ├── test_bolna_client.py     # Bolna client tests
│   └── test_slack_client.py     # Slack client tests
└── docker/
    ├── Dockerfile               # Docker container definition
    └── docker-compose.yml       # Docker compose for local dev
```

## File Descriptions

### Root Level Files

- **`.env`**: Contains sensitive configuration (API keys, webhook URLs)
- **`.env.example`**: Template showing required environment variables
- **`.gitignore`**: Excludes sensitive files and Python artifacts
- **`requirements.txt`**: Python package dependencies
- **`README.md`**: Complete setup, configuration, and usage guide

### Application Code (`app/`)

#### Core Files
- **`main.py`**: FastAPI app initialization, middleware, startup/shutdown events
- **`config.py`**: Loads and validates environment variables using Pydantic
- **`models.py`**: Data models for webhooks, API responses, Slack messages

#### Routes (`app/routes/`)
- **`webhooks.py`**: 
  - POST `/webhook/bolna/call-ended` - Receives Bolna call end events
  - GET `/health` - Health check endpoint

#### Services (`app/services/`)
- **`bolna_client.py`**:
  - `BolnaClient` class with async methods
  - `get_call_details(call_id)` - Fetches call information
  - Error handling and retries
  
- **`slack_client.py`**:
  - `SlackClient` class with async methods
  - `send_call_alert(call_data)` - Sends formatted message
  - Message formatting with Slack blocks

#### Utilities (`app/utils/`)
- **`logger.py`**: Structured logging configuration
- **`formatters.py`**: Helper functions for formatting data

### Tests (`tests/`)
- Unit tests for each component
- Integration tests for end-to-end flow
- Mock external API calls

### Docker (`docker/`)
- **`Dockerfile`**: Multi-stage build for production
- **`docker-compose.yml`**: Local development environment

## Implementation Order

1. **Setup Phase**:
   - Create directory structure
   - Set up `.gitignore`, `.env.example`
   - Create `requirements.txt`

2. **Core Infrastructure**:
   - `config.py` - Configuration management
   - `logger.py` - Logging setup
   - `models.py` - Data models

3. **API Clients**:
   - `bolna_client.py` - Bolna API integration
   - `slack_client.py` - Slack API integration

4. **Web Layer**:
   - `main.py` - FastAPI app
   - `webhooks.py` - Webhook endpoints

5. **Utilities & Polish**:
   - `formatters.py` - Message formatting
   - Error handling improvements
   - Documentation

6. **Testing & Deployment**:
   - Unit tests
   - Docker setup
   - README documentation

## Key Dependencies

```
fastapi>=0.104.0          # Web framework
uvicorn[standard]>=0.24.0 # ASGI server
httpx>=0.25.0             # Async HTTP client
pydantic>=2.4.0           # Data validation
pydantic-settings>=2.0.0  # Settings management
python-dotenv>=1.0.0      # Environment variables
```

## Development Workflow

1. Install dependencies: `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and configure
3. Run locally: `uvicorn app.main:app --reload`
4. Test webhook: `curl -X POST http://localhost:8000/webhook/bolna/call-ended`
5. Check logs for debugging

## Production Deployment

- Use Docker container for consistent environment
- Set environment variables in deployment platform
- Enable HTTPS with reverse proxy (nginx/Caddy)
- Monitor logs and set up alerts
- Consider using managed services (AWS Lambda, Google Cloud Run)