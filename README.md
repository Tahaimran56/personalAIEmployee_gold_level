# Personal AI Employee - Silver Tier: Functional Assistant

[![Tier](https://img.shields.io/badge/Tier-Silver-C0C0C0)](https://github.com/Tahaimran56/personalAIEmployee_silverlevel)
[![Status](https://img.shields.io/badge/Status-Planning%20Complete-blue)](https://github.com/Tahaimran56/personalAIEmployee_silverlevel)
[![Python](https://img.shields.io/badge/Python-3.13+-green)](https://www.python.org/)
[![Node.js](https://img.shields.io/badge/Node.js-24+-green)](https://nodejs.org/)

> **Building on Bronze**: Silver tier transforms your AI Employee from a passive file watcher into a **functional assistant** that monitors Gmail, sends emails with approval, posts to LinkedIn, generates multi-step plans, and runs on autopilot with scheduling.

**Bronze Tier Repository**: https://github.com/Tahaimran56/personalAIEmployee_bronze_level

---

## 🎯 What's New in Silver Tier

Silver tier adds **6 major capabilities** to your AI Employee:

### 1. 📧 Gmail Monitoring
- Automatically detects new emails in your Gmail inbox
- Creates action files with sender, subject, priority, and attachments
- Priority detection (URGENT, ASAP, IMPORTANT keywords)
- Duplicate prevention (never processes the same email twice)
- Runs every 5 minutes on schedule

### 2. 📤 Email Sending with Approval
- Drafts email responses based on action files
- **Human-in-the-loop approval** required before sending
- MCP email server with OAuth2 SMTP
- Supports HTML formatting and attachments
- Logs all sent emails with timestamps

### 3. 💼 LinkedIn Integration
- Drafts LinkedIn posts for your profile
- **Approval workflow** prevents unauthorized posts
- Validates content (3000 character limit, hashtags)
- Tracks engagement metrics (views, likes, comments, shares)
- Logs all published posts

### 4. 🧠 Multi-Step Task Planning
- Detects complex tasks and generates step-by-step plans
- Uses Claude API for intelligent reasoning
- Creates Plan.md files with acceptance criteria
- Sequential execution with checkpoint logging
- Pauses on failure and notifies user

### 5. ✅ Enhanced Approval Workflow
- All sensitive actions require explicit approval
- 24-hour timeout with auto-rejection
- Approval logging with timestamp and approver
- Configurable approval rules in Company Handbook
- Supports email send, LinkedIn post, file delete

### 6. ⏰ Scheduled Automation
- Watchers run automatically on schedule
- Cross-platform: cron (Linux/Mac), Task Scheduler (Windows)
- Configurable intervals (every 5 min, hourly, daily)
- Execution logging and error handling
- Survives system restarts

---

## 📊 Silver Tier Statistics

| Metric | Value |
|--------|-------|
| **Planning Documents** | 8 comprehensive documents |
| **Total Lines of Documentation** | 4,210 lines |
| **User Stories** | 6 stories (4 P1, 2 P2) |
| **Functional Requirements** | 25 requirements |
| **Success Criteria** | 15 measurable outcomes |
| **Implementation Tasks** | 112 actionable tasks |
| **API Integrations** | 3 (Gmail, LinkedIn, Claude) |
| **New Watchers** | 2 (Gmail, LinkedIn) |
| **New Services** | 3 (Email, LinkedIn, Reasoning) |
| **New Agent Skills** | 5 skills |
| **Estimated Duration** | 14-21 days (MVP: 8-12 days) |

---

## 🏗️ Architecture Overview

```
Silver Tier Architecture
├── Bronze Tier Foundation
│   ├── Obsidian Vault (AI_Employee_Vault/)
│   ├── File System Watcher
│   ├── BaseWatcher Class
│   └── Agent Skills Framework
│
└── Silver Tier Extensions
    ├── Gmail Watcher (email monitoring)
    ├── Email Service (MCP server + approval)
    ├── LinkedIn Service (posts + approval)
    ├── Reasoning Service (Claude API planning)
    ├── Scheduler Service (automated execution)
    └── Enhanced Approval Workflow
```

### Data Flow

```
Gmail → Email Action → Needs_Action/ → Claude Processing → Draft Email → Pending_Approval/ → User Approval → MCP Server → Sent Email → Logs/

Action File → Complex Task Detection → Claude Reasoning → Plan.md → Step Execution → Dashboard Update

LinkedIn Request → Draft Post → Pending_Approval/ → User Approval → LinkedIn API → Published Post → Logs/

Scheduler → Watcher Execution → Action Files → Processing Loop
```

---

## 📋 Prerequisites

### 1. Bronze Tier Complete
- ✅ Obsidian vault set up at `AI_Employee_Vault/`
- ✅ BaseWatcher class implemented
- ✅ File System Watcher working
- ✅ Agent Skills documented
- ✅ Dashboard and Company Handbook created

**Bronze Tier Repository**: https://github.com/Tahaimran56/personalAIEmployee_bronze_level

### 2. System Requirements
- Python 3.13+ installed
- Node.js 24+ installed (for MCP server)
- Git installed
- Internet connectivity for API calls
- Windows, Linux, or Mac

### 3. API Credentials Required
- **Gmail API**: OAuth2 Client ID and Secret
- **LinkedIn API**: OAuth2 Client ID and Secret
- **Claude API**: API Key

---

## 🚀 Quick Start

### Step 1: Clone Repository

```bash
git clone https://github.com/Tahaimran56/personalAIEmployee_silverlevel.git
cd personalAIEmployee_silverlevel
git checkout 002-silver-functional-assistant
```

### Step 2: Install Dependencies

```bash
# Python dependencies
pip install google-auth google-auth-oauthlib google-api-python-client
pip install linkedin-api anthropic schedule python-dotenv pytest

# Node.js dependencies (MCP server)
cd AI_Employee_Vault/mcp
npm install
cd ../..
```

### Step 3: Set Up API Credentials

#### Gmail API
1. Go to https://console.cloud.google.com
2. Create project: "AI Employee Silver"
3. Enable Gmail API
4. Create OAuth 2.0 Client ID (Desktop app)
5. Download credentials JSON
6. Run: `python AI_Employee_Vault/setup/gmail_auth.py`

#### LinkedIn API
1. Go to https://www.linkedin.com/developers/apps
2. Create new app
3. Request Share API access
4. Note Client ID and Client Secret
5. Run: `python AI_Employee_Vault/setup/linkedin_auth.py`

#### Claude API
1. Go to https://console.anthropic.com
2. Create API key
3. Add to `config/.env`: `CLAUDE_API_KEY=your_key`

### Step 4: Configure Environment

```bash
# Copy template
cp config/.env.template config/.env

# Edit config/.env with your credentials
nano config/.env
```

### Step 5: Run Verification

```bash
# Verify all components
python AI_Employee_Vault/verify_silver.py
```

Expected output:
```
Silver Tier Verification Report
================================

✅ Gmail Watcher: Working
✅ Email Service: Working
✅ LinkedIn Service: Working
✅ Reasoning Service: Working
✅ Scheduler: Working
✅ Approval Workflow: Working

All checks passed! Silver tier is complete.
```

---

## 📖 Usage Examples

### Example 1: Email Monitoring

```bash
# Run Gmail Watcher manually
python AI_Employee_Vault/watchers/gmail_watcher.py

# Check for new action files
ls AI_Employee_Vault/Needs_Action/

# Example output:
# email-abc123.md (URGENT: Client meeting)
# email-def456.md (Weekly report)
```

### Example 2: Send Email with Approval

```bash
# 1. Create action file requesting email send
cat > AI_Employee_Vault/Needs_Action/send-email-request.md << 'EOF'
---
action_type: send_email
recipient: client@example.com
subject: Re: Meeting tomorrow
---

# Email Send Request

Draft a response confirming the meeting at 2 PM tomorrow.
EOF

# 2. Claude processes and creates draft in Pending_Approval/
# 3. Review draft: cat AI_Employee_Vault/Pending_Approval/email-draft-*.md
# 4. Approve: mv AI_Employee_Vault/Pending_Approval/email-draft-*.md AI_Employee_Vault/Approved/
# 5. Email sent automatically, logged in Logs/
```

### Example 3: Generate Multi-Step Plan

```bash
# Create complex task
cat > AI_Employee_Vault/Needs_Action/research-task.md << 'EOF'
---
action_type: complex_task
---

# Research Task

Research top 5 competitors in AI automation space and prepare summary report with strengths, weaknesses, and market positioning.
EOF

# Claude detects complexity and generates Plan.md
# View plan: cat AI_Employee_Vault/Plans/plan-*.md
```

### Example 4: LinkedIn Post with Approval

```bash
# Create LinkedIn post request
cat > AI_Employee_Vault/Needs_Action/linkedin-post.md << 'EOF'
---
action_type: linkedin_post
---

# LinkedIn Post

Announce our new AI Employee Silver tier release with key features and benefits.
EOF

# Draft created in Pending_Approval/
# Approve and post publishes to LinkedIn
```

### Example 5: Scheduled Execution

```bash
# Configure schedules
cat config/scheduler_config.json

# Start scheduler
python AI_Employee_Vault/scheduler/scheduler.py

# Watchers run automatically:
# - Gmail Watcher: Every 5 minutes
# - LinkedIn Watcher: Every hour

# Check logs
tail -f AI_Employee_Vault/Logs/scheduler.log
```

---

## 📁 Project Structure

```
personalAIEmployee_silverlevel/
├── AI_Employee_Vault/
│   ├── watchers/
│   │   ├── base_watcher.py          # Base class (from Bronze)
│   │   ├── filesystem_watcher.py    # File watcher (from Bronze)
│   │   ├── gmail_watcher.py         # NEW: Gmail monitoring
│   │   └── linkedin_watcher.py      # NEW: LinkedIn monitoring
│   │
│   ├── services/
│   │   ├── email_service.py         # NEW: Email composition & sending
│   │   ├── linkedin_service.py      # NEW: LinkedIn API client
│   │   ├── reasoning_service.py     # NEW: Claude reasoning loop
│   │   └── approval_service.py      # NEW: Enhanced approval workflow
│   │
│   ├── scheduler/
│   │   ├── scheduler.py             # NEW: Task scheduler
│   │   ├── cron_setup.sh           # NEW: Linux/Mac setup
│   │   └── task_scheduler.ps1      # NEW: Windows setup
│   │
│   ├── mcp/
│   │   ├── server.js               # NEW: MCP email server
│   │   └── package.json            # NEW: Node.js dependencies
│   │
│   ├── .claude/skills/
│   │   ├── process-actions.skill.md      # Enhanced from Bronze
│   │   ├── send-email.skill.md           # NEW
│   │   ├── post-linkedin.skill.md        # NEW
│   │   ├── create-plan.skill.md          # NEW
│   │   └── schedule-task.skill.md        # NEW
│   │
│   ├── Plans/                       # NEW: Generated plans
│   ├── Inbox/                       # From Bronze
│   ├── Needs_Action/                # From Bronze
│   ├── Pending_Approval/            # From Bronze (enhanced)
│   ├── Approved/                    # From Bronze
│   ├── Done/                        # From Bronze
│   ├── Logs/                        # From Bronze (enhanced)
│   ├── Dashboard.md                 # From Bronze (enhanced)
│   └── Company_Handbook.md          # From Bronze (enhanced)
│
├── config/
│   ├── .env                         # API credentials (gitignored)
│   ├── .env.template                # Template for credentials
│   ├── gmail_config.json            # Gmail settings
│   ├── linkedin_config.json         # LinkedIn settings
│   ├── scheduler_config.json        # Schedule definitions
│   └── mcp_email_server.json        # SMTP settings
│
├── specs/002-silver-functional-assistant/
│   ├── spec.md                      # Feature specification
│   ├── plan.md                      # Implementation plan
│   ├── tasks.md                     # 112 actionable tasks
│   ├── research.md                  # Technical decisions
│   ├── data-model.md                # Entity definitions
│   ├── quickstart.md                # Setup guide
│   ├── contracts/                   # API contracts
│   │   ├── gmail-watcher-contract.md
│   │   ├── email-service-contract.md
│   │   ├── linkedin-service-contract.md
│   │   ├── reasoning-service-contract.md
│   │   └── scheduler-service-contract.md
│   └── checklists/
│       └── requirements.md          # Quality validation
│
├── tests/
│   ├── unit/                        # Unit tests
│   └── integration/                 # Integration tests
│
├── README.md                        # This file
├── SILVER_TIER_README.md            # Feature overview
└── .gitignore
```

---

## 📚 Documentation

### Planning Documents

All planning documents are in `specs/002-silver-functional-assistant/`:

- **[spec.md](specs/002-silver-functional-assistant/spec.md)** - 6 user stories, 25 requirements, 15 success criteria
- **[plan.md](specs/002-silver-functional-assistant/plan.md)** - 7 implementation phases, 6 design decisions, 6 risk analyses
- **[tasks.md](specs/002-silver-functional-assistant/tasks.md)** - 112 actionable tasks organized by user story
- **[research.md](specs/002-silver-functional-assistant/research.md)** - Technical decisions for Gmail, LinkedIn, MCP, Claude, Scheduler
- **[data-model.md](specs/002-silver-functional-assistant/data-model.md)** - 7 entities with validation rules
- **[quickstart.md](specs/002-silver-functional-assistant/quickstart.md)** - Complete setup and troubleshooting guide
- **[contracts/](specs/002-silver-functional-assistant/contracts/)** - 5 API contracts with operations and error handling

### Agent Skills

All Agent Skills are documented in `AI_Employee_Vault/.claude/skills/`:

- **process-actions.skill.md** - Process pending action items (enhanced)
- **send-email.skill.md** - Send email with approval workflow
- **post-linkedin.skill.md** - Post to LinkedIn with approval
- **create-plan.skill.md** - Generate Plan.md for complex tasks
- **schedule-task.skill.md** - Schedule recurring tasks

---

## ✅ Success Criteria

Silver tier is complete when all 15 success criteria are met:

- [ ] **SC-001**: Gmail Watcher detects new emails within 5 minutes with 99% reliability
- [ ] **SC-002**: Action files created with correct metadata in 100% of cases
- [ ] **SC-003**: Email drafts require approval and no email sent without explicit approval
- [ ] **SC-004**: Approved emails sent successfully within 30 seconds with 95% success rate
- [ ] **SC-005**: Multi-step tasks generate Plan.md files with clear, actionable steps in 100% of cases
- [ ] **SC-006**: Plan execution follows sequential order with checkpoint logging
- [ ] **SC-007**: LinkedIn posts require approval and no post published without explicit approval
- [ ] **SC-008**: Approved LinkedIn posts published successfully within 60 seconds with 90% success rate
- [ ] **SC-009**: All sensitive actions move to Pending_Approval/ with 100% accuracy
- [ ] **SC-010**: Approval/rejection decisions logged with timestamp and reason in 100% of cases
- [ ] **SC-011**: Scheduled watchers execute at configured intervals with 95% on-time execution rate
- [ ] **SC-012**: System handles API rate limits gracefully without crashing or losing data
- [ ] **SC-013**: OAuth tokens refreshed automatically before expiration with 99% success rate
- [ ] **SC-014**: All API credentials stored securely in .env and never exposed in logs or git
- [ ] **SC-015**: System operates on Windows, Linux, and Mac with platform-appropriate scheduling

---

## 🧪 Testing

### Run Verification Script

```bash
python AI_Employee_Vault/verify_silver.py
```

### Manual Testing

**Test Email Monitoring**:
```bash
# Send test email to your Gmail account
# Run watcher: python AI_Employee_Vault/watchers/gmail_watcher.py
# Verify action file created in Needs_Action/
```

**Test Email Sending**:
```bash
# Create email draft request in Needs_Action/
# Verify draft created in Pending_Approval/
# Approve draft (move to Approved/)
# Verify email sent and logged in Logs/
```

**Test LinkedIn Posting**:
```bash
# Create LinkedIn post request in Needs_Action/
# Verify draft created in Pending_Approval/
# Approve draft (move to Approved/)
# Verify post published on LinkedIn
```

**Test Task Planning**:
```bash
# Create complex task in Needs_Action/
# Verify Plan.md generated in Plans/
# Check plan has numbered steps with acceptance criteria
```

**Test Scheduler**:
```bash
# Start scheduler: python AI_Employee_Vault/scheduler/scheduler.py
# Wait for scheduled execution
# Check logs: tail -f AI_Employee_Vault/Logs/scheduler.log
```

---

## 🔒 Security

### Credential Management
- All API credentials stored in `config/.env` (gitignored)
- OAuth tokens refreshed automatically
- No credentials in code or logs
- Logs sanitized (show last 4 digits only)

### Approval Workflow
- All sensitive actions require explicit approval
- 24-hour timeout with auto-rejection
- Approval logging with timestamp and approver
- Configurable approval rules in Company Handbook

### Data Protection
- All data stored locally in Obsidian vault
- No cloud storage (local-first architecture)
- File permissions: readable/writable by user only
- API keys scoped to minimum required permissions

---

## 🐛 Troubleshooting

### Gmail API Issues

**Error: 401 Unauthorized**
```bash
# Refresh OAuth token
python AI_Employee_Vault/setup/gmail_auth.py --refresh
```

**Error: 429 Rate Limit**
```bash
# Reduce check frequency in config/scheduler_config.json
# Change "*/5 * * * *" to "*/10 * * * *" (every 10 minutes)
```

### LinkedIn API Issues

**Error: 401 Unauthorized**
```bash
# Re-authenticate (access token expires after 60 days)
python AI_Employee_Vault/setup/linkedin_auth.py
```

### MCP Email Server Issues

**Error: Connection refused**
```bash
# Start MCP server
cd AI_Employee_Vault/mcp
npm start
```

### Scheduler Issues

**Windows: Task not running**
```powershell
# Check Task Scheduler
schtasks /query /tn "AI Employee - Gmail Watcher"
```

**Linux/Mac: Cron not running**
```bash
# Check crontab
crontab -l | grep gmail_watcher
```

See [quickstart.md](specs/002-silver-functional-assistant/quickstart.md) for detailed troubleshooting.

---

## 🎯 Implementation Status

### Planning Phase: ✅ 100% Complete

- [x] Specification (spec.md)
- [x] Implementation Plan (plan.md)
- [x] Task List (tasks.md)
- [x] Research & Decisions (research.md)
- [x] Data Model (data-model.md)
- [x] API Contracts (contracts/)
- [x] Quick Start Guide (quickstart.md)
- [x] Quality Validation (checklists/requirements.md)

### Implementation Phase: ⏳ Ready to Start

**MVP (P1 User Stories)**: 52 tasks
- [ ] Phase 1: Setup (10 tasks)
- [ ] Phase 2: Foundational (10 tasks)
- [ ] Phase 3: Email Monitoring (10 tasks)
- [ ] Phase 4: Email Sending (12 tasks)
- [ ] Phase 5: Task Planning (12 tasks)
- [ ] Phase 6: Enhanced Approval (10 tasks)

**Full Silver Tier**: 112 tasks
- [ ] Phase 7: LinkedIn Integration (12 tasks)
- [ ] Phase 8: Scheduler (14 tasks)
- [ ] Phase 9: Integration & Testing (13 tasks)
- [ ] Phase 10: Documentation & Polish (9 tasks)

---

## 🚀 Next Steps

### For Developers

1. **Review Planning Documents**: Read spec.md, plan.md, and tasks.md
2. **Set Up API Credentials**: Gmail, LinkedIn, Claude
3. **Start Implementation**: Begin with Phase 1 (Setup)
4. **Follow Task List**: Use tasks.md as your implementation checklist
5. **Test Incrementally**: Verify each user story independently

### For Users

1. **Wait for Implementation**: Silver tier is in planning phase
2. **Prepare API Credentials**: Get Gmail, LinkedIn, Claude API access
3. **Review Features**: Understand what Silver tier will do
4. **Plan Usage**: Think about how you'll use email monitoring, LinkedIn posting, etc.

---

## 🏆 Hackathon Submission

### Tier Declaration
**Silver Tier**: Functional Assistant

### Key Features
- Gmail monitoring with priority detection
- Email sending with MCP server and approval
- LinkedIn integration with engagement tracking
- Claude reasoning loop for multi-step planning
- Enhanced approval workflow for sensitive actions
- Cross-platform scheduling (cron/Task Scheduler)

### Documentation
- ✅ Complete specification (6 user stories, 25 requirements)
- ✅ Implementation plan (7 phases, 6 design decisions)
- ✅ 112 actionable tasks organized by user story
- ✅ API contracts for all 5 services
- ✅ Setup guide with troubleshooting
- ✅ Security disclosure (credentials, approval workflow)

### Repository
- **GitHub**: https://github.com/Tahaimran56/personalAIEmployee_silverlevel
- **Branch**: 002-silver-functional-assistant
- **Bronze Tier**: https://github.com/Tahaimran56/personalAIEmployee_bronze_level

---

## 📈 Roadmap

### Silver Tier (Current)
- Gmail monitoring
- Email sending with approval
- LinkedIn integration
- Multi-step task planning
- Enhanced approval workflow
- Basic scheduling

### Gold Tier (Next)
- Odoo ERP integration
- Twitter/X integration
- Advanced analytics and reporting
- Multi-domain task orchestration
- Intelligent task prioritization
- Cross-platform notifications

### Platinum Tier (Future)
- 24/7 cloud deployment
- Multi-agent collaboration
- Production-ready scaling
- Advanced security features
- Enterprise integrations
- Mobile app

---

## 🤝 Contributing

This is a hackathon project. Contributions are welcome after the hackathon concludes.

---

## 📄 License

This project is part of the Personal AI Employee Hackathon.

---

## 🙏 Acknowledgments

- **Anthropic** for Claude Code and Claude API
- **Obsidian** for the Markdown-based knowledge management platform
- **Google** for Gmail API
- **LinkedIn** for Share API
- **SpecifyPlus** methodology for structured development

---

## 📞 Support

- **Documentation**: See `specs/002-silver-functional-assistant/`
- **Issues**: Check `AI_Employee_Vault/Logs/` for error logs
- **Troubleshooting**: See [quickstart.md](specs/002-silver-functional-assistant/quickstart.md)

---

**Built with ❤️ using Claude Code, Obsidian, and SpecifyPlus methodology**

**Status**: Planning Complete | Implementation Ready | Silver Tier 🥈
