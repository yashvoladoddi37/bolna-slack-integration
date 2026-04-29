# Live Testing Guide - Simple Steps

## What You Need Before Testing

✅ You have a Bolna agent ready  
✅ You have Slack webhook URL  
✅ You need Bolna API key  

## Step 1: Get Your Bolna API Key

1. Go to https://www.bolna.ai
2. Log in to your account
3. Go to **Settings** or **API Keys** section
4. Click **Create API Key** or **Generate New Key**
5. **COPY THE KEY** - you won't see it again!

## Step 2: Update Your .env File

Open the `.env` file in this project and replace these values:

```bash
# Replace this with your actual Bolna API key
BOLNA_API_KEY=paste_your_bolna_api_key_here

# Replace this with your actual Slack webhook URL
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/ACTUAL/WEBHOOK
```

## Step 3: Start Your Server

Open terminal in this project folder and run:

```bash
# Install dependencies (first time only)
pip install -r requirements.txt

# Start the server
python -m uvicorn app.main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

**Keep this terminal open!** The server needs to stay running.

## Step 4: Expose Your Server to Internet

Your server is running on your computer, but Bolna needs to reach it from the internet.

### Using ngrok (Easiest for Testing)

1. Download ngrok from https://ngrok.com/download
2. Install and run:
   ```bash
   ngrok http 8000
   ```
3. You'll see something like:
   ```
   Forwarding    https://abc123.ngrok.io -> http://localhost:8000
   ```
4. **Copy that URL** (e.g., `https://abc123.ngrok.io`)

**Keep ngrok running in a separate terminal!**

## Step 5: Configure Webhook in Bolna

Now tell Bolna where to send notifications:

1. Go to your Bolna dashboard
2. Open your agent (the one you want to test with)
3. Go to the **Analytics Tab**
4. Find the section **"Push Execution Data to Webhook"**
5. Enter your webhook URL: `https://abc123.ngrok.io/webhook/bolna/call-ended`
   (Replace `abc123.ngrok.io` with your actual ngrok URL from Step 4)
6. Click **Save** or **Update**

**Note**: This webhook will receive ALL execution data for this agent, including when calls end.

## Step 6: Make a Test Call

1. In Bolna dashboard, go to your agent
2. Make a test call using your agent
3. Have a short conversation (even just "Hello" and "Goodbye")
4. **End the call**

## Step 7: Check if It Worked

### Check Your Terminal
Look at the terminal where your server is running. You should see logs like:
```
INFO: Received webhook for call: call-123-abc
INFO: Fetching call details from Bolna
INFO: Sending Slack alert
INFO: Slack alert sent successfully
```

### Check Your Slack Channel
Go to the Slack channel where you configured the webhook. You should see a formatted message with:
- 📞 Bolna Call Ended header
- Call ID
- Agent ID
- Duration
- Transcript

## Troubleshooting

### Problem: "Connection refused" or "Cannot connect to Bolna API"
**Solution**: Check your `BOLNA_API_KEY` in `.env` file is correct

### Problem: "Slack message not appearing"
**Solution**: Check your `SLACK_WEBHOOK_URL` in `.env` file is correct

### Problem: "Webhook not received"
**Solution**: 
- Make sure ngrok is still running
- Check the webhook URL in Bolna matches your ngrok URL
- Make sure your server is still running

### Problem: "Module not found" errors
**Solution**: Run `pip install -r requirements.txt` again

## Quick Checklist

- [ ] Bolna API key added to `.env`
- [ ] Slack webhook URL added to `.env`
- [ ] Server running (`python -m uvicorn app.main:app --reload --port 8000`)
- [ ] ngrok running (`ngrok http 8000`)
- [ ] Webhook configured in Bolna with ngrok URL
- [ ] Test call made and ended
- [ ] Slack message received

That's it! You're done! 🎉

## Understanding the Two Webhooks (IMPORTANT!)

There are **TWO different webhooks** in this setup - don't confuse them!

### 1. Bolna Webhook → Your Server (ngrok URL)
**What**: Bolna sends data TO your server  
**Where to configure**: Bolna Dashboard → Analytics Tab  
**URL**: `https://abc123.ngrok.io/webhook/bolna/call-ended`  
**Purpose**: Bolna notifies YOUR server when a call ends

### 2. Slack Webhook → Slack (in .env file)
**What**: Your server sends data TO Slack  
**Where to configure**: In your `.env` file  
**URL**: `https://hooks.slack.com/services/YOUR/WEBHOOK/URL`  
**Purpose**: YOUR server sends formatted messages to Slack

## The Flow:
```
Bolna Call Ends
    ↓
Bolna sends webhook TO your server (ngrok URL)
    ↓
Your server receives it
    ↓
Your server fetches call details from Bolna API
    ↓
Your server formats the message
    ↓
Your server sends TO Slack (using Slack webhook URL)
    ↓
Message appears in Slack channel
```

**In simple terms:**
- **Bolna webhook** = Bolna talks to YOU
- **Slack webhook** = YOU talk to Slack

Both are needed for the integration to work!
