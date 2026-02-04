# Post LinkedIn Skill

**Skill Name**: post-linkedin
**Version**: 1.0.0
**Purpose**: Draft and publish LinkedIn posts with approval workflow

## Description

This skill enables drafting LinkedIn business posts with human-in-the-loop approval before publishing. Posts are created as draft files in the Pending_Approval/ folder, reviewed by the user, and automatically published after approval.

## Usage

### Basic Usage

```
/post-linkedin "Your post content here"
```

### With Hashtags

```
/post-linkedin "Your post content here" --hashtags AI Automation Python ProductivityTools
```

### With Visibility Setting

```
/post-linkedin "Your post content here" --visibility CONNECTIONS
```

## Parameters

- `content` (required): Post content text (max 3000 characters)
- `--hashtags` (optional): List of hashtags (max 30, alphanumeric only)
- `--visibility` (optional): Post visibility
  - `PUBLIC` (default): Visible to everyone
  - `CONNECTIONS`: Visible to your connections only
  - `LOGGED_IN`: Visible to logged-in LinkedIn members

## Content Validation

The skill automatically validates:
- **Character limit**: Maximum 3000 characters
- **Hashtag limit**: Maximum 30 hashtags
- **Hashtag format**: Only letters, numbers, and underscores (no spaces or special characters)
- **Empty content**: Content cannot be empty

## Approval Workflow

### Step 1: Draft Creation

When you run the skill, it creates a draft file in `Pending_Approval/`:

```markdown
---
entity_type: draft_linkedin_post
draft_id: linkedin-draft-20260204120000
visibility: PUBLIC
created_timestamp: 2026-02-04T12:00:00Z
approval_status: pending
published_status: not_published
character_count: 245
hashtags:
  - AI
  - Automation
  - Python
---

# Draft LinkedIn Post

**Visibility**: PUBLIC
**Status**: ⏳ Pending Approval
**Character Count**: 245 / 3000

## Post Content

Excited to share our latest AI automation project! 🚀

We've built a personal AI assistant that helps manage emails, tasks, and social media posts.

#AI #Automation #Python

## Approval Actions
- ✅ **Approve**: Move this file to Approved/ folder
- ❌ **Reject**: Move this file to Done/ folder
```

### Step 2: User Review

1. Open the draft file in Obsidian
2. Review the post content
3. Check character count and hashtags
4. Verify visibility setting

### Step 3: Approval

**To Approve**:
- Move the file from `Pending_Approval/` to `Approved/` folder
- The system will automatically publish the post

**To Reject**:
- Move the file from `Pending_Approval/` to `Done/` folder
- Add rejection reason in the file (optional)

### Step 4: Publishing

Once approved:
1. System detects file in `Approved/` folder
2. Publishes post via LinkedIn Share API
3. Logs published post in `Logs/linkedin-post-{draft_id}.md`
4. Moves draft to `Done/` folder

## Example Usage

### Example 1: Simple Post

```
/post-linkedin "Just launched our new AI automation tool! Check it out at example.com"
```

**Output**:
```
Draft created: AI_Employee_Vault/Pending_Approval/linkedin-draft-20260204120000.md
Character count: 67 / 3000
Status: Pending approval
```

### Example 2: Post with Hashtags

```
/post-linkedin "Excited to announce our Q1 results! Revenue up 25% 📈" --hashtags Business Growth Q1Results
```

**Output**:
```
Draft created: AI_Employee_Vault/Pending_Approval/linkedin-draft-20260204120001.md
Character count: 52 / 3000
Hashtags: #Business #Growth #Q1Results
Status: Pending approval
```

### Example 3: Connections-Only Post

```
/post-linkedin "Looking for a senior Python developer to join our team. DM me if interested!" --visibility CONNECTIONS
```

**Output**:
```
Draft created: AI_Employee_Vault/Pending_Approval/linkedin-draft-20260204120002.md
Character count: 78 / 3000
Visibility: CONNECTIONS
Status: Pending approval
```

## Implementation

The skill uses the `LinkedInService` class:

```python
from AI_Employee_Vault.services.linkedin_service import LinkedInService

service = LinkedInService(vault_path)

# Compose draft post
draft = service.compose_draft_post(
    content="Your post content here",
    visibility='PUBLIC',
    hashtags=['AI', 'Automation']
)

print(f"Draft created: {draft['draft_file_path']}")
```

## Publishing Process

After approval, the system:

1. Reads draft from `Approved/` folder
2. Validates approval status
3. Checks LinkedIn token expiry (60-day limit)
4. Publishes via LinkedIn Share API
5. Logs published post with post ID
6. Moves draft to `Done/` folder

## Engagement Metrics

After publishing, you can fetch engagement metrics:

```python
from AI_Employee_Vault.services.linkedin_service import LinkedInService

service = LinkedInService(vault_path)
metrics = service.get_engagement_metrics(post_id)

print(f"Likes: {metrics['likes']}")
print(f"Comments: {metrics['comments']}")
print(f"Shares: {metrics['shares']}")
print(f"Impressions: {metrics['impressions']}")
```

## Error Handling

### Validation Errors

- **Content too long**: "Post exceeds maximum length: 3500 / 3000 characters"
- **Too many hashtags**: "Too many hashtags: 35 / 30"
- **Invalid hashtag**: "Invalid hashtag format: #my-tag (use only letters, numbers, underscores)"
- **Empty content**: "Post content cannot be empty"

### API Errors

- **401 Unauthorized**: Token expired. Run: `python AI_Employee_Vault/setup/linkedin_auth.py`
- **403 Forbidden**: Permission denied. Check LinkedIn app permissions.
- **429 Rate Limit**: Too many requests. Wait and retry.
- **422 Unprocessable**: Invalid post content. Check format and length.

### Token Expiry

LinkedIn access tokens expire after 60 days. The system:
- Checks token expiry before publishing
- Warns if token expires within 7 days
- Errors if token is expired
- Logs expiry warnings in `Logs/linkedin_service.log`

## Prerequisites

1. LinkedIn API credentials configured in `config/.env`:
   ```
   LINKEDIN_CLIENT_ID=your_client_id
   LINKEDIN_CLIENT_SECRET=your_client_secret
   LINKEDIN_ACCESS_TOKEN=your_access_token
   LINKEDIN_PERSON_ID=your_person_id
   ```

2. LinkedIn app setup:
   - Create app at https://www.linkedin.com/developers/apps
   - Request "Share on LinkedIn" product access
   - Add redirect URL: http://localhost:8080/callback
   - Run OAuth setup: `python AI_Employee_Vault/setup/linkedin_auth.py`

3. Python dependencies installed:
   ```bash
   pip install requests python-dotenv
   ```

## Security Notes

- **Approval Required**: All posts require explicit approval before publishing
- **Token Expiry**: 60-day token expiry enforced
- **Audit Trail**: All posts logged with timestamps
- **Visibility Control**: User controls post visibility (PUBLIC, CONNECTIONS, LOGGED_IN)
- **Content Validation**: Automatic validation prevents invalid posts

## Related Skills

- `/process-actions` - Automatically processes LinkedIn post requests
- `/create-plan` - Create multi-step plans (can include LinkedIn posts)
- `/send-email` - Send emails (similar approval workflow)

## Troubleshooting

### "LinkedIn credentials not found"
**Solution**: Run `python AI_Employee_Vault/setup/linkedin_auth.py` to set up OAuth

### "Token expired"
**Solution**: Re-run `python AI_Employee_Vault/setup/linkedin_auth.py` to refresh token

### "Permission denied"
**Solution**: Check LinkedIn app has "Share on LinkedIn" product access approved

### "Post not publishing after approval"
**Solution**: Check `Logs/linkedin_service.log` for errors. Ensure file is in `Approved/` folder.

### "Character count incorrect"
**Solution**: Hashtags are added to content. Count includes hashtags in final post.

## Notes

- Posts are published immediately after approval (no scheduling)
- Hashtags are automatically formatted with # prefix
- Visibility cannot be changed after publishing
- Engagement metrics may take time to populate
- LinkedIn API has rate limits (check LinkedIn documentation)
- Token refresh requires manual re-authentication (no refresh token)
- Draft files can be edited before approval
- Rejected drafts are archived in `Done/` folder
