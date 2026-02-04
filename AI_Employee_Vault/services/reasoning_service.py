"""
Reasoning Service - Multi-Step Task Planning
Uses Claude API to generate and execute step-by-step plans for complex tasks
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List
from dotenv import load_dotenv
import logging
import anthropic


class ReasoningService:
    """
    Reasoning service for generating and executing multi-step plans.

    Features:
    - Claude API integration for plan generation
    - Step-by-step plan execution
    - Progress tracking and logging
    - Error handling with retry logic
    - Plan validation and completion checks
    """

    def __init__(self, vault_path: str):
        """
        Initialize Reasoning Service.

        Args:
            vault_path: Path to Obsidian vault
        """
        self.vault_path = Path(vault_path)
        self.plans_dir = self.vault_path / 'Plans'
        self.logs_dir = self.vault_path / 'Logs'

        # Ensure directories exist
        self.plans_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # Load configuration
        load_dotenv(Path(__file__).parent.parent.parent / 'config' / '.env')
        self.api_key = os.getenv('CLAUDE_API_KEY')

        if not self.api_key:
            raise ValueError("CLAUDE_API_KEY not found in config/.env")

        # Initialize Claude client
        self.client = anthropic.Anthropic(api_key=self.api_key)

        # Model configuration
        self.model = "claude-sonnet-4-5-20250929"
        self.temperature = 0.7
        self.max_tokens = 4000
        self.max_steps_per_plan = 10

        # Setup logging
        self.logger = self._setup_logger()

        self.logger.info("Reasoning Service initialized")

    def _setup_logger(self) -> logging.Logger:
        """Set up logging for reasoning service."""
        logger = logging.getLogger('ReasoningService')
        logger.setLevel(logging.INFO)

        log_file = self.logs_dir / 'reasoning_service.log'
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        return logger

    def generate_plan(self, task_description: str, context: str = "",
                     success_criteria: str = "", constraints: str = "") -> Dict:
        """
        Generate a multi-step plan for a complex task using Claude API.

        Args:
            task_description: Description of the task to plan
            context: Additional context about the task
            success_criteria: How to measure success
            constraints: Any constraints or limitations

        Returns:
            Dict with plan_id, plan_file_path, total_steps, status
        """
        self.logger.info(f"Generating plan for task: {task_description}")

        # Validate input
        if not task_description:
            raise ValueError("task_description cannot be empty")

        # Generate plan ID
        plan_id = f"plan-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        try:
            # Build prompt
            prompt = self._build_plan_prompt(
                task_description, context, success_criteria, constraints
            )

            # Call Claude API
            response = self._call_claude_api(prompt)

            # Parse response into steps
            steps = self._parse_plan_response(response)

            # Validate plan
            if not steps:
                raise ValueError("Claude API returned empty plan")
            if len(steps) > self.max_steps_per_plan:
                raise ValueError(f"Plan has too many steps: {len(steps)} (max: {self.max_steps_per_plan})")

            # Create plan file
            plan_file = self._create_plan_file(
                plan_id, task_description, context, success_criteria,
                constraints, steps
            )

            self.logger.info(f"Plan generated successfully: {plan_file}")

            return {
                'plan_id': plan_id,
                'plan_file_path': str(plan_file),
                'total_steps': len(steps),
                'estimated_effort': self._estimate_effort(steps),
                'created_timestamp': datetime.utcnow().isoformat() + 'Z',
                'status': 'draft'
            }

        except anthropic.APIError as e:
            self.logger.error(f"Claude API error: {e}")
            self._handle_api_error(e)
            raise
        except Exception as e:
            self.logger.error(f"Error generating plan: {e}")
            raise

    def _build_plan_prompt(self, task_description: str, context: str,
                          success_criteria: str, constraints: str) -> str:
        """
        Build structured prompt for Claude API.

        Args:
            task_description: Task description
            context: Additional context
            success_criteria: Success criteria
            constraints: Constraints

        Returns:
            Formatted prompt string
        """
        prompt = f"""Task: {task_description}"""

        if context:
            prompt += f"\n\nContext: {context}"

        if success_criteria:
            prompt += f"\n\nSuccess Criteria: {success_criteria}"

        if constraints:
            prompt += f"\n\nConstraints: {constraints}"

        prompt += """

Generate a detailed, actionable plan to accomplish this task. The plan should:
1. Have 1-10 numbered steps
2. Each step should include:
   - Clear description of what to do
   - Acceptance criteria (how to verify success)
   - Estimated effort (e.g., "30 minutes", "2 hours", "1 day")
3. Steps should be ordered by dependencies (later steps may depend on earlier ones)
4. The plan should be realistic and achievable with available resources

Format your response as a numbered list with this structure for each step:

Step N: [Description]
Acceptance Criteria: [How to verify success]
Estimated Effort: [Time or complexity]
Dependencies: [Step numbers this depends on, or "None"]
"""

        return prompt

    def _call_claude_api(self, prompt: str) -> str:
        """
        Call Claude API with retry logic.

        Args:
            prompt: User prompt

        Returns:
            Claude's response text
        """
        system_prompt = """You are a task planning assistant. Generate detailed, actionable plans with numbered steps. Each step must include:
- Clear description of what to do
- Acceptance criteria (how to verify success)
- Estimated effort (time or complexity)
- Dependencies (which steps must complete first)

Keep plans realistic and achievable. Use 1-10 steps maximum."""

        # Retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )

                # Extract text from response
                response_text = message.content[0].text
                return response_text

            except anthropic.RateLimitError as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    self.logger.warning(f"Rate limit hit, retrying in {wait_time}s...")
                    import time
                    time.sleep(wait_time)
                else:
                    raise
            except Exception as e:
                self.logger.error(f"Claude API call failed: {e}")
                raise

    def _parse_plan_response(self, response: str) -> List[Dict]:
        """
        Parse Claude's response into structured steps.

        Args:
            response: Claude's response text

        Returns:
            List of step dictionaries
        """
        steps = []

        # Split response into step blocks
        # Look for patterns like "Step 1:", "Step 2:", etc.
        step_pattern = r'Step (\d+):\s*(.+?)(?=Step \d+:|$)'
        matches = re.finditer(step_pattern, response, re.DOTALL | re.IGNORECASE)

        for match in matches:
            step_number = int(match.group(1))
            step_content = match.group(2).strip()

            # Extract components
            description = ""
            acceptance_criteria = ""
            estimated_effort = ""
            dependencies = []

            # Parse step content
            lines = step_content.split('\n')
            current_section = "description"

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Check for section headers
                if line.lower().startswith('acceptance criteria:'):
                    current_section = "acceptance"
                    acceptance_criteria = line.split(':', 1)[1].strip() if ':' in line else ""
                elif line.lower().startswith('estimated effort:'):
                    current_section = "effort"
                    estimated_effort = line.split(':', 1)[1].strip() if ':' in line else ""
                elif line.lower().startswith('dependencies:'):
                    current_section = "dependencies"
                    deps_text = line.split(':', 1)[1].strip() if ':' in line else ""
                    if deps_text.lower() != "none":
                        # Extract step numbers
                        dep_numbers = re.findall(r'\d+', deps_text)
                        dependencies = [int(n) for n in dep_numbers]
                else:
                    # Add to current section
                    if current_section == "description":
                        description += line + " "
                    elif current_section == "acceptance":
                        acceptance_criteria += line + " "
                    elif current_section == "effort":
                        estimated_effort += line + " "

            # Clean up
            description = description.strip()
            acceptance_criteria = acceptance_criteria.strip()
            estimated_effort = estimated_effort.strip()

            # Validate step
            if not description:
                self.logger.warning(f"Step {step_number} has no description, skipping")
                continue

            steps.append({
                'step_number': step_number,
                'description': description,
                'acceptance_criteria': acceptance_criteria or "Step completed successfully",
                'estimated_effort': estimated_effort or "Unknown",
                'dependencies': dependencies,
                'status': 'pending',
                'started_timestamp': None,
                'completed_timestamp': None,
                'error_message': None,
                'output': None
            })

        return steps

    def _create_plan_file(self, plan_id: str, task_description: str,
                         context: str, success_criteria: str, constraints: str,
                         steps: List[Dict]) -> Path:
        """
        Create Plan.md file in Plans/ directory.

        Args:
            plan_id: Plan ID
            task_description: Task description
            context: Context
            success_criteria: Success criteria
            constraints: Constraints
            steps: List of step dictionaries

        Returns:
            Path to created plan file
        """
        plan_file = self.plans_dir / f"{plan_id}-plan.md"

        # Build frontmatter
        frontmatter = {
            'entity_type': 'plan',
            'plan_id': plan_id,
            'task_description': task_description,
            'status': 'draft',
            'current_step': 0,
            'total_steps': len(steps),
            'created_timestamp': datetime.utcnow().isoformat() + 'Z'
        }

        # Build body
        body = f"""
# Plan: {task_description}

**Task**: {task_description}
**Status**: 📝 Draft
**Created**: {datetime.utcnow().strftime('%Y-%m-%d %I:%M %p')}

## Task Details

**Context**: {context or 'None provided'}

**Success Criteria**: {success_criteria or 'None specified'}

**Constraints**: {constraints or 'None specified'}

## Steps

"""

        # Add steps
        for step in steps:
            step_num = step['step_number']
            body += f"""
### Step {step_num}: {step['description']} ⏳
**Status**: Pending
**Acceptance Criteria**: {step['acceptance_criteria']}
**Estimated Effort**: {step['estimated_effort']}
**Dependencies**: {', '.join(f"Step {d}" for d in step['dependencies']) if step['dependencies'] else 'None'}

---
"""

        # Add progress section
        body += """
## Progress
- ✅ Completed: 0 steps
- 🔄 In Progress: 0 steps
- ⏳ Pending: {} steps
- ❌ Failed: 0 steps

## Execution Log
Plan created. Ready for execution.
""".format(len(steps))

        # Write file
        self._create_markdown_file(plan_file, frontmatter, body)

        return plan_file

    def execute_plan_step(self, plan_id: str, step_number: int) -> Dict:
        """
        Execute a single step in a plan.

        Args:
            plan_id: Plan ID
            step_number: Step number to execute

        Returns:
            Dict with success status, output, and next step
        """
        self.logger.info(f"Executing plan {plan_id}, step {step_number}")

        # Find plan file
        plan_file = self.plans_dir / f"{plan_id}-plan.md"

        if not plan_file.exists():
            raise FileNotFoundError(f"Plan not found: {plan_id}")

        # Parse plan file
        plan_data = self._parse_plan_file(plan_file)

        # Find step
        step = None
        for s in plan_data['steps']:
            if s['step_number'] == step_number:
                step = s
                break

        if not step:
            raise ValueError(f"Step {step_number} not found in plan {plan_id}")

        # Check dependencies
        for dep in step.get('dependencies', []):
            dep_step = next((s for s in plan_data['steps'] if s['step_number'] == dep), None)
            if dep_step and dep_step['status'] != 'completed':
                raise ValueError(f"Dependency not met: Step {dep} must complete before Step {step_number}")

        # Mark step as in progress
        step['status'] = 'in_progress'
        step['started_timestamp'] = datetime.utcnow().isoformat() + 'Z'

        try:
            # Execute step (placeholder - actual execution would be task-specific)
            # For now, we just mark it as completed
            # In a real implementation, this would call appropriate services
            output = f"Step {step_number} executed: {step['description']}"

            # Mark step as completed
            step['status'] = 'completed'
            step['completed_timestamp'] = datetime.utcnow().isoformat() + 'Z'
            step['output'] = output

            # Update plan file
            self._update_plan_file(plan_file, plan_data)

            # Log checkpoint
            self._log_checkpoint(plan_id, step_number, "completed", output)

            # Find next step
            next_step = None
            for s in plan_data['steps']:
                if s['status'] == 'pending':
                    next_step = s['step_number']
                    break

            self.logger.info(f"Step {step_number} completed successfully")

            return {
                'success': True,
                'step_number': step_number,
                'output': output,
                'completed_timestamp': step['completed_timestamp'],
                'next_step': next_step
            }

        except Exception as e:
            # Mark step as failed
            step['status'] = 'failed'
            step['error_message'] = str(e)

            # Update plan file
            self._update_plan_file(plan_file, plan_data)

            # Log checkpoint
            self._log_checkpoint(plan_id, step_number, "failed", str(e))

            self.logger.error(f"Step {step_number} failed: {e}")

            return {
                'success': False,
                'step_number': step_number,
                'error': str(e),
                'completed_timestamp': datetime.utcnow().isoformat() + 'Z',
                'next_step': None
            }

    def validate_plan_completion(self, plan_id: str) -> Dict:
        """
        Check if all plan steps are completed.

        Args:
            plan_id: Plan ID

        Returns:
            Dict with completion status and statistics
        """
        self.logger.info(f"Validating completion for plan {plan_id}")

        # Find plan file
        plan_file = self.plans_dir / f"{plan_id}-plan.md"

        if not plan_file.exists():
            raise FileNotFoundError(f"Plan not found: {plan_id}")

        # Parse plan file
        plan_data = self._parse_plan_file(plan_file)

        # Count step statuses
        total_steps = len(plan_data['steps'])
        completed_steps = sum(1 for s in plan_data['steps'] if s['status'] == 'completed')
        failed_steps = sum(1 for s in plan_data['steps'] if s['status'] == 'failed')
        skipped_steps = sum(1 for s in plan_data['steps'] if s['status'] == 'skipped')

        # Check if all steps completed
        all_completed = completed_steps == total_steps

        # Update plan status if completed
        if all_completed:
            plan_data['status'] = 'completed'
            plan_data['completed_timestamp'] = datetime.utcnow().isoformat() + 'Z'
            self._update_plan_file(plan_file, plan_data)

        self.logger.info(f"Plan {plan_id} validation: {completed_steps}/{total_steps} steps completed")

        return {
            'completed': all_completed,
            'total_steps': total_steps,
            'completed_steps': completed_steps,
            'failed_steps': failed_steps,
            'skipped_steps': skipped_steps,
            'success_criteria_met': all_completed and failed_steps == 0,
            'completion_timestamp': plan_data.get('completed_timestamp')
        }

    def _parse_plan_file(self, file_path: Path) -> Dict:
        """
        Parse plan file.

        Args:
            file_path: Path to plan file

        Returns:
            Dict with plan data
        """
        content = file_path.read_text(encoding='utf-8')

        # Extract frontmatter
        plan_data = {}
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter_text = parts[1]
                body_text = parts[2].strip()

                # Parse YAML frontmatter (simple parsing)
                for line in frontmatter_text.strip().split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        plan_data[key.strip()] = value.strip()

        # Extract steps from body
        steps = []
        step_pattern = r'### Step (\d+):\s*(.+?)\s*([⏳🔄✅❌])\s*\n\*\*Status\*\*:\s*(.+?)\n\*\*Acceptance Criteria\*\*:\s*(.+?)\n\*\*Estimated Effort\*\*:\s*(.+?)\n\*\*Dependencies\*\*:\s*(.+?)(?=\n---|$)'
        matches = re.finditer(step_pattern, content, re.DOTALL)

        for match in matches:
            step_number = int(match.group(1))
            description = match.group(2).strip()
            status_emoji = match.group(3)
            status_text = match.group(4).strip().lower()
            acceptance_criteria = match.group(5).strip()
            estimated_effort = match.group(6).strip()
            dependencies_text = match.group(7).strip()

            # Parse status
            if 'completed' in status_text or '✅' in status_emoji:
                status = 'completed'
            elif 'in progress' in status_text or '🔄' in status_emoji:
                status = 'in_progress'
            elif 'failed' in status_text or '❌' in status_emoji:
                status = 'failed'
            else:
                status = 'pending'

            # Parse dependencies
            dependencies = []
            if dependencies_text.lower() != 'none':
                dep_numbers = re.findall(r'\d+', dependencies_text)
                dependencies = [int(n) for n in dep_numbers]

            steps.append({
                'step_number': step_number,
                'description': description,
                'acceptance_criteria': acceptance_criteria,
                'estimated_effort': estimated_effort,
                'dependencies': dependencies,
                'status': status,
                'started_timestamp': None,
                'completed_timestamp': None,
                'error_message': None,
                'output': None
            })

        plan_data['steps'] = steps
        return plan_data

    def _update_plan_file(self, file_path: Path, plan_data: Dict):
        """
        Update plan file with new data.

        Args:
            file_path: Path to plan file
            plan_data: Updated plan data
        """
        # Read current content
        content = file_path.read_text(encoding='utf-8')

        # Update step statuses in content
        for step in plan_data['steps']:
            step_num = step['step_number']

            # Determine emoji
            emoji = {
                'pending': '⏳',
                'in_progress': '🔄',
                'completed': '✅',
                'failed': '❌',
                'skipped': '⏭️'
            }.get(step['status'], '⏳')

            # Update step header
            old_pattern = rf'(### Step {step_num}:.*?)([⏳🔄✅❌⏭️])'
            new_text = rf'\1{emoji}'
            content = re.sub(old_pattern, new_text, content)

            # Update status line
            old_status_pattern = rf'(\*\*Status\*\*:)\s*(.+?)(\n)'
            new_status = step['status'].replace('_', ' ').title()
            content = re.sub(
                old_status_pattern,
                rf'\1 {new_status}\3',
                content
            )

        # Update progress section
        total = len(plan_data['steps'])
        completed = sum(1 for s in plan_data['steps'] if s['status'] == 'completed')
        in_progress = sum(1 for s in plan_data['steps'] if s['status'] == 'in_progress')
        pending = sum(1 for s in plan_data['steps'] if s['status'] == 'pending')
        failed = sum(1 for s in plan_data['steps'] if s['status'] == 'failed')

        progress_pattern = r'## Progress\n- ✅ Completed:.*?\n- 🔄 In Progress:.*?\n- ⏳ Pending:.*?\n- ❌ Failed:.*?\n'
        new_progress = f"""## Progress
- ✅ Completed: {completed} steps
- 🔄 In Progress: {in_progress} steps
- ⏳ Pending: {pending} steps
- ❌ Failed: {failed} steps

"""
        content = re.sub(progress_pattern, new_progress, content)

        # Write updated content
        file_path.write_text(content, encoding='utf-8')

    def _log_checkpoint(self, plan_id: str, step_number: int, status: str, message: str):
        """
        Log checkpoint after each plan step.

        Args:
            plan_id: Plan ID
            step_number: Step number
            status: Step status
            message: Log message
        """
        log_file = self.logs_dir / f"plan-{plan_id}.log"

        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] Step {step_number} - {status}: {message}\n"

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)

    def _estimate_effort(self, steps: List[Dict]) -> str:
        """
        Estimate total effort from steps.

        Args:
            steps: List of step dictionaries

        Returns:
            Estimated effort string
        """
        # Simple heuristic: count steps
        num_steps = len(steps)

        if num_steps <= 3:
            return "1-2 hours"
        elif num_steps <= 5:
            return "Half day"
        elif num_steps <= 8:
            return "1-2 days"
        else:
            return "3+ days"

    def _handle_api_error(self, error: anthropic.APIError):
        """
        Handle Claude API errors.

        Args:
            error: API error
        """
        if isinstance(error, anthropic.AuthenticationError):
            self.logger.error("Authentication failed. Check CLAUDE_API_KEY in config/.env")
            raise ValueError("Invalid Claude API key")
        elif isinstance(error, anthropic.RateLimitError):
            self.logger.error("Rate limit exceeded. Please wait and try again.")
            raise ValueError("Claude API rate limit exceeded")
        elif isinstance(error, anthropic.APIStatusError):
            self.logger.error(f"Claude API error: {error.status_code} - {error.message}")
            raise ValueError(f"Claude API error: {error.message}")
        else:
            self.logger.error(f"Unexpected API error: {error}")
            raise

    def _create_markdown_file(self, file_path: Path, frontmatter: Dict, body: str):
        """
        Create a Markdown file with YAML frontmatter.

        Args:
            file_path: Path where file should be created
            frontmatter: Dictionary of frontmatter data
            body: Markdown body content
        """
        # Convert frontmatter to YAML
        yaml_lines = ['---']
        for key, value in frontmatter.items():
            yaml_lines.append(f'{key}: {value}')
        yaml_lines.append('---')
        yaml_lines.append('')

        # Combine frontmatter and body
        content = '\n'.join(yaml_lines) + body

        # Write file
        file_path.write_text(content, encoding='utf-8')


# Example usage
if __name__ == '__main__':
    import sys

    # Get vault path
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        vault_path = Path(__file__).parent.parent

    # Create service
    service = ReasoningService(str(vault_path))

    # Example: Generate plan
    plan = service.generate_plan(
        task_description="Research competitors and prepare summary report",
        context="We're launching a new AI automation product",
        success_criteria="Report includes 5 competitors with strengths, weaknesses, and market positioning",
        constraints="Complete within 3 days, budget $0 (use free resources)"
    )

    print(f"Plan created: {plan['plan_file_path']}")
    print(f"Total steps: {plan['total_steps']}")
