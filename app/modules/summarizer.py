from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from openai import api_key

from app.modules.schema import MeetingMinutes
from app.config import OPENAI_API_KEY
import os
from typing import List

# Thiết lập API key cho OpenAI
# os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


def generate_meeting_minutes(transcript: str) -> MeetingMinutes:
    """
    Nhận transcript của cuộc họp và sử dụng LLM thông qua LangChain để trích xuất thông tin
    và tạo biên bản cuộc họp dưới dạng JSON theo schema MeetingMinutes.

    Args:
        transcript (str): Nội dung transcript của cuộc họp.

    Returns:
        MeetingMinutes: Object chứa biên bản cuộc họp với định dạng JSON chuẩn.
    """
    # Sử dụng PydanticOutputParser để kiểm soát định dạng output
    parser = PydanticOutputParser(pydantic_object=MeetingMinutes)

    # Escape các dấu ngoặc nhọn để không bị trùng với template formatter
    format_instructions = parser.get_format_instructions().replace("{", "{{").replace("}", "}}")

    prompt_template = """
Bạn là trợ lý AI thông minh, nhiệm vụ của bạn là đọc transcript cuộc họp dưới đây và trích xuất thông tin để tạo biên bản cuộc họp.
Nếu một mục không được đề cập, hãy trả về giá trị null.
Đầu ra phải tuân thủ đúng định dạng JSON với các khóa theo thứ tự như sau:
{format_instructions}

Output mẫu:
{{
  "ngay_hop": "30/03/2025",
  "gio_hop": "10:00 - null",
  "dia_diem": "Phòng họp A",
  "chu_tri": "Nguyễn Văn A",
  "nguoi_ghi_chep": "Trần Thị B",
  "thanh_vien_tham_du": ["Nguyễn Văn A", "Trần Thị B", "Lê Văn C", "Phạm Thị D"],
  "muc_tieu_cuoc_hop": "Đánh giá tiến độ và lên kế hoạch giai đoạn tiếp theo",
  "chuong_trinh_nghi_su": ["Báo cáo tiến độ", "Phân tích khó khăn", "Giải pháp và phân công nhiệm vụ"],
  "noi_dung_thao_luan": {{
    "Báo cáo tiến độ": ["Đã hoàn thành 70% công việc"],
    "Khó khăn": ["Thiếu nhân sự cho giai đoạn thử nghiệm"],
    "Giải pháp": ["Đề xuất tăng thêm 2 tester", "Lê Văn C phụ trách", "Hạn chót: 15/04/2025"]
  }},
  "cac_quyet_dinh": ["Phê duyệt bổ sung nhân sự", "Tái phân công nhiệm vụ"],
  "ket_luan": "Thống nhất hạn hoàn thành và họp tiếp theo vào 20/04/2025",
  "tai_lieu_dinh_kem": null,
  "ghi_chu": null
}}

Transcript cần xử lý:
{transcript}
"""

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["transcript"],
        partial_variables={"format_instructions": format_instructions}
    )

    # Khởi tạo LLM (ở đây dùng model "gpt-4o-mini", temperature=0 để output ổn định)
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

    formatted_prompt = prompt.format_prompt(transcript=transcript)
    response = llm.invoke(formatted_prompt.to_messages())

    # Phân tích output theo schema MeetingMinutes
    meeting_minutes = parser.parse(response.content)
    return meeting_minutes


def merge_meeting_minutes(minutes_list: List[MeetingMinutes]) -> MeetingMinutes:
    """
    Hợp nhất danh sách các object MeetingMinutes thành một object duy nhất.
    - Với các trường kiểu list, sẽ lấy hợp các phần tử (unique).
    - Với trường 'noi_dung_thao_luan' (dict), hợp nhất các key và union giá trị của các list.
    - Với các trường kiểu string, nếu có nhiều giá trị khác nhau, sẽ nối chúng lại bằng dấu chấm phẩy.

    Args:
        minutes_list (List[MeetingMinutes]): Danh sách các MeetingMinutes cần hợp nhất.

    Returns:
        MeetingMinutes: Object hợp nhất.
    """
    merged = {}
    # Lấy danh sách các key từ schema MeetingMinutes
    for key in MeetingMinutes.model_fields.keys():
        # Các trường kiểu list
        if key in ["thanh_vien_tham_du", "chuong_trinh_nghi_su", "cac_quyet_dinh", "tai_lieu_dinh_kem"]:
            union_set = set()
            for m in minutes_list:
                value = getattr(m, key)
                if value:
                    union_set.update(value)
            merged[key] = list(union_set) if union_set else None

        # Trường dạng dict: 'noi_dung_thao_luan'
        elif key == "noi_dung_thao_luan":
            merged_sub = {}
            for m in minutes_list:
                subdict = getattr(m, key)
                if subdict:
                    for subkey, sublist in subdict.items():
                        if subkey in merged_sub:
                            merged_sub[subkey].update(sublist)
                        else:
                            merged_sub[subkey] = set(sublist)
            merged[key] = {k: list(v) for k, v in merged_sub.items()} if merged_sub else None

        # Các trường dạng string
        else:
            union_set = set()
            for m in minutes_list:
                value = getattr(m, key)
                if value:
                    union_set.add(value)
            if not union_set:
                merged[key] = None
            elif len(union_set) == 1:
                merged[key] = union_set.pop()
            else:
                # Nối các giá trị khác nhau bằng dấu chấm phẩy
                merged[key] = "; ".join(sorted(union_set))
    return MeetingMinutes(**merged)


def read_transcript_in_chunks(file_path: str, chunk_size: int = 7, chunk_overlap: int = 0) -> List[str]:
    """
    Đọc file transcript và chia thành các chunk, mỗi chunk gồm chunk_size dòng,
    với số dòng chồng lấn giữa các chunk là chunk_overlap.

    Args:
        file_path (str): Đường dẫn tới file transcript.
        chunk_size (int): Số dòng trên mỗi chunk (mặc định 7).
        chunk_overlap (int): Số dòng chồng lấn giữa các chunk (mặc định 0).

    Returns:
        List[str]: Danh sách các đoạn transcript, mỗi đoạn là một chuỗi.
    """
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap phải nhỏ hơn chunk_size.")

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    chunks = []
    i = 0
    while i < len(lines):
        chunk = "".join(lines[i:i + chunk_size]).strip()
        if chunk:
            chunks.append(chunk)
        # Di chuyển chỉ số bắt đầu của chunk mới: giảm số dòng chồng lấn
        i += (chunk_size - chunk_overlap) if (chunk_size - chunk_overlap) > 0 else 1
    return chunks


def process_transcript_file(file_path: str, chunk_size: int = 7, chunk_overlap: int = 0) -> MeetingMinutes:
    """
    Đọc file transcript, chia thành các chunk theo số dòng xác định (với số dòng chồng lấn),
    gọi generate_meeting_minutes cho từng chunk và hợp nhất kết quả lại thành một object MeetingMinutes duy nhất.

    Args:
        file_path (str): Đường dẫn tới file transcript.
        chunk_size (int): Số dòng trên mỗi chunk (mặc định 7).
        chunk_overlap (int): Số dòng chồng lấn giữa các chunk (mặc định 0).

    Returns:
        MeetingMinutes: Meeting minutes hợp nhất từ toàn bộ file transcript.
    """
    chunks = read_transcript_in_chunks(file_path, chunk_size, chunk_overlap)
    meeting_minutes_list = []
    for idx, chunk in enumerate(chunks, start=1):
        print(f"Processing chunk {idx}...")
        mm = generate_meeting_minutes(chunk)
        meeting_minutes_list.append(mm)

    if meeting_minutes_list:
        merged_minutes = merge_meeting_minutes(meeting_minutes_list)
        return merged_minutes
    else:
        raise ValueError("Không có dữ liệu transcript nào để xử lý.")
