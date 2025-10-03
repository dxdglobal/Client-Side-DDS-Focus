"""
Daily Logs Automation Script

This script can be scheduled to run daily (e.g., using Windows Task Scheduler)
to automatically generate and upload daily logs reports for all employees.

Usage:
    python daily_logs_automation.py
    python daily_logs_automation.py --date 2025-09-09  # For specific date
    python daily_logs_automation.py --email employee@company.com  # For specific employee
"""

import sys
import os
import argparse
import logging
from datetime import datetime, timedelta

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from moduller.daily_logs_reporter import (
    generate_daily_reports_for_all_employees,
    generate_daily_report_for_employee
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('daily_logs_automation.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Daily Logs Automation Script')
    parser.add_argument('--date', type=str, help='Date in YYYY-MM-DD format (default: today)')
    parser.add_argument('--email', type=str, help='Specific employee email (if not provided, processes all employees)')
    parser.add_argument('--yesterday', action='store_true', help='Use yesterday\'s date')
    
    args = parser.parse_args()
    
    # Determine target date
    if args.yesterday:
        target_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    elif args.date:
        target_date = args.date
    else:
        target_date = datetime.now().strftime("%Y-%m-%d")
    
    logger.info("🚀 Starting daily logs automation for date: %s", target_date)
    
    try:
        if args.email:
            # Process specific employee
            logger.info("👤 Processing specific employee: %s", args.email)
            result = generate_daily_report_for_employee(args.email, target_date)
            
            if result["status"] == "success":
                logger.info("✅ Report generated successfully for %s", args.email)
                logger.info("📁 S3 URL: %s", result["url"])
                print(f"✅ SUCCESS: Report uploaded for {args.email}")
                print(f"📁 URL: {result['url']}")
            else:
                logger.error("❌ Failed to generate report for %s: %s", args.email, result["message"])
                print(f"❌ FAILED: {result['message']}")
                sys.exit(1)
        else:
            # Process all employees
            logger.info("👥 Processing all employees")
            results = generate_daily_reports_for_all_employees(target_date)
            
            if not results:
                logger.warning("⚠️ No employees found or processed")
                print("⚠️ No employees found to process")
                sys.exit(0)
            
            # Count successes and failures
            successful = [r for r in results if r.get("status") == "success"]
            failed = [r for r in results if r.get("status") != "success"]
            
            logger.info("📊 Processing complete: %d successful, %d failed", len(successful), len(failed))
            
            print(f"\n📊 Daily Logs Automation Results for {target_date}")
            print(f"=" * 60)
            print(f"✅ Successful uploads: {len(successful)}")
            print(f"❌ Failed uploads: {len(failed)}")
            print(f"📋 Total employees processed: {len(results)}")
            
            if successful:
                print(f"\n✅ Successful Uploads:")
                for result in successful:
                    print(f"   👤 {result['email']}: {result.get('entries_count', 0)} entries")
                    logger.info("✅ Success: %s (%d entries)", result['email'], result.get('entries_count', 0))
            
            if failed:
                print(f"\n❌ Failed Uploads:")
                for result in failed:
                    print(f"   👤 {result['email']}: {result.get('error', 'Unknown error')}")
                    logger.error("❌ Failed: %s - %s", result['email'], result.get('error', 'Unknown error'))
            
            # Exit with error code if any uploads failed
            if failed:
                logger.error("❌ Some uploads failed. Check logs for details.")
                sys.exit(1)
            else:
                logger.info("✅ All uploads completed successfully")
                print(f"\n🎉 All daily reports uploaded successfully!")
    
    except Exception as e:
        logger.error("❌ Automation script failed: %s", e)
        print(f"❌ CRITICAL ERROR: {e}")
        sys.exit(1)

def schedule_info():
    """Print information about scheduling this script"""
    print("""
📅 Scheduling Information:

Windows Task Scheduler:
  1. Open Task Scheduler
  2. Create Basic Task
  3. Set trigger to Daily at desired time (e.g., 11:59 PM)
  4. Set action to start program:
     Program: python
     Arguments: "C:\\path\\to\\daily_logs_automation.py" --yesterday
     Start in: C:\\path\\to\\project\\folder

Linux/Mac Cron:
  Add to crontab (crontab -e):
  59 23 * * * cd /path/to/project && python daily_logs_automation.py --yesterday

Example Usage:
  python daily_logs_automation.py                           # Today's reports
  python daily_logs_automation.py --yesterday               # Yesterday's reports  
  python daily_logs_automation.py --date 2025-09-09        # Specific date
  python daily_logs_automation.py --email user@company.com # Specific employee
""")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--schedule-info":
        schedule_info()
    else:
        main()
