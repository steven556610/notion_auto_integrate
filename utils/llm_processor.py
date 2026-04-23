import os
from huggingface_hub import hf_hub_download
from llama_cpp import Llama

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

class LLMProcessor:
    def __init__(self, model_key="Qwen2.5-7B-Instruct (Default - Fast)"):
        self.model_info = AVAILABLE_MODELS.get(model_key, AVAILABLE_MODELS["Qwen2.5-7B-Instruct (Default - Fast)"])
        self.model_path = os.path.join(MODELS_DIR, self.model_info["filename"])
        self.llm = None
        
        if not os.path.exists(MODELS_DIR):
            os.makedirs(MODELS_DIR)

    def download_model_if_not_exists(self, progress_callback=None):
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
        if self.llm is None:
            self.llm = Llama(
                model_path=self.model_path,
                n_ctx=4096,          # 上下文長度，足以容納多天報告
                n_threads=max(1, os.cpu_count() - 2),  # 預留核心
                chat_format=self.model_info["chat_format"],
                verbose=False
            )
            
    def generate_summary(self, daily_records, task_type, theme=""):
        self.load_model()
        
        # 準備資料文本
        context_text = ""
        for record in daily_records:
            context_text += f"\n--- Date: {record['date']} ---\n{record['content']}\n"
            
        sys_prompt = "你是一個專業的助理，擅長分析和整理個人的工作日誌與生活紀錄。"
        
        if task_type == "Weekly":
            user_prompt = f"請幫我分析以下這幾天的日誌紀錄，並產生一份「週報告」。請將內容結構化（例如：本週重點、完成事項、未完成/挑戰、下週計畫等）。\n\n日誌內容：\n{context_text}"
        elif task_type == "Monthly":
            user_prompt = f"請幫我分析以下這個月的日誌紀錄，並產生一份「月報告」。請以宏觀的角度總結這個月的重點成就與趨勢。\n\n日誌內容：\n{context_text}"
        elif task_type == "Custom":
            user_prompt = f"請幫我分析以下的日誌紀錄，並專注於「{theme}」這個特定主題進行總結與報告。\n\n日誌內容：\n{context_text}"
        else:
            user_prompt = f"請總結以下資料：\n{context_text}"

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
