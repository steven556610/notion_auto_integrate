我想要分析平日的紀錄，然後在禮拜六產生一個週報告。
今天是4/24，可以幫我分析4/13~4/17
開頭會是 "日期_daily"的page
分析的內容主要放在notion的calender 上面。
然後每周執行一次，最後產生一個 "日期_weekly"的page。上面的例子，我要看到 20260418_weekly的page，裡面有週報的markdown file
有放一個example 腳本在script/workflow.py。
幫我整理環境，也要包含有ci/cd，也要有一個完整的read me
並且 key : [MASKED_KEY] 。這一個key 是notion api key，我設定了一個internal connection 名為 LLM_associate。
幫我撰寫好相關的腳本，也下載模型來分析我每天的報告。
模型的大小可以選擇夠大的，Qwen系列就不錯，30B 應該可以，但我都是用CPU在跑。