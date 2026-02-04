# Silver Tier Setup Guide

Complete step-by-step installation and setup guide for AI Employee Silver Tier.

---

## Prerequisites

Before starting, ensure you have:

- **Python 3.8+** installed
- **Node.js 16+** and npm installed
- **Git** installed
- **Obsidian** (optional, for viewing vault)
- **Gmail account** with API access
- **LinkedIn account** with developer access
- **Claude API key** from Anthropic

---

## Estimated Setup Time

- **Quick Setup** (minimal testing): 30-45 minutes
- **Full Setup** (with testing): 2-3 hours

---

## Step 1: Clone Repository

```bash
git clone https://github.com/Tahaimran56/personalAIEmployee_silverlevel.git
cd personalAIEmployee_silverlevel
```

---

## Step 2: Install Python Dependencies

### Install Required Packages

```bash
pip install -r requirements.txt
```

### Verify Installation

```bash
python -c "import google.auth, anthropic, schedule; print('✓ All packages installed')"
```

---

## Step 3: Install Node.js Dependencies

### Navigate to MCP Directory

```bash
cd AI_Employee_Vault/mcp
```

### Install Packages

```bash
npm install
```

### Verify Installation

```bash
npm list
```

Expected output should show: express, nodemailer, dotenv, cors

---

## Step 4: Set Up Gmail API

### 4.1 Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project: "AI Employee"
3. Enable Gmail API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"

### 4.2 Create OAuth2 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Configure consent screen:
   - User Type: External
   - App name: "AI Employee"
   - User support email: Your email
   - Developer contact: Your email
4. Create OAuth client ID:
   - Application type: Desktop app
   - Name: "AI Employee Desktop"
5. Download credentials JSON file

### 4.3 Configure Credentials

1. Copy `config/.env.template` to `config/.env`
2. Open the downloaded credentials JSON
3. Copy values to `config/.env`:
   ```
   GMAIL_CLIENT_ID=your_client_id_here
   GMAIL_CLIENT_SECRET=your_client_secret_here
   GMAIL_USER=your_email@gmail.com
   ```

### 4.4 Run OAuth Setup

```bash
cd ../../  # Back to project root
python AI_Employee_Vault/setup/gmail_auth.py
```

This will:
- Open browser for authorization
- Save refresh token to `config/.env`
- Create `token.json` file

**Expected Output:**
```
✓ Access token received
✓ Authenticated as: your_email@gmail.com
✓ Updated config/.env
```

---

## Step 5: Set Up LinkedIn API

### 5.1 Create LinkedIn App

1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/apps)
2. Click "Create app"
3. Fill in details:
   - App name: "AI Employee"
   - LinkedIn Page: Your page (or create one)
   - App logo: Upload any image
4. Click "Create app"

### 5.2 Request API Access

1. In your app, go to "Products" tab
2. Request access to "Share on LinkedIn"
3. Wait for approval (usually instant for personal use)

### 5.3 Configure OAuth Settings

1. Go to "Auth" tab
2. Add redirect URL: `http://localhost:8080/callback`
3. Copy Client ID and Client Secret

### 5.4 Add Credentials to .env

Edit `config/.env`:
```
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
```

### 5.5 Run OAuth Setup

```bash
python AI_Employee_Vault/setup/linkedin_auth.py
```

This will:
- Open browser for authorization
- Save access token to `config/.env`
- Save person ID to `config/.env`

**Expected Output:**
```
✓ Access token received (expires in 5184000 seconds)
✓ Authenticated as: Your Name
✓ Person ID: urn:li:person:XXXXXXXXXX
✓ Updated config/.env
```

**Note:** LinkedIn tokens expire after 60 days. Re-run this script when expired.

---

## Step 6: Set Up Claude API

### 6.1 Get API Key

1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to "API Keys"
4. Click "Create Key"
5. Copy the API key

### 6.2 Add to .env

Edit `config/.env`:
```
CLAUDE_API_KEY=sk-ant-api03-your_key_here
```

### 6.3 Verify API Key

```bash
python -c "import anthropic; client = anthropic.Anthropic(api_key='YOUR_KEY'); print('✓ Claude API key valid')"
```

---

## Step 7: Configure MCP Email Server

### 7.1 Verify .env Configuration

Ensure `config/.env` has:
```
MCP_EMAIL_SERVER_URL=http://localhost:3000
```

### 7.2 Start MCP Server

```bash
cd AI_Employee_Vault/mcp
npm start
```

**Expected Output:**
```
==========================================================
MCP Email Server
==========================================================
Server running on http://localhost:3000
Health check: http://localhost:3000/health

Endpoints:
  POST /send-email - Send an email
  POST /refresh-transporter - Refresh OAuth2 transporter
  GET  /health - Health check
==========================================================
✓ Email transporter ready
```

### 7.3 Test MCP Server

In a new terminal:
```bash
curl http://localhost:3000/health
```

Expected response:
```json
{
  "status": "ok",
  "service": "MCP Email Server",
  "version": "1.0.0"
}
```

**Keep this terminal running** - the MCP server must be running for email sending to work.

---

## Step 8: Set Up Scheduler (Optional)

### Windows

```powershell
cd AI_Employee_Vault/scheduler
.\task_scheduler.ps1
```

### Linux/Mac

```bash
cd AI_Employee_Vault/scheduler
chmod +x cron_setup.sh
./cron_setup.sh
```

**Expected Output:**
```
✓ Scheduled: Gmail Watcher (every 5 minutes)
✓ Scheduled: Process Actions (every 5 minutes)
✓ Scheduled: Check Expired Approvals (every 6 hours)
```

---

## Step 9: Verify Installation

### Run Verification Script

```bash
cd ..  # Back to AI_Employee_Vault
python verify_silver.py
```

**Expected Output:**
```
========================================
Silver Tier Verification
========================================

Checking file structure...
  ✓ Folder exists: Needs_Action
  ✓ Folder exists: Pending_Approval
  ...

Checking service implementations...
  ✓ Service class: EmailService
  ✓   Method: compose_draft_email()
  ...

========================================
Verification Summary
========================================

Passed:   85
Failed:   0
Warnings: 10

Success Rate: 100.0%

✅ All critical checks passed!
⚠️  Some warnings present (see above)
```

Warnings are expected if you haven't sent any emails yet (credentials configured but not tested).

---

## Step 10: Test Workflows

### Test 1: Gmail Monitoring

1. Send a test email to your Gmail account
2. Wait 5 minutes (or run manually):
   ```bash
   python AI_Employee_Vault/watchers/gmail_watcher.py AI_Employee_Vault
   ```
3. Check `AI_Employee_Vault/Needs_Action/` for new email action file

**Expected:** Email action file created with subject and sender

### Test 2: Email Sending

1. Create a draft email:
   ```bash
   python AI_Employee_Vault/services/email_service.py AI_Employee_Vault
   ```
2. Check `AI_Employee_Vault/Pending_Approval/` for draft
3. Move draft to `Approved/` folder
4. Email should be sent automatically (if scheduler running) or run:
   ```bash
   python AI_Employee_Vault/services/email_service.py AI_Employee_Vault --send-approved
   ```

**Expected:** Email sent, logged in `Logs/email_service.log`

### Test 3: LinkedIn Posting

1. Create a draft post:
   ```python
   from AI_Employee_Vault.services.linkedin_service import LinkedInService
   service = LinkedInService('AI_Employee_Vault')
   draft = service.compose_draft_post(
       content="Test post from AI Employee! 🤖",
       visibility='PUBLIC',
       hashtags=['AI', 'Automation']
   )
   print(f"Draft: {draft['draft_file_path']}")
   ```
2. Check `Pending_Approval/` for draft
3. Move to `Approved/` folder
4. Post should be published automatically

**Expected:** Post published to LinkedIn, logged in `Logs/linkedin_service.log`

### Test 4: Multi-Step Planning

1. Create a complex task:
   ```python
   from AI_Employee_Vault.services.reasoning_service import ReasoningService
   service = ReasoningService('AI_Employee_Vault')
   plan = service.generate_plan(
       task_description="Research competitors and prepare summary report",
       context="We're launching a new AI automation product",
       success_criteria="Report includes 5 competitors with analysis"
   )
   print(f"Plan: {plan['plan_file_path']}")
   ```
2. Check `Plans/` folder for generated plan

**Expected:** Plan.md created with 5-10 numbered steps

### Test 5: Approval Workflow

1. Create an approval request:
   ```python
   from AI_Employee_Vault.services.approval_service import ApprovalService
   service = ApprovalService('AI_Employee_Vault')
   request = service.create_approval_request(
       action_type='email_send',
       action_description='Send test email',
       action_details={'recipient': 'test@example.com', 'subject': 'Test'}
   )
   print(f"Request: {request['request_file_path']}")
   ```
2. Check `Pending_Approval/` for request
3. Move to `Approved/` or `Rejected/` folder
4. Check `Logs/approval.log` for result

**Expected:** Approval logged with timestamp

---

## Troubleshooting

### Gmail API Issues

**Error: "token.json not found"**
- Solution: Run `python AI_Employee_Vault/setup/gmail_auth.py`

**Error: "Authentication failed"**
- Solution: Delete `token.json` and re-run OAuth setup
- Check that Gmail API is enabled in Google Cloud Console

**Error: "Rate limit exceeded"**
- Solution: Wait 1 minute and retry
- Gmail API has rate limits (check Google Cloud Console quotas)

### LinkedIn API Issues

**Error: "LinkedIn credentials not found"**
- Solution: Run `python AI_Employee_Vault/setup/linkedin_auth.py`

**Error: "Token expired"**
- Solution: LinkedIn tokens expire after 60 days, re-run OAuth setup

**Error: "Permission denied (403)"**
- Solution: Ensure "Share on LinkedIn" product is approved for your app

### Claude API Issues

**Error: "Invalid API key"**
- Solution: Check API key in `config/.env` starts with `sk-ant-api03-`
- Verify key is active in Anthropic Console

**Error: "Rate limit exceeded"**
- Solution: Wait and retry, or upgrade Claude API tier

### MCP Server Issues

**Error: "Cannot connect to MCP server"**
- Solution: Start MCP server: `cd AI_Employee_Vault/mcp && npm start`
- Check server is running on http://localhost:3000

**Error: "Transporter verification failed"**
- Solution: Check Gmail OAuth credentials in `config/.env`
- Re-run `python AI_Employee_Vault/setup/gmail_auth.py`

### Scheduler Issues

**Windows: "Task not running"**
- Solution: Open Task Scheduler (`taskschd.msc`) and check task status
- Verify Python is in PATH
- Check task history for errors

**Linux/Mac: "Cron not working"**
- Solution: Check crontab: `crontab -l`
- Verify cron daemon is running: `systemctl status cron` (Linux)
- Check logs: `tail -f AI_Employee_Vault/Logs/scheduler.log`

---

## Next Steps

After successful setup:

1. **Review Company Handbook**: `AI_Employee_Vault/Company_Handbook.md`
2. **Check Dashboard**: `AI_Employee_Vault/Dashboard.md`
3. **Read Skill Documentation**: `AI_Employee_Vault/.claude/skills/`
4. **Monitor Logs**: `AI_Employee_Vault/Logs/`
5. **Customize Schedules**: Edit `config/scheduler_config.json`

---

## Security Best Practices

1. **Never commit `.env` file** - it contains sensitive credentials
2. **Rotate API keys regularly** - especially LinkedIn (60-day expiry)
3. **Review approval logs** - check `Logs/approval.log` weekly
4. **Limit API permissions** - only grant necessary scopes
5. **Use strong passwords** - for Gmail and LinkedIn accounts
6. **Enable 2FA** - on Gmail and LinkedIn accounts
7. **Monitor API usage** - check quotas in respective consoles

---

## Support

- **Issues**: https://github.com/Tahaimran56/personalAIEmployee_silverlevel/issues
- **Documentation**: See `README.md` and `specs/` folder
- **Logs**: Check `AI_Employee_Vault/Logs/` for detailed error messages

---

## Maintenance

### Weekly
- Check `Logs/` for errors
- Review `Dashboard.md` metrics
- Verify scheduler is running

### Monthly
- Rotate API keys (if needed)
- Review approval patterns
- Update dependencies: `pip install --upgrade -r requirements.txt`

### Every 60 Days
- Refresh LinkedIn token: `python AI_Employee_Vault/setup/linkedin_auth.py`

---

**Setup Complete!** 🎉

Your AI Employee Silver Tier is now ready to use.
