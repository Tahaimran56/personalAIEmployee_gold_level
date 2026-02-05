"""
CEO Briefing Service for Gold Tier AI Employee

This service generates comprehensive weekly business intelligence reports.
It implements:
- Revenue and expense analysis from Odoo
- Completed tasks analysis from vault
- Bottleneck detection (tasks taking longer than expected)
- Unused subscription detection
- Upcoming deadline alerts
- Proactive suggestions for business optimization

Author: AI Employee Gold Tier
Created: 2026-02-05
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CEOBriefingService:
    """
    Generates weekly CEO Briefing with business intelligence.

    The briefing includes:
    - Revenue summary (from Odoo)
    - Expense analysis (from Odoo)
    - Completed tasks (from vault)
    - Bottleneck identification
    - Proactive suggestions
    - Upcoming deadlines
    """

    def __init__(
        self,
        vault_dir: str = "AI_Employee_Vault",
        briefing_dir: str = "AI_Employee_Vault/CEO_Briefings"
    ):
        """
        Initialize the CEOBriefingService.

        Args:
            vault_dir: Root directory of the AI Employee vault
            briefing_dir: Directory to store generated briefings
        """
        self.vault_dir = Path(vault_dir)
        self.briefing_dir = Path(briefing_dir)
        self.briefing_dir.mkdir(parents=True, exist_ok=True)

        # Load Business Goals
        self.business_goals = self._load_business_goals()

        logger.info(f"CEOBriefingService initialized")

    def _load_business_goals(self) -> Dict[str, Any]:
        """Load business goals from Business_Goals.md."""
        goals_file = self.vault_dir / "Business_Goals.md"

        if not goals_file.exists():
            logger.warning("Business_Goals.md not found, using defaults")
            return {
                "revenue_targets": {"monthly": 10000},
                "subscriptions": []
            }

        # Parse Business_Goals.md (simplified parsing)
        # In production, use a proper markdown parser
        with open(goals_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract revenue target (simplified)
        goals = {
            "revenue_targets": {"monthly": 10000},
            "subscriptions": []
        }

        # TODO: Implement proper markdown parsing
        return goals

    def calculate_revenue_summary(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Calculate revenue summary from Odoo transactions.

        Args:
            start_date: Start of analysis period
            end_date: End of analysis period

        Returns:
            dict: Revenue summary with totals, counts, and top customers
        """
        try:
            from services.odoo_service import OdooService
            odoo_service = OdooService()

            # Get transactions from Odoo
            transactions = odoo_service.get_transactions(
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
                transaction_type="invoice"
            )

            # Calculate summary
            total_revenue = 0
            invoice_count = 0
            payment_count = 0
            customer_revenue = {}

            for txn in transactions:
                if txn.get("transaction_type") == "invoice":
                    invoice_count += 1
                    amount = txn.get("amount", 0)
                    total_revenue += amount

                    # Track by customer
                    customer = txn.get("customer_vendor_name", "Unknown")
                    customer_revenue[customer] = customer_revenue.get(customer, 0) + amount

                    # Count paid invoices
                    if txn.get("status") == "paid":
                        payment_count += 1

            # Get top 5 customers
            top_customers = sorted(
                [{"customer_name": k, "revenue": v} for k, v in customer_revenue.items()],
                key=lambda x: x["revenue"],
                reverse=True
            )[:5]

            average_invoice_value = total_revenue / invoice_count if invoice_count > 0 else 0

            return {
                "total_revenue": round(total_revenue, 2),
                "invoice_count": invoice_count,
                "payment_count": payment_count,
                "average_invoice_value": round(average_invoice_value, 2),
                "top_customers": top_customers
            }

        except Exception as e:
            logger.error(f"Failed to calculate revenue summary: {e}")
            return {
                "total_revenue": 0,
                "invoice_count": 0,
                "payment_count": 0,
                "average_invoice_value": 0,
                "top_customers": []
            }

    def calculate_expense_summary(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Calculate expense summary from Odoo transactions.

        Args:
            start_date: Start of analysis period
            end_date: End of analysis period

        Returns:
            dict: Expense summary with totals and top categories
        """
        try:
            from services.odoo_service import OdooService
            odoo_service = OdooService()

            # Get transactions from Odoo
            transactions = odoo_service.get_transactions(
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
                transaction_type="expense"
            )

            # Calculate summary
            total_expenses = 0
            expense_count = 0
            category_expenses = {}

            for txn in transactions:
                if txn.get("transaction_type") == "expense":
                    expense_count += 1
                    amount = txn.get("amount", 0)
                    total_expenses += amount

                    # Extract category from description
                    description = txn.get("description", "")
                    category = description.split(":")[0] if ":" in description else "Other"
                    category_expenses[category] = category_expenses.get(category, 0) + amount

            # Get top 5 categories
            top_categories = sorted(
                [{"category_name": k, "amount": v} for k, v in category_expenses.items()],
                key=lambda x: x["amount"],
                reverse=True
            )[:5]

            return {
                "total_expenses": round(total_expenses, 2),
                "expense_count": expense_count,
                "top_categories": top_categories
            }

        except Exception as e:
            logger.error(f"Failed to calculate expense summary: {e}")
            return {
                "total_expenses": 0,
                "expense_count": 0,
                "top_categories": []
            }

    def analyze_completed_tasks(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Analyze completed tasks from vault.

        Args:
            start_date: Start of analysis period
            end_date: End of analysis period

        Returns:
            list: Completed tasks with duration
        """
        completed_tasks = []
        done_dir = self.vault_dir / "Done"

        if not done_dir.exists():
            return completed_tasks

        for task_file in done_dir.glob("*.md"):
            try:
                with open(task_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Parse frontmatter (simplified)
                # TODO: Use proper YAML parser
                if "completed:" in content:
                    # Extract completion date
                    for line in content.split('\n'):
                        if line.startswith("completed:"):
                            date_str = line.split(":", 1)[1].strip()
                            try:
                                completed_date = datetime.fromisoformat(date_str)
                                if start_date <= completed_date <= end_date:
                                    completed_tasks.append({
                                        "task_name": task_file.stem,
                                        "completion_date": completed_date.strftime("%Y-%m-%d"),
                                        "duration_hours": 0  # TODO: Calculate from created/completed dates
                                    })
                            except ValueError:
                                pass

            except Exception as e:
                logger.error(f"Error analyzing task {task_file.name}: {e}")

        return completed_tasks

    def identify_bottlenecks(
        self,
        completed_tasks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Identify tasks that took longer than expected.

        Args:
            completed_tasks: List of completed tasks

        Returns:
            list: Bottleneck tasks with expected vs actual duration
        """
        bottlenecks = []

        # TODO: Implement actual bottleneck detection
        # This requires tracking expected vs actual duration
        # For now, return empty list

        return bottlenecks

    def detect_unused_subscriptions(self) -> List[Dict[str, Any]]:
        """
        Detect subscriptions not used in 30+ days.

        Returns:
            list: Unused subscriptions with potential savings
        """
        unused_subscriptions = []

        # Parse Business_Goals.md for subscriptions
        goals_file = self.vault_dir / "Business_Goals.md"

        if not goals_file.exists():
            return unused_subscriptions

        try:
            with open(goals_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse subscription table (simplified)
            # TODO: Use proper markdown table parser
            in_table = False
            for line in content.split('\n'):
                if '| Service Name |' in line:
                    in_table = True
                    continue

                if in_table and line.startswith('|') and 'Total Monthly' not in line:
                    parts = [p.strip() for p in line.split('|')[1:-1]]
                    if len(parts) >= 5:
                        service_name = parts[0]
                        cost = parts[1]
                        last_used = parts[3]

                        # Check if last used > 30 days ago
                        try:
                            last_used_date = datetime.strptime(last_used, "%Y-%m-%d")
                            days_since_use = (datetime.now() - last_used_date).days

                            if days_since_use > 30:
                                # Extract cost value
                                cost_value = float(cost.replace('$', '').replace(',', ''))
                                unused_subscriptions.append({
                                    "service_name": service_name,
                                    "monthly_cost": cost_value,
                                    "days_since_use": days_since_use,
                                    "annual_savings": round(cost_value * 12, 2)
                                })
                        except ValueError:
                            pass

        except Exception as e:
            logger.error(f"Error detecting unused subscriptions: {e}")

        return unused_subscriptions

    def get_upcoming_deadlines(self, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """
        Get upcoming deadlines within specified days.

        Args:
            days_ahead: Number of days to look ahead

        Returns:
            list: Upcoming deadlines with priority
        """
        upcoming_deadlines = []
        cutoff_date = datetime.now() + timedelta(days=days_ahead)

        # Parse Business_Goals.md for deadlines
        goals_file = self.vault_dir / "Business_Goals.md"

        if not goals_file.exists():
            return upcoming_deadlines

        try:
            with open(goals_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse deadline table (simplified)
            in_table = False
            for line in content.split('\n'):
                if '| Deadline |' in line:
                    in_table = True
                    continue

                if in_table and line.startswith('|'):
                    parts = [p.strip() for p in line.split('|')[1:-1]]
                    if len(parts) >= 3:
                        deadline_str = parts[0]
                        task_name = parts[1]
                        priority = parts[2]

                        try:
                            deadline_date = datetime.strptime(deadline_str, "%Y-%m-%d")

                            if datetime.now() <= deadline_date <= cutoff_date:
                                upcoming_deadlines.append({
                                    "deadline_date": deadline_date.strftime("%Y-%m-%d"),
                                    "task_name": task_name,
                                    "priority": priority.lower()
                                })
                        except ValueError:
                            pass

        except Exception as e:
            logger.error(f"Error getting upcoming deadlines: {e}")

        return upcoming_deadlines

    def generate_suggestions(
        self,
        revenue_summary: Dict[str, Any],
        expense_summary: Dict[str, Any],
        unused_subscriptions: List[Dict[str, Any]],
        upcoming_deadlines: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate proactive suggestions based on analysis.

        Args:
            revenue_summary: Revenue analysis
            expense_summary: Expense analysis
            unused_subscriptions: Unused subscriptions
            upcoming_deadlines: Upcoming deadlines

        Returns:
            list: Proactive suggestions
        """
        suggestions = []

        # Unused subscription suggestions
        for sub in unused_subscriptions:
            suggestions.append({
                "suggestion_type": "unused_subscription",
                "title": f"Cancel unused subscription: {sub['service_name']}",
                "details": f"This subscription hasn't been used in {sub['days_since_use']} days. Canceling would save ${sub['annual_savings']}/year.",
                "potential_savings": sub['annual_savings'],
                "action_required": True
            })

        # Upcoming deadline alerts
        for deadline in upcoming_deadlines:
            if deadline['priority'] == 'high':
                suggestions.append({
                    "suggestion_type": "upcoming_deadline",
                    "title": f"High priority deadline approaching: {deadline['task_name']}",
                    "details": f"Due on {deadline['deadline_date']}. Ensure resources are allocated.",
                    "potential_savings": None,
                    "action_required": True
                })

        # Revenue optimization suggestions
        if revenue_summary['invoice_count'] > 0:
            avg_invoice = revenue_summary['average_invoice_value']
            if avg_invoice < 2000:  # Threshold from Business_Goals
                suggestions.append({
                    "suggestion_type": "cost_optimization",
                    "title": "Increase average invoice value",
                    "details": f"Current average invoice is ${avg_invoice:.2f}. Consider upselling or bundling services to reach $2,000 target.",
                    "potential_savings": None,
                    "action_required": False
                })

        return suggestions

    def create_briefing_file(
        self,
        week_start_date: datetime,
        week_end_date: datetime,
        revenue_summary: Dict[str, Any],
        expense_summary: Dict[str, Any],
        completed_tasks: List[Dict[str, Any]],
        bottlenecks: List[Dict[str, Any]],
        proactive_suggestions: List[Dict[str, Any]],
        upcoming_deadlines: List[Dict[str, Any]]
    ) -> str:
        """
        Create briefing markdown file.

        Args:
            week_start_date: Monday of the week
            week_end_date: Sunday of the week
            revenue_summary: Revenue analysis
            expense_summary: Expense analysis
            completed_tasks: Completed tasks
            bottlenecks: Bottleneck tasks
            proactive_suggestions: Proactive suggestions
            upcoming_deadlines: Upcoming deadlines

        Returns:
            str: Path to created briefing file
        """
        filename = f"{week_start_date.strftime('%Y-%m-%d')}_Monday_Briefing.md"
        briefing_file = self.briefing_dir / filename

        # Calculate net income
        net_income = revenue_summary['total_revenue'] - expense_summary['total_expenses']

        # Generate markdown content
        content = f"""---
briefing_id: {week_start_date.strftime('%Y%m%d')}
week_start_date: {week_start_date.strftime('%Y-%m-%d')}
week_end_date: {week_end_date.strftime('%Y-%m-%d')}
generated_at: {datetime.now().isoformat()}
---

# CEO Briefing - Week of {week_start_date.strftime('%B %d, %Y')}

**Period**: {week_start_date.strftime('%B %d')} - {week_end_date.strftime('%B %d, %Y')}
**Generated**: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

---

## 📊 Financial Summary

### Revenue
- **Total Revenue**: ${revenue_summary['total_revenue']:,.2f}
- **Invoices Issued**: {revenue_summary['invoice_count']}
- **Payments Received**: {revenue_summary['payment_count']}
- **Average Invoice Value**: ${revenue_summary['average_invoice_value']:,.2f}

### Top Customers
"""

        for i, customer in enumerate(revenue_summary['top_customers'], 1):
            content += f"{i}. **{customer['customer_name']}**: ${customer['revenue']:,.2f}\n"

        content += f"""
### Expenses
- **Total Expenses**: ${expense_summary['total_expenses']:,.2f}
- **Expense Count**: {expense_summary['expense_count']}

### Top Expense Categories
"""

        for i, category in enumerate(expense_summary['top_categories'], 1):
            content += f"{i}. **{category['category_name']}**: ${category['amount']:,.2f}\n"

        content += f"""
### Net Income
- **Net Income**: ${net_income:,.2f}
- **Profit Margin**: {(net_income / revenue_summary['total_revenue'] * 100) if revenue_summary['total_revenue'] > 0 else 0:.1f}%

---

## ✅ Completed Tasks

**Total Tasks Completed**: {len(completed_tasks)}

"""

        for task in completed_tasks[:10]:  # Show top 10
            content += f"- {task['task_name']} (completed {task['completion_date']})\n"

        if len(completed_tasks) > 10:
            content += f"\n*...and {len(completed_tasks) - 10} more tasks*\n"

        content += """
---

## 🚧 Bottlenecks Identified

"""

        if bottlenecks:
            for bottleneck in bottlenecks:
                content += f"- **{bottleneck['task_name']}**: Expected {bottleneck['expected_duration_hours']}h, took {bottleneck['actual_duration_hours']}h ({bottleneck['delay_percentage']:.0f}% over)\n"
        else:
            content += "*No significant bottlenecks detected this week.*\n"

        content += """
---

## 💡 Proactive Suggestions

"""

        if proactive_suggestions:
            for suggestion in proactive_suggestions:
                icon = "💰" if suggestion['suggestion_type'] == "unused_subscription" else "⚠️" if suggestion['suggestion_type'] == "upcoming_deadline" else "📈"
                content += f"\n### {icon} {suggestion['title']}\n\n"
                content += f"{suggestion['details']}\n"
                if suggestion.get('potential_savings'):
                    content += f"\n**Potential Annual Savings**: ${suggestion['potential_savings']:,.2f}\n"
                if suggestion['action_required']:
                    content += f"\n**Action Required**: Yes\n"
        else:
            content += "*No suggestions at this time. Keep up the great work!*\n"

        content += """
---

## 📅 Upcoming Deadlines (Next 7 Days)

"""

        if upcoming_deadlines:
            for deadline in upcoming_deadlines:
                priority_icon = "🔴" if deadline['priority'] == "high" else "🟡" if deadline['priority'] == "medium" else "🟢"
                content += f"- {priority_icon} **{deadline['task_name']}** - Due {deadline['deadline_date']}\n"
        else:
            content += "*No upcoming deadlines in the next 7 days.*\n"

        content += """
---

## 📝 Notes

This briefing was automatically generated by your AI Employee. All data is sourced from:
- Odoo accounting system (revenue and expenses)
- Task completion records in your vault
- Business goals and targets from Business_Goals.md

**Next Briefing**: {next_monday}

---

*Generated by AI Employee Gold Tier - Autonomous Business Intelligence*
""".format(next_monday=(week_start_date + timedelta(days=7)).strftime('%B %d, %Y'))

        # Write briefing file
        with open(briefing_file, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Created CEO Briefing: {briefing_file}")
        return str(briefing_file)

    def generate_weekly_briefing(self, target_date: Optional[datetime] = None) -> str:
        """
        Generate weekly CEO Briefing for the specified date.

        Args:
            target_date: Date to generate briefing for (default: last Monday)

        Returns:
            str: Path to generated briefing file
        """
        # Determine week start (Monday) and end (Sunday)
        if target_date is None:
            target_date = datetime.now()

        # Find last Monday
        days_since_monday = target_date.weekday()
        week_start_date = target_date - timedelta(days=days_since_monday)
        week_end_date = week_start_date + timedelta(days=6)

        logger.info(f"Generating CEO Briefing for week {week_start_date.strftime('%Y-%m-%d')} to {week_end_date.strftime('%Y-%m-%d')}")

        # Gather all data
        revenue_summary = self.calculate_revenue_summary(week_start_date, week_end_date)
        expense_summary = self.calculate_expense_summary(week_start_date, week_end_date)
        completed_tasks = self.analyze_completed_tasks(week_start_date, week_end_date)
        bottlenecks = self.identify_bottlenecks(completed_tasks)
        unused_subscriptions = self.detect_unused_subscriptions()
        upcoming_deadlines = self.get_upcoming_deadlines()

        # Generate suggestions
        proactive_suggestions = self.generate_suggestions(
            revenue_summary,
            expense_summary,
            unused_subscriptions,
            upcoming_deadlines
        )

        # Create briefing file
        briefing_file = self.create_briefing_file(
            week_start_date,
            week_end_date,
            revenue_summary,
            expense_summary,
            completed_tasks,
            bottlenecks,
            proactive_suggestions,
            upcoming_deadlines
        )

        # Audit log
        try:
            from services.audit_service import AuditService
            audit_service = AuditService()
            audit_service.log_action(
                action_type="ceo_briefing",
                actor="ai_employee",
                target="ceo_briefing",
                parameters={
                    "week_start": week_start_date.strftime("%Y-%m-%d"),
                    "week_end": week_end_date.strftime("%Y-%m-%d"),
                    "revenue": revenue_summary['total_revenue'],
                    "expenses": expense_summary['total_expenses']
                },
                result="success",
                approval_status="not_required"
            )
        except Exception as e:
            logger.error(f"Failed to log CEO Briefing generation: {e}")

        return briefing_file


# Example usage
if __name__ == "__main__":
    # Initialize service
    briefing_service = CEOBriefingService()

    # Generate briefing
    briefing_file = briefing_service.generate_weekly_briefing()
    print(f"✓ CEO Briefing generated: {briefing_file}")
