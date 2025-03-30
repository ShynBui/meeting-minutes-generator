# meeting-minutes-generator

Dự án này tạo ra một ứng dụng để tạo biên bản cuộc họp (meeting minutes) từ transcript.

## Cấu trúc thư mục
### Mô tả

* **`app/`**: Chứa mã nguồn cho API FastAPI.
    * `main.py`: Điểm đầu vào của API FastAPI.
    * `modules/`: Chứa các module xử lý logic chính.
        * `preprocessing.py`: Module tiền xử lý transcript.
        * `summarizer.py`: Module gọi API OpenAI/Gemini để tạo meeting minutes.
        * `exporter.py`: Module xuất meeting minutes ra file Word.
* **`ui/`**: Chứa mã nguồn cho giao diện người dùng Gradio.
    * `interface.py`: Mã nguồn cho giao diện web đơn giản.
* **`requirements.txt`**: Danh sách các thư viện Python cần thiết.
* **`run.py`**: Script để chạy cả API FastAPI và giao diện Gradio.

## Hướng dẫn chạy

1.  Cài đặt các thư viện cần thiết:

    ```bash
    pip install -r requirements.txt
    ```

2.  Chạy ứng dụng:

    ```bash
    python run.py
    ```

3.  Truy cập giao diện web tại `http://localhost:8000`.

## Yêu cầu

* Python 3.6+
* Các thư viện được liệt kê trong `requirements.txt`

## Lưu ý

* Cần có API key của OpenAI hoặc Gemini để sử dụng module `summarizer.py`.
* Ứng dụng này chỉ hỗ trợ xuất meeting minutes ra file Word.
* Giao diện Gradio chỉ là một giao diện web đơn giản để thử nghiệm.

## Phát triển thêm

* Thêm hỗ trợ cho các định dạng xuất file khác.
* Cải thiện giao diện người dùng.
* Thêm các tính năng tiền xử lý transcript nâng cao.
* Tối ưu hóa hiệu suất của ứng dụng.
