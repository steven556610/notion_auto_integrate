import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_API_KEY", "")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID", "")

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def check_config():
    if not NOTION_TOKEN or NOTION_TOKEN == "ntn_your_api_key_here":
        raise ValueError("Please provide a valid NOTION_API_KEY in .env")
    if not DATABASE_ID or DATABASE_ID == "your_database_id_here":
        raise ValueError("Please provide a valid NOTION_DATABASE_ID in .env")

def get_page_content(page_id):
    """
    獲取指定 notion page 裡面的 block content。
    這裡簡單提取所有 paragraph 和 bulleted_list_item 的文字。
    """
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        return ""
    
    blocks = response.json().get("results", [])
    text_content = ""
    for block in blocks:
        block_type = block["type"]
        if block_type in ["paragraph", "bulleted_list_item", "numbered_list_item", "heading_1", "heading_2", "heading_3"]:
            rich_texts = block[block_type].get("rich_text", [])
            for rt in rich_texts:
                text_content += rt.get("plain_text", "")
            text_content += "\n"
    return text_content

def fetch_daily_pages(start_date_str, end_date_str):
    """
    獲取 start_date 到 end_date 範圍內的所有日誌頁面。
    如果有些日期沒有 "日期_daily" 的頁面，它會自然忽略。
    """
    check_config()
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    
    # 結束日期我們加上一天來做 before 條件過濾
    end_date_obj = datetime.strptime(end_date_str, "%Y-%m-%d")
    next_day_str = (end_date_obj + timedelta(days=1)).strftime("%Y-%m-%d")

    query_data = {
        "filter": {
            "and": [
                {
                    "property": "Date",  # 假設日期欄位叫做 Date
                    "date": {
                        "on_or_after": start_date_str
                    }
                },
                {
                    "property": "Date",
                    "date": {
                        "before": next_day_str
                    }
                }
            ]
        }
    }
    
    response = requests.post(url, headers=HEADERS, json=query_data)
    if response.status_code != 200:
        print(f"Error fetching from Notion: {response.text}")
        return []
    
    results = response.json().get("results", [])
    
    daily_records = []
    for page in results:
        # Extract title (Name)
        try:
            title = page["properties"]["Name"]["title"][0]["plain_text"]
        except (KeyError, IndexError):
            title = "Untitled"
            
        # Optional: Only parse pages containing "_daily" in their title, if that's a strict requirement.
        # But generally if it's in the designated date range, we might just parse it. Let's strictly check if the user asked.
        if "_daily" not in title and "_Daily" not in title:
            # 依據提示：如果當天沒有看到 "日期_daily" 的page，就跳過那天
            continue
            
        content = get_page_content(page["id"])
        
        # Extract the date it belongs to
        try:
            page_date = page["properties"]["Date"]["date"]["start"]
        except Exception:
            page_date = "Unknown Date"
            
        daily_records.append({
            "title": title,
            "date": page_date,
            "content": content,
            "url": page["url"]
        })
        
    # Sort by date
    daily_records = sorted(daily_records, key=lambda x: x["date"])
    
    return daily_records


def create_summary_page(title, content_text):
    """
    將產生的總結報告寫回 Notion。
    寫入一個單純的 page，包含報告內容。
    """
    check_config()
    url = "https://api.notion.com/v1/pages"
    
    # Simple chunking if the content is too long for one block
    # Notion has a 2000 character limit per text block.
    # We will chunk by paragraphs to be safe
    paragraphs = content_text.split('\n\n')
    blocks = []
    for p in paragraphs:
        if not p.strip(): continue
        # if a single sequence is > 2000 chars, it might error, but we do simple chunking
        chunk_len = 2000
        for i in range(0, len(p), chunk_len):
            chunk = p[i:i+chunk_len]
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"text": {"content": chunk}}]
                }
            })
    
    # 限制 blocks 的數量（Notion API 一次最多 100 個 blocks）
    blocks = blocks[:100]
    
    new_page_data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {"title": [{"text": {"content": title}}]},
            "Date": {"date": {"start": datetime.now().strftime('%Y-%m-%d')}}
        },
        "children": blocks
    }
    
    response = requests.post(url, headers=HEADERS, json=new_page_data)
    if response.status_code == 200:
        return response.json().get("url", "")
    else:
        print(f"Error creating Notion page: {response.text}")
        return ""
