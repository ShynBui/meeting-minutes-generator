import argparse
import os
import re
from faster_whisper import WhisperModel


def clean_text(text: str) -> str:
    """
    Hàm này thực hiện tiền xử lý văn bản:
      - Loại bỏ khoảng trắng thừa.
      - Cắt bỏ khoảng trắng đầu/cuối.
    Có thể bổ sung thêm các bước xử lý khác nếu cần (ví dụ: chuẩn hóa dấu câu).
    """
    # Loại bỏ khoảng trắng thừa giữa các từ
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def preprocess_transcript(segments) -> list:
    """
    Duyệt qua các đoạn transcript từ model, tiền xử lý từng đoạn và trả về danh sách dictionary chứa:
      - start: thời gian bắt đầu đoạn
      - end: thời gian kết thúc đoạn
      - text: nội dung đã được làm sạch
    """
    processed_segments = []
    for segment in segments:
        cleaned_text = clean_text(segment.text)
        processed_segments.append({
            'start': segment.start,
            'end': segment.end,
            'text': cleaned_text
        })
    return processed_segments


def save_transcript(segments: list, output_file: str):
    """
    Lưu transcript đã tiền xử lý vào file văn bản.
    Mỗi đoạn được lưu kèm theo timestamp theo định dạng:
      [start_time -> end_time] transcript_text
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        for seg in segments:
            f.write(f"[{seg['start']:.2f}s -> {seg['end']:.2f}s] {seg['text']}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Preprocessing và transcription audio bằng faster-whisper."
    )
    parser.add_argument("input_audio", help="Đường dẫn tới file audio (ví dụ: audio.mp3)")
    parser.add_argument(
        "-o", "--output", default="transcript.txt",
        help="Đường dẫn file transcript đầu ra (mặc định: transcript.txt)"
    )
    parser.add_argument(
        "--model_size", default="large-v3",
        help="Kích thước model sử dụng (mặc định: large-v3)"
    )
    parser.add_argument(
        "--device", default="cuda",
        help="Thiết bị chạy inference (ví dụ: 'cuda' hoặc 'cpu')"
    )
    parser.add_argument(
        "--compute_type", default="float16",
        help="Kiểu tính toán (ví dụ: float16, int8, …)"
    )
    parser.add_argument(
        "--beam_size", type=int, default=5,
        help="Beam size cho quá trình transcribe (mặc định: 5)"
    )
    parser.add_argument(
        "--vad_filter", action="store_true",
        help="Bật VAD filter để loại bỏ phần không có lời nói"
    )
    args = parser.parse_args()

    # Kiểm tra file audio có tồn tại không
    if not os.path.exists(args.input_audio):
        print(f"Error: File '{args.input_audio}' không tồn tại.")
        exit(1)

    print("Đang load model...")
    model = WhisperModel(args.model_size, device=args.device, compute_type=args.compute_type)

    # Cấu hình tham số truyền cho hàm transcribe
    transcription_kwargs = {"beam_size": args.beam_size}
    if args.vad_filter:
        transcription_kwargs["vad_filter"] = True

    print(f"Đang chuyển đổi file {args.input_audio}...")
    segments, info = model.transcribe(args.input_audio, **transcription_kwargs)

    # Vì segments là generator nên ép nó thành list để dễ xử lý nhiều lần
    segments = list(segments)

    print(f"Ngôn ngữ phát hiện: {info.language} (xác suất: {info.language_probability:.2f})")

    # Tiền xử lý transcript
    processed_segments = preprocess_transcript(segments)

    # Lưu transcript ra file
    save_transcript(processed_segments, args.output)
    print(f"Transcript đã được lưu tại {args.output}")


if __name__ == "__main__":
    main()
