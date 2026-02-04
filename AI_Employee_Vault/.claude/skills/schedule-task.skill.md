# Schedule Task Skill

**Skill Name**: schedule-task
**Version**: 1.0.0
**Purpose**: Set up automated scheduling for watchers and tasks

## Description

This skill enables hands-free operation by automatically running watchers and tasks on schedule. It supports Windows (Task Scheduler), Linux (cron), and Mac (cron) with platform-specific setup scripts.

## Usage

### Setup Scheduler

**Windows:**
```powershell
cd AI_Employee_Vault/scheduler
.\task_scheduler.ps1
```

**Linux/Mac:**
```bash
cd AI_Employee_Vault/scheduler
chmod +x cron_setup.sh
./cron_setup.sh
```

### List Scheduled Tasks

**Windows:**
```powershell
.\task_scheduler.ps1 -List
```

**Linux/Mac:**
```bash
crontab -l
```

### Remove Scheduled Tasks

**Windows:**
```powershell
.\task_scheduler.ps1 -Remove
```

**Linux/Mac:**
```bash
crontab -l | grep -v 'AI_Employee_Vault/scheduler/scheduler.py' | crontab -
```

## Default Schedules

The scheduler comes with pre-configured schedules:

### 1. Gmail Watcher
- **Frequency**: Every 5 minutes
- **Command**: `python AI_Employee_Vault/watchers/gmail_watcher.py`
- **Purpose**: Check Gmail inbox for new emails
- **Enabled**: Yes (by default)

### 2. Process Actions
- **Frequency**: Every 5 minutes
- **Command**: `python AI_Employee_Vault/scheduler/scheduler.py --run-once`
- **Purpose**: Process action files from Needs_Action/
- **Enabled**: Yes (by default)

### 3. Check Expired Approvals
- **Frequency**: Every 6 hours
- **Command**: `python AI_Employee_Vault/services/approval_service.py --check-expired`
- **Purpose**: Auto-reject expired approval requests
- **Enabled**: Yes (by default)

### 4. LinkedIn Watcher (Optional)
- **Frequency**: Every hour
- **Command**: `python AI_Employee_Vault/watchers/linkedin_watcher.py`
- **Purpose**: Check LinkedIn notifications
- **Enabled**: No (by default, enable if needed)

## Configuration

Schedules are configured in `config/scheduler_config.json`:

```json
{
  "schedules": [
    {
      "task_name": "Gmail Watcher",
      "task_type": "watcher",
      "task_command": "python AI_Employee_Vault/watchers/gmail_watcher.py AI_Employee_Vault",
      "cron_expression": "*/5 * * * *",
      "interval_minutes": 5,
      "enabled": true,
      "description": "Check Gmail inbox for new emails every 5 minutes"
    }
  ],
  "global_settings": {
    "max_concurrent_tasks": 1,
    "task_timeout_seconds": 300,
    "retry_on_failure": true,
    "max_retries": 3,
    "log_level": "INFO"
  }
}
```

## Adding Custom Schedules

### Programmatically

```python
from AI_Employee_Vault.scheduler.scheduler import Scheduler

scheduler = Scheduler('AI_Employee_Vault')

# Add custom schedule
scheduler.add_schedule(
    task_name="Custom Task",
    task_command="python my_script.py",
    interval_minutes=30,
    task_type="custom",
    enabled=True,
    description="Run my custom script every 30 minutes"
)
```

### Manually

Edit `config/scheduler_config.json` and add a new entry to the `schedules` array:

```json
{
  "task_name": "My Custom Task",
  "task_type": "custom",
  "task_command": "python my_script.py",
  "cron_expression": "*/30 * * * *",
  "interval_minutes": 30,
  "enabled": true,
  "description": "My custom task description"
}
```

## Platform-Specific Details

### Windows (Task Scheduler)

**Setup:**
- Creates scheduled tasks in Windows Task Scheduler
- Tasks run with current user credentials
- Requires PowerShell 5.0 or later
- May require administrator privileges

**Task Names:**
- `AI_Employee_Gmail_Watcher`
- `AI_Employee_Process_Actions`
- `AI_Employee_Check_Approvals`

**View in GUI:**
```
taskschd.msc
```

**Task Settings:**
- Allow start if on batteries: Yes
- Don't stop if going on batteries: Yes
- Start when available: Yes
- Run only if network available: Yes
- Execution time limit: 5 minutes

### Linux/Mac (Cron)

**Setup:**
- Adds cron entry to user's crontab
- Runs with current user permissions
- Requires cron daemon running

**Cron Entry:**
```
* * * * * cd /path/to/project && python3 AI_Employee_Vault/scheduler/scheduler.py AI_Employee_Vault >> AI_Employee_Vault/Logs/scheduler.log 2>&1
```

**Cron Expression Format:**
```
* * * * *
│ │ │ │ │
│ │ │ │ └─── Day of week (0-7, Sunday=0 or 7)
│ │ │ └───── Month (1-12)
│ │ └─────── Day of month (1-31)
│ └───────── Hour (0-23)
└─────────── Minute (0-59)
```

**Examples:**
- `*/5 * * * *` - Every 5 minutes
- `0 * * * *` - Every hour
- `0 */6 * * *` - Every 6 hours
- `0 9 * * *` - Every day at 9:00 AM
- `0 9 * * 1` - Every Monday at 9:00 AM

## Execution Logging

All scheduled task executions are logged in `AI_Employee_Vault/Logs/scheduler.log`:

```
2026-02-04 12:00:00 - Scheduler - INFO - Starting scheduler...
2026-02-04 12:00:00 - Scheduler - INFO - Scheduled: Gmail Watcher (every 5 minutes)
2026-02-04 12:00:00 - Scheduler - INFO - Scheduled: Process Actions (every 5 minutes)
2026-02-04 12:00:00 - Scheduler - INFO - Scheduler running. Press Ctrl+C to stop.
2026-02-04 12:05:00 - Scheduler - INFO - Executing task: Gmail Watcher
2026-02-04 12:05:03 - Scheduler - INFO - Task completed successfully: Gmail Watcher (3.2s)
```

## Error Handling

### Task Failures

When a scheduled task fails:
1. Error is logged in `scheduler.log`
2. Scheduler continues running (doesn't stop)
3. Task will retry on next scheduled interval
4. If `retry_on_failure` is enabled, task retries up to `max_retries` times

### Task Timeouts

Tasks have a timeout (default: 300 seconds):
- If task exceeds timeout, it's terminated
- Timeout error is logged
- Scheduler continues with next scheduled task

### Graceful Shutdown

The scheduler handles shutdown signals gracefully:
- **SIGTERM**: Graceful shutdown (finish current task)
- **SIGINT** (Ctrl+C): Immediate shutdown
- **Keyboard Interrupt**: Clean exit

## Monitoring

### Check Scheduler Status

**Windows:**
```powershell
Get-ScheduledTask -TaskName "AI_Employee_*"
```

**Linux/Mac:**
```bash
ps aux | grep scheduler.py
```

### View Logs

```bash
tail -f AI_Employee_Vault/Logs/scheduler.log
```

### Check Last Execution

```bash
# Windows
Get-ScheduledTask -TaskName "AI_Employee_Gmail_Watcher" | Get-ScheduledTaskInfo

# Linux/Mac
grep "Gmail Watcher" AI_Employee_Vault/Logs/scheduler.log | tail -5
```

## Troubleshooting

### "Python not found"
**Solution**: Ensure Python is installed and in PATH. Test with `python --version` or `python3 --version`

### "Permission denied" (Linux/Mac)
**Solution**: Make script executable: `chmod +x cron_setup.sh`

### "Task not running" (Windows)
**Solution**:
1. Check Task Scheduler GUI (`taskschd.msc`)
2. Verify task is enabled
3. Check "Last Run Result" column
4. Review task history

### "Cron not working" (Linux/Mac)
**Solution**:
1. Check cron daemon: `systemctl status cron` (Linux) or `sudo launchctl list | grep cron` (Mac)
2. Verify crontab entry: `crontab -l`
3. Check cron logs: `/var/log/syslog` (Linux) or `/var/log/system.log` (Mac)

### "Tasks running but not working"
**Solution**:
1. Check `scheduler.log` for errors
2. Verify Python dependencies installed
3. Check API credentials in `config/.env`
4. Test task manually: `python AI_Employee_Vault/watchers/gmail_watcher.py AI_Employee_Vault`

### "High CPU usage"
**Solution**:
1. Check if multiple scheduler instances are running
2. Increase task intervals in `scheduler_config.json`
3. Review task execution times in logs

## Best Practices

1. **Start with default schedules**: Test with pre-configured schedules before customizing
2. **Monitor logs**: Regularly check `scheduler.log` for errors
3. **Adjust intervals**: If tasks take long to execute, increase intervals to avoid overlap
4. **Test manually first**: Always test tasks manually before scheduling
5. **Use appropriate intervals**: Don't schedule tasks too frequently (respect API rate limits)
6. **Enable only needed tasks**: Disable optional tasks (like LinkedIn Watcher) if not needed
7. **Check credentials**: Ensure all API credentials are valid before scheduling

## Security Notes

- Scheduler runs with current user permissions
- API credentials stored in `config/.env` (not in scheduler config)
- Logs may contain sensitive information (review before sharing)
- Tasks run in project directory (no system-wide access)
- Windows tasks require user to be logged in (or configure "Run whether user is logged on or not")

## Related Skills

- `/process-actions` - Manually trigger action processing
- `/send-email` - Manually send emails
- `/post-linkedin` - Manually post to LinkedIn
- `/create-plan` - Manually create plans

## Notes

- Scheduler uses Python `schedule` library (not OS-native scheduling)
- Windows Task Scheduler and cron are used to start the scheduler process
- The scheduler process runs continuously and manages task execution
- Tasks are executed sequentially (not in parallel) by default
- Task execution is logged with timestamps and duration
- Failed tasks don't stop the scheduler
- Scheduler can be stopped with Ctrl+C or SIGTERM
- Configuration changes require scheduler restart
