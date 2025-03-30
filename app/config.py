import os
from dotenv import load_dotenv

# Load biến môi trường từ file .env (nếu có)
load_dotenv()

# ========== Cấu hình OpenAI / Gemini ==========
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-gemini-api-key")

# ========== Cấu hình model Whisper ==========
WHISPER_MODEL_SIZE = "large-v3"
WHISPER_DEVICE = "cuda"       # hoặc "cuda"
WHISPER_COMPUTE_TYPE = "float16"
WHISPER_BEAM_SIZE = 8
WHISPER_USE_VAD = True

# ========== Đường dẫn mặc định ==========
DEFAULT_TRANSCRIPT_PATH = "transcript.txt"
DEFAULT_WORD_EXPORT_PATH = "meeting_minutes.docx"
