# Feature Specification: Silver Tier Functional Assistant

**Feature Branch**: `002-silver-functional-assistant`
**Created**: 2026-02-04
**Status**: Draft
**Input**: User description: "Implement Silver tier Functional Assistant: Add Gmail Watcher for email monitoring, LinkedIn integration for automated business posts, MCP email server for sending emails with approval, Claude reasoning loop that creates Plan.md files for multi-step tasks, human-in-the-loop approval workflow for sensitive actions, and basic scheduling via cron or Task Scheduler. All functionality must be implemented as Agent Skills following Bronze tier architecture."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Email Monitoring and Response (Priority: P1)

As a busy professional, I want the AI Employee to monitor my Gmail inbox and automatically detect important emails so I can respond quickly without constantly checking my email.

**Why this priority**: Email monitoring is the foundation of functional automation. It enables the AI to be proactive rather than reactive, and provides immediate value by reducing email management overhead.

**Independent Test**: Can be fully tested by sending test emails to the monitored Gmail account and verifying that action files are created in Needs_Action/ with correct metadata (sender, subject, priority, timestamp).

**Acceptance Scenarios**:

1. **Given** Gmail Watcher is running, **When** a new email arrives with subject "URGENT: Client meeting", **Then** an action file is created in Needs_Action/ with priority=urgent within 5 minutes
2. **Given** Gmail Watcher is running, **When** a new email arrives with an attachment, **Then** the action file includes attachment metadata (filename, size, type)
3. **Given** Gmail Watcher is running, **When** multiple emails arrive simultaneously, **Then** each email gets its own action file with unique IDs
4. **Given** an email has been processed, **When** the same email is checked again, **Then** no duplicate action file is created

---

### User Story 2 - Email Sending with Approval (Priority: P1)

As a professional who values accuracy, I want the AI Employee to draft email responses for me and require my approval before sending, so I maintain control over all outgoing communications.

**Why this priority**: Email sending is a sensitive action that requires human oversight. This story delivers immediate value by automating email composition while maintaining safety through approval workflow.

**Independent Test**: Can be fully tested by creating an action file requesting an email to be sent, verifying that a draft is created in Pending_Approval/, approving it, and confirming the email is sent and logged.

**Acceptance Scenarios**:

1. **Given** an action file requests sending an email, **When** Claude processes it, **Then** a draft email is created in Pending_Approval/ with subject, body, and recipient
2. **Given** a draft email is in Pending_Approval/, **When** user approves it, **Then** the email is sent via MCP email server and logged in Logs/
3. **Given** a draft email is in Pending_Approval/, **When** user rejects it, **Then** the draft is moved to Done/ with status=rejected and no email is sent
4. **Given** an email send fails, **When** the error occurs, **Then** the failure is logged with error details and user is notified

---

### User Story 3 - Multi-Step Task Planning (Priority: P1)

As someone who delegates complex tasks, I want the AI Employee to break down multi-step requests into actionable plans so I can review the approach before execution begins.

**Why this priority**: Complex task handling is what differentiates a functional assistant from a simple automation tool. This enables the AI to handle sophisticated workflows that require reasoning and planning.

**Independent Test**: Can be fully tested by creating an action file with a complex task (e.g., "Research competitors and prepare summary report"), verifying that a Plan.md file is generated with step-by-step breakdown, and confirming the plan is human-readable and actionable.

**Acceptance Scenarios**:

1. **Given** an action file contains a multi-step task, **When** Claude processes it, **Then** a Plan.md file is created in Plans/ with numbered steps and acceptance criteria
2. **Given** a Plan.md exists, **When** execution begins, **Then** each step is executed in order with checkpoint logging
3. **Given** a plan step fails, **When** the failure occurs, **Then** execution pauses and user is notified with failure details
4. **Given** a plan is complete, **When** all steps succeed, **Then** the plan is marked complete and results are summarized in Dashboard

---

### User Story 4 - LinkedIn Business Posts (Priority: P2)

As a business professional, I want the AI Employee to draft and post LinkedIn updates on my behalf (with approval) so I can maintain consistent social media presence without manual effort.

**Why this priority**: LinkedIn automation provides business value but is less critical than email handling. It's a nice-to-have feature that enhances professional presence.

**Independent Test**: Can be fully tested by creating an action file requesting a LinkedIn post, verifying the draft is created in Pending_Approval/, approving it, and confirming the post appears on LinkedIn with correct content.

**Acceptance Scenarios**:

1. **Given** an action file requests a LinkedIn post, **When** Claude processes it, **Then** a draft post is created in Pending_Approval/ with content and hashtags
2. **Given** a draft LinkedIn post is approved, **When** the post is published, **Then** it appears on the user's LinkedIn profile and is logged with post ID
3. **Given** a LinkedIn post fails to publish, **When** the error occurs, **Then** the failure is logged and user is notified with retry option
4. **Given** a LinkedIn post is published, **When** engagement metrics are available, **Then** they are logged (views, likes, comments)

---

### User Story 5 - Scheduled Automation (Priority: P2)

As someone who wants hands-free operation, I want the AI Employee's watchers to run automatically on a schedule so I don't have to manually start them each time.

**Why this priority**: Scheduling enables true automation but is less critical than core functionality. The system can work without it (manual execution), but scheduling improves user experience significantly.

**Independent Test**: Can be fully tested by configuring a watcher to run every 10 minutes, waiting for scheduled execution, and verifying that the watcher runs automatically and logs execution times.

**Acceptance Scenarios**:

1. **Given** Gmail Watcher is scheduled to run every 5 minutes, **When** the schedule triggers, **Then** the watcher executes and logs the execution time
2. **Given** multiple watchers are scheduled, **When** schedules overlap, **Then** each watcher runs independently without conflicts
3. **Given** a scheduled task fails, **When** the failure occurs, **Then** the error is logged and the schedule continues for next execution
4. **Given** the system restarts, **When** it comes back online, **Then** all schedules are restored and continue running

---

### User Story 6 - Enhanced Approval Workflow (Priority: P1)

As a security-conscious user, I want all sensitive actions (email send, LinkedIn post, file delete) to require my explicit approval so the AI never takes risky actions without my consent.

**Why this priority**: Safety is paramount. This story ensures the AI operates within safe boundaries and never performs actions that could have negative consequences without human oversight.

**Independent Test**: Can be fully tested by triggering various sensitive actions (email send, LinkedIn post, file delete), verifying they all move to Pending_Approval/, and confirming that no action executes without approval.

**Acceptance Scenarios**:

1. **Given** an action is classified as sensitive, **When** Claude processes it, **Then** it is moved to Pending_Approval/ with clear description of what will happen
2. **Given** an action is in Pending_Approval/, **When** user approves it, **Then** the action executes and is logged with approval timestamp
3. **Given** an action is in Pending_Approval/, **When** user rejects it, **Then** the action is cancelled and logged with rejection reason
4. **Given** an action has been pending for 24 hours, **When** the timeout occurs, **Then** the action is auto-rejected and user is notified

---

### Edge Cases

- What happens when Gmail API rate limits are hit? (System should pause, log the rate limit, and retry after the limit resets)
- How does the system handle emails with very large attachments (>25MB)? (Log attachment metadata but don't download; notify user)
- What happens when LinkedIn OAuth token expires? (Detect expiration, notify user, provide re-authentication link)
- How does the system handle malformed action files? (Log error, move to Done/ with status=error, notify user)
- What happens when multiple users approve/reject the same action simultaneously? (First action wins, log conflict, notify other users)
- How does the system handle network failures during email send? (Retry up to 3 times with exponential backoff, then fail and notify user)
- What happens when a Plan.md step depends on external data that's unavailable? (Pause execution, log dependency issue, notify user)
- How does the system handle timezone differences for scheduling? (Use UTC internally, convert to user's local timezone for display)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST monitor Gmail inbox for new emails at configurable intervals (default: 5 minutes)
- **FR-002**: System MUST create action files for each new email with metadata: sender, subject, body preview, timestamp, priority, attachment info
- **FR-003**: System MUST detect priority keywords (URGENT, ASAP, IMPORTANT) and set action file priority accordingly
- **FR-004**: System MUST prevent duplicate action files for the same email (track processed email IDs)
- **FR-005**: System MUST compose draft emails based on action file instructions
- **FR-006**: System MUST require approval before sending any email
- **FR-007**: System MUST send approved emails via MCP email server with support for HTML formatting and attachments
- **FR-008**: System MUST log all sent emails with timestamp, recipient, subject, and status
- **FR-009**: System MUST detect multi-step tasks and generate Plan.md files with step-by-step breakdown
- **FR-010**: System MUST execute plans sequentially with checkpoint logging after each step
- **FR-011**: System MUST pause plan execution on step failure and notify user
- **FR-012**: System MUST compose draft LinkedIn posts based on action file instructions
- **FR-013**: System MUST require approval before posting to LinkedIn
- **FR-014**: System MUST post approved content to LinkedIn via OAuth2 API
- **FR-015**: System MUST log all LinkedIn posts with timestamp, content, post ID, and engagement metrics
- **FR-016**: System MUST classify actions as sensitive or non-sensitive based on configurable rules
- **FR-017**: System MUST move all sensitive actions to Pending_Approval/ folder
- **FR-018**: System MUST execute approved actions and log approval timestamp and approver
- **FR-019**: System MUST cancel rejected actions and log rejection reason
- **FR-020**: System MUST support scheduled execution of watchers via cron (Linux/Mac) or Task Scheduler (Windows)
- **FR-021**: System MUST detect platform (Windows/Linux/Mac) and use appropriate scheduling mechanism
- **FR-022**: System MUST log all scheduled executions with timestamp and status
- **FR-023**: System MUST handle API rate limits gracefully with exponential backoff retry
- **FR-024**: System MUST store API credentials securely in .env file (never in code or git)
- **FR-025**: System MUST refresh OAuth tokens automatically when they expire

### Key Entities

- **Email Action**: Represents an email detected by Gmail Watcher. Attributes: email_id, sender, recipient, subject, body_preview, timestamp, priority, attachments[], processed_status
- **Draft Email**: Represents an email pending approval. Attributes: draft_id, recipient, subject, body, attachments[], created_timestamp, approval_status
- **LinkedIn Post**: Represents a LinkedIn post pending or published. Attributes: post_id, content, hashtags[], created_timestamp, published_timestamp, approval_status, engagement_metrics
- **Plan**: Represents a multi-step task plan. Attributes: plan_id, task_description, steps[], current_step, status, created_timestamp, completed_timestamp
- **Plan Step**: Represents a single step in a plan. Attributes: step_number, description, acceptance_criteria, status, started_timestamp, completed_timestamp, error_message
- **Approval Request**: Represents an action requiring approval. Attributes: request_id, action_type, action_description, created_timestamp, approval_status, approver, approval_timestamp, rejection_reason
- **Schedule**: Represents a scheduled task. Attributes: schedule_id, task_name, cron_expression, last_execution, next_execution, status, execution_count

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Gmail Watcher detects new emails within 5 minutes of arrival with 99% reliability
- **SC-002**: Action files are created with correct metadata (sender, subject, priority) in 100% of cases
- **SC-003**: Email drafts require approval and no email is sent without explicit user approval
- **SC-004**: Approved emails are sent successfully within 30 seconds with 95% success rate
- **SC-005**: Multi-step tasks generate Plan.md files with clear, actionable steps in 100% of cases
- **SC-006**: Plan execution follows sequential order with checkpoint logging after each step
- **SC-007**: LinkedIn posts require approval and no post is published without explicit user approval
- **SC-008**: Approved LinkedIn posts are published successfully within 60 seconds with 90% success rate
- **SC-009**: All sensitive actions (email send, LinkedIn post, file delete) move to Pending_Approval/ with 100% accuracy
- **SC-010**: Approval/rejection decisions are logged with timestamp and reason in 100% of cases
- **SC-011**: Scheduled watchers execute at configured intervals with 95% on-time execution rate
- **SC-012**: System handles API rate limits gracefully without crashing or losing data
- **SC-013**: OAuth tokens are refreshed automatically before expiration with 99% success rate
- **SC-014**: All API credentials are stored securely in .env and never exposed in logs or git
- **SC-015**: System operates on Windows, Linux, and Mac with platform-appropriate scheduling

## Assumptions

- User has valid Gmail API credentials (OAuth2 client ID and secret)
- User has valid LinkedIn API credentials (OAuth2 client ID and secret)
- User has valid Claude API key
- User has Python 3.13+ installed
- User has Obsidian vault set up from Bronze tier
- User has internet connectivity for API calls
- User will manually approve/reject actions within 24 hours
- Gmail inbox has fewer than 10,000 unread emails (initial sync)
- LinkedIn API rate limits allow at least 10 posts per day
- User's email provider allows SMTP/IMAP access via OAuth2

## Dependencies

- Bronze tier implementation (BaseWatcher, folder structure, Agent Skills)
- Gmail API (google-auth, google-api-python-client)
- LinkedIn API (linkedin-api or custom OAuth2 implementation)
- Claude API (anthropic Python SDK)
- MCP email server (custom implementation or existing MCP server)
- Python schedule library for task scheduling
- Platform-specific scheduling (cron for Linux/Mac, Task Scheduler for Windows)

## Out of Scope

- Calendar integration (reserved for Gold tier)
- Slack integration (reserved for Gold tier)
- Advanced analytics and reporting (reserved for Gold tier)
- Multi-user support (single user only for Silver tier)
- Mobile app or web interface (CLI/Obsidian only)
- Email filtering rules (process all emails equally)
- LinkedIn analytics dashboard (basic logging only)
- Automated email responses without approval (all emails require approval)
- Voice or video message handling (text only)
