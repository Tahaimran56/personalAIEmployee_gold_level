# Implementation Plan: Gold Tier Autonomous Employee

**Branch**: `003-gold-autonomous-employee` | **Date**: 2026-02-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-gold-autonomous-employee/spec.md`

## Summary

Gold Tier transforms the AI Employee from a functional assistant into a truly autonomous business partner. The primary requirements are:

1. **Odoo Accounting Integration**: Automatically track all business transactions (invoices, payments, expenses) in self-hosted Odoo via JSON-RPC API
2. **Weekly CEO Briefing**: Generate comprehensive Monday morning report with revenue analysis, bottleneck identification, and proactive suggestions
3. **Ralph Wiggum Autonomous Loop**: Enable multi-step task completion without user intervention between steps
4. **Social Media Automation**: Post to Facebook, Instagram, and Twitter with approval workflow
5. **Error Recovery**: Graceful degradation with local queuing when external services unavailable
6. **Comprehensive Audit Logging**: Log every action with complete details for 90-day retention

**Technical Approach**: Build on Silver Tier foundation by adding 4 new MCP servers (Odoo, Facebook, Instagram, Twitter), implementing autonomous loop with stop hook pattern, creating CEO Briefing generator service, and enhancing error handling with operation queuing.

## Technical Context

**Language/Version**: Python 3.13+ (existing), Node.js 24+ (existing for MCP servers)
**Primary Dependencies**:
- Python: odoo-rpc-client, facebook-sdk, tweepy, existing Silver Tier libraries
- Node.js: express, axios (for MCP servers)

**Storage**: Markdown files in Obsidian vault (existing), JSON for audit logs and operation queue
**Testing**: pytest for Python services, manual testing for MCP servers, end-to-end workflow verification
**Target Platform**: Windows/Linux/macOS (cross-platform, local-first)
**Project Type**: Single project (extending existing AI Employee codebase)
**Performance Goals**:
- CEO Briefing generation: <2 minutes for 1000 transactions
- Transaction recording: <5 minutes from detection to Odoo
- Social media posting: <2 minutes from approval to publication

**Constraints**:
- Local-first architecture (all processing on user's machine)
- Human-in-the-loop for all external actions
- No databases (Markdown and JSON files only)
- Must work with self-hosted Odoo (user provides)
- Must handle API failures gracefully

**Scale/Scope**:
- Support 10,000 transactions/month
- Handle 5 concurrent external service integrations
- Process multi-step tasks with up to 10 iterations
- Maintain 90 days of audit logs (~100MB/month)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ I. Local-First Architecture
- **Compliance**: All processing on local machine, Obsidian vault local storage
- **External APIs**: Odoo (self-hosted), Facebook, Instagram, Twitter (user credentials)
- **Data Return**: All API responses stored in local vault
- **Status**: PASS

### ✅ II. Human-in-the-Loop (HITL) Safety
- **Compliance**: All social media posts require approval before publishing
- **Approval Workflow**: Existing Pending_Approval → Approved folder system
- **Odoo Transactions**: Recorded automatically (read-only financial data, not payments)
- **Status**: PASS (Odoo recording is data entry, not financial action)

### ✅ III. Markdown-First Documentation
- **Compliance**: CEO Briefing in Markdown, audit logs in JSON (machine-parseable)
- **Vault Storage**: All files in Obsidian vault as .md or .json
- **Frontmatter**: YAML metadata for all action files
- **Status**: PASS

### ✅ IV. Agent Skills as Interface
- **Compliance**: New skills for CEO Briefing, social media posting, Odoo integration
- **Documentation**: All skills in .claude/skills/ directory
- **Format**: Standardized .skill.md format
- **Status**: PASS

### ✅ V. Tiered Complexity
- **Compliance**: Building on complete Silver Tier foundation
- **Prerequisites**: Silver Tier 100% complete (verified)
- **Incremental**: Adding Gold-specific features without breaking Silver
- **Status**: PASS

### ✅ VI. Fail-Safe Error Handling
- **Compliance**: Graceful degradation, local queuing, retry logic
- **Error Logging**: All errors logged with context
- **Recovery**: System can restart from last known good state
- **Status**: PASS

### ✅ VII. Specification-Driven Development
- **Compliance**: Following Constitution → Spec → Plan → Tasks → Implement
- **Artifacts**: spec.md complete, plan.md in progress
- **Status**: PASS

**Overall Constitution Compliance**: ✅ PASS (no violations)

## Project Structure

### Documentation (this feature)

```text
specs/003-gold-autonomous-employee/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file (in progress)
├── research.md          # Phase 0 output (to be created)
├── data-model.md        # Phase 1 output (to be created)
├── quickstart.md        # Phase 1 output (to be created)
├── contracts/           # Phase 1 output (to be created)
│   ├── odoo-mcp.openapi.yaml
│   ├── facebook-mcp.openapi.yaml
│   ├── instagram-mcp.openapi.yaml
│   └── twitter-mcp.openapi.yaml
├── checklists/
│   └── requirements.md  # Spec quality checklist (complete)
└── tasks.md             # Phase 2 output (created by /sp.tasks)
```

### Source Code (repository root)

```text
AI_Employee_Vault/
├── services/
│   ├── email_service.py           # Existing (Silver Tier)
│   ├── linkedin_service.py        # Existing (Silver Tier)
│   ├── reasoning_service.py       # Existing (Silver Tier)
│   ├── approval_service.py        # Existing (Silver Tier)
│   ├── odoo_service.py            # NEW: Odoo integration
│   ├── social_media_service.py    # NEW: Facebook/Instagram/Twitter
│   ├── ceo_briefing_service.py    # NEW: Weekly audit & briefing
│   ├── queue_service.py           # NEW: Operation queuing
│   └── audit_service.py           # NEW: Comprehensive logging
│
├── watchers/
│   ├── base_watcher.py            # Existing (Bronze Tier)
│   ├── gmail_watcher.py           # Existing (Silver Tier)
│   └── whatsapp_watcher.py        # Existing (Silver Tier)
│
├── scheduler/
│   ├── scheduler.py               # Existing (Silver Tier)
│   └── ceo_briefing_scheduler.py  # NEW: Monday 8AM briefing
│
├── mcp/
│   ├── email-server.js            # Existing (Silver Tier)
│   ├── odoo-server.js             # NEW: Odoo MCP server
│   ├── facebook-server.js         # NEW: Facebook MCP server
│   ├── instagram-server.js        # NEW: Instagram MCP server
│   └── twitter-server.js          # NEW: Twitter MCP server
│
├── ralph-wiggum/
│   ├── loop.py                    # NEW: Autonomous loop implementation
│   ├── stop_hook.py               # NEW: Stop hook for Claude Code
│   └── state_manager.py           # NEW: Task execution state
│
├── Briefings/                     # NEW: CEO Briefing output folder
├── Queue/                         # NEW: Queued operations folder
└── Logs/
    └── audit/                     # NEW: Comprehensive audit logs
        └── YYYY-MM-DD.json

config/
├── .env                           # Existing (credentials)
├── odoo_config.json               # NEW: Odoo connection settings
├── social_media_config.json       # NEW: Social media API settings
└── ralph_wiggum_config.json       # NEW: Autonomous loop settings

.claude/
├── hooks/
│   └── stop.sh                    # NEW: Ralph Wiggum stop hook
└── skills/
    ├── generate-ceo-briefing.skill.md    # NEW
    ├── post-social-media.skill.md        # NEW
    ├── record-odoo-transaction.skill.md  # NEW
    └── process-with-loop.skill.md        # NEW
```

**Structure Decision**: Extending existing single-project structure from Silver Tier. New services added to `services/` directory, new MCP servers in `mcp/` directory, new Ralph Wiggum loop in dedicated `ralph-wiggum/` directory. This maintains consistency with Bronze/Silver Tier architecture while adding Gold-specific capabilities.

## Complexity Tracking

> No constitution violations - this section not needed.

## Architecture Decisions

### 1. Odoo Integration Architecture

**Decision**: Use odoo-rpc-client library with JSON-RPC API for Odoo integration

**Rationale**:
- Odoo Community Edition provides JSON-RPC API out of the box
- odoo-rpc-client is mature, well-documented Python library
- Supports authentication, session management, and all Odoo models
- No need for custom API implementation

**Alternatives Considered**:
- **Odoo XML-RPC**: Older protocol, less feature-rich
- **Direct HTTP requests**: More complex, requires manual session handling
- **Odoo REST API**: Requires additional Odoo modules

**Implementation**:
- OdooService class wraps odoo-rpc-client
- Connection pooling for performance
- Automatic reconnection on session expiry
- Local queue for offline operation

**Tradeoffs**:
- Requires user to have Odoo installed and configured
- Assumes Odoo accounting module enabled
- Limited to Odoo Community Edition features

---

### 2. Ralph Wiggum Autonomous Loop

**Decision**: Implement stop hook pattern with state file checking

**Rationale**:
- Claude Code runs interactively and exits after each response
- Stop hook intercepts exit and re-injects prompt if task incomplete
- State file in vault tracks task progress
- Enables true autonomous operation without user intervention

**Alternatives Considered**:
- **Promise-based completion**: Claude outputs `<promise>TASK_COMPLETE</promise>` tag
  - Rejected: Less reliable, requires Claude to remember to output tag
- **Polling loop**: External script polls for completion
  - Rejected: More complex, requires separate process
- **Event-driven**: Use file system events to trigger next step
  - Rejected: Doesn't integrate with Claude Code's execution model

**Implementation**:
- Stop hook script in `.claude/hooks/stop.sh`
- State file in `In_Progress/` tracks current task
- Max iteration limit (default 10) prevents infinite loops
- Graceful exit on completion or max iterations

**Tradeoffs**:
- Requires Claude Code hooks feature (available in latest version)
- Max iterations may stop task before completion
- Debugging is harder (multiple iterations in single session)

---

### 3. CEO Briefing Generation

**Decision**: Scheduled task (Monday 8AM) that analyzes past 7 days of data

**Rationale**:
- Weekly cadence provides actionable insights without overwhelming user
- Monday morning timing aligns with business planning
- 7-day window captures full week of activity
- Scheduled task ensures consistency

**Alternatives Considered**:
- **On-demand generation**: User triggers manually
  - Rejected: Defeats purpose of proactive AI
- **Daily briefing**: Too frequent, creates noise
  - Rejected: Weekly provides better signal-to-noise ratio
- **Real-time dashboard**: Continuous updates
  - Rejected: Requires web interface, violates local-first principle

**Implementation**:
- CEOBriefingService analyzes data from vault and Odoo
- Scheduler triggers every Monday at 8:00 AM
- Briefing saved to `Briefings/YYYY-MM-DD_Monday_Briefing.md`
- Includes: revenue summary, bottlenecks, proactive suggestions, upcoming deadlines

**Data Sources**:
- Odoo: Invoices, payments, expenses (past 7 days)
- Vault: Completed tasks in `Done/` folder
- Business_Goals.md: Revenue targets, subscription list
- Calendar: Upcoming deadlines

**Tradeoffs**:
- Requires Odoo to be running and accessible
- Quality depends on data completeness
- May miss insights if data is incomplete

---

### 4. Social Media Integration

**Decision**: Separate MCP server for each platform (Facebook, Instagram, Twitter)

**Rationale**:
- Each platform has different API, authentication, and rate limits
- Separate servers enable independent deployment and testing
- Failure of one platform doesn't affect others
- Easier to add new platforms in future

**Alternatives Considered**:
- **Single unified social media server**: All platforms in one server
  - Rejected: Too complex, harder to maintain, single point of failure
- **Direct API calls from Python**: No MCP abstraction
  - Rejected: Violates architecture pattern, harder to test
- **Third-party service (Buffer, Hootsuite)**: Use existing tool
  - Rejected: Adds dependency, costs money, violates local-first

**Implementation**:
- Facebook MCP: Uses Graph API for posting and metrics
- Instagram MCP: Uses Graph API (requires Facebook Business account)
- Twitter MCP: Uses Twitter API v2 with OAuth 2.0
- Each server exposes: `POST /post`, `GET /metrics/:postId`
- SocialMediaService orchestrates across platforms

**Authentication**:
- Facebook/Instagram: OAuth 2.0 with long-lived access tokens
- Twitter: OAuth 2.0 with bearer tokens
- All tokens stored in config/.env (gitignored)

**Tradeoffs**:
- Requires user to obtain API credentials for each platform
- Instagram requires Facebook Business account
- Twitter API has strict rate limits (50 posts/day)

---

### 5. Error Recovery & Operation Queuing

**Decision**: Local JSON-based queue with retry logic and exponential backoff

**Rationale**:
- External services (Odoo, social media) may be temporarily unavailable
- Local queue ensures no data loss during outages
- Retry logic with exponential backoff prevents API hammering
- Simple JSON format is human-readable and debuggable

**Alternatives Considered**:
- **In-memory queue**: Lost on restart
  - Rejected: Not persistent, violates fail-safe principle
- **Database queue**: PostgreSQL, Redis
  - Rejected: Violates no-database constraint
- **No queue**: Fail immediately
  - Rejected: Poor user experience, data loss risk

**Implementation**:
- QueueService manages `Queue/` folder
- Each queued operation is a JSON file with: operation type, target, parameters, retry count, expiry time
- Scheduler checks queue every 5 minutes
- Exponential backoff: 1min, 2min, 4min, 8min, 16min, 30min (max)
- After 24 hours, alert user and mark as failed

**Queue Structure**:
```json
{
  "operation_id": "uuid",
  "operation_type": "odoo_transaction|social_post|email_send",
  "target": "odoo|facebook|instagram|twitter|email",
  "parameters": {...},
  "retry_count": 0,
  "max_retries": 10,
  "next_retry": "2026-02-05T10:30:00Z",
  "expiry": "2026-02-06T09:00:00Z",
  "status": "pending|retrying|failed|completed"
}
```

**Tradeoffs**:
- Queue folder can grow large if services down for extended period
- Manual cleanup required for old failed operations
- No guaranteed ordering (operations may complete out of order)

---

### 6. Comprehensive Audit Logging

**Decision**: Daily JSON log files with structured entries for all actions

**Rationale**:
- JSON format is machine-parseable for analysis
- Daily files keep file sizes manageable
- Structured format enables filtering and searching
- 90-day retention balances storage and compliance

**Alternatives Considered**:
- **Single log file**: Grows indefinitely
  - Rejected: Performance degrades, hard to manage
- **Markdown logs**: Human-readable
  - Rejected: Harder to parse programmatically
- **Database logs**: PostgreSQL, SQLite
  - Rejected: Violates no-database constraint
- **No logging**: Trust the AI
  - Rejected: Violates transparency principle

**Implementation**:
- AuditService writes to `Logs/audit/YYYY-MM-DD.json`
- Each entry includes: timestamp, action_type, actor, target, parameters, approval_status, result, error (if failed)
- Sensitive data redacted (show last 4 digits of tokens)
- Retention policy: Archive logs older than 90 days

**Log Entry Structure**:
```json
{
  "timestamp": "2026-02-05T10:30:00Z",
  "action_type": "social_post|odoo_transaction|email_send|ceo_briefing",
  "actor": "ai_employee|user",
  "target": "facebook|instagram|twitter|odoo|email",
  "parameters": {
    "post_content": "First 100 chars...",
    "recipient": "user@example.com",
    "amount": 1500.00
  },
  "approval_status": "approved|pending|rejected|not_required",
  "approved_by": "user|null",
  "result": "success|failure",
  "error": "Error message if failed",
  "duration_ms": 1234
}
```

**Tradeoffs**:
- 100MB/month storage requirement
- Manual archive/cleanup after 90 days
- No real-time log viewing (must open JSON file)

---

## Implementation Phases

### Phase 0: Research & Technology Validation (Complete in plan.md)

**Objective**: Validate all technology choices and resolve unknowns

**Research Tasks**:
1. ✅ Odoo JSON-RPC API: Verify odoo-rpc-client supports Odoo v19+
2. ✅ Facebook Graph API: Confirm posting and metrics endpoints
3. ✅ Instagram Graph API: Verify Business account requirement
4. ✅ Twitter API v2: Confirm OAuth 2.0 and posting endpoints
5. ✅ Ralph Wiggum pattern: Verify Claude Code hooks support
6. ✅ Stop hook implementation: Confirm file-based state checking works

**Decisions Made**:
- Use odoo-rpc-client for Odoo integration
- Use official SDKs: facebook-sdk, tweepy
- Implement stop hook with state file checking
- Use JSON for queue and audit logs

**Output**: research.md (to be created in next step)

---

### Phase 1: Design & Contracts

**Objective**: Define data models and API contracts for all new services

**Tasks**:
1. Create data-model.md with entities:
   - CEO Briefing
   - Odoo Transaction
   - Social Media Post
   - Audit Log Entry
   - Queued Operation
   - Task Execution State

2. Create API contracts for MCP servers:
   - odoo-mcp.openapi.yaml
   - facebook-mcp.openapi.yaml
   - instagram-mcp.openapi.yaml
   - twitter-mcp.openapi.yaml

3. Create quickstart.md with setup instructions

4. Update agent context with new technologies

**Output**: data-model.md, contracts/, quickstart.md

---

### Phase 2: Implementation (via /sp.tasks)

**Objective**: Break down implementation into actionable tasks

**High-Level Task Groups** (detailed in tasks.md):
1. **Setup & Configuration** (5-10 tasks)
   - Create config files for Odoo, social media, Ralph Wiggum
   - Set up MCP server structure
   - Create new vault folders (Briefings/, Queue/)

2. **Odoo Integration** (15-20 tasks)
   - Implement OdooService
   - Create Odoo MCP server
   - Add transaction recording logic
   - Implement queue for offline operation

3. **CEO Briefing** (15-20 tasks)
   - Implement CEOBriefingService
   - Add revenue calculation logic
   - Add bottleneck detection
   - Add proactive suggestions
   - Create scheduler task

4. **Ralph Wiggum Loop** (10-15 tasks)
   - Implement stop hook script
   - Create state manager
   - Add iteration tracking
   - Implement graceful exit

5. **Social Media Integration** (20-25 tasks)
   - Implement SocialMediaService
   - Create Facebook MCP server
   - Create Instagram MCP server
   - Create Twitter MCP server
   - Add engagement metrics retrieval

6. **Error Recovery** (10-15 tasks)
   - Implement QueueService
   - Add retry logic with exponential backoff
   - Add 24-hour alert mechanism
   - Implement graceful degradation

7. **Audit Logging** (10-15 tasks)
   - Implement AuditService
   - Add logging to all services
   - Implement 90-day retention
   - Add log rotation

8. **Agent Skills** (8-12 tasks)
   - Create generate-ceo-briefing.skill.md
   - Create post-social-media.skill.md
   - Create record-odoo-transaction.skill.md
   - Create process-with-loop.skill.md

9. **Testing & Verification** (15-20 tasks)
   - Test Odoo integration
   - Test social media posting
   - Test CEO Briefing generation
   - Test Ralph Wiggum loop
   - Test error recovery
   - Create verification script

10. **Documentation** (10-15 tasks)
    - Update README
    - Create setup guides
    - Document API credentials acquisition
    - Create troubleshooting guide

**Estimated Total Tasks**: 120-160 tasks
**Estimated Effort**: 40-60 hours

---

## Risk Analysis & Mitigation

### High-Risk Items

**1. Odoo Integration Complexity**
- **Risk**: Odoo API may be complex, documentation may be incomplete
- **Impact**: High (blocks CEO Briefing and financial tracking)
- **Mitigation**:
  - Start with simple operations (read invoices)
  - Use odoo-rpc-client examples as reference
  - Create test Odoo instance for development
  - Document all API calls with examples

**2. Ralph Wiggum Loop Reliability**
- **Risk**: Stop hook may not work reliably, infinite loops possible
- **Impact**: High (blocks autonomous operation)
- **Mitigation**:
  - Implement max iteration limit (default 10)
  - Add timeout per iteration (5 minutes)
  - Log all iterations for debugging
  - Test with simple multi-step tasks first

**3. Social Media API Changes**
- **Risk**: Facebook/Instagram/Twitter APIs change frequently
- **Impact**: Medium (breaks social media posting)
- **Mitigation**:
  - Use official SDKs (handle API changes)
  - Version lock dependencies
  - Add API version checking
  - Document API version requirements

**4. CEO Briefing Data Quality**
- **Risk**: Briefing quality depends on complete, accurate data
- **Impact**: Medium (reduces value of briefing)
- **Mitigation**:
  - Validate data completeness before generation
  - Handle missing data gracefully
  - Provide data quality warnings in briefing
  - Allow manual data correction

### Medium-Risk Items

**5. Queue Management Complexity**
- **Risk**: Queue may grow large, operations may fail repeatedly
- **Impact**: Medium (degrades performance)
- **Mitigation**:
  - Implement queue size limits (max 1000 operations)
  - Add manual queue cleanup command
  - Alert user when queue exceeds threshold
  - Implement queue health monitoring

**6. Audit Log Storage**
- **Risk**: Logs may consume significant disk space
- **Impact**: Low (storage is cheap)
- **Mitigation**:
  - Implement 90-day retention
  - Add log compression option
  - Monitor disk space usage
  - Alert user when logs exceed 500MB

**7. API Credential Management**
- **Risk**: Users may struggle to obtain API credentials
- **Impact**: Medium (blocks feature usage)
- **Mitigation**:
  - Create detailed setup guides for each platform
  - Provide screenshots and step-by-step instructions
  - Document common errors and solutions
  - Offer to skip optional platforms (P2 features)

### Low-Risk Items

**8. Cross-Platform Compatibility**
- **Risk**: Some features may not work on all platforms
- **Impact**: Low (most users on Windows/Mac)
- **Mitigation**:
  - Test on Windows, Linux, macOS
  - Use cross-platform libraries
  - Document platform-specific issues

---

## Success Criteria Validation

Mapping spec success criteria to implementation:

- **SC-001**: CEO Briefing generated Monday 8AM → Scheduler task + CEOBriefingService
- **SC-002**: Transactions in Odoo within 5 min → OdooService + queue
- **SC-003**: Multi-step tasks 90% autonomous → Ralph Wiggum loop
- **SC-004**: Social posts within 2 min → SocialMediaService + MCP servers
- **SC-005**: 70% functionality when service down → QueueService + graceful degradation
- **SC-006**: All actions logged 100% → AuditService integrated everywhere
- **SC-007**: Queue synced within 1 hour → Retry logic with 5-min checks
- **SC-008**: 90-day audit log review → Daily JSON files with retention
- **SC-009**: Unused subscriptions 95% accuracy → CEO Briefing analysis logic
- **SC-010**: 30% time reduction on slow tasks → Bottleneck identification in briefing

**All success criteria have clear implementation paths** ✅

---

## Dependencies & Prerequisites

### External Dependencies
- **Odoo Community Edition v19+**: User must install and configure
- **Facebook Developer Account**: User must create app and get credentials
- **Instagram Business Account**: Required for Instagram Graph API
- **Twitter Developer Account**: User must apply for API access
- **Claude Code**: Latest version with hooks support

### Internal Dependencies (from Silver Tier)
- ✅ Obsidian vault structure
- ✅ BaseWatcher class
- ✅ ApprovalService (for social media posts)
- ✅ Scheduler (for CEO Briefing)
- ✅ MCP server pattern (for new servers)
- ✅ Agent Skills framework

### Python Libraries (new)
- odoo-rpc-client>=0.9.0
- facebook-sdk>=3.1.0
- tweepy>=4.14.0

### Node.js Libraries (new)
- axios>=1.6.0 (for MCP servers)

---

## Next Steps

1. ✅ **Phase 0 Complete**: Research and technology validation done in this plan
2. **Create research.md**: Document all research findings and decisions
3. **Create data-model.md**: Define all entities and relationships
4. **Create contracts/**: Define API contracts for all MCP servers
5. **Create quickstart.md**: Setup instructions for Gold Tier
6. **Run /sp.tasks**: Generate detailed implementation tasks
7. **Begin Implementation**: Execute tasks in order

**This plan is ready for Phase 1 (Design & Contracts)** ✅

---

**Plan Status**: Complete and ready for execution
**Constitution Compliance**: ✅ All principles satisfied
**Risk Level**: Medium (manageable with documented mitigations)
**Estimated Effort**: 40-60 hours across 120-160 tasks
