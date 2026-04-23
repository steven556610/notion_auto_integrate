import requests
from datetime import datetime, timedelta

# 配置資訊
NOTION_TOKEN = "your_integration_token"
DATABASE_ID = "your_database_id"
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def get_weekly_pages():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    
    # 計算週間範圍 (前 5 天)
    five_days_ago = (datetime.now() - timedelta(days=5)).isoformat()
    
    query_data = {
        "filter": {
            "property": "Date",  # 確保你的 Calendar 資料庫日期屬性名稱為 Date
            "date": {
                "on_or_after": five_days_ago
            }
        }
    }
    
    response = requests.post(url, headers=HEADERS, json=query_data)
    return response.json().get("results", [])

def create_summary_page(content_text):
    url = "https://api.notion.com/v1/pages"
    
    new_page_data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {"title": [{"text": {"content": f"📅 週總結報告 - {datetime.now().strftime('%Y-%m-%d')}"}}]},
            "Date": {"date": {"start": datetime.now().strftime('%Y-%m-%d')}}
        },
        "children": [
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {"rich_text": [{"text": {"content": "週間任務總結" reconstruction}}]}
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"text": {"content": content_text}}]
                }
            }
        ]
    }
    
    requests.post(url, headers=HEADERS, json=new_page_data)

def main():
    # 1. 抓取資料
    pages = get_weekly_pages()
    
    # 2. 整理 Markdown 內容
    summary_md = "本週完成項目：\n"
    for page in pages:
        try:
            title = page["properties"]["Name"]["title"][0]["plain_text"]
            summary_md += f"- {title}\n"
        except:
            continue
    
    # 3. 寫回 Notion
    create_summary_page(summary_md)
    print("週末報告已生成！")

if __name__ == "__main__":
    main()