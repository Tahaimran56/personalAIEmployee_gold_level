# Gmail Watcher API Contract

**Service**: Gmail Watcher
**Version**: 1.0.0
**Purpose**: Monitor Gmail inbox and create action files for new emails

## Operations

### 1. Check for New Emails

**Operation**: `check_new_emails()`

**Description**: Fetches unread emails from Gmail inbox and creates action files

**Input**: None (uses credentials from .env)

**Output**:
```json
{
  "emails_found": 5,
  "action_files_created": 5,
  "errors": [],
  "last_check_timestamp": "2026-02-04T10:30:00Z"
}
```

**Behavior**:
- Fetches unread emails using Gmail API
- Filters out already processed emails (checks processed_emails.json)
- Creates action file for each new email in Needs_Action/
- Updates processed_emails.json with new email IDs
- Logs all operations

**Error Handling**:
- 401 Unauthorized → Refresh OAuth token, retry
- 429 Rate Limit → Wait and retry with exponential backoff
- 500 Server Error → Retry up to 3 times
- Network Error → Log and retry next cycle

**Performance**: Completes within 30 seconds for up to 100 emails

---

### 2. Create Action File

**Operation**: `create_action_file(email_data)`

**Description**: Creates a Markdown action file from email data

**Input**:
```json
{
  "email_id": "abc123",
  "sender": "client@example.com",
  "sender_name": "John Client",
  "subject": "URGENT: Meeting tomorrow",
  "body_preview": "Hi, we need to discuss...",
  "timestamp": "2026-02-04T10:30:00Z",
  "attachments": [
    {
      "filename": "proposal.pdf",
      "size": 1258291,
      "mime_type": "application/pdf"
    }
  ]
}
```

**Output**:
```json
{
  "action_file_path": "AI_Employee_Vault/Needs_Action/email-abc123.md",
  "priority": "urgent",
  "created_timestamp": "2026-02-04T10:31:00Z"
}
```

**Behavior**:
- Detects priority from keywords (URGENT, ASAP, IMPORTANT)
- Formats email data as Markdown with YAML frontmatter
- Writes file to Needs_Action/ directory
- Returns file path and metadata

**Validation**:
- email_id must be unique
- sender must be valid email format
- subject and body_preview must not be empty

---

### 3. Detect Priority

**Operation**: `detect_priority(subject, body)`

**Description**: Analyzes email content to determine priority level

**Input**:
```json
{
  "subject": "URGENT: Meeting tomorrow",
  "body": "Hi, we need to discuss the project urgently..."
}
```

**Output**:
```json
{
  "priority": "urgent",
  "keywords_found": ["URGENT", "urgently"]
}
```

**Priority Rules**:
- **urgent**: Contains URGENT, ASAP, CRITICAL, EMERGENCY
- **normal**: Default priority
- **low**: Contains FYI, No rush, When you have time

**Behavior**:
- Case-insensitive keyword matching
- Checks both subject and body
- Returns highest priority found

---

## Data Structures

### Email Action File Format

```markdown
---
entity_type: email_action
email_id: "abc123"
sender: "client@example.com"
sender_name: "John Client"
subject: "URGENT: Meeting tomorrow"
priority: urgent
timestamp: 2026-02-04T10:30:00Z
processed_status: pending
attachments:
  - filename: proposal.pdf
    size: 1258291
    mime_type: application/pdf
---

# Email Action: URGENT: Meeting tomorrow

**From**: John Client <client@example.com>
**Received**: 2026-02-04 10:30 AM
**Priority**: 🔴 Urgent

## Body Preview
Hi, we need to discuss the project urgently. Can we meet tomorrow at 2 PM?

## Attachments
- proposal.pdf (1.2 MB)

## Suggested Actions
1. Review proposal.pdf
2. Draft response confirming meeting
3. Add meeting to calendar
```

### Processed Emails Tracking

**File**: `AI_Employee_Vault/.state/processed_emails.json`

```json
{
  "last_updated": "2026-02-04T10:31:00Z",
  "processed_email_ids": [
    "abc123",
    "def456",
    "ghi789"
  ]
}
```

---

## Configuration

### Gmail API Credentials (.env)

```
GMAIL_CLIENT_ID=your_client_id
GMAIL_CLIENT_SECRET=your_client_secret
GMAIL_REFRESH_TOKEN=your_refresh_token
GMAIL_USER=your_email@gmail.com
```

### Watcher Configuration

```json
{
  "check_interval_seconds": 300,
  "max_emails_per_check": 100,
  "priority_keywords": {
    "urgent": ["URGENT", "ASAP", "CRITICAL", "EMERGENCY"],
    "low": ["FYI", "No rush", "When you have time"]
  }
}
```

---

## Rate Limits

- Gmail API: 250 quota units per user per second
- Typical check uses ~10 quota units
- Can check ~25 times per second (far exceeds 5-minute interval)

---

## Testing

### Unit Tests
- `test_check_new_emails()` - Mock Gmail API responses
- `test_create_action_file()` - Verify file format
- `test_detect_priority()` - Test keyword detection

### Integration Tests
- `test_end_to_end_email_detection()` - Send test email, verify action file created
- `test_duplicate_prevention()` - Verify same email not processed twice
- `test_rate_limit_handling()` - Simulate rate limit, verify retry logic
