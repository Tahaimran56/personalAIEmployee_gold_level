# Silver Tier: Functional Assistant

## Overview

Silver tier builds on Bronze tier's foundation by adding **functional automation capabilities**. The AI Employee can now monitor external services (Gmail, LinkedIn), execute multi-step reasoning workflows, and perform actions with human-in-the-loop approval.

## What's New in Silver Tier

### 1. Gmail Watcher
- **Purpose**: Monitor Gmail inbox for new emails
- **Functionality**:
  - Detect new emails automatically
  - Extract sender, subject, body, attachments
  - Create action files in `Needs_Action/` folder
  - Categorize by priority (urgent, normal, low)
- **Implementation**: New watcher class extending `BaseWatcher`

### 2. LinkedIn Integration
- **Purpose**: Automate business-related LinkedIn posts
- **Functionality**:
  - Post updates to LinkedIn profile/company page
  - Schedule posts for optimal timing
  - Track post performance (views, engagement)
  - Require approval before posting
- **Implementation**: LinkedIn API integration with OAuth2

### 3. MCP Email Server
- **Purpose**: Send emails with human approval workflow
- **Functionality**:
  - Compose emails based on action files
  - Generate draft emails for review
  - Require approval before sending
  - Track sent emails in logs
- **Implementation**: MCP server for email operations

### 4. Claude Reasoning Loop
- **Purpose**: Handle multi-step tasks with planning
- **Functionality**:
  - Analyze complex tasks from action files
  - Generate `Plan.md` files with step-by-step approach
  - Break down tasks into subtasks
  - Execute plan with checkpoints
- **Implementation**: Claude API integration with reasoning prompts

### 5. Human-in-the-Loop (HITL) Approval
- **Purpose**: Safety mechanism for sensitive actions
- **Functionality**:
  - Identify actions requiring approval (email send, LinkedIn post, file delete)
  - Move to `Pending_Approval/` folder
  - Wait for user approval/rejection
  - Execute only after approval
  - Log all approval decisions
- **Implementation**: Enhanced approval workflow from Bronze tier

### 6. Basic Scheduling
- **Purpose**: Run watchers and tasks on schedule
- **Functionality**:
  - Schedule watchers to run at intervals (every 5 min, hourly, daily)
  - Schedule recurring tasks (daily reports, weekly summaries)
  - Platform-specific: cron (Linux/Mac) or Task Scheduler (Windows)
- **Implementation**: Scheduler scripts with platform detection

## Architecture

```
AI_Employee_Vault/
├── watchers/
│   ├── base_watcher.py          # Base class (from Bronze)
│   ├── filesystem_watcher.py    # File watcher (from Bronze)
│   ├── gmail_watcher.py         # NEW: Gmail monitoring
│   └── linkedin_watcher.py      # NEW: LinkedIn monitoring
├── services/
│   ├── email_service.py         # NEW: MCP email server
│   ├── linkedin_service.py      # NEW: LinkedIn API client
│   └── reasoning_service.py     # NEW: Claude reasoning loop
├── .claude/skills/
│   ├── process-actions.skill.md      # Enhanced from Bronze
│   ├── send-email.skill.md           # NEW: Send email with approval
│   ├── post-linkedin.skill.md        # NEW: Post to LinkedIn
│   ├── create-plan.skill.md          # NEW: Generate Plan.md
│   └── schedule-task.skill.md        # NEW: Schedule recurring tasks
├── scheduler/
│   ├── scheduler.py             # NEW: Task scheduler
│   ├── cron_setup.sh           # NEW: Linux/Mac cron setup
│   └── task_scheduler.ps1      # NEW: Windows Task Scheduler setup
└── Plans/                       # NEW: Generated plan files
    └── [task-id]-plan.md
```

## Success Criteria

### SC-1: Gmail Monitoring
- [ ] Watcher detects new emails within 5 minutes
- [ ] Action files created with correct metadata
- [ ] Priority detection works (urgent keywords)
- [ ] Attachments are referenced correctly

### SC-2: LinkedIn Integration
- [ ] Can post text updates to LinkedIn
- [ ] Approval workflow prevents unauthorized posts
- [ ] Posts are logged with timestamps
- [ ] OAuth2 authentication works

### SC-3: Email Sending
- [ ] MCP server can compose emails
- [ ] Drafts require approval before sending
- [ ] Sent emails are logged
- [ ] Supports attachments and HTML formatting

### SC-4: Reasoning Loop
- [ ] Complex tasks generate Plan.md files
- [ ] Plans include step-by-step breakdown
- [ ] Plans are human-readable and actionable
- [ ] Execution follows plan checkpoints

### SC-5: HITL Approval
- [ ] Sensitive actions move to Pending_Approval/
- [ ] Approval/rejection is logged
- [ ] Rejected actions are archived
- [ ] Approved actions execute correctly

### SC-6: Scheduling
- [ ] Watchers run on schedule (configurable intervals)
- [ ] Recurring tasks execute at specified times
- [ ] Platform detection works (Windows/Linux/Mac)
- [ ] Logs show scheduled execution history

## Implementation Phases

### Phase 1: Gmail Watcher (Priority: P1)
1. Set up Gmail API credentials
2. Implement `gmail_watcher.py`
3. Test email detection and action file creation
4. Add Gmail skill to `.claude/skills/`

### Phase 2: MCP Email Server (Priority: P1)
1. Set up MCP email server
2. Implement email composition logic
3. Add approval workflow
4. Test email sending with approval

### Phase 3: LinkedIn Integration (Priority: P2)
1. Set up LinkedIn OAuth2
2. Implement `linkedin_service.py`
3. Add posting functionality with approval
4. Test post creation and logging

### Phase 4: Claude Reasoning Loop (Priority: P1)
1. Design Plan.md template
2. Implement reasoning service
3. Add plan generation skill
4. Test with multi-step tasks

### Phase 5: Enhanced HITL Approval (Priority: P1)
1. Extend approval workflow from Bronze
2. Add approval rules for new actions
3. Implement approval logging
4. Test approval/rejection flows

### Phase 6: Basic Scheduling (Priority: P2)
1. Implement scheduler.py
2. Create platform-specific setup scripts
3. Configure watcher schedules
4. Test scheduled execution

## Dependencies

### Python Packages
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
pip install linkedin-api
pip install anthropic  # Claude API
pip install schedule
```

### External Services
- Gmail API (OAuth2 credentials required)
- LinkedIn API (OAuth2 credentials required)
- Claude API (API key required)

### Configuration Files
- `.env` - API keys and credentials
- `config/gmail_config.json` - Gmail API settings
- `config/linkedin_config.json` - LinkedIn API settings
- `config/scheduler_config.json` - Scheduling rules

## Security Considerations

1. **API Keys**: Store in `.env`, never commit to git
2. **OAuth Tokens**: Store encrypted, refresh automatically
3. **Approval Logs**: Track all sensitive actions
4. **Email Content**: Sanitize before sending
5. **LinkedIn Posts**: Validate content before posting

## Testing Strategy

1. **Unit Tests**: Test each watcher and service independently
2. **Integration Tests**: Test end-to-end workflows
3. **Approval Tests**: Verify HITL workflow for all sensitive actions
4. **Schedule Tests**: Verify scheduled execution works correctly
5. **Manual Tests**: Test with real Gmail/LinkedIn accounts

## Next Steps

1. Run `/sp.specify` to create detailed specification
2. Run `/sp.plan` to generate architecture plan
3. Run `/sp.tasks` to create actionable task list
4. Implement phase by phase
5. Test each phase before moving to next
6. Document all Agent Skills

---

**Status**: Ready to start Silver tier implementation
**Prerequisites**: Bronze tier complete ✅
**Estimated Complexity**: Medium-High (6 new components, 3 external APIs)
