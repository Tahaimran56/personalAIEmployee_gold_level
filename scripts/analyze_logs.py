"""
Gold Tier AI Employee - Log Analysis Script

This script analyzes audit logs to provide insights:
- Action type distribution
- Success/failure rates
- Most active actors
- Most common errors
- Timeline of activities
- Security alerts (failed authentications, suspicious patterns)

Author: AI Employee Gold Tier
Created: 2026-02-05
"""

import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
from collections import Counter, defaultdict


class LogAnalyzer:
    """Analyze audit logs."""

    def __init__(self, log_dir: str = "AI_Employee_Vault/Audit_Logs"):
        self.log_dir = Path(log_dir)

    def load_logs(self, days: int = 7) -> List[Dict[str, Any]]:
        """Load logs from the past N days."""
        if not self.log_dir.exists():
            print(f"❌ Log directory not found: {self.log_dir}")
            return []

        logs = []
        cutoff_date = datetime.now() - timedelta(days=days)

        for log_file in sorted(self.log_dir.glob("*.json")):
            try:
                # Parse date from filename (YYYY-MM-DD.json)
                date_str = log_file.stem
                log_date = datetime.strptime(date_str, "%Y-%m-%d")

                if log_date >= cutoff_date:
                    with open(log_file, 'r') as f:
                        for line in f:
                            try:
                                log_entry = json.loads(line.strip())
                                logs.append(log_entry)
                            except json.JSONDecodeError:
                                pass
            except Exception as e:
                print(f"⚠️  Error reading {log_file}: {e}")

        return logs

    def analyze_action_types(self, logs: List[Dict[str, Any]]):
        """Analyze distribution of action types."""
        action_types = Counter(log.get('action_type', 'unknown') for log in logs)

        print(f"\n{'='*60}")
        print("Action Type Distribution")
        print(f"{'='*60}")
        print(f"{'Action Type':<30} {'Count':<10} {'Percentage':<10}")
        print(f"{'-'*60}")

        total = len(logs)
        for action_type, count in action_types.most_common():
            percentage = (count / total * 100) if total > 0 else 0
            print(f"{action_type:<30} {count:<10} {percentage:>6.1f}%")

        print(f"{'='*60}\n")

    def analyze_success_rates(self, logs: List[Dict[str, Any]]):
        """Analyze success/failure rates by action type."""
        results_by_type = defaultdict(lambda: {'success': 0, 'failure': 0, 'partial': 0})

        for log in logs:
            action_type = log.get('action_type', 'unknown')
            result = log.get('result', 'unknown')

            if result == 'success':
                results_by_type[action_type]['success'] += 1
            elif result == 'failure':
                results_by_type[action_type]['failure'] += 1
            elif result in ['partial_success', 'partial']:
                results_by_type[action_type]['partial'] += 1

        print(f"\n{'='*80}")
        print("Success Rates by Action Type")
        print(f"{'='*80}")
        print(f"{'Action Type':<25} {'Success':<10} {'Failure':<10} {'Partial':<10} {'Rate':<10}")
        print(f"{'-'*80}")

        for action_type, results in sorted(results_by_type.items()):
            success = results['success']
            failure = results['failure']
            partial = results['partial']
            total = success + failure + partial

            success_rate = (success / total * 100) if total > 0 else 0

            print(f"{action_type:<25} {success:<10} {failure:<10} {partial:<10} {success_rate:>6.1f}%")

        print(f"{'='*80}\n")

    def analyze_actors(self, logs: List[Dict[str, Any]]):
        """Analyze most active actors."""
        actors = Counter(log.get('actor', 'unknown') for log in logs)

        print(f"\n{'='*60}")
        print("Most Active Actors")
        print(f"{'='*60}")
        print(f"{'Actor':<30} {'Actions':<10} {'Percentage':<10}")
        print(f"{'-'*60}")

        total = len(logs)
        for actor, count in actors.most_common(10):
            percentage = (count / total * 100) if total > 0 else 0
            print(f"{actor:<30} {count:<10} {percentage:>6.1f}%")

        print(f"{'='*60}\n")

    def analyze_errors(self, logs: List[Dict[str, Any]]):
        """Analyze most common errors."""
        errors = []
        for log in logs:
            if log.get('result') == 'failure':
                error_msg = log.get('error_message', 'Unknown error')
                errors.append(error_msg)

        if not errors:
            print("\n✓ No errors found in logs\n")
            return

        error_counts = Counter(errors)

        print(f"\n{'='*80}")
        print("Most Common Errors")
        print(f"{'='*80}")
        print(f"{'Error Message':<60} {'Count':<10}")
        print(f"{'-'*80}")

        for error, count in error_counts.most_common(10):
            error_short = error[:58] if len(error) > 58 else error
            print(f"{error_short:<60} {count:<10}")

        print(f"{'='*80}\n")

    def analyze_timeline(self, logs: List[Dict[str, Any]]):
        """Analyze activity timeline by hour."""
        hours = defaultdict(int)

        for log in logs:
            timestamp = log.get('timestamp')
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    hour = dt.hour
                    hours[hour] += 1
                except:
                    pass

        print(f"\n{'='*60}")
        print("Activity Timeline (by hour)")
        print(f"{'='*60}")

        max_count = max(hours.values()) if hours else 1

        for hour in range(24):
            count = hours.get(hour, 0)
            bar_length = int((count / max_count) * 40) if max_count > 0 else 0
            bar = '█' * bar_length
            print(f"{hour:02d}:00 | {bar} {count}")

        print(f"{'='*60}\n")

    def detect_security_alerts(self, logs: List[Dict[str, Any]]):
        """Detect potential security issues."""
        alerts = []

        # Check for failed authentications
        failed_auth = [log for log in logs if 'INVALID_API_KEY' in str(log.get('error_message', ''))]
        if len(failed_auth) > 10:
            alerts.append(f"⚠️  HIGH: {len(failed_auth)} failed authentication attempts")

        # Check for unusual activity patterns
        action_counts = Counter(log.get('action_type') for log in logs)
        for action_type, count in action_counts.items():
            if count > 1000:
                alerts.append(f"⚠️  MEDIUM: Unusually high activity for {action_type} ({count} actions)")

        # Check for repeated failures
        failure_counts = defaultdict(int)
        for log in logs:
            if log.get('result') == 'failure':
                target = log.get('target', 'unknown')
                failure_counts[target] += 1

        for target, count in failure_counts.items():
            if count > 50:
                alerts.append(f"⚠️  MEDIUM: High failure rate for {target} ({count} failures)")

        # Check for operations outside business hours
        after_hours = []
        for log in logs:
            timestamp = log.get('timestamp')
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    if dt.hour < 6 or dt.hour > 22:
                        after_hours.append(log)
                except:
                    pass

        if len(after_hours) > 100:
            alerts.append(f"⚠️  LOW: {len(after_hours)} actions outside business hours (6am-10pm)")

        if alerts:
            print(f"\n{'='*80}")
            print("Security Alerts")
            print(f"{'='*80}")
            for alert in alerts:
                print(alert)
            print(f"{'='*80}\n")
        else:
            print("\n✓ No security alerts detected\n")

    def generate_summary(self, logs: List[Dict[str, Any]], days: int):
        """Generate overall summary."""
        if not logs:
            print("\n❌ No logs found for analysis\n")
            return

        total_actions = len(logs)
        success_count = sum(1 for log in logs if log.get('result') == 'success')
        failure_count = sum(1 for log in logs if log.get('result') == 'failure')
        success_rate = (success_count / total_actions * 100) if total_actions > 0 else 0

        # Get date range
        timestamps = [log.get('timestamp') for log in logs if log.get('timestamp')]
        if timestamps:
            dates = [datetime.fromisoformat(ts.replace('Z', '+00:00')) for ts in timestamps]
            start_date = min(dates).strftime('%Y-%m-%d')
            end_date = max(dates).strftime('%Y-%m-%d')
        else:
            start_date = end_date = 'N/A'

        print(f"\n{'='*80}")
        print(f"Audit Log Summary (Past {days} days)")
        print(f"{'='*80}")
        print(f"Date range: {start_date} to {end_date}")
        print(f"Total actions: {total_actions:,}")
        print(f"Successful: {success_count:,} ({success_rate:.1f}%)")
        print(f"Failed: {failure_count:,} ({(failure_count/total_actions*100) if total_actions > 0 else 0:.1f}%)")
        print(f"Unique action types: {len(set(log.get('action_type') for log in logs))}")
        print(f"Unique actors: {len(set(log.get('actor') for log in logs))}")
        print(f"{'='*80}\n")

    def search_logs(self, logs: List[Dict[str, Any]], query: str):
        """Search logs for specific text."""
        results = []
        query_lower = query.lower()

        for log in logs:
            log_str = json.dumps(log).lower()
            if query_lower in log_str:
                results.append(log)

        if not results:
            print(f"\n❌ No logs found matching: {query}\n")
            return

        print(f"\n{'='*80}")
        print(f"Search Results: {len(results)} log(s) found matching '{query}'")
        print(f"{'='*80}\n")

        for log in results[:20]:  # Show first 20 results
            timestamp = log.get('timestamp', 'N/A')
            action_type = log.get('action_type', 'N/A')
            actor = log.get('actor', 'N/A')
            result = log.get('result', 'N/A')
            target = log.get('target', 'N/A')

            print(f"[{timestamp}] {action_type} by {actor}")
            print(f"  Target: {target}")
            print(f"  Result: {result}")
            if log.get('error_message'):
                print(f"  Error: {log.get('error_message')}")
            print()

        if len(results) > 20:
            print(f"... and {len(results) - 20} more results\n")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Gold Tier AI Employee - Log Analysis')
    parser.add_argument('--days', type=int, default=7, help='Number of days to analyze (default: 7)')
    parser.add_argument('--search', help='Search logs for specific text')
    parser.add_argument('--action', choices=['summary', 'actions', 'success', 'actors', 'errors', 'timeline', 'security', 'all'],
                        default='all', help='Analysis to perform (default: all)')

    args = parser.parse_args()

    analyzer = LogAnalyzer()

    print(f"📊 Loading logs from past {args.days} days...")
    logs = analyzer.load_logs(days=args.days)

    if not logs:
        print("❌ No logs found")
        sys.exit(1)

    print(f"✓ Loaded {len(logs):,} log entries\n")

    if args.search:
        analyzer.search_logs(logs, args.search)
        return

    if args.action in ['summary', 'all']:
        analyzer.generate_summary(logs, args.days)

    if args.action in ['actions', 'all']:
        analyzer.analyze_action_types(logs)

    if args.action in ['success', 'all']:
        analyzer.analyze_success_rates(logs)

    if args.action in ['actors', 'all']:
        analyzer.analyze_actors(logs)

    if args.action in ['errors', 'all']:
        analyzer.analyze_errors(logs)

    if args.action in ['timeline', 'all']:
        analyzer.analyze_timeline(logs)

    if args.action in ['security', 'all']:
        analyzer.detect_security_alerts(logs)


if __name__ == "__main__":
    main()
