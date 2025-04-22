import os
from dotenv import load_dotenv
from faster_whisper import WhisperModel

load_dotenv()
##Cau hinh cho Whisper

WHISPER_MODEL_SIZE = 'medium'
WHISPER_DEVICE = 'cpu'
WHISPER_COMPUTE_TYPE = 'int8'
WHISPER_BEAM_SIZE = 8
WHISPER_USE_VAD = True


## OPen ai key
OPENAI_API_KEY = os.getenv('OPEN_AI_KEY')