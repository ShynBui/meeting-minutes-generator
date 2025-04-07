import gradio as gr
import os
from app.modules.preprocessing import transcribe_audio
from app.modules.summarizer import process_transcript_file, generate_meeting_minutes
from app.modules.exporter import export_meeting_minutes_to_docx, refine_meeting_minutes
from app import config

def process_audio_to_docx(audio_file: str) -> str:
    """
    Nhận file audio, chuyển đổi thành transcript, xử lý transcript để tạo MeetingMinutes,
    refine MeetingMinutes và xuất ra file DOCX.

    Quy trình:
      - Sử dụng transcribe_audio để lấy transcript từ audio.
      - Kết hợp transcript thành văn bản và lưu tạm ra file.
      - Gọi process_transcript_file để tạo MeetingMinutes.
      - Sử dụng refine_meeting_minutes để cải thiện nội dung.
      - Xuất ra file DOCX theo định dạng hành chính Việt Nam.

    Args:
        audio_file (str): Đường dẫn tới file audio được tải lên.

    Returns:
        str: Đường dẫn file DOCX được tạo ra.
    """
    if not audio_file:
        raise ValueError("Không có file audio nào được tải lên.")

    temp_transcript = "temp_transcript.txt"
    try:
        # Bước 1: Chuyển đổi audio thành transcript
        segments, info = transcribe_audio(
            input_audio=audio_file,
            model_size=config.WHISPER_MODEL_SIZE,
            device=config.WHISPER_DEVICE,
            compute_type=config.WHISPER_COMPUTE_TYPE,
            beam_size=config.WHISPER_BEAM_SIZE,
            vad_filter=config.WHISPER_USE_VAD
        )
        # Bước 2: Kết hợp transcript thành văn bản
        transcript_text = "\n".join(seg['text'] for seg in segments)
        # Lưu transcript ra file tạm
        with open(temp_transcript, "w", encoding="utf-8") as f:
            f.write(transcript_text)

        # Bước 3: Xử lý transcript thành MeetingMinutes qua process_transcript_file
        meeting_minutes = process_transcript_file(temp_transcript, chunk_size=10, chunk_overlap=2)

        # Bước 4: Refine MeetingMinutes bằng LLM để cải thiện văn phong
        refined_minutes = refine_meeting_minutes(meeting_minutes)

        # Bước 5: Xuất MeetingMinutes đã refine ra file DOCX
        output_docx = "generated_meeting_minutes.docx"
        export_meeting_minutes_to_docx(refined_minutes, output_docx)

        # return os.path.abspath(output_docx)
        return output_docx

    except Exception as e:
        raise Exception(f"Xảy ra lỗi: {str(e)}")
    finally:
        if os.path.exists(temp_transcript):
            os.remove(temp_transcript)

# Xây dựng giao diện Gradio với output type là "filepath"
iface = gr.Interface(
    fn=process_audio_to_docx,
    inputs=gr.Audio(type="filepath", label="Tải lên file audio"),
    outputs=gr.File(label="Tải xuống biên bản họp (.docx)"),
    title="Meeting Minutes Generator",
    description="Tải lên file audio để tạo biên bản cuộc họp (DOCX). Kết quả sẽ trả về đường dẫn tới file .docx."
)


if __name__ == "__main__":
    iface.launch()
