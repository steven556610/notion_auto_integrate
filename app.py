import streamlit as st
import os
from datetime import datetime, timedelta
import pandas as pd

from utils.notion_api import fetch_daily_pages, create_summary_page, check_config
from utils.llm_processor import LLMProcessor, AVAILABLE_MODELS
from utils.db_manager import init_db, save_report, get_all_reports
from utils.notifier import send_notifications

# Initialize DB on startup
init_db()

st.set_page_config(
    page_title="Notion Integrator & Summarizer",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Notion Daily Logs Summarizer 📅")

# --- SIDEBAR: Model Selection ---
st.sidebar.header("⚙️ Configuration")

selected_model = st.sidebar.selectbox(
    "Choose LLM Model:",
    list(AVAILABLE_MODELS.keys()),
    index=0,
    help="Qwen2.5-7B is recommended for a balanced speed/quality on CPU."
)

st.sidebar.markdown("---")
st.sidebar.info("Make sure your `.env` file is properly configured with:\n- `NOTION_API_KEY`\n- `NOTION_DATABASE_ID`")

# --- Tabs Setup ---
tab1, tab2, tab3 = st.tabs(["🗓️ Time-Based Report", "🎯 Thematic Report", "🗄️ History Vault"])

with tab1:
    st.header("Generate Weekly/Monthly Reports")
    st.write("Select a date range. The system will extract your `Date_daily` pages and compile them.")
    
    col1, col2 = st.columns(2)
    with col1:
        default_start = datetime.today() - timedelta(days=6)
        start_date = st.date_input("Start Date", value=default_start)
    with col2:
        end_date = st.date_input("End Date", value=datetime.today())
        
    report_type = st.radio("Report Type:", ["Weekly", "Monthly"], horizontal=True)
    
    if st.button("Generate Time-Based Report", type="primary"):
        if start_date > end_date:
            st.error("Start Date must be before End Date!")
        else:
            with st.spinner("Fetching pages from Notion..."):
                try:
                    pages = fetch_daily_pages(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
                except Exception as e:
                    st.error(f"Configuration Error: {e}")
                    pages = []
                    
            if not pages:
                st.warning("No missing pages or dates found in this range.")
            else:
                st.success(f"Found {len(pages)} daily pages.")
                
                status_placeholder = st.empty()
                status_placeholder.info("Initializing Model (will download if not exists)...")
                
                processor = LLMProcessor(model_key=selected_model)
                processor.download_model_if_not_exists(lambda x: status_placeholder.info(x))
                
                status_placeholder.info("Generating Report... This might take a while on CPU depending on the model size.")
                with st.spinner("LLM Generating..."):
                    summary = processor.generate_summary(pages, task_type=report_type)
                
                st.markdown("### Generated Summary Preview")
                st.markdown(summary)
                
                status_placeholder.info("Pushing back to Notion...")
                title_date_format = end_date.strftime("%Y%m%d")
                page_title = f"{title_date_format}_{report_type.lower()}"
                
                notion_url = create_summary_page(page_title, summary)
                if notion_url:
                    send_notifications(page_title, notion_url)
                    st.success(f"Successfully generated and pushed to Notion! [View Page]({notion_url})")
                    save_report(report_type, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"), "", summary, notion_url)
                else:
                    st.error("Failed to push to Notion. Check terminal output.")

with tab2:
    st.header("Generate Thematic Report")
    st.write("Specify a topic/question and let the AI synthesize an answer strictly from the selected date range.")
    
    t_col1, t_col2 = st.columns(2)
    with t_col1:
        t_start_date = st.date_input("Start Date (Theme)", value=datetime.today() - timedelta(days=6))
    with t_col2:
        t_end_date = st.date_input("End Date (Theme)", value=datetime.today())
        
    theme_input = st.text_input("Enter your specific Theme or Question:", placeholder="例如：我這週主要閱讀了哪些技術文章？")
    
    if st.button("Generate Thematic Report", type="primary"):
        if t_start_date > t_end_date:
            st.error("Start Date must be before End Date!")
        elif not theme_input.strip():
            st.warning("Please enter a theme/question.")
        else:
            with st.spinner("Fetching pages from Notion..."):
                try:
                    pages = fetch_daily_pages(t_start_date.strftime("%Y-%m-%d"), t_end_date.strftime("%Y-%m-%d"))
                except Exception as e:
                    st.error(f"Configuration Error: {e}")
                    pages = []
                    
            if not pages:
                st.warning("No pages found in this range.")
            else:
                status_placeholder2 = st.empty()
                status_placeholder2.info("Initializing Model...")
                
                processor = LLMProcessor(model_key=selected_model)
                processor.download_model_if_not_exists(lambda x: status_placeholder2.info(x))
                
                status_placeholder2.info(f"Synthesizing theme: {theme_input}")
                with st.spinner("LLM Generating..."):
                    summary = processor.generate_summary(pages, task_type="Custom", theme=theme_input)
                
                st.markdown("### Thematic Report Preview")
                st.markdown(summary)
                
                status_placeholder2.info("Pushing to Notion...")
                page_title = f"{t_end_date.strftime('%Y%m%d')}_theme_{theme_input[:10]}"
                
                notion_url = create_summary_page(page_title, summary)
                if notion_url:
                    send_notifications(page_title, notion_url)
                    st.success(f"Successfully generated and pushed to Notion! [View Page]({notion_url})")
                    save_report("Custom", t_start_date.strftime("%Y-%m-%d"), t_end_date.strftime("%Y-%m-%d"), theme_input, summary, notion_url)
                else:
                    st.error("Failed to push to Notion.")

with tab3:
    st.header("🗄️ History Vault")
    st.write("A record of all reports you have previously compiled and saved to the database.")
    
    if st.button("Refresh History"):
        # The screen will naturally re-render
        pass
        
    history = get_all_reports()
    if not history:
        st.info("No reports generated yet.")
    else:
        df = pd.DataFrame(history)
        df = df[["id", "task_type", "theme", "start_date", "end_date", "created_at", "notion_url"]]
        # Display as a dataframe
        st.dataframe(df, use_container_width=True)
