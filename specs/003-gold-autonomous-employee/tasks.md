# Tasks: Gold Tier Autonomous Employee

**Input**: Design documents from `/specs/003-gold-autonomous-employee/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/, research.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Single project structure extending existing AI Employee codebase
- Services: `services/`
- MCP servers: `mcp/`
- Ralph Wiggum: `ralph-wiggum/`
- Vault folders: `AI_Employee_Vault/`
- Config: `config/`
- Skills: `.claude/skills/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and Gold Tier directory structure

- [x] T001 Create Gold Tier vault directories: CEO_Briefings/, Queue/, Audit_Logs/
- [x] T002 [P] Create config files: config/odoo_config.json, config/social_media_config.json, config/ralph_wiggum_config.json
- [x] T003 [P] Add Gold Tier environment variables to .env.example (ODOO_URL, ODOO_DATABASE, ODOO_USERNAME, ODOO_PASSWORD, FACEBOOK_*, INSTAGRAM_*, TWITTER_*)
- [x] T004 [P] Create Business_Goals.md template in AI_Employee_Vault/ with revenue targets and subscription tracking
- [x] T005 [P] Install Python dependencies: odoo-rpc-client>=0.9.0, facebook-sdk>=3.1.0, tweepy>=4.14.0
- [x] T006 [P] Install Node.js dependencies for MCP servers: axios@^1.6.0, express@^4.18.0, winston@^3.11.0
- [x] T007 Create MCP server base structure in mcp/ directory with shared utilities

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Error Recovery Infrastructure (US6)

- [x] T008 Create QueueService class in services/queue_service.py with queue management methods
- [x] T009 Implement queue file creation in services/queue_service.py (create_operation method)
- [x] T010 Implement exponential backoff retry logic in services/queue_service.py (calculate_next_retry method)
- [x] T011 Implement queue processing in services/queue_service.py (process_queue method)
- [x] T012 Implement 24-hour expiry alert in services/queue_service.py (check_expired_operations method)
- [x] T013 Add queue health monitoring in services/queue_service.py (get_queue_status method)

### Audit Logging Infrastructure (US7)

- [x] T014 [P] Create AuditService class in services/audit_service.py with logging methods
- [x] T015 [P] Implement daily log file creation in services/audit_service.py (get_log_file_path method)
- [x] T016 [P] Implement log entry writing in services/audit_service.py (log_action method)
- [x] T017 [P] Implement sensitive data redaction in services/audit_service.py (redact_sensitive_data method)
- [x] T018 [P] Implement 90-day retention policy in services/audit_service.py (cleanup_old_logs method)
- [x] T019 [P] Add log rotation logic in services/audit_service.py (rotate_logs method)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Odoo Accounting Integration (Priority: P1) 🎯 MVP

**Goal**: Automatically track all business transactions in Odoo accounting system

**Independent Test**: Create a test invoice and verify it appears in Odoo with correct details (amount, date, customer, status)

### Implementation for User Story 1

- [x] T020 [P] [US1] Create OdooService class in services/odoo_service.py with connection management
- [x] T021 [US1] Implement Odoo connection initialization in services/odoo_service.py (connect method)
- [x] T022 [US1] Implement invoice creation in services/odoo_service.py (create_invoice method)
- [x] T023 [P] [US1] Implement payment recording in services/odoo_service.py (record_payment method)
- [x] T024 [P] [US1] Implement expense recording in services/odoo_service.py (record_expense method)
- [x] T025 [US1] Implement transaction retrieval in services/odoo_service.py (get_transactions method)
- [x] T026 [US1] Add error handling with queue integration in services/odoo_service.py (handle_odoo_error method)
- [x] T027 [US1] Add audit logging to all Odoo operations in services/odoo_service.py
- [x] T028 [P] [US1] Create Odoo MCP server in mcp/odoo-server.js with Express setup
- [x] T029 [P] [US1] Implement health check endpoint in mcp/odoo-server.js (GET /health)
- [x] T030 [US1] Implement invoice creation endpoint in mcp/odoo-server.js (POST /invoices)
- [x] T031 [P] [US1] Implement payment recording endpoint in mcp/odoo-server.js (POST /payments)
- [x] T032 [P] [US1] Implement expense recording endpoint in mcp/odoo-server.js (POST /expenses)
- [x] T033 [US1] Implement transaction listing endpoint in mcp/odoo-server.js (GET /invoices, GET /expenses)
- [x] T034 [US1] Implement transaction summary endpoint in mcp/odoo-server.js (GET /transactions/summary)
- [x] T035 [US1] Add MCP server error handling and logging in mcp/odoo-server.js
- [x] T036 [P] [US1] Create record-odoo-transaction.skill.md in .claude/skills/ with usage examples
- [ ] T037 [US1] Test Odoo integration end-to-end: create invoice, record payment, record expense

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Weekly CEO Briefing (Priority: P1)

**Goal**: Generate comprehensive Monday morning business intelligence report

**Independent Test**: Run briefing generation on test data and verify it contains accurate revenue totals, identifies bottlenecks, and suggests improvements

**Dependencies**: Requires US1 (Odoo Integration) for transaction data

### Implementation for User Story 2

- [x] T038 [P] [US2] Create CEOBriefingService class in services/ceo_briefing_service.py with generation methods
- [x] T039 [US2] Implement revenue calculation in services/ceo_briefing_service.py (calculate_revenue_summary method)
- [x] T040 [P] [US2] Implement expense analysis in services/ceo_briefing_service.py (calculate_expense_summary method)
- [x] T041 [P] [US2] Implement completed tasks analysis in services/ceo_briefing_service.py (analyze_completed_tasks method)
- [x] T042 [US2] Implement bottleneck detection in services/ceo_briefing_service.py (identify_bottlenecks method)
- [x] T043 [US2] Implement unused subscription detection in services/ceo_briefing_service.py (detect_unused_subscriptions method)
- [x] T044 [P] [US2] Implement upcoming deadline detection in services/ceo_briefing_service.py (get_upcoming_deadlines method)
- [x] T045 [US2] Implement proactive suggestions generation in services/ceo_briefing_service.py (generate_suggestions method)
- [x] T046 [US2] Implement briefing file creation in services/ceo_briefing_service.py (create_briefing_file method)
- [x] T047 [US2] Add audit logging to briefing generation in services/ceo_briefing_service.py
- [x] T048 [P] [US2] Create CEO briefing scheduler in scheduler/ceo_briefing_scheduler.py with Monday 8AM trigger
- [x] T049 [US2] Integrate CEOBriefingService with scheduler in scheduler/ceo_briefing_scheduler.py
- [x] T050 [P] [US2] Create generate-ceo-briefing.skill.md in .claude/skills/ with manual trigger option
- [ ] T051 [US2] Test CEO Briefing generation with sample data: verify revenue accuracy, bottleneck detection, suggestions

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Ralph Wiggum Autonomous Loop (Priority: P1)

**Goal**: Enable multi-step task completion without user intervention

**Independent Test**: Assign a multi-step task and verify AI continues working until all steps complete

### Implementation for User Story 3

- [x] T052 [P] [US3] Create stop hook script in .claude/hooks/stop.sh (Linux/Mac) with state file checking
- [x] T053 [P] [US3] Create stop hook script in .claude/hooks/stop.ps1 (Windows) with state file checking
- [x] T054 [P] [US3] Create StateManager class in ralph-wiggum/state_manager.py with state tracking methods
- [x] T055 [US3] Implement task state initialization in ralph-wiggum/state_manager.py (initialize_task method)
- [x] T056 [US3] Implement step completion tracking in ralph-wiggum/state_manager.py (mark_step_complete method)
- [x] T057 [US3] Implement task completion detection in ralph-wiggum/state_manager.py (is_task_complete method)
- [x] T058 [P] [US3] Create autonomous loop implementation in ralph-wiggum/loop.py with iteration tracking
- [x] T059 [US3] Implement max iteration limit in ralph-wiggum/loop.py (check_iteration_limit method)
- [x] T060 [US3] Implement graceful exit on completion in ralph-wiggum/loop.py (exit_gracefully method)
- [x] T061 [US3] Implement error handling and task blocking in ralph-wiggum/loop.py (handle_error method)
- [x] T062 [US3] Add audit logging to loop iterations in ralph-wiggum/loop.py
- [x] T063 [P] [US3] Create process-with-loop.skill.md in .claude/skills/ with usage examples
- [ ] T064 [US3] Test Ralph Wiggum loop with simple multi-step task: verify autonomous completion
- [ ] T065 [US3] Test max iteration limit: verify graceful stop at limit
- [ ] T066 [US3] Test error handling: verify task marked as blocked on failure

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently

---

## Phase 6: User Story 4 - Social Media Integration (Facebook/Instagram) (Priority: P2)

**Goal**: Automatically post business updates to Facebook and Instagram

**Independent Test**: Create draft post, approve it, verify it appears on both platforms with correct content

### Implementation for User Story 4

- [x] T067 [P] [US4] Create SocialMediaService class in services/social_media_service.py with posting methods
- [x] T068 [US4] Implement post validation in services/social_media_service.py (validate_post method)
- [x] T069 [US4] Implement multi-platform posting in services/social_media_service.py (publish_post method)
- [x] T070 [US4] Implement engagement metrics retrieval in services/social_media_service.py (get_metrics method)
- [x] T071 [US4] Add error handling with queue integration in services/social_media_service.py
- [x] T072 [US4] Add audit logging to all social media operations in services/social_media_service.py
- [x] T073 [P] [US4] Create Facebook MCP server in mcp/facebook-server.js with Express setup
- [x] T074 [P] [US4] Implement health check endpoint in mcp/facebook-server.js (GET /health)
- [x] T075 [US4] Implement post creation endpoint in mcp/facebook-server.js (POST /posts)
- [x] T076 [P] [US4] Implement post retrieval endpoint in mcp/facebook-server.js (GET /posts/:post_id)
- [x] T077 [P] [US4] Implement post insights endpoint in mcp/facebook-server.js (GET /posts/:post_id/insights)
- [x] T078 [US4] Implement post deletion endpoint in mcp/facebook-server.js (DELETE /posts/:post_id)
- [x] T079 [US4] Add rate limit handling in mcp/facebook-server.js
- [x] T080 [P] [US4] Create Instagram MCP server in mcp/instagram-server.js with Express setup
- [x] T081 [P] [US4] Implement health check endpoint in mcp/instagram-server.js (GET /health)
- [x] T082 [US4] Implement media container creation endpoint in mcp/instagram-server.js (POST /media)
- [x] T083 [US4] Implement media publishing endpoint in mcp/instagram-server.js (POST /media/publish)
- [x] T084 [P] [US4] Implement media retrieval endpoint in mcp/instagram-server.js (GET /media/:media_id)
- [x] T085 [P] [US4] Implement media insights endpoint in mcp/instagram-server.js (GET /media/:media_id/insights)
- [x] T086 [US4] Implement media deletion endpoint in mcp/instagram-server.js (DELETE /media/:media_id)
- [x] T087 [US4] Add rate limit handling in mcp/instagram-server.js
- [x] T088 [P] [US4] Create post-social-media.skill.md in .claude/skills/ with approval workflow
- [ ] T089 [US4] Test Facebook posting: create post, verify publication, retrieve metrics
- [ ] T090 [US4] Test Instagram posting: create post with image, verify publication, retrieve metrics
- [ ] T091 [US4] Test multi-platform posting: verify same content on both platforms

**Checkpoint**: At this point, User Stories 1-4 should all work independently

---

## Phase 7: User Story 5 - Twitter Integration (Priority: P2)

**Goal**: Automatically post business updates to Twitter

**Independent Test**: Create draft tweet, approve it, verify it appears on Twitter with correct content

### Implementation for User Story 5

- [x] T092 [P] [US5] Create Twitter MCP server in mcp/twitter-server.js with Express setup
- [x] T093 [P] [US5] Implement health check endpoint in mcp/twitter-server.js (GET /health)
- [x] T094 [US5] Implement tweet creation endpoint in mcp/twitter-server.js (POST /tweets)
- [x] T095 [P] [US5] Implement tweet retrieval endpoint in mcp/twitter-server.js (GET /tweets/:tweet_id)
- [x] T096 [P] [US5] Implement tweet metrics endpoint in mcp/twitter-server.js (GET /tweets/:tweet_id/metrics)
- [x] T097 [US5] Implement tweet deletion endpoint in mcp/twitter-server.js (DELETE /tweets/:tweet_id)
- [x] T098 [US5] Implement rate limit status endpoint in mcp/twitter-server.js (GET /rate_limit_status)
- [x] T099 [US5] Add rate limit handling with queue integration in mcp/twitter-server.js
- [x] T100 [US5] Integrate Twitter posting into SocialMediaService in services/social_media_service.py
- [x] T101 [US5] Add Twitter-specific validation (280 char limit) in services/social_media_service.py
- [x] T102 [US5] Update post-social-media.skill.md to include Twitter platform
- [ ] T103 [US5] Test Twitter posting: create tweet, verify publication, retrieve metrics
- [ ] T104 [US5] Test Twitter rate limit handling: verify queue integration when limit reached

**Checkpoint**: All user stories (1-5) should now be independently functional

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T105 [P] Create comprehensive setup guide in docs/gold-tier-setup.md based on quickstart.md
- [x] T106 [P] Create troubleshooting guide in docs/gold-tier-troubleshooting.md with common issues
- [x] T107 [P] Update main README.md with Gold Tier features and setup instructions
- [x] T108 [P] Create API credential acquisition guide in docs/api-credentials.md for Odoo, Facebook, Instagram, Twitter
- [x] T109 [P] Add health check script in scripts/health_check.py to verify all services
- [x] T110 [P] Add queue cleanup script in scripts/cleanup_queue.py for manual queue management
- [x] T111 [P] Add log analysis script in scripts/analyze_logs.py for audit log review
- [x] T112 Create verification script in scripts/verify_gold_tier.py to test all features end-to-end
- [ ] T113 [P] Add performance monitoring to all services (track execution time)
- [ ] T114 [P] Add error rate monitoring to all MCP servers
- [ ] T115 [P] Implement graceful shutdown for all MCP servers
- [ ] T116 [P] Add configuration validation on startup for all services
- [ ] T117 Run quickstart.md validation: follow setup guide and verify all features work
- [ ] T118 Code cleanup: remove debug logging, optimize imports, format code
- [ ] T119 Security audit: verify no credentials in code, sensitive data redacted in logs
- [ ] T120 Performance optimization: profile CEO Briefing generation, optimize slow queries

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1 (Odoo): Can start after Foundational - No dependencies on other stories
  - US2 (CEO Briefing): Can start after Foundational - Depends on US1 for transaction data
  - US3 (Ralph Wiggum): Can start after Foundational - No dependencies on other stories
  - US4 (Facebook/Instagram): Can start after Foundational - No dependencies on other stories
  - US5 (Twitter): Can start after Foundational - No dependencies on other stories
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1 - Odoo)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1 - CEO Briefing)**: Requires US1 complete for transaction data - Can integrate with US3 for task analysis
- **User Story 3 (P1 - Ralph Wiggum)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 4 (P2 - Facebook/Instagram)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 5 (P2 - Twitter)**: Can start after Foundational (Phase 2) - No dependencies on other stories

### Within Each User Story

- Services before MCP servers (services define business logic)
- MCP servers before skills (skills use MCP endpoints)
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T002, T003, T004, T005, T006)
- Within Foundational phase:
  - US6 tasks (T008-T013) can run in parallel with US7 tasks (T014-T019)
- Once Foundational phase completes:
  - US1, US3, US4, US5 can all start in parallel (US2 should wait for US1)
- Within each user story:
  - Tasks marked [P] can run in parallel (different files, no dependencies)
  - Example US1: T020, T023, T024 (different methods) can run in parallel
  - Example US1: T028, T029 (MCP server setup and health check) can run in parallel
- Polish phase: Most tasks marked [P] can run in parallel (documentation, scripts, monitoring)

---

## Parallel Example: User Story 1 (Odoo Integration)

```bash
# Launch all parallel service methods together:
Task T020: "Create OdooService class in services/odoo_service.py"
Task T023: "Implement payment recording in services/odoo_service.py"
Task T024: "Implement expense recording in services/odoo_service.py"

# Launch all parallel MCP endpoints together:
Task T028: "Create Odoo MCP server in mcp/odoo-server.js"
Task T029: "Implement health check endpoint in mcp/odoo-server.js"
Task T031: "Implement payment recording endpoint in mcp/odoo-server.js"
Task T032: "Implement expense recording endpoint in mcp/odoo-server.js"
```

---

## Parallel Example: Foundational Phase

```bash
# Launch Error Recovery (US6) and Audit Logging (US7) in parallel:

# US6 - Error Recovery:
Task T008: "Create QueueService class in services/queue_service.py"
Task T009: "Implement queue file creation in services/queue_service.py"

# US7 - Audit Logging (parallel with US6):
Task T014: "Create AuditService class in services/audit_service.py"
Task T015: "Implement daily log file creation in services/audit_service.py"
Task T016: "Implement log entry writing in services/audit_service.py"
Task T017: "Implement sensitive data redaction in services/audit_service.py"
Task T018: "Implement 90-day retention policy in services/audit_service.py"
Task T019: "Add log rotation logic in services/audit_service.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1, 2, 3 Only - All P1)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Odoo Integration)
4. Complete Phase 4: User Story 2 (CEO Briefing) - depends on US1
5. Complete Phase 5: User Story 3 (Ralph Wiggum Loop)
6. **STOP and VALIDATE**: Test all P1 features independently
7. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (Odoo) → Test independently → Deploy/Demo
3. Add User Story 2 (CEO Briefing) → Test independently → Deploy/Demo (MVP!)
4. Add User Story 3 (Ralph Wiggum) → Test independently → Deploy/Demo
5. Add User Story 4 (Facebook/Instagram) → Test independently → Deploy/Demo
6. Add User Story 5 (Twitter) → Test independently → Deploy/Demo
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Odoo)
   - Developer B: User Story 3 (Ralph Wiggum)
   - Developer C: User Story 4 (Facebook/Instagram)
3. After US1 completes:
   - Developer A: User Story 2 (CEO Briefing) - needs US1 data
4. Stories complete and integrate independently

---

## Task Summary

- **Total Tasks**: 120 tasks
- **Setup Phase**: 7 tasks
- **Foundational Phase**: 12 tasks (US6: 6 tasks, US7: 6 tasks)
- **User Story 1 (Odoo)**: 18 tasks
- **User Story 2 (CEO Briefing)**: 14 tasks
- **User Story 3 (Ralph Wiggum)**: 15 tasks
- **User Story 4 (Facebook/Instagram)**: 25 tasks
- **User Story 5 (Twitter)**: 13 tasks
- **Polish Phase**: 16 tasks

### Tasks by Priority

- **P1 (Critical)**: 66 tasks (Setup + Foundational + US1 + US2 + US3 + US6 + US7)
- **P2 (Important)**: 38 tasks (US4 + US5)
- **Polish**: 16 tasks

### Parallel Opportunities

- **Setup Phase**: 5 of 7 tasks can run in parallel (71%)
- **Foundational Phase**: All 12 tasks can run in parallel (100%)
- **User Story 1**: 10 of 18 tasks can run in parallel (56%)
- **User Story 2**: 6 of 14 tasks can run in parallel (43%)
- **User Story 3**: 8 of 15 tasks can run in parallel (53%)
- **User Story 4**: 14 of 25 tasks can run in parallel (56%)
- **User Story 5**: 6 of 13 tasks can run in parallel (46%)
- **Polish Phase**: 14 of 16 tasks can run in parallel (88%)

### Estimated Effort

- **Setup**: 2-3 hours
- **Foundational**: 4-6 hours
- **User Story 1**: 8-10 hours
- **User Story 2**: 6-8 hours
- **User Story 3**: 6-8 hours
- **User Story 4**: 10-12 hours
- **User Story 5**: 5-6 hours
- **Polish**: 6-8 hours
- **Total**: 47-61 hours

### MVP Scope (P1 Only)

Complete these phases for MVP:
1. Setup (Phase 1)
2. Foundational (Phase 2)
3. User Story 1 - Odoo Integration (Phase 3)
4. User Story 2 - CEO Briefing (Phase 4)
5. User Story 3 - Ralph Wiggum Loop (Phase 5)

**MVP Effort**: 26-35 hours (66 tasks)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- Tests are not included as they were not explicitly requested in the specification
