# Ralph Wiggum Stop Hook for Windows PowerShell
# This hook prevents Claude Code from stopping when a task is still in progress
#
# How it works:
# - Checks if a task file exists in In_Progress\ directory
# - If task exists, returns exit code 1 (prevents Claude from stopping)
# - If no task exists, returns exit code 0 (allows Claude to stop)
#
# Author: AI Employee Gold Tier
# Created: 2026-02-05

$TaskFile = "AI_Employee_Vault\In_Progress\current_task.md"
$StateDir = "AI_Employee_Vault\In_Progress"

# Check if In_Progress directory exists
if (-not (Test-Path $StateDir)) {
    Write-Host "✓ No In_Progress directory - task complete"
    exit 0
}

# Check if any task files exist in In_Progress
$TaskCount = (Get-ChildItem -Path $StateDir -Filter "*.md" -File -ErrorAction SilentlyContinue | Measure-Object).Count

if ($TaskCount -gt 0) {
    Write-Host "⚠️  Task incomplete - continuing autonomous loop..."
    Write-Host "   Tasks in progress: $TaskCount"
    exit 1  # Non-zero exit prevents Claude from stopping
} else {
    Write-Host "✓ All tasks complete!"
    exit 0  # Allow Claude to stop
}
