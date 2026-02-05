#!/bin/bash
# Ralph Wiggum Stop Hook for Linux/Mac
# This hook prevents Claude Code from stopping when a task is still in progress
#
# How it works:
# - Checks if a task file exists in In_Progress/ directory
# - If task exists, returns exit code 1 (prevents Claude from stopping)
# - If no task exists, returns exit code 0 (allows Claude to stop)
#
# Author: AI Employee Gold Tier
# Created: 2026-02-05

TASK_FILE="AI_Employee_Vault/In_Progress/current_task.md"
STATE_DIR="AI_Employee_Vault/In_Progress"

# Check if In_Progress directory exists
if [ ! -d "$STATE_DIR" ]; then
    echo "✓ No In_Progress directory - task complete"
    exit 0
fi

# Check if any task files exist in In_Progress
TASK_COUNT=$(find "$STATE_DIR" -name "*.md" -type f 2>/dev/null | wc -l)

if [ "$TASK_COUNT" -gt 0 ]; then
    echo "⚠️  Task incomplete - continuing autonomous loop..."
    echo "   Tasks in progress: $TASK_COUNT"
    exit 1  # Non-zero exit prevents Claude from stopping
else
    echo "✓ All tasks complete!"
    exit 0  # Allow Claude to stop
fi
