# Notion Integrator & Summarizer 📅

這個專案能幫助你自動化整理 Notion 上面的每日日誌 (例如格式為 `Date_daily` 的頁面)！你可以隨時選擇時間段來生成「週報」、「月報」甚至針對特定日期的「主題追蹤報告」。

系統內部搭配了本地的 LLM (預設使用 **Qwen2.5-7B-Instruct** 的 GGUF 格式，高度優化於純 CPU 環境)，確保資料隱私且不用支付 API 費用。整理完畢的結果將會自動推回至你的 Notion Database，並且在本地的 SQLite 資料庫做留存，讓你有一個完整的 Dashboard 檢視歷史紀錄！

---

## 🌟 功能特色

1. **時間段靈活挑選**：透過 Web 介面 (Streamlit) 指定任意日期區間，可彈性生成週報告或月報告。
2. **主題式報告**：除了流水帳流水式總結，你可以問特定問題或指定主題 (例如：這週我學了什麼技術？這週情緒如何？)，LLM 將針對你的日誌回答並產出「Thematic Report」。
3. **歷史紀錄瀏覽器 (History Vault)**：你整理過的所有紀錄都會被記錄下來，幫助你回顧並快速找到 Notion 的對應連結。
4. **自動容錯機制**：如果在設定的時間區間內，某些天你忘記寫「日期_daily」的紀錄，系統會智慧地自動跳過它，不會發生報錯。
5. **高度個人化分析**：系統提示詞針對使用者專業背景設計 (Acer 癌症疫苗開發、生物資訊工程師、資料科學家等)，會自動判斷日誌內容屬性，將報告清楚分拆為【工作內容】與【Side Project】進行深度回顧與展望。
6. **自動推播通知 (LINE & Email)**：當報告生成完畢並推送到 Notion 後，會自動發送包含 Notion 連結的 LINE Notify 或 Email 通知給您。

---

## 🚀 快速開始

### 1. 準備環境

建議使用 Conda 或 venv，專案內附有 `environment.yml`，使用以下指令即可安裝全部依賴：

```bash
# 如果使用 Conda
conda env create -f enviroment.yml
# 或者如果上方指令不如預期，您可以強制指定名稱：
# conda env create -f enviroment.yml -n notion_integrator
conda activate notion_integrator

# 或者使用 pip 直接安裝
pip install streamlit requests python-dotenv sqlalchemy llama-cpp-python huggingface-hub pandas
```

### 2. 設定環境變數

請複製 `.env.example` 變成 `.env` 並填寫所有必填的 Token、ID 或是通知相關的參數：

```ini
NOTION_API_KEY=ntn_你的_Integration_Token_
NOTION_DATABASE_ID=你的_Database_ID

# [可選] 通知設定：若填寫，則在報告完成後送出 LINE Notify / Email
LINE_NOTIFY_TOKEN=你的_line_notify_token
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=你的_email@gmail.com
SENDER_PASSWORD=你的_app_password
RECEIVER_EMAIL=你的_收件email
```
> **怎麼拿到 Database ID？**
> 你可以在瀏覽器開啟你的 Notion Calendar 資料庫頁面，網址看起來像這樣：`https://www.notion.so/{workspace_name}/{DATABASE_ID}?v={view_id}`，請擷取問號前面的那段亂數。

### 3. 啟動 Web UI

在終端機輸入：

```bash
streamlit run app.py
```
App 啟動後，瀏覽器會自動開啟網頁。

1. 到左側欄確認你的模型設定。預設是 **Qwen2.5-7B-Instruct**。
2. 第一次執行特定模型時，系統會在背後自動從 HuggingFace 下載 GGUF 到 `models/` 資料夾，下載完成後就會開始推理！依據你的 CPU 性能，推理時間可能會落在 15秒 到 幾分鐘區間。

### 4. 命令列腳本 (可選)
如果你想把流程串接到系統排程 (Cronjob / Task Scheduler)，我們也提供單獨執行的命令列：
```bash
python script/workflow.py
```

---

## 🗂 目錄結構

```
notion_integrator/
│
├── app.py                 # Streamlit UI 主程式
├── environment.yml        # 環境依賴檔案
├── .env.example           # 環境變數範例
│
├── utils/                 # 工具包
│   ├── db_manager.py      # SQLite 歷史追蹤紀錄
│   ├── llm_processor.py   # 模型下載與 llama-cpp 串接
│   └── notion_api.py      # 負責 Notion CRUD (跳過無紀錄天數)
│
├── script/
│   └── workflow.py        # 獨立腳本入口點
│
├── data/                  # 供存放 history.db
└── models/                # 模型下載暫存地 (.gguf)
```
