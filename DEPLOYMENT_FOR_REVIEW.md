# Deployment for Assignment Review

## Problem
The reviewer needs to test this instantly without setting up ngrok or running locally.

## Solution Options

### Option 1: Deploy to a Free Cloud Platform (RECOMMENDED)

Deploy to a platform with a public URL so the reviewer can just:
1. Add their Bolna API key
2. Add their Slack webhook URL
3. Configure the webhook in Bolna
4. Test immediately

#### Best Free Platforms:

**A. Render.com (Easiest)**
- Free tier available
- Automatic HTTPS
- Easy deployment from GitHub
- Public URL provided

**B. Railway.app**
- Free tier with $5 credit
- Very simple deployment
- Public URL provided

**C. Fly.io**
- Free tier available
- Global deployment
- Public URL provided

### Option 2: Provide a Pre-Deployed Instance

**If you deploy it yourself:**
1. Deploy to any platform above
2. Get the public URL (e.g., `https://bolna-slack.onrender.com`)
3. In your submission, provide:
   - The public URL
   - Instructions for reviewer to add their credentials via environment variables
   - Or create a simple web form for them to input credentials

## Recommended Approach for Submission

### Deploy to Render.com (5 minutes)

1. **Push code to GitHub** (if not already)
   ```bash
   git init
   git add .
   git commit -m "Bolna-Slack integration"
   git push origin main
   ```

2. **Sign up at render.com**

3. **Create New Web Service**
   - Connect your GitHub repo
   - Name: `bolna-slack-integration`
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. **Add Environment Variables** in Render dashboard:
   - `BOLNA_API_KEY` = (leave blank - reviewer will add)
   - `SLACK_WEBHOOK_URL` = (leave blank - reviewer will add)
   - `BOLNA_API_BASE_URL` = `https://api.bolna.dev`
   - `PORT` = `8000`
   - `LOG_LEVEL` = `INFO`

5. **Deploy** - Render will give you a URL like:
   `https://bolna-slack-integration.onrender.com`

6. **In your submission email**, provide:
   ```
   Deployed URL: https://bolna-slack-integration.onrender.com
   
   For the reviewer to test:
   1. Set environment variables in Render dashboard:
      - BOLNA_API_KEY: [your Bolna API key]
      - SLACK_WEBHOOK_URL: [your Slack webhook]
   2. Configure webhook in Bolna:
      https://bolna-slack-integration.onrender.com/webhook/bolna/call-ended
   3. Make a test call
   4. Check Slack for the alert
   ```

## Alternative: Include Deployment Instructions

If you don't want to maintain a deployed instance, include clear deployment instructions in your submission:

**In README.md, add:**

```markdown
## Quick Deploy for Review

### Deploy to Render (5 minutes)

1. Fork this repo to your GitHub
2. Sign up at render.com
3. Create New Web Service
4. Connect your GitHub repo
5. Use these settings:
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables (your Bolna API key and Slack webhook)
7. Deploy
8. Use the provided URL in Bolna webhook configuration

Total time: 5 minutes
```

## What to Include in Submission

### Option A: Pre-Deployed (Best for Reviewer)
```
Subject: Bolna-Slack Integration Submission

Hi,

I've deployed the integration for easy testing:

Deployed URL: https://bolna-slack-integration.onrender.com

To test:
1. Add your credentials in Render dashboard (I'll share access)
2. Configure webhook in Bolna: [deployed-url]/webhook/bolna/call-ended
3. Make a test call
4. Check Slack

Attached: Complete source code ZIP

GitHub: [your-repo-url]
```

### Option B: Easy Deploy Instructions
```
Subject: Bolna-Slack Integration Submission

Hi,

The integration is ready to deploy in 5 minutes:

Quick Deploy:
1. Upload to Render.com (free)
2. Add your Bolna API key and Slack webhook
3. Configure webhook in Bolna
4. Test

Detailed instructions in DEPLOYMENT_FOR_REVIEW.md

Attached: Complete source code ZIP
```

## Recommendation

**For the best reviewer experience:**

1. Deploy it yourself to Render.com (free)
2. Get the public URL
3. In your submission, provide:
   - The deployed URL
   - Instructions for adding their credentials
   - Or share temporary access to the Render dashboard
4. Include the source code ZIP as backup

This way, the reviewer can test in 2 minutes instead of 15 minutes!