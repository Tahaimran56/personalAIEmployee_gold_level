# Gold Tier Quickstart Guide

**Feature**: 003-gold-autonomous-employee
**Created**: 2026-02-05
**Purpose**: Step-by-step setup instructions for Gold Tier Autonomous Employee

---

## Overview

Gold Tier adds autonomous business management capabilities to your AI Employee:
- **Odoo Accounting Integration**: Automatic transaction tracking
- **Weekly CEO Briefing**: Monday morning business intelligence reports
- **Ralph Wiggum Loop**: Multi-step task automation without stopping
- **Social Media Automation**: Facebook, Instagram, Twitter posting
- **Error Recovery**: Graceful degradation when services fail
- **Comprehensive Audit Logging**: 90-day audit trail

**Estimated Setup Time**: 2-3 hours (mostly waiting for API approvals)

---

## Prerequisites

Before starting Gold Tier setup, ensure you have:

- ✅ **Silver Tier Complete**: Gold Tier builds on Silver Tier infrastructure
- ✅ **Node.js 18+**: For MCP servers (`node --version`)
- ✅ **Python 3.10+**: For service integrations (`python --version`)
- ✅ **Git**: For version control (`git --version`)
- ✅ **Odoo Community Edition v19+**: Self-hosted or accessible instance
- ✅ **Social Media Accounts**: Facebook Page, Instagram Business Account, Twitter account
- ✅ **Developer Accounts**: Facebook Developer, Twitter Developer (apply in advance)

---

## Phase 1: Odoo Setup (30 minutes)

### 1.1 Install Odoo Community Edition

**Option A: Docker (Recommended)**
```bash
# Pull Odoo 19 image
docker pull odoo:19

# Create Odoo data directory
mkdir -p ~/odoo-data

# Run Odoo container
docker run -d \
  --name odoo19 \
  -p 8069:8069 \
  -v ~/odoo-data:/var/lib/odoo \
  -e POSTGRES_USER=odoo \
  -e POSTGRES_PASSWORD=odoo \
  -e POSTGRES_DB=postgres \
  odoo:19
```

**Option B: Manual Installation**
Follow official Odoo installation guide: https://www.odoo.com/documentation/19.0/administration/install.html

### 1.2 Configure Odoo Accounting

1. Open Odoo in browser: `http://localhost:8069`
2. Create database: `gold_tier_accounting`
3. Install **Accounting** module:
   - Go to Apps → Search "Accounting" → Install
4. Configure Chart of Accounts:
   - Accounting → Configuration → Chart of Accounts
   - Select your country's standard chart (e.g., US GAAP)
5. Create API user:
   - Settings → Users & Companies → Users → Create
   - Name: `AI Employee API`
   - Login: `ai_employee`
   - Password: (generate strong password)
   - Access Rights: Accounting / Manager

### 1.3 Test Odoo Connection

```bash
# Install odoo-rpc-client
pip install odoo-rpc-client

# Test connection
python -c "
from odoorpc import ODOO
odoo = ODOO('localhost', port=8069)
odoo.login('gold_tier_accounting', 'ai_employee', 'YOUR_PASSWORD')
print('✅ Odoo connection successful!')
print(f'Odoo version: {odoo.version}')
"
```

### 1.4 Add Odoo Credentials to .env

```bash
# Add to .env file
echo "ODOO_URL=http://localhost:8069" >> .env
echo "ODOO_DATABASE=gold_tier_accounting" >> .env
echo "ODOO_USERNAME=ai_employee" >> .env
echo "ODOO_PASSWORD=YOUR_PASSWORD" >> .env
```

---

## Phase 2: Facebook & Instagram Setup (45 minutes)

### 2.1 Create Facebook Developer Account

1. Go to https://developers.facebook.com/
2. Click "Get Started" → Complete registration
3. Verify email and phone number

### 2.2 Create Facebook App

1. My Apps → Create App
2. Select "Business" as app type
3. App Name: `AI Employee Gold Tier`
4. App Contact Email: Your email
5. Click "Create App"

### 2.3 Add Facebook Login Product

1. In app dashboard → Add Product → Facebook Login → Set Up
2. Settings → Valid OAuth Redirect URIs: `http://localhost:3000/callback`
3. Save Changes

### 2.4 Get Facebook Page Access Token

1. Go to Graph API Explorer: https://developers.facebook.com/tools/explorer/
2. Select your app from dropdown
3. Click "Generate Access Token"
4. Grant permissions:
   - `pages_manage_posts`
   - `pages_read_engagement`
   - `pages_show_list`
5. Copy the short-lived token
6. Convert to long-lived token (60 days):

```bash
curl -X GET "https://graph.facebook.com/v19.0/oauth/access_token" \
  -d "grant_type=fb_exchange_token" \
  -d "client_id=YOUR_APP_ID" \
  -d "client_secret=YOUR_APP_SECRET" \
  -d "fb_exchange_token=SHORT_LIVED_TOKEN"
```

7. Get Page Access Token:

```bash
curl -X GET "https://graph.facebook.com/v19.0/me/accounts" \
  -d "access_token=LONG_LIVED_USER_TOKEN"
```

### 2.5 Link Instagram Business Account

1. Ensure your Instagram account is a Business Account:
   - Instagram App → Settings → Account → Switch to Professional Account → Business
2. Link to Facebook Page:
   - Instagram → Settings → Account → Linked Accounts → Facebook
   - Select your Facebook Page
3. Get Instagram Business Account ID:

```bash
curl -X GET "https://graph.facebook.com/v19.0/PAGE_ID" \
  -d "fields=instagram_business_account" \
  -d "access_token=PAGE_ACCESS_TOKEN"
```

### 2.6 Add Facebook/Instagram Credentials to .env

```bash
# Add to .env file
echo "FACEBOOK_APP_ID=YOUR_APP_ID" >> .env
echo "FACEBOOK_APP_SECRET=YOUR_APP_SECRET" >> .env
echo "FACEBOOK_PAGE_ID=YOUR_PAGE_ID" >> .env
echo "FACEBOOK_PAGE_ACCESS_TOKEN=YOUR_PAGE_TOKEN" >> .env
echo "INSTAGRAM_BUSINESS_ACCOUNT_ID=YOUR_IG_ACCOUNT_ID" >> .env
```

---

## Phase 3: Twitter Setup (30 minutes)

### 3.1 Apply for Twitter Developer Account

1. Go to https://developer.twitter.com/
2. Click "Sign up" → Apply for Developer Account
3. Select "Hobbyist" → "Making a bot"
4. Fill out application (describe AI Employee use case)
5. Wait for approval (usually 1-2 hours, can take up to 24 hours)

### 3.2 Create Twitter App

1. Developer Portal → Projects & Apps → Create App
2. App Name: `AI Employee Gold Tier`
3. App Environment: Development
4. Click "Create"

### 3.3 Configure App Permissions

1. App Settings → User authentication settings → Set up
2. App permissions: Read and Write
3. Type of App: Web App
4. Callback URI: `http://localhost:3000/callback`
5. Website URL: `http://localhost:3000`
6. Save

### 3.4 Generate OAuth 2.0 Credentials

1. App Settings → Keys and tokens
2. Generate Consumer Keys (API Key and Secret)
3. Generate Access Token and Secret
4. Copy all four values

### 3.5 Add Twitter Credentials to .env

```bash
# Add to .env file
echo "TWITTER_API_KEY=YOUR_API_KEY" >> .env
echo "TWITTER_API_SECRET=YOUR_API_SECRET" >> .env
echo "TWITTER_ACCESS_TOKEN=YOUR_ACCESS_TOKEN" >> .env
echo "TWITTER_ACCESS_TOKEN_SECRET=YOUR_ACCESS_TOKEN_SECRET" >> .env
echo "TWITTER_BEARER_TOKEN=YOUR_BEARER_TOKEN" >> .env
```

---

## Phase 4: Install Gold Tier Dependencies (10 minutes)

### 4.1 Install Python Libraries

```bash
# Navigate to project root
cd ~/AI_Employee_Vault

# Install Gold Tier Python dependencies
pip install odoo-rpc-client>=0.9.0
pip install facebook-sdk>=3.1.0
pip install tweepy>=4.14.0
```

### 4.2 Install Node.js Dependencies for MCP Servers

```bash
# Install MCP server dependencies
npm install axios@^1.6.0
npm install express@^4.18.0
npm install dotenv@^16.0.0
npm install winston@^3.11.0
```

### 4.3 Verify Installation

```bash
# Check Python packages
pip list | grep -E "odoo-rpc-client|facebook-sdk|tweepy"

# Check Node packages
npm list axios express dotenv winston
```

---

## Phase 5: Configure Ralph Wiggum Autonomous Loop (15 minutes)

### 5.1 Create Stop Hook

**For Windows (PowerShell):**
```powershell
# Create .claude/hooks directory
New-Item -ItemType Directory -Force -Path ".claude\hooks"

# Create stop.ps1 hook
@"
# Ralph Wiggum Stop Hook
`$taskFile = "AI_Employee_Vault\In_Progress\current_task.md"

if (Test-Path `$taskFile) {
    Write-Host "Task incomplete, continuing autonomous loop..."
    exit 1  # Non-zero exit prevents Claude from stopping
} else {
    Write-Host "Task complete!"
    exit 0  # Allow Claude to stop
}
"@ | Out-File -FilePath ".claude\hooks\stop.ps1" -Encoding UTF8
```

**For Linux/Mac (Bash):**
```bash
# Create .claude/hooks directory
mkdir -p .claude/hooks

# Create stop.sh hook
cat > .claude/hooks/stop.sh << 'EOF'
#!/bin/bash
# Ralph Wiggum Stop Hook

TASK_FILE="AI_Employee_Vault/In_Progress/current_task.md"

if [ -f "$TASK_FILE" ]; then
    echo "Task incomplete, continuing autonomous loop..."
    exit 1  # Non-zero exit prevents Claude from stopping
else
    echo "Task complete!"
    exit 0  # Allow Claude to stop
fi
EOF

# Make executable
chmod +x .claude/hooks/stop.sh
```

### 5.2 Configure Max Iterations

```bash
# Add to .env file
echo "RALPH_WIGGUM_MAX_ITERATIONS=10" >> .env
echo "RALPH_WIGGUM_TIMEOUT_MINUTES=5" >> .env
```

---

## Phase 6: Initialize Gold Tier Directories (5 minutes)

```bash
# Create Gold Tier directory structure
mkdir -p AI_Employee_Vault/CEO_Briefings
mkdir -p AI_Employee_Vault/Social_Media/Pending_Approval
mkdir -p AI_Employee_Vault/Social_Media/Published
mkdir -p AI_Employee_Vault/Audit_Logs
mkdir -p AI_Employee_Vault/Queue

# Create Business_Goals.md template
cat > AI_Employee_Vault/Business_Goals.md << 'EOF'
---
created: 2026-02-05
updated: 2026-02-05
---

# Business Goals & Targets

## Revenue Targets
- Monthly Revenue Goal: $10,000
- Quarterly Revenue Goal: $30,000
- Annual Revenue Goal: $120,000

## Active Subscriptions
- Subscription 1: Service Name - $99/month - Last Used: 2026-02-01
- Subscription 2: Service Name - $49/month - Last Used: 2026-01-15

## Key Performance Indicators
- Average Invoice Value: $1,500
- Payment Collection Time: 14 days
- Customer Retention Rate: 90%

## Upcoming Deadlines
- Project Alpha: 2026-02-15 (High Priority)
- Tax Filing: 2026-04-15 (High Priority)
- Contract Renewal: 2026-03-01 (Medium Priority)
EOF
```

---

## Phase 7: Test Gold Tier Features (20 minutes)

### 7.1 Test Odoo Integration

```bash
# Create test invoice
python << 'EOF'
from services.odoo_service import OdooService

odoo = OdooService()
invoice_id = odoo.create_invoice(
    customer_name="Test Customer",
    amount=1500.00,
    description="Test Invoice for Gold Tier Setup"
)
print(f"✅ Test invoice created: {invoice_id}")
EOF
```

### 7.2 Test Social Media (Draft Mode)

```bash
# Create test social media post (won't publish, just creates draft)
cat > AI_Employee_Vault/Social_Media/Pending_Approval/test_post.md << 'EOF'
---
post_id: test-001
platforms: [facebook, instagram, twitter]
status: pending_approval
created_at: 2026-02-05T10:00:00Z
---

# Test Post

Testing Gold Tier social media integration! 🚀

This is a test post to verify the system is working correctly.

#GoldTier #AIEmployee #Testing
EOF

echo "✅ Test post created in Pending_Approval/"
```

### 7.3 Test Ralph Wiggum Loop

```bash
# Create test multi-step task
cat > AI_Employee_Vault/Needs_Action/test_task.md << 'EOF'
---
task_id: test-ralph-001
status: pending
total_steps: 3
---

# Test Ralph Wiggum Loop

## Steps
1. [ ] Read this file
2. [ ] Move to In_Progress/
3. [ ] Move to Done/

This task tests the Ralph Wiggum autonomous loop.
EOF

echo "✅ Test task created. Run Claude Code to test autonomous execution."
```

### 7.4 Test CEO Briefing Generation

```bash
# Manually trigger CEO briefing (normally runs Monday 8 AM)
python << 'EOF'
from services.ceo_briefing_service import CEOBriefingService

briefing = CEOBriefingService()
briefing.generate_weekly_briefing()
print("✅ CEO Briefing generated in AI_Employee_Vault/CEO_Briefings/")
EOF
```

---

## Phase 8: Verify Setup (10 minutes)

### 8.1 Run Health Checks

```bash
# Check all MCP servers
curl http://localhost:3100/health  # Odoo
curl http://localhost:3101/health  # Facebook
curl http://localhost:3102/health  # Instagram
curl http://localhost:3103/health  # Twitter
```

Expected output for each:
```json
{
  "status": "healthy",
  "connected": true,
  "timestamp": "2026-02-05T10:00:00Z"
}
```

### 8.2 Verify Directory Structure

```bash
# Check all Gold Tier directories exist
ls -la AI_Employee_Vault/ | grep -E "CEO_Briefings|Social_Media|Audit_Logs|Queue"
```

### 8.3 Verify .env Configuration

```bash
# Check all required environment variables
grep -E "ODOO|FACEBOOK|INSTAGRAM|TWITTER|RALPH_WIGGUM" .env
```

Should show all credentials configured.

---

## Troubleshooting

### Odoo Connection Failed

**Problem**: `odoo-rpc-client` can't connect to Odoo

**Solutions**:
1. Check Odoo is running: `docker ps | grep odoo` or visit `http://localhost:8069`
2. Verify credentials in `.env` match Odoo user
3. Check firewall isn't blocking port 8069
4. Try connecting manually: `python -c "from odoorpc import ODOO; odoo = ODOO('localhost', port=8069); print(odoo.version)"`

### Facebook/Instagram Token Expired

**Problem**: `OAuthException: Error validating access token`

**Solutions**:
1. Long-lived tokens expire after 60 days - regenerate using steps in Phase 2.4
2. Check token expiry: `curl "https://graph.facebook.com/debug_token?input_token=YOUR_TOKEN&access_token=YOUR_TOKEN"`
3. Consider implementing token refresh automation (future enhancement)

### Twitter Rate Limit Exceeded

**Problem**: `429 Too Many Requests`

**Solutions**:
1. Standard access: 50 tweets per 24 hours - wait for reset
2. Check rate limit status: `curl "https://api.twitter.com/2/tweets" -H "Authorization: Bearer YOUR_TOKEN"`
3. Apply for Elevated access (300 tweets per 24 hours): https://developer.twitter.com/en/portal/products/elevated

### Ralph Wiggum Loop Not Continuing

**Problem**: Claude stops after each step instead of continuing

**Solutions**:
1. Verify stop hook exists: `ls .claude/hooks/stop.*`
2. Check hook is executable (Linux/Mac): `chmod +x .claude/hooks/stop.sh`
3. Test hook manually: `.claude/hooks/stop.sh` (should exit 1 if task in In_Progress/)
4. Check Claude Code settings allow hooks

### CEO Briefing Empty or Incomplete

**Problem**: Briefing generated but missing data

**Solutions**:
1. Ensure Odoo has transaction data for the past 7 days
2. Check `Business_Goals.md` exists and is properly formatted
3. Verify task files in `Done/` have completion timestamps
4. Check audit logs for errors: `cat AI_Employee_Vault/Audit_Logs/$(date +%Y-%m-%d).json`

### Queue Not Processing

**Problem**: Operations stuck in queue, not retrying

**Solutions**:
1. Check queue files: `ls AI_Employee_Vault/Queue/`
2. Verify scheduler is running (should check every 5 minutes)
3. Check service is actually down (e.g., Odoo, Facebook API)
4. Manually retry: `python -c "from services.queue_service import QueueService; QueueService().process_queue()"`

---

## Next Steps

After completing setup:

1. **Review Business_Goals.md**: Update with your actual revenue targets and subscriptions
2. **Create First Real Task**: Add a multi-step task to `Needs_Action/` and watch Ralph Wiggum work
3. **Schedule CEO Briefing**: Ensure it runs every Monday at 8 AM (configure in scheduler)
4. **Test Social Media Workflow**: Create a real post, approve it, verify it publishes
5. **Monitor Audit Logs**: Review `Audit_Logs/` daily to understand what AI Employee is doing
6. **Run `/sp.tasks`**: Generate detailed implementation tasks for Gold Tier development

---

## Security Best Practices

1. **Never commit .env file**: Add to `.gitignore`
2. **Rotate tokens regularly**: Facebook/Instagram tokens expire in 60 days
3. **Use strong passwords**: Especially for Odoo API user
4. **Limit API permissions**: Only grant what's needed (e.g., `pages_manage_posts`, not `pages_manage_metadata`)
5. **Monitor audit logs**: Review weekly for suspicious activity
6. **Backup Odoo database**: Regular backups of accounting data
7. **Encrypt sensitive data**: Consider encrypting `.env` file at rest

---

## Support & Resources

- **Odoo Documentation**: https://www.odoo.com/documentation/19.0/
- **Facebook Graph API**: https://developers.facebook.com/docs/graph-api/
- **Instagram Graph API**: https://developers.facebook.com/docs/instagram-api/
- **Twitter API v2**: https://developer.twitter.com/en/docs/twitter-api
- **Gold Tier Spec**: `specs/003-gold-autonomous-employee/spec.md`
- **Implementation Plan**: `specs/003-gold-autonomous-employee/plan.md`

---

## Estimated Costs

- **Odoo Community Edition**: Free (self-hosted)
- **Facebook/Instagram API**: Free (200 calls/hour)
- **Twitter API Standard**: Free (50 tweets/24 hours)
- **Twitter API Elevated**: Free (300 tweets/24 hours, requires approval)
- **Server/Hosting**: $0 (runs locally)
- **Total Monthly Cost**: $0 (excluding electricity/internet)

---

## Success Criteria

You'll know Gold Tier is working when:

- ✅ Odoo transactions sync within 5 minutes
- ✅ CEO Briefing generates every Monday at 8 AM
- ✅ Multi-step tasks complete without stopping
- ✅ Social media posts publish to all platforms
- ✅ Failed operations queue and retry automatically
- ✅ All actions logged in `Audit_Logs/`

**Congratulations! Gold Tier is now operational.** 🎉
