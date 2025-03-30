# meeting-minutes-generator

Dự án này tạo ra một ứng dụng để tạo biên bản cuộc họp (meeting minutes) từ transcript.

## Cấu trúc thư mục
### Mô tả

* **`app/`**: Chứa mã nguồn cho API FastAPI.
    * `main.py`: Điểm đầu vào của API FastAPI.
    * `config.py`:Cấu hình toàn cục (API keys, thông số model,...)
    * `modules/`: Chứa các module xử lý logic chính.
        * `preprocessing.py`: Module tiền xử lý transcript.
        * `summarizer.py`: Module gọi API OpenAI/Gemini để tạo meeting minutes.
        * `exporter.py`: Module xuất meeting minutes ra file Word.
        * `schema.py`: Định dạng kiểu meeting minutes.
* **`ui/`**: Chứa mã nguồn cho giao diện người dùng Gradio.
    * `interface.py`: Mã nguồn cho giao diện web đơn giản.
* **`requirements.txt`**: Danh sách các thư viện Python cần thiết.
* **`run.py`**: Script để chạy cả API FastAPI và giao diện Gradio.

## Hướng dẫn chạy

1.  Cài đặt các thư viện cần thiết:

    ```bash
    pip install -r requirements.txt
    ```

2. Thiết lập API Key

    Tạo file .env ở thư mục gốc với nội dung như sau:
    ```text
    OPENAI_API_KEY=your_openai_api_key_here
    # hoặc nếu dùng Gemini:
    GEMINI_API_KEY=your_gemini_api_key_here
    ```

3. Chạy ứng dụng:
    ```bash
    python ui/interface.py
    ```

4. Truy cập giao diện web tại `http://localhost:7860`.

## Yêu cầu

* Python 3.9+
* Các thư viện được liệt kê trong `requirements.txt`

## Lưu ý

* Cần có API key của OpenAI hoặc Gemini để sử dụng module `summarizer.py` hoặc `exporter.py`.
* Ứng dụng này chỉ hỗ trợ xuất meeting minutes ra file Word.
* Giao diện Gradio chỉ là một giao diện web đơn giản để thử nghiệm.

## Phát triển thêm

* Thêm hỗ trợ cho các định dạng xuất file khác.
* Cải thiện giao diện người dùng.
* Thêm các tính năng tiền xử lý transcript nâng cao.
* Tối ưu hóa hiệu suất của ứng dụng.
