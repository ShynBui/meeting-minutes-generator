import gradio as gr
import os
from app.modules.preprocessing import transcribe_audio
from app.modules.summarizer import process_transcript_file, generate_meeting_minutes
from app.modules.exporter import export_meeting_minutes_to_docx, refine_meeting_minutes
from app import config

def process_audio_to_docx(audio_file: str, api_key_text: str) -> str:
    """
    Nhận file audio và API key, chuyển đổi thành transcript, xử lý transcript để tạo MeetingMinutes,
    refine MeetingMinutes và xuất ra file DOCX.

    Args:
        audio_file (str): Đường dẫn tới file audio được tải lên.
        api_key_text (str): API Key dùng cho OpenAI.

    Returns:
        str: Đường dẫn file DOCX được tạo ra.
    """
    if not audio_file:
        raise ValueError("Không có file audio nào được tải lên.")
    if not api_key_text:
        raise ValueError("Vui lòng cung cấp OpenAI API Key.")

    os.environ["OPENAI_API_KEY"] = api_key_text

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
        with open(temp_transcript, "w", encoding="utf-8") as f:
            f.write(transcript_text)

        # Bước 3: Xử lý transcript thành MeetingMinutes
        meeting_minutes = process_transcript_file(temp_transcript, chunk_size=10, chunk_overlap=2)

        # Bước 4: Refine MeetingMinutes
        refined_minutes = refine_meeting_minutes(meeting_minutes)

        # Bước 5: Xuất ra DOCX
        output_docx = "generated_meeting_minutes.docx"
        export_meeting_minutes_to_docx(refined_minutes, output_docx)

        return output_docx

    except Exception as e:
        raise Exception(f"Xảy ra lỗi: {str(e)}")
    finally:
        if os.path.exists(temp_transcript):
            os.remove(temp_transcript)

# Giao diện Gradio cập nhật
iface = gr.Interface(
    fn=process_audio_to_docx,
    inputs=[
        gr.Audio(type="filepath", label="Tải lên file audio"),
        gr.Textbox(lines=1, placeholder="Nhập OpenAI API Key", label="OpenAI API Key", type="text")
    ],
    outputs=gr.File(label="Tải xuống biên bản họp (.docx)"),
    title="Meeting Minutes Generator",
    description="Tải lên file audio và nhập OpenAI API Key để tạo biên bản cuộc họp (DOCX)."
)

if __name__ == "__main__":
    iface.launch()
