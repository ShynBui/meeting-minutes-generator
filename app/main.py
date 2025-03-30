import os
import sys
import shutil
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Form
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from app.modules.preprocessing import transcribe_audio, save_transcript, preprocess_transcript, clean_text
from app.modules.summarizer import generate_meeting_minutes, process_transcript_file
from app.modules.exporter import export_meeting_minutes_to_docx
from app.modules.schema import MeetingMinutes
import config



app = FastAPI(
    title="Meeting Minutes Generator API",
    description="API cho ứng dụng tạo biên bản cuộc họp từ transcript",
    version="1.0"
)


# ---------------------
# Endpoint cho chuyển đổi audio thành transcript
# ---------------------
@app.post("/transcribe", summary="Chuyển đổi audio thành transcript")
async def transcribe_endpoint(audio: UploadFile = File(...)):
    """
    Nhận file audio, lưu tạm trên đĩa, gọi hàm transcribe_audio và trả về transcript cùng thông tin.
    """
    temp_audio_path = f"temp_{audio.filename}"
    try:
        with open(temp_audio_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)

        segments, info = transcribe_audio(
            input_audio=temp_audio_path,
            model_size=config.WHISPER_MODEL_SIZE,
            device=config.WHISPER_DEVICE,
            compute_type=config.WHISPER_COMPUTE_TYPE,
            beam_size=config.WHISPER_BEAM_SIZE,
            vad_filter=config.WHISPER_USE_VAD
        )
        result = {
            "transcript": segments,
            "info": {
                "language": info.language,
                "language_probability": info.language_probability
            }
        }
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)


# ---------------------
# Endpoint cho chuyển đổi audio thành transcript và trả về file TXT
# ---------------------
# Hàm hỗ trợ xóa file sau khi trả về FileResponse
def remove_file(path: str):
    if os.path.exists(path):
        os.remove(path)

@app.post("/transcribe-txt", summary="Chuyển đổi audio thành transcript và trả về file TXT")
async def transcribe_txt_endpoint(audio: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    """
    Nhận file audio, lưu tạm trên đĩa, gọi hàm transcribe_audio, lưu transcript ra file TXT
    và trả về file TXT để client có thể tải về.
    """
    temp_audio_path = f"temp_{audio.filename}"
    temp_txt_path = f"transcript_{audio.filename}.txt"
    try:
        # Lưu file audio tạm
        with open(temp_audio_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)

        segments, info = transcribe_audio(
            input_audio=temp_audio_path,
            model_size=config.WHISPER_MODEL_SIZE,
            device=config.WHISPER_DEVICE,
            compute_type=config.WHISPER_COMPUTE_TYPE,
            beam_size=config.WHISPER_BEAM_SIZE,
            vad_filter=config.WHISPER_USE_VAD
        )
        # Lưu transcript ra file TXT
        save_transcript(segments, temp_txt_path)

        # Xóa file audio tạm
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)

        # Đặt background task để xóa file TXT sau khi trả về
        if background_tasks:
            background_tasks.add_task(remove_file, temp_txt_path)
        else:
            # Nếu không sử dụng BackgroundTasks, xóa file sau khi trả về (có thể gây lỗi nếu file bị xóa quá sớm)
            pass

        return FileResponse(
            path=temp_txt_path,
            media_type="text/plain",
            filename="transcript.txt"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------
# Endpoint cho tạo meeting minutes từ file transcript
# ---------------------
@app.post("/summarize-file", summary="Tạo meeting minutes từ file transcript")
async def summarize_file_endpoint(
        file: UploadFile = File(...),
        chunk_size: int = Form(7),
        chunk_overlap: int = Form(2)
):
    """
    Nhận file transcript dưới dạng UploadFile, lưu tạm, gọi hàm process_transcript_file để xử lý và hợp nhất meeting minutes.
    Các tham số chunk_size và chunk_overlap được truyền qua Form.
    """
    temp_file_path = f"temp_{file.filename}"
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        merged_minutes = process_transcript_file(temp_file_path, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        return JSONResponse(content=merged_minutes.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


# ---------------------
# Endpoint cho tạo meeting minutes từ transcript dạng văn bản (JSON input)
# ---------------------
class TranscriptInput(BaseModel):
    transcript: str


@app.post("/summarize", summary="Tạo meeting minutes từ transcript dạng văn bản")
async def summarize_endpoint(input_data: TranscriptInput):
    """
    Nhận transcript của cuộc họp dưới dạng văn bản và trả về meeting minutes theo định dạng JSON.
    """
    try:
        meeting_minutes = generate_meeting_minutes(input_data.transcript)
        return JSONResponse(content=meeting_minutes.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------
# Endpoint cho xuất meeting minutes ra file DOCX
# ---------------------
@app.post("/export-docx", summary="Xuất biên bản cuộc họp ra file DOCX")
async def export_docx_endpoint(meeting_minutes: MeetingMinutes, background_tasks: BackgroundTasks):
    """
    Nhận thông tin biên bản cuộc họp dưới dạng JSON (MeetingMinutes),
    xử lý và xuất ra file DOCX theo định dạng hành chính Việt Nam.
    Sau khi trả về file, file tạm sẽ được xóa trong background.
    """
    try:
        temp_docx = "temp_meeting_minutes.docx"
        export_meeting_minutes_to_docx(meeting_minutes, temp_docx)
        background_tasks.add_task(remove_file, temp_docx)
        return FileResponse(
            path=temp_docx,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename="meeting_minutes.docx"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
