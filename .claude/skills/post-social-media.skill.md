---
name: post-social-media
description: Post business updates to Facebook, Instagram, and Twitter with approval workflow
version: 1.0.0
author: AI Employee Gold Tier
created: 2026-02-05
---

# Post to Social Media

Post business updates to multiple social media platforms (Facebook, Instagram, Twitter) with built-in validation, approval workflow, and engagement tracking.

## Usage

This skill enables the AI Employee to:
- Create social media posts for multiple platforms
- Validate content against platform requirements
- Submit posts for approval (optional)
- Publish approved posts automatically
- Track engagement metrics after 24 hours
- Handle errors with automatic retry

## Prerequisites

- MCP servers running:
  - Facebook MCP: http://localhost:3101
  - Instagram MCP: http://localhost:3102
  - Twitter MCP: http://localhost:3103
- Environment variables configured in .env:
  - `FACEBOOK_PAGE_ACCESS_TOKEN`
  - `FACEBOOK_PAGE_ID`
  - `INSTAGRAM_BUSINESS_ACCOUNT_ID`
  - `TWITTER_API_KEY`, `TWITTER_API_SECRET`, `TWITTER_ACCESS_TOKEN`, `TWITTER_ACCESS_SECRET`
  - `MCP_API_KEY`
- Social media accounts connected and authorized

## Platform Requirements

### Facebook
- **Text limit**: 63,206 characters
- **Image**: Optional
- **Link**: Optional
- **Best practices**: Include engaging visuals, ask questions, use emojis sparingly

### Instagram
- **Text limit**: 2,200 characters
- **Image**: **REQUIRED** (Instagram is a visual platform)
- **Hashtags**: Recommended (up to 30, but 5-10 is optimal)
- **Best practices**: High-quality images, relevant hashtags, engaging captions

### Twitter
- **Text limit**: 280 characters
- **Image**: Optional
- **Hashtags**: Optional (but recommended for discoverability)
- **Best practices**: Concise messaging, 1-2 hashtags, include links

## Commands

### Post to Single Platform

```
Post to Facebook: "Check out our new product launch! 🚀 #innovation #tech"
```

```
Post to Instagram with image: "Behind the scenes at our office" with image https://example.com/office.jpg
```

```
Post to Twitter: "Excited to announce our Q1 results! Revenue up 25% 📈 #business #growth"
```

### Post to Multiple Platforms

```
Post to Facebook and Instagram: "Join us for our webinar on AI automation next week! Register at example.com/webinar" with image https://example.com/webinar-banner.jpg
```

**What happens:**
1. AI Employee validates content for both platforms
2. Creates draft post in Pending_Approval/ folder
3. Waits for your approval
4. After approval, publishes to both platforms
5. Tracks engagement metrics after 24 hours

### Post with Approval Workflow

```
Create social media post for approval:
- Platforms: Facebook, Instagram, Twitter
- Text: "We're hiring! Join our team as a Senior Developer. Apply at example.com/careers"
- Image: https://example.com/hiring-banner.jpg
- Hashtags: hiring, jobs, developer, tech
```

**Approval workflow:**
1. AI Employee creates draft post
2. Saves to `AI_Employee_Vault/Pending_Approval/social_post_[timestamp].json`
3. Notifies you for review
4. You review and approve/reject
5. If approved, AI Employee publishes to all platforms
6. If rejected, AI Employee archives the draft

### Retrieve Engagement Metrics

```
Get engagement metrics for Facebook post [post_id]
```

```
Get engagement metrics for Instagram post [media_id]
```

```
Get engagement metrics for Twitter tweet [tweet_id]
```

**Metrics returned:**
- **Facebook**: Likes, comments, shares, reach, impressions, engagement rate
- **Instagram**: Likes, comments, saves, reach, impressions, engagement rate
- **Twitter**: Likes, retweets, replies, impressions, engagement rate

## Configuration

### Social Media Config (config/social_media_config.json)

```json
{
  "approval_workflow": {
    "enabled": true,
    "require_approval_for": ["facebook", "instagram", "twitter"],
    "approval_timeout_hours": 24,
    "auto_reject_on_timeout": false
  },
  "posting_schedule": {
    "facebook": {
      "optimal_times": ["09:00", "13:00", "19:00"],
      "timezone": "America/New_York"
    },
    "instagram": {
      "optimal_times": ["11:00", "14:00", "20:00"],
      "timezone": "America/New_York"
    },
    "twitter": {
      "optimal_times": ["08:00", "12:00", "17:00"],
      "timezone": "America/New_York"
    }
  },
  "engagement_tracking": {
    "enabled": true,
    "check_after_hours": 24,
    "metrics_retention_days": 90
  },
  "rate_limits": {
    "facebook": {
      "posts_per_hour": 10,
      "posts_per_day": 100
    },
    "instagram": {
      "posts_per_hour": 5,
      "posts_per_day": 25
    },
    "twitter": {
      "tweets_per_hour": 50,
      "tweets_per_day": 300
    }
  }
}
```

### Environment Variables (.env)

```bash
# Facebook
FACEBOOK_PAGE_ACCESS_TOKEN=your_facebook_page_access_token
FACEBOOK_PAGE_ID=your_facebook_page_id

# Instagram (uses Facebook Graph API)
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_instagram_business_account_id

# Twitter
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_SECRET=your_twitter_access_secret
TWITTER_BEARER_TOKEN=your_twitter_bearer_token

# MCP Servers
FACEBOOK_MCP_URL=http://localhost:3101
INSTAGRAM_MCP_URL=http://localhost:3102
TWITTER_MCP_URL=http://localhost:3103
MCP_API_KEY=your_secure_api_key
```

## Validation Rules

The AI Employee automatically validates posts before submission:

### Text Length
- Facebook: Max 63,206 characters
- Instagram: Max 2,200 characters
- Twitter: Max 280 characters

### Image Requirements
- Instagram: Image is **REQUIRED**
- Facebook/Twitter: Image is optional
- Supported formats: JPG, PNG, GIF
- Image URL must be publicly accessible (https://)

### Hashtags
- Maximum 30 hashtags recommended
- More than 30 hashtags may reduce engagement
- Hashtags automatically added to caption/text

### Links
- Must start with http:// or https://
- Link shorteners are allowed
- Instagram: Links in bio only (not clickable in captions)

## Error Handling

### Validation Errors

If validation fails, AI Employee will:
1. Report specific validation errors
2. Suggest corrections
3. Wait for corrected input

**Example validation error:**
```
❌ Validation failed:
- Instagram: Image is required
- Twitter: Text exceeds 280 characters (current: 315)

Suggestions:
- Add an image URL for Instagram
- Shorten Twitter text to 280 characters or less
```

### Publishing Errors

If publishing fails, AI Employee will:
1. Log error to Audit_Logs/
2. Queue post for retry in Queue/
3. Retry with exponential backoff (2min, 4min, 8min, 16min, 30min)
4. Alert you if post expires after 24 hours

**Common publishing errors:**
- **Invalid token**: Access token expired or invalid → Refresh token
- **Rate limit**: Too many posts in short time → Queued for retry
- **API unavailable**: Platform API is down → Queued for retry
- **Content violation**: Post violates platform policies → Manual review required

### Rate Limit Handling

When rate limit is reached:
1. AI Employee detects rate limit error
2. Calculates next available time slot
3. Queues post for automatic retry
4. Notifies you of delay

**Example:**
```
⚠️ Rate limit reached for Twitter (50 tweets/hour)
📅 Post queued for retry at 2026-02-05 15:30:00
✓ You will be notified when post is published
```

## Approval Workflow

### Step 1: Create Draft Post

AI Employee creates draft post and saves to:
```
AI_Employee_Vault/Pending_Approval/social_post_20260205103000.json
```

**Draft format:**
```json
{
  "post_id": "social_post_20260205103000",
  "created_at": "2026-02-05T10:30:00Z",
  "platforms": ["facebook", "instagram"],
  "text": "Check out our new product! 🚀",
  "image_url": "https://example.com/product.jpg",
  "hashtags": ["innovation", "tech", "product"],
  "status": "pending_approval",
  "approval_deadline": "2026-02-06T10:30:00Z"
}
```

### Step 2: Review Draft

You review the draft post:
```
Show me pending social media posts
```

AI Employee displays:
```
📝 Pending Social Media Posts:

1. Post ID: social_post_20260205103000
   Platforms: Facebook, Instagram
   Text: "Check out our new product! 🚀"
   Image: https://example.com/product.jpg
   Hashtags: #innovation #tech #product
   Created: 2026-02-05 10:30:00
   Deadline: 2026-02-06 10:30:00 (23 hours remaining)
```

### Step 3: Approve or Reject

**Approve:**
```
Approve social media post social_post_20260205103000
```

**Reject:**
```
Reject social media post social_post_20260205103000 because [reason]
```

**Approve with changes:**
```
Approve social media post social_post_20260205103000 with changes:
- Update text to: "Excited to announce our new product! 🚀"
- Add hashtag: newproduct
```

### Step 4: Publish

After approval, AI Employee:
1. Publishes to all specified platforms
2. Saves post IDs for tracking
3. Schedules engagement metrics check for 24 hours later
4. Moves draft to Done/ folder
5. Logs action to Audit_Logs/

## Engagement Tracking

### Automatic Tracking

24 hours after posting, AI Employee automatically:
1. Retrieves engagement metrics from each platform
2. Calculates engagement rate
3. Saves metrics to `AI_Employee_Vault/Social_Media_Metrics/`
4. Includes metrics in next CEO Briefing

**Metrics file format:**
```json
{
  "post_id": "social_post_20260205103000",
  "published_at": "2026-02-05T10:35:00Z",
  "metrics_retrieved_at": "2026-02-06T10:35:00Z",
  "platforms": {
    "facebook": {
      "post_id": "123456789_987654321",
      "likes": 245,
      "comments": 18,
      "shares": 32,
      "reach": 5420,
      "impressions": 8230,
      "engagement": 295,
      "engagement_rate": 5.44
    },
    "instagram": {
      "media_id": "18123456789012345",
      "likes": 412,
      "comments": 28,
      "saves": 56,
      "reach": 6830,
      "impressions": 9120,
      "engagement": 496,
      "engagement_rate": 7.26
    }
  }
}
```

### Manual Metrics Check

```
Get engagement metrics for all posts from the past week
```

AI Employee retrieves and displays:
```
📊 Social Media Engagement (Past 7 Days):

Facebook:
- Total posts: 5
- Total reach: 28,450
- Total engagement: 1,234
- Avg engagement rate: 4.34%
- Top post: "Product launch announcement" (8.2% engagement)

Instagram:
- Total posts: 7
- Total reach: 35,620
- Total engagement: 2,156
- Avg engagement rate: 6.05%
- Top post: "Behind the scenes photo" (9.8% engagement)

Twitter:
- Total posts: 12
- Total impressions: 45,230
- Total engagement: 892
- Avg engagement rate: 1.97%
- Top tweet: "Q1 results announcement" (3.4% engagement)
```

## Integration with Other Features

### CEO Briefing Integration

Social media metrics automatically included in weekly CEO Briefing:
- Total posts per platform
- Engagement trends
- Top performing posts
- Recommendations for improvement

### Audit Logging

All social media actions logged:
- Post creation
- Approval/rejection
- Publishing
- Metrics retrieval
- Errors and retries

### Queue Integration

Failed posts automatically queued for retry:
- Exponential backoff
- 24-hour expiry
- Automatic alerts

### Ralph Wiggum Loop

Social media posting can be part of autonomous tasks:
```
Process this multi-step task autonomously:
1. Create 5 social media posts about our new feature
2. Save drafts to Pending_Approval folder
3. Wait for my approval (this will block the task)
4. After approval, publish posts to Facebook and Instagram
5. Track engagement metrics after 24 hours
```

## Examples

### Example 1: Product Launch Announcement

```
Create social media post for product launch:
- Platforms: Facebook, Instagram, Twitter
- Text: "🚀 Introducing our revolutionary new product! Transform your workflow with AI-powered automation. Learn more at example.com/product"
- Image: https://example.com/product-launch.jpg
- Hashtags: productlaunch, innovation, AI, automation, tech
- Require approval: yes
```

**Result:**
- Draft created in Pending_Approval/
- You review and approve
- Published to all 3 platforms
- Engagement tracked after 24 hours
- Metrics included in next CEO Briefing

### Example 2: Weekly Update

```
Post weekly update to Facebook and Instagram:
"Happy Friday! 🎉 This week we:
✅ Launched new feature
✅ Onboarded 50 new customers
✅ Hit $100K MRR milestone

Thank you to our amazing team and customers! 🙏

#startup #milestone #growth"

Image: https://example.com/team-celebration.jpg
```

**Result:**
- Validation passes (text within limits, image provided for Instagram)
- Published immediately (no approval required if configured)
- Engagement tracked automatically

### Example 3: Event Promotion

```
Create event promotion post:
- Platforms: Facebook, Instagram, Twitter
- Event: "AI Automation Webinar"
- Date: "February 15, 2026 at 2:00 PM EST"
- Registration: "https://example.com/webinar"
- Image: https://example.com/webinar-banner.jpg
- Hashtags: webinar, AI, automation, learning
```

**Result:**
- AI Employee generates optimized text for each platform:
  - Facebook: Full description with event details
  - Instagram: Engaging caption with hashtags
  - Twitter: Concise announcement with link
- Published to all platforms
- Engagement tracked

## Troubleshooting

### Post Not Publishing

**Problem:** Post validation passes but doesn't publish

**Solutions:**
1. Check MCP servers are running:
   ```bash
   curl http://localhost:3101/health  # Facebook
   curl http://localhost:3102/health  # Instagram
   curl http://localhost:3103/health  # Twitter
   ```
2. Verify access tokens are valid (check health endpoint response)
3. Check Queue/ folder for queued posts
4. Review Audit_Logs/ for error details

### Invalid Access Token

**Problem:** "Invalid token" error when posting

**Solutions:**
1. Refresh access tokens (they expire periodically)
2. Facebook/Instagram: Generate new Page Access Token from Facebook Developer Console
3. Twitter: Regenerate API keys from Twitter Developer Portal
4. Update .env file with new tokens
5. Restart MCP servers

### Rate Limit Reached

**Problem:** "Rate limit exceeded" error

**Solutions:**
1. Check current rate limit status:
   ```
   Get rate limit status for Twitter
   ```
2. Wait for rate limit window to reset
3. Queued posts will automatically retry
4. Adjust posting frequency in config/social_media_config.json

### Image Not Loading

**Problem:** Instagram post fails with "Image not accessible"

**Solutions:**
1. Verify image URL is publicly accessible (https://)
2. Check image format (JPG, PNG, GIF supported)
3. Ensure image size is within limits (max 8MB)
4. Test image URL in browser
5. Use image hosting service (Imgur, Cloudinary, etc.)

### Engagement Metrics Not Retrieved

**Problem:** Metrics show 0 for all fields

**Solutions:**
1. Wait 24 hours after posting (metrics need time to accumulate)
2. Verify post was actually published (check platform directly)
3. Check if post ID is correct
4. Review Audit_Logs/ for API errors
5. Manually retrieve metrics:
   ```
   Get engagement metrics for Facebook post [post_id]
   ```

## Best Practices

1. **Use Approval Workflow**: Always review posts before publishing to avoid mistakes
2. **Optimize Timing**: Post during optimal times for each platform (see config)
3. **Platform-Specific Content**: Tailor content for each platform's audience
4. **Visual Content**: Always include images for Instagram, recommended for Facebook/Twitter
5. **Hashtag Strategy**: Use 5-10 relevant hashtags for Instagram, 1-2 for Twitter
6. **Engagement**: Respond to comments and messages promptly
7. **Track Metrics**: Review engagement metrics weekly to optimize content strategy
8. **Error Monitoring**: Check Queue/ and Audit_Logs/ regularly for failed posts
9. **Token Refresh**: Refresh access tokens before they expire (every 60 days for Facebook)
10. **Content Calendar**: Plan posts in advance using the approval workflow

## API Reference

### SocialMediaService Methods

#### `validate_post(platforms, text, image_url=None, link_url=None, hashtags=None)`
Validate post content for specified platforms

**Returns:** Validation result with errors if any

#### `publish_post(platforms, text, image_url=None, link_url=None, hashtags=None)`
Publish post to multiple platforms

**Returns:** Publishing results with post IDs for each platform

#### `get_metrics(platform, post_id)`
Retrieve engagement metrics for a post

**Returns:** Engagement metrics (likes, comments, shares, reach, etc.)

### MCP Server Endpoints

#### Facebook MCP (http://localhost:3101)
- `GET /health` - Health check
- `POST /posts` - Create post
- `GET /posts/:post_id` - Get post details
- `GET /posts/:post_id/insights` - Get engagement metrics
- `DELETE /posts/:post_id` - Delete post

#### Instagram MCP (http://localhost:3102)
- `GET /health` - Health check
- `POST /media` - Create media container
- `POST /media/publish` - Publish media container
- `GET /media/:media_id` - Get media details
- `GET /media/:media_id/insights` - Get engagement metrics
- `DELETE /media/:media_id` - Delete media

#### Twitter MCP (http://localhost:3103)
- `GET /health` - Health check
- `POST /tweets` - Create tweet
- `GET /tweets/:tweet_id` - Get tweet details
- `GET /tweets/:tweet_id/metrics` - Get engagement metrics
- `DELETE /tweets/:tweet_id` - Delete tweet
- `GET /rate_limit_status` - Get rate limit status

## Related Skills

- `/generate-ceo-briefing` - Includes social media metrics in weekly report
- `/process-with-loop` - Automate multi-step social media campaigns
- `/record-odoo-transaction` - Track social media advertising expenses

## Support

For issues or questions:
- Check MCP server health: `curl http://localhost:310X/health`
- Review audit logs: `AI_Employee_Vault/Audit_Logs/`
- Check queued posts: `AI_Employee_Vault/Queue/`
- Review pending approvals: `AI_Employee_Vault/Pending_Approval/`
