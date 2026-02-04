# Task Scheduler Setup Script for Windows
# Sets up scheduled tasks using Windows Task Scheduler

param(
    [switch]$Remove,
    [switch]$List
)

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "AI Employee Scheduler - Windows Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "Warning: Not running as administrator. Some operations may fail." -ForegroundColor Yellow
    Write-Host "Consider running: Start-Process powershell -Verb RunAs -ArgumentList '-File $($MyInvocation.MyCommand.Path)'" -ForegroundColor Yellow
    Write-Host ""
}

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Check Python dependencies
Write-Host "Checking Python dependencies..." -ForegroundColor Cyan
try {
    python -c "import schedule" 2>$null
    Write-Host "[OK] Python dependencies OK" -ForegroundColor Green
} catch {
    Write-Host "[WARNING] 'schedule' package not found. Installing..." -ForegroundColor Yellow
    pip install schedule
}

# Task names
$TaskNameGmail = "AI_Employee_Gmail_Watcher"
$TaskNameActions = "AI_Employee_Process_Actions"
$TaskNameApprovals = "AI_Employee_Check_Approvals"

# Handle list command
if ($List) {
    Write-Host ""
    Write-Host "Current scheduled tasks:" -ForegroundColor Cyan
    Write-Host ""

    $tasks = @($TaskNameGmail, $TaskNameActions, $TaskNameApprovals)
    foreach ($taskName in $tasks) {
        $task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
        if ($task) {
            Write-Host "[OK] $taskName" -ForegroundColor Green
            Write-Host "     State: $($task.State)" -ForegroundColor Gray
            Write-Host "     Next Run: $($task.NextRunTime)" -ForegroundColor Gray
        } else {
            Write-Host "[NOT FOUND] $taskName" -ForegroundColor Yellow
        }
    }

    exit 0
}

# Handle remove command
if ($Remove) {
    Write-Host ""
    Write-Host "Removing scheduled tasks..." -ForegroundColor Cyan

    $tasks = @($TaskNameGmail, $TaskNameActions, $TaskNameApprovals)
    foreach ($taskName in $tasks) {
        try {
            Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
            Write-Host "[OK] Removed: $taskName" -ForegroundColor Green
        } catch {
            Write-Host "[WARNING] Could not remove: $taskName" -ForegroundColor Yellow
        }
    }

    Write-Host ""
    Write-Host "Scheduled tasks removed" -ForegroundColor Green
    exit 0
}

# Create scheduled tasks
Write-Host ""
Write-Host "Creating scheduled tasks..." -ForegroundColor Cyan
Write-Host ""

# Task 1: Gmail Watcher (every 5 minutes)
Write-Host "Setting up: $TaskNameGmail (every 5 minutes)" -ForegroundColor Cyan

$actionGmail = New-ScheduledTaskAction `
    -Execute "python" `
    -Argument "$ProjectRoot\AI_Employee_Vault\watchers\gmail_watcher.py $ProjectRoot\AI_Employee_Vault" `
    -WorkingDirectory $ProjectRoot

$triggerGmail = New-ScheduledTaskTrigger `
    -Once `
    -At (Get-Date) `
    -RepetitionInterval (New-TimeSpan -Minutes 5) `
    -RepetitionDuration ([TimeSpan]::MaxValue)

$settingsGmail = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 5)

try {
    Unregister-ScheduledTask -TaskName $TaskNameGmail -Confirm:$false -ErrorAction SilentlyContinue
    Register-ScheduledTask `
        -TaskName $TaskNameGmail `
        -Action $actionGmail `
        -Trigger $triggerGmail `
        -Settings $settingsGmail `
        -Description "AI Employee: Check Gmail inbox for new emails every 5 minutes" | Out-Null

    Write-Host "[OK] $TaskNameGmail created" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to create $TaskNameGmail : $_" -ForegroundColor Red
}

# Task 2: Process Actions (every 5 minutes)
Write-Host "Setting up: $TaskNameActions (every 5 minutes)" -ForegroundColor Cyan

$actionActions = New-ScheduledTaskAction `
    -Execute "python" `
    -Argument "$ProjectRoot\AI_Employee_Vault\scheduler\scheduler.py $ProjectRoot\AI_Employee_Vault --run-once" `
    -WorkingDirectory $ProjectRoot

$triggerActions = New-ScheduledTaskTrigger `
    -Once `
    -At (Get-Date) `
    -RepetitionInterval (New-TimeSpan -Minutes 5) `
    -RepetitionDuration ([TimeSpan]::MaxValue)

$settingsActions = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 5)

try {
    Unregister-ScheduledTask -TaskName $TaskNameActions -Confirm:$false -ErrorAction SilentlyContinue
    Register-ScheduledTask `
        -TaskName $TaskNameActions `
        -Action $actionActions `
        -Trigger $triggerActions `
        -Settings $settingsActions `
        -Description "AI Employee: Process action files every 5 minutes" | Out-Null

    Write-Host "[OK] $TaskNameActions created" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to create $TaskNameActions : $_" -ForegroundColor Red
}

# Task 3: Check Expired Approvals (every 6 hours)
Write-Host "Setting up: $TaskNameApprovals (every 6 hours)" -ForegroundColor Cyan

$actionApprovals = New-ScheduledTaskAction `
    -Execute "python" `
    -Argument "$ProjectRoot\AI_Employee_Vault\services\approval_service.py $ProjectRoot\AI_Employee_Vault --check-expired" `
    -WorkingDirectory $ProjectRoot

$triggerApprovals = New-ScheduledTaskTrigger `
    -Once `
    -At (Get-Date) `
    -RepetitionInterval (New-TimeSpan -Hours 6) `
    -RepetitionDuration ([TimeSpan]::MaxValue)

$settingsApprovals = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 5)

try {
    Unregister-ScheduledTask -TaskName $TaskNameApprovals -Confirm:$false -ErrorAction SilentlyContinue
    Register-ScheduledTask `
        -TaskName $TaskNameApprovals `
        -Action $actionApprovals `
        -Trigger $triggerApprovals `
        -Settings $settingsApprovals `
        -Description "AI Employee: Check for expired approval requests every 6 hours" | Out-Null

    Write-Host "[OK] $TaskNameApprovals created" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to create $TaskNameApprovals : $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Scheduled tasks created:" -ForegroundColor Cyan
Write-Host "  - $TaskNameGmail (every 5 minutes)" -ForegroundColor Gray
Write-Host "  - $TaskNameActions (every 5 minutes)" -ForegroundColor Gray
Write-Host "  - $TaskNameApprovals (every 6 hours)" -ForegroundColor Gray
Write-Host ""
Write-Host "Logs: $ProjectRoot\AI_Employee_Vault\Logs\scheduler.log" -ForegroundColor Gray
Write-Host ""
Write-Host "To view tasks:" -ForegroundColor Cyan
Write-Host "  .\task_scheduler.ps1 -List" -ForegroundColor Gray
Write-Host ""
Write-Host "To remove tasks:" -ForegroundColor Cyan
Write-Host "  .\task_scheduler.ps1 -Remove" -ForegroundColor Gray
Write-Host ""
Write-Host "To view in Task Scheduler GUI:" -ForegroundColor Cyan
Write-Host "  taskschd.msc" -ForegroundColor Gray
Write-Host ""
