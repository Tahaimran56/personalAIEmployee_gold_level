---
name: process-with-loop
description: Process multi-step tasks autonomously without stopping after each step using Ralph Wiggum loop
version: 1.0.0
author: AI Employee Gold Tier
created: 2026-02-05
---

# Process with Ralph Wiggum Loop

Execute multi-step tasks autonomously without stopping after each step. The AI Employee will continue working until the task is complete or max iterations reached.

## Usage

This skill enables true autonomous operation by:
- Continuing execution across multiple steps
- Tracking progress automatically
- Handling errors gracefully
- Stopping only when task is complete or blocked

## Prerequisites

- Stop hook configured in `.claude/hooks/stop.ps1` (Windows) or `.claude/hooks/stop.sh` (Linux/Mac)
- Ralph Wiggum configuration in `config/ralph_wiggum_config.json`
- Task files in vault directories (Needs_Action/, In_Progress/, Done/, Blocked/)

## How It Works

### The Ralph Wiggum Pattern

Named after the Simpsons character who famously said "I'm helping!", the Ralph Wiggum loop allows the AI Employee to keep working without stopping.

**Normal Claude Code behavior:**
1. User gives prompt
2. Claude executes action
3. Claude stops and waits for next prompt

**Ralph Wiggum loop behavior:**
1. User gives prompt with multi-step task
2. Claude executes first step
3. Stop hook checks if task complete
4. If incomplete, Claude continues to next step
5. Repeat until task complete or max iterations

### Stop Hook

The stop hook is a script that runs when Claude tries to stop. It checks:
- Are there any tasks in `In_Progress/` directory?
- If yes: Return exit code 1 (prevents stopping)
- If no: Return exit code 0 (allows stopping)

This creates an autonomous loop where Claude keeps working until the task is done.

## Commands

### Process Multi-Step Task

```
Process this multi-step task autonomously:
1. [Step 1 description]
2. [Step 2 description]
3. [Step 3 description]
```

**Example:**
```
Process this multi-step task autonomously:
1. Read all emails from Needs_Action folder
2. Generate responses for each email
3. Send responses and move emails to Done
```

**What happens:**
1. AI Employee creates task file in Needs_Action/
2. Moves task to In_Progress/
3. Executes step 1
4. Stop hook prevents stopping (task still in In_Progress/)
5. AI Employee continues to step 2
6. Executes step 2
7. Stop hook prevents stopping
8. AI Employee continues to step 3
9. Executes step 3
10. Task complete, moved to Done/
11. Stop hook allows stopping (no tasks in In_Progress/)

### Check Loop Status

```
What tasks are currently in progress?
```

Shows all tasks in the In_Progress/ directory with their status.

### Resume Blocked Task

```
Resume the blocked task [task_name]
```

Moves a task from Blocked/ back to In_Progress/ to retry.

## Configuration

### Ralph Wiggum Config (config/ralph_wiggum_config.json)

```json
{
  "autonomous_loop": {
    "enabled": true,
    "max_iterations": 10,
    "timeout_minutes_per_iteration": 5,
    "stop_hook_enabled": true
  },
  "task_tracking": {
    "state_file_location": "AI_Employee_Vault/In_Progress",
    "completed_folder": "AI_Employee_Vault/Done",
    "blocked_folder": "AI_Employee_Vault/Blocked",
    "needs_action_folder": "AI_Employee_Vault/Needs_Action"
  },
  "iteration_behavior": {
    "continue_on_step_completion": true,
    "stop_on_error": true,
    "stop_on_user_input_required": true,
    "stop_on_max_iterations": true
  }
}
```

### Stop Hook (Windows: .claude/hooks/stop.ps1)

```powershell
$TaskFile = "AI_Employee_Vault\In_Progress\current_task.md"
$StateDir = "AI_Employee_Vault\In_Progress"

if (-not (Test-Path $StateDir)) {
    Write-Host "✓ No In_Progress directory - task complete"
    exit 0
}

$TaskCount = (Get-ChildItem -Path $StateDir -Filter "*.md" -File -ErrorAction SilentlyContinue | Measure-Object).Count

if ($TaskCount -gt 0) {
    Write-Host "⚠️  Task incomplete - continuing autonomous loop..."
    exit 1  # Prevents Claude from stopping
} else {
    Write-Host "✓ All tasks complete!"
    exit 0  # Allows Claude to stop
}
```

### Stop Hook (Linux/Mac: .claude/hooks/stop.sh)

```bash
#!/bin/bash
STATE_DIR="AI_Employee_Vault/In_Progress"

if [ ! -d "$STATE_DIR" ]; then
    echo "✓ No In_Progress directory - task complete"
    exit 0
fi

TASK_COUNT=$(find "$STATE_DIR" -name "*.md" -type f 2>/dev/null | wc -l)

if [ "$TASK_COUNT" -gt 0 ]; then
    echo "⚠️  Task incomplete - continuing autonomous loop..."
    exit 1  # Prevents Claude from stopping
else
    echo "✓ All tasks complete!"
    exit 0  # Allows Claude to stop
fi
```

Make executable: `chmod +x .claude/hooks/stop.sh`

## Task File Format

Tasks are stored as markdown files with JSON frontmatter:

```markdown
```json
{
  "task_id": "task-20260205103000",
  "task_name": "Process all emails",
  "status": "in_progress",
  "total_steps": 3,
  "completed_steps": [
    {
      "step_number": 1,
      "step_description": "Read all emails",
      "completed_at": "2026-02-05T10:30:15Z",
      "duration_seconds": 30
    }
  ],
  "current_step": 2,
  "remaining_steps": [
    {
      "step_number": 2,
      "step_description": "Generate responses"
    },
    {
      "step_number": 3,
      "step_description": "Send responses"
    }
  ],
  "iteration_count": 1,
  "max_iterations": 10,
  "started_at": "2026-02-05T10:30:00Z"
}
```

# Task: Process all emails

**Status**: in_progress
**Progress**: 1/3 steps completed
**Iteration**: 1/10

## Completed Steps
- ✓ Step 1: Read all emails (completed 2026-02-05T10:30:15Z)

## Remaining Steps
- ☐ Step 2: Generate responses
- ☐ Step 3: Send responses
```

## Task States

Tasks move through directories based on their state:

- **Needs_Action/**: Tasks waiting to be started (status: pending)
- **In_Progress/**: Tasks currently being executed (status: in_progress)
- **Done/**: Completed tasks (status: completed)
- **Blocked/**: Tasks that require user input or encountered errors (status: blocked)

## Error Handling

### Task Blocked

If a step requires user input or encounters an error:
1. Task is moved to Blocked/
2. Blocked reason is recorded
3. Loop stops
4. User is notified

**Resume blocked task:**
```
Resume the blocked task and continue from where it left off
```

### Max Iterations Reached

If task reaches max iterations (default: 10):
1. Loop stops gracefully
2. Progress is saved
3. Task remains in In_Progress/
4. User can resume manually

**Increase max iterations:**
Edit `config/ralph_wiggum_config.json` and set `max_iterations` to higher value.

### Timeout

If a single iteration takes longer than timeout (default: 5 minutes):
1. Iteration is cancelled
2. Task is marked as blocked
3. User is notified

## Examples

### Example 1: Email Processing

```
Process this multi-step task autonomously:
1. Read all emails from Needs_Action folder
2. For each email, generate an appropriate response
3. Send the responses
4. Move processed emails to Done folder
5. Create a summary report
```

**Result:**
- AI Employee processes all 5 steps without stopping
- Each email gets a response
- Summary report created
- Task moved to Done/

### Example 2: Social Media Campaign

```
Process this multi-step task autonomously:
1. Create 5 social media posts about our new product
2. Save each post to Pending_Approval folder
3. Wait for my approval (this will block the task)
4. After approval, publish posts to Facebook and Instagram
5. Track engagement metrics after 24 hours
```

**Result:**
- Steps 1-2 complete autonomously
- Task blocks at step 3 (requires user approval)
- User approves posts
- User resumes task
- Steps 4-5 complete autonomously

### Example 3: Data Analysis

```
Process this multi-step task autonomously:
1. Retrieve all transactions from Odoo for the past month
2. Calculate total revenue by customer
3. Identify top 10 customers
4. Generate a report with charts
5. Save report to CEO_Briefings folder
```

**Result:**
- All 5 steps complete without stopping
- Report generated with accurate data
- Task moved to Done/

## Monitoring

### Check Current Progress

```
What's the status of the current task?
```

Shows:
- Task name
- Steps completed / total steps
- Current iteration / max iterations
- Time elapsed
- Estimated time remaining

### View Task History

```
Show me all completed tasks from the past week
```

Lists all tasks in Done/ folder with completion dates.

### View Blocked Tasks

```
Show me all blocked tasks
```

Lists all tasks in Blocked/ folder with blocked reasons.

## Troubleshooting

### Loop Not Continuing

**Problem:** Claude stops after each step instead of continuing

**Solutions:**
1. Verify stop hook exists: `ls .claude/hooks/stop.*`
2. Check hook is executable (Linux/Mac): `chmod +x .claude/hooks/stop.sh`
3. Test hook manually:
   - Windows: `powershell .claude/hooks/stop.ps1`
   - Linux/Mac: `.claude/hooks/stop.sh`
4. Verify task file exists in In_Progress/
5. Check Claude Code settings allow hooks

### Max Iterations Reached Too Quickly

**Problem:** Task stops before completion due to max iterations

**Solutions:**
1. Increase max_iterations in config/ralph_wiggum_config.json
2. Break task into smaller sub-tasks
3. Optimize step execution to be faster
4. Check for infinite loops in task logic

### Task Stuck in In_Progress

**Problem:** Task file remains in In_Progress/ but loop stopped

**Solutions:**
1. Check task status: Read the task file
2. Manually move to Done/ if actually complete
3. Move to Blocked/ if needs attention
4. Resume task: `Resume the task in In_Progress/`

### Stop Hook Not Working

**Problem:** Stop hook doesn't prevent Claude from stopping

**Solutions:**
1. Verify hook file location: `.claude/hooks/stop.ps1` or `.claude/hooks/stop.sh`
2. Check file permissions (Linux/Mac): `ls -l .claude/hooks/stop.sh`
3. Test hook returns correct exit code:
   - With task in In_Progress/: Should return 1
   - Without task in In_Progress/: Should return 0
4. Check Claude Code version supports hooks

## Best Practices

1. **Clear Step Descriptions:** Write specific, actionable step descriptions
2. **Reasonable Step Count:** Keep tasks to 3-10 steps for best results
3. **Error Handling:** Include error handling in step descriptions
4. **User Input Steps:** Explicitly mark steps that require user input
5. **Progress Monitoring:** Check task status periodically for long-running tasks
6. **Max Iterations:** Set appropriate max_iterations based on task complexity
7. **Timeout Settings:** Adjust timeout based on expected step duration

## Integration with Other Features

### Odoo Integration
- Use loop to process multiple transactions
- Example: "Record all invoices from spreadsheet to Odoo"

### CEO Briefing
- Completed tasks automatically included in weekly briefing
- Bottleneck detection identifies slow steps

### Social Media
- Use loop to create and schedule multiple posts
- Example: "Create 7 posts for next week, one per day"

### Audit Logging
- Every iteration logged with step details
- Track total time spent on autonomous tasks

## API Reference

### StateManager Methods

#### `initialize_task(task_name, total_steps, steps, max_iterations=10)`
Create a new task for autonomous execution

**Returns:** Task state dict

#### `mark_step_complete(task_id, step_number, step_description, duration_seconds)`
Mark a step as complete

**Returns:** True if successful

#### `is_task_complete(task_id)`
Check if all steps are done

**Returns:** True if complete

#### `move_to_in_progress(task_id)`
Move task from Needs_Action to In_Progress

#### `mark_task_blocked(task_id, reason)`
Mark task as blocked and move to Blocked/

### RalphWiggumLoop Methods

#### `run_task(task_id)`
Run a task through the autonomous loop

**Returns:** True if completed successfully

#### `should_continue()`
Check if loop should continue (called by stop hook)

**Returns:** True if should continue

#### `check_iteration_limit(task_id)`
Check if max iterations reached

**Returns:** True if limit reached

## Related Skills

- `/record-odoo-transaction` - Record business transactions
- `/generate-ceo-briefing` - Generate weekly business intelligence
- `/post-social-media` - Post to social media platforms

## Support

For issues or questions:
- Check task files: `AI_Employee_Vault/In_Progress/`, `AI_Employee_Vault/Blocked/`
- Check audit logs: `AI_Employee_Vault/Audit_Logs/`
- Test stop hook: Run manually to verify exit codes
- Review config: `config/ralph_wiggum_config.json`
