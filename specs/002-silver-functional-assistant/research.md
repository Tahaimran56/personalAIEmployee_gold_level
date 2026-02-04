# Research: Silver Tier Functional Assistant

**Feature**: 002-silver-functional-assistant
**Date**: 2026-02-04
**Purpose**: Resolve technical unknowns and establish best practices for Gmail, LinkedIn, MCP email, Claude reasoning, and scheduling integrations

## Research Areas

### 1. Gmail API Integration

**Decision**: Use Gmail API with OAuth2 and service account delegation

**Rationale**:
- Gmail API provides structured access to email data (better than IMAP)
- OAuth2 ensures secure authentication without storing passwords
- Service account delegation allows background access without user interaction
- Official Python client library (google-api-python-client) is well-maintained

**Best Practices**:
- Use OAuth2 with refresh tokens (access tokens expire after 1 hour)
- Implement exponential backoff for rate limit errors (quota: 250 units/user/second)
- Use `users.messages.list` with `q` parameter for filtering (e.g., "is:unread")
- Use `users.messages.get` with `format=metadata` to minimize quota usage
- Store message IDs in processed_emails.json to prevent duplicates
- Handle rate limits with 429 status code → wait and retry
- Use batch requests for multiple operations (up to 100 requests per batch)

**Error Handling**:
- 401 Unauthorized → refresh OAuth token
- 403 Forbidden → check API quotas and permissions
- 429 Too Many Requests → exponential backoff (1s, 2s, 4s, 8s)
- 500/503 Server Error → retry up to 3 times
- Network errors → log and retry next cycle

**Implementation Pattern**:
```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def get_gmail_service():
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build('gmail', 'v1', credentials=creds)
```

**Alternatives Considered**:
- IMAP: Rejected - less structured, harder to parse, no rate limit info
- Email forwarding: Rejected - requires email provider config, not portable

---

### 2. LinkedIn API Integration

**Decision**: Use LinkedIn OAuth2 with Share API for posting

**Rationale**:
- LinkedIn Share API allows posting text updates with hashtags
- OAuth2 provides secure authentication
- API supports both personal profiles and company pages
- Rate limits are reasonable for Silver tier use case (~10 posts/week)

**Best Practices**:
- Use OAuth2 authorization code flow (not implicit flow)
- Request minimal scopes: `w_member_social` for personal posts
- Store access tokens securely (expire after 60 days)
- Use refresh tokens to get new access tokens
- Validate post content before API call (max 3000 characters)
- Include hashtags in post text (no separate hashtag field)
- Handle rate limits gracefully (LinkedIn doesn't publish exact limits)

**Error Handling**:
- 401 Unauthorized → refresh OAuth token or re-authenticate
- 403 Forbidden → check permissions and scopes
- 429 Too Many Requests → wait 1 hour and retry
- 422 Unprocessable Entity → validate post content
- Network errors → retry up to 3 times with exponential backoff

**Implementation Pattern**:
```python
import requests

def post_to_linkedin(access_token, content):
    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "author": f"urn:li:person:{person_id}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": content},
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()
```

**Alternatives Considered**:
- Unofficial linkedin-api library: Rejected - uses scraping, violates ToS
- Selenium automation: Rejected - fragile, requires browser, violates ToS
- Email-to-LinkedIn: Rejected - not supported by LinkedIn

---

### 3. MCP Email Server Integration

**Decision**: Use custom MCP server with nodemailer for email sending

**Rationale**:
- MCP (Model Context Protocol) provides standardized interface for Claude
- nodemailer is mature, supports SMTP, OAuth2, and attachments
- Custom MCP server allows approval workflow integration
- Can use Gmail SMTP with OAuth2 (no app passwords needed)

**Best Practices**:
- Use OAuth2 for SMTP authentication (not app passwords)
- Validate email addresses before sending (regex + DNS check)
- Sanitize HTML content to prevent XSS
- Limit attachment size (25MB max for Gmail)
- Log all sent emails with message ID
- Implement retry logic for transient failures
- Use connection pooling for multiple emails

**Error Handling**:
- SMTP 421 Service not available → retry after 5 minutes
- SMTP 450 Mailbox unavailable → retry up to 3 times
- SMTP 550 Mailbox not found → permanent failure, notify user
- SMTP 552 Mailbox full → permanent failure, notify user
- Network timeout → retry with exponential backoff

**Implementation Pattern**:
```javascript
const nodemailer = require('nodemailer');

const transporter = nodemailer.createTransport({
  service: 'gmail',
  auth: {
    type: 'OAuth2',
    user: process.env.GMAIL_USER,
    clientId: process.env.GMAIL_CLIENT_ID,
    clientSecret: process.env.GMAIL_CLIENT_SECRET,
    refreshToken: process.env.GMAIL_REFRESH_TOKEN
  }
});

async function sendEmail(to, subject, body, attachments) {
  const info = await transporter.sendMail({
    from: process.env.GMAIL_USER,
    to, subject, html: body, attachments
  });
  return info.messageId;
}
```

**Alternatives Considered**:
- SendGrid/Mailgun: Rejected - requires cloud service, violates local-first
- Python smtplib: Rejected - less feature-rich than nodemailer
- Direct Gmail API send: Considered - but MCP pattern preferred for consistency

---

### 4. Claude API Reasoning Loop

**Decision**: Use Claude API with structured prompts for plan generation

**Rationale**:
- Claude Sonnet 4.5 has strong reasoning capabilities
- Structured prompts ensure consistent plan format
- API supports long context (200K tokens) for complex tasks
- Can include relevant context from vault in prompts

**Best Practices**:
- Use system prompts to define plan format and structure
- Include task description, success criteria, and constraints in prompt
- Request numbered steps with acceptance criteria
- Use temperature=0.7 for creative but consistent plans
- Limit plan generation to 4000 tokens max
- Cache system prompts to reduce costs
- Include examples of good plans in system prompt

**Prompt Pattern**:
```
System: You are a task planning assistant. Generate a detailed plan with:
1. Numbered steps (1-10 steps max)
2. Each step has: description, acceptance criteria, estimated effort
3. Steps are ordered by dependencies
4. Plan is actionable and testable

User: Task: {task_description}
Context: {relevant_context}
Success Criteria: {success_criteria}

Generate a plan in markdown format.
```

**Error Handling**:
- 401 Unauthorized → check API key
- 429 Too Many Requests → exponential backoff
- 500 Server Error → retry up to 3 times
- Timeout → reduce context size and retry
- Invalid response → log error, notify user

**Alternatives Considered**:
- Local LLM (Ollama): Rejected - requires GPU, slower, less capable
- GPT-4: Rejected - Claude Code already uses Claude, consistency preferred
- Rule-based planning: Rejected - not flexible enough for varied tasks

---

### 5. Cross-Platform Scheduling

**Decision**: Use Python schedule library + platform-specific persistence

**Rationale**:
- Python schedule library is simple and cross-platform
- Platform-specific persistence (cron/Task Scheduler) ensures survival across reboots
- Hybrid approach: Python for runtime, native scheduler for startup

**Best Practices**:
- Use schedule library for in-process scheduling (simple, no dependencies)
- Generate cron entries (Linux/Mac) or Task Scheduler XML (Windows) for persistence
- Detect platform with `sys.platform` (win32, linux, darwin)
- Store schedule config in scheduler_config.json
- Run scheduler as background process with logging
- Implement graceful shutdown (SIGTERM handler)

**Implementation Pattern**:
```python
import schedule
import time
import sys

def run_gmail_watcher():
    # Watcher logic here
    pass

# Runtime scheduling
schedule.every(5).minutes.do(run_gmail_watcher)

# Persistence (Linux/Mac)
if sys.platform != 'win32':
    cron_entry = "*/5 * * * * python /path/to/scheduler.py"
    # Add to crontab

# Persistence (Windows)
else:
    # Create Task Scheduler XML and import
    pass

while True:
    schedule.run_pending()
    time.sleep(1)
```

**Error Handling**:
- Scheduled task fails → log error, continue schedule
- Scheduler process crashes → restart via systemd/Task Scheduler
- Config file missing → use defaults, warn user
- Permission denied (cron/Task Scheduler) → notify user, run in-process only

**Alternatives Considered**:
- APScheduler: Rejected - heavier, more complex than needed
- Celery: Rejected - requires message broker, overkill for Silver tier
- Native only (cron/Task Scheduler): Rejected - harder to configure cross-platform

---

### 6. OAuth Token Management

**Decision**: Store tokens in .env with automatic refresh

**Rationale**:
- .env file is gitignored, secure for local storage
- Automatic refresh prevents user interruption
- Refresh tokens are long-lived (Gmail: no expiry, LinkedIn: 60 days)
- Centralized token management simplifies code

**Best Practices**:
- Store refresh tokens in .env (never access tokens)
- Check token expiry before each API call
- Refresh proactively (5 minutes before expiry)
- Handle refresh failures gracefully (notify user, pause operations)
- Log token refresh events (without exposing tokens)
- Use OS keychain for production (optional enhancement)

**Token Storage Format (.env)**:
```
GMAIL_CLIENT_ID=xxx
GMAIL_CLIENT_SECRET=xxx
GMAIL_REFRESH_TOKEN=xxx
LINKEDIN_CLIENT_ID=xxx
LINKEDIN_CLIENT_SECRET=xxx
LINKEDIN_REFRESH_TOKEN=xxx
CLAUDE_API_KEY=xxx
```

**Error Handling**:
- Refresh token expired → notify user, provide re-auth link
- Invalid refresh token → notify user, provide re-auth link
- Network error during refresh → retry up to 3 times
- .env file missing → create template, notify user

**Alternatives Considered**:
- OS keychain (Keyring): Considered for future - more secure but complex
- Encrypted file: Rejected - adds complexity, .env + gitignore sufficient for Silver
- Database: Rejected - violates Markdown-first principle

---

### 7. Error Handling Patterns

**Decision**: Implement tiered error handling with logging and user notification

**Rationale**:
- Different errors require different responses (retry vs notify)
- Comprehensive logging enables debugging
- User notification prevents silent failures
- Graceful degradation maintains system stability

**Error Tiers**:
1. **Transient Errors** (retry automatically)
   - Network timeouts
   - Rate limits (429)
   - Server errors (500, 503)
   - Action: Exponential backoff, retry up to 3 times

2. **Authentication Errors** (notify user)
   - Invalid credentials (401)
   - Expired tokens (401)
   - Insufficient permissions (403)
   - Action: Log error, notify user, pause operations

3. **Validation Errors** (log and skip)
   - Malformed data
   - Invalid email addresses
   - Content too long
   - Action: Log error, move to Done/ with error status

4. **Fatal Errors** (shutdown gracefully)
   - Config file missing
   - Vault path invalid
   - Python version incompatible
   - Action: Log error, notify user, exit cleanly

**Logging Pattern**:
```python
import logging

logging.basicConfig(
    filename='vault/Logs/watcher.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

try:
    result = api_call()
except HttpError as e:
    if e.resp.status == 429:
        logging.warning(f"Rate limit hit: {e}")
        time.sleep(exponential_backoff())
        retry()
    elif e.resp.status == 401:
        logging.error(f"Auth failed: {e}")
        notify_user("Please re-authenticate")
    else:
        logging.error(f"API error: {e}")
        raise
```

---

## Summary of Decisions

| Area | Decision | Key Benefit |
|------|----------|-------------|
| Gmail | OAuth2 + Gmail API | Structured access, rate limit info |
| LinkedIn | OAuth2 + Share API | Official API, secure auth |
| Email Send | MCP + nodemailer | Standardized interface, mature library |
| Reasoning | Claude API + structured prompts | Strong reasoning, consistent format |
| Scheduling | Python schedule + native persistence | Cross-platform, survives reboots |
| Tokens | .env + auto-refresh | Secure, automatic, simple |
| Errors | Tiered handling + logging | Graceful degradation, debuggable |

## Next Steps

1. Create data-model.md with entity definitions
2. Create API contracts in contracts/ directory
3. Create quickstart.md with setup instructions
4. Update agent context with new technologies
5. Proceed to Phase 2: Task generation
