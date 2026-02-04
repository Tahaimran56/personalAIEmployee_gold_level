# Silver Tier Implementation - Manual Tasks Checklist

**Status**: Phase 1 Setup - Automated tasks complete
**Date**: 2026-02-04

---

## ✅ Automated Tasks (Already Done)

- [x] Created directory structure (config/, services/, scheduler/, mcp/, setup/, Plans/, .state/, tests/)
- [x] Created .env.template with all credential placeholders
- [x] Created gmail_config.json with watcher settings
- [x] Created linkedin_config.json with service settings
- [x] Created mcp_email_server.json with SMTP settings
- [x] Created scheduler_config.json with schedule definitions
- [x] Created processed_emails.json for duplicate prevention

---

## 🔴 MANUAL TASKS - YOU NEED TO DO THESE

### Priority 1: Install Dependencies (15 minutes)

**Python Dependencies**:
```bash
# Install all dependencies at once
pip install -r requirements.txt

# Or install individually:
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
pip install anthropic
pip install schedule
pip install python-dotenv
pip install playwright
pip install pytest

# Install Playwright browsers (required for WhatsApp watcher)
playwright install chromium
```

**Node.js Dependencies** (for MCP server):
```bash
cd AI_Employee_Vault/mcp
npm init -y
npm install nodemailer
cd ../..
```

**Verification**:
```bash
# Check Python packages installed
pip list | grep -E "google-auth|linkedin|anthropic|schedule|dotenv|pytest"

# Check Node.js packages installed
cd AI_Employee_Vault/mcp && npm list && cd ../..
```

---

### Priority 2: Set Up Gmail API (30-45 minutes)

**Steps**:

1. **Go to Google Cloud Console**
   - URL: https://console.cloud.google.com
   - Sign in with your Google account

2. **Create New Project**
   - Click "Select a project" → "New Project"
   - Project name: "AI Employee Silver"
   - Click "Create"

3. **Enable Gmail API**
   - Go to "APIs & Services" → "Library"
   - Search for "Gmail API"
   - Click "Enable"

4. **Create OAuth 2.0 Credentials**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Application type: "Desktop app"
   - Name: "AI Employee Desktop"
   - Click "Create"

5. **Download Credentials**
   - Click "Download JSON" button
   - Save as `credentials.json` in project root
   - **DO NOT commit this file to git**

6. **Run OAuth Flow** (after implementing gmail_auth.py)
   ```bash
   python AI_Employee_Vault/setup/gmail_auth.py
   ```
   - Browser will open for authorization
   - Grant permissions
   - Refresh token will be saved to config/.env

**What You'll Get**:
- `GMAIL_CLIENT_ID`
- `GMAIL_CLIENT_SECRET`
- `GMAIL_REFRESH_TOKEN` (after OAuth flow)

---

### Priority 3: Set Up WhatsApp Watcher (15-20 minutes)

**Steps**:

1. **Install Playwright Browsers**
   ```bash
   # Install Chromium browser (~300MB download)
   playwright install chromium
   ```

2. **Run WhatsApp Setup Script**
   ```bash
   python AI_Employee_Vault/setup/whatsapp_setup.py
   ```
   - Browser will open automatically
   - You'll see WhatsApp Web with QR code

3. **Scan QR Code**
   - Open WhatsApp on your phone
   - Tap Menu (⋮) or Settings
   - Tap "Linked Devices"
   - Tap "Link a Device"
   - Scan the QR code in browser window
   - Wait for login confirmation (up to 2 minutes)

4. **Verify Session Saved**
   - Setup script will confirm successful login
   - Session saved in: `AI_Employee_Vault/.state/whatsapp_session/`
   - No QR code needed for future runs

**What You'll Get**:
- WhatsApp Web session (persistent login)
- Browser profile with saved credentials
- Ready-to-use WhatsApp watcher

**Configuration**:
- Edit `config/whatsapp_config.json` to customize keywords
- Default keywords: urgent, asap, invoice, payment, help, emergency, critical

**Documentation**:
- Full guide: `AI_Employee_Vault/docs/WhatsApp_Setup_Guide.md`

---

### Priority 4: Set Up LinkedIn API (OPTIONAL - Can Skip)

**Note**: LinkedIn is optional for Silver tier. You can skip this if you're using Gmail + WhatsApp (2 watchers required).

**Steps**:

1. **Go to LinkedIn Developers**
   - URL: https://www.linkedin.com/developers/apps
   - Sign in with your LinkedIn account

2. **Create New App**
   - Click "Create app"
   - App name: "AI Employee Silver"
   - LinkedIn Page: Select your company page (or create one)
   - App logo: Upload any logo (required)
   - Click "Create app"

3. **Request Share API Access**
   - Go to "Products" tab
   - Find "Share on LinkedIn"
   - Click "Request access"
   - Fill out the form explaining your use case
   - **Note**: This may take 1-2 days for approval

4. **Get Credentials**
   - Go to "Auth" tab
   - Copy "Client ID"
   - Copy "Client Secret"
   - Add redirect URL: `http://localhost:8080/callback`

5. **Run OAuth Flow** (after implementing linkedin_auth.py)
   ```bash
   python AI_Employee_Vault/setup/linkedin_auth.py
   ```
   - Browser will open for authorization
   - Grant permissions
   - Access token will be saved to config/.env

**What You'll Get**:
- `LINKEDIN_CLIENT_ID`
- `LINKEDIN_CLIENT_SECRET`
- `LINKEDIN_ACCESS_TOKEN` (after OAuth flow)
- `LINKEDIN_PERSON_ID` (from OAuth response)

**Important**: LinkedIn access tokens expire after 60 days. You'll need to re-authenticate.

---

### Priority 5: Set Up Claude API (5 minutes)

**Steps**:

1. **Go to Anthropic Console**
   - URL: https://console.anthropic.com
   - Sign in or create account

2. **Create API Key**
   - Go to "API Keys" section
   - Click "Create Key"
   - Name: "AI Employee Silver"
   - Copy the key immediately (shown only once)

3. **Add to .env**
   ```bash
   # Edit config/.env
   CLAUDE_API_KEY=sk-ant-your-key-here
   ```

**What You'll Get**:
- `CLAUDE_API_KEY`

---

### Priority 6: Create config/.env File (5 minutes)

**Steps**:

1. **Copy template**
   ```bash
   cp config/.env.template config/.env
   ```

2. **Edit config/.env with your credentials**
   ```bash
   # Use your preferred editor
   nano config/.env
   # or
   notepad config/.env
   ```

3. **Fill in all values** (from Priority 2, 3, 4 above)
   - Replace all `your_*_here` placeholders
   - Save the file

4. **Verify .env is gitignored**
   ```bash
   # Check .gitignore contains config/.env
   grep "config/.env" .gitignore
   ```

**Important**: NEVER commit config/.env to git. It contains sensitive credentials.

---

### Priority 7: Copy Bronze Tier Files (10 minutes)

**If you have Bronze tier in a separate directory**:

```bash
# Copy Bronze tier vault structure
cp -r ../personalAIEmployee_bronze_level/AI_Employee_Vault/Inbox AI_Employee_Vault/
cp -r ../personalAIEmployee_bronze_level/AI_Employee_Vault/Needs_Action AI_Employee_Vault/
cp -r ../personalAIEmployee_bronze_level/AI_Employee_Vault/Done AI_Employee_Vault/
cp -r ../personalAIEmployee_bronze_level/AI_Employee_Vault/Pending_Approval AI_Employee_Vault/
cp -r ../personalAIEmployee_bronze_level/AI_Employee_Vault/Approved AI_Employee_Vault/
cp -r ../personalAIEmployee_bronze_level/AI_Employee_Vault/Logs AI_Employee_Vault/

# Copy Bronze tier watchers
cp ../personalAIEmployee_bronze_level/AI_Employee_Vault/base_watcher.py AI_Employee_Vault/watchers/
cp ../personalAIEmployee_bronze_level/AI_Employee_Vault/filesystem_watcher.py AI_Employee_Vault/watchers/

# Copy Bronze tier files
cp ../personalAIEmployee_bronze_level/AI_Employee_Vault/Dashboard.md AI_Employee_Vault/
cp ../personalAIEmployee_bronze_level/AI_Employee_Vault/Company_Handbook.md AI_Employee_Vault/

# Copy Bronze tier skills
cp -r ../personalAIEmployee_bronze_level/AI_Employee_Vault/.claude AI_Employee_Vault/
```

**If Bronze tier is in the same directory**:
- You already have these files
- Skip this step

---

## 📋 Summary of Manual Tasks

| Priority | Task | Time | Status |
|----------|------|------|--------|
| P1 | Install Python dependencies | 15 min | ⏳ TODO |
| P1 | Install Node.js dependencies | 5 min | ⏳ TODO |
| P2 | Set up Gmail API | 30-45 min | ⏳ TODO |
| P3 | Set up WhatsApp Watcher | 15-20 min | ⏳ TODO |
| P4 | Set up LinkedIn API (OPTIONAL) | 30-45 min | ⏸️ SKIP |
| P5 | Set up Claude API | 5 min | ⏳ TODO |
| P6 | Create config/.env file | 5 min | ⏳ TODO |
| P7 | Copy Bronze tier files | 10 min | ⏳ TODO |

**Total Estimated Time**: 2-3 hours

---

## 🚦 What Happens Next

### After You Complete Manual Tasks:

1. **I will implement Phase 2: Foundational** (OAuth scripts, config setup)
2. **I will implement Phase 3: Gmail Watcher** (email monitoring)
3. **I will implement Phase 4: Email Service** (MCP server, email sending)
4. **I will implement Phase 5: Reasoning Service** (Claude planning)
5. **I will implement Phase 6: Approval Workflow** (enhanced approval)
6. **I will implement Phase 7: LinkedIn Service** (LinkedIn posting)
7. **I will implement Phase 8: Scheduler** (automated execution)
8. **I will implement Phase 9: Integration & Testing** (verification)
9. **I will implement Phase 10: Documentation** (final polish)

---

## ⚠️ Important Notes

### Security
- **NEVER commit config/.env to git** - It contains sensitive credentials
- Keep credentials.json private (add to .gitignore)
- OAuth tokens should be refreshed automatically by the code

### API Limitations
- **Gmail API**: 250 quota units/user/second (sufficient for our use)
- **LinkedIn API**: Rate limits not publicly documented (be conservative)
- **Claude API**: Depends on your tier (check console.anthropic.com)

### OAuth Token Expiry
- **Gmail**: Access tokens expire after 1 hour (auto-refreshed by code)
- **LinkedIn**: Access tokens expire after 60 days (manual re-auth required)
- **Claude**: API keys don't expire (unless revoked)

---

## 🆘 If You Get Stuck

### Gmail API Issues
- **Error: API not enabled** → Enable Gmail API in Google Cloud Console
- **Error: Invalid credentials** → Re-download credentials.json
- **Error: Redirect URI mismatch** → Add http://localhost:8080 to authorized redirects

### LinkedIn API Issues
- **Error: App not approved** → Wait for LinkedIn to approve Share API access
- **Error: Invalid scope** → Request w_member_social scope in OAuth flow
- **Error: Token expired** → Re-run linkedin_auth.py to get new token

### Claude API Issues
- **Error: Invalid API key** → Check key is correct in config/.env
- **Error: Rate limit** → Upgrade your Claude API tier or reduce usage

---

## ✅ Checklist for You

Mark these as you complete them:

- [ ] Install Python dependencies (pip install ...)
- [ ] Install Node.js dependencies (npm install)
- [ ] Create Google Cloud project
- [ ] Enable Gmail API
- [ ] Create OAuth 2.0 credentials
- [ ] Download credentials.json
- [ ] Create LinkedIn developer app
- [ ] Request Share API access (may take 1-2 days)
- [ ] Get LinkedIn Client ID and Secret
- [ ] Create Claude API key
- [ ] Copy config/.env.template to config/.env
- [ ] Fill in all credentials in config/.env
- [ ] Verify config/.env is gitignored
- [ ] Copy Bronze tier files (if needed)

---

**When you've completed these manual tasks, let me know and I'll continue with Phase 2 implementation!**
