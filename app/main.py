from app import (
    transcribe_audio,
    clean_text,
    save_transcript,
    preprocess_transcript
)
import config

if __name__ == "__main__":
    # --- Cấu hình đầu vào từ file config.py ---
    input_audio = r"D:\meeting-minutes-generator\audio.mp3"  # Đường dẫn file audio đầu vào (có thể chỉnh sửa tại đây)
    output_file = config.DEFAULT_TRANSCRIPT_PATH             # Đường dẫn file transcript đầu ra từ config

    try:
        print("🔁 Đang thực hiện quá trình chuyển đổi...")
        segments, info = transcribe_audio(
            input_audio=input_audio,
            model_size=config.WHISPER_MODEL_SIZE,
            device=config.WHISPER_DEVICE,
            compute_type=config.WHISPER_COMPUTE_TYPE,
            beam_size=config.WHISPER_BEAM_SIZE,
            vad_filter=config.WHISPER_USE_VAD
        )

        print(f"🗣️  Ngôn ngữ phát hiện: {info.language} (Xác suất: {info.language_probability:.2f})")
        save_transcript(segments, output_file)
        print(f"✅ Transcript đã được lưu tại: {output_file}")

    except Exception as e:
        print(f"❌ Đã xảy ra lỗi: {e}")