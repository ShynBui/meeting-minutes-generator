from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class MeetingMinutes(BaseModel):
    ngay_hop: Optional[str] = Field(
        None,
        description="Ngày diễn ra cuộc họp. Định dạng: dd/mm/yyyy (ví dụ: 30/03/2025)"
    )
    gio_hop: Optional[str] = Field(
        None,
        description="Thời gian bắt đầu và kết thúc cuộc họp. Ví dụ: '10:00 - 11:30'"
    )
    dia_diem: Optional[str] = Field(
        None,
        description="Địa điểm tổ chức cuộc họp. Có thể là phòng họp, văn phòng, hoặc họp online (ví dụ: 'Phòng họp A')"
    )
    chu_tri: Optional[str] = Field(
        None,
        description="Tên người chủ trì cuộc họp (ví dụ: 'Nguyễn Văn A')"
    )
    nguoi_ghi_chep: Optional[str] = Field(
        None,
        description="Tên người ghi chép biên bản cuộc họp"
    )
    thanh_vien_tham_du: Optional[List[str]] = Field(
        None,
        description="Danh sách các thành viên tham dự cuộc họp"
    )
    muc_tieu_cuoc_hop: Optional[str] = Field(
        None,
        description="Tóm tắt mục tiêu chính của cuộc họp"
    )
    chuong_trinh_nghi_su: Optional[List[str]] = Field(
        None,
        description="Danh sách các nội dung chính hoặc chủ đề được đưa ra thảo luận trong cuộc họp"
    )
    noi_dung_thao_luan: Optional[Dict[str, List[str]]] = Field(
        None,
        description="Nội dung chi tiết được thảo luận trong từng chủ đề. Dạng: {chủ đề: [các ý chính]}"
    )
    cac_quyet_dinh: Optional[List[str]] = Field(
        None,
        description="Danh sách các quyết định chính thức được đưa ra trong cuộc họp"
    )
    ket_luan: Optional[str] = Field(
        None,
        description="Tóm tắt kết luận của cuộc họp và hướng đi tiếp theo"
    )
    tai_lieu_dinh_kem: Optional[List[str]] = Field(
        None,
        description="Danh sách các tài liệu liên quan được đính kèm hoặc đề cập trong cuộc họp"
    )
    ghi_chu: Optional[str] = Field(
        None,
        description="Ghi chú bổ sung khác nếu có"
    )
