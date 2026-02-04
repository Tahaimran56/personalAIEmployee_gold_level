# Process Actions Skill

**Skill Name**: process-actions
**Version**: 3.0.0 (Enhanced with Multi-Step Planning & Approval Workflow)
**Purpose**: Process action files from Needs_Action folder and route to appropriate handlers with approval workflow

## Description

This skill monitors the Needs_Action/ folder for new action files (emails, tasks, etc.) and routes them to the appropriate service. Enhanced in Silver tier to:
1. Detect complex multi-step tasks and automatically generate plans
2. Classify actions as sensitive/non-sensitive
3. Create approval requests for sensitive actions
4. Execute approved actions with logging

## Usage

### Manual Trigger

```
/process-actions
```

### Automatic Trigger

The skill runs automatically when:
- Gmail watcher creates new email action files
- User manually creates action files in Needs_Action/
- Scheduler triggers periodic processing (every 5 minutes)

## Action Detection

### Simple Actions (Bronze Tier)

Processed directly without planning:
- Single email responses (requires approval before sending)
- Simple file operations (read-only)
- Quick status updates
- Straightforward tasks with clear single action

### Complex Actions (Silver Tier - NEW)

Automatically trigger plan generation when task contains:
- Multiple verbs indicating steps (e.g., "research AND prepare")
- Time-based phrases (e.g., "over the next week", "multi-day")
- Keywords: "plan", "strategy", "prepare", "organize", "coordinate"
- Deliverables requiring multiple outputs
- Tasks with explicit steps or phases

### Sensitive Actions (Silver Tier - NEW)

Automatically trigger approval workflow for:
- **email_send**: Sending any email or message
- **linkedin_post**: Posting to LinkedIn
- **file_delete**: Deleting files
- **api_call_external**: External API calls
- **data_export**: Exporting data externally
- **system_command**: System configuration changes
- **Large operations**: Data operations >100MB

## Processing Flow (Enhanced)

```
1. Scan Needs_Action/ folder for new files
2. For each action file:
   a. Parse frontmatter and body
   b. Detect action type (email, task, etc.)

   c. Check if complex task (NEW in Silver)
      - If complex → ReasoningService.generate_plan()
      - Create Plan.md in Plans/
      - Move action to In_Progress/
      - Continue to next action

   d. Check if sensitive action (NEW in Silver)
      - Call ApprovalService.classify_action()
      - If sensitive → Create approval request
      - Move to Pending_Approval/
      - Wait for user approval
      - Continue to next action

   e. If simple, non-sensitive action:
      - Execute directly
      - Log result
      - Move to Done/

3. Check Approved/ folder for approved actions
   - Execute approved actions
   - Log execution
   - Move to Done/

4. Check for expired approval requests (>24 hours)
   - Auto-reject expired requests
   - Log rejection
   - Move to Rejected/
```

## Approval Workflow Integration

### Step 1: Action Classification

```python
from AI_Employee_Vault.services.approval_service import ApprovalService

approval_service = ApprovalService(vault_path)

# Classify action
classification = approval_service.classify_action(
    action_type='email_send',
    action_details={
        'recipient': 'client@example.com',
        'subject': 'Project Update',
        'body': 'Here is the update...'
    }
)

if classification['approval_required']:
    # Create approval request
    request = approval_service.create_approval_request(
        action_type='email_send',
        action_description='Send email to client about project update',
        action_details=action_details,
        related_entity_id=draft_id
    )
    print(f"Approval required: {request['request_file_path']}")
```

### Step 2: User Approval

User reviews approval request in Obsidian:
- **To Approve**: Move file from `Pending_Approval/` to `Approved/`
- **To Reject**: Move file from `Pending_Approval/` to `Rejected/`
- **To Ignore**: Leave in `Pending_Approval/` (auto-rejects after 24 hours)

### Step 3: Execution

```python
# Check for approved actions
for approved_file in approved_folder.glob('*.md'):
    request_id = extract_request_id(approved_file)

    # Execute approved action
    result = approval_service.execute_approved_action(request_id)

    if result['success']:
        print(f"Action executed: {request_id}")
    else:
        print(f"Execution failed: {result['error']}")
```

### Step 4: Timeout Handling

```python
# Check for expired requests (run periodically)
expired = approval_service.check_expired_requests()

for request_id in expired:
    print(f"Auto-rejected expired request: {request_id}")
```

## Example: Email Action with Approval

**Input**: `Needs_Action/email-abc123-reply-to-client.md`

```markdown
---
entity_type: email_action
email_id: abc123
sender: client@example.com
subject: Project Update Request
priority: normal
---

# Email Action: Reply to Client

**From**: client@example.com
**Subject**: Project Update Request

Please send an update on the project status.
```

**Processing**:
1. Parse action file
2. Detect action type: `email_send` (when drafting reply)
3. Classify as sensitive (requires approval)
4. Create draft email in `Pending_Approval/email-draft-20260204120000.md`
5. Create approval request in `Pending_Approval/email_send-req-20260204120000.md`
6. Wait for user to move to `Approved/`
7. Execute: Send email via MCP server
8. Log execution in `Logs/approval.log`
9. Move to `Done/`

## Sensitive Action Types

### email_send
- **Requires**: recipient, subject, body
- **Timeout**: 24 hours
- **Reason**: Prevent unauthorized communication

### linkedin_post
- **Requires**: post content, visibility
- **Timeout**: 24 hours
- **Reason**: Maintain professional reputation

### file_delete
- **Requires**: file path, file size, reason
- **Timeout**: 24 hours
- **Reason**: Prevent data loss

### api_call_external
- **Requires**: API endpoint, data being sent
- **Timeout**: 24 hours
- **Reason**: Security and data protection

### data_export
- **Requires**: data description, recipient, purpose
- **Timeout**: 24 hours
- **Reason**: Protect sensitive information

### system_command
- **Requires**: command details, expected impact
- **Timeout**: 24 hours
- **Reason**: System security

## Configuration

No configuration required. Approval workflow is automatic based on action classification.

To customize sensitive action types, edit `ApprovalService.SENSITIVE_ACTIONS` in `approval_service.py`.

## Output

### For Complex Tasks
- Creates Plan.md in `Plans/` directory
- Moves action file to `In_Progress/`
- Logs plan generation

### For Sensitive Actions
- Creates approval request in `Pending_Approval/`
- Waits for user approval
- Executes after approval
- Logs all steps in `Logs/approval.log`

### For Simple Actions
- Executes directly
- Moves to `Done/`
- Logs execution

## Error Handling

- **No action files**: Skill completes silently
- **Parse error**: Logs error, skips file
- **Plan generation fails**: Logs error, keeps file in Needs_Action/
- **Approval timeout**: Auto-rejects after 24 hours
- **Execution fails**: Logs error, keeps in Approved/ for retry

## Prerequisites

1. Services initialized:
   - ApprovalService (approval workflow)
   - ReasoningService (Claude API for planning)
   - EmailService (MCP server for email)
   - LinkedInService (LinkedIn API)

2. Folder structure exists:
   - `Needs_Action/`
   - `In_Progress/`
   - `Pending_Approval/`
   - `Approved/`
   - `Rejected/`
   - `Plans/`
   - `Done/`
   - `Logs/`

## Related Skills

- `/create-plan` - Manually create a plan
- `/execute-plan` - Execute plan steps
- `/send-email` - Send draft emails (requires approval)
- `/post-linkedin` - Post to LinkedIn (requires approval)
- `/check-approvals` - Check pending approval requests

## Security Notes

- **24-Hour Timeout**: All approval requests expire after 24 hours
- **Explicit Approval**: No default approvals or assumptions
- **Audit Trail**: All actions logged with timestamps in `Logs/approval.log`
- **Folder-Based**: Simple, transparent approval mechanism
- **Reversible**: Can reject even after initial approval (before execution)
- **Auto-Rejection**: Expired requests are automatically rejected

## Notes

- Runs automatically via scheduler (every 5 minutes)
- Can be triggered manually for immediate processing
- Complex task detection is heuristic-based (may need tuning)
- Plans can be edited before execution
- Approval workflow is mandatory for sensitive actions
- Failed plan generation doesn't block other actions
- Expired approvals are logged and archived
