# Render.com Deployment Guide

This guide will walk you through deploying the Bolna-Slack integration to Render.com in under 10 minutes.

## Prerequisites

- GitHub account
- Render.com account (free tier is sufficient)
- Your Bolna API key
- Your Slack webhook URL

## Step 1: Push Code to GitHub (5 minutes)

### 1.1 Initialize Git Repository

```bash
cd /home/yashvoladoddi/bolna-ie
git init
git add .
git commit -m "Initial commit: Bolna-Slack integration"
```

### 1.2 Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `bolna-slack-integration` (or any name you prefer)
3. Keep it **Private** (recommended for assignment)
4. **DO NOT** initialize with README, .gitignore, or license
5. Click "Create repository"

### 1.3 Push to GitHub

```bash
# Replace YOUR_USERNAME with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/bolna-slack-integration.git
git branch -M main
git push -u origin main
```

**Note:** You may need to authenticate with GitHub. Use a Personal Access Token if prompted.

## Step 2: Deploy to Render.com (5 minutes)

### 2.1 Sign Up / Log In to Render

1. Go to https://render.com
2. Click "Get Started" or "Sign In"
3. Sign up with GitHub (recommended) or email

### 2.2 Create New Web Service

1. Click "New +" button in top right
2. Select "Web Service"
3. Click "Connect account" if this is your first time
4. Find and select your `bolna-slack-integration` repository
5. Click "Connect"

### 2.3 Configure Web Service

Fill in the following details:

**Basic Settings:**
- **Name:** `bolna-slack-integration` (or your preferred name)
- **Region:** Choose closest to you (e.g., Oregon, Frankfurt, Singapore)
- **Branch:** `main`
- **Root Directory:** Leave blank
- **Runtime:** `Python 3`

**Build & Deploy:**
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**Instance Type:**
- Select **Free** (sufficient for this integration)

### 2.4 Add Environment Variables

Scroll down to "Environment Variables" section and add:

1. Click "Add Environment Variable"
2. Add the following variables:

| Key | Value | Notes |
|-----|-------|-------|
| `BOLNA_API_KEY` | `your-actual-bolna-api-key` | Get from Bolna dashboard |
| `SLACK_WEBHOOK_URL` | `your-actual-slack-webhook-url` | Get from Slack app settings |
| `ENVIRONMENT` | `production` | Fixed value |
| `LOG_LEVEL` | `INFO` | Fixed value |
| `BOLNA_API_BASE_URL` | `https://api.bolna.dev` | Fixed value |

**Important:** Replace the placeholder values with your actual credentials!

### 2.5 Deploy

1. Click "Create Web Service" button at the bottom
2. Render will start building and deploying your app
3. Wait 2-3 minutes for the deployment to complete
4. You'll see "Live" status when ready

### 2.6 Get Your Webhook URL

Once deployed, you'll see your app URL at the top:

```
https://bolna-slack-integration-xxxx.onrender.com
```

Your webhook URL for Bolna will be:

```
https://bolna-slack-integration-xxxx.onrender.com/webhook/bolna/call-ended
```

**Copy this URL** - you'll need it for the next step!

## Step 3: Configure Bolna Webhook (2 minutes)

1. Go to your Bolna dashboard
2. Open your agent (e.g., "Practo Appointment Booking Agent")
3. Click on the **Analytics** tab
4. Find **"Post Call Tasks"** section
5. Enable **"Push all execution data to webhook"**
6. Paste your webhook URL: `https://your-app.onrender.com/webhook/bolna/call-ended`
7. Click **"Save agent"**

## Step 4: Test the Integration (2 minutes)

### 4.1 Make a Test Call

1. In Bolna dashboard, click "Get call from agent" or "Test via browser"
2. Have a short conversation with the agent
3. End the call

### 4.2 Verify Slack Alert

1. Check your Slack channel
2. You should see a message with:
   - Call ID
   - Agent ID
   - Duration
   - Transcript

### 4.3 Check Logs (if needed)

If you don't see the Slack message:

1. Go to Render dashboard
2. Click on your service
3. Click "Logs" tab
4. Look for any errors

## Troubleshooting

### Issue: Deployment Failed

**Solution:** Check the build logs in Render dashboard. Common issues:
- Missing dependencies in `requirements.txt`
- Python version mismatch

### Issue: Service is Running but No Slack Messages

**Solution:** Check the following:
1. Environment variables are set correctly in Render
2. Webhook URL is configured correctly in Bolna
3. Check Render logs for errors
4. Verify Slack webhook URL is valid (test it with curl)

### Issue: "Application startup failed"

**Solution:** 
1. Check Render logs for the specific error
2. Verify all environment variables are set
3. Ensure `BOLNA_API_KEY` and `SLACK_WEBHOOK_URL` are correct

### Issue: Render Free Tier Sleeps After Inactivity

**Note:** Render free tier services sleep after 15 minutes of inactivity. The first request after sleep will take 30-60 seconds to wake up. This is normal for free tier.

**Solution for Production:** Upgrade to paid tier ($7/month) for always-on service.

## Monitoring Your Deployment

### View Logs

```
Render Dashboard → Your Service → Logs tab
```

### View Metrics

```
Render Dashboard → Your Service → Metrics tab
```

### Restart Service

```
Render Dashboard → Your Service → Manual Deploy → "Clear build cache & deploy"
```

## Updating Your Deployment

When you make code changes:

```bash
git add .
git commit -m "Description of changes"
git push origin main
```

Render will automatically detect the push and redeploy (takes 2-3 minutes).

## Cost

- **Render Free Tier:** $0/month
  - 750 hours/month free
  - Sleeps after 15 min inactivity
  - Perfect for this assignment

- **Render Starter Tier:** $7/month
  - Always-on service
  - Better for production use

## Security Notes

1. **Never commit `.env` file** - It's already in `.gitignore`
2. **Use environment variables** in Render for all secrets
3. **Keep repository private** if it contains sensitive logic
4. **Rotate API keys** periodically

## Next Steps

After successful deployment:

1. ✅ Test with multiple calls
2. ✅ Document your webhook URL
3. ✅ Prepare submission package
4. ✅ Include webhook URL in submission email

## Your Webhook URL

Once deployed, add this to your submission:

```
Webhook URL: https://your-app-name.onrender.com/webhook/bolna/call-ended
```

## Support

If you encounter issues:

1. Check Render logs first
2. Review this guide
3. Check `TESTING_GUIDE.md` for local testing
4. Review `DEPLOYMENT_FOR_REVIEW.md` for reviewer instructions

---

**Estimated Total Time:** 10-15 minutes

**You're now ready to submit your assignment!** 🎉