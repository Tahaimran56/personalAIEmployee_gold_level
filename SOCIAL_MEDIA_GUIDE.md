# Social Media Posting Guide

Complete guide to posting to Facebook, Instagram, and Twitter using the AI Employee system.

---

## 🚀 Quick Start (5 Steps)

### Step 1: Get API Credentials

You need API credentials from each platform. This is a one-time setup.

#### Facebook & Instagram (30 minutes)

1. **Create Facebook Developer Account**
   - Go to https://developers.facebook.com/
   - Click "Get Started" and create account
   - Verify email and phone number

2. **Create Facebook App**
   - Click "Create App" → Select "Business"
   - App Name: "AI Employee Social Media"
   - Contact Email: your email
   - Click "Create App"

3. **Add Products**
   - In app dashboard, click "Add Products"
   - Add "Facebook Login"
   - Add "Instagram Graph API"

4. **Get Page Access Token**
   ```bash
   # Go to Graph API Explorer
   https://developers.facebook.com/tools/explorer/

   # Select your app
   # Click "Generate Access Token"
   # Select your Facebook Page
   # Grant permissions: pages_manage_posts, pages_read_engagement
   # Copy the SHORT-LIVED token

   # Convert to LONG-LIVED token (60 days):
   curl "https://graph.facebook.com/v19.0/oauth/access_token?grant_type=fb_exchange_token&client_id=YOUR_APP_ID&client_secret=YOUR_APP_SECRET&fb_exchange_token=SHORT_LIVED_TOKEN"
   ```

5. **Get IDs**
   ```bash
   # Get Facebook Page ID:
   curl "https://graph.facebook.com/v19.0/me/accounts?access_token=YOUR_LONG_LIVED_TOKEN"

   # Get Instagram Business Account ID:
   curl "https://graph.facebook.com/v19.0/YOUR_PAGE_ID?fields=instagram_business_account&access_token=YOUR_LONG_LIVED_TOKEN"
   ```

#### Twitter (20 minutes)

1. **Create Twitter Developer Account**
   - Go to https://developer.twitter.com/
   - Click "Sign up" (use your Twitter account)
   - Apply for "Elevated" access (required for posting)
   - Fill application:
     - Purpose: "Business automation for social media management"
     - Use case: "Automated posting to company Twitter account"
   - Wait for approval (1-2 days)

2. **Create Twitter App**
   - Go to Developer Portal → "Projects & Apps"
   - Click "Create App"
   - App Name: "AI Employee Bot"
   - Save API Key and API Secret

3. **Enable OAuth 1.0a**
   - Go to app settings → "User authentication settings"
   - Enable "OAuth 1.0a"
   - Permissions: "Read and Write"
   - Callback URL: http://localhost:3000/callback
   - Save settings

4. **Generate Tokens**
   - Go to "Keys and tokens" tab
   - Click "Generate" under "Access Token and Secret"
   - Save all 5 credentials:
     - API Key
     - API Secret
     - Access Token
     - Access Token Secret
     - Bearer Token

---

### Step 2: Configure Environment

Edit your `.env` file with the credentials:

```bash
# Facebook Integration
FACEBOOK_APP_ID=123456789012345
FACEBOOK_APP_SECRET=abc123def456ghi789jkl012mno345pq
FACEBOOK_PAGE_ID=987654321098765
FACEBOOK_PAGE_ACCESS_TOKEN=EAABsbCS1iHgBO7ZC8wZBZCqL... (long token)

# Instagram Integration
INSTAGRAM_BUSINESS_ACCOUNT_ID=17841405309211844

# Twitter Integration
TWITTER_API_KEY=abcdefghijklmnopqrstuvwxy
TWITTER_API_SECRET=1234567890abcdefghijklmnopqrstuvwxyz12345
TWITTER_ACCESS_TOKEN=1234567890-AbCdEfGhIjKlMnOpQrStUvWxYz
TWITTER_ACCESS_TOKEN_SECRET=AbCdEfGhIjKlMnOpQrStUvWxYz1234567890Ab
TWITTER_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAAA... (long token)

# MCP Server Configuration
FACEBOOK_MCP_PORT=3101
INSTAGRAM_MCP_PORT=3102
TWITTER_MCP_PORT=3103
MCP_API_KEY=your_random_secure_key_here
```

**Generate MCP_API_KEY:**
```bash
# On Windows PowerShell:
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | % {[char]$_})

# On Linux/Mac:
openssl rand -base64 32
```

---

### Step 3: Start MCP Servers

**On Windows:**
```bash
# Double-click this file:
start_social_media_servers.bat

# Or run from command line:
.\start_social_media_servers.bat
```

**On Linux/Mac:**
```bash
chmod +x start_social_media_servers.sh
./start_social_media_servers.sh
```

You should see 3 command windows open:
- Facebook MCP Server (port 3101)
- Instagram MCP Server (port 3102)
- Twitter MCP Server (port 3103)

**Verify servers are running:**
```bash
# Test Facebook MCP
curl http://localhost:3101/health

# Test Instagram MCP
curl http://localhost:3102/health

# Test Twitter MCP
curl http://localhost:3103/health
```

All should return: `{"status": "healthy"}`

---

### Step 4: Post to Social Media

#### Option A: Post to Facebook Only

```bash
python post_to_facebook.py
```

Or use in your code:
```python
from post_to_facebook import post_to_facebook

post_to_facebook(
    message="Your message here",
    link="https://your-link.com",
    image_url="https://your-image.jpg"
)
```

#### Option B: Post to Instagram Only

```bash
python post_to_instagram.py
```

Or use in your code:
```python
from post_to_instagram import post_to_instagram

post_to_instagram(
    caption="Your caption with #hashtags",
    image_url="https://your-image.jpg"  # REQUIRED
)
```

#### Option C: Post to Twitter Only

```bash
python post_to_twitter.py
```

Or use in your code:
```python
from post_to_twitter import post_to_twitter

post_to_twitter(
    text="Your tweet (max 280 chars)",
    image_url="https://your-image.jpg"  # Optional
)
```

#### Option D: Post to All Platforms (Recommended)

```bash
python post_to_all_platforms.py
```

Or use in your code:
```python
from post_to_all_platforms import post_to_all_platforms

post_to_all_platforms(
    message="Your message here",
    image_url="https://your-image.jpg",  # Required for Instagram
    link="https://your-link.com"  # Optional
)
```

---

### Step 5: Verify Posts

After posting, check your social media accounts:

**Facebook:**
- Go to https://www.facebook.com/YOUR_PAGE_NAME
- Check your latest post

**Instagram:**
- Go to https://www.instagram.com/YOUR_USERNAME
- Check your latest post

**Twitter:**
- Go to https://twitter.com/YOUR_USERNAME
- Check your latest tweet

---

## 📊 Engagement Metrics

Get engagement metrics after 24 hours:

```python
from AI_Employee_Vault.services.social_media_service import SocialMediaService

service = SocialMediaService()

# Get Facebook metrics
fb_metrics = service.get_metrics("facebook", post_id="123456789_987654321")
print(f"Likes: {fb_metrics['likes']}")
print(f"Comments: {fb_metrics['comments']}")
print(f"Shares: {fb_metrics['shares']}")
print(f"Reach: {fb_metrics['reach']}")

# Get Instagram metrics
ig_metrics = service.get_metrics("instagram", media_id="17895695668004551")
print(f"Likes: {ig_metrics['likes']}")
print(f"Comments: {ig_metrics['comments']}")
print(f"Saves: {ig_metrics['saves']}")
print(f"Reach: {ig_metrics['reach']}")

# Get Twitter metrics
tw_metrics = service.get_metrics("twitter", tweet_id="1234567890123456789")
print(f"Likes: {tw_metrics['likes']}")
print(f"Retweets: {tw_metrics['retweets']}")
print(f"Replies: {tw_metrics['replies']}")
print(f"Impressions: {tw_metrics['impressions']}")
```

---

## 🔧 Troubleshooting

### Issue: "Invalid access token"

**Solution:**
1. Your token may have expired (Facebook tokens expire after 60 days)
2. Regenerate a new long-lived token
3. Update `.env` with new token
4. Restart MCP servers

### Issue: "Rate limit exceeded"

**Solution:**
1. Wait for rate limit to reset (15 minutes for Twitter)
2. The system will automatically queue failed posts
3. Check `AI_Employee_Vault/Queue/` for queued operations
4. Posts will retry automatically with exponential backoff

### Issue: "Instagram requires image"

**Solution:**
1. Instagram REQUIRES an image for all posts
2. Provide `image_url` parameter
3. Image must be publicly accessible URL
4. Supported formats: JPG, PNG (max 8MB)

### Issue: "MCP server not responding"

**Solution:**
1. Check if servers are running (look for command windows)
2. Restart servers: `.\start_social_media_servers.bat`
3. Check ports are not in use: `netstat -ano | findstr "3101 3102 3103"`
4. Check `.env` file has correct credentials

### Issue: "Permission denied"

**Solution:**
1. Check your Facebook app has required permissions:
   - pages_manage_posts
   - pages_read_engagement
   - instagram_basic
   - instagram_content_publish
2. Go to App Review and request permissions if needed
3. Regenerate access token after permissions granted

---

## 📝 Best Practices

### Content Guidelines

**Facebook:**
- Optimal post length: 40-80 characters
- Best time to post: 1-4 PM weekdays
- Use images/videos for 2x engagement
- Include call-to-action

**Instagram:**
- Optimal caption length: 138-150 characters
- Best time to post: 11 AM - 1 PM weekdays
- Use 5-10 relevant hashtags
- High-quality images (1080x1080 or 1080x1350)

**Twitter:**
- Optimal tweet length: 71-100 characters
- Best time to post: 8-10 AM, 6-9 PM
- Use 1-2 hashtags maximum
- Include images for 150% more retweets

### Posting Schedule

**Recommended frequency:**
- Facebook: 1-2 posts per day
- Instagram: 1-2 posts per day
- Twitter: 3-5 tweets per day

**Avoid:**
- Posting same content too frequently
- Posting during off-hours (2-6 AM)
- Over-using hashtags (looks spammy)

---

## 🎯 Example Workflows

### Workflow 1: Product Launch

```python
from post_to_all_platforms import post_to_all_platforms

# Day 1: Teaser
post_to_all_platforms(
    message="Something exciting is coming... 🚀 Stay tuned! #comingsoon #newproduct",
    image_url="https://example.com/images/teaser.jpg"
)

# Day 2: Launch announcement
post_to_all_platforms(
    message="🎉 It's here! Introducing our new AI-powered automation tool. Check it out! #launch #AI #automation",
    image_url="https://example.com/images/product-launch.jpg",
    link="https://example.com/products/new-launch"
)

# Day 3: Customer testimonial
post_to_all_platforms(
    message="'This tool saved us 10 hours per week!' - Happy Customer. Try it today! #testimonial #success",
    image_url="https://example.com/images/testimonial.jpg",
    link="https://example.com/products/new-launch"
)
```

### Workflow 2: Weekly Updates

```python
from post_to_all_platforms import post_to_all_platforms
from datetime import datetime

# Monday: Week kickoff
post_to_all_platforms(
    message="Happy Monday! 💼 This week we're focusing on customer success. What are your goals? #mondaymotivation #business",
    image_url="https://example.com/images/monday.jpg"
)

# Wednesday: Mid-week tip
post_to_all_platforms(
    message="Mid-week tip: Automate repetitive tasks to save time. Here's how we do it: #productivity #automation",
    link="https://example.com/blog/automation-tips"
)

# Friday: Week wrap-up
post_to_all_platforms(
    message="That's a wrap! 🎉 This week we helped 50+ businesses automate their workflows. What did you accomplish? #fridayfeeling #success",
    image_url="https://example.com/images/friday.jpg"
)
```

---

## 🔐 Security Notes

**Protect your credentials:**
- Never commit `.env` to version control
- Rotate tokens every 30-60 days
- Use environment variables in production
- Limit API permissions to minimum required

**Token expiration:**
- Facebook: 60 days (long-lived tokens)
- Twitter: Never expires (unless revoked)
- Instagram: Uses Facebook token (60 days)

**Regenerate tokens before expiration:**
```bash
# Set reminder 7 days before expiration
# Regenerate tokens and update .env
# Restart MCP servers
```

---

## 📞 Support

**Issues with this guide:**
- Check `GOLD_TIER_COMPLETION.md` for test results
- Check `docs/gold-tier-troubleshooting.md` for common issues
- Check `AI_Employee_Vault/Logs/` for error logs

**Platform-specific help:**
- Facebook: https://developers.facebook.com/support/
- Instagram: https://developers.facebook.com/docs/instagram-api/
- Twitter: https://developer.twitter.com/en/support

---

## ✅ Checklist

Before posting, verify:
- [ ] API credentials configured in `.env`
- [ ] MCP servers running (3 command windows open)
- [ ] Health checks passing (all return "healthy")
- [ ] Content follows platform guidelines
- [ ] Images are publicly accessible URLs
- [ ] Twitter posts under 280 characters
- [ ] Instagram posts include image

---

**Status: Ready to Post!** 🚀

Use the posting scripts to start sharing your content across all platforms.
