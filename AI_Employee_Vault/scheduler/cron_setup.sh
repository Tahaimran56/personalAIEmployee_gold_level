#!/bin/bash
# Cron Setup Script for Linux/Mac
# Sets up scheduled tasks using cron

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "AI Employee Scheduler - Cron Setup"
echo "=========================================="
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Python 3 found"

# Check if required Python packages are installed
echo "Checking Python dependencies..."
python3 -c "import schedule" 2>/dev/null || {
    echo -e "${YELLOW}⚠${NC} 'schedule' package not found. Installing..."
    pip3 install schedule
}

echo -e "${GREEN}✓${NC} Python dependencies OK"

# Load scheduler config
CONFIG_FILE="$PROJECT_ROOT/config/scheduler_config.json"

if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${YELLOW}⚠${NC} Scheduler config not found. Creating default config..."
    python3 "$PROJECT_ROOT/AI_Employee_Vault/scheduler/scheduler.py" "$PROJECT_ROOT/AI_Employee_Vault" --init-config
fi

echo -e "${GREEN}✓${NC} Scheduler config loaded"

# Generate cron entries
echo ""
echo "Generating cron entries..."
echo ""

# Main scheduler entry (runs every minute to check schedules)
CRON_ENTRY="* * * * * cd $PROJECT_ROOT && python3 AI_Employee_Vault/scheduler/scheduler.py AI_Employee_Vault >> AI_Employee_Vault/Logs/scheduler.log 2>&1"

# Check if cron entry already exists
if crontab -l 2>/dev/null | grep -q "AI_Employee_Vault/scheduler/scheduler.py"; then
    echo -e "${YELLOW}⚠${NC} Scheduler cron entry already exists"
    echo ""
    echo "Current cron entry:"
    crontab -l | grep "AI_Employee_Vault/scheduler/scheduler.py"
    echo ""
    read -p "Do you want to replace it? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Remove old entry
        crontab -l | grep -v "AI_Employee_Vault/scheduler/scheduler.py" | crontab -
        echo -e "${GREEN}✓${NC} Old entry removed"
    else
        echo "Keeping existing entry"
        exit 0
    fi
fi

# Add new cron entry
(crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -

echo -e "${GREEN}✓${NC} Cron entry added"
echo ""
echo "Cron entry:"
echo "$CRON_ENTRY"
echo ""

# Verify cron entry
echo "Verifying cron setup..."
if crontab -l | grep -q "AI_Employee_Vault/scheduler/scheduler.py"; then
    echo -e "${GREEN}✓${NC} Cron setup successful"
else
    echo -e "${RED}✗${NC} Cron setup failed"
    exit 1
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "The scheduler will now run automatically."
echo ""
echo "Scheduled tasks:"
echo "  - Gmail Watcher: Every 5 minutes"
echo "  - Process Actions: Every 5 minutes"
echo "  - Check Expired Approvals: Every 6 hours"
echo ""
echo "Logs: $PROJECT_ROOT/AI_Employee_Vault/Logs/scheduler.log"
echo ""
echo "To view scheduled tasks:"
echo "  crontab -l"
echo ""
echo "To remove scheduler:"
echo "  crontab -l | grep -v 'AI_Employee_Vault/scheduler/scheduler.py' | crontab -"
echo ""
