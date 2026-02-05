# Gold Tier AI Employee - Setup Guide

Complete setup guide for the Gold Tier Autonomous AI Employee with Odoo accounting integration, weekly CEO briefing, Ralph Wiggum autonomous loop, and social media automation.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Service Setup](#service-setup)
5. [Verification](#verification)
6. [First Run](#first-run)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **Python**: 3.9 or higher
- **Node.js**: 16.x or higher
- **npm**: 8.x or higher
- **Git**: 2.30 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Disk Space**: Minimum 2GB free space

### External Services

- **Odoo**: Community Edition v19+ (self-hosted or cloud)
- **Facebook**: Business Page with Admin access
- **Instagram**: Business Account linked to Facebook Page
- **Twitter**: Developer Account with API access
- **Claude Code**: CLI installed and configured

### API Access Requirements

- Odoo JSON-RPC access credentials
- Facebook Page Access Token (long-lived)
- Instagram Business Account ID
- Twitter API v2 credentials (API Key, Secret, Access Token, Bearer Token)

## Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/your-org/ai-employee.git
cd ai-employee
```

### Step 2: Install Python Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Required Python packages:**
- odoo-rpc-client>=0.9.0
- python-dotenv>=1.0.0
- schedule>=1.2.0
- requests>=2.31.0

### Step 3: Install Node.js Dependencies

```bash
# Install MCP server dependencies
cd AI_Employee_Vault/mcp
npm install

# Dependencies installed:
# - express@^4.18.0
# - axios@^1.6.0
# - winston@^3.11.0
# - oauth-1.0a@^2.2.6
# - form-data@^4.0.0
```

### Step 4: Verify Installation

```bash
# Check Python version
python --version  # Should be 3.9+

# Check Node.js version
node --version  # Should be 16.x+

# Check installed packages
pip list | grep odoo
npm list --depth=0
```

## Configuration

### Step 1: Create Environment File

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

### Step 2: Configure Odoo Connection

Edit `.env` and add your Odoo credentials:

```bash
# Odoo Configuration
ODOO_URL=http://localhost:8069
ODOO_DATABASE=gold_tier_accounting
ODOO_USERNAME=admin
ODOO_PASSWORD=your_odoo_password
```

**To get Odoo credentials:**
1. Install Odoo Community Edition v19+
2. Create a new database named `gold_tier_accounting`
3. Note the admin username and password
4. Ensure JSON-RPC is enabled (default)

### Step 3: Configure Facebook/Instagram

Edit `.env` and add your Facebook credentials:

```bash
# Facebook Configuration
FACEBOOK_PAGE_ACCESS_TOKEN=your_long_lived_page_access_token
FACEBOOK_PAGE_ID=your_facebook_page_id
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_instagram_business_account_id
```

**To get Facebook credentials:**
1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create an app or use existing app
3. Add "Instagram Basic Display" and "Pages" permissions
4. Generate Page Access Token (long-lived, 60 days)
5. Get Page ID from your Facebook Page settings
6. Link Instagram Business Account to Facebook Page
7. Get Instagram Business Account ID from Graph API Explorer

See [API Credentials Guide](api-credentials.md) for detailed instructions.

### Step 4: Configure Twitter

Edit `.env` and add your Twitter credentials:

```bash
# Twitter Configuration
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_SECRET=your_twitter_access_secret
TWITTER_BEARER_TOKEN=your_twitter_bearer_token
```

**To get Twitter credentials:**
1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Create a new app or use existing app
3. Enable OAuth 1.0a with Read and Write permissions
4. Generate API Key, API Secret, Access Token, Access Secret
5. Generate Bearer Token for API v2
6. Save all credentials securely

See [API Credentials Guide](api-credentials.md) for detailed instructions.

### Step 5: Configure MCP Servers

Edit `.env` and set MCP server ports and API key:

```bash
# MCP Server Configuration
ODOO_MCP_PORT=3100
FACEBOOK_MCP_PORT=3101
INSTAGRAM_MCP_PORT=3102
TWITTER_MCP_PORT=3103
MCP_API_KEY=your_secure_random_api_key
```

**Generate secure API key:**
```bash
# Linux/macOS:
openssl rand -hex 32

# Windows (PowerShell):
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Maximum 256 }))
```

### Step 6: Configure Business Goals

Edit `AI_Employee_Vault/Business_Goals.md` with your actual business targets:

```markdown
# Business Goals

## Revenue Targets
- Monthly Revenue Target: $50,000
- Quarterly Revenue Target: $150,000
- Annual Revenue Target: $600,000

## Active Subscriptions
- Subscription 1: GitHub Enterprise ($210/month)
- Subscription 2: AWS ($500/month)
- Subscription 3: Slack Business+ ($12.50/user/month)

## Key Performance Indicators
- Customer Acquisition Cost (CAC): $500
- Customer Lifetime Value (LTV): $5,000
- Monthly Recurring Revenue (MRR): $45,000
- Churn Rate: <5%

## Upcoming Deadlines
- Q1 Board Meeting: 2026-03-15
- Annual Report Due: 2026-04-01
- Tax Filing Deadline: 2026-04-15
```

## Service Setup

### Step 1: Start MCP Servers

Start all MCP servers in separate terminal windows:

```bash
# Terminal 1 - Odoo MCP Server
cd AI_Employee_Vault/mcp
node odoo-server.js

# Terminal 2 - Facebook MCP Server
cd AI_Employee_Vault/mcp
node facebook-server.js

# Terminal 3 - Instagram MCP Server
cd AI_Employee_Vault/mcp
node instagram-server.js

# Terminal 4 - Twitter MCP Server
cd AI_Employee_Vault/mcp
node twitter-server.js
```

**Expected output:**
```
✓ Odoo MCP Server running on http://localhost:3100
✓ Health check: http://localhost:3100/health
```

### Step 2: Verify MCP Server Health

Check that all servers are running:

```bash
# Check Odoo MCP
curl http://localhost:3100/health

# Check Facebook MCP
curl http://localhost:3101/health

# Check Instagram MCP
curl http://localhost:3102/health

# Check Twitter MCP
curl http://localhost:3103/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "service": "odoo-mcp",
  "timestamp": "2026-02-05T10:30:00.000Z",
  "details": {
    "connected": true,
    "token_valid": true
  }
}
```

### Step 3: Start CEO Briefing Scheduler

```bash
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Start scheduler
python AI_Employee_Vault/scheduler/ceo_briefing_scheduler.py
```

**Expected output:**
```
✓ CEO Briefing Scheduler started
✓ Next briefing scheduled for: Monday 2026-02-10 08:00:00
```

### Step 4: Configure Stop Hook (Ralph Wiggum Loop)

**Windows:**
```powershell
# Verify stop hook exists
Test-Path .claude\hooks\stop.ps1

# Test stop hook
powershell .claude\hooks\stop.ps1
```

**Linux/macOS:**
```bash
# Make stop hook executable
chmod +x .claude/hooks/stop.sh

# Test stop hook
./.claude/hooks/stop.sh
```

**Expected output:**
```
✓ No In_Progress directory - task complete
```

## Verification

### Step 1: Run Health Check Script

```bash
python scripts/health_check.py
```

**Expected output:**
```
🏥 Gold Tier AI Employee - Health Check

✓ Python version: 3.9.7
✓ Node.js version: 16.14.0
✓ Odoo MCP Server: healthy (http://localhost:3100)
✓ Facebook MCP Server: healthy (http://localhost:3101)
✓ Instagram MCP Server: healthy (http://localhost:3102)
✓ Twitter MCP Server: healthy (http://localhost:3103)
✓ Odoo connection: connected
✓ Facebook token: valid
✓ Instagram token: valid
✓ Twitter token: valid
✓ Vault directories: all present
✓ Config files: all present
✓ Stop hook: configured

✅ All systems operational!
```

### Step 2: Run Verification Script

```bash
python scripts/verify_gold_tier.py
```

This script tests all features end-to-end:
- Odoo integration (create invoice, record payment, record expense)
- CEO Briefing generation
- Ralph Wiggum loop (multi-step task)
- Social media posting (Facebook, Instagram, Twitter)
- Error recovery (queue and retry)
- Audit logging

### Step 3: Verify Vault Structure

```bash
# Check vault directories
ls -la AI_Employee_Vault/

# Expected directories:
# - CEO_Briefings/
# - Queue/
# - Audit_Logs/
# - Needs_Action/
# - In_Progress/
# - Done/
# - Blocked/
# - Pending_Approval/
# - Social_Media_Metrics/
```

## First Run

### Test 1: Record Odoo Transaction

```bash
# Start Claude Code
claude

# In Claude Code, run:
Record an invoice in Odoo:
- Customer: Acme Corp
- Amount: $5,000
- Description: Consulting services for January 2026
- Due date: 2026-02-15
```

**Expected result:**
- Invoice created in Odoo
- Audit log entry created
- Success message with invoice ID

### Test 2: Generate CEO Briefing

```bash
# In Claude Code, run:
Generate CEO briefing for this week
```

**Expected result:**
- Briefing file created in `CEO_Briefings/`
- Contains revenue summary, expense analysis, bottlenecks, suggestions
- Audit log entry created

### Test 3: Test Ralph Wiggum Loop

```bash
# In Claude Code, run:
Process this multi-step task autonomously:
1. Create a test file in AI_Employee_Vault/test.txt
2. Write "Hello from Ralph Wiggum" to the file
3. Read the file and confirm content
```

**Expected result:**
- All 3 steps complete without stopping
- Task file created in In_Progress/, then moved to Done/
- Audit log entries for each step

### Test 4: Post to Social Media

```bash
# In Claude Code, run:
Create social media post for approval:
- Platforms: Facebook, Instagram
- Text: "Test post from Gold Tier AI Employee! 🤖"
- Image: https://example.com/test-image.jpg
```

**Expected result:**
- Draft created in Pending_Approval/
- Validation passes
- Waiting for approval

## Troubleshooting

### MCP Server Won't Start

**Problem:** `Error: listen EADDRINUSE: address already in use`

**Solution:**
```bash
# Find process using the port
# Windows:
netstat -ano | findstr :3100

# Linux/macOS:
lsof -i :3100

# Kill the process
# Windows:
taskkill /PID <pid> /F

# Linux/macOS:
kill -9 <pid>
```

### Odoo Connection Failed

**Problem:** `Connection refused` or `Invalid credentials`

**Solutions:**
1. Verify Odoo is running: `curl http://localhost:8069`
2. Check database name in `.env` matches Odoo database
3. Verify username and password are correct
4. Check Odoo logs: `docker logs odoo` (if using Docker)

### Facebook/Instagram Token Invalid

**Problem:** `Invalid token` or `Token expired`

**Solutions:**
1. Regenerate Page Access Token (tokens expire after 60 days)
2. Ensure token has required permissions (pages_manage_posts, instagram_basic, instagram_content_publish)
3. Verify Page ID is correct
4. Check Instagram Business Account is linked to Facebook Page

### Twitter API Error

**Problem:** `401 Unauthorized` or `403 Forbidden`

**Solutions:**
1. Verify all 5 credentials are correct (API Key, Secret, Access Token, Secret, Bearer Token)
2. Check app has Read and Write permissions
3. Regenerate credentials if needed
4. Ensure OAuth 1.0a is enabled

### Ralph Wiggum Loop Not Continuing

**Problem:** Claude stops after each step instead of continuing

**Solutions:**
1. Verify stop hook exists: `ls .claude/hooks/stop.*`
2. Make hook executable (Linux/macOS): `chmod +x .claude/hooks/stop.sh`
3. Test hook manually: `powershell .claude/hooks/stop.ps1` or `./.claude/hooks/stop.sh`
4. Check task file exists in In_Progress/
5. Verify Claude Code settings allow hooks

### CEO Briefing Not Generated

**Problem:** Scheduler running but no briefing created

**Solutions:**
1. Check scheduler logs for errors
2. Verify Odoo has transaction data
3. Check Business_Goals.md exists and is readable
4. Manually trigger: `Generate CEO briefing for this week`
5. Check CEO_Briefings/ directory permissions

## Next Steps

After successful setup:

1. **Configure Business Goals**: Update `AI_Employee_Vault/Business_Goals.md` with real targets
2. **Import Historical Data**: Import past transactions into Odoo
3. **Set Up Social Media Approval**: Configure approval workflow in `config/social_media_config.json`
4. **Schedule Regular Tasks**: Create recurring tasks for the Ralph Wiggum loop
5. **Monitor Audit Logs**: Regularly review `AI_Employee_Vault/Audit_Logs/`
6. **Review CEO Briefings**: Check weekly briefings every Monday morning
7. **Optimize Performance**: Profile slow operations and optimize as needed

## Support

For additional help:
- **Troubleshooting Guide**: See [gold-tier-troubleshooting.md](gold-tier-troubleshooting.md)
- **API Credentials Guide**: See [api-credentials.md](api-credentials.md)
- **Skills Documentation**: Check `.claude/skills/` for detailed feature guides
- **Audit Logs**: Review `AI_Employee_Vault/Audit_Logs/` for error details
- **GitHub Issues**: Report bugs at https://github.com/your-org/ai-employee/issues

## Security Notes

- **Never commit `.env` file** to version control
- **Rotate API tokens regularly** (every 60 days for Facebook, every 90 days for Twitter)
- **Use strong MCP_API_KEY** (minimum 32 characters, random)
- **Restrict Odoo user permissions** (create dedicated user for AI Employee)
- **Enable audit logging** for all sensitive operations
- **Review Audit_Logs/** regularly for suspicious activity
- **Backup Business_Goals.md** and CEO_Briefings/ regularly

## Performance Tips

- **Use SSD storage** for faster file operations
- **Allocate sufficient RAM** (8GB recommended for concurrent MCP servers)
- **Monitor MCP server memory** usage (restart if memory leak detected)
- **Clean up old audit logs** (keep last 90 days only)
- **Archive old CEO briefings** (move to separate folder after 1 year)
- **Optimize Odoo queries** (add indexes for frequently queried fields)
- **Use CDN for social media images** (faster upload, better reliability)

## Maintenance Schedule

- **Daily**: Check MCP server health, review audit logs
- **Weekly**: Review CEO briefing, check queue for stuck operations
- **Monthly**: Rotate API tokens, clean up old logs, backup data
- **Quarterly**: Performance audit, security review, update dependencies
- **Annually**: Full system audit, disaster recovery test, documentation update
