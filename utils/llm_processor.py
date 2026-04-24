import os
from huggingface_hub import hf_hub_download
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

try:
    from llama_cpp import Llama
except ImportError:
    Llama = None

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")

# 常見的模型列表
AVAILABLE_MODELS = {
    "Qwen2.5-7B-Instruct (Default - Fast)": {
        "repo_id": "bartowski/Qwen2.5-7B-Instruct-GGUF",
        "filename": "Qwen2.5-7B-Instruct-Q4_K_M.gguf",
        "chat_format": "chatml"
    },
    "Qwen2.5-14B-Instruct (Slower - Better)": {
        "repo_id": "bartowski/Qwen2.5-14B-Instruct-GGUF",
        "filename": "Qwen2.5-14B-Instruct-Q4_K_M.gguf",
        "chat_format": "chatml"
    },
    "Llama-3-8B-Instruct (Alternative)": {
        "repo_id": "QuantFactory/Meta-Llama-3-8B-Instruct-GGUF",
        "filename": "Meta-Llama-3-8B-Instruct.Q4_K_M.gguf",
        "chat_format": "llama-3"
    }
}

# 動態新增 Google API 選項
if GOOGLE_API_KEY:
    AVAILABLE_MODELS["Google-Gemini-1.5-Pro (API)"] = {
        "is_api": True,
        "model_name": "gemini-1.5-pro"
    }
    AVAILABLE_MODELS["Google-Gemini-1.5-Flash (API)"] = {
        "is_api": True,
        "model_name": "gemini-1.5-flash"
    }

class LLMProcessor:
    def __init__(self, model_key="Qwen2.5-7B-Instruct (Default - Fast)"):
        if model_key not in AVAILABLE_MODELS:
            model_key = "Qwen2.5-7B-Instruct (Default - Fast)"
        self.model_info = AVAILABLE_MODELS[model_key]
        self.is_api = self.model_info.get("is_api", False)
        
        if not self.is_api:
            self.model_path = os.path.join(MODELS_DIR, self.model_info["filename"])
            self.llm = None
            if not os.path.exists(MODELS_DIR):
                os.makedirs(MODELS_DIR)

    def download_model_if_not_exists(self, progress_callback=None):
        if self.is_api:
            return
        if not os.path.exists(self.model_path):
            if progress_callback:
                progress_callback(f"Downloading {self.model_info['filename']} from HuggingFace. This may take a while...")
            
            # hf_hub_download 會自動將快取檔案對應到指定路徑
            downloaded_path = hf_hub_download(
                repo_id=self.model_info["repo_id"],
                filename=self.model_info["filename"],
                local_dir=MODELS_DIR,
                local_dir_use_symlinks=False
            )
            # rename or ensure it matches
            if downloaded_path != self.model_path:
                os.rename(downloaded_path, self.model_path)
                
            if progress_callback:
                progress_callback("Download completed!")
                
    def load_model(self):
        if self.is_api:
            import google.generativeai as genai
            genai.configure(api_key=GOOGLE_API_KEY)
            self.llm = genai
            
            try:
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                target_name = "models/" + self.model_info["model_name"]
                
                # 若指定的模型不在可用清單中，自動尋替代方案
                if target_name not in available_models and self.model_info["model_name"] not in available_models:
                    print(f"[Warn] {target_name} is not available in your API tier. Available models: {available_models}")
                    fallback = None
                    for m in available_models:
                        if "gemini-1.5-flash" in m: fallback = m; break
                    if not fallback:
                        for m in available_models:
                            if "gemini-1.5-pro" in m: fallback = m; break
                    if not fallback:
                        for m in available_models:
                            if "gemini-pro" in m and "vision" not in m: fallback = m; break
                            
                    if fallback:
                        self.model_info["model_name"] = fallback.replace("models/", "")
                        print(f"[*] Auto-fell back to available model: {self.model_info['model_name']}")
            except Exception as e:
                print(f"[Error] Failed to verify model availability: {e}")
                
        elif self.llm is None:
            if Llama is None:
                raise ImportError("llama_cpp is not installed. Please install it to use local GGUF models.")
            self.llm = Llama(
                model_path=self.model_path,
                n_ctx=4096,          # 上下文長度，足以容納多天報告
                n_threads=max(1, os.cpu_count() - 2),  # 預留核心
                chat_format=self.model_info.get("chat_format", "chatml"),
                verbose=False
            )
            
    def generate_summary(self, daily_records, task_type, theme=""):
        self.load_model()
        
        # 準備資料文本
        context_text = ""
        for record in daily_records:
            context_text += f"\n--- Date: {record['date']} ---\n{record['content']}\n"
            
        sys_prompt = (
            "你是一個專業的助理，擅長分析和整理個人的工作日誌與生活紀錄。\n"
            "目前的背景資訊：\n"
            "使用者在 acer 從事癌症疫苗相關的開發工作與生物資訊研究。\n"
            "身兼生物資訊工程師、資料科學家和機器學習工程師，工作範圍也包含管理兩台 server。\n"
            "請「務必」以繁體中文撰寫所有回應，並將最後的結果排版為 Markdown 格式。"
        )
        
        if task_type == "Weekly":
            user_prompt = (
                "請幫我分析以下這幾天的日誌紀錄，並產生一份「週報告」。\n"
                "請務必將內容嚴格區分為兩大類別：【工作內容】與【Side Project】。\n\n"
                "【工作內容】需要包含（例如 acer 開發相關、生資處理、server 管理等日常工作事項）：\n"
                "- 本週進度總結與每天大概做了哪些事項。\n"
                "- 列出完成了哪些項目，以及完成到什麼程度（提供細項）。\n"
                "- 未來可以持續怎麼做或優化。\n"
                "- 下週預計要完成的目標。\n\n"
                "【Side Project】需要包含（非日常工作的個人專案，例如 portrait、notion_integrator 等）：\n"
                "- 目前特定專案進行到什麼程度。\n"
                "- 有哪些可能的發想可以繼續進行。\n"
                "- 假設要持續往後開發，未來該怎麼優化、應學習哪些新東西，或是推薦可能需要閱讀什麼文獻。\n\n"
                "請完全以繁體中文 (Traditional Chinese) 和 Markdown 格式輸出。\n\n"
                f"日誌內容：\n{context_text}"
            )
        elif task_type == "Monthly":
            user_prompt = f"請幫我分析以下這個月的日誌紀錄，並產生一份「月報告」。請限定使用繁體中文，以宏觀的角度總結這個月的重點成就與趨勢，並以 Markdown 格式呈現。\n\n日誌內容：\n{context_text}"
        elif task_type == "Custom":
            user_prompt = f"請幫我分析以下的日誌紀錄，並專注於「{theme}」這個特定主題進行總結與報告。請限定使用繁體中文，並以 Markdown 格式呈現。\n\n日誌內容：\n{context_text}"
        else:
            user_prompt = f"請限定使用繁體中文總結以下資料，並以 Markdown 格式呈現：\n{context_text}"

        if self.is_api:
            import google.generativeai as genai
            model = genai.GenerativeModel(
                model_name=self.model_info["model_name"],
                system_instruction=sys_prompt
            )
            response = model.generate_content(
                user_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                )
            )
            return response.text
        else:
            messages = [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_prompt}
            ]

            # 呼叫 Llama cpp 進行 inference
            response = self.llm.create_chat_completion(
                messages=messages,
                max_tokens=1500,
                temperature=0.7,
            )
            
            return response["choices"][0]["message"]["content"]
