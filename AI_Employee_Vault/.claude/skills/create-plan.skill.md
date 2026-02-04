# Create Plan Skill

**Skill Name**: create-plan
**Version**: 1.0.0
**Purpose**: Generate multi-step plans for complex tasks using Claude API

## Description

This skill analyzes complex tasks and generates detailed, actionable step-by-step plans. It uses Claude's reasoning capabilities to break down tasks into manageable steps with clear acceptance criteria.

## Usage

### Basic Usage

```
/create-plan "Research competitors and prepare summary report"
```

### With Context

```
/create-plan "Research competitors and prepare summary report" --context "We're launching a new AI automation product" --criteria "Report includes 5 competitors with strengths, weaknesses, and market positioning" --constraints "Complete within 3 days, budget $0"
```

## Parameters

- `task_description` (required): Description of the task to plan
- `--context` (optional): Additional context about the task
- `--criteria` (optional): Success criteria for the task
- `--constraints` (optional): Any constraints or limitations

## Output

Creates a Plan.md file in `AI_Employee_Vault/Plans/` with:
- Numbered steps (1-10 steps)
- Acceptance criteria for each step
- Estimated effort per step
- Dependencies between steps
- Progress tracking

## Example Output

```markdown
# Plan: Research Competitors

**Task**: Research competitors and prepare summary report
**Status**: 📝 Draft
**Created**: 2026-02-04 12:00 PM

## Steps

### Step 1: Identify Competitors ⏳
**Status**: Pending
**Acceptance Criteria**: List of 5 main competitors identified
**Estimated Effort**: 1 hour
**Dependencies**: None

### Step 2: Research Company A ⏳
**Status**: Pending
**Acceptance Criteria**: Documented strengths, weaknesses, market position
**Estimated Effort**: 2 hours
**Dependencies**: Step 1

[... more steps ...]
```

## Implementation

The skill uses the `ReasoningService` class:

```python
from AI_Employee_Vault.services.reasoning_service import ReasoningService

service = ReasoningService(vault_path)
plan = service.generate_plan(
    task_description="Your task here",
    context="Optional context",
    success_criteria="Optional criteria",
    constraints="Optional constraints"
)
```

## Error Handling

- **Invalid API Key**: Check `CLAUDE_API_KEY` in `config/.env`
- **Rate Limit**: Wait and retry (automatic exponential backoff)
- **Empty Task**: Task description cannot be empty
- **Too Many Steps**: Plans limited to 10 steps maximum

## Prerequisites

1. Claude API key configured in `config/.env`:
   ```
   CLAUDE_API_KEY=your_api_key_here
   ```

2. Python dependencies installed:
   ```bash
   pip install anthropic
   ```

## When to Use

Use this skill when:
- Task requires multiple steps to complete
- Task is complex and needs breaking down
- You want structured execution with checkpoints
- You need to track progress on multi-day tasks

Examples:
- "Research competitors and prepare report"
- "Set up new development environment"
- "Migrate database to new schema"
- "Prepare quarterly business review presentation"

## Related Skills

- `/execute-plan` - Execute steps in a generated plan
- `/validate-plan` - Check if plan is complete
- `/process-actions` - Automatically detect complex tasks and create plans

## Notes

- Plans are stored in `AI_Employee_Vault/Plans/`
- Each plan gets a unique ID: `plan-YYYYMMDDHHMMSS`
- Plans can be edited manually before execution
- Step execution is tracked with timestamps and outputs
- Failed steps pause execution and notify user
