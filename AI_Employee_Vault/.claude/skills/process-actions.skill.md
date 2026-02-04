# Process Actions Skill

**Skill Name**: process-actions
**Version**: 2.0.0 (Enhanced with Multi-Step Planning)
**Purpose**: Process action files from Needs_Action folder and route to appropriate handlers

## Description

This skill monitors the Needs_Action/ folder for new action files (emails, tasks, etc.) and routes them to the appropriate service. Enhanced in Silver tier to detect complex multi-step tasks and automatically generate plans.

## Usage

### Manual Trigger

```
/process-actions
```

### Automatic Trigger

The skill runs automatically when:
- Gmail watcher creates new email action files
- User manually creates action files in Needs_Action/
- Scheduler triggers periodic processing

## Action Detection

### Simple Actions (Bronze Tier)

Processed directly without planning:
- Single email responses
- Simple file operations
- Quick status updates
- Straightforward tasks with clear single action

### Complex Actions (Silver Tier - NEW)

Automatically trigger plan generation when task contains:
- Multiple verbs indicating steps (e.g., "research AND prepare")
- Time-based phrases (e.g., "over the next week", "multi-day")
- Keywords: "plan", "strategy", "prepare", "organize", "coordinate"
- Deliverables requiring multiple outputs
- Tasks with explicit steps or phases

## Multi-Step Task Detection

The skill analyzes action descriptions for complexity indicators.

## Processing Flow

1. Scan Needs_Action/ folder for new files
2. For each action file:
   - Parse frontmatter and body
   - Detect action type (email, task, etc.)
   - Check if complex task (NEW)
   - Route to appropriate handler
3. Move processed file to In_Progress/
4. Log processing result

## Related Skills

- /create-plan - Manually create a plan
- /execute-plan - Execute plan steps
- /send-email - Send draft emails
- /post-linkedin - Post to LinkedIn

## Notes

- Runs automatically via scheduler (every 5 minutes)
- Can be triggered manually for immediate processing
- Complex task detection is heuristic-based
- Plans can be edited before execution
