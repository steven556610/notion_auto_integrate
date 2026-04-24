import os
import sys

# 添加 root path 確保可以 import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.notion_api import fetch_daily_pages, create_summary_page
from utils.llm_processor import LLMProcessor
from utils.db_manager import save_report, init_db
from datetime import datetime, timedelta

def run_weekly_report_workflow():
    init_db()
    
    # 預設抓取過去 5 天
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5)
    
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    
    print(f"[*] Fetching Notion pages from {start_date_str} to {end_date_str}...")
    pages = fetch_daily_pages(start_date_str, end_date_str)
    
    if not pages:
        print("[!] No pages found in the specified date range. Exiting.")
        return
        
    print(f"[*] Found {len(pages)} daily pages. Processing with LLM...")
    
    # 偏好選用 Google API模型（如果有設置 KEY 的話），否則預設使用快速模型
    from utils.llm_processor import AVAILABLE_MODELS
    if "Google-Gemini-1.5-Pro (API)" in AVAILABLE_MODELS:
        processor = LLMProcessor(model_key="Google-Gemini-1.5-Pro (API)")
        print("    [Model] Using Google Gemini 1.5 Pro API")
    else:
        processor = LLMProcessor()
        processor.download_model_if_not_exists(lambda x: print(f"    [Model] {x}"))
    
    summary = processor.generate_summary(pages, task_type="Weekly")
    
    print("[*] Summary generated. Pushing to Notion...")
    title = f"{end_date.strftime('%Y%m%d')}_weekly"
    notion_url = create_summary_page(title, summary, end_date_str=end_date_str)
    
    print(f"[*] Pushed to Notion. URL: {notion_url}")
    
    print("[*] Saving to local database...")
    save_report(
        task_type="Weekly",
        start_date=start_date_str,
        end_date=end_date_str,
        theme="",
        summary_content=summary,
        notion_url=notion_url
    )
    print("[*] Workflow complete!")

if __name__ == "__main__":
    run_weekly_report_workflow()