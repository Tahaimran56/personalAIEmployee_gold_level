# Silver Tier Quick Start Guide

**Feature**: Silver Tier Functional Assistant
**Version**: 1.0.0
**Prerequisites**: Bronze tier complete

## Overview

Silver tier adds functional automation capabilities to your AI Employee:
- 📧 Gmail monitoring for email detection
- 📤 Email sending with approval workflow
- 💼 LinkedIn post automation
- 🧠 Multi-step task planning with Claude reasoning
- ⏰ Scheduled watcher execution
- ✅ Enhanced approval workflow

## Prerequisites

### 1. Bronze Tier Complete
- Obsidian vault set up at `AI_Employee_Vault/`
- BaseWatcher class implemented
- File System Watcher working
- Agent Skills documented
- Dashboard and Company Handbook created

### 2. System Requirements
- Python 3.13+ installed
- Node.js 24+ installed (for MCP server)
- Git installed
- Internet connectivity for API calls

### 3. API Credentials Required
- Gmail API OAuth2 credentials
- LinkedIn API OAuth2 credentials
- Claude API key

---

## Installation Steps

### Step 1: Install Python Dependencies

```bash
# Navigate to project directory
cd C:\Users\Dell\Desktop\hackathon0

# Install required packages
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
pip install linkedin-api
pip install anthropic
pip install schedule
pip install python-dotenv
pip install pytest  # for testing
```

### Step 2: Set Up Gmail API

1. **Create Google Cloud Project**:
   - Go to https://console.cloud.google.com
   - Create new project: "AI Employee"
   - Enable Gmail API

2. **Create OAuth2 Credentials**:
   - Go to APIs & Services > Credentials
   - Create OAuth 2.0 Client ID (Desktop app)
   - Download credentials JSON

3. **Authorize Application**:
   ```bash
   python AI_Employee_Vault/setup/gmail_auth.py
   ```
   - Opens browser for authorization
   - Saves refresh token to .env

4. **Verify Setup**:
   ```bash
   python AI_Employee_Vault/watchers/gmail_watcher.py --test
   ```

### Step 3: Set Up LinkedIn API

1. **Create LinkedIn App**:
   - Go to https://www.linkedin.com/developers/apps
   - Create new app
   - Request access to Share API
   - Note Client ID and Client Secret

2. **Authorize Application**:
   ```bash
   python AI_Employee_Vault/setup/linkedin_auth.py
   ```
   - Opens browser for authorization
   - Saves access token to .env

3. **Verify Setup**:
   ```bash
   python AI_Employee_Vault/watchers/linkedin_watcher.py --test
   ```

### Step 4: Set Up Claude API

1. **Get API Key**:
   - Go to https://console.anthropic.com
   - Create API key
   - Copy key

2. **Add to .env**:
   ```bash
   echo "CLAUDE_API_KEY=your_api_key_here" >> .env
   ```

3. **Verify Setup**:
   ```bash
   python AI_Employee_Vault/services/reasoning_service.py --test
   ```

### Step 5: Set Up MCP Email Server

1. **Install MCP Server**:
   ```bash
   cd AI_Employee_Vault/mcp
   npm install
   ```

2. **Configure Server**:
   - Edit `config/mcp_email_server.json`
   - Add Gmail SMTP credentials from .env

3. **Start Server**:
   ```bash
   npm start
   ```

4. **Verify Setup**:
   ```bash
   curl http://localhost:3000/health
   ```

### Step 6: Configure Scheduler

**For Windows**:
```powershell
# Run scheduler setup script
powershell -ExecutionPolicy Bypass -File AI_Employee_Vault/scheduler/task_scheduler.ps1
```

**For Linux/Mac**:
```bash
# Run scheduler setup script
bash AI_Employee_Vault/scheduler/cron_setup.sh
```

---

## Configuration

### Environment Variables (.env)

Create `.env` file in project root:

```env
# Gmail API
GMAIL_CLIENT_ID=your_client_id
GMAIL_CLIENT_SECRET=your_client_secret
GMAIL_REFRESH_TOKEN=your_refresh_token
GMAIL_USER=your_email@gmail.com

# LinkedIn API
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret
LINKEDIN_ACCESS_TOKEN=your_access_token
LINKEDIN_PERSON_ID=your_person_id

# Claude API
CLAUDE_API_KEY=your_api_key

# MCP Server
MCP_EMAIL_SERVER_URL=http://localhost:3000
```

### Scheduler Configuration (config/scheduler_config.json)

```json
{
  "schedules": [
    {
      "task_name": "Gmail Watcher",
      "task_command": "python AI_Employee_Vault/watchers/gmail_watcher.py",
      "cron_expression": "*/5 * * * *",
      "status": "active"
    },
    {
      "task_name": "LinkedIn Watcher",
      "task_command": "python AI_Employee_Vault/watchers/linkedin_watcher.py",
      "cron_expression": "0 */1 * * *",
      "status": "active"
    }
  ]
}
```

---

## Usage

### Manual Execution

**Run Gmail Watcher**:
```bash
python AI_Employee_Vault/watchers/gmail_watcher.py
```

**Run LinkedIn Watcher**:
```bash
python AI_Employee_Vault/watchers/linkedin_watcher.py
```

**Generate Plan for Complex Task**:
```bash
# Create action file in Needs_Action/ with complex task
# Claude will detect and generate Plan.md automatically
```

**Send Email with Approval**:
```bash
# Create action file requesting email send
# Draft will be created in Pending_Approval/
# Approve by moving to Approved/
```

### Scheduled Execution

Watchers run automatically based on scheduler configuration:
- Gmail Watcher: Every 5 minutes
- LinkedIn Watcher: Every hour

Check logs:
```bash
# View watcher logs
cat AI_Employee_Vault/Logs/gmail_watcher.log
cat AI_Employee_Vault/Logs/linkedin_watcher.log

# View scheduler logs
cat AI_Employee_Vault/Logs/scheduler.log
```

---

## Testing

### Run Unit Tests

```bash
# Test all components
pytest tests/unit/

# Test specific component
pytest tests/unit/test_gmail_watcher.py
pytest tests/unit/test_email_service.py
pytest tests/unit/test_linkedin_service.py
pytest tests/unit/test_reasoning_service.py
pytest tests/unit/test_scheduler.py
```

### Run Integration Tests

```bash
# Test end-to-end workflows
pytest tests/integration/

# Test specific workflow
pytest tests/integration/test_email_workflow.py
pytest tests/integration/test_linkedin_workflow.py
pytest tests/integration/test_planning_workflow.py
pytest tests/integration/test_scheduling_workflow.py
```

### Run Verification Script

```bash
# Verify all Silver tier requirements met
python AI_Employee_Vault/verify_silver.py
```

Expected output:
```
Silver Tier Verification Report
================================

✅ Gmail Watcher: Working
✅ Email Service: Working
✅ LinkedIn Service: Working
✅ Reasoning Service: Working
✅ Scheduler: Working
✅ Approval Workflow: Working

All checks passed! Silver tier is complete.
```

---

## Troubleshooting

### Gmail API Issues

**Error: 401 Unauthorized**
- Solution: Refresh OAuth token
  ```bash
  python AI_Employee_Vault/setup/gmail_auth.py --refresh
  ```

**Error: 429 Rate Limit**
- Solution: Wait 1 minute, reduce check frequency
- Edit scheduler_config.json: Change `*/5 * * * *` to `*/10 * * * *`

**Error: 403 Forbidden**
- Solution: Check Gmail API is enabled in Google Cloud Console
- Verify OAuth scopes include `gmail.readonly`

### LinkedIn API Issues

**Error: 401 Unauthorized**
- Solution: Re-authenticate (access token expires after 60 days)
  ```bash
  python AI_Employee_Vault/setup/linkedin_auth.py
  ```

**Error: 403 Forbidden**
- Solution: Verify app has Share API access
- Check OAuth scopes include `w_member_social`

**Error: 429 Rate Limit**
- Solution: Wait 1 hour, reduce posting frequency

### MCP Email Server Issues

**Error: Connection refused**
- Solution: Start MCP server
  ```bash
  cd AI_Employee_Vault/mcp
  npm start
  ```

**Error: SMTP authentication failed**
- Solution: Verify Gmail OAuth credentials in .env
- Check refresh token is valid

### Scheduler Issues

**Windows: Task not running**
- Solution: Check Task Scheduler
  ```powershell
  schtasks /query /tn "AI Employee - Gmail Watcher"
  ```
- Verify task is enabled and has correct path

**Linux/Mac: Cron not running**
- Solution: Check crontab
  ```bash
  crontab -l | grep gmail_watcher
  ```
- Verify cron service is running: `systemctl status cron`

---

## Next Steps

After completing Silver tier:

1. **Verify All Requirements Met**:
   ```bash
   python AI_Employee_Vault/verify_silver.py
   ```

2. **Test End-to-End Workflows**:
   - Send test email → verify action file created
   - Create email draft → approve → verify sent
   - Create LinkedIn post → approve → verify published
   - Create complex task → verify plan generated

3. **Monitor for 24 Hours**:
   - Check logs for errors
   - Verify scheduled execution working
   - Test approval workflow

4. **Document Learnings**:
   - Update README.md with Silver tier features
   - Document any issues encountered
   - Note performance metrics

5. **Prepare for Gold Tier**:
   - Review Gold tier requirements
   - Plan Odoo integration
   - Plan Twitter/social media integration

---

## Support

- **Documentation**: See `specs/002-silver-functional-assistant/`
- **Issues**: Check `AI_Employee_Vault/Logs/` for error logs
- **Testing**: Run `pytest tests/` for diagnostics

---

**Silver Tier Status**: Ready for implementation
**Estimated Setup Time**: 2-3 hours
**Estimated Testing Time**: 1-2 hours
