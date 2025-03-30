import os
import re
from faster_whisper import WhisperModel, BatchedInferencePipeline

def clean_text(text: str) -> str:
    """
    Thực hiện tiền xử lý văn bản:
      - Loại bỏ khoảng trắng thừa giữa các từ.
      - Cắt bỏ khoảng trắng đầu/cuối.
    Có thể mở rộng thêm các bước xử lý (ví dụ: chuẩn hóa dấu câu) nếu cần.
    """
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def preprocess_transcript(segments: list) -> list:
    """
    Tiền xử lý từng đoạn transcript, trả về danh sách các dictionary với các thông tin:
      - start: thời gian bắt đầu đoạn
      - end: thời gian kết thúc đoạn
      - text: nội dung đã được làm sạch
    """
    processed_segments = []
    for segment in segments:
        processed_segments.append({
            'start': segment.start,
            'end': segment.end,
            'text': clean_text(segment.text)
        })
    return processed_segments


def transcribe_audio(input_audio: str = 'audio.mp3',
                     model_size: str = 'base',
                     device: str = 'cpu',
                     compute_type: str = 'int8',
                     beam_size: int = '5',
                     vad_filter: bool = True) -> tuple:
    """
    Thực hiện chuyển đổi file audio thành transcript sử dụng Faster Whisper.

    Args:
        input_audio (str): Đường dẫn tới file audio (ví dụ: audio.mp3).
        model_size (str): Kích thước model sử dụng (mặc định lấy từ config).
        device (str): Thiết bị chạy inference (mặc định lấy từ config).
        compute_type (str): Kiểu tính toán (mặc định lấy từ config).
        beam_size (int): Số lượng beam cho quá trình transcribe (mặc định lấy từ config).
        vad_filter (bool): Bật VAD filter để loại bỏ phần không có lời nói (mặc định lấy từ config).

    Returns:
        tuple: (processed_segments, info) trong đó processed_segments là danh sách transcript đã tiền xử lý,
               info chứa thông tin chi tiết về quá trình transcription (ví dụ: ngôn ngữ, xác suất,...).

    Raises:
        FileNotFoundError: Nếu file audio không tồn tại.
    """
    if not os.path.exists(input_audio):
        raise FileNotFoundError(f"File '{input_audio}' không tồn tại.")

    # Khởi tạo model Faster Whisper với các tham số lấy từ config
    model = WhisperModel(model_size, device=device, compute_type=compute_type)

    # Cấu hình tham số cho quá trình transcription
    transcription_kwargs = {"beam_size": beam_size}
    if vad_filter:
        transcription_kwargs["vad_filter"] = True

    # Chạy quá trình transcription
    batched_model = BatchedInferencePipeline(model=model)
    segments, info = batched_model.transcribe(input_audio, **transcription_kwargs, batch_size=32)
    segments = list(segments)  # Ép generator thành list để dễ xử lý lại sau này
    processed_segments = preprocess_transcript(segments)
    return processed_segments, info


def save_transcript(segments: list, output_file: str) -> None:
    """
    Lưu transcript đã tiền xử lý vào file văn bản.
    Mỗi đoạn được lưu theo định dạng:
      [start_time -> end_time] transcript_text
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        for seg in segments:
            f.write(f"[{seg['start']:.2f}s -> {seg['end']:.2f}s] {seg['text']}\n")



##Hãy subscribe cho kênh Ghiền Mì Gõ Để không bỏ lỡ những video hấp dẫn
##Hãy đăng ký kênh để ủng hộ kênh của mình nhé!

