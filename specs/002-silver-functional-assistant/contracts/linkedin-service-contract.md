# LinkedIn Service API Contract

**Service**: LinkedIn Service
**Version**: 1.0.0
**Purpose**: Post updates to LinkedIn with approval workflow

## Operations

### 1. Compose Draft Post

**Operation**: `compose_draft_post(action_data)`

**Description**: Creates a draft LinkedIn post from action file data

**Input**:
```json
{
  "content": "Excited to share our latest project milestone! We've successfully implemented...",
  "hashtags": ["#AI", "#Automation", "#Productivity"]
}
```

**Output**:
```json
{
  "post_id": "post-uuid-456",
  "draft_file_path": "AI_Employee_Vault/Pending_Approval/linkedin-post-uuid-456.md",
  "approval_status": "pending",
  "created_timestamp": "2026-02-04T11:00:00Z",
  "character_count": 145
}
```

**Behavior**:
- Validates content length (max 3000 characters)
- Validates hashtags format (must start with #, no spaces)
- Creates draft file in Pending_Approval/
- Returns post ID for tracking

**Validation**:
- content must not exceed 3000 characters
- content must not be empty
- hashtags must start with # and contain no spaces
- maximum 30 hashtags per post

---

### 2. Publish Approved Post

**Operation**: `publish_post(post_id)`

**Description**: Publishes an approved draft post to LinkedIn

**Input**:
```json
{
  "post_id": "post-uuid-456"
}
```

**Output**:
```json
{
  "success": true,
  "linkedin_post_id": "urn:li:share:1234567890",
  "published_timestamp": "2026-02-04T11:05:00Z",
  "post_url": "https://www.linkedin.com/feed/update/urn:li:share:1234567890",
  "log_file_path": "AI_Employee_Vault/Logs/linkedin-post-uuid-456.md"
}
```

**Behavior**:
- Verifies post is approved
- Publishes via LinkedIn Share API with OAuth2
- Logs published post with LinkedIn URN
- Moves draft to Done/ folder
- Updates Dashboard with post count

**Error Handling**:
- Post not approved → Return error, do not publish
- 401 Unauthorized → Refresh OAuth token, retry
- 403 Forbidden → Check permissions, notify user
- 429 Rate Limit → Wait 1 hour, retry
- 422 Unprocessable → Validate content, notify user

**Performance**: Publishes within 60 seconds of approval

---

### 3. Get Engagement Metrics

**Operation**: `get_engagement_metrics(linkedin_post_id)`

**Description**: Fetches engagement metrics for a published post

**Input**:
```json
{
  "linkedin_post_id": "urn:li:share:1234567890"
}
```

**Output**:
```json
{
  "views": 1250,
  "likes": 45,
  "comments": 8,
  "shares": 12,
  "last_updated": "2026-02-04T15:00:00Z"
}
```

**Behavior**:
- Fetches metrics via LinkedIn API
- Updates log file with latest metrics
- Returns engagement data

**Rate Limits**: Can fetch metrics once per hour per post

---

## LinkedIn API Integration

### OAuth2 Configuration

**Scopes Required**:
- `w_member_social` - Post updates to personal profile
- `r_basicprofile` - Read basic profile info

**Token Lifecycle**:
- Access token: Valid for 60 days
- Refresh token: Not provided by LinkedIn
- Re-authentication required after 60 days

### API Endpoints

**Post Creation**:
```
POST https://api.linkedin.com/v2/ugcPosts
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "author": "urn:li:person:{person_id}",
  "lifecycleState": "PUBLISHED",
  "specificContent": {
    "com.linkedin.ugc.ShareContent": {
      "shareCommentary": {
        "text": "Post content with #hashtags"
      },
      "shareMediaCategory": "NONE"
    }
  },
  "visibility": {
    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
  }
}
```

**Engagement Metrics**:
```
GET https://api.linkedin.com/v2/socialActions/{share_urn}/statistics
Authorization: Bearer {access_token}
```

---

## Data Structures

### Draft Post File Format

```markdown
---
entity_type: linkedin_post
post_id: "post-uuid-456"
content: "Excited to share our latest project milestone!"
hashtags:
  - "#AI"
  - "#Automation"
  - "#Productivity"
created_timestamp: 2026-02-04T11:00:00Z
approval_status: pending
publish_status: not_published
character_count: 145
---

# LinkedIn Post Draft

**Status**: ⏳ Pending Approval
**Character Count**: 145 / 3000

## Post Content

Excited to share our latest project milestone! We've successfully implemented an AI-powered automation system that saves 10 hours per week.

#AI #Automation #Productivity

## Preview
[Preview how post will appear on LinkedIn]

## Approval Actions
- ✅ Approve: Move to Approved/ folder
- ❌ Reject: Move to Done/ with rejection reason
```

### Published Post Log Format

```markdown
---
entity_type: linkedin_post_log
post_id: "post-uuid-456"
linkedin_post_id: "urn:li:share:1234567890"
published_timestamp: 2026-02-04T11:05:00Z
approved_by: "user"
approval_timestamp: 2026-02-04T11:03:00Z
engagement_metrics:
  views: 1250
  likes: 45
  comments: 8
  shares: 12
  last_updated: 2026-02-04T15:00:00Z
---

# LinkedIn Post Log

**Published**: 2026-02-04 11:05 AM
**Post URL**: https://www.linkedin.com/feed/update/urn:li:share:1234567890
**Status**: ✅ Published Successfully

## Post Content
[Post content]

## Engagement Metrics
- 👁️ Views: 1,250
- 👍 Likes: 45
- 💬 Comments: 8
- 🔄 Shares: 12

Last updated: 2026-02-04 3:00 PM
```

---

## Configuration

### LinkedIn API Credentials (.env)

```
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret
LINKEDIN_ACCESS_TOKEN=your_access_token
LINKEDIN_PERSON_ID=your_person_id
```

### Service Configuration

```json
{
  "max_content_length": 3000,
  "max_hashtags": 30,
  "approval_required": true,
  "approval_timeout_hours": 24,
  "engagement_check_interval_hours": 1,
  "default_visibility": "PUBLIC"
}
```

---

## Rate Limits

- LinkedIn API: Not publicly documented, but conservative estimates:
  - ~100 posts per day
  - ~1000 API calls per day
  - Engagement metrics: 1 request per hour per post

---

## Testing

### Unit Tests
- `test_compose_draft_post()` - Verify draft creation
- `test_publish_post()` - Mock LinkedIn API, verify publish logic
- `test_get_engagement_metrics()` - Mock metrics API

### Integration Tests
- `test_end_to_end_post_publish()` - Create draft, approve, publish, verify log
- `test_approval_workflow()` - Verify approval required before publish
- `test_oauth_token_refresh()` - Simulate token expiry, verify re-auth prompt
