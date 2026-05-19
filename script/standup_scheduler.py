import os
import sys
import time
import logging
import schedule
import subprocess

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_daily_task():
    logger.info("Running daily standup task...")
    script_path = os.path.join(os.path.dirname(__file__), 'daily_standup.py')
    try:
        subprocess.run([sys.executable, script_path], check=True)
        logger.info("Daily standup task completed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running daily standup task: {e}")

def main():
    logger.info("Starting scheduler. Daily standup task is scheduled at 09:00 AM.")
    # Set the schedule
    schedule.every().day.at("09:00").do(run_daily_task)
    
    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
