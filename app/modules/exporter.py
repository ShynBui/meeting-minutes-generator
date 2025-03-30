from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from app.modules.schema import MeetingMinutes
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from docx.shared import Pt, Cm
from app.config import OPENAI_API_KEY
import os
import concurrent.futures

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

def export_meeting_minutes_to_docx(meeting_minutes: MeetingMinutes, output_file: str) -> None:
    """
    Xuất meeting minutes thành file DOCX với định dạng chuẩn văn bản hành chính Việt Nam,
    mô phỏng layout như biểu mẫu (có phần tiêu ngữ, số hiệu, chữ ký, ...).

    Args:
        meeting_minutes (MeetingMinutes): Object chứa thông tin biên bản cuộc họp.
        output_file (str): Đường dẫn file DOCX đầu ra.
    """
    document = Document()

    # Thiết lập font mặc định (Times New Roman, size 13)
    style = document.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(13)

    # Đặt đơn vị đo lề (nếu cần)
    section = document.sections[0]
    section.left_margin = Cm(3.0)
    section.right_margin = Cm(2.0)
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)

    # -------- PHẦN HEADER (TIÊU NGỮ, SỐ HIỆU) --------
    # Sử dụng bảng 2 cột để mô phỏng cột trái và cột phải
    table = document.add_table(rows=2, cols=2)
    table.alignment = WD_ALIGN_PARAGRAPH.CENTER
    table.allow_autofit = False
    table.columns[0].width = Cm(8)
    table.columns[1].width = Cm(8)

    # Cột trái: Tên cơ quan, tổ chức
    cell_left_1 = table.cell(0, 0).paragraphs[0]
    cell_left_1.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run_left_1 = cell_left_1.add_run("TÊN CƠ QUAN, TỔ CHỨC CHỦ QUẢN (1)\nTÊN CƠ QUAN, TỔ CHỨC (2)\n-------")
    run_left_1.font.name = 'Times New Roman'
    run_left_1.font.size = Pt(13)
    run_left_1.bold = True

    # Cột phải: Tiêu ngữ
    cell_right_1 = table.cell(0, 1).paragraphs[0]
    cell_right_1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_right_1 = cell_right_1.add_run("CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM\nĐộc lập - Tự do - Hạnh phúc\n-------")
    run_right_1.font.name = 'Times New Roman'
    run_right_1.font.size = Pt(13)
    run_right_1.bold = True

    # Hàng 2: Số hiệu
    cell_left_2 = table.cell(1, 0).paragraphs[0]
    cell_left_2.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run_left_2 = cell_left_2.add_run("")  # để trống

    cell_right_2 = table.cell(1, 1).paragraphs[0]
    cell_right_2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_right_2 = cell_right_2.add_run("Số: ....../BB-....(3)....")
    run_right_2.font.name = 'Times New Roman'
    run_right_2.font.size = Pt(13)

    # Xuống dòng sau bảng
    document.add_paragraph("")

    # -------- TIÊU ĐỀ CHÍNH --------
    title_para = document.add_paragraph()
    title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_title = title_para.add_run("BIÊN BẢN CUỘC HỌP GIAO BAN")
    run_title.font.name = 'Times New Roman'
    run_title.font.size = Pt(16)
    run_title.bold = True

    # -------- NỘI DUNG BIÊN BẢN --------
    document.add_paragraph("")  # Dòng trống

    # Thời gian bắt đầu (dùng gio_hop hoặc custom)
    # Ví dụ: "Thời gian bắt đầu: 10:00 - 11:30"
    if meeting_minutes.gio_hop:
        p_time = document.add_paragraph()
        p_time.add_run("Thời gian bắt đầu: ").bold = True
        p_time.add_run(meeting_minutes.gio_hop)

    # Địa điểm
    if meeting_minutes.dia_diem:
        p_place = document.add_paragraph()
        p_place.add_run("Địa điểm: ").bold = True
        p_place.add_run(meeting_minutes.dia_diem)

    document.add_paragraph("")

    # Thành phần
    # Gộp: Chủ trì, Thư ký, Thành viên tham dự
    document.add_paragraph("Thành phần cuộc họp:", style='List Paragraph').runs[0].bold = True
    if meeting_minutes.chu_tri:
        document.add_paragraph(f"- Chủ trì: {meeting_minutes.chu_tri}", style='List Bullet')
    if meeting_minutes.nguoi_ghi_chep:
        document.add_paragraph(f"- Thư ký: {meeting_minutes.nguoi_ghi_chep}", style='List Bullet')
    if meeting_minutes.thanh_vien_tham_du:
        document.add_paragraph(f"- Các thành viên tham dự: " + ", ".join(meeting_minutes.thanh_vien_tham_du), style='List Bullet')

    document.add_paragraph("")

    # Mục tiêu cuộc họp
    if meeting_minutes.muc_tieu_cuoc_hop:
        doc_para = document.add_paragraph()
        doc_para.add_run("Nội dung, mục tiêu cuộc họp: ").bold = True
        doc_para.add_run(meeting_minutes.muc_tieu_cuoc_hop)

    document.add_paragraph("")

    # Chương trình nghị sự
    if meeting_minutes.chuong_trinh_nghi_su:
        doc_para = document.add_paragraph()
        doc_para.add_run("Chương trình nghị sự:").bold = True
        for item in meeting_minutes.chuong_trinh_nghi_su:
            document.add_paragraph(item, style='List Bullet')
    document.add_paragraph("")

    # Nội dung thảo luận
    if meeting_minutes.noi_dung_thao_luan:
        doc_para = document.add_paragraph()
        doc_para.add_run("Nội dung thảo luận:").bold = True
        for topic, points in meeting_minutes.noi_dung_thao_luan.items():
            sub_heading = document.add_paragraph(topic)
            sub_heading.style = 'List Bullet'
            for point in points:
                document.add_paragraph(point, style='List Bullet 2')

    document.add_paragraph("")

    # Các quyết định
    if meeting_minutes.cac_quyet_dinh:
        doc_para = document.add_paragraph()
        doc_para.add_run("Các quyết định:").bold = True
        for decision in meeting_minutes.cac_quyet_dinh:
            document.add_paragraph(decision, style='List Bullet')

    document.add_paragraph("")

    # Kết luận
    if meeting_minutes.ket_luan:
        doc_para = document.add_paragraph()
        doc_para.add_run("Kết luận: ").bold = True
        doc_para.add_run(meeting_minutes.ket_luan)

    document.add_paragraph("")

    # Tài liệu đính kèm
    if meeting_minutes.tai_lieu_dinh_kem:
        doc_para = document.add_paragraph()
        doc_para.add_run("Tài liệu đính kèm:").bold = True
        for item in meeting_minutes.tai_lieu_dinh_kem:
            document.add_paragraph(item, style='List Bullet')
    else:
        document.add_paragraph("Tài liệu đính kèm: Không có")

    document.add_paragraph("")

    # Ghi chú
    if meeting_minutes.ghi_chu:
        doc_para = document.add_paragraph()
        doc_para.add_run("Ghi chú: ").bold = True
        doc_para.add_run(meeting_minutes.ghi_chu)
    else:
        document.add_paragraph("Ghi chú: Không có")

    document.add_paragraph("")

    # -------- PHẦN CHỮ KÝ --------
    # Tạo bảng 2 cột cho chữ ký (Chủ trì - Thư ký)
    signature_table = document.add_table(rows=1, cols=2)
    signature_table.alignment = WD_ALIGN_PARAGRAPH.CENTER
    signature_table.columns[0].width = Cm(8)
    signature_table.columns[1].width = Cm(8)

    cell_left = signature_table.cell(0, 0).paragraphs[0]
    cell_left.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_left = cell_left.add_run("CHỦ TRÌ\n\n\n\n\n(Ký, ghi rõ họ tên)")
    run_left.font.name = 'Times New Roman'
    run_left.font.size = Pt(13)

    cell_right = signature_table.cell(0, 1).paragraphs[0]
    cell_right.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_right = cell_right.add_run("THƯ KÝ\n\n\n\n\n(Ký, ghi rõ họ tên)")
    run_right.font.name = 'Times New Roman'
    run_right.font.size = Pt(13)

    # Lưu file DOCX
    document.save(output_file)


def refine_text(text: str, chunk_size: int = 1200) -> str:
    """
    Sử dụng LLM để chỉnh sửa lại văn bản, làm cho nội dung chuyên nghiệp hơn,
    loại bỏ trùng lặp và cải thiện văn phong. Văn bản được chia thành các khối,
    mỗi khối tối đa chunk_size từ. Các khối sẽ được xử lý song song bằng multithreading.

    Args:
        text (str): Đoạn văn bản cần chỉnh sửa.
        chunk_size (int): Số từ tối đa cho mỗi khối (mặc định 1200).

    Returns:
        str: Văn bản đã được chỉnh sửa.
    """
    if not text.strip():
        return text

    # Tách văn bản thành danh sách từ và chia thành các khối
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)

    total_chunks = len(chunks)
    prompt_template = """
Hãy chuyển đổi đoạn văn sau thành một văn bản chuyên nghiệp, mạch lạc và trang trọng.
Loại bỏ những nội dung trùng lặp và cải thiện văn phong.

Đoạn văn:
{text}

Văn bản đã chỉnh sửa:
"""
    prompt = PromptTemplate(template=prompt_template, input_variables=["text"])

    def process_chunk(idx, chunk):
        print(f"Processing chunk {idx}/{total_chunks}...")
        # Tạo instance LLM mới cho mỗi thread nếu cần đảm bảo thread-safety,
        # hoặc có thể chia sẻ chung nếu thư viện hỗ trợ.
        llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
        formatted_prompt = prompt.format_prompt(text=chunk)
        response = llm.invoke(formatted_prompt.to_messages())
        return response.content.strip()

    # Sử dụng ThreadPoolExecutor để xử lý các khối song song và đảm bảo thứ tự
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Sử dụng map với tuple (idx, chunk) để duy trì thứ tự
        results = list(executor.map(process_chunk, range(1, total_chunks + 1), chunks))

    refined_text = "\n".join(results)
    return refined_text



def refine_meeting_minutes(meeting_minutes: MeetingMinutes) -> MeetingMinutes:
    """
    Sử dụng LLM để xử lý lại các thành phần của MeetingMinutes nhằm cải thiện văn phong,
    loại bỏ trùng lặp và làm cho biên bản cuộc họp trở nên chuyên nghiệp hơn trước khi xuất ra DOCX.

    Args:
        meeting_minutes (MeetingMinutes): Object chứa thông tin biên bản cuộc họp gốc.

    Returns:
        MeetingMinutes: Object biên bản cuộc họp đã được cải thiện.
    """
    print("Bắt đầu refine MeetingMinutes...")
    refined = {}

    # Các trường giữ nguyên
    print("Giữ nguyên: ngay_hop, gio_hop, dia_diem, chu_tri, nguoi_ghi_chep, thanh_vien_tham_du")
    refined["ngay_hop"] = meeting_minutes.ngay_hop
    refined["gio_hop"] = meeting_minutes.gio_hop
    refined["dia_diem"] = meeting_minutes.dia_diem
    refined["chu_tri"] = meeting_minutes.chu_tri
    refined["nguoi_ghi_chep"] = meeting_minutes.nguoi_ghi_chep
    refined["thanh_vien_tham_du"] = meeting_minutes.thanh_vien_tham_du

    # Xử lý muc_tieu_cuoc_hop
    if meeting_minutes.muc_tieu_cuoc_hop:
        print("Processing muc_tieu_cuoc_hop...")
        refined["muc_tieu_cuoc_hop"] = refine_text(meeting_minutes.muc_tieu_cuoc_hop)
    else:
        refined["muc_tieu_cuoc_hop"] = None

    # Xử lý chuong_trinh_nghi_su theo batch
    if meeting_minutes.chuong_trinh_nghi_su:
        print("Processing chuong_trinh_nghi_su...")
        combined = "\n".join(meeting_minutes.chuong_trinh_nghi_su)
        refined_combined = refine_text(combined)
        refined["chuong_trinh_nghi_su"] = [line.strip() for line in refined_combined.split("\n") if line.strip()]
    else:
        refined["chuong_trinh_nghi_su"] = None

    # Xử lý noi_dung_thao_luan theo từng chủ đề
    if meeting_minutes.noi_dung_thao_luan:
        print("Processing noi_dung_thao_luan...")
        refined_noi_dung = {}
        for topic, points in meeting_minutes.noi_dung_thao_luan.items():
            print(f" - Processing topic: {topic}...")
            combined_points = "\n".join(points)
            refined_combined = refine_text(combined_points)
            refined_noi_dung[topic] = [line.strip() for line in refined_combined.split("\n") if line.strip()]
        refined["noi_dung_thao_luan"] = refined_noi_dung
    else:
        refined["noi_dung_thao_luan"] = None

    # Xử lý cac_quyet_dinh theo batch
    if meeting_minutes.cac_quyet_dinh:
        print("Processing cac_quyet_dinh...")
        combined = "\n".join(meeting_minutes.cac_quyet_dinh)
        refined_combined = refine_text(combined)
        refined["cac_quyet_dinh"] = [line.strip() for line in refined_combined.split("\n") if line.strip()]
    else:
        refined["cac_quyet_dinh"] = None

    # Xử lý ket_luan
    if meeting_minutes.ket_luan:
        print("Processing ket_luan...")
        refined["ket_luan"] = refine_text(meeting_minutes.ket_luan)
    else:
        refined["ket_luan"] = None

    # Tài liệu đính kèm giữ nguyên
    refined["tai_lieu_dinh_kem"] = meeting_minutes.tai_lieu_dinh_kem

    # Xử lý ghi_chu
    if meeting_minutes.ghi_chu:
        print("Processing ghi_chu...")
        refined["ghi_chu"] = refine_text(meeting_minutes.ghi_chu)
    else:
        refined["ghi_chu"] = None

    print("Refine MeetingMinutes hoàn tất.")
    return MeetingMinutes(**refined)



# --- Phần test chạy độc lập ---
# if __name__ == "__main__":
#     # Giả sử bạn có một đối tượng MeetingMinutes mẫu
#     sample_minutes = MeetingMinutes(
#         ngay_hop="30/03/2025",
#         gio_hop="10:00 - 11:30",
#         dia_diem="Phòng họp A",
#         chu_tri="Nguyễn Văn A",
#         nguoi_ghi_chep="Trần Thị B",
#         thanh_vien_tham_du=["Nguyễn Văn A", "Trần Thị B", "Lê Văn C", "Phạm Thị D"],
#         muc_tieu_cuoc_hop="Đánh giá tiến độ và lên kế hoạch giai đoạn tiếp theo",
#         chuong_trinh_nghi_su=["Báo cáo tiến độ", "Phân tích khó khăn", "Giải pháp và phân công nhiệm vụ"],
#         noi_dung_thao_luan={
#             "Báo cáo tiến độ": ["Đã hoàn thành 70% công việc"],
#             "Khó khăn": ["Thiếu nhân sự cho giai đoạn thử nghiệm"],
#             "Giải pháp": ["Đề xuất tăng thêm 2 tester", "Lê Văn C phụ trách", "Hạn chót: 15/04/2025"]
#         },
#         cac_quyet_dinh=["Phê duyệt bổ sung nhân sự", "Tái phân công nhiệm vụ"],
#         ket_luan="Thống nhất hạn hoàn thành và họp tiếp theo vào 20/04/2025",
#         tai_lieu_dinh_kem=None,
#         ghi_chu="Cần chú ý việc phân bổ nhiệm vụ và theo dõi tiến độ một cách chặt chẽ."
#     )
#
#     print("----- Meeting Minutes gốc -----")
#     print(sample_minutes.model_dump())
#
#     refined_minutes = refine_meeting_minutes(sample_minutes)
#     print("----- Meeting Minutes đã chỉnh sửa -----")
#     print(refined_minutes.model_dump())
#
#     # Xuất file DOCX từ meeting minutes đã được chỉnh sửa
#     output_docx = "meeting_minutes_refined.docx"
#     export_meeting_minutes_to_docx(refined_minutes, output_docx)
#     print(f"Meeting minutes đã được xuất ra file: {output_docx}")
