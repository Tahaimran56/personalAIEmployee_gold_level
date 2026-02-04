# Reasoning Service API Contract

**Service**: Reasoning Service (Claude API)
**Version**: 1.0.0
**Purpose**: Generate multi-step plans for complex tasks using Claude reasoning

## Operations

### 1. Generate Plan

**Operation**: `generate_plan(task_data)`

**Description**: Analyzes a complex task and generates a step-by-step plan

**Input**:
```json
{
  "task_description": "Research competitors and prepare summary report",
  "context": "We're launching a new AI automation product and need to understand the competitive landscape",
  "success_criteria": "Report includes 5 competitors with strengths, weaknesses, and market positioning",
  "constraints": "Complete within 3 days, budget $0 (use free resources)"
}
```

**Output**:
```json
{
  "plan_id": "plan-uuid-789",
  "plan_file_path": "AI_Employee_Vault/Plans/plan-uuid-789-plan.md",
  "total_steps": 6,
  "estimated_effort": "3 days",
  "created_timestamp": "2026-02-04T12:00:00Z",
  "status": "draft"
}
```

**Behavior**:
- Sends task to Claude API with structured prompt
- Parses response into numbered steps with acceptance criteria
- Creates Plan.md file in Plans/ directory
- Returns plan ID for tracking

**Validation**:
- task_description must not be empty
- Plan must have 1-10 steps
- Each step must have acceptance criteria
- Steps must be ordered by dependencies

---

### 2. Execute Plan Step

**Operation**: `execute_plan_step(plan_id, step_number)`

**Description**: Executes a single step in a plan and logs the result

**Input**:
```json
{
  "plan_id": "plan-uuid-789",
  "step_number": 1
}
```

**Output**:
```json
{
  "success": true,
  "step_number": 1,
  "output": "Identified 5 competitors: CompanyA, CompanyB, CompanyC, CompanyD, CompanyE",
  "completed_timestamp": "2026-02-04T13:00:00Z",
  "next_step": 2
}
```

**Behavior**:
- Reads plan file to get step details
- Executes step (may involve Claude API, web search, file operations)
- Updates plan file with step status and output
- Returns execution result

**Error Handling**:
- Step fails → Mark as failed, pause execution, notify user
- Dependency not met → Skip step, mark as skipped
- Timeout → Mark as failed, log timeout error

---

### 3. Validate Plan Completion

**Operation**: `validate_plan_completion(plan_id)`

**Description**: Checks if all plan steps are completed and success criteria met

**Input**:
```json
{
  "plan_id": "plan-uuid-789"
}
```

**Output**:
```json
{
  "completed": true,
  "total_steps": 6,
  "completed_steps": 6,
  "failed_steps": 0,
  "skipped_steps": 0,
  "success_criteria_met": true,
  "completion_timestamp": "2026-02-04T16:00:00Z"
}
```

**Behavior**:
- Reads plan file to check all step statuses
- Verifies success criteria are met
- Updates plan status to completed
- Generates summary for Dashboard

---

## Claude API Integration

### Prompt Template

**System Prompt**:
```
You are a task planning assistant. Generate a detailed, actionable plan with:
1. Numbered steps (1-10 steps maximum)
2. Each step includes:
   - Clear description of what to do
   - Acceptance criteria (how to verify success)
   - Estimated effort (time or complexity)
3. Steps are ordered by dependencies (step N may depend on step N-1)
4. Plan is realistic and achievable with available resources

Output format: Markdown with numbered list
```

**User Prompt**:
```
Task: {task_description}

Context: {context}

Success Criteria: {success_criteria}

Constraints: {constraints}

Generate a step-by-step plan to accomplish this task.
```

### API Configuration

**Model**: claude-sonnet-4-5-20250929
**Temperature**: 0.7 (creative but consistent)
**Max Tokens**: 4000
**System Prompt Caching**: Enabled (reduce costs)

---

## Data Structures

### Plan File Format

```markdown
---
entity_type: plan
plan_id: "plan-uuid-789"
task_description: "Research competitors and prepare summary report"
status: in_progress
current_step: 3
total_steps: 6
created_timestamp: 2026-02-04T12:00:00Z
started_timestamp: 2026-02-04T12:30:00Z
---

# Plan: Research Competitors

**Task**: Research competitors and prepare summary report
**Status**: 🔄 In Progress (Step 3 of 6)
**Created**: 2026-02-04 12:00 PM

## Success Criteria
- Report includes 5 competitors
- Each competitor has strengths, weaknesses, market positioning
- Complete within 3 days
- Budget: $0 (free resources only)

## Steps

### Step 1: Identify Competitors ✅
**Status**: Completed
**Acceptance Criteria**: List of 5 main competitors identified
**Completed**: 2026-02-04 1:00 PM

**Output**: Identified 5 competitors: CompanyA, CompanyB, CompanyC, CompanyD, CompanyE

---

### Step 2: Research Company A ✅
**Status**: Completed
**Acceptance Criteria**: Documented strengths, weaknesses, market position
**Completed**: 2026-02-04 2:00 PM

**Output**: [Research findings for Company A]

---

### Step 3: Research Company B 🔄
**Status**: In Progress
**Acceptance Criteria**: Documented strengths, weaknesses, market position
**Started**: 2026-02-04 2:30 PM

---

### Step 4: Research Company C ⏳
**Status**: Pending
**Acceptance Criteria**: Documented strengths, weaknesses, market position
**Dependencies**: Step 3

---

### Step 5: Research Company D ⏳
**Status**: Pending
**Acceptance Criteria**: Documented strengths, weaknesses, market position
**Dependencies**: Step 4

---

### Step 6: Compile Summary Report ⏳
**Status**: Pending
**Acceptance Criteria**: Report includes all 5 competitors with analysis
**Dependencies**: Steps 1-5

---

## Progress
- ✅ Completed: 2 steps
- 🔄 In Progress: 1 step
- ⏳ Pending: 3 steps
- ❌ Failed: 0 steps
```

---

## Configuration

### Claude API Credentials (.env)

```
CLAUDE_API_KEY=your_api_key
```

### Service Configuration

```json
{
  "model": "claude-sonnet-4-5-20250929",
  "temperature": 0.7,
  "max_tokens": 4000,
  "max_steps_per_plan": 10,
  "enable_prompt_caching": true,
  "timeout_seconds": 60
}
```

---

## Rate Limits

- Claude API: Based on tier (varies)
- Typical: 50 requests per minute
- Plan generation: ~1 request per plan
- Step execution: May use 0-5 requests per step (depends on complexity)

---

## Testing

### Unit Tests
- `test_generate_plan()` - Mock Claude API, verify plan structure
- `test_execute_plan_step()` - Test step execution logic
- `test_validate_plan_completion()` - Verify completion checks

### Integration Tests
- `test_end_to_end_planning()` - Generate plan, execute all steps, verify completion
- `test_plan_failure_handling()` - Simulate step failure, verify pause and notification
- `test_claude_api_error_handling()` - Simulate API errors, verify retry logic
