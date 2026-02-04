# Email Service API Contract

**Service**: Email Service (MCP Server)
**Version**: 1.0.0
**Purpose**: Send emails with approval workflow via MCP server

## Operations

### 1. Compose Draft Email

**Operation**: `compose_draft_email(action_data)`

**Description**: Creates a draft email from action file data

**Input**:
```json
{
  "recipient": "client@example.com",
  "subject": "Re: Meeting tomorrow",
  "body": "Hi John, I'd be happy to meet tomorrow at 2 PM...",
  "body_format": "plain",
  "attachments": []
}
```

**Output**:
```json
{
  "draft_id": "draft-uuid-123",
  "draft_file_path": "AI_Employee_Vault/Pending_Approval/email-draft-uuid-123.md",
  "approval_status": "pending",
  "created_timestamp": "2026-02-04T10:35:00Z"
}
```

**Behavior**:
- Validates recipient email address
- Sanitizes HTML content (if body_format is html)
- Creates draft file in Pending_Approval/
- Returns draft ID for tracking

**Validation**:
- recipient must be valid email format
- subject must not be empty
- body must not be empty
- attachments total size must not exceed 25MB

---

### 2. Send Approved Email

**Operation**: `send_email(draft_id)`

**Description**: Sends an approved draft email via SMTP

**Input**:
```json
{
  "draft_id": "draft-uuid-123"
}
```

**Output**:
```json
{
  "success": true,
  "message_id": "<abc123@gmail.com>",
  "sent_timestamp": "2026-02-04T10:40:00Z",
  "log_file_path": "AI_Employee_Vault/Logs/email-sent-uuid-123.md"
}
```

**Behavior**:
- Verifies draft is approved
- Sends email via SMTP with OAuth2
- Logs sent email with message ID
- Moves draft to Done/ folder
- Updates Dashboard with sent count

**Error Handling**:
- Draft not approved → Return error, do not send
- SMTP 421 Service unavailable → Retry after 5 minutes
- SMTP 550 Mailbox not found → Permanent failure, notify user
- Network timeout → Retry up to 3 times with exponential backoff

**Performance**: Sends within 30 seconds of approval

---

### 3. Validate Email Address

**Operation**: `validate_email(email_address)`

**Description**: Validates email address format and optionally checks DNS

**Input**:
```json
{
  "email_address": "client@example.com",
  "check_dns": true
}
```

**Output**:
```json
{
  "valid": true,
  "format_valid": true,
  "dns_valid": true,
  "mx_records": ["mail.example.com"]
}
```

**Validation Rules**:
- Format: RFC 5322 compliant
- DNS: MX records exist (optional)
- Blacklist: Not in spam blacklist (optional)

---

## MCP Server Interface

### Tool Definition

```json
{
  "name": "send_email",
  "description": "Send an email with approval workflow",
  "inputSchema": {
    "type": "object",
    "properties": {
      "recipient": {"type": "string", "format": "email"},
      "subject": {"type": "string"},
      "body": {"type": "string"},
      "body_format": {"type": "string", "enum": ["plain", "html"]},
      "attachments": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "filename": {"type": "string"},
            "path": {"type": "string"}
          }
        }
      }
    },
    "required": ["recipient", "subject", "body"]
  }
}
```

### MCP Server Configuration

**File**: `config/mcp_email_server.json`

```json
{
  "server_name": "email-server",
  "transport": {
    "service": "gmail",
    "auth": {
      "type": "OAuth2",
      "user": "${GMAIL_USER}",
      "clientId": "${GMAIL_CLIENT_ID}",
      "clientSecret": "${GMAIL_CLIENT_SECRET}",
      "refreshToken": "${GMAIL_REFRESH_TOKEN}"
    }
  },
  "approval_required": true,
  "approval_timeout_hours": 24,
  "max_attachment_size_mb": 25
}
```

---

## Data Structures

### Draft Email File Format

```markdown
---
entity_type: draft_email
draft_id: "draft-uuid-123"
recipient: "client@example.com"
subject: "Re: Meeting tomorrow"
body_format: plain
created_timestamp: 2026-02-04T10:35:00Z
approval_status: pending
sent_status: not_sent
---

# Draft Email: Re: Meeting tomorrow

**To**: client@example.com
**Subject**: Re: Meeting tomorrow
**Status**: ⏳ Pending Approval

## Email Body

Hi John,

I'd be happy to meet tomorrow at 2 PM. I've reviewed the proposal and have some questions to discuss.

Looking forward to it!

Best regards

## Attachments
None

## Approval Actions
- ✅ Approve: Move to Approved/ folder
- ❌ Reject: Move to Done/ with rejection reason
```

### Sent Email Log Format

```markdown
---
entity_type: sent_email_log
draft_id: "draft-uuid-123"
message_id: "<abc123@gmail.com>"
recipient: "client@example.com"
subject: "Re: Meeting tomorrow"
sent_timestamp: 2026-02-04T10:40:00Z
approved_by: "user"
approval_timestamp: 2026-02-04T10:38:00Z
---

# Sent Email Log: Re: Meeting tomorrow

**To**: client@example.com
**Sent**: 2026-02-04 10:40 AM
**Message ID**: <abc123@gmail.com>
**Status**: ✅ Sent Successfully

## Email Body
[Email body content]

## Delivery Status
- Sent via: Gmail SMTP
- Authentication: OAuth2
- Delivery: Successful
```

---

## Rate Limits

- Gmail SMTP: 500 emails per day (free account), 2000 per day (paid)
- Rate: ~1 email per second recommended
- Batch sending: Not supported in Silver tier

---

## Testing

### Unit Tests
- `test_compose_draft_email()` - Verify draft creation
- `test_send_email()` - Mock SMTP, verify send logic
- `test_validate_email()` - Test email validation

### Integration Tests
- `test_end_to_end_email_send()` - Create draft, approve, send, verify log
- `test_approval_workflow()` - Verify approval required before send
- `test_smtp_error_handling()` - Simulate SMTP errors, verify retry logic
