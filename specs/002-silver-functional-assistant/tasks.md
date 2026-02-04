# Tasks: Silver Tier Functional Assistant

**Input**: Design documents from `/specs/002-silver-functional-assistant/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Tests are NOT included in this task list as they were not explicitly requested in the specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Based on plan.md, this project extends Bronze tier architecture:
- Watchers: `AI_Employee_Vault/watchers/`
- Services: `AI_Employee_Vault/services/`
- Skills: `AI_Employee_Vault/.claude/skills/`
- Config: `config/`
- Tests: `tests/unit/` and `tests/integration/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency installation

- [ ] T001 Install Python dependencies: google-auth, google-auth-oauthlib, google-api-python-client, linkedin-api, anthropic, schedule, python-dotenv
- [ ] T002 Install Node.js dependencies for MCP server in AI_Employee_Vault/mcp/
- [ ] T003 [P] Create config/ directory with .env template
- [ ] T004 [P] Create AI_Employee_Vault/services/ directory
- [ ] T005 [P] Create AI_Employee_Vault/scheduler/ directory
- [ ] T006 [P] Create AI_Employee_Vault/Plans/ directory
- [ ] T007 [P] Create AI_Employee_Vault/.state/ directory for tracking files
- [ ] T008 [P] Create tests/unit/ and tests/integration/ directories
- [ ] T009 Add config/.env to .gitignore
- [ ] T010 Create config/.env.template with all required API credential placeholders

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T011 Create AI_Employee_Vault/setup/ directory for authentication scripts
- [ ] T012 [P] Implement gmail_auth.py in AI_Employee_Vault/setup/ for OAuth2 flow
- [ ] T013 [P] Implement linkedin_auth.py in AI_Employee_Vault/setup/ for OAuth2 flow
- [ ] T014 [P] Create AI_Employee_Vault/.state/processed_emails.json for duplicate prevention
- [ ] T015 [P] Update Company_Handbook.md with Silver tier approval rules
- [ ] T016 Extend BaseWatcher class with error handling patterns from research.md
- [ ] T017 [P] Create config/gmail_config.json with watcher settings
- [ ] T018 [P] Create config/linkedin_config.json with service settings
- [ ] T019 [P] Create config/scheduler_config.json with schedule definitions
- [ ] T020 [P] Create config/mcp_email_server.json with SMTP settings

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Email Monitoring and Response (Priority: P1) 🎯 MVP

**Goal**: Monitor Gmail inbox and automatically detect important emails, creating action files in Needs_Action/

**Independent Test**: Send test email to monitored Gmail account, verify action file created in Needs_Action/ with correct metadata (sender, subject, priority, timestamp) within 5 minutes

### Implementation for User Story 1

- [ ] T021 [P] [US1] Create gmail_watcher.py extending BaseWatcher in AI_Employee_Vault/watchers/
- [ ] T022 [P] [US1] Implement get_gmail_service() function with OAuth2 credentials in gmail_watcher.py
- [ ] T023 [US1] Implement check_new_emails() method to fetch unread emails via Gmail API in gmail_watcher.py
- [ ] T024 [US1] Implement detect_priority() method with keyword matching (URGENT, ASAP, IMPORTANT) in gmail_watcher.py
- [ ] T025 [US1] Implement create_action_file() method to generate Markdown files in Needs_Action/ in gmail_watcher.py
- [ ] T026 [US1] Implement duplicate prevention using processed_emails.json in gmail_watcher.py
- [ ] T027 [US1] Add error handling for Gmail API rate limits (429) with exponential backoff in gmail_watcher.py
- [ ] T028 [US1] Add error handling for OAuth token refresh (401) in gmail_watcher.py
- [ ] T029 [US1] Add logging to AI_Employee_Vault/Logs/gmail_watcher.log in gmail_watcher.py
- [ ] T030 [US1] Create gmail-watcher.skill.md in AI_Employee_Vault/.claude/skills/ with usage documentation

**Checkpoint**: At this point, User Story 1 should be fully functional - Gmail Watcher detects emails and creates action files

---

## Phase 4: User Story 2 - Email Sending with Approval (Priority: P1)

**Goal**: Draft email responses and require approval before sending, maintaining control over all outgoing communications

**Independent Test**: Create action file requesting email send, verify draft created in Pending_Approval/, approve it, confirm email sent and logged in Logs/

### Implementation for User Story 2

- [ ] T031 [P] [US2] Create email_service.py in AI_Employee_Vault/services/
- [ ] T032 [P] [US2] Set up MCP email server with nodemailer in AI_Employee_Vault/mcp/server.js
- [ ] T033 [US2] Implement compose_draft_email() function in email_service.py
- [ ] T034 [US2] Implement validate_email() function with format and DNS checking in email_service.py
- [ ] T035 [US2] Implement create_draft_file() to generate draft in Pending_Approval/ in email_service.py
- [ ] T036 [US2] Implement send_email() function with MCP server integration in email_service.py
- [ ] T037 [US2] Add SMTP OAuth2 configuration in MCP server (server.js)
- [ ] T038 [US2] Implement retry logic for transient SMTP failures (421, 450) in email_service.py
- [ ] T039 [US2] Implement email logging to AI_Employee_Vault/Logs/ in email_service.py
- [ ] T040 [US2] Add error handling for permanent failures (550, 552) in email_service.py
- [ ] T041 [US2] Create send-email.skill.md in AI_Employee_Vault/.claude/skills/ with usage documentation
- [ ] T042 [US2] Update process-actions.skill.md to handle email send requests

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - emails can be detected and sent with approval

---

## Phase 5: User Story 3 - Multi-Step Task Planning (Priority: P1)

**Goal**: Break down multi-step requests into actionable plans for review before execution begins

**Independent Test**: Create action file with complex task (e.g., "Research competitors and prepare summary report"), verify Plan.md file generated in Plans/ with step-by-step breakdown

### Implementation for User Story 3

- [ ] T043 [P] [US3] Create reasoning_service.py in AI_Employee_Vault/services/
- [ ] T044 [P] [US3] Create plan_template.md in AI_Employee_Vault/templates/ with plan structure
- [ ] T045 [US3] Implement generate_plan() function with Claude API integration in reasoning_service.py
- [ ] T046 [US3] Implement structured prompt template for plan generation in reasoning_service.py
- [ ] T047 [US3] Implement parse_plan_response() to extract steps from Claude response in reasoning_service.py
- [ ] T048 [US3] Implement create_plan_file() to generate Plan.md in Plans/ directory in reasoning_service.py
- [ ] T049 [US3] Implement execute_plan_step() function for step-by-step execution in reasoning_service.py
- [ ] T050 [US3] Implement validate_plan_completion() to check all steps completed in reasoning_service.py
- [ ] T051 [US3] Add error handling for Claude API failures (401, 429, 500) in reasoning_service.py
- [ ] T052 [US3] Add checkpoint logging after each plan step in reasoning_service.py
- [ ] T053 [US3] Create create-plan.skill.md in AI_Employee_Vault/.claude/skills/ with usage documentation
- [ ] T054 [US3] Update process-actions.skill.md to detect multi-step tasks and trigger plan generation

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently - complex tasks generate plans

---

## Phase 6: User Story 6 - Enhanced Approval Workflow (Priority: P1)

**Goal**: Ensure all sensitive actions (email send, LinkedIn post, file delete) require explicit approval

**Independent Test**: Trigger various sensitive actions (email send, LinkedIn post, file delete), verify they all move to Pending_Approval/, confirm no action executes without approval

### Implementation for User Story 6

- [ ] T055 [P] [US6] Create approval_service.py in AI_Employee_Vault/services/
- [ ] T056 [US6] Implement classify_action() to determine if action is sensitive in approval_service.py
- [ ] T057 [US6] Implement create_approval_request() to generate approval file in Pending_Approval/ in approval_service.py
- [ ] T058 [US6] Implement check_approval_status() to monitor approval folder in approval_service.py
- [ ] T059 [US6] Implement execute_approved_action() with logging in approval_service.py
- [ ] T060 [US6] Implement handle_rejection() to archive rejected actions in approval_service.py
- [ ] T061 [US6] Implement 24-hour timeout with auto-rejection in approval_service.py
- [ ] T062 [US6] Add approval logging to AI_Employee_Vault/Logs/approval.log in approval_service.py
- [ ] T063 [US6] Update Company_Handbook.md with approval thresholds and rules
- [ ] T064 [US6] Update process-actions.skill.md to integrate approval workflow for all sensitive actions

**Checkpoint**: At this point, all P1 user stories (1, 2, 3, 6) should work independently with proper approval workflow

---

## Phase 7: User Story 4 - LinkedIn Business Posts (Priority: P2)

**Goal**: Draft and post LinkedIn updates with approval to maintain consistent social media presence

**Independent Test**: Create action file requesting LinkedIn post, verify draft created in Pending_Approval/, approve it, confirm post appears on LinkedIn with correct content

### Implementation for User Story 4

- [ ] T065 [P] [US4] Create linkedin_service.py in AI_Employee_Vault/services/
- [ ] T066 [P] [US4] Create linkedin_watcher.py extending BaseWatcher in AI_Employee_Vault/watchers/ (optional for monitoring)
- [ ] T067 [US4] Implement compose_draft_post() function in linkedin_service.py
- [ ] T068 [US4] Implement validate_post_content() with 3000 character limit and hashtag validation in linkedin_service.py
- [ ] T069 [US4] Implement create_draft_post_file() to generate draft in Pending_Approval/ in linkedin_service.py
- [ ] T070 [US4] Implement publish_post() function with LinkedIn Share API integration in linkedin_service.py
- [ ] T071 [US4] Add OAuth2 token management with 60-day expiry detection in linkedin_service.py
- [ ] T072 [US4] Implement get_engagement_metrics() to fetch post performance in linkedin_service.py
- [ ] T073 [US4] Implement post logging to AI_Employee_Vault/Logs/ in linkedin_service.py
- [ ] T074 [US4] Add error handling for LinkedIn API failures (401, 403, 429, 422) in linkedin_service.py
- [ ] T075 [US4] Create post-linkedin.skill.md in AI_Employee_Vault/.claude/skills/ with usage documentation
- [ ] T076 [US4] Update process-actions.skill.md to handle LinkedIn post requests

**Checkpoint**: At this point, User Stories 1-4 and 6 should all work independently - LinkedIn posts can be created with approval

---

## Phase 8: User Story 5 - Scheduled Automation (Priority: P2)

**Goal**: Run watchers automatically on schedule for hands-free operation

**Independent Test**: Configure watcher to run every 10 minutes, wait for scheduled execution, verify watcher runs automatically and logs execution times

### Implementation for User Story 5

- [ ] T077 [P] [US5] Create scheduler.py in AI_Employee_Vault/scheduler/
- [ ] T078 [P] [US5] Create cron_setup.sh for Linux/Mac in AI_Employee_Vault/scheduler/
- [ ] T079 [P] [US5] Create task_scheduler.ps1 for Windows in AI_Employee_Vault/scheduler/
- [ ] T080 [US5] Implement platform detection (Windows/Linux/Mac) in scheduler.py
- [ ] T081 [US5] Implement add_schedule() function to create new scheduled tasks in scheduler.py
- [ ] T082 [US5] Implement execute_scheduled_task() with subprocess execution in scheduler.py
- [ ] T083 [US5] Implement schedule persistence to config/scheduler_config.json in scheduler.py
- [ ] T084 [US5] Implement cron entry generation for Linux/Mac in cron_setup.sh
- [ ] T085 [US5] Implement Task Scheduler XML generation for Windows in task_scheduler.ps1
- [ ] T086 [US5] Add execution logging to AI_Employee_Vault/Logs/scheduler.log in scheduler.py
- [ ] T087 [US5] Implement graceful shutdown with SIGTERM handler in scheduler.py
- [ ] T088 [US5] Add error handling for task failures (continue schedule) in scheduler.py
- [ ] T089 [US5] Create schedule-task.skill.md in AI_Employee_Vault/.claude/skills/ with usage documentation
- [ ] T090 [US5] Configure default schedules: Gmail Watcher (every 5 min), LinkedIn Watcher (every hour) in config/scheduler_config.json

**Checkpoint**: All user stories should now be independently functional - watchers run on schedule automatically

---

## Phase 9: Integration & Verification

**Purpose**: End-to-end testing and verification of all Silver tier requirements

- [ ] T091 [P] Update Dashboard.md with Silver tier metrics (emails processed, emails sent, LinkedIn posts, plans generated)
- [ ] T092 [P] Create verify_silver.py verification script in AI_Employee_Vault/
- [ ] T093 Test end-to-end email workflow: send test email → verify action file → create draft → approve → verify sent
- [ ] T094 Test end-to-end LinkedIn workflow: create post request → verify draft → approve → verify published
- [ ] T095 Test end-to-end planning workflow: create complex task → verify Plan.md generated → execute steps
- [ ] T096 Test approval workflow: trigger sensitive actions → verify all move to Pending_Approval/ → test approval/rejection
- [ ] T097 Test scheduler: configure schedules → verify execution → check logs
- [ ] T098 Test error handling: simulate API failures → verify retry logic → check error logs
- [ ] T099 Test OAuth token refresh: simulate token expiry → verify automatic refresh
- [ ] T100 Test cross-platform compatibility: run on Windows, Linux, Mac (if available)
- [ ] T101 Run verify_silver.py and confirm all checks pass
- [ ] T102 Performance testing: verify email detection <5 min, email send <30 sec, LinkedIn post <60 sec
- [ ] T103 Security audit: verify credentials in .env, approval workflow enforced, logs sanitized

---

## Phase 10: Documentation & Polish

**Purpose**: Complete documentation and final improvements

- [ ] T104 [P] Update README.md with Silver tier features and setup instructions
- [ ] T105 [P] Create SILVER_TIER_SETUP.md with detailed installation guide
- [ ] T106 [P] Document all Agent Skills in .claude/skills/ directory
- [ ] T107 [P] Add troubleshooting section to quickstart.md
- [ ] T108 Code cleanup: remove debug statements, format code consistently
- [ ] T109 Add inline comments for complex logic in all services
- [ ] T110 Create requirements.txt with all Python dependencies and versions
- [ ] T111 Create package.json for MCP server with dependencies
- [ ] T112 Final verification: run verify_silver.py one last time

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-8)**: All depend on Foundational phase completion
  - US1 (P1): Email Monitoring - Can start after Foundational
  - US2 (P1): Email Sending - Can start after Foundational (integrates with US1 but independent)
  - US3 (P1): Task Planning - Can start after Foundational (fully independent)
  - US6 (P1): Enhanced Approval - Can start after Foundational (integrates with US2, US4)
  - US4 (P2): LinkedIn Posts - Can start after Foundational (integrates with US6)
  - US5 (P2): Scheduler - Can start after Foundational (schedules US1, US4 watchers)
- **Integration (Phase 9)**: Depends on all desired user stories being complete
- **Documentation (Phase 10)**: Depends on Integration phase completion

### User Story Dependencies

- **User Story 1 (P1)**: No dependencies on other stories - fully independent
- **User Story 2 (P1)**: No dependencies on other stories - fully independent (can use US1 emails but not required)
- **User Story 3 (P1)**: No dependencies on other stories - fully independent
- **User Story 6 (P1)**: No dependencies on other stories - provides approval for US2, US4
- **User Story 4 (P2)**: No dependencies on other stories - uses US6 approval but independent
- **User Story 5 (P2)**: No dependencies on other stories - schedules US1, US4 but independent

### Within Each User Story

- Setup tasks before implementation
- Services before skills
- Core implementation before integration
- Error handling after core logic
- Documentation after implementation

### Parallel Opportunities

- **Phase 1 (Setup)**: All tasks marked [P] can run in parallel (T003-T008)
- **Phase 2 (Foundational)**: All tasks marked [P] can run in parallel (T012-T020)
- **Phase 3+ (User Stories)**: Once Foundational completes, all user stories can start in parallel
  - Within US1: T021-T022 can run in parallel
  - Within US2: T031-T032 can run in parallel
  - Within US3: T043-T044 can run in parallel
  - Within US4: T065-T066 can run in parallel
  - Within US5: T077-T079 can run in parallel
  - Within US6: T055 can start immediately
- **Phase 9 (Integration)**: T091-T092 can run in parallel
- **Phase 10 (Documentation)**: T104-T107 can run in parallel

---

## Parallel Example: User Story 1 (Email Monitoring)

```bash
# Launch setup tasks together:
Task T021: "Create gmail_watcher.py extending BaseWatcher"
Task T022: "Implement get_gmail_service() function with OAuth2"

# Then sequential implementation:
Task T023: "Implement check_new_emails() method" (depends on T021, T022)
Task T024: "Implement detect_priority() method" (depends on T023)
# ... and so on
```

---

## Parallel Example: Multiple User Stories

```bash
# After Foundational phase completes, launch all P1 stories in parallel:
Team Member A: User Story 1 (Email Monitoring) - Tasks T021-T030
Team Member B: User Story 2 (Email Sending) - Tasks T031-T042
Team Member C: User Story 3 (Task Planning) - Tasks T043-T054
Team Member D: User Story 6 (Enhanced Approval) - Tasks T055-T064

# Then P2 stories:
Team Member A: User Story 4 (LinkedIn) - Tasks T065-T076
Team Member B: User Story 5 (Scheduler) - Tasks T077-T090
```

---

## Implementation Strategy

### MVP First (User Stories 1, 2, 3, 6 - All P1)

1. Complete Phase 1: Setup (T001-T010)
2. Complete Phase 2: Foundational (T011-T020) - CRITICAL
3. Complete Phase 3: User Story 1 - Email Monitoring (T021-T030)
4. **STOP and VALIDATE**: Test US1 independently
5. Complete Phase 4: User Story 2 - Email Sending (T031-T042)
6. **STOP and VALIDATE**: Test US2 independently
7. Complete Phase 5: User Story 3 - Task Planning (T043-T054)
8. **STOP and VALIDATE**: Test US3 independently
9. Complete Phase 6: User Story 6 - Enhanced Approval (T055-T064)
10. **STOP and VALIDATE**: Test US6 independently
11. **MVP COMPLETE**: All P1 stories functional

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 → Test independently → Core email monitoring works
3. Add US2 → Test independently → Email sending with approval works
4. Add US3 → Test independently → Multi-step planning works
5. Add US6 → Test independently → Approval workflow enhanced
6. Add US4 → Test independently → LinkedIn posting works
7. Add US5 → Test independently → Scheduling works
8. Integration → Test all together → Silver tier complete

### Parallel Team Strategy

With 4 developers after Foundational phase:

1. Team completes Setup + Foundational together (T001-T020)
2. Once Foundational is done:
   - Developer A: User Story 1 (T021-T030)
   - Developer B: User Story 2 (T031-T042)
   - Developer C: User Story 3 (T043-T054)
   - Developer D: User Story 6 (T055-T064)
3. Then:
   - Developer A: User Story 4 (T065-T076)
   - Developer B: User Story 5 (T077-T090)
   - Developers C+D: Integration testing (T091-T103)
4. All: Documentation (T104-T112)

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Tests are NOT included as they were not explicitly requested in spec.md
- All file paths are absolute and follow Bronze tier architecture
- OAuth setup (T012, T013) must be completed before watchers can run
- MCP server (T032) must be running for email sending to work
- Scheduler (US5) should be implemented last as it depends on watchers being functional

---

## Task Summary

- **Total Tasks**: 112
- **Setup Phase**: 10 tasks
- **Foundational Phase**: 10 tasks (BLOCKS all stories)
- **User Story 1 (P1)**: 10 tasks
- **User Story 2 (P1)**: 12 tasks
- **User Story 3 (P1)**: 12 tasks
- **User Story 6 (P1)**: 10 tasks
- **User Story 4 (P2)**: 12 tasks
- **User Story 5 (P2)**: 14 tasks
- **Integration Phase**: 13 tasks
- **Documentation Phase**: 9 tasks

**Parallel Opportunities**: 28 tasks marked [P] can run in parallel within their phases

**MVP Scope**: Phases 1-6 (Tasks T001-T064) = 52 tasks for all P1 user stories

**Estimated Duration**: 14-21 days (per plan.md)
