# API Credentials Acquisition Guide

Step-by-step guide to obtain API credentials for Odoo, Facebook, Instagram, and Twitter integration.

## Table of Contents

1. [Odoo Credentials](#odoo-credentials)
2. [Facebook Credentials](#facebook-credentials)
3. [Instagram Credentials](#instagram-credentials)
4. [Twitter Credentials](#twitter-credentials)
5. [Security Best Practices](#security-best-practices)

---

## Odoo Credentials

### Prerequisites
- Odoo Community Edition v19+ installed
- Admin access to Odoo instance

### Step 1: Install Odoo

**Option A: Docker (Recommended)**
```bash
# Pull Odoo image
docker pull odoo:19

# Start PostgreSQL
docker run -d -e POSTGRES_USER=odoo -e POSTGRES_PASSWORD=odoo -e POSTGRES_DB=postgres --name db postgres:15

# Start Odoo
docker run -d -p 8069:8069 --name odoo --link db:db -t odoo:19
```

**Option B: Native Installation**
```bash
# Ubuntu/Debian
wget -O - https://nightly.odoo.com/odoo.key | apt-key add -
echo "deb http://nightly.odoo.com/19.0/nightly/deb/ ./" >> /etc/apt/sources.list.d/odoo.list
apt-get update && apt-get install odoo
```

### Step 2: Create Database

1. Open browser: http://localhost:8069
2. Click "Create Database"
3. Fill in details:
   - **Database Name**: `gold_tier_accounting`
   - **Email**: your email
   - **Password**: strong password (save this!)
   - **Language**: English
   - **Country**: Your country
4. Click "Create Database"

### Step 3: Get Credentials

Your Odoo credentials are:
- **URL**: `http://localhost:8069` (or your server URL)
- **Database**: `gold_tier_accounting`
- **Username**: `admin`
- **Password**: The password you set in Step 2

### Step 4: Test Connection

```bash
curl -X POST http://localhost:8069/jsonrpc \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
      "service": "common",
      "method": "authenticate",
      "args": ["gold_tier_accounting", "admin", "YOUR_PASSWORD", {}]
    },
    "id": 1
  }'
```

**Expected response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": 2
}
```

### Step 5: Configure .env

```bash
ODOO_URL=http://localhost:8069
ODOO_DATABASE=gold_tier_accounting
ODOO_USERNAME=admin
ODOO_PASSWORD=your_password_here
```

---

## Facebook Credentials

### Prerequisites
- Facebook account
- Facebook Business Page (create one if you don't have)
- Admin access to the Page

### Step 1: Create Facebook App

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Click "My Apps" → "Create App"
3. Select "Business" as app type
4. Fill in details:
   - **App Name**: "AI Employee Gold Tier"
   - **App Contact Email**: your email
5. Click "Create App"

### Step 2: Add Facebook Login Product

1. In your app dashboard, click "Add Product"
2. Find "Facebook Login" and click "Set Up"
3. Select "Web" as platform
4. Enter your website URL (can be http://localhost for testing)

### Step 3: Configure App Permissions

1. Go to "App Review" → "Permissions and Features"
2. Request these permissions:
   - `pages_manage_posts` - Required for posting
   - `pages_read_engagement` - Required for metrics
   - `pages_show_list` - Required for page access
3. Click "Request" for each permission
4. Fill in use case details (explain it's for business automation)

### Step 4: Get Page Access Token

1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app from dropdown
3. Click "Generate Access Token"
4. Select your Facebook Page
5. Grant all requested permissions
6. Copy the access token (short-lived, 1 hour)

### Step 5: Exchange for Long-Lived Token

```bash
curl -X GET "https://graph.facebook.com/v19.0/oauth/access_token?grant_type=fb_exchange_token&client_id=YOUR_APP_ID&client_secret=YOUR_APP_SECRET&fb_exchange_token=YOUR_SHORT_LIVED_TOKEN"
```

**Response:**
```json
{
  "access_token": "LONG_LIVED_TOKEN",
  "token_type": "bearer",
  "expires_in": 5183944
}
```

This token lasts 60 days. Save it securely!

### Step 6: Get Page ID

1. Go to your Facebook Page
2. Click "About"
3. Scroll to "Page ID" or "Page Transparency"
4. Copy the numeric Page ID

**Alternative method:**
```bash
curl "https://graph.facebook.com/v19.0/me/accounts?access_token=YOUR_LONG_LIVED_TOKEN"
```

### Step 7: Test Token

```bash
curl "https://graph.facebook.com/v19.0/me?access_token=YOUR_PAGE_ACCESS_TOKEN"
```

**Expected response:**
```json
{
  "name": "Your Page Name",
  "id": "123456789012345"
}
```

### Step 8: Configure .env

```bash
FACEBOOK_PAGE_ACCESS_TOKEN=your_long_lived_page_access_token
FACEBOOK_PAGE_ID=your_page_id
```

### Token Renewal

Facebook Page Access Tokens expire after 60 days. Set a reminder to renew:

1. Repeat Steps 4-5 every 60 days
2. Update .env with new token
3. Restart MCP servers

---

## Instagram Credentials

### Prerequisites
- Instagram Business Account (not personal account)
- Facebook Business Page (Instagram must be linked to it)
- Admin access to both

### Step 1: Convert to Business Account

1. Open Instagram app
2. Go to Settings → Account
3. Click "Switch to Professional Account"
4. Select "Business"
5. Complete setup

### Step 2: Link to Facebook Page

1. In Instagram app, go to Settings → Account
2. Click "Linked Accounts"
3. Select "Facebook"
4. Log in and select your Facebook Page
5. Confirm linking

### Step 3: Get Instagram Business Account ID

**Method 1: Graph API Explorer**
```bash
curl "https://graph.facebook.com/v19.0/me/accounts?fields=instagram_business_account&access_token=YOUR_FACEBOOK_TOKEN"
```

**Response:**
```json
{
  "data": [
    {
      "instagram_business_account": {
        "id": "17841400000000000"
      },
      "id": "123456789012345"
    }
  ]
}
```

**Method 2: Facebook Business Settings**
1. Go to [Facebook Business Settings](https://business.facebook.com/settings/)
2. Click "Instagram Accounts"
3. Find your account and copy the ID

### Step 4: Verify Permissions

Your Facebook Page Access Token must have these permissions:
- `instagram_basic`
- `instagram_content_publish`
- `pages_read_engagement`

Test permissions:
```bash
curl "https://graph.facebook.com/v19.0/INSTAGRAM_ACCOUNT_ID?fields=id,username&access_token=YOUR_PAGE_ACCESS_TOKEN"
```

**Expected response:**
```json
{
  "id": "17841400000000000",
  "username": "your_instagram_username"
}
```

### Step 5: Configure .env

```bash
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_instagram_business_account_id
# Note: Instagram uses the same FACEBOOK_PAGE_ACCESS_TOKEN
```

### Important Notes

- Instagram requires **Business Account**, not Creator Account
- Instagram must be linked to Facebook Page
- Same Facebook token works for both Facebook and Instagram
- Instagram posts require images (text-only posts not supported)

---

## Twitter Credentials

### Prerequisites
- Twitter account
- Elevated access to Twitter API (required for posting)

### Step 1: Apply for Developer Account

1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Click "Sign up" or "Apply"
3. Select "Hobbyist" → "Making a bot" (or appropriate category)
4. Fill in application:
   - **Account name**: Your name or business name
   - **Use case**: "Business automation and social media management"
   - **Description**: Explain you're building an AI assistant for business tasks
5. Agree to terms and submit
6. Wait for approval (usually instant, sometimes 1-2 days)

### Step 2: Create App

1. After approval, go to [Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Click "Create Project"
3. Fill in project details:
   - **Project Name**: "AI Employee Gold Tier"
   - **Use case**: "Making a bot"
   - **Description**: "Automated business updates and social media management"
4. Click "Next"
5. Create app:
   - **App Name**: "AI Employee Bot"
   - **Environment**: "Production"

### Step 3: Request Elevated Access

1. In your app dashboard, click "Elevated" under "Access Level"
2. Click "Apply for Elevated"
3. Fill in additional details:
   - **How will you use the Twitter API?**: "Post automated business updates, retrieve engagement metrics"
   - **Are you planning to analyze Twitter data?**: "Yes, to track engagement metrics"
   - **Will your app use Tweet, Retweet, Like, Follow, or Direct Message functionality?**: "Yes, Tweet functionality"
4. Submit application
5. Wait for approval (usually instant)

### Step 4: Generate API Keys

1. Go to your app → "Keys and tokens"
2. Under "Consumer Keys", click "Generate" (if not already generated)
3. Copy and save:
   - **API Key** (Consumer Key)
   - **API Secret** (Consumer Secret)
4. Under "Authentication Tokens", click "Generate"
5. Copy and save:
   - **Access Token**
   - **Access Token Secret**
6. Under "Bearer Token", click "Generate" (if not already generated)
7. Copy and save:
   - **Bearer Token**

**⚠️ IMPORTANT**: Save these immediately! You cannot view them again.

### Step 5: Configure App Permissions

1. Go to your app → "Settings"
2. Under "User authentication settings", click "Set up"
3. Enable "OAuth 1.0a"
4. Set permissions to "Read and Write"
5. Fill in callback URLs (can use http://localhost for testing)
6. Save changes

### Step 6: Test Credentials

**Test Bearer Token:**
```bash
curl "https://api.twitter.com/2/users/me" \
  -H "Authorization: Bearer YOUR_BEARER_TOKEN"
```

**Expected response:**
```json
{
  "data": {
    "id": "1234567890",
    "name": "Your Name",
    "username": "your_username"
  }
}
```

**Test OAuth 1.0a (for posting):**
```bash
# This requires OAuth signature, easier to test via MCP server
# Start Twitter MCP server and check health endpoint
curl http://localhost:3103/health
```

### Step 7: Configure .env

```bash
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_token_secret
TWITTER_BEARER_TOKEN=your_bearer_token
```

### Rate Limits

Twitter API v2 rate limits (with Elevated access):
- **Tweets**: 300 per 3 hours
- **Tweet lookup**: 900 per 15 minutes
- **User lookup**: 900 per 15 minutes

Monitor rate limits:
```bash
curl http://localhost:3103/rate_limit_status
```

---

## Security Best Practices

### 1. Never Commit Credentials

```bash
# Add to .gitignore
echo ".env" >> .gitignore
echo "*.log" >> .gitignore
echo "AI_Employee_Vault/Audit_Logs/*.json" >> .gitignore
```

### 2. Use Environment Variables

Never hardcode credentials in code:
```python
# ✅ GOOD
import os
api_key = os.getenv('TWITTER_API_KEY')

# ❌ BAD
api_key = 'abc123xyz'
```

### 3. Rotate Credentials Regularly

- **Facebook/Instagram**: Every 60 days (token expiration)
- **Twitter**: Every 90 days (recommended)
- **Odoo**: Every 180 days (recommended)
- **MCP_API_KEY**: Every 30 days (recommended)

### 4. Use Least Privilege

- **Odoo**: Create dedicated user with only Accounting permissions
- **Facebook**: Request only required permissions
- **Twitter**: Use Read and Write only (not DM permissions)

### 5. Monitor Access

```bash
# Check audit logs regularly
tail -100 AI_Employee_Vault/Audit_Logs/$(date +%Y-%m-%d).json

# Look for suspicious activity
grep "INVALID_API_KEY" AI_Employee_Vault/Audit_Logs/*.json
```

### 6. Secure Storage

- **Development**: Use .env file (never commit)
- **Production**: Use secrets manager (AWS Secrets Manager, Azure Key Vault, etc.)
- **Backup**: Store encrypted backup of credentials in secure location

### 7. Revoke Compromised Credentials

If credentials are exposed:
1. **Immediately revoke** old credentials
2. **Generate new** credentials
3. **Update** .env file
4. **Restart** all services
5. **Review** audit logs for unauthorized access
6. **Rotate** all other credentials as precaution

### 8. Use HTTPS

- Always use HTTPS for API calls (enforced by default)
- Never send credentials over HTTP
- Verify SSL certificates

### 9. Implement IP Whitelisting

```javascript
// In MCP servers (shared-utils.js)
const allowedIPs = ['127.0.0.1', '::1', 'YOUR_SERVER_IP'];

function authenticateApiKey(req, res, next) {
  const clientIP = req.ip;
  if (!allowedIPs.includes(clientIP)) {
    return res.status(403).json({error: 'Forbidden'});
  }
  // ... rest of authentication
}
```

### 10. Enable Audit Logging

All credential usage is automatically logged:
```json
{
  "log_id": "log-20260205103000-abc123",
  "timestamp": "2026-02-05T10:30:00.000Z",
  "action_type": "api_call",
  "actor": "ai_employee",
  "target": "facebook_api",
  "result": "success"
}
```

---

## Credential Checklist

Before starting, ensure you have:

- [ ] Odoo URL, database name, username, password
- [ ] Facebook Page Access Token (long-lived, 60 days)
- [ ] Facebook Page ID
- [ ] Instagram Business Account ID
- [ ] Twitter API Key and Secret
- [ ] Twitter Access Token and Secret
- [ ] Twitter Bearer Token
- [ ] MCP API Key (generated securely)
- [ ] All credentials added to .env file
- [ ] .env file added to .gitignore
- [ ] Credentials backed up securely
- [ ] Calendar reminders set for token renewal

---

## Troubleshooting

### Facebook Token Invalid

**Error**: "Invalid OAuth access token"

**Solutions**:
1. Token expired (60 days) → Generate new long-lived token
2. Missing permissions → Re-request with all required permissions
3. Page access revoked → Re-link app to Page

### Instagram Account Not Found

**Error**: "Instagram account not found"

**Solutions**:
1. Not a Business Account → Convert to Business
2. Not linked to Facebook Page → Link in Instagram settings
3. Wrong Account ID → Verify ID via Graph API

### Twitter Elevated Access Required

**Error**: "You currently have Essential access"

**Solutions**:
1. Apply for Elevated access in Developer Portal
2. Wait for approval (usually instant)
3. Regenerate tokens after approval

### Odoo Connection Refused

**Error**: "Connection refused"

**Solutions**:
1. Odoo not running → Start Odoo service
2. Wrong URL → Verify URL in .env
3. Firewall blocking → Allow port 8069

---

## Support

For additional help:
- **Facebook**: [Facebook Developers Community](https://developers.facebook.com/community/)
- **Instagram**: [Instagram Platform Documentation](https://developers.facebook.com/docs/instagram-api)
- **Twitter**: [Twitter Developer Community](https://twittercommunity.com/)
- **Odoo**: [Odoo Documentation](https://www.odoo.com/documentation/19.0/)

## Related Documentation

- [Setup Guide](gold-tier-setup.md)
- [Troubleshooting Guide](gold-tier-troubleshooting.md)
