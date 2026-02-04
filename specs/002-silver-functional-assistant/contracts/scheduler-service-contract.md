# Scheduler Service API Contract

**Service**: Scheduler Service
**Version**: 1.0.0
**Purpose**: Schedule and execute watchers and tasks automatically

## Operations

### 1. Add Schedule

**Operation**: `add_schedule(schedule_data)`

**Description**: Creates a new scheduled task

**Input**:
```json
{
  "task_name": "Gmail Watcher",
  "task_type": "watcher",
  "task_command": "python AI_Employee_Vault/watchers/gmail_watcher.py",
  "cron_expression": "*/5 * * * *",
  "platform": "windows"
}
```

**Output**:
```json
{
  "schedule_id": "schedule-uuid-abc",
  "next_execution": "2026-02-04T12:05:00Z",
  "status": "active",
  "created_timestamp": "2026-02-04T12:00:00Z"
}
```

**Behavior**:
- Validates cron expression syntax
- Calculates next execution time
- Adds to scheduler_config.json
- Creates platform-specific persistence (cron/Task Scheduler)
- Returns schedule ID for tracking

**Validation**:
- cron_expression must be valid cron syntax
- task_command must be executable
- task_name must be unique

---

### 2. Execute Scheduled Task

**Operation**: `execute_scheduled_task(schedule_id)`

**Description**: Executes a scheduled task and logs the result

**Input**:
```json
{
  "schedule_id": "schedule-uuid-abc"
}
```

**Output**:
```json
{
  "success": true,
  "execution_timestamp": "2026-02-04T12:05:00Z",
  "duration_seconds": 15,
  "output": "Gmail Watcher completed: 3 new emails detected",
  "next_execution": "2026-02-04T12:10:00Z"
}
```

**Behavior**:
- Reads schedule config to get task command
- Executes command in subprocess
- Captures stdout/stderr
- Logs execution result
- Updates last_execution and next_execution
- Increments execution_count

**Error Handling**:
- Task fails → Log error, continue schedule
- Task timeout → Kill process, log timeout
- Command not found → Disable schedule, notify user

---

### 3. Pause/Resume Schedule

**Operation**: `pause_schedule(schedule_id)` / `resume_schedule(schedule_id)`

**Description**: Temporarily pauses or resumes a scheduled task

**Input**:
```json
{
  "schedule_id": "schedule-uuid-abc"
}
```

**Output**:
```json
{
  "schedule_id": "schedule-uuid-abc",
  "status": "paused",
  "paused_timestamp": "2026-02-04T12:15:00Z"
}
```

**Behavior**:
- Updates schedule status in config
- Removes from active schedule loop (pause)
- Adds back to active schedule loop (resume)
- Logs status change

---

### 4. Remove Schedule

**Operation**: `remove_schedule(schedule_id)`

**Description**: Permanently removes a scheduled task

**Input**:
```json
{
  "schedule_id": "schedule-uuid-abc"
}
```

**Output**:
```json
{
  "success": true,
  "removed_timestamp": "2026-02-04T12:20:00Z"
}
```

**Behavior**:
- Removes from scheduler_config.json
- Removes platform-specific persistence
- Logs removal

---

## Platform-Specific Implementation

### Linux/Mac (cron)

**Cron Entry Format**:
```bash
# AI Employee - Gmail Watcher
*/5 * * * * cd /path/to/hackathon0 && python AI_Employee_Vault/watchers/gmail_watcher.py >> AI_Employee_Vault/Logs/gmail_watcher.log 2>&1
```

**Installation**:
```bash
# Add to crontab
crontab -l > /tmp/crontab.bak
echo "*/5 * * * * cd /path/to/hackathon0 && python AI_Employee_Vault/watchers/gmail_watcher.py >> AI_Employee_Vault/Logs/gmail_watcher.log 2>&1" >> /tmp/crontab.bak
crontab /tmp/crontab.bak
```

**Removal**:
```bash
# Remove from crontab
crontab -l | grep -v "gmail_watcher.py" | crontab -
```

---

### Windows (Task Scheduler)

**Task XML Template**:
```xml
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <Triggers>
    <CalendarTrigger>
      <Repetition>
        <Interval>PT5M</Interval>
        <StopAtDurationEnd>false</StopAtDurationEnd>
      </Repetition>
      <StartBoundary>2026-02-04T12:00:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Actions>
    <Exec>
      <Command>python</Command>
      <Arguments>AI_Employee_Vault/watchers/gmail_watcher.py</Arguments>
      <WorkingDirectory>C:\Users\Dell\Desktop\hackathon0</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
```

**Installation**:
```powershell
# Import task
schtasks /create /tn "AI Employee - Gmail Watcher" /xml gmail_watcher_task.xml
```

**Removal**:
```powershell
# Delete task
schtasks /delete /tn "AI Employee - Gmail Watcher" /f
```

---

## Data Structures

### Scheduler Configuration

**File**: `config/scheduler_config.json`

```json
{
  "schedules": [
    {
      "schedule_id": "schedule-uuid-abc",
      "task_name": "Gmail Watcher",
      "task_type": "watcher",
      "task_command": "python AI_Employee_Vault/watchers/gmail_watcher.py",
      "cron_expression": "*/5 * * * *",
      "last_execution": "2026-02-04T12:05:00Z",
      "next_execution": "2026-02-04T12:10:00Z",
      "status": "active",
      "execution_count": 145,
      "failure_count": 2,
      "created_timestamp": "2026-02-04T10:00:00Z",
      "platform": "windows"
    },
    {
      "schedule_id": "schedule-uuid-def",
      "task_name": "LinkedIn Watcher",
      "task_type": "watcher",
      "task_command": "python AI_Employee_Vault/watchers/linkedin_watcher.py",
      "cron_expression": "0 */1 * * *",
      "last_execution": "2026-02-04T11:00:00Z",
      "next_execution": "2026-02-04T12:00:00Z",
      "status": "active",
      "execution_count": 24,
      "failure_count": 0,
      "created_timestamp": "2026-02-04T10:00:00Z",
      "platform": "windows"
    }
  ],
  "global_settings": {
    "timezone": "UTC",
    "max_concurrent_tasks": 3,
    "task_timeout_seconds": 300,
    "log_retention_days": 90
  }
}
```

### Execution Log Format

```markdown
---
entity_type: scheduled_execution_log
schedule_id: "schedule-uuid-abc"
task_name: "Gmail Watcher"
execution_timestamp: 2026-02-04T12:05:00Z
duration_seconds: 15
status: success
---

# Scheduled Execution Log: Gmail Watcher

**Executed**: 2026-02-04 12:05 PM
**Duration**: 15 seconds
**Status**: ✅ Success

## Output
Gmail Watcher completed: 3 new emails detected
- Email 1: URGENT: Client meeting
- Email 2: Weekly report
- Email 3: Invoice #12345

## Next Execution
2026-02-04 12:10 PM (in 5 minutes)
```

---

## Cron Expression Reference

| Expression | Meaning | Example Use Case |
|------------|---------|------------------|
| `*/5 * * * *` | Every 5 minutes | Gmail Watcher (frequent checks) |
| `0 */1 * * *` | Every hour | LinkedIn Watcher (less frequent) |
| `0 9 * * *` | Daily at 9 AM | Daily summary report |
| `0 9 * * 1` | Weekly on Monday at 9 AM | Weekly analytics |
| `0 0 1 * *` | Monthly on 1st at midnight | Monthly cleanup |

---

## Python schedule Library Integration

**Runtime Scheduler**:
```python
import schedule
import time
import subprocess

def run_gmail_watcher():
    result = subprocess.run(
        ["python", "AI_Employee_Vault/watchers/gmail_watcher.py"],
        capture_output=True,
        text=True,
        timeout=300
    )
    log_execution(result)

# Schedule tasks
schedule.every(5).minutes.do(run_gmail_watcher)

# Run scheduler loop
while True:
    schedule.run_pending()
    time.sleep(1)
```

---

## Configuration

### Scheduler Settings

```json
{
  "scheduler_enabled": true,
  "use_native_scheduler": true,
  "fallback_to_python_schedule": true,
  "max_concurrent_tasks": 3,
  "task_timeout_seconds": 300,
  "log_retention_days": 90,
  "timezone": "UTC"
}
```

---

## Error Handling

- **Task timeout**: Kill process after 5 minutes, log timeout
- **Task failure**: Log error, continue schedule (don't disable)
- **Scheduler crash**: Restart via systemd/Task Scheduler
- **Config file corrupt**: Use defaults, notify user
- **Permission denied**: Notify user, run in-process only

---

## Testing

### Unit Tests
- `test_add_schedule()` - Verify schedule creation
- `test_execute_scheduled_task()` - Mock task execution
- `test_cron_expression_parsing()` - Validate cron syntax

### Integration Tests
- `test_end_to_end_scheduling()` - Add schedule, wait for execution, verify log
- `test_platform_detection()` - Verify correct scheduler used per platform
- `test_schedule_persistence()` - Restart scheduler, verify schedules restored
