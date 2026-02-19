# Gold Tier Setup Checklist

**Status**: Development Complete ✅ | Setup Required ⏳

**Goal**: Complete all 10 manual tests to achieve 100% Gold Tier completion

**Estimated Time**: 4-7 hours (mostly setup, testing is quick)

---

## 📋 Progress Tracker

- [ ] Phase 1: Install Odoo ERP (30-60 min)
- [ ] Phase 2: Set Up Facebook/Instagram (30-60 min)
- [ ] Phase 3: Set Up Twitter Developer Account (30-60 min)
- [ ] Phase 4: Configure Environment Variables (15 min)
- [ ] Phase 5: Configure Business Goals (5 min)
- [ ] Phase 6: Start MCP Servers (5 min)
- [ ] Phase 7: Run Health Check (2 min)
- [ ] Phase 8: Run Verification Script (5 min)
- [ ] Phase 9: Perform Manual Tests (2 hours)
- [ ] Phase 10: Final Verification & Celebration 🎉

---

## Phase 1: Install Odoo ERP (30-60 minutes)

**Purpose**: Set up accounting system for invoice/payment tracking and CEO briefing

### Option A: Docker Installation (Recommended - You Have Docker Desktop ✅)

- [ ] **Step 1.1**: Verify Docker Desktop is running
  - Open Docker Desktop application
  - Wait for "Docker Desktop is running" status in system tray
  - If not running, start it and wait 1-2 minutes

- [ ] **Step 1.2**: Open Command Prompt or PowerShell
  - Press `Win + R`
  - Type `cmd` or `powershell`
  - Press Enter

- [ ] **Step 1.3**: Check if old containers exist (cleanup)
  ```bash
  docker ps -a | findstr "odoo\|db"
  ```
  - If you see old containers, remove them:
  ```bash
  docker rm -f odoo db
  ```

- [ ] **Step 1.4**: Start PostgreSQL database container
  ```bash
  docker run -d -e POSTGRES_USER=odoo -e POSTGRES_PASSWORD=odoo -e POSTGRES_DB=postgres --name db postgres:15
  ```
  - **What this does**: Creates a PostgreSQL database for Odoo
  - **Expected output**: A long container ID (64 characters)
  - **If error "name already in use"**: Run `docker rm -f db` first

- [ ] **Step 1.5**: Verify PostgreSQL is running
  ```bash
  docker ps | findstr "db"
  ```
  - **Expected output**: Should show `postgres:15` with status "Up X seconds"
  - **If not running**: Check Docker Desktop → Containers tab

- [ ] **Step 1.6**: Start Odoo container
  ```bash
  docker run -d -p 8069:8069 --name odoo --link db:db -t odoo:19
  ```
  - **What this does**: Creates Odoo ERP container linked to database
  - **Expected output**: A long container ID (64 characters)
  - **If error "port already allocated"**: Another app is using port 8069
    - Check with: `netstat -ano | findstr :8069`
    - Kill the process or change Odoo port to 8070

- [ ] **Step 1.7**: Verify Odoo is running
  ```bash
  docker ps | findstr "odoo"
  ```
  - **Expected output**: Should show `odoo:19` with status "Up X seconds"
  - **Wait 2-3 minutes** for Odoo to fully start (first time takes longer)

- [ ] **Step 1.8**: Check Odoo logs (optional but recommended)
  ```bash
  docker logs odoo
  ```
  - **Look for**: "HTTP service (werkzeug) running on 0.0.0.0:8069"
  - **If errors**: See troubleshooting section at bottom

- [ ] **Step 1.9**: Open Odoo in browser
  - Open browser (Chrome, Edge, Firefox)
  - Go to: http://localhost:8069
  - **Expected**: Odoo database creation page
  - **If "This site can't be reached"**: Wait another minute and refresh

- [ ] **Step 1.10**: Create Odoo database
  - **Master Password**: `admin` (default, leave as-is)
  - **Database Name**: `gold_tier_accounting` (exactly this name)
  - **Email**: your@email.com (your actual email)
  - **Password**: Choose a strong password (save this!)
    - Example: `GoldTier2026!Secure`
    - Write it down immediately!
  - **Phone Number**: (optional, can skip)
  - **Language**: English
  - **Country**: Your country (select from dropdown)
  - **Demo data**: **UNCHECK THIS BOX** (important!)
  - Click "Create Database" button

- [ ] **Step 1.11**: Wait for database creation
  - **Time**: 2-5 minutes
  - **What you'll see**: Progress bar or loading spinner
  - **Don't close the browser!**

- [ ] **Step 1.12**: Complete Odoo setup wizard
  - **Company Name**: Your company name (e.g., "My Business")
  - **Industry**: Select closest match (e.g., "Services", "Consulting")
  - **Employees**: Select range (e.g., "1-5")
  - Click "Next" or "Skip" through remaining screens
  - You'll land on Odoo dashboard

- [ ] **Step 1.13**: Verify Odoo is working
  - You should see Odoo main dashboard
  - Top menu shows: Discuss, Calendar, Contacts, etc.
  - Click "Accounting" app icon (if visible)
  - If prompted to install, click "Install"

- [ ] **Step 1.14**: Save credentials in a text file
  - Open Notepad
  - Copy and paste this template:
  ```
  ODOO CREDENTIALS (Save this!)
  ================================
  ODOO_URL=http://localhost:8069
  ODOO_DATABASE=gold_tier_accounting
  ODOO_USERNAME=admin
  ODOO_PASSWORD=_____________ (paste your password here)

  Login URL: http://localhost:8069/web/login
  ```
  - Save as: `odoo_credentials.txt` on Desktop
  - **Keep this file safe!**

**Verification Checklist**:
- [ ] Can you access http://localhost:8069 in browser?
- [ ] Can you log in with admin and your password?
- [ ] Do you see the Odoo dashboard?
- [ ] Is the database name "gold_tier_accounting"?

**Troubleshooting**:
- **"This site can't be reached"**:
  - Check Docker Desktop → Containers → odoo is running
  - Wait 2 more minutes and refresh
  - Check logs: `docker logs odoo`
- **"Database creation failed"**:
  - Restart containers: `docker restart db odoo`
  - Try again after 2 minutes
- **"Port 8069 already in use"**:
  - Find process: `netstat -ano | findstr :8069`
  - Kill it or use different port

### Option B: Native Installation

- [ ] Follow detailed instructions in: `docs/api-credentials.md` (Section 1)

**Verification**: Can you log in to http://localhost:8069 with your credentials?

---

## Phase 2: Set Up Facebook/Instagram (30-60 minutes)

**Purpose**: Enable social media posting to Facebook Pages and Instagram Business accounts

**Prerequisites**:
- [ ] You have a Facebook account
- [ ] You have a Facebook Page (not personal profile)
- [ ] You have an Instagram Business account linked to that Page

**If you don't have these, create them first**:
- Facebook Page: https://www.facebook.com/pages/create
- Instagram Business: Open Instagram app → Settings → Account → Switch to Professional Account

---

### Step 2.1: Create Facebook Developer Account (5 minutes)

- [ ] **Step 2.1.1**: Open Facebook Developers
  - Go to: https://developers.facebook.com/
  - **Expected**: Facebook Developers homepage

- [ ] **Step 2.1.2**: Log in with your Facebook account
  - Click "Log In" (top right)
  - Enter your Facebook email and password
  - Complete 2FA if enabled

- [ ] **Step 2.1.3**: Register as a developer (first time only)
  - Click "Get Started" button (if you see it)
  - **If already registered**: Skip to Step 2.2
  - Accept Terms of Service
  - Click "Next"

- [ ] **Step 2.1.4**: Complete developer registration
  - **Display Name**: Your name or company name
  - **Contact Email**: Your email (verify this!)
  - Click "Submit"
  - **Check your email** for verification link
  - Click the verification link

- [ ] **Step 2.1.5**: Verify you're registered
  - Go back to: https://developers.facebook.com/
  - You should see "My Apps" in top menu
  - **If you see "My Apps"**: ✅ Registration complete!

---

### Step 2.2: Create Facebook App (10 minutes)

- [ ] **Step 2.2.1**: Navigate to My Apps
  - Click "My Apps" (top right corner)
  - **Expected**: List of your apps (may be empty)

- [ ] **Step 2.2.2**: Create new app
  - Click green "Create App" button
  - **Expected**: "Select an app type" dialog

- [ ] **Step 2.2.3**: Choose app type
  - Select "Business" (the middle option)
  - **Why Business?**: Allows posting to Pages
  - Click "Next" button

- [ ] **Step 2.2.4**: Fill in app details
  - **App Display Name**: `AI Employee Gold Tier`
    - This is what users see (not important for our use)
  - **App Contact Email**: Your email
    - Must be verified email
  - **Business Account**: (optional, can skip)
  - Click "Create App" button

- [ ] **Step 2.2.5**: Complete security check
  - **Expected**: CAPTCHA or security verification
  - Complete the verification
  - Click "Submit"

- [ ] **Step 2.2.6**: Wait for app creation
  - **Time**: 5-10 seconds
  - **Expected**: Redirects to App Dashboard
  - **You should see**: "AI Employee Gold Tier" at top

- [ ] **Step 2.2.7**: Note your App ID
  - Look at top of page: "App ID: 1234567890123456"
  - Copy this App ID
  - Save it in Notepad (you'll need it later)

---

### Step 2.3: Add Required Products (5 minutes)

- [ ] **Step 2.3.1**: Navigate to Add Products
  - In left sidebar, click "Add Products" (or scroll down on dashboard)
  - **Expected**: Grid of available products

- [ ] **Step 2.3.2**: Add Facebook Login
  - Find "Facebook Login" card
  - Click "Set Up" button on that card
  - **Expected**: Facebook Login added to left sidebar
  - **Don't configure it yet**, just add it

- [ ] **Step 2.3.3**: Add Instagram Graph API
  - Scroll down to find "Instagram Graph API" card
  - Click "Set Up" button
  - **Expected**: Instagram Graph API added to left sidebar

- [ ] **Step 2.3.4**: Verify products added
  - Check left sidebar
  - You should see:
    - Facebook Login
    - Instagram Graph API
  - **If you see both**: ✅ Products added!

---

### Step 2.4: Configure App Settings (5 minutes)

- [ ] **Step 2.4.1**: Go to App Settings
  - Left sidebar → Click "Settings" → "Basic"
  - **Expected**: Basic settings page

- [ ] **Step 2.4.2**: Scroll to "App Domains"
  - Find "App Domains" field (middle of page)
  - Enter: `localhost`
  - **Why?**: Allows testing on local machine

- [ ] **Step 2.4.3**: Add Platform
  - Scroll to bottom of page
  - Click "+ Add Platform" button
  - **Expected**: Platform selection dialog

- [ ] **Step 2.4.4**: Select Website platform
  - Click "Website" option
  - **Expected**: Website URL fields appear

- [ ] **Step 2.4.5**: Enter website URL
  - **Site URL**: `http://localhost:3000`
  - Leave other fields empty
  - Click "Save Changes" (bottom right)
  - **Expected**: "Changes saved" notification

---

### Step 2.5: Get Page Access Token (15 minutes - MOST IMPORTANT)

- [ ] **Step 2.5.1**: Open Graph API Explorer
  - Go to: https://developers.facebook.com/tools/explorer/
  - **Or**: Top menu → "Tools" → "Graph API Explorer"
  - **Expected**: Graph API Explorer interface

- [ ] **Step 2.5.2**: Select your app
  - Top right: "Meta App" dropdown
  - Select "AI Employee Gold Tier" (your app)
  - **Expected**: App name shows in dropdown

- [ ] **Step 2.5.3**: Select your Facebook Page
  - Next dropdown: "User or Page"
  - Click dropdown
  - **Expected**: List of your Pages
  - Select the Page you want to post to
  - **If no Pages shown**: You need to create a Facebook Page first

- [ ] **Step 2.5.4**: Add required permissions
  - Click "Permissions" tab (below dropdowns)
  - **Expected**: List of permissions with checkboxes
  - Search and check these permissions:
    - [ ] `pages_show_list`
    - [ ] `pages_read_engagement`
    - [ ] `pages_manage_posts`
    - [ ] `instagram_basic`
    - [ ] `instagram_content_publish`
  - **How to find**: Use search box at top of permissions list

- [ ] **Step 2.5.5**: Generate Access Token
  - Click "Generate Access Token" button (top right)
  - **Expected**: Permission request dialog
  - Click "Continue as [Your Name]"
  - **Expected**: Permission confirmation screens
  - Check all boxes and click "OK" for each permission
  - **Expected**: Returns to Graph API Explorer

- [ ] **Step 2.5.6**: Copy the short-lived token
  - Look for "Access Token" field (top of page)
  - **Expected**: Long string starting with "EAAA..."
  - Click the token to select all
  - Copy it (Ctrl+C)
  - **Paste in Notepad** - label it "SHORT-LIVED TOKEN"
  - **Important**: This token expires in 1 hour!

---

### Step 2.6: Extend Token to 60 Days (10 minutes - CRITICAL)

- [ ] **Step 2.6.1**: Open Access Token Debugger
  - Go to: https://developers.facebook.com/tools/debug/accesstoken/
  - **Or**: In Graph API Explorer, click "i" icon next to token
  - **Expected**: Access Token Debugger page

- [ ] **Step 2.6.2**: Paste your short-lived token
  - Paste the token you copied (the EAAA... string)
  - Click "Debug" button
  - **Expected**: Token information displayed

- [ ] **Step 2.6.3**: Verify token details
  - Check these fields:
    - **Type**: Should say "Page Access Token"
    - **App**: Should show "AI Employee Gold Tier"
    - **Expires**: Should show "in about an hour"
    - **Scopes**: Should list all permissions you added
  - **If Type is "User Token"**: You selected wrong option in Step 2.5.2

- [ ] **Step 2.6.4**: Extend the token
  - Scroll down to bottom of page
  - Click "Extend Access Token" button
  - **Expected**: New token appears in field above
  - **Expected**: "Expires" now shows "in about 2 months"

- [ ] **Step 2.6.5**: Copy the long-lived token
  - Select the new token (different from before!)
  - Copy it (Ctrl+C)
  - **Paste in Notepad** - label it "LONG-LIVED TOKEN (60 days)"
  - **This is your FACEBOOK_PAGE_ACCESS_TOKEN!**

- [ ] **Step 2.6.6**: Save this token securely
  - Open Notepad
  - Create new section:
  ```
  FACEBOOK CREDENTIALS (Save this!)
  ================================
  FACEBOOK_PAGE_ACCESS_TOKEN=EAAA... (paste long-lived token here)
  Token Expires: (today's date + 60 days)
  ```
  - Save file as: `facebook_credentials.txt` on Desktop

---

### Step 2.7: Get Facebook Page ID (5 minutes)

- [ ] **Step 2.7.1**: Go to your Facebook Page
  - Open Facebook: https://www.facebook.com/
  - Click "Pages" in left sidebar
  - Select your Page

- [ ] **Step 2.7.2**: Navigate to Page Transparency
  - On your Page, click "About" tab (left side)
  - Scroll down to "Transparency" section
  - Click "See all" or "Page transparency"

- [ ] **Step 2.7.3**: Find Page ID
  - Look for "Page ID" field
  - **Expected**: Number like "123456789012345"
  - Copy this number

- [ ] **Step 2.7.4**: Alternative method (if above doesn't work)
  - Go to Graph API Explorer: https://developers.facebook.com/tools/explorer/
  - Make sure your app is selected
  - In query field, enter: `me/accounts`
  - Click "Submit" button
  - **Expected**: JSON response with your Pages
  - Find your Page name in the response
  - Copy the "id" value next to it

- [ ] **Step 2.7.5**: Save Page ID
  - Add to your `facebook_credentials.txt`:
  ```
  FACEBOOK_PAGE_ID=123456789012345 (paste your Page ID here)
  ```

---

### Step 2.8: Link Instagram Business Account (10 minutes)

**Prerequisites**: You need an Instagram Business account

- [ ] **Step 2.8.1**: Check if you have Instagram Business account
  - Open Instagram app on phone
  - Go to your profile
  - Look at bio section
  - **If you see "Edit Profile" button only**: You have Personal account
  - **If you see category (e.g., "Entrepreneur")**: You have Business account ✅

- [ ] **Step 2.8.2**: Convert to Business account (if needed)
  - Tap menu (☰) → Settings
  - Tap "Account"
  - Tap "Switch to Professional Account"
  - Choose "Business"
  - Select category (e.g., "Entrepreneur", "Brand")
  - Tap "Done"

- [ ] **Step 2.8.3**: Link Instagram to Facebook Page
  - In Instagram app: Settings → Account
  - Tap "Linked Accounts"
  - Tap "Facebook"
  - Log in to Facebook if prompted
  - Select your Facebook Page
  - Tap "Link" or "Connect"
  - **Expected**: "Connected to [Page Name]"

- [ ] **Step 2.8.4**: Verify connection
  - Go back to Instagram profile
  - Tap "Edit Profile"
  - Scroll down to "Page"
  - **Expected**: Shows your Facebook Page name
  - **If not showing**: Repeat Step 2.8.3

---

### Step 2.9: Get Instagram Business Account ID (10 minutes)

- [ ] **Step 2.9.1**: Open Graph API Explorer
  - Go to: https://developers.facebook.com/tools/explorer/
  - Select your app: "AI Employee Gold Tier"
  - Select your Page (not User)

- [ ] **Step 2.9.2**: Query for accounts
  - In the query field (shows "me?" by default)
  - Clear it and type: `me/accounts`
  - Click "Submit" button
  - **Expected**: JSON response with your Pages

- [ ] **Step 2.9.3**: Find your Page in response
  - Look through the JSON response
  - Find the object with your Page name
  - Copy the "id" value (this is your Page ID)
  - Example:
  ```json
  {
    "name": "My Business Page",
    "id": "123456789012345"  ← Copy this
  }
  ```

- [ ] **Step 2.9.4**: Query for Instagram account
  - In query field, type: `123456789012345?fields=instagram_business_account`
    - Replace `123456789012345` with your actual Page ID
  - Click "Submit" button
  - **Expected**: JSON response with Instagram account

- [ ] **Step 2.9.5**: Copy Instagram Business Account ID
  - Look at the response:
  ```json
  {
    "instagram_business_account": {
      "id": "17841400123456789"  ← Copy this!
    },
    "id": "123456789012345"
  }
  ```
  - Copy the `instagram_business_account` → `id` value
  - **This is your INSTAGRAM_BUSINESS_ACCOUNT_ID!**

- [ ] **Step 2.9.6**: Troubleshooting if no Instagram account shown
  - **Error: "instagram_business_account field doesn't exist"**
    - Your Instagram is not linked to the Page
    - Go back to Step 2.8.3 and link it
  - **Error: Empty response**
    - Make sure you're querying the correct Page ID
    - Make sure you selected Page (not User) in Step 2.9.1

- [ ] **Step 2.9.7**: Save Instagram Account ID
  - Add to your `facebook_credentials.txt`:
  ```
  INSTAGRAM_BUSINESS_ACCOUNT_ID=17841400123456789 (paste your ID here)
  ```

---

### Step 2.10: Final Verification for Facebook/Instagram

- [ ] **Verify you have all 3 credentials**:
  ```
  ✓ FACEBOOK_PAGE_ACCESS_TOKEN=EAAA... (long string, 60-day token)
  ✓ FACEBOOK_PAGE_ID=123456789012345 (15-digit number)
  ✓ INSTAGRAM_BUSINESS_ACCOUNT_ID=17841400123456789 (17-digit number)
  ```

- [ ] **Test the token (optional but recommended)**:
  - Go to Graph API Explorer
  - Paste your long-lived token in "Access Token" field
  - Query: `me?fields=name,id`
  - Click "Submit"
  - **Expected**: Shows your Page name and ID
  - **If error**: Token may be invalid, regenerate it

**Troubleshooting**:
- **"Invalid OAuth access token"**: Token expired or wrong token
  - Regenerate token from Step 2.5
- **"Page not found"**: Wrong Page ID
  - Verify Page ID from Step 2.7
- **"Instagram account not found"**: Not linked properly
  - Relink Instagram from Step 2.8

**Detailed Guide**: See `docs/api-credentials.md` (Section 2)

**Verification**: Can you see your Page ID and Instagram Account ID?

---

## Phase 3: Set Up Twitter Developer Account (30-60 minutes)

**Purpose**: Enable posting tweets and tracking engagement

**Important**: Twitter requires **Elevated Access** for posting tweets. Basic access only allows reading.

---

### Step 3.1: Create Twitter Developer Account (10 minutes)

- [ ] **Step 3.1.1**: Go to Twitter Developer Portal
  - Open: https://developer.twitter.com/
  - **Expected**: Twitter Developer homepage

- [ ] **Step 3.1.2**: Sign in with your Twitter account
  - Click "Sign in" (top right)
  - Enter your Twitter username/email and password
  - Complete 2FA if enabled
  - **Expected**: Redirects to Developer Portal

- [ ] **Step 3.1.3**: Check if you already have developer access
  - Look for "Developer Portal" link in top menu
  - **If you see it**: You already have access, skip to Step 3.2
  - **If you don't see it**: Continue to next step

- [ ] **Step 3.1.4**: Apply for developer account
  - Click "Apply" or "Sign up" button
  - **Expected**: "How will you use the Twitter API?" page

- [ ] **Step 3.1.5**: Choose use case
  - Select "Hobbyist" (first option)
  - Then select "Exploring the API"
  - Click "Get started" button
  - **Expected**: Application form

- [ ] **Step 3.1.6**: Fill in basic information
  - **What country do you live in?**: Select your country
  - **What's your coding skill level?**: Select any (doesn't matter)
  - Click "Next"

- [ ] **Step 3.1.7**: Describe your use case (IMPORTANT)
  - **In your own words, describe how you plan to use Twitter data and/or APIs:**

  Copy and paste this (or write similar):
  ```
  I'm building an AI-powered business assistant that automates social media tasks.
  The application will:

  1. Post tweets on behalf of my business account to share updates, announcements,
     and engage with customers (using POST statuses/update endpoint)

  2. Retrieve engagement metrics (likes, retweets, replies, impressions) to track
     post performance and measure social media ROI (using GET statuses/show endpoint)

  3. Monitor rate limits to ensure compliance with Twitter API guidelines

  The app will NOT:
  - Make Twitter content available to any government entities
  - Analyze Twitter data for research purposes
  - Display Twitter content off Twitter
  - Use Twitter data for advertising

  This is for personal/business use only, posting to my own account.
  ```

- [ ] **Step 3.1.8**: Answer additional questions
  - **Will you make Twitter content available to a government entity?**: **No**
  - **Will you make Twitter content or derived information available to a government entity?**: **No**
  - Check the box: "I have read and agree to the Developer Agreement"
  - Click "Next"

- [ ] **Step 3.1.9**: Review and submit
  - Review your application
  - Click "Looks good!" button
  - **Expected**: Email verification screen

- [ ] **Step 3.1.10**: Verify your email
  - Check your email inbox
  - Look for email from Twitter Developer
  - Click "Confirm your email" button in email
  - **Expected**: "Email verified" confirmation

- [ ] **Step 3.1.11**: Wait for approval
  - **Time**: Usually instant to 2 hours (can take up to 24 hours)
  - **Expected**: Email saying "Your developer account application has been approved"
  - **While waiting**: You can continue to next step

---

### Step 3.2: Apply for Elevated Access (15 minutes - REQUIRED FOR POSTING)

**Why needed**: Basic access only allows reading tweets. Elevated access allows posting.

- [ ] **Step 3.2.1**: Go to Developer Portal
  - Open: https://developer.twitter.com/en/portal/dashboard
  - Sign in if needed
  - **Expected**: Developer Portal dashboard

- [ ] **Step 3.2.2**: Navigate to Products
  - Left sidebar → Click "Products"
  - **Or**: Look for "Elevated" section on dashboard
  - **Expected**: List of available products

- [ ] **Step 3.2.3**: Find Twitter API v2
  - Look for "Twitter API v2" card
  - You should see "Essential" (your current access level)
  - Click "Apply for Elevated" button
  - **Expected**: Elevated access application form

- [ ] **Step 3.2.4**: Fill in basic information
  - **First name**: Your first name
  - **Last name**: Your last name
  - **Country**: Your country
  - **Programming language**: Select "Python" or "JavaScript"
  - Click "Next"

- [ ] **Step 3.2.5**: Describe your use case (DETAILED)
  - **In English, please describe how you plan to use Twitter data and/or APIs. The more detailed the response, the easier it is to review and approve.**

  Copy and paste this (minimum 250 words required):
  ```
  I am developing an AI-powered business automation system called "Gold Tier AI Employee"
  that helps small businesses manage their social media presence efficiently. The system
  will use Twitter API v2 to automate social media posting and track engagement metrics.

  SPECIFIC USE CASES:

  1. AUTOMATED TWEET POSTING (POST /2/tweets)
     - Post business updates, product announcements, and promotional content
     - Schedule tweets for optimal engagement times
     - Post on behalf of my business Twitter account only
     - Frequency: 3-5 tweets per day maximum
     - All content is original, created by the AI assistant based on business data

  2. ENGAGEMENT METRICS TRACKING (GET /2/tweets/:id)
     - Retrieve likes, retweets, replies, and impression counts
     - Analyze which content performs best
     - Generate weekly reports on social media performance
     - Track ROI of social media marketing efforts

  3. RATE LIMIT MONITORING (GET /2/rate_limit_status)
     - Monitor API usage to stay within limits
     - Implement exponential backoff when approaching limits
     - Ensure compliance with Twitter API guidelines

  DATA HANDLING:
  - All data is stored locally on my machine
  - No data is shared with third parties
  - No government entities will have access
  - No Twitter content will be displayed outside of Twitter
  - No analysis of other users' tweets
  - Only posting to and analyzing my own business account

  TECHNICAL IMPLEMENTATION:
  - Using OAuth 1.0a for authentication
  - Implementing proper error handling and retry logic
  - Respecting rate limits and API guidelines
  - Local-first architecture with no cloud storage

  This is a personal project for my own business use, not a commercial product.
  ```

- [ ] **Step 3.2.6**: Answer specific questions
  - **Are you planning to analyze Twitter data?**: **No**
  - **Will your app use Tweet, Retweet, Like, Follow, or Direct Message functionality?**: **Yes**
    - Explain: "Yes, the app will post tweets (Tweet functionality) to share business updates."
  - **Do you plan to display Tweets or aggregate data about Twitter content outside Twitter?**: **No**
  - **Will your product, service, or analysis make Twitter content or derived information available to a government entity?**: **No**

- [ ] **Step 3.2.7**: Review and submit
  - Review all your answers
  - Check the box: "I have read and agree to the Developer Agreement and Policy"
  - Click "Submit" button
  - **Expected**: "Application submitted" confirmation

- [ ] **Step 3.2.8**: Wait for Elevated access approval
  - **Time**: Usually 1-2 hours (can take up to 48 hours)
  - **Expected**: Email saying "Your application for Elevated access has been approved"
  - **Check**: Developer Portal → Products → Should show "Elevated" instead of "Essential"
  - **Important**: Don't proceed until you have Elevated access!

---

### Step 3.3: Create Twitter App (10 minutes)

**Prerequisites**: Elevated access approved

- [ ] **Step 3.3.1**: Go to Developer Portal
  - Open: https://developer.twitter.com/en/portal/dashboard
  - **Expected**: Developer Portal dashboard

- [ ] **Step 3.3.2**: Navigate to Projects & Apps
  - Left sidebar → Click "Projects & Apps"
  - **Expected**: List of your projects (may be empty)

- [ ] **Step 3.3.3**: Create new app
  - Click "+ Create App" button (or "+ Add App" if you have a project)
  - **Expected**: "Create an App" dialog

- [ ] **Step 3.3.4**: Name your app
  - **App name**: `AI-Employee-Gold-Tier` (must be unique across all Twitter)
  - **If name taken**: Try `AI-Employee-Gold-Tier-YourName` or add numbers
  - Click "Next" or "Complete"
  - **Expected**: App created successfully

- [ ] **Step 3.3.5**: Save API Keys (IMPORTANT - SHOWN ONLY ONCE!)
  - **Expected**: Screen showing API Key and API Secret
  - **API Key**: Copy this (looks like: `abcdefghijklmnopqrstuvwxy`)
  - **API Secret**: Copy this (looks like: `1234567890abcdefghijklmnopqrstuvwxyz1234567890abcd`)
  - **CRITICAL**: These are shown ONLY ONCE! Save them now!
  - Open Notepad and paste:
  ```
  TWITTER CREDENTIALS (Save this!)
  ================================
  TWITTER_API_KEY=_____________ (paste API Key here)
  TWITTER_API_SECRET=_____________ (paste API Secret here)
  ```
  - Click "App Settings" button

- [ ] **Step 3.3.6**: Verify app created
  - You should see your app dashboard
  - Top shows: "AI-Employee-Gold-Tier"
  - **If you lost the keys**: Go to "Keys and tokens" tab → Regenerate

---

### Step 3.4: Configure OAuth 1.0a (10 minutes - REQUIRED FOR POSTING)

- [ ] **Step 3.4.1**: Navigate to app settings
  - In your app dashboard, click "Settings" tab (top menu)
  - **Expected**: App settings page

- [ ] **Step 3.4.2**: Scroll to User authentication settings
  - Scroll down to "User authentication settings" section
  - Click "Set up" button
  - **Expected**: User authentication settings form

- [ ] **Step 3.4.3**: Configure App permissions
  - **App permissions**: Select **"Read and Write"**
    - **Why**: Allows posting tweets (Write) and reading metrics (Read)
    - **Don't select "Read only"** - won't work!
  - **Type of App**: Select **"Web App, Automated App or Bot"**
  - **App info**: Fill in these fields:
    - **Callback URI / Redirect URL**: `http://localhost:3000/callback`
    - **Website URL**: `http://localhost:3000`
  - Click "Save" button

- [ ] **Step 3.4.4**: Verify OAuth 1.0a is enabled
  - You should see "OAuth 1.0a" section appear
  - Shows "Read and Write" permissions
  - **If not showing**: Go back and ensure you selected "Read and Write"

---

### Step 3.5: Generate Access Token and Secret (5 minutes)

- [ ] **Step 3.5.1**: Go to Keys and tokens tab
  - Click "Keys and tokens" tab (top menu)
  - **Expected**: Keys and tokens page

- [ ] **Step 3.5.2**: Regenerate API Keys (if needed)
  - **If you lost them from Step 3.3.5**:
    - Scroll to "API Key and Secret" section
    - Click "Regenerate" button
    - Copy and save the new keys
  - **If you have them**: Skip this step

- [ ] **Step 3.5.3**: Generate Access Token and Secret
  - Scroll to "Authentication Tokens" section
  - Find "Access Token and Secret"
  - Click "Generate" button
  - **Expected**: Confirmation dialog
  - Click "Yes, generate" or "Generate"

- [ ] **Step 3.5.4**: Save Access Token and Secret (SHOWN ONLY ONCE!)
  - **Expected**: Screen showing Access Token and Access Token Secret
  - **Access Token**: Copy this (looks like: `1234567890-abcdefghijklmnopqrstuvwxyz123456`)
  - **Access Token Secret**: Copy this (looks like: `abcdefghijklmnopqrstuvwxyz1234567890abcdefg`)
  - **CRITICAL**: These are shown ONLY ONCE! Save them now!
  - Add to your Notepad:
  ```
  TWITTER_ACCESS_TOKEN=_____________ (paste Access Token here)
  TWITTER_ACCESS_SECRET=_____________ (paste Access Token Secret here)
  ```

- [ ] **Step 3.5.5**: Verify token permissions
  - Look at "Access Token and Secret" section
  - Should show: "Created with Read and Write permissions"
  - **If shows "Read only"**:
    - You need to regenerate after changing permissions
    - Go back to Step 3.4.3 and ensure "Read and Write" is selected
    - Then regenerate tokens

---

### Step 3.6: Generate Bearer Token (5 minutes)

- [ ] **Step 3.6.1**: Still on Keys and tokens tab
  - Scroll to "Bearer Token" section
  - **Expected**: Bearer Token section (may already be generated)

- [ ] **Step 3.6.2**: Generate or reveal Bearer Token
  - **If "Generate" button**: Click it
  - **If "Regenerate" button**: Click "Reveal" first to see existing token
  - **Expected**: Bearer Token displayed

- [ ] **Step 3.6.3**: Copy Bearer Token
  - **Bearer Token**: Copy this (looks like: `AAAAAAAAAAAAAAAAAAAAAA...` very long)
  - Add to your Notepad:
  ```
  TWITTER_BEARER_TOKEN=_____________ (paste Bearer Token here)
  ```

---

### Step 3.7: Get Client ID (5 minutes)

- [ ] **Step 3.7.1**: Go to Settings tab
  - Click "Settings" tab (top menu)
  - Scroll to "User authentication settings"

- [ ] **Step 3.7.2**: Find Client ID
  - Look for "Client ID" field
  - **Expected**: String like `abcdefghijklmnopqrstuvwxyz123456`
  - Copy this Client ID

- [ ] **Step 3.7.3**: Save Client ID
  - Add to your Notepad:
  ```
  TWITTER_CLIENT_ID=_____________ (paste Client ID here)
  ```

---

### Step 3.8: Final Verification for Twitter

- [ ] **Verify you have all 6 credentials**:
  ```
  ✓ TWITTER_API_KEY=abcdefghijklmnopqrstuvwxy (25 characters)
  ✓ TWITTER_API_SECRET=1234567890abcdefghijklmnopqrstuvwxyz1234567890abcd (50 characters)
  ✓ TWITTER_ACCESS_TOKEN=1234567890-abcdefghijklmnopqrstuvwxyz123456 (50 characters with dash)
  ✓ TWITTER_ACCESS_SECRET=abcdefghijklmnopqrstuvwxyz1234567890abcdefg (45 characters)
  ✓ TWITTER_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAAA... (very long, 100+ characters)
  ✓ TWITTER_CLIENT_ID=abcdefghijklmnopqrstuvwxyz123456 (28 characters)
  ```

- [ ] **Save all credentials to file**:
  - Save your Notepad as: `twitter_credentials.txt` on Desktop
  - **Keep this file safe!**

- [ ] **Verify app permissions**:
  - Go to app Settings tab
  - Check "App permissions" shows: **"Read and Write"**
  - **If shows "Read only"**: You won't be able to post tweets!
    - Fix: Go back to Step 3.4.3

- [ ] **Verify Elevated access**:
  - Go to: https://developer.twitter.com/en/portal/products
  - Should show "Elevated" (not "Essential")
  - **If shows "Essential"**: Wait for approval or reapply

**Troubleshooting**:
- **"Read only" permissions**: Regenerate tokens after changing to "Read and Write"
- **"Could not authenticate you"**: API keys may be wrong, regenerate them
- **"403 Forbidden"**: You don't have Elevated access yet
- **Lost API keys**: Regenerate from Keys and tokens tab (old ones will stop working)

**Detailed Guide**: See `docs/api-credentials.md` (Section 3)

**Verification**: Do you have all 6 Twitter credentials saved?

---

## Phase 4: Configure Environment Variables (15 minutes)

**Purpose**: Set up all API credentials in one centralized .env file

**Prerequisites**: You have all credentials from Phases 1-3 saved

---

### Step 4.1: Navigate to Project Directory

- [ ] **Step 4.1.1**: Open Command Prompt or PowerShell
  - Press `Win + R`
  - Type `cmd` or `powershell`
  - Press Enter

- [ ] **Step 4.1.2**: Navigate to project folder
  ```bash
  cd C:\Users\Dell\Desktop\hackathon0
  ```
  - **Expected**: Prompt shows the project directory
  - **Verify**: Run `dir` and you should see folders like `AI_Employee_Vault`, `docs`, `scripts`

---

### Step 4.2: Create .env File from Template

- [ ] **Step 4.2.1**: Check if .env.example exists
  ```bash
  dir .env.example
  ```
  - **Expected**: Shows `.env.example` file
  - **If not found**: The file should exist in the repo

- [ ] **Step 4.2.2**: Copy template to .env
  ```bash
  copy .env.example .env
  ```
  - **Expected**: "1 file(s) copied."
  - **If error "file already exists"**: That's okay, it means .env already exists

- [ ] **Step 4.2.3**: Verify .env was created
  ```bash
  dir .env
  ```
  - **Expected**: Shows `.env` file
  - **File size**: Should be similar to .env.example

---

### Step 4.3: Open .env File for Editing

- [ ] **Step 4.3.1**: Open .env in Notepad
  ```bash
  notepad .env
  ```
  - **Expected**: Notepad opens with .env file
  - **You should see**: Template with placeholder values

- [ ] **Step 4.3.2**: Keep your credential files handy
  - Open these files you created earlier:
    - `odoo_credentials.txt`
    - `facebook_credentials.txt`
    - `twitter_credentials.txt`
  - You'll copy values from these files

---

### Step 4.4: Add Odoo Credentials

- [ ] **Step 4.4.1**: Find the Odoo section in .env
  - Look for lines starting with `ODOO_`
  - Should have 4 variables

- [ ] **Step 4.4.2**: Fill in Odoo values
  ```bash
  # Odoo Configuration
  ODOO_URL=http://localhost:8069
  ODOO_DATABASE=gold_tier_accounting
  ODOO_USERNAME=admin
  ODOO_PASSWORD=your_actual_password_here
  ```
  - Replace `your_actual_password_here` with your Odoo password
  - **Don't use quotes** around the values
  - **No spaces** around the `=` sign

- [ ] **Step 4.4.3**: Verify Odoo section
  - All 4 variables filled in
  - No placeholder text remaining
  - Password matches what you set in Phase 1

---

### Step 4.5: Add Facebook/Instagram Credentials

- [ ] **Step 4.5.1**: Find the Facebook section in .env
  - Look for lines starting with `FACEBOOK_` and `INSTAGRAM_`

- [ ] **Step 4.5.2**: Fill in Facebook/Instagram values
  ```bash
  # Facebook/Instagram Configuration
  FACEBOOK_PAGE_ACCESS_TOKEN=EAAA...your_long_lived_token_here
  FACEBOOK_PAGE_ID=123456789012345
  INSTAGRAM_BUSINESS_ACCOUNT_ID=17841400123456789
  ```
  - Copy token from `facebook_credentials.txt`
  - **Token should start with "EAAA"**
  - **Page ID is 15 digits**
  - **Instagram ID is 17 digits**

- [ ] **Step 4.5.3**: Verify Facebook section
  - Token is the long-lived one (60 days), not short-lived
  - Page ID matches your Facebook Page
  - Instagram ID matches your Instagram Business account
  - No quotes, no spaces around `=`

---

### Step 4.6: Add Twitter Credentials

- [ ] **Step 4.6.1**: Find the Twitter section in .env
  - Look for lines starting with `TWITTER_`
  - Should have 6 variables

- [ ] **Step 4.6.2**: Fill in Twitter values
  ```bash
  # Twitter Configuration
  TWITTER_API_KEY=your_api_key_here
  TWITTER_API_SECRET=your_api_secret_here
  TWITTER_ACCESS_TOKEN=1234567890-your_access_token_here
  TWITTER_ACCESS_SECRET=your_access_secret_here
  TWITTER_BEARER_TOKEN=AAAAAAAAAA...your_bearer_token_here
  TWITTER_CLIENT_ID=your_client_id_here
  ```
  - Copy all 6 values from `twitter_credentials.txt`
  - **Access Token has a dash** in the middle (e.g., `1234567890-abc...`)
  - **Bearer Token is very long** (100+ characters)

- [ ] **Step 4.6.3**: Verify Twitter section
  - All 6 variables filled in
  - No placeholder text
  - Access Token has the dash
  - Bearer Token starts with "AAAA"

---

### Step 4.7: Generate and Add MCP API Key

- [ ] **Step 4.7.1**: Generate a random 32-character key
  - **Option A - PowerShell** (recommended):
    - Open PowerShell
    - Run this command:
    ```powershell
    -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | % {[char]$_})
    ```
    - **Expected**: Random string like `aB3dE7fG9hJ2kL4mN6pQ8rS0tU1vW5xY`
    - Copy this string

  - **Option B - Online Generator**:
    - Go to: https://www.random.org/strings/
    - Set length: 32
    - Characters: Alphanumeric
    - Click "Get Strings"
    - Copy the generated string

- [ ] **Step 4.7.2**: Add MCP API Key to .env
  ```bash
  # MCP Server Configuration
  MCP_API_KEY=aB3dE7fG9hJ2kL4mN6pQ8rS0tU1vW5xY
  ```
  - Paste your generated 32-character string
  - **This key is for internal use** (securing MCP server endpoints)

---

### Step 4.8: Add Claude API Key (from Silver Tier)

- [ ] **Step 4.8.1**: Find your Claude API key
  - You should have this from Silver Tier setup
  - **If you don't have it**:
    - Go to: https://console.anthropic.com/
    - Sign in
    - Go to "API Keys"
    - Create new key or copy existing one

- [ ] **Step 4.8.2**: Add Claude API Key to .env
  ```bash
  # Claude API Configuration
  CLAUDE_API_KEY=sk-ant-api03-...your_claude_api_key_here
  ```
  - **Key starts with**: `sk-ant-api03-`
  - **Very long**: 100+ characters

---

### Step 4.9: Add Optional Configuration (if needed)

- [ ] **Step 4.9.1**: MCP Server URLs (usually default)
  ```bash
  # MCP Server URLs (optional - defaults shown)
  ODOO_MCP_URL=http://localhost:3100
  FACEBOOK_MCP_URL=http://localhost:3101
  INSTAGRAM_MCP_URL=http://localhost:3102
  TWITTER_MCP_URL=http://localhost:3103
  ```
  - **Only change if** you're using different ports
  - **Default ports work** for most setups

- [ ] **Step 4.9.2**: Email configuration (from Silver Tier)
  - If you have email service configured:
  ```bash
  # Email Configuration (from Silver Tier)
  GMAIL_CLIENT_ID=your_gmail_client_id
  GMAIL_CLIENT_SECRET=your_gmail_client_secret
  ```
  - **If you don't have these**: Leave commented out or empty

---

### Step 4.10: Save and Verify .env File

- [ ] **Step 4.10.1**: Save the .env file
  - In Notepad: File → Save (or Ctrl+S)
  - Close Notepad

- [ ] **Step 4.10.2**: Verify .env file exists and has content
  ```bash
  dir .env
  ```
  - **Expected**: Shows `.env` file
  - **File size**: Should be 1-2 KB (not 0 bytes)

- [ ] **Step 4.10.3**: Check file content (optional)
  ```bash
  type .env | findstr "ODOO_URL FACEBOOK_PAGE_ACCESS_TOKEN TWITTER_API_KEY"
  ```
  - **Expected**: Shows your actual values (not placeholders)
  - **If shows placeholders**: You didn't save the file

- [ ] **Step 4.10.4**: Verify no placeholder text remains
  - Open .env again: `notepad .env`
  - Search (Ctrl+F) for:
    - `your_` (should find nothing)
    - `placeholder` (should find nothing)
    - `CHANGEME` (should find nothing)
  - **If found**: Replace with actual values

---

### Step 4.11: Secure Your .env File

- [ ] **Step 4.11.1**: Verify .env is in .gitignore
  ```bash
  findstr ".env" .gitignore
  ```
  - **Expected**: Shows `.env` in .gitignore
  - **Why important**: Prevents committing secrets to git

- [ ] **Step 4.11.2**: Check git status
  ```bash
  git status
  ```
  - **Expected**: Should NOT show `.env` in "Changes to be committed"
  - **If it shows .env**: Run `git reset .env` to unstage it

- [ ] **Step 4.11.3**: Create backup (optional but recommended)
  ```bash
  copy .env .env.backup
  ```
  - **Why**: In case you accidentally delete .env
  - **Keep backup safe** and don't commit it to git

---

### Step 4.12: Final Verification Checklist

- [ ] **All required variables filled in**:
  - [ ] ODOO_URL, ODOO_DATABASE, ODOO_USERNAME, ODOO_PASSWORD
  - [ ] FACEBOOK_PAGE_ACCESS_TOKEN, FACEBOOK_PAGE_ID
  - [ ] INSTAGRAM_BUSINESS_ACCOUNT_ID
  - [ ] TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET, TWITTER_BEARER_TOKEN, TWITTER_CLIENT_ID
  - [ ] MCP_API_KEY
  - [ ] CLAUDE_API_KEY

- [ ] **No placeholder text** (no "your_", "placeholder", "CHANGEME")

- [ ] **Correct formats**:
  - [ ] Odoo URL starts with `http://`
  - [ ] Facebook token starts with `EAAA`
  - [ ] Twitter Bearer Token starts with `AAAA`
  - [ ] Claude API key starts with `sk-ant-api03-`

- [ ] **File is saved** (not 0 bytes)

- [ ] **File is secure** (in .gitignore, not staged in git)

**Troubleshooting**:
- **"File not found"**: Make sure you're in the project directory
- **"Access denied"**: Close any programs that might have .env open
- **"Syntax error" later**: Check for spaces around `=` signs (should be none)
- **Values not loading**: Check for quotes around values (should be none)

---

## Phase 5: Configure Business Goals (5 minutes)

**Purpose**: Set up your actual business targets for CEO briefing generation

**Why needed**: The CEO Briefing service uses these targets to calculate progress and provide insights

---

### Step 5.1: Locate Business Goals File

- [ ] **Step 5.1.1**: Navigate to AI_Employee_Vault folder
  ```bash
  cd C:\Users\Dell\Desktop\hackathon0\AI_Employee_Vault
  ```

- [ ] **Step 5.1.2**: Check if Business_Goals.md exists
  ```bash
  dir Business_Goals.md
  ```
  - **Expected**: Shows `Business_Goals.md` file
  - **If not found**: File should exist from Phase 1 setup

---

### Step 5.2: Open Business Goals File

- [ ] **Step 5.2.1**: Open in Notepad
  ```bash
  notepad Business_Goals.md
  ```
  - **Expected**: Notepad opens with template content
  - **You should see**: Placeholder values like "$10,000", "Subscription Name"

---

### Step 5.3: Update Revenue Targets

- [ ] **Step 5.3.1**: Find the Revenue Targets section
  - Look for `## Revenue Targets` heading

- [ ] **Step 5.3.2**: Replace with your actual targets
  ```markdown
  ## Revenue Targets
  - Monthly Revenue Target: $50,000
  - Quarterly Revenue Target: $150,000
  - Annual Revenue Target: $600,000
  ```
  - **Customize these numbers** to match your business
  - **Use realistic targets** for meaningful insights
  - **Format**: Keep the `$` sign and commas

- [ ] **Step 5.3.3**: Example for different business sizes
  - **Small business**: Monthly $5,000, Quarterly $15,000, Annual $60,000
  - **Medium business**: Monthly $50,000, Quarterly $150,000, Annual $600,000
  - **Large business**: Monthly $500,000, Quarterly $1,500,000, Annual $6,000,000

---

### Step 5.4: Update Active Subscriptions

- [ ] **Step 5.4.1**: Find the Active Subscriptions section
  - Look for `## Active Subscriptions` heading

- [ ] **Step 5.4.2**: List your actual subscriptions
  ```markdown
  ## Active Subscriptions
  - GitHub Enterprise: $210/month
  - AWS: $500/month
  - Slack Business: $12.50/month
  - Zoom Pro: $15/month
  - Microsoft 365: $20/month
  - Adobe Creative Cloud: $54.99/month
  - Total Monthly: $812.49
  ```
  - **Add your real subscriptions** (software, services, tools)
  - **Include monthly cost** for each
  - **Calculate total** at the bottom
  - **Why important**: CEO Briefing detects unused subscriptions

- [ ] **Step 5.4.3**: Common subscriptions to include
  - Cloud services (AWS, Azure, Google Cloud)
  - Software tools (GitHub, Jira, Confluence)
  - Communication (Slack, Zoom, Microsoft Teams)
  - Design tools (Adobe, Figma, Canva)
  - Marketing (Mailchimp, HubSpot, Google Ads)
  - Analytics (Google Analytics, Mixpanel)

---

### Step 5.5: Add Key Metrics (Optional but Recommended)

- [ ] **Step 5.5.1**: Add Key Metrics section (if not present)
  ```markdown
  ## Key Metrics
  - Target Profit Margin: 40%
  - Customer Acquisition Cost: $500
  - Customer Lifetime Value: $5,000
  - Monthly Recurring Revenue (MRR): $25,000
  - Churn Rate Target: <5%
  ```
  - **Customize to your business model**
  - **These help CEO Briefing** provide better insights

---

### Step 5.6: Add Business Context (Optional)

- [ ] **Step 5.6.1**: Add Business Context section
  ```markdown
  ## Business Context
  - Industry: Software Development / Consulting
  - Business Model: B2B SaaS
  - Team Size: 5 employees
  - Founded: 2024
  - Primary Market: United States
  ```
  - **Helps AI understand** your business better
  - **Provides context** for suggestions

---

### Step 5.7: Save and Verify

- [ ] **Step 5.7.1**: Save the file
  - In Notepad: File → Save (or Ctrl+S)
  - Close Notepad

- [ ] **Step 5.7.2**: Verify file was saved
  ```bash
  type Business_Goals.md
  ```
  - **Expected**: Shows your updated content
  - **Check**: No placeholder values remain

- [ ] **Step 5.7.3**: Verify file size increased
  ```bash
  dir Business_Goals.md
  ```
  - **Expected**: File size > 0 bytes
  - **If 0 bytes**: File wasn't saved properly

---

### Step 5.8: Example Complete Business_Goals.md

Here's a complete example for reference:

```markdown
# Business Goals

## Revenue Targets
- Monthly Revenue Target: $50,000
- Quarterly Revenue Target: $150,000
- Annual Revenue Target: $600,000

## Active Subscriptions
- GitHub Enterprise: $210/month
- AWS: $500/month
- Slack Business: $12.50/month
- Zoom Pro: $15/month
- Microsoft 365: $20/month
- Adobe Creative Cloud: $54.99/month
- Mailchimp: $299/month
- Total Monthly: $1,111.49

## Key Metrics
- Target Profit Margin: 40%
- Customer Acquisition Cost: $500
- Customer Lifetime Value: $5,000
- Monthly Recurring Revenue (MRR): $25,000
- Churn Rate Target: <5%
- Average Deal Size: $10,000

## Business Context
- Industry: Software Development
- Business Model: B2B SaaS
- Team Size: 5 employees
- Founded: 2024
- Primary Market: United States
- Target Customers: Small to medium businesses

## Notes
- Review and update these goals quarterly
- CEO Briefing will track progress against these targets
- Unused subscriptions will be flagged for potential savings
```

---

### Step 5.9: Final Verification

- [ ] **All sections updated**:
  - [ ] Revenue Targets (realistic numbers)
  - [ ] Active Subscriptions (actual subscriptions with costs)
  - [ ] Total Monthly calculated correctly
  - [ ] Optional: Key Metrics added
  - [ ] Optional: Business Context added

- [ ] **No placeholder text** (no "Subscription Name", "$10,000" defaults)

- [ ] **File saved** and readable

**Verification**: Does Business_Goals.md reflect your actual business targets?

---

## Phase 6: Start MCP Servers (5 minutes)

**Purpose**: Start all 4 MCP servers that handle external API integrations

**What are MCP Servers?**: Model Context Protocol servers that act as bridges between the AI Employee and external services (Odoo, Facebook, Instagram, Twitter)

**Prerequisites**:
- Node.js installed
- .env file configured with all credentials
- All 4 terminals/command prompts ready

---

### Step 6.1: Prepare Terminal Windows

- [ ] **Step 6.1.1**: Open 4 separate Command Prompt windows
  - **Method 1**: Press `Win + R`, type `cmd`, press Enter (repeat 4 times)
  - **Method 2**: Right-click Start → "Command Prompt" (repeat 4 times)
  - **Method 3**: Use Windows Terminal with 4 tabs

- [ ] **Step 6.1.2**: Arrange windows for visibility
  - Arrange all 4 windows so you can see them simultaneously
  - **Tip**: Use Windows Snap (Win + Arrow keys)
  - **Why**: You need to monitor all servers for errors

- [ ] **Step 6.1.3**: Label your windows mentally
  - Terminal 1: Odoo MCP Server (port 3100)
  - Terminal 2: Facebook MCP Server (port 3101)
  - Terminal 3: Instagram MCP Server (port 3102)
  - Terminal 4: Twitter MCP Server (port 3103)

---

### Step 6.2: Start Odoo MCP Server (Terminal 1)

- [ ] **Step 6.2.1**: Navigate to MCP directory
  ```bash
  cd C:\Users\Dell\Desktop\hackathon0\AI_Employee_Vault\mcp
  ```
  - **Expected**: Prompt shows the mcp directory

- [ ] **Step 6.2.2**: Verify Node.js is installed
  ```bash
  node --version
  ```
  - **Expected**: Shows version like `v16.14.0` or higher
  - **If error**: Install Node.js from https://nodejs.org/

- [ ] **Step 6.2.3**: Check if dependencies are installed
  ```bash
  dir node_modules
  ```
  - **Expected**: Shows node_modules folder
  - **If not found**: Run `npm install` first

- [ ] **Step 6.2.4**: Start Odoo MCP Server
  ```bash
  node odoo-server.js
  ```
  - **Expected output** (within 2-3 seconds):
  ```
  🚀 Odoo MCP Server running on port 3100
  ✓ Configuration validated
  ✓ Performance monitoring enabled
  ✓ Error tracking enabled
  ✓ Graceful shutdown configured
  ```

- [ ] **Step 6.2.5**: Verify server is running
  - Look for "running on port 3100" message
  - **No errors** should appear
  - **Cursor should be blinking** (server is running)
  - **Don't close this window!**

- [ ] **Step 6.2.6**: Troubleshoot if errors occur
  - **Error: "Cannot find module"**:
    - Run `npm install` in the mcp directory
    - Then try starting again
  - **Error: "Port 3100 already in use"**:
    - Another process is using port 3100
    - Find it: `netstat -ano | findstr :3100`
    - Kill it or change port in config
  - **Error: "ODOO_URL is not defined"**:
    - .env file not loaded properly
    - Check .env file exists in project root
    - Verify ODOO_URL is set

---

### Step 6.3: Start Facebook MCP Server (Terminal 2)

- [ ] **Step 6.3.1**: In Terminal 2, navigate to MCP directory
  ```bash
  cd C:\Users\Dell\Desktop\hackathon0\AI_Employee_Vault\mcp
  ```

- [ ] **Step 6.3.2**: Start Facebook MCP Server
  ```bash
  node facebook-server.js
  ```
  - **Expected output**:
  ```
  🚀 Facebook MCP Server running on port 3101
  ✓ Configuration validated
  ✓ Performance monitoring enabled
  ✓ Error tracking enabled
  ✓ Graceful shutdown configured
  ```

- [ ] **Step 6.3.3**: Verify server is running
  - Look for "running on port 3101" message
  - No errors should appear
  - **Don't close this window!**

- [ ] **Step 6.3.4**: Troubleshoot if errors occur
  - **Error: "FACEBOOK_PAGE_ACCESS_TOKEN is not defined"**:
    - Check .env file has FACEBOOK_PAGE_ACCESS_TOKEN
    - Verify token is the long-lived one (60 days)
  - **Error: "Invalid OAuth access token"**:
    - Token may have expired
    - Regenerate token from Phase 2
  - **Error: "Port 3101 already in use"**:
    - Change port or kill existing process

---

### Step 6.4: Start Instagram MCP Server (Terminal 3)

- [ ] **Step 6.4.1**: In Terminal 3, navigate to MCP directory
  ```bash
  cd C:\Users\Dell\Desktop\hackathon0\AI_Employee_Vault\mcp
  ```

- [ ] **Step 6.4.2**: Start Instagram MCP Server
  ```bash
  node instagram-server.js
  ```
  - **Expected output**:
  ```
  🚀 Instagram MCP Server running on port 3102
  ✓ Configuration validated
  ✓ Performance monitoring enabled
  ✓ Error tracking enabled
  ✓ Graceful shutdown configured
  ```

- [ ] **Step 6.4.3**: Verify server is running
  - Look for "running on port 3102" message
  - No errors should appear
  - **Don't close this window!**

- [ ] **Step 6.4.4**: Troubleshoot if errors occur
  - **Error: "INSTAGRAM_BUSINESS_ACCOUNT_ID is not defined"**:
    - Check .env file has INSTAGRAM_BUSINESS_ACCOUNT_ID
    - Verify it's the 17-digit Instagram Business Account ID
  - **Error: "Instagram account not found"**:
    - Instagram may not be linked to Facebook Page
    - Go back to Phase 2, Step 2.8

---

### Step 6.5: Start Twitter MCP Server (Terminal 4)

- [ ] **Step 6.5.1**: In Terminal 4, navigate to MCP directory
  ```bash
  cd C:\Users\Dell\Desktop\hackathon0\AI_Employee_Vault\mcp
  ```

- [ ] **Step 6.5.2**: Start Twitter MCP Server
  ```bash
  node twitter-server.js
  ```
  - **Expected output**:
  ```
  🚀 Twitter MCP Server running on port 3103
  ✓ Configuration validated
  ✓ Performance monitoring enabled
  ✓ Error tracking enabled
  ✓ Graceful shutdown configured
  ```

- [ ] **Step 6.5.3**: Verify server is running
  - Look for "running on port 3103" message
  - No errors should appear
  - **Don't close this window!**

- [ ] **Step 6.5.4**: Troubleshoot if errors occur
  - **Error: "TWITTER_API_KEY is not defined"**:
    - Check .env file has all 6 Twitter credentials
    - Verify no typos in variable names
  - **Error: "Could not authenticate you"**:
    - API keys may be wrong
    - Regenerate from Twitter Developer Portal
  - **Error: "403 Forbidden"**:
    - You don't have Elevated access
    - Go back to Phase 3, Step 3.2

---

### Step 6.6: Verify All Servers Are Running

- [ ] **Step 6.6.1**: Check all 4 terminal windows
  - [ ] Terminal 1: Odoo server running (port 3100)
  - [ ] Terminal 2: Facebook server running (port 3101)
  - [ ] Terminal 3: Instagram server running (port 3102)
  - [ ] Terminal 4: Twitter server running (port 3103)

- [ ] **Step 6.6.2**: Verify no error messages
  - All 4 windows should show "✓ Configuration validated"
  - No red error text
  - Cursors blinking (servers waiting for requests)

- [ ] **Step 6.6.3**: Test server connectivity (optional)
  - Open new terminal (Terminal 5)
  - Test Odoo server:
  ```bash
  curl http://localhost:3100/health
  ```
  - **Expected**: `{"status":"healthy"}`
  - Repeat for other servers (ports 3101, 3102, 3103)

---

### Step 6.7: Keep Servers Running

- [ ] **Step 6.7.1**: Minimize (don't close) all 4 terminal windows
  - Click minimize button (not X)
  - **Why**: Servers must stay running during testing

- [ ] **Step 6.7.2**: Note: Servers will run until you close them
  - To stop a server: Press `Ctrl+C` in its terminal
  - To stop all: Close all 4 terminal windows
  - **For now**: Keep them running!

---

### Step 6.8: What to Do If a Server Crashes

- [ ] **If a server stops unexpectedly**:
  1. Check the terminal for error message
  2. Note the error (copy it)
  3. Restart the server (run `node [server-name].js` again)
  4. If error persists, see troubleshooting section below

---

### Troubleshooting Common Issues

**All servers fail to start**:
- Check if .env file exists in project root
- Verify .env has all required variables
- Run `npm install` in mcp directory

**"Cannot find module 'express'"**:
- Dependencies not installed
- Run: `cd AI_Employee_Vault\mcp && npm install`

**"Port already in use"**:
- Find process using port: `netstat -ano | findstr :310X`
- Kill process: `taskkill /PID [process_id] /F`
- Or change port in server config

**"Configuration validation failed"**:
- Missing or invalid credentials in .env
- Check specific error message for which credential
- Verify credential format (no quotes, no spaces)

**Server starts but crashes immediately**:
- Check for syntax errors in .env file
- Verify all credentials are valid (not expired)
- Check server logs for specific error

**Verification**: Are all 4 servers running without errors?

---

## Phase 7: Run Health Check (2 minutes)

**Purpose**: Verify all systems are operational before testing

**What it checks**: Python/Node.js versions, MCP servers, vault directories, config files, stop hook, environment variables

---

### Step 7.1: Open New Terminal Window

- [ ] **Step 7.1.1**: Open a 5th terminal window
  - Press `Win + R`, type `cmd`, press Enter
  - **Why new terminal**: The other 4 are running MCP servers

- [ ] **Step 7.1.2**: Navigate to project root
  ```bash
  cd C:\Users\Dell\Desktop\hackathon0
  ```
  - **Expected**: Prompt shows project directory
  - **Verify**: Run `dir` and see `scripts` folder

---

### Step 7.2: Verify Python is Installed

- [ ] **Step 7.2.1**: Check Python version
  ```bash
  python --version
  ```
  - **Expected**: `Python 3.9.0` or higher
  - **If error "python not found"**:
    - Try: `python3 --version`
    - If still not found: Install Python from https://www.python.org/

- [ ] **Step 7.2.2**: Verify pip is installed
  ```bash
  pip --version
  ```
  - **Expected**: Shows pip version
  - **If error**: Reinstall Python with pip included

---

### Step 7.3: Install Python Dependencies (if not done)

- [ ] **Step 7.3.1**: Check if requirements.txt exists
  ```bash
  dir requirements.txt
  ```
  - **Expected**: Shows requirements.txt file

- [ ] **Step 7.3.2**: Install dependencies
  ```bash
  pip install -r requirements.txt
  ```
  - **Expected**: Installs packages (may take 1-2 minutes)
  - **If already installed**: Shows "Requirement already satisfied"
  - **If errors**: Note the error and see troubleshooting

---

### Step 7.4: Run Health Check Script

- [ ] **Step 7.4.1**: Navigate to scripts directory
  ```bash
  cd scripts
  ```

- [ ] **Step 7.4.2**: Run health check
  ```bash
  python health_check.py
  ```
  - **Expected**: Script runs and shows checks
  - **Time**: Takes 5-10 seconds

---

### Step 7.5: Interpret Health Check Results

**Expected Output** (all checks should pass):

```
🏥 Gold Tier AI Employee - Health Check
========================================

System Requirements:
✓ Python version: 3.9.7 (minimum 3.9.0 required)
✓ Node.js version: 16.14.0 (minimum 16.0.0 required)

MCP Servers:
✓ Odoo MCP Server: healthy (http://localhost:3100)
✓ Facebook MCP Server: healthy (http://localhost:3101)
✓ Instagram MCP Server: healthy (http://localhost:3102)
✓ Twitter MCP Server: healthy (http://localhost:3103)

Vault Directories:
✓ AI_Employee_Vault: exists
✓ CEO_Briefings: exists
✓ Pending_Approval: exists
✓ Approved: exists
✓ In_Progress: exists
✓ Done: exists
✓ Logs: exists

Configuration Files:
✓ .env: exists and readable
✓ Business_Goals.md: exists and readable

Stop Hook:
✓ Stop hook configured: hooks/stop_hook.bat

Environment Variables:
✓ ODOO_URL: set
✓ ODOO_DATABASE: set
✓ ODOO_USERNAME: set
✓ ODOO_PASSWORD: set
✓ FACEBOOK_PAGE_ACCESS_TOKEN: set
✓ FACEBOOK_PAGE_ID: set
✓ INSTAGRAM_BUSINESS_ACCOUNT_ID: set
✓ TWITTER_API_KEY: set
✓ TWITTER_API_SECRET: set
✓ TWITTER_ACCESS_TOKEN: set
✓ TWITTER_ACCESS_SECRET: set
✓ TWITTER_BEARER_TOKEN: set
✓ TWITTER_CLIENT_ID: set
✓ MCP_API_KEY: set
✓ CLAUDE_API_KEY: set

========================================
All systems operational! ✅
Ready for Gold Tier testing.
```

---

### Step 7.6: Verify Each Section

- [ ] **Step 7.6.1**: Check System Requirements section
  - [ ] Python version ≥ 3.9.0 ✓
  - [ ] Node.js version ≥ 16.0.0 ✓
  - **If ✗**: Upgrade Python or Node.js

- [ ] **Step 7.6.2**: Check MCP Servers section
  - [ ] All 4 servers show "healthy" ✓
  - **If ✗**: Server not running or crashed
    - Go back to Phase 6 and restart the server
    - Check terminal for error messages

- [ ] **Step 7.6.3**: Check Vault Directories section
  - [ ] All 7 directories exist ✓
  - **If ✗**: Directory missing
    - Create manually: `mkdir AI_Employee_Vault\[directory_name]`

- [ ] **Step 7.6.4**: Check Configuration Files section
  - [ ] .env exists and readable ✓
  - [ ] Business_Goals.md exists and readable ✓
  - **If ✗**: File missing or unreadable
    - Go back to Phase 4 or 5 and recreate

- [ ] **Step 7.6.5**: Check Stop Hook section
  - [ ] Stop hook configured ✓
  - **If ✗**: Stop hook missing
    - Check `AI_Employee_Vault\hooks\stop_hook.bat` exists

- [ ] **Step 7.6.6**: Check Environment Variables section
  - [ ] All 15 variables show "set" ✓
  - **If ✗**: Variable not set
    - Go back to Phase 4 and add missing variable to .env

---

### Step 7.7: Troubleshoot Failed Checks

**If Python version check fails**:
- [ ] Upgrade Python to 3.9 or higher
- [ ] Download from: https://www.python.org/downloads/
- [ ] During install, check "Add Python to PATH"

**If Node.js version check fails**:
- [ ] Upgrade Node.js to 16 or higher
- [ ] Download from: https://nodejs.org/
- [ ] Restart terminal after install

**If MCP Server check fails**:
- [ ] Check if server is running (look at terminal windows)
- [ ] If not running, restart from Phase 6
- [ ] If running but showing unhealthy:
  - Check server logs in terminal
  - Verify credentials in .env
  - Restart the server

**If directory check fails**:
- [ ] Create missing directory:
  ```bash
  mkdir AI_Employee_Vault\[directory_name]
  ```
- [ ] Run health check again

**If .env check fails**:
- [ ] Verify .env file exists in project root
- [ ] Check file is not empty: `type .env`
- [ ] Verify file permissions (should be readable)

**If environment variable check fails**:
- [ ] Open .env file: `notepad .env`
- [ ] Find the missing variable
- [ ] Add the value (no quotes, no spaces around =)
- [ ] Save and run health check again

---

### Step 7.8: Save Health Check Results (Optional)

- [ ] **Step 7.8.1**: Run health check with output redirect
  ```bash
  python health_check.py > health_check_results.txt
  ```
  - **Why**: Keep a record of successful health check
  - **File location**: `scripts\health_check_results.txt`

- [ ] **Step 7.8.2**: View saved results
  ```bash
  type health_check_results.txt
  ```

---

### Step 7.9: Final Verification

- [ ] **All checks passed** (all ✓, no ✗)
- [ ] **"All systems operational!"** message shown
- [ ] **No error messages** in output
- [ ] **All 4 MCP servers** still running in their terminals

**If any checks failed**:
- [ ] Fix the issues using troubleshooting steps above
- [ ] Run health check again
- [ ] **Don't proceed to Phase 8** until all checks pass

**Verification**: Does health check show "All systems operational!"?

---

### Common Health Check Errors and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| "Python not found" | Python not installed or not in PATH | Install Python, add to PATH |
| "Node.js not found" | Node.js not installed or not in PATH | Install Node.js, restart terminal |
| "MCP server unhealthy" | Server not running or crashed | Restart server from Phase 6 |
| "Directory not found" | Vault directory missing | Create directory manually |
| ".env not found" | .env file missing | Go back to Phase 4 |
| "Variable not set" | Missing in .env | Add variable to .env |
| "Cannot connect to server" | Server not started or wrong port | Check server terminal, verify port |

---

## Phase 8: Run Verification Script (5 minutes)

**Purpose**: Run end-to-end tests of all Gold Tier features

**What it tests**: Odoo integration, CEO briefing, Ralph Wiggum loop, social media validation, queue service, audit logging

---

### Step 8.1: Prepare for Verification

- [ ] **Step 8.1.1**: Ensure all MCP servers are still running
  - Check all 4 terminal windows from Phase 6
  - All should show servers running (no errors)
  - **If any stopped**: Restart from Phase 6

- [ ] **Step 8.1.2**: Ensure you're in project root
  ```bash
  cd C:\Users\Dell\Desktop\hackathon0
  ```

---

### Step 8.2: Run Verification Script

- [ ] **Step 8.2.1**: Navigate to scripts directory
  ```bash
  cd scripts
  ```

- [ ] **Step 8.2.2**: Run verification script
  ```bash
  python verify_gold_tier.py
  ```
  - **Expected**: Script starts running
  - **Time**: Takes 30-60 seconds
  - **What it does**: Tests all Gold Tier features

---

### Step 8.3: Monitor Verification Progress

**Expected Output** (as script runs):

```
🔍 Gold Tier AI Employee - Verification Script
==============================================

Starting verification tests...

Test 1: Odoo Integration
  ✓ Odoo service initialized
  ✓ Can connect to Odoo MCP server
  ⚠ Cannot create test invoice (Odoo not fully configured)
  Status: PARTIAL PASS

Test 2: CEO Briefing Service
  ✓ CEO Briefing service initialized
  ✓ Business goals loaded
  ⚠ No Odoo data available for briefing
  Status: PARTIAL PASS

Test 3: Ralph Wiggum Loop
  ✓ State manager initialized
  ✓ Stop hook exists
  ✓ Can create task state
  ✓ Can track task progress
  Status: PASS

Test 4: Social Media Validation
  ✓ Social media service initialized
  ✓ Facebook MCP server reachable
  ✓ Instagram MCP server reachable
  ✓ Twitter MCP server reachable
  ⚠ Cannot post without approval workflow
  Status: PASS

Test 5: Queue Service
  ✓ Queue service initialized
  ✓ Can create operation
  ✓ Exponential backoff logic works
  ✓ Can retry failed operations
  Status: PASS

Test 6: Audit Logging
  ✓ Audit service initialized
  ✓ Can create log entry
  ✓ Log file created in Logs/
  ✓ Sensitive data redaction works
  Status: PASS

==============================================
Verification Summary:
  Total Tests: 6
  Passed: 4
  Partial Pass: 2
  Failed: 0

Overall Status: READY FOR MANUAL TESTING ✅

Results saved to: verification_results_2026-02-19_14-30-45.json
```

---

### Step 8.4: Interpret Results

- [ ] **Step 8.4.1**: Check overall status
  - **Expected**: "READY FOR MANUAL TESTING ✅"
  - **If shows "FAILED"**: See troubleshooting below

- [ ] **Step 8.4.2**: Review individual test results
  - [ ] **Test 1 (Odoo)**: PARTIAL PASS is okay
    - Why: Can't create invoices without Odoo fully set up
    - Will test manually in Phase 9

  - [ ] **Test 2 (CEO Briefing)**: PARTIAL PASS is okay
    - Why: No Odoo data yet
    - Will test manually in Phase 9

  - [ ] **Test 3 (Ralph Wiggum)**: Should be PASS ✓
    - If FAIL: Stop hook may be missing

  - [ ] **Test 4 (Social Media)**: Should be PASS ✓
    - If FAIL: MCP servers not reachable

  - [ ] **Test 5 (Queue Service)**: Should be PASS ✓
    - If FAIL: Queue directory may be missing

  - [ ] **Test 6 (Audit Logging)**: Should be PASS ✓
    - If FAIL: Logs directory may be missing

---

### Step 8.5: Check Verification Results File

- [ ] **Step 8.5.1**: Find the results file
  - Look for filename in output: `verification_results_YYYY-MM-DD_HH-MM-SS.json`
  - File location: `scripts\` directory

- [ ] **Step 8.5.2**: Open results file
  ```bash
  notepad verification_results_2026-02-19_14-30-45.json
  ```
  - Replace with your actual filename
  - **Expected**: JSON file with detailed test results

- [ ] **Step 8.5.3**: Review JSON structure
  ```json
  {
    "timestamp": "2026-02-19T14:30:45",
    "overall_status": "READY",
    "tests": [
      {
        "name": "Odoo Integration",
        "status": "PARTIAL_PASS",
        "checks": [...]
      },
      ...
    ],
    "summary": {
      "total": 6,
      "passed": 4,
      "partial": 2,
      "failed": 0
    }
  }
  ```

---

### Step 8.6: Verify Created Files

- [ ] **Step 8.6.1**: Check if audit log was created
  ```bash
  cd ..\AI_Employee_Vault\Logs
  dir audit_*.json
  ```
  - **Expected**: Shows audit log file(s)
  - **File format**: `audit_YYYY-MM-DD.json`

- [ ] **Step 8.6.2**: Check audit log content
  ```bash
  type audit_2026-02-19.json
  ```
  - **Expected**: JSON array with log entries
  - **Should contain**: Verification test actions

- [ ] **Step 8.6.3**: Return to project root
  ```bash
  cd ..\..
  ```

---

### Step 8.7: Troubleshoot Failed Tests

**If Test 1 (Odoo) shows FAIL**:
- [ ] Check Odoo is running: http://localhost:8069
- [ ] Check Odoo MCP server is running (Terminal 1)
- [ ] Verify ODOO_* credentials in .env
- [ ] Test Odoo connection manually:
  ```bash
  curl http://localhost:3100/health
  ```

**If Test 2 (CEO Briefing) shows FAIL**:
- [ ] Check Business_Goals.md exists and has content
- [ ] Verify file is readable
- [ ] Check for syntax errors in Business_Goals.md

**If Test 3 (Ralph Wiggum) shows FAIL**:
- [ ] Check stop hook exists:
  ```bash
  dir AI_Employee_Vault\hooks\stop_hook.bat
  ```
- [ ] Check In_Progress directory exists:
  ```bash
  dir AI_Employee_Vault\In_Progress
  ```
- [ ] Create missing directories if needed

**If Test 4 (Social Media) shows FAIL**:
- [ ] Check all 3 MCP servers running (Terminals 2, 3, 4)
- [ ] Test each server:
  ```bash
  curl http://localhost:3101/health
  curl http://localhost:3102/health
  curl http://localhost:3103/health
  ```
- [ ] Verify social media credentials in .env

**If Test 5 (Queue Service) shows FAIL**:
- [ ] Check Queue directory exists:
  ```bash
  dir AI_Employee_Vault\Queue
  ```
- [ ] Create if missing: `mkdir AI_Employee_Vault\Queue`

**If Test 6 (Audit Logging) shows FAIL**:
- [ ] Check Logs directory exists:
  ```bash
  dir AI_Employee_Vault\Logs
  ```
- [ ] Create if missing: `mkdir AI_Employee_Vault\Logs`
- [ ] Check write permissions on Logs directory

---

### Step 8.8: Re-run Verification After Fixes

- [ ] **Step 8.8.1**: If you fixed any issues, re-run verification
  ```bash
  cd scripts
  python verify_gold_tier.py
  ```

- [ ] **Step 8.8.2**: Verify improvements
  - Check if previously failed tests now pass
  - Overall status should be "READY FOR MANUAL TESTING"

---

### Step 8.9: Save Verification Report

- [ ] **Step 8.9.1**: Copy results to project root (optional)
  ```bash
  copy verification_results_*.json ..\verification_report.json
  ```
  - **Why**: Easy to find later

- [ ] **Step 8.9.2**: Create verification summary (optional)
  - Open Notepad
  - Write summary:
  ```
  Gold Tier Verification Summary
  ==============================
  Date: 2026-02-19
  Time: 14:30:45

  Results:
  - Odoo Integration: PARTIAL PASS (expected)
  - CEO Briefing: PARTIAL PASS (expected)
  - Ralph Wiggum Loop: PASS ✓
  - Social Media: PASS ✓
  - Queue Service: PASS ✓
  - Audit Logging: PASS ✓

  Overall: READY FOR MANUAL TESTING ✅

  Next Steps:
  - Proceed to Phase 9 (Manual Tests)
  - Test Odoo invoice creation
  - Test CEO briefing generation
  - Test social media posting
  ```
  - Save as: `verification_summary.txt`

---

### Step 8.10: Final Verification Checklist

- [ ] **Verification script completed** without crashing
- [ ] **At least 4 tests passed** (Ralph Wiggum, Social Media, Queue, Audit)
- [ ] **Odoo and CEO Briefing** show PARTIAL PASS (acceptable)
- [ ] **Results file created** and readable
- [ ] **Audit log created** in Logs/ directory
- [ ] **Overall status**: "READY FOR MANUAL TESTING"

**If all checks pass**: ✅ Ready for Phase 9 (Manual Tests)

**If any critical failures**: ⚠️ Fix issues before proceeding

**Verification**: Did verification script show "READY FOR MANUAL TESTING"?

---

## Phase 9: Perform Manual Tests (2 hours)

**Purpose**: Complete the 10 remaining manual acceptance tests

### Test T037: Odoo Integration (15 minutes)

- [ ] **Step 1**: Open Claude Code in project directory
- [ ] **Step 2**: Ask Claude to:
  ```
  Record an invoice in Odoo:
  - Customer: Acme Corp
  - Amount: $5,000
  - Description: Consulting services for January 2026
  - Due date: 2026-02-28
  ```
- [ ] **Step 3**: Verify invoice created:
  - [ ] Open http://localhost:8069
  - [ ] Go to Accounting → Customers → Invoices
  - [ ] Find the invoice for Acme Corp
- [ ] **Step 4**: Verify audit log:
  - [ ] Check `AI_Employee_Vault/Logs/audit_YYYY-MM-DD.json`
  - [ ] Find entry with `action_type: "odoo_transaction"`
- [ ] **Step 5**: Mark test as PASSED ✅

### Test T051: CEO Briefing Generation (10 minutes)

- [ ] **Step 1**: In Claude Code, ask:
  ```
  Generate CEO briefing for this week
  ```
- [ ] **Step 2**: Verify briefing created:
  - [ ] Check `AI_Employee_Vault/CEO_Briefings/` folder
  - [ ] Open the latest briefing file
- [ ] **Step 3**: Verify briefing contains:
  - [ ] Revenue summary (from Odoo data)
  - [ ] Expense analysis
  - [ ] Bottleneck detection
  - [ ] Proactive suggestions
- [ ] **Step 4**: Mark test as PASSED ✅

### Test T064: Ralph Wiggum Loop - Simple Task (10 minutes)

- [ ] **Step 1**: In Claude Code, ask:
  ```
  Process this multi-step task autonomously:
  1. Create a test file in Inbox/ with content "Test data for Ralph Wiggum"
  2. Read the file and verify the content
  3. Move the file to Done/
  ```
- [ ] **Step 2**: Verify autonomous completion:
  - [ ] Claude should complete all 3 steps without stopping
  - [ ] No "should I continue?" prompts
- [ ] **Step 3**: Verify file moved:
  - [ ] Check `AI_Employee_Vault/Done/` for the test file
- [ ] **Step 4**: Verify state tracking:
  - [ ] Check `AI_Employee_Vault/In_Progress/` (should be empty after completion)
- [ ] **Step 5**: Mark test as PASSED ✅

### Test T065: Ralph Wiggum Max Iterations (10 minutes)

- [ ] **Step 1**: In Claude Code, ask:
  ```
  Process this task autonomously (this will test max iterations):
  Repeat the following 15 times:
  1. Create a file named "iteration_N.txt" in Inbox/
  2. Write "Iteration N" to the file
  3. Move it to Done/
  ```
- [ ] **Step 2**: Verify graceful stop:
  - [ ] Loop should stop at max iterations (10 by default)
  - [ ] Should show message about reaching limit
- [ ] **Step 3**: Count files created:
  - [ ] Check `AI_Employee_Vault/Done/` folder
  - [ ] Should have ~10 iteration files (not 15)
- [ ] **Step 4**: Mark test as PASSED ✅

### Test T066: Ralph Wiggum Error Handling (10 minutes)

- [ ] **Step 1**: In Claude Code, ask:
  ```
  Process this task autonomously:
  1. Create a test file in Inbox/
  2. Try to read a non-existent file "does_not_exist.txt"
  3. Move the test file to Done/
  ```
- [ ] **Step 2**: Verify error handling:
  - [ ] Step 2 should fail (file doesn't exist)
  - [ ] Task should be marked as blocked
- [ ] **Step 3**: Verify state:
  - [ ] Check `AI_Employee_Vault/In_Progress/` for blocked task
  - [ ] Task should have error details
- [ ] **Step 4**: Mark test as PASSED ✅

### Test T089: Facebook Posting (15 minutes)

- [ ] **Step 1**: Prepare test image (optional):
  - [ ] Find a test image URL or use text-only post
- [ ] **Step 2**: In Claude Code, ask:
  ```
  Create a Facebook post for approval:
  - Text: "Testing Gold Tier AI Employee! 🤖 Automated social media posting is now live. #AI #Automation"
  - Image: [optional - provide URL if you have one]
  ```
- [ ] **Step 3**: Verify draft created:
  - [ ] Check `AI_Employee_Vault/Pending_Approval/` folder
  - [ ] Review the draft post
- [ ] **Step 4**: Approve the post:
  - [ ] Move file from `Pending_Approval/` to `Approved/`
  - [ ] Or tell Claude to approve it
- [ ] **Step 5**: Verify publication:
  - [ ] Check your Facebook Page
  - [ ] Find the post
- [ ] **Step 6**: Retrieve metrics (after 1 hour):
  - [ ] Ask Claude to get engagement metrics
  - [ ] Verify likes, comments, shares, reach
- [ ] **Step 7**: Mark test as PASSED ✅

### Test T090: Instagram Posting (15 minutes)

- [ ] **Step 1**: Prepare test image (REQUIRED for Instagram):
  - [ ] Instagram requires an image
  - [ ] Find a publicly accessible image URL
- [ ] **Step 2**: In Claude Code, ask:
  ```
  Create an Instagram post for approval:
  - Text: "Excited to share our AI Employee Gold Tier launch! 🚀 #AI #Automation #TechInnovation"
  - Image: [your image URL]
  - Hashtags: #AI #Automation #TechInnovation
  ```
- [ ] **Step 3**: Verify draft created:
  - [ ] Check `AI_Employee_Vault/Pending_Approval/` folder
- [ ] **Step 4**: Approve the post:
  - [ ] Move to `Approved/` or tell Claude to approve
- [ ] **Step 5**: Verify publication:
  - [ ] Check your Instagram Business account
  - [ ] Find the post
- [ ] **Step 6**: Retrieve metrics (after 1 hour):
  - [ ] Ask Claude to get engagement metrics
  - [ ] Verify likes, comments, saves, reach
- [ ] **Step 7**: Mark test as PASSED ✅

### Test T091: Multi-Platform Posting (15 minutes)

- [ ] **Step 1**: In Claude Code, ask:
  ```
  Create a multi-platform social media post for approval:
  - Platforms: Facebook, Instagram
  - Text: "Big announcement! Our Q1 results are in and we're thrilled with the growth! 📈 Thank you to our amazing customers! #Business #Growth"
  - Image: [your image URL]
  ```
- [ ] **Step 2**: Verify drafts created:
  - [ ] Check `Pending_Approval/` for 2 draft files (one per platform)
- [ ] **Step 3**: Approve both posts:
  - [ ] Move both to `Approved/`
- [ ] **Step 4**: Verify publication on both platforms:
  - [ ] Check Facebook Page
  - [ ] Check Instagram account
  - [ ] Same content on both
- [ ] **Step 5**: Mark test as PASSED ✅

### Test T103: Twitter Posting (15 minutes)

- [ ] **Step 1**: In Claude Code, ask:
  ```
  Post to Twitter:
  - Text: "Just completed the Gold Tier implementation of our AI Employee! 🤖 Autonomous task execution, social media automation, and business intelligence all in one. #AI #Automation #Claude"
  ```
- [ ] **Step 2**: Verify tweet posted:
  - [ ] Check your Twitter account
  - [ ] Find the tweet
- [ ] **Step 3**: Verify tweet ID returned:
  - [ ] Claude should show the tweet ID
- [ ] **Step 4**: Retrieve metrics (after 1 hour):
  - [ ] Ask Claude to get engagement metrics
  - [ ] Verify likes, retweets, replies, impressions
- [ ] **Step 5**: Mark test as PASSED ✅

### Test T104: Twitter Rate Limit Handling (10 minutes)

- [ ] **Step 1**: Check current rate limit status:
  - [ ] In Claude Code, ask:
    ```
    Check Twitter API rate limit status
    ```
- [ ] **Step 2**: Verify rate limit info returned:
  - [ ] Should show remaining requests
  - [ ] Should show reset time
- [ ] **Step 3**: (Optional) Test rate limit handling:
  - [ ] Post multiple tweets rapidly
  - [ ] Verify queue integration when limit reached
- [ ] **Step 4**: Mark test as PASSED ✅

---

## Phase 10: Final Verification & Celebration 🎉

### Step 10.1: Review Test Results

- [ ] Count passed tests: _____ / 10
- [ ] Review any failures
- [ ] Document issues in `AI_Employee_Vault/Logs/`

### Step 10.2: Update Tasks.md

- [ ] Open `specs/003-gold-autonomous-employee/tasks.md`
- [ ] Mark all completed tests as `[x]`
- [ ] Update completion percentage

### Step 10.3: Final Commit

- [ ] Commit test results:
  ```bash
  git add .
  git commit -m "Complete Gold Tier manual testing - All 10 tests passed"
  git push gold 003-gold-autonomous-employee
  ```

### Step 10.4: Generate Completion Report

- [ ] In Claude Code, ask:
  ```
  Generate a Gold Tier completion report summarizing:
  - All features implemented
  - All tests passed
  - Final statistics
  - Next steps for production deployment
  ```

### Step 10.5: Celebrate! 🎉

- [ ] **Congratulations!** You've completed Gold Tier!
- [ ] Final Status: **120/120 tasks complete (100%)**
- [ ] You now have a fully autonomous AI employee!

---

## 📊 Final Statistics

| Metric | Value |
|--------|-------|
| **Total Tasks** | 120 |
| **Development Tasks** | 112 (100% complete) |
| **Manual Tests** | 10 (___% complete) |
| **Overall Completion** | ___% |
| **Lines of Code** | 12,000+ |
| **Files Created** | 50+ |
| **Documentation** | 2,400+ lines |
| **Time Invested** | ___ hours |

---

## 🆘 Troubleshooting

### If MCP Server Won't Start

- [ ] Check if port is already in use:
  ```bash
  netstat -ano | findstr :3100
  ```
- [ ] Kill the process or change port in config

### If Odoo Connection Fails

- [ ] Verify Odoo is running: http://localhost:8069
- [ ] Check credentials in .env file
- [ ] Restart Odoo container:
  ```bash
  docker restart odoo
  ```

### If Social Media API Fails

- [ ] Verify tokens haven't expired
- [ ] Check token permissions in developer console
- [ ] Regenerate tokens if needed

### If Tests Fail

- [ ] Check `AI_Employee_Vault/Logs/` for error details
- [ ] Review `docs/gold-tier-troubleshooting.md`
- [ ] Ask Claude Code for help with specific errors

---

## 📚 Documentation References

- **Setup Guide**: `docs/gold-tier-setup.md`
- **API Credentials**: `docs/api-credentials.md`
- **Troubleshooting**: `docs/gold-tier-troubleshooting.md`
- **Tasks List**: `specs/003-gold-autonomous-employee/tasks.md`
- **GitHub Repo**: https://github.com/Tahaimran56/personalAIEmployee_gold_level

---

## 🎯 Success Criteria

Gold Tier is **100% complete** when:
- ✅ All 112 development tasks complete
- ✅ All 4 MCP servers running
- ✅ Health check passes
- ✅ All 10 manual tests pass
- ✅ All features working end-to-end

---

**Good luck with your setup! You're building something amazing!** 🚀
