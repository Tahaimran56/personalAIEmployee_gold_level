"""
CEO Briefing Scheduler for Gold Tier AI Employee

This scheduler runs the CEO Briefing generation every Monday at 8:00 AM.
It integrates with the existing scheduler system from Silver Tier.

Author: AI Employee Gold Tier
Created: 2026-02-05
"""

import schedule
import time
from datetime import datetime
import logging

from services.ceo_briefing_service import CEOBriefingService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CEOBriefingScheduler:
    """
    Scheduler for weekly CEO Briefing generation.

    Runs every Monday at 8:00 AM to generate the weekly business intelligence report.
    """

    def __init__(self):
        """Initialize the CEO Briefing Scheduler."""
        self.briefing_service = CEOBriefingService()
        self.enabled = True
        logger.info("CEO Briefing Scheduler initialized")

    def generate_briefing_job(self):
        """Job function to generate CEO Briefing."""
        try:
            logger.info("Starting scheduled CEO Briefing generation")

            briefing_file = self.briefing_service.generate_weekly_briefing()

            logger.info(f"✓ CEO Briefing generated successfully: {briefing_file}")

            # TODO: Send notification to user about new briefing
            print(f"\n{'='*60}")
            print(f"📊 CEO BRIEFING GENERATED")
            print(f"{'='*60}")
            print(f"Location: {briefing_file}")
            print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*60}\n")

        except Exception as e:
            logger.error(f"Failed to generate CEO Briefing: {e}")
            # TODO: Send error notification to user

    def schedule_briefing(self):
        """Schedule the CEO Briefing to run every Monday at 8:00 AM."""
        schedule.every().monday.at("08:00").do(self.generate_briefing_job)
        logger.info("CEO Briefing scheduled for every Monday at 8:00 AM")

    def run_now(self):
        """Manually trigger CEO Briefing generation (for testing)."""
        logger.info("Manual CEO Briefing generation triggered")
        self.generate_briefing_job()

    def start(self):
        """Start the scheduler loop."""
        self.schedule_briefing()

        logger.info("CEO Briefing Scheduler started")

        while self.enabled:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    def stop(self):
        """Stop the scheduler."""
        self.enabled = False
        logger.info("CEO Briefing Scheduler stopped")


# Integration with existing scheduler
def integrate_with_main_scheduler():
    """
    Integrate CEO Briefing scheduler with the main Silver Tier scheduler.

    This function should be called from the main scheduler.py file.
    """
    briefing_scheduler = CEOBriefingScheduler()
    briefing_scheduler.schedule_briefing()
    logger.info("CEO Briefing integrated with main scheduler")
    return briefing_scheduler


# Standalone execution
if __name__ == "__main__":
    scheduler = CEOBriefingScheduler()

    # For testing, run immediately
    print("Running CEO Briefing generation now (test mode)...")
    scheduler.run_now()

    # Then start scheduled execution
    print("\nStarting scheduled execution (every Monday at 8:00 AM)...")
    print("Press Ctrl+C to stop")

    try:
        scheduler.start()
    except KeyboardInterrupt:
        print("\nStopping CEO Briefing Scheduler...")
        scheduler.stop()
