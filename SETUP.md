# Setup Guide for Bolna-Slack Integration

This guide provides detailed step-by-step instructions for setting up the Bolna-Slack integration.

## Prerequisites Checklist

Before you begin, ensure you have:

- [ ] Python 3.9 or higher installed
- [ ] pip package manager
- [ ] Git (for cloning the repository)
- [ ] Bolna account with API access
- [ ] Slack workspace with admin permissions
- [ ] A server or hosting platform (for production deployment)

## Step 1: Get Bolna API Credentials

### 1.1 Access Bolna Dashboard

1. Go to https://www.bolna.ai
2. Log in to your account
3. Navigate to the dashboard

### 1.2 Generate API Key

1. Click on **Settings** or **API Keys** in the sidebar
2. Click **Generate New API Key** or **Create API Key**
3. Give it a descriptive name (e.g., "Slack Integration")
4. Copy the API key immediately (you won't be able to see it again)
5. Store it securely - you'll need it for the `.env` file

### 1.3 Note the API Base URL

The default Bolna API base URL is typically:
```
https://api.bolna.dev
```

Verify this in the Bolna documentation or dashboard.

## Step 2: Set Up Slack Webhook

### 2.1 Create Slack App

1. Go to https://api.slack.com/apps
2. Click **Create New App**
3. Choose **From scratch**
4. Enter app name: "Bolna Call Alerts"
5. Select your workspace
6. Click **Create App**

### 2.2 Enable Incoming Webhooks

1. In your app settings, click **Incoming Webhooks** in the sidebar
2. Toggle **Activate Incoming Webhooks** to **On**
3. Scroll down and click **Add New Webhook to Workspace**
4. Select the channel where you want alerts (e.g., #bolna-alerts)
5. Click **Allow**

### 2.3 Copy Webhook URL

1. You'll see a webhook URL like:
   ```
   https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXX
   ```
2. Copy this URL - you'll need it for the `.env` file

## Step 3: Install the Application

### 3.1 Clone Repository

```bash
git clone <repository-url>
cd bolna-ie
```

### 3.2 Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3.3 Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 4: Configure Environment

### 4.1 Create .env File

```bash
cp .env.example .env
```

### 4.2 Edit .env File

Open `.env` in your text editor and fill in the values:

```bash
# Bolna API Configuration
BOLNA_API_KEY=your_actual_bolna_api_key_here
BOLNA_API_BASE_URL=https://api.bolna.dev

# Slack Configuration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/ACTUAL/WEBHOOK

# Server Configuration
PORT=8000
HOST=0.0.0.0
LOG_LEVEL=INFO
ENVIRONMENT=development

# Optional Configuration
MAX_RETRIES=3
RETRY_DELAY=1
REQUEST_TIMEOUT=30
MAX_TRANSCRIPT_LENGTH=3000
```

**Important**: Replace the placeholder values with your actual credentials!

## Step 5: Test Locally

### 5.1 Start the Server

```bash
python -m uvicorn app.main:app --reload --port 8000
```

You should see output like:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### 5.2 Verify Server is Running

Open your browser and go to:
- http://localhost:8000 - Should show service info
- http://localhost:8000/health - Should return `{"status": "healthy"}`
- http://localhost:8000/docs - Should show API documentation

### 5.3 Test Webhook Endpoint

You can test the webhook endpoint with curl:

```bash
curl -X POST http://localhost:8000/webhook/bolna/call-ended \
  -H "Content-Type: application/json" \
  -d '{
    "event": "call.ended",
    "call_id": "test-call-123",
    "timestamp": "2026-04-29T05:30:00Z",
    "agent_id": "test-agent-456"
  }'
```

**Note**: This will attempt to fetch call details from Bolna API, which may fail if the call ID doesn't exist. Check the logs for details.

## Step 6: Configure Bolna Webhook

### 6.1 Expose Your Server (for testing)

For local testing, you need to expose your local server to the internet. Options:

**Option A: ngrok (Recommended for testing)**
```bash
# Install ngrok from https://ngrok.com
ngrok http 8000
```

This will give you a public URL like: `https://abc123.ngrok.io`

**Option B: Deploy to a server** (see Step 7)

### 6.2 Add Webhook in Bolna

1. Go to Bolna Dashboard
2. Navigate to **Settings** → **Webhooks**
3. Click **Add Webhook** or **Create Webhook**
4. Enter webhook URL: `https://your-server.com/webhook/bolna/call-ended`
   - For ngrok: `https://abc123.ngrok.io/webhook/bolna/call-ended`
5. Select event type: **call.ended**
6. Save the webhook

### 6.3 Test with Real Call

1. Make a test call using Bolna
2. Wait for the call to end
3. Check your Slack channel for the alert
4. Check server logs for any errors

## Step 7: Production Deployment

### Option A: Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose -f docker/docker-compose.yml up -d

# View logs
docker-compose -f docker/docker-compose.yml logs -f
```

### Option B: Cloud Platform Deployment

#### Heroku

```bash
# Install Heroku CLI
# Login to Heroku
heroku login

# Create app
heroku create bolna-slack-integration

# Set environment variables
heroku config:set BOLNA_API_KEY=your_key
heroku config:set SLACK_WEBHOOK_URL=your_webhook_url

# Deploy
git push heroku main
```

#### AWS/Google Cloud/Azure

Refer to platform-specific documentation for deploying Python applications.

### Option C: VPS Deployment

1. Set up a VPS (DigitalOcean, Linode, etc.)
2. Install Python and dependencies
3. Clone repository
4. Configure `.env` file
5. Set up systemd service or use PM2
6. Configure nginx as reverse proxy
7. Set up SSL certificate (Let's Encrypt)

## Step 8: Monitoring and Maintenance

### 8.1 Check Logs

```bash
# If running locally
# Logs appear in console

# If using Docker
docker-compose -f docker/docker-compose.yml logs -f

# If using systemd
journalctl -u bolna-slack-integration -f
```

### 8.2 Monitor Health

Set up monitoring for:
- `/health` endpoint (should return 200)
- Server uptime
- Error rates in logs
- Slack message delivery

### 8.3 Update Webhook URL

If your server URL changes:
1. Update webhook URL in Bolna dashboard
2. Test with a new call

## Troubleshooting

### Issue: "Import errors" when running

**Solution**: Make sure you're in the virtual environment and dependencies are installed:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Issue: "Connection refused" to Bolna API

**Solution**: 
- Check BOLNA_API_KEY is correct
- Verify BOLNA_API_BASE_URL is correct
- Check your internet connection
- Review Bolna API status

### Issue: Slack messages not appearing

**Solution**:
- Verify SLACK_WEBHOOK_URL is correct
- Check Slack app is installed in workspace
- Verify webhook channel permissions
- Test webhook URL with curl:
  ```bash
  curl -X POST YOUR_WEBHOOK_URL \
    -H 'Content-Type: application/json' \
    -d '{"text":"Test message"}'
  ```

### Issue: Webhook not receiving events

**Solution**:
- Verify webhook URL is publicly accessible
- Check firewall/security group settings
- Verify webhook is configured correctly in Bolna
- Check server logs for incoming requests

## Security Best Practices

1. **Never commit `.env` file** to version control
2. **Use HTTPS** in production (not HTTP)
3. **Rotate API keys** periodically
4. **Implement rate limiting** for production
5. **Monitor logs** for suspicious activity
6. **Keep dependencies updated**: `pip install --upgrade -r requirements.txt`

## Next Steps

After successful setup:

1. ✅ Monitor first few calls to ensure alerts work correctly
2. ✅ Customize Slack message format if needed (edit `app/services/slack_client.py`)
3. ✅ Set up log aggregation (e.g., ELK stack, CloudWatch)
4. ✅ Configure alerts for system errors
5. ✅ Document any custom configurations for your team

## Support

If you encounter issues:

1. Check the logs first
2. Review this setup guide
3. Consult the main README.md
4. Check Bolna API documentation: https://www.bolna.ai/docs
5. Check Slack API documentation: https://api.slack.com

## Checklist

Use this checklist to track your setup progress:

- [ ] Python 3.9+ installed
- [ ] Repository cloned
- [ ] Virtual environment created and activated
- [ ] Dependencies installed
- [ ] Bolna API key obtained
- [ ] Slack webhook created
- [ ] `.env` file configured
- [ ] Server runs locally
- [ ] Health endpoint accessible
- [ ] Webhook endpoint tested
- [ ] Bolna webhook configured
- [ ] Test call completed successfully
- [ ] Slack alert received
- [ ] Production deployment completed (if applicable)
- [ ] Monitoring set up

Congratulations! Your Bolna-Slack integration is now set up and running! 🎉