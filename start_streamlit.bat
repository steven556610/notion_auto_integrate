@echo off
title Notion Integrator Streamlit Runner
cd /d "D:\code\notion_integrator"

echo [*] Starting Streamlit App for Notion Integrator...

:: 優先嘗試使用 conda 啟動
call conda activate notion_integrator 2>nul
if %errorlevel% equ 0 (
    streamlit run app.py
    goto end
)

:: 若失敗，嘗試尋找預設的 Miniconda/Anaconda 環境路徑執行
if exist "C:\Users\steven.su\miniconda3\envs\notion_integrator\python.exe" (
    "C:\Users\steven.su\miniconda3\envs\notion_integrator\python.exe" -m streamlit run app.py
    goto end
)

if exist "C:\Users\steven.su\anaconda3\envs\notion_integrator\python.exe" (
    "C:\Users\steven.su\anaconda3\envs\notion_integrator\python.exe" -m streamlit run app.py
    goto end
)

:: 最後的後備方案：直接呼叫 streamlit（假設已加入環境變數）
streamlit run app.py

:end
echo.
echo [*] Application closed.
pause
