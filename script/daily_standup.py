import os
import sys

# 添加 root path 確保可以 import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.notion_api import fetch_daily_pages, create_summary_page
from utils.llm_processor import LLMProcessor
from utils.db_manager import save_report, init_db
from utils.notifier import send_notifications
from datetime import datetime, timedelta

def run_daily_standup_workflow():
    init_db()
    
    # 抓取昨天的資料
    yesterday = datetime.now() - timedelta(days=1)
    yesterday_str = yesterday.strftime("%Y-%m-%d")
    
    print(f"[*] Fetching Notion pages for {yesterday_str}...")
    pages = fetch_daily_pages(yesterday_str, yesterday_str)
    
    if not pages:
        print(f"[!] No pages found for {yesterday_str}. Exiting.")
        return
        
    print(f"[*] Found {len(pages)} daily pages. Processing with LLM for Standup Report...")
    
    # 偏好選用 Google API模型（如果有設置 KEY 的話），否則預設使用快速模型
    from utils.llm_processor import AVAILABLE_MODELS
    if "Google-Gemini-2.5-Flash (API)" in AVAILABLE_MODELS:
        processor = LLMProcessor(model_key="Google-Gemini-2.5-Flash (API)")
        print("    [Model] Using Google Gemini 2.5 Flash API")
    else:
        processor = LLMProcessor()
        processor.download_model_if_not_exists(lambda x: print(f"    [Model] {x}"))
    
    summary = processor.generate_summary(pages, task_type="Standup")
    
    print("[*] Summary generated. Pushing to Notion...")
    today_str = datetime.now().strftime('%Y%m%d')
    title = f"{today_str}_standup"
    notion_url = create_summary_page(title, summary, end_date_str=datetime.now().strftime("%Y-%m-%d"))
    
    print(f"[*] Pushed to Notion. URL: {notion_url}")
    
    if notion_url:
        print("[*] Sending notifications...")
        send_notifications(title, notion_url)
    
    print("[*] Saving to local database...")
    save_report(
        task_type="Standup",
        start_date=yesterday_str,
        end_date=yesterday_str,
        theme="Agile Daily Standup",
        summary_content=summary,
        notion_url=notion_url
    )
    print("[*] Workflow complete!")

if __name__ == "__main__":
    run_daily_standup_workflow()
