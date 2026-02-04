# Implementation Plan: Silver Tier Functional Assistant

**Branch**: `002-silver-functional-assistant` | **Date**: 2026-02-04 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-silver-functional-assistant/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Silver tier extends Bronze tier's foundation by adding functional automation capabilities: Gmail monitoring for email detection, LinkedIn integration for business posts, MCP email server for sending emails with approval, Claude reasoning loop for multi-step task planning, enhanced human-in-the-loop approval workflow for sensitive actions, and basic scheduling for automated watcher execution. All functionality implemented as Agent Skills following Bronze tier architecture patterns.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**:
- google-auth, google-auth-oauthlib, google-api-python-client (Gmail API)
- linkedin-api or custom OAuth2 implementation (LinkedIn integration)
- anthropic (Claude API for reasoning loop)
- schedule (task scheduling)
- watchdog (file system monitoring, from Bronze tier)
- python-dotenv (environment variables)

**Storage**: Markdown files in Obsidian vault (no database)
**Testing**: pytest for unit tests, manual testing for end-to-end workflows, verification script for requirements
**Target Platform**: Cross-platform (Windows, Linux, Mac) with platform-specific scheduling (cron vs Task Scheduler)
**Project Type**: Single project extending Bronze tier architecture
**Performance Goals**:
- Email detection within 5 minutes of arrival (99% reliability)
- Email send within 30 seconds of approval (95% success rate)
- LinkedIn post within 60 seconds of approval (90% success rate)
- Scheduled tasks execute within 1 minute of scheduled time (95% on-time rate)

**Constraints**:
- Local-first architecture (all data in vault)
- Human-in-the-loop approval required for all sensitive actions
- API rate limits (Gmail: 250 quota units/user/second, LinkedIn: varies by endpoint)
- OAuth token refresh required (Gmail: 1 hour access token, LinkedIn: 60 days)
- No database (Markdown files only)
- Single user only (no multi-tenancy)

**Scale/Scope**:
- Single user
- ~100 emails/day monitored
- ~10 LinkedIn posts/week
- ~5 multi-step plans/week
- 3 new watchers (Gmail, LinkedIn, Scheduler)
- 5 new Agent Skills
- 3 new services (email, LinkedIn, reasoning)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Local-First Architecture ✅
- **Compliance**: All data stored in Obsidian vault locally
- **API Calls**: Gmail, LinkedIn, Claude APIs require internet but data returns to vault
- **Credentials**: Stored in .env file (gitignored), never in code
- **Status**: PASS - No cloud storage, all processing local

### Principle II: Human-in-the-Loop (HITL) Safety ✅
- **Compliance**: All sensitive actions (email send, LinkedIn post, file delete) require approval
- **Workflow**: Pending_Approval/ → user approval → execution
- **Timeout**: 24-hour auto-rejection for pending actions
- **Audit**: All actions logged with timestamp, approver, result
- **Status**: PASS - No auto-send, no auto-post without approval

### Principle III: Markdown-First Documentation ✅
- **Compliance**: All action files, plans, logs in Markdown
- **Format**: YAML frontmatter + Markdown body
- **Storage**: .md files in vault folders
- **Status**: PASS - No proprietary formats or databases

### Principle IV: Agent Skills as Interface ✅
- **Compliance**: All new functionality packaged as Agent Skills
- **Skills**: send-email.skill.md, post-linkedin.skill.md, create-plan.skill.md, schedule-task.skill.md
- **Documentation**: Each skill in .claude/skills/ with clear description, usage, workflow
- **Status**: PASS - All functionality exposed as documented skills

### Principle V: Tiered Complexity ✅
- **Compliance**: Building on Bronze tier foundation
- **Prerequisites**: Bronze tier complete (BaseWatcher, folder structure, Agent Skills)
- **Scope**: Silver tier only (no Gold/Platinum features)
- **Status**: PASS - Incremental build on Bronze tier

### Principle VI: Fail-Safe Error Handling ⚠️
- **Compliance**: Error handling required for all API calls
- **Requirements**:
  - Gmail API rate limits: pause, log, retry after reset
  - LinkedIn OAuth expiration: detect, notify, re-auth
  - Network failures: retry 3x with exponential backoff
  - Malformed files: log, quarantine, notify user
  - No silent failures
- **Status**: PASS WITH REQUIREMENTS - Must implement robust error handling in all services

### Principle VII: Specification-Driven Development ✅
- **Compliance**: Following Constitution → Spec → Plan → Tasks → Implement
- **Artifacts**: spec.md (complete), plan.md (in progress), tasks.md (next), implementation (final)
- **Status**: PASS - Following SpecifyPlus workflow

### Overall Gate Status: ✅ PASS
All principles satisfied. Proceed to Phase 0 research with focus on error handling patterns for API integrations.

## Project Structure

### Documentation (this feature)

```text
specs/002-silver-functional-assistant/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file (in progress)
├── research.md          # Phase 0 output (next)
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (API contracts)
├── checklists/
│   └── requirements.md  # Spec quality checklist (complete)
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
AI_Employee_Vault/
├── watchers/
│   ├── base_watcher.py          # Base class (from Bronze)
│   ├── filesystem_watcher.py    # File watcher (from Bronze)
│   ├── gmail_watcher.py         # NEW: Gmail monitoring
│   └── linkedin_watcher.py      # NEW: LinkedIn monitoring
│
├── services/
│   ├── email_service.py         # NEW: MCP email server integration
│   ├── linkedin_service.py      # NEW: LinkedIn API client
│   └── reasoning_service.py     # NEW: Claude reasoning loop
│
├── scheduler/
│   ├── scheduler.py             # NEW: Task scheduler
│   ├── cron_setup.sh           # NEW: Linux/Mac cron setup
│   └── task_scheduler.ps1      # NEW: Windows Task Scheduler setup
│
├── .claude/skills/
│   ├── process-actions.skill.md      # Enhanced from Bronze
│   ├── start-watcher.skill.md        # From Bronze
│   ├── update-dashboard.skill.md     # From Bronze
│   ├── send-email.skill.md           # NEW: Send email with approval
│   ├── post-linkedin.skill.md        # NEW: Post to LinkedIn
│   ├── create-plan.skill.md          # NEW: Generate Plan.md
│   └── schedule-task.skill.md        # NEW: Schedule recurring tasks
│
├── Plans/                       # NEW: Generated plan files
│   └── [task-id]-plan.md
│
├── Inbox/                       # From Bronze
├── Needs_Action/                # From Bronze
├── Pending_Approval/            # From Bronze (enhanced)
├── Approved/                    # From Bronze
├── Done/                        # From Bronze
├── Logs/                        # From Bronze (enhanced)
│
├── Dashboard.md                 # From Bronze (enhanced)
├── Company_Handbook.md          # From Bronze (enhanced)
└── verify_silver.py             # NEW: Silver tier verification script

config/
├── .env                         # NEW: API credentials (gitignored)
├── gmail_config.json            # NEW: Gmail API settings
├── linkedin_config.json         # NEW: LinkedIn API settings
└── scheduler_config.json        # NEW: Scheduling rules

tests/
├── unit/
│   ├── test_gmail_watcher.py
│   ├── test_linkedin_watcher.py
│   ├── test_email_service.py
│   ├── test_linkedin_service.py
│   ├── test_reasoning_service.py
│   └── test_scheduler.py
│
└── integration/
    ├── test_email_workflow.py
    ├── test_linkedin_workflow.py
    ├── test_planning_workflow.py
    └── test_scheduling_workflow.py
```

**Structure Decision**: Single project extending Bronze tier architecture. All new components follow the established patterns: watchers extend BaseWatcher, services are standalone modules, Agent Skills documented in .claude/skills/. Configuration files in separate config/ directory. Tests organized by type (unit vs integration).

## Complexity Tracking

No constitution violations requiring justification. All principles satisfied.

---

## Implementation Phases

### Phase 0: Research & Design ✅ COMPLETE

**Deliverables**:
- ✅ research.md - Technical decisions and best practices
- ✅ data-model.md - Entity definitions and relationships
- ✅ contracts/ - API contracts for all services
- ✅ quickstart.md - Setup and usage guide

**Key Decisions**:
- Gmail API with OAuth2 for email monitoring
- LinkedIn Share API for posting
- MCP + nodemailer for email sending
- Claude API for reasoning loop
- Python schedule + native persistence for scheduling
- Tiered error handling with logging

---

### Phase 1: Gmail Integration (Priority: P1)

**Duration**: 2-3 days

**Tasks**:
1. Implement Gmail OAuth2 authentication flow
2. Create gmail_watcher.py extending BaseWatcher
3. Implement email detection and action file creation
4. Add priority detection logic
5. Implement duplicate prevention (processed_emails.json)
6. Add error handling for rate limits and auth failures
7. Create unit tests for Gmail Watcher
8. Create integration test for end-to-end email detection
9. Document gmail-watcher.skill.md

**Acceptance Criteria**:
- Gmail Watcher detects new emails within 5 minutes
- Action files created with correct metadata
- Priority detection works for urgent keywords
- No duplicate action files for same email
- Rate limit errors handled gracefully
- All tests pass

**Dependencies**: None (builds on Bronze tier BaseWatcher)

---

### Phase 2: Email Sending Service (Priority: P1)

**Duration**: 2-3 days

**Tasks**:
1. Set up MCP email server with nodemailer
2. Implement email_service.py for draft composition
3. Add email validation (format + DNS check)
4. Implement approval workflow integration
5. Add SMTP sending with OAuth2
6. Implement retry logic for transient failures
7. Add email logging to Logs/
8. Create unit tests for email service
9. Create integration test for end-to-end email send
10. Document send-email.skill.md

**Acceptance Criteria**:
- Draft emails created in Pending_Approval/
- Approval required before sending
- Emails sent within 30 seconds of approval
- SMTP errors handled with retry logic
- All sent emails logged
- All tests pass

**Dependencies**: Phase 1 (Gmail auth setup)

---

### Phase 3: LinkedIn Integration (Priority: P2)

**Duration**: 2-3 days

**Tasks**:
1. Implement LinkedIn OAuth2 authentication flow
2. Create linkedin_service.py for post composition
3. Implement post validation (length, hashtags)
4. Add approval workflow integration
5. Implement LinkedIn Share API posting
6. Add engagement metrics fetching
7. Add post logging to Logs/
8. Create unit tests for LinkedIn service
9. Create integration test for end-to-end post publish
10. Document post-linkedin.skill.md

**Acceptance Criteria**:
- Draft posts created in Pending_Approval/
- Approval required before publishing
- Posts published within 60 seconds of approval
- Content validation works (3000 char limit)
- Engagement metrics logged
- All tests pass

**Dependencies**: Phase 2 (approval workflow patterns established)

---

### Phase 4: Claude Reasoning Loop (Priority: P1)

**Duration**: 2-3 days

**Tasks**:
1. Implement reasoning_service.py with Claude API
2. Create structured prompt template for plan generation
3. Implement plan parsing and validation
4. Create Plan.md file generation
5. Implement step execution logic
6. Add checkpoint logging after each step
7. Implement failure handling and pause logic
8. Create unit tests for reasoning service
9. Create integration test for end-to-end planning
10. Document create-plan.skill.md

**Acceptance Criteria**:
- Complex tasks generate Plan.md files
- Plans have 1-10 steps with acceptance criteria
- Steps execute sequentially with logging
- Failures pause execution and notify user
- All tests pass

**Dependencies**: None (independent service)

---

### Phase 5: Scheduler Service (Priority: P2)

**Duration**: 2-3 days

**Tasks**:
1. Implement scheduler.py with Python schedule library
2. Add platform detection (Windows/Linux/Mac)
3. Create cron_setup.sh for Linux/Mac
4. Create task_scheduler.ps1 for Windows
5. Implement schedule persistence (scheduler_config.json)
6. Add execution logging
7. Implement graceful shutdown (SIGTERM handler)
8. Create unit tests for scheduler
9. Create integration test for scheduled execution
10. Document schedule-task.skill.md

**Acceptance Criteria**:
- Watchers run on schedule (configurable intervals)
- Platform-specific persistence works
- Schedules survive system restart
- Execution logs show scheduled runs
- All tests pass

**Dependencies**: Phases 1-4 (watchers to schedule)

---

### Phase 6: Enhanced Approval Workflow (Priority: P1)

**Duration**: 1-2 days

**Tasks**:
1. Extend approval workflow from Bronze tier
2. Add approval rules for email send, LinkedIn post, file delete
3. Implement 24-hour timeout with auto-rejection
4. Add approval logging with timestamp and approver
5. Update Company_Handbook.md with new approval rules
6. Create unit tests for approval workflow
7. Create integration test for approval/rejection flows
8. Update process-actions.skill.md

**Acceptance Criteria**:
- All sensitive actions move to Pending_Approval/
- Approval/rejection logged with timestamp
- 24-hour timeout works correctly
- Rejected actions archived with reason
- All tests pass

**Dependencies**: Phases 2-3 (email and LinkedIn services)

---

### Phase 7: Integration & Testing (Priority: P1)

**Duration**: 2-3 days

**Tasks**:
1. Run all unit tests and fix failures
2. Run all integration tests and fix failures
3. Test end-to-end workflows manually
4. Create verify_silver.py verification script
5. Update Dashboard.md with Silver tier metrics
6. Update README.md with Silver tier features
7. Test on all platforms (Windows, Linux, Mac)
8. Performance testing (email detection latency, send latency)
9. Load testing (100 emails, 10 posts)
10. Security audit (credential storage, approval workflow)

**Acceptance Criteria**:
- All unit tests pass (100% pass rate)
- All integration tests pass (100% pass rate)
- verify_silver.py passes all checks
- End-to-end workflows work on all platforms
- Performance goals met (see Technical Context)
- Security audit passes

**Dependencies**: Phases 1-6 (all components complete)

---

## Design Decisions

### Decision 1: Gmail API vs IMAP

**Options Considered**:
- Gmail API with OAuth2
- IMAP with app password
- Email forwarding to local server

**Decision**: Gmail API with OAuth2

**Rationale**:
- Structured access to email data (JSON format)
- Rate limit information in API responses
- OAuth2 more secure than app passwords
- Official Python client library well-maintained
- Better error handling and retry logic

**Trade-offs**:
- Requires OAuth2 setup (more complex initial setup)
- API quota limits (but sufficient for Silver tier)
- Internet dependency (but required anyway for email)

---

### Decision 2: MCP Email Server vs Direct SMTP

**Options Considered**:
- Custom MCP server with nodemailer
- Direct SMTP from Python (smtplib)
- Third-party email service (SendGrid, Mailgun)

**Decision**: Custom MCP server with nodemailer

**Rationale**:
- MCP provides standardized interface for Claude
- nodemailer is mature and feature-rich
- Consistent with MCP architecture pattern
- Supports OAuth2, HTML, attachments
- Local-first (no third-party service)

**Trade-offs**:
- Requires Node.js installation
- Additional process to manage
- More complex than direct SMTP

---

### Decision 3: LinkedIn Official API vs Unofficial Library

**Options Considered**:
- Official LinkedIn Share API with OAuth2
- Unofficial linkedin-api library (scraping)
- Selenium browser automation

**Decision**: Official LinkedIn Share API with OAuth2

**Rationale**:
- Complies with LinkedIn Terms of Service
- Stable and supported by LinkedIn
- OAuth2 provides secure authentication
- Less likely to break with LinkedIn UI changes

**Trade-offs**:
- Requires app approval from LinkedIn
- Access token expires after 60 days (re-auth needed)
- Rate limits not publicly documented

---

### Decision 4: Claude API vs Local LLM

**Options Considered**:
- Claude API (Sonnet 4.5)
- Local LLM (Ollama, LLaMA)
- GPT-4 API

**Decision**: Claude API (Sonnet 4.5)

**Rationale**:
- Strong reasoning capabilities for planning
- Already using Claude Code (consistency)
- 200K context window (sufficient for complex tasks)
- Prompt caching reduces costs
- No GPU required (local LLM would need GPU)

**Trade-offs**:
- Requires internet connectivity
- API costs (but manageable for Silver tier)
- Dependency on external service

---

### Decision 5: Python schedule + Native Persistence

**Options Considered**:
- Python schedule library only
- Native scheduler only (cron/Task Scheduler)
- APScheduler (advanced Python scheduler)
- Celery (distributed task queue)

**Decision**: Python schedule + native persistence

**Rationale**:
- Python schedule simple and cross-platform
- Native persistence ensures survival across reboots
- Hybrid approach: Python for runtime, native for startup
- No message broker required (Celery overkill)
- Platform detection handles Windows/Linux/Mac

**Trade-offs**:
- Two systems to manage (Python + native)
- Platform-specific setup scripts required
- More complex than single solution

---

### Decision 6: Markdown Files vs Database

**Options Considered**:
- Markdown files with YAML frontmatter
- SQLite database
- JSON files

**Decision**: Markdown files with YAML frontmatter

**Rationale**:
- Consistent with Bronze tier and constitution
- Human-readable and editable
- Version-controllable with Git
- No database setup required
- Obsidian-native format

**Trade-offs**:
- Slower queries than database
- No ACID transactions
- Manual file locking required for concurrent access

---

## Risk Analysis

### Risk 1: API Rate Limits

**Probability**: Medium
**Impact**: Medium
**Mitigation**:
- Implement exponential backoff for rate limit errors
- Monitor quota usage in logs
- Reduce check frequency if limits hit
- Cache API responses where possible

**Contingency**:
- Increase check interval (5 min → 10 min)
- Implement request queuing
- Notify user of rate limit issues

---

### Risk 2: OAuth Token Expiration

**Probability**: High (LinkedIn: 60 days)
**Impact**: High (service stops working)
**Mitigation**:
- Implement automatic token refresh (Gmail)
- Detect token expiry proactively
- Notify user 7 days before expiry
- Provide re-authentication link

**Contingency**:
- Clear error messages with re-auth instructions
- Pause affected services until re-auth
- Log token expiry events

---

### Risk 3: Email/Post Approval Bottleneck

**Probability**: Medium
**Impact**: Medium
**Mitigation**:
- 24-hour timeout with auto-rejection
- Clear approval notifications in Dashboard
- Email/Slack notifications for pending approvals (future)

**Contingency**:
- Increase timeout to 48 hours if needed
- Implement approval delegation (future)
- Add approval history for audit

---

### Risk 4: Scheduler Reliability

**Probability**: Low
**Impact**: High (watchers don't run)
**Mitigation**:
- Use native scheduler for persistence
- Implement watchdog process monitoring
- Log all scheduled executions
- Alert on missed executions

**Contingency**:
- Manual watcher execution as fallback
- Systemd/Task Scheduler auto-restart
- Monitoring dashboard for schedule health

---

### Risk 5: API Service Outages

**Probability**: Low
**Impact**: High (service unavailable)
**Mitigation**:
- Implement retry logic with exponential backoff
- Detect service outages vs auth errors
- Queue operations for retry
- Log outage events

**Contingency**:
- Graceful degradation (continue other services)
- User notification of outage
- Automatic retry when service recovers

---

### Risk 6: Data Loss (File Corruption)

**Probability**: Low
**Impact**: High
**Mitigation**:
- Atomic file writes (write to temp, then rename)
- Validate YAML frontmatter before write
- Backup files before modification
- Git version control

**Contingency**:
- Quarantine corrupted files
- Restore from Git history
- Manual recovery from logs

---

## Deployment Strategy

### Development Environment
- Local development on Windows/Linux/Mac
- Git branch: 002-silver-functional-assistant
- Testing with test Gmail/LinkedIn accounts

### Testing Strategy
- Unit tests: pytest for all components
- Integration tests: End-to-end workflows
- Manual testing: Real email/LinkedIn accounts
- Verification script: verify_silver.py

### Rollout Plan
1. Phase 1-2: Gmail + Email (core functionality)
2. Phase 3: LinkedIn (nice-to-have)
3. Phase 4: Reasoning (core functionality)
4. Phase 5: Scheduler (automation)
5. Phase 6: Enhanced approval (safety)
6. Phase 7: Integration testing

### Rollback Plan
- Git revert to Bronze tier if critical issues
- Disable individual services via config
- Manual watcher execution as fallback

---

## Monitoring & Observability

### Logging
- All watchers log to AI_Employee_Vault/Logs/
- Log format: timestamp, level, component, message
- Log retention: 90 days
- Log rotation: Daily

### Metrics
- Email detection latency (target: <5 min)
- Email send latency (target: <30 sec)
- LinkedIn post latency (target: <60 sec)
- Scheduled execution on-time rate (target: >95%)
- API error rates
- Approval workflow metrics

### Alerts
- OAuth token expiry (7 days before)
- API rate limits hit
- Scheduler missed execution
- Service failures (3 consecutive)

### Dashboard Updates
- Total emails processed
- Total emails sent
- Total LinkedIn posts
- Total plans generated
- Approval pending count
- Last watcher execution times

---

## Success Criteria

Silver tier is complete when:
- ✅ All 15 success criteria from spec.md met
- ✅ All unit tests pass (100%)
- ✅ All integration tests pass (100%)
- ✅ verify_silver.py passes all checks
- ✅ End-to-end workflows tested on all platforms
- ✅ Documentation complete (README, quickstart, skills)
- ✅ Performance goals met (see Technical Context)
- ✅ Security audit passes

---

## Next Steps

After completing Silver tier:
1. Run verify_silver.py to confirm all requirements met
2. Update README.md with Silver tier features
3. Create demo video showing key workflows
4. Commit to Git with detailed message
5. Push to GitHub repository
6. Prepare for Gold tier (Odoo, Twitter, advanced features)

---

**Plan Status**: ✅ COMPLETE - Ready for Phase 2 (Task Generation)
**Next Command**: `/sp.tasks` to generate actionable task list
