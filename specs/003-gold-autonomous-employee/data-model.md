# Data Model: Gold Tier Autonomous Employee

**Feature**: 003-gold-autonomous-employee
**Created**: 2026-02-05
**Purpose**: Define all entities, relationships, and validation rules for Gold Tier

---

## Entity Definitions

### 1. CEO Briefing

**Purpose**: Weekly business intelligence report generated every Monday at 8:00 AM

**Fields**:
- `briefing_id` (string, UUID): Unique identifier
- `week_start_date` (date, ISO 8601): Monday of the week being analyzed
- `week_end_date` (date, ISO 8601): Sunday of the week being analyzed
- `generated_at` (datetime, ISO 8601): When the briefing was generated
- `revenue_summary` (object): Revenue analysis
  - `total_revenue` (decimal): Total revenue for the week
  - `invoice_count` (integer): Number of invoices issued
  - `payment_count` (integer): Number of payments received
  - `average_invoice_value` (decimal): Average invoice amount
  - `top_customers` (array): Top 5 customers by revenue
    - `customer_name` (string)
    - `revenue` (decimal)
- `expense_summary` (object): Expense analysis
  - `total_expenses` (decimal): Total expenses for the week
  - `expense_count` (integer): Number of expenses recorded
  - `top_categories` (array): Top 5 expense categories
    - `category_name` (string)
    - `amount` (decimal)
- `completed_tasks` (array): Tasks completed during the week
  - `task_name` (string)
  - `completion_date` (date)
  - `duration_hours` (decimal)
- `bottlenecks` (array): Tasks that took longer than expected
  - `task_name` (string)
  - `expected_duration_hours` (decimal)
  - `actual_duration_hours` (decimal)
  - `delay_percentage` (decimal)
- `proactive_suggestions` (array): AI-generated recommendations
  - `suggestion_type` (enum): "unused_subscription" | "upcoming_deadline" | "cost_optimization" | "process_improvement"
  - `title` (string): Brief description
  - `details` (string): Full explanation
  - `potential_savings` (decimal, optional): Estimated cost savings
  - `action_required` (boolean): Whether user action is needed
- `upcoming_deadlines` (array): Deadlines within next 7 days
  - `deadline_date` (date)
  - `task_name` (string)
  - `priority` (enum): "high" | "medium" | "low"
- `file_path` (string): Path to generated briefing file in vault

**Validation Rules**:
- `week_start_date` must be a Monday
- `week_end_date` must be the Sunday following `week_start_date`
- `generated_at` must be after `week_end_date`
- All monetary values must be non-negative
- `bottlenecks` array must only include tasks where `actual_duration_hours > expected_duration_hours`

**Relationships**:
- References multiple `Odoo Transaction` entities for revenue/expense data
- References `Task Execution State` entities for completed tasks and bottlenecks

**State Transitions**:
- `draft` → `generating` → `complete` → `archived` (after 90 days)

---

### 2. Odoo Transaction

**Purpose**: Record of a business transaction in Odoo accounting system

**Fields**:
- `transaction_id` (string, UUID): Unique identifier
- `odoo_record_id` (integer): Odoo's internal record ID
- `transaction_type` (enum): "invoice" | "payment" | "expense"
- `amount` (decimal): Transaction amount
- `currency` (string, ISO 4217): Currency code (default: "USD")
- `transaction_date` (date, ISO 8601): Date of transaction
- `customer_vendor_id` (integer, optional): Odoo partner ID
- `customer_vendor_name` (string, optional): Partner name
- `description` (string): Transaction description
- `category` (string, optional): Expense category or invoice type
- `accounting_code` (string, optional): Chart of accounts code
- `status` (enum): "draft" | "pending" | "posted" | "paid" | "cancelled"
- `created_at` (datetime, ISO 8601): When record was created locally
- `synced_at` (datetime, ISO 8601, optional): When synced to Odoo
- `sync_status` (enum): "pending" | "synced" | "failed" | "queued"
- `error_message` (string, optional): Error details if sync failed

**Validation Rules**:
- `amount` must be positive
- `currency` must be valid ISO 4217 code
- `transaction_date` cannot be in the future
- `customer_vendor_name` required for invoices and payments
- `category` required for expenses
- `synced_at` must be after `created_at`

**Relationships**:
- May reference `Queued Operation` if sync failed
- Referenced by `CEO Briefing` for revenue/expense analysis
- Referenced by `Audit Log Entry` for transaction recording

**State Transitions**:
- Invoice: `draft` → `pending` → `posted` → `paid`
- Payment: `draft` → `posted`
- Expense: `draft` → `posted`

---

### 3. Social Media Post

**Purpose**: Content for posting to Facebook, Instagram, or Twitter

**Fields**:
- `post_id` (string, UUID): Unique identifier
- `platforms` (array): Target platforms
  - Values: "facebook" | "instagram" | "twitter"
- `content` (object): Post content
  - `text` (string): Post text/caption
  - `image_url` (string, optional): URL to image file
  - `link_url` (string, optional): External link to include
  - `hashtags` (array of strings): Hashtags to include
- `status` (enum): "draft" | "pending_approval" | "approved" | "published" | "failed"
- `created_at` (datetime, ISO 8601): When post was created
- `approved_at` (datetime, ISO 8601, optional): When user approved
- `approved_by` (string, optional): User who approved
- `published_at` (datetime, ISO 8601, optional): When post was published
- `platform_post_ids` (object, optional): Platform-specific post IDs
  - `facebook_post_id` (string, optional)
  - `instagram_media_id` (string, optional)
  - `twitter_tweet_id` (string, optional)
- `engagement_metrics` (object, optional): Retrieved 24 hours after publishing
  - `facebook` (object, optional):
    - `likes` (integer)
    - `comments` (integer)
    - `shares` (integer)
    - `reach` (integer)
  - `instagram` (object, optional):
    - `likes` (integer)
    - `comments` (integer)
    - `saves` (integer)
    - `reach` (integer)
  - `twitter` (object, optional):
    - `likes` (integer)
    - `retweets` (integer)
    - `replies` (integer)
    - `impressions` (integer)
- `metrics_retrieved_at` (datetime, ISO 8601, optional): When metrics were fetched
- `error_details` (object, optional): Error information if publishing failed
  - `platform` (string): Which platform failed
  - `error_message` (string)
  - `error_code` (string, optional)

**Validation Rules**:
- `platforms` array must not be empty
- `content.text` required for all platforms
- Twitter: `content.text` max 280 characters
- Instagram: `content.image_url` required
- `approved_at` must be after `created_at`
- `published_at` must be after `approved_at`
- `metrics_retrieved_at` must be at least 24 hours after `published_at`

**Relationships**:
- May reference `Queued Operation` if publishing failed
- Referenced by `Audit Log Entry` for post publishing
- May be referenced by `CEO Briefing` for social media activity summary

**State Transitions**:
- `draft` → `pending_approval` → `approved` → `published`
- `approved` → `failed` (if publishing fails, can retry)

---

### 4. Audit Log Entry

**Purpose**: Comprehensive record of every action taken by the AI Employee

**Fields**:
- `log_id` (string, UUID): Unique identifier
- `timestamp` (datetime, ISO 8601): When action occurred
- `action_type` (enum): "social_post" | "odoo_transaction" | "email_send" | "ceo_briefing" | "task_execution" | "queue_operation"
- `actor` (enum): "ai_employee" | "user"
- `target` (string): What was acted upon (e.g., "facebook", "odoo", "email")
- `parameters` (object): Action-specific parameters (sensitive data redacted)
  - Structure varies by `action_type`
  - Example for social_post: `{"platforms": ["facebook"], "text_preview": "First 50 chars..."}`
  - Example for odoo_transaction: `{"type": "invoice", "amount": 1500.00, "customer": "Acme Corp"}`
- `approval_status` (enum): "approved" | "pending" | "rejected" | "not_required"
- `approved_by` (string, optional): User who approved (if applicable)
- `result` (enum): "success" | "failure" | "partial_success"
- `error_message` (string, optional): Error details if failed
- `duration_ms` (integer): How long the action took
- `metadata` (object, optional): Additional context
  - `ip_address` (string, optional): Redacted for privacy
  - `user_agent` (string, optional)
  - `correlation_id` (string, optional): Links related actions

**Validation Rules**:
- `timestamp` cannot be in the future
- `duration_ms` must be non-negative
- `approved_by` required when `approval_status` is "approved" or "rejected"
- `error_message` required when `result` is "failure"
- Sensitive data (passwords, tokens, full credit card numbers) must never be logged

**Relationships**:
- May reference `Social Media Post`, `Odoo Transaction`, `CEO Briefing`, or `Task Execution State`
- Standalone entity (not referenced by others)

**Retention Policy**:
- Logs older than 90 days are archived or deleted
- Daily log files: `audit_logs/YYYY-MM-DD.json`

---

### 5. Queued Operation

**Purpose**: Pending operation that couldn't be completed due to service unavailability

**Fields**:
- `operation_id` (string, UUID): Unique identifier
- `operation_type` (enum): "odoo_transaction" | "social_post" | "email_send"
- `target` (string): Service that was unavailable (e.g., "odoo", "facebook")
- `parameters` (object): Operation-specific parameters
  - Structure varies by `operation_type`
  - Contains all data needed to retry the operation
- `retry_count` (integer): Number of retry attempts so far
- `max_retries` (integer): Maximum retry attempts (default: 10)
- `next_retry` (datetime, ISO 8601): When to attempt next retry
- `expiry` (datetime, ISO 8601): When to give up and alert user (24 hours from creation)
- `status` (enum): "pending" | "retrying" | "succeeded" | "expired" | "cancelled"
- `created_at` (datetime, ISO 8601): When operation was queued
- `last_retry_at` (datetime, ISO 8601, optional): When last retry was attempted
- `completed_at` (datetime, ISO 8601, optional): When operation succeeded
- `last_error` (string, optional): Most recent error message

**Validation Rules**:
- `retry_count` must be ≤ `max_retries`
- `next_retry` must be after `created_at`
- `expiry` must be after `created_at` (typically 24 hours)
- `completed_at` must be after `created_at`
- `last_retry_at` must be after `created_at`

**Relationships**:
- May reference `Odoo Transaction` or `Social Media Post`
- Referenced by `Audit Log Entry` for queue operations

**State Transitions**:
- `pending` → `retrying` → `succeeded` (operation completed)
- `pending` → `retrying` → `expired` (24 hours passed, alert user)
- `pending` → `cancelled` (user manually cancelled)

**Retry Logic**:
- Exponential backoff: 1min, 2min, 4min, 8min, 16min, then 30min max
- Formula: `next_retry = last_retry + min(2^retry_count minutes, 30 minutes)`

---

### 6. Task Execution State

**Purpose**: Track progress of multi-step tasks in Ralph Wiggum autonomous loop

**Fields**:
- `task_id` (string, UUID): Unique identifier
- `task_name` (string): Human-readable task name
- `task_file_path` (string): Path to task file in vault
- `status` (enum): "pending" | "in_progress" | "completed" | "blocked" | "failed"
- `total_steps` (integer): Total number of steps in task
- `completed_steps` (array): Steps that have been completed
  - `step_number` (integer)
  - `step_description` (string)
  - `completed_at` (datetime, ISO 8601)
  - `duration_seconds` (integer)
- `current_step` (integer, optional): Step currently being executed
- `remaining_steps` (array): Steps not yet started
  - `step_number` (integer)
  - `step_description` (string)
- `iteration_count` (integer): Number of autonomous loop iterations
- `max_iterations` (integer): Maximum iterations before stopping (default: 10)
- `started_at` (datetime, ISO 8601): When task execution began
- `completed_at` (datetime, ISO 8601, optional): When task finished
- `blocked_reason` (string, optional): Why task is blocked (if applicable)
- `error_message` (string, optional): Error details if failed

**Validation Rules**:
- `total_steps` must equal sum of completed, current, and remaining steps
- `iteration_count` must be ≤ `max_iterations`
- `completed_at` must be after `started_at`
- `current_step` must be between 1 and `total_steps`
- `blocked_reason` required when `status` is "blocked"
- `error_message` required when `status` is "failed"

**Relationships**:
- Referenced by `CEO Briefing` for completed tasks and bottleneck analysis
- Referenced by `Audit Log Entry` for task execution logging

**State Transitions**:
- `pending` → `in_progress` → `completed` (all steps done)
- `in_progress` → `blocked` (step requires user input or external dependency)
- `in_progress` → `failed` (unrecoverable error)
- `blocked` → `in_progress` (blocker resolved)

**Ralph Wiggum Loop Integration**:
- Task file location determines state:
  - `AI_Employee_Vault/Needs_Action/` → `pending`
  - `AI_Employee_Vault/In_Progress/` → `in_progress`
  - `AI_Employee_Vault/Done/` → `completed`
  - `AI_Employee_Vault/Blocked/` → `blocked`

---

## Entity Relationships Diagram

```
CEO Briefing
├── references → Odoo Transaction (many)
└── references → Task Execution State (many)

Odoo Transaction
├── may reference → Queued Operation (one)
└── referenced by → Audit Log Entry (many)

Social Media Post
├── may reference → Queued Operation (one)
└── referenced by → Audit Log Entry (many)

Queued Operation
├── may reference → Odoo Transaction (one)
├── may reference → Social Media Post (one)
└── referenced by → Audit Log Entry (many)

Task Execution State
├── referenced by → CEO Briefing (many)
└── referenced by → Audit Log Entry (many)

Audit Log Entry
├── may reference → Social Media Post (one)
├── may reference → Odoo Transaction (one)
├── may reference → CEO Briefing (one)
└── may reference → Task Execution State (one)
```

---

## Storage Format

All entities are stored as JSON or Markdown files in the local filesystem:

- **CEO Briefing**: `AI_Employee_Vault/CEO_Briefings/YYYY-MM-DD.md` (Markdown with YAML frontmatter)
- **Odoo Transaction**: In-memory during processing, synced to Odoo, logged in audit
- **Social Media Post**: `AI_Employee_Vault/Social_Media/Pending_Approval/*.md` (Markdown with YAML frontmatter)
- **Audit Log Entry**: `AI_Employee_Vault/Audit_Logs/YYYY-MM-DD.json` (JSON array)
- **Queued Operation**: `AI_Employee_Vault/Queue/*.json` (Individual JSON files)
- **Task Execution State**: `AI_Employee_Vault/{Needs_Action|In_Progress|Done|Blocked}/*.md` (Markdown with YAML frontmatter)

---

## Data Validation Summary

| Entity | Required Fields | Unique Constraints | Foreign Keys |
|--------|----------------|-------------------|--------------|
| CEO Briefing | briefing_id, week_start_date, week_end_date, generated_at | briefing_id | None |
| Odoo Transaction | transaction_id, transaction_type, amount, transaction_date | transaction_id, odoo_record_id | None |
| Social Media Post | post_id, platforms, content.text | post_id | None |
| Audit Log Entry | log_id, timestamp, action_type, actor, target, result | log_id | None |
| Queued Operation | operation_id, operation_type, target, parameters | operation_id | None |
| Task Execution State | task_id, task_name, task_file_path, status | task_id, task_file_path | None |

---

## Data Migration Notes

- **From Silver Tier**: Existing task files in `AI_Employee_Vault/` will be enhanced with `Task Execution State` metadata
- **Backward Compatibility**: All new entities are additive; no breaking changes to existing Silver Tier data
- **Rollback Strategy**: If Gold Tier is disabled, new entities are simply ignored; Silver Tier continues functioning

---

## Security & Privacy

- **Sensitive Data Redaction**: Audit logs must never contain passwords, API tokens, or full credit card numbers
- **Encryption**: API credentials stored in `.env` file (not in entities)
- **Access Control**: All files stored locally; no external access
- **Data Retention**: Audit logs and CEO Briefings archived after 90 days

---

## Performance Considerations

- **CEO Briefing Generation**: Must complete in under 2 minutes for 1000 transactions
- **Queue Processing**: Check every 5 minutes for pending operations
- **Audit Logging**: Asynchronous writes to avoid blocking main operations
- **Metrics Retrieval**: Batch process all posts from 24 hours ago once per day

---

## Validation Rules Summary

1. **Temporal Consistency**: All timestamps must be logically ordered (created < updated < completed)
2. **State Validity**: Entity status must match allowed state transitions
3. **Data Integrity**: Foreign key references must exist (soft validation, no database constraints)
4. **Business Rules**: Domain-specific rules (e.g., Twitter 280 char limit, positive amounts)
5. **Security**: No sensitive data in logs, all credentials in `.env`
