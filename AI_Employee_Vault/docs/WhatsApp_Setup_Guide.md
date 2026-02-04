# WhatsApp Watcher Setup Guide

## Overview

The WhatsApp Watcher monitors WhatsApp Web for new messages containing priority keywords and creates action files in your Obsidian vault.

## Features

- **Keyword-based monitoring**: Detects messages with keywords like "urgent", "invoice", "payment", "help"
- **Session persistence**: Login once with QR code, session saved for future use
- **Automated monitoring**: Runs every 30 seconds (configurable)
- **Action file creation**: Creates markdown files in Needs_Action/ folder
- **Priority detection**: All matched messages marked as urgent

## Prerequisites

1. Python 3.13+ installed
2. Playwright package installed
3. Chromium browser installed (via Playwright)
4. WhatsApp account with phone access

## Installation Steps

### Step 1: Install Playwright

```bash
# Install Playwright package
pip install playwright

# Install Chromium browser (~300MB download)
playwright install chromium
```

### Step 2: Run Setup Script

```bash
# Run the automated setup script
python AI_Employee_Vault/setup/whatsapp_setup.py
```

The setup script will:
1. Check if Playwright is installed
2. Install Chromium browser if needed
3. Create session directory
4. Open browser for QR code scan
5. Test WhatsApp Web connection

### Step 3: Scan QR Code

When the browser opens:

1. Open WhatsApp on your phone
2. Tap Menu (⋮) or Settings
3. Tap "Linked Devices"
4. Tap "Link a Device"
5. Scan the QR code in the browser window

**Important**: You have 2 minutes to scan the QR code.

### Step 4: Verify Session

After scanning, the setup script will:
- Wait for successful login
- Save session for future use
- Confirm setup completion

## Configuration

Edit `config/whatsapp_config.json` to customize:

```json
{
  "whatsapp_watcher": {
    "check_interval_seconds": 30,
    "max_messages_per_check": 50,
    "priority_keywords": [
      "urgent",
      "asap",
      "invoice",
      "payment",
      "help",
      "emergency",
      "critical"
    ],
    "headless": false,
    "timeout_seconds": 30
  }
}
```

### Configuration Options

- **check_interval_seconds**: How often to check for new messages (default: 30)
- **max_messages_per_check**: Maximum messages to process per check (default: 50)
- **priority_keywords**: Keywords that trigger action file creation
- **headless**: Run browser in background (false = visible, true = hidden)
- **timeout_seconds**: Timeout for page operations (default: 30)

## Running the Watcher

### Manual Mode

```bash
# Run watcher manually (Ctrl+C to stop)
python AI_Employee_Vault/watchers/whatsapp_watcher.py
```

### Scheduled Mode

The watcher runs automatically via the scheduler:

```bash
# Start scheduler (includes WhatsApp watcher)
python AI_Employee_Vault/scheduler/scheduler.py
```

## How It Works

### 1. Message Detection

The watcher:
1. Opens WhatsApp Web in browser
2. Scans for unread messages
3. Checks message text for priority keywords
4. Creates action files for matches

### 2. Action File Creation

When a priority message is detected, an action file is created:

**Location**: `AI_Employee_Vault/Needs_Action/whatsapp-YYYYMMDD_HHMMSS-ChatName.md`

**Content**:
```markdown
---
entity_type: whatsapp_action
message_id: ChatName_20260204_103000_0
chat_name: Client Name
matched_keywords: ['urgent', 'payment']
priority: urgent
timestamp: 2026-02-04T10:30:00Z
processed_status: pending
---

# WhatsApp Action: Client Name

**From**: Client Name
**Received**: 2026-02-04T10:30:00Z
**Priority**: 🔴 Urgent
**Matched Keywords**: urgent, payment

## Message Preview
Need urgent payment for invoice #123

## Suggested Actions
1. Open WhatsApp Web to view full conversation
2. Draft response if needed
3. Mark as processed when complete
```

### 3. Processing Workflow

1. **Detection**: Watcher finds priority message
2. **Action File**: Creates markdown file in Needs_Action/
3. **Claude Processing**: Claude reads action file and generates response plan
4. **Approval**: Response requires approval before sending
5. **Execution**: Approved response sent via WhatsApp (manual for now)
6. **Logging**: Action logged in Logs/

## Troubleshooting

### Issue: QR Code Not Appearing

**Solution**:
- Set `headless: false` in config
- Ensure browser window is visible
- Check internet connection

### Issue: Session Expired

**Symptoms**: QR code appears every time

**Solution**:
```bash
# Re-run setup to create new session
python AI_Employee_Vault/setup/whatsapp_setup.py
```

### Issue: Browser Crashes

**Solution**:
- Check available RAM (browser needs ~500MB)
- Close other applications
- Restart watcher

### Issue: Messages Not Detected

**Solution**:
1. Check keywords in config match your messages
2. Verify messages are unread in WhatsApp Web
3. Check watcher logs: `AI_Employee_Vault/Logs/whatsappwatcher.log`

### Issue: Playwright Not Found

**Solution**:
```bash
# Install Playwright
pip install playwright

# Install browsers
playwright install chromium
```

## Session Management

### Session Location

Session data stored in: `AI_Employee_Vault/.state/whatsapp_session/`

This directory contains:
- Browser profile data
- WhatsApp Web login session
- Cookies and local storage

### Session Persistence

- Session persists across watcher restarts
- No QR code scan needed after initial setup
- Session expires after ~2 weeks of inactivity

### Resetting Session

To reset and re-login:

```bash
# Delete session directory
rm -rf AI_Employee_Vault/.state/whatsapp_session

# Re-run setup
python AI_Employee_Vault/setup/whatsapp_setup.py
```

## Security Considerations

### WhatsApp Terms of Service

**Important**: WhatsApp's Terms of Service prohibit automated access to WhatsApp Web. This watcher is intended for:
- Personal use only
- Educational purposes
- Low-volume monitoring (not bulk messaging)

**Do NOT use for**:
- Spam or bulk messaging
- Commercial automation
- Violating WhatsApp ToS

### Data Privacy

- All data stored locally in your vault
- No data sent to third parties
- Session data encrypted by browser

### Best Practices

1. **Use responsibly**: Monitor only your own messages
2. **Respect privacy**: Don't automate responses to sensitive conversations
3. **Human oversight**: Always review before sending responses
4. **Rate limiting**: Don't check too frequently (30 seconds minimum)

## Advanced Usage

### Custom Keywords

Add domain-specific keywords to config:

```json
"priority_keywords": [
  "urgent",
  "invoice",
  "payment",
  "client name",
  "project deadline",
  "meeting today"
]
```

### Headless Mode

For production use, enable headless mode:

```json
"headless": true
```

Browser runs in background (no visible window).

### Integration with Scheduler

The watcher is automatically scheduled to run every minute:

```json
{
  "schedule_id": "whatsapp-watcher-schedule",
  "task_name": "WhatsApp Watcher",
  "cron_expression": "*/1 * * * *",
  "status": "active"
}
```

## Logs and Monitoring

### Log Location

`AI_Employee_Vault/Logs/whatsappwatcher.log`

### Log Contents

- Watcher start/stop events
- Messages detected
- Action files created
- Errors and warnings

### Monitoring

Check logs regularly:

```bash
# View recent logs
tail -f AI_Employee_Vault/Logs/whatsappwatcher.log

# Search for errors
grep ERROR AI_Employee_Vault/Logs/whatsappwatcher.log
```

## Next Steps

After setup:

1. ✅ Test watcher manually
2. ✅ Send test message with keyword
3. ✅ Verify action file created
4. ✅ Enable scheduler for automation
5. ✅ Monitor logs for issues

## Support

For issues or questions:
- Check logs: `AI_Employee_Vault/Logs/whatsappwatcher.log`
- Review troubleshooting section above
- Check Playwright docs: https://playwright.dev/python/
