# Research: Gold Tier Autonomous Employee

**Feature**: 003-gold-autonomous-employee
**Date**: 2026-02-05
**Purpose**: Document technology research and decisions for Gold Tier implementation

## Research Questions & Findings

### 1. Odoo JSON-RPC API Integration

**Question**: Can we integrate with Odoo Community Edition v19+ using Python?

**Research Findings**:
- **Library**: odoo-rpc-client (Python library for Odoo JSON-RPC)
- **Version Support**: Supports Odoo 8.0 through 19.0+
- **Authentication**: Username/password or API key
- **Session Management**: Automatic session handling with reconnection
- **Models Supported**: All Odoo models including account.invoice, account.payment, account.move

**Decision**: Use odoo-rpc-client library
- Mature and well-maintained
- Comprehensive documentation
- Handles authentication and session management
- Supports all accounting operations we need

**Example Usage**:
```python
from odoorpc import ODOO

odoo = ODOO('localhost', port=8069)
odoo.login('database_name', 'username', 'password')

# Create invoice
invoice_id = odoo.env['account.move'].create({
    'partner_id': customer_id,
    'move_type': 'out_invoice',
    'invoice_date': '2026-02-05',
    'invoice_line_ids': [(0, 0, {
        'product_id': product_id,
        'quantity': 1,
        'price_unit': 1500.00
    })]
})
```

**Alternatives Rejected**:
- XML-RPC: Older protocol, less feature-rich
- Direct HTTP: Too complex, manual session handling
- REST API: Requires additional Odoo modules

---

### 2. Facebook Graph API for Posting

**Question**: How do we post to Facebook pages programmatically?

**Research Findings**:
- **API**: Facebook Graph API v19.0
- **Library**: facebook-sdk (Python)
- **Authentication**: OAuth 2.0 with long-lived access tokens (60 days)
- **Endpoints**:
  - POST /{page-id}/feed - Create post
  - GET /{post-id}/insights - Get engagement metrics
- **Rate Limits**: 200 calls per hour per user

**Decision**: Use facebook-sdk with Graph API
- Official Python SDK
- Handles authentication and token refresh
- Supports all posting features (text, images, links)

**Example Usage**:
```python
import facebook

graph = facebook.GraphAPI(access_token='...')
graph.put_object(
    parent_object='page_id',
    connection_name='feed',
    message='Post content here',
    link='https://example.com'
)
```

**Requirements**:
- Facebook Developer account
- Facebook Page (not personal profile)
- Page access token with pages_manage_posts permission

**Alternatives Rejected**:
- Direct HTTP requests: More complex, no SDK benefits
- Third-party services (Buffer, Hootsuite): Costs money, adds dependency

---

### 3. Instagram Graph API for Posting

**Question**: How do we post to Instagram business accounts?

**Research Findings**:
- **API**: Instagram Graph API (part of Facebook Graph API)
- **Authentication**: Same as Facebook (OAuth 2.0)
- **Requirements**: Instagram Business Account linked to Facebook Page
- **Endpoints**:
  - POST /{ig-user-id}/media - Create media container
  - POST /{ig-user-id}/media_publish - Publish container
- **Two-Step Process**: Create container, then publish
- **Rate Limits**: 200 calls per hour per user

**Decision**: Use facebook-sdk (same library as Facebook)
- Instagram Graph API is part of Facebook Graph API
- Same authentication flow
- Requires two API calls per post (create + publish)

**Example Usage**:
```python
# Step 1: Create media container
container = graph.put_object(
    parent_object='instagram_business_account_id',
    connection_name='media',
    image_url='https://example.com/image.jpg',
    caption='Post caption'
)

# Step 2: Publish container
graph.put_object(
    parent_object='instagram_business_account_id',
    connection_name='media_publish',
    creation_id=container['id']
)
```

**Requirements**:
- Instagram Business Account (not personal)
- Facebook Page linked to Instagram account
- instagram_basic, instagram_content_publish permissions

**Alternatives Rejected**:
- Instagram Basic Display API: Read-only, can't post
- Direct HTTP: More complex, no SDK benefits

---

### 4. Twitter API v2 for Posting

**Question**: How do we post tweets programmatically?

**Research Findings**:
- **API**: Twitter API v2
- **Library**: tweepy (Python library for Twitter API)
- **Authentication**: OAuth 2.0 with bearer tokens
- **Endpoints**:
  - POST /2/tweets - Create tweet
  - GET /2/tweets/:id - Get tweet details
  - GET /2/tweets/:id/metrics - Get engagement metrics (requires elevated access)
- **Rate Limits**: 50 tweets per 24 hours (standard access)
- **Character Limit**: 280 characters (4000 for Twitter Blue)

**Decision**: Use tweepy library
- Official Python library for Twitter API v2
- Handles OAuth 2.0 authentication
- Supports all tweet features (text, images, hashtags)

**Example Usage**:
```python
import tweepy

client = tweepy.Client(
    bearer_token='...',
    consumer_key='...',
    consumer_secret='...',
    access_token='...',
    access_token_secret='...'
)

response = client.create_tweet(
    text='Tweet content here #hashtag',
    media_ids=[media_id]  # Optional
)
```

**Requirements**:
- Twitter Developer account (apply for access)
- Elevated access for engagement metrics
- OAuth 2.0 credentials (consumer key, secret, access token)

**Alternatives Rejected**:
- Twitter API v1.1: Deprecated, use v2
- Direct HTTP: More complex, no SDK benefits

---

### 5. Ralph Wiggum Autonomous Loop Pattern

**Question**: How do we make Claude Code continue working without user intervention?

**Research Findings**:
- **Pattern**: Stop hook with state file checking
- **Mechanism**: Claude Code supports hooks that intercept exit
- **Hook Location**: `.claude/hooks/stop.sh` (or stop.ps1 for Windows)
- **State Tracking**: File in `In_Progress/` folder indicates task incomplete
- **Completion Detection**: File moved to `Done/` indicates completion

**Decision**: Implement stop hook pattern
- Proven pattern from Ralph Wiggum reference implementation
- Works with Claude Code's execution model
- Simple state tracking with files
- Max iteration limit prevents infinite loops

**Hook Logic**:
```bash
#!/bin/bash
# .claude/hooks/stop.sh

# Check if task file exists in In_Progress/
if [ -f "AI_Employee_Vault/In_Progress/current_task.md" ]; then
  # Task incomplete, re-inject prompt
  echo "Task incomplete, continuing..."
  exit 1  # Non-zero exit prevents Claude from stopping
else
  # Task complete, allow exit
  echo "Task complete!"
  exit 0
fi
```

**Implementation Details**:
- Max iterations: 10 (configurable)
- Timeout per iteration: 5 minutes
- State file format: Markdown with YAML frontmatter
- Graceful exit on max iterations or timeout

**Alternatives Rejected**:
- Promise-based: Less reliable, requires Claude to output tag
- Polling loop: More complex, separate process
- Event-driven: Doesn't integrate with Claude Code

---

### 6. Operation Queuing for Error Recovery

**Question**: How do we handle temporary service outages without losing data?

**Research Findings**:
- **Pattern**: Local JSON-based queue with retry logic
- **Storage**: JSON files in `Queue/` folder
- **Retry Strategy**: Exponential backoff (1min, 2min, 4min, 8min, 16min, 30min max)
- **Expiry**: 24 hours, then alert user
- **Queue Processing**: Scheduler checks every 5 minutes

**Decision**: Use JSON file-based queue
- Simple and human-readable
- No database required (aligns with constitution)
- Persistent across restarts
- Easy to debug and manually fix

**Queue File Structure**:
```json
{
  "operation_id": "uuid-here",
  "operation_type": "odoo_transaction",
  "target": "odoo",
  "parameters": {
    "invoice_data": {...}
  },
  "retry_count": 0,
  "max_retries": 10,
  "next_retry": "2026-02-05T10:30:00Z",
  "expiry": "2026-02-06T09:00:00Z",
  "status": "pending",
  "created_at": "2026-02-05T09:00:00Z",
  "last_error": null
}
```

**Retry Logic**:
- Attempt 1: Immediate
- Attempt 2: +1 minute
- Attempt 3: +2 minutes
- Attempt 4: +4 minutes
- Attempt 5: +8 minutes
- Attempt 6+: +30 minutes (max)

**Alternatives Rejected**:
- In-memory queue: Lost on restart
- Database queue: Violates no-database constraint
- No queue: Data loss risk

---

### 7. Audit Logging Format

**Question**: What format should we use for comprehensive audit logs?

**Research Findings**:
- **Format**: JSON (machine-parseable)
- **Organization**: Daily files (YYYY-MM-DD.json)
- **Retention**: 90 days
- **Size Estimate**: ~100MB per month for 10,000 transactions

**Decision**: Daily JSON log files
- Machine-parseable for analysis
- Daily files keep sizes manageable
- Structured format enables filtering
- Human-readable with JSON viewer

**Log Entry Schema**:
```json
{
  "timestamp": "ISO 8601 datetime",
  "action_type": "social_post|odoo_transaction|email_send|ceo_briefing",
  "actor": "ai_employee|user",
  "target": "facebook|instagram|twitter|odoo|email",
  "parameters": {
    "redacted_sensitive_data": "last 4 digits only"
  },
  "approval_status": "approved|pending|rejected|not_required",
  "approved_by": "user|null",
  "result": "success|failure",
  "error": "error message if failed",
  "duration_ms": 1234
}
```

**Alternatives Rejected**:
- Single log file: Grows too large
- Markdown logs: Harder to parse programmatically
- Database logs: Violates constitution

---

## Technology Stack Summary

### Python Libraries (New)
- **odoo-rpc-client>=0.9.0**: Odoo integration
- **facebook-sdk>=3.1.0**: Facebook/Instagram posting
- **tweepy>=4.14.0**: Twitter posting

### Node.js Libraries (New)
- **axios>=1.6.0**: HTTP client for MCP servers

### External Services
- **Odoo Community Edition v19+**: Self-hosted accounting system
- **Facebook Graph API v19.0**: Social media posting
- **Instagram Graph API**: Social media posting (via Facebook)
- **Twitter API v2**: Social media posting

### Authentication Methods
- **Odoo**: Username/password or API key
- **Facebook/Instagram**: OAuth 2.0 with long-lived tokens (60 days)
- **Twitter**: OAuth 2.0 with bearer tokens

---

## Implementation Risks & Mitigations

### High-Risk Areas
1. **Odoo API Complexity**: Mitigate with test instance and examples
2. **Ralph Wiggum Loop Reliability**: Mitigate with max iterations and timeout
3. **Social Media API Changes**: Mitigate with official SDKs and version locking

### Medium-Risk Areas
4. **Queue Management**: Mitigate with size limits and health monitoring
5. **API Credential Acquisition**: Mitigate with detailed setup guides

### Low-Risk Areas
6. **Cross-Platform Compatibility**: Mitigate with testing on all platforms

---

## Conclusion

All technology choices validated and documented. No unresolved questions or NEEDS CLARIFICATION markers. Ready to proceed to Phase 1 (Design & Contracts).

**Key Decisions**:
- ✅ Odoo: odoo-rpc-client library
- ✅ Facebook/Instagram: facebook-sdk library
- ✅ Twitter: tweepy library
- ✅ Ralph Wiggum: Stop hook pattern
- ✅ Queue: JSON file-based with exponential backoff
- ✅ Audit Logs: Daily JSON files with 90-day retention

**Next Steps**: Create data-model.md, contracts/, and quickstart.md
