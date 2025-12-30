# Streamlit App — Mô tả dự án

Ứng dụng mẫu xây dựng bằng Streamlit để trực quan hóa dữ liệu tài chính (OHLCV, giao dịch, ...).

## Tổng quan

Repository này chứa một ứng dụng Streamlit đơn trang / đa trang, kèm helpers để vẽ biểu đồ bằng Plotly và các ví dụ xử lý dữ liệu.

## Yêu cầu

- Python 3.9+ (hoặc môi trường phù hợp)
- Xem `requirements.txt` để biết các phụ thuộc chính (Streamlit, Plotly, pandas...)

## Cài đặt & chạy (cục bộ)

1. Tạo và kích hoạt virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Cài đặt phụ thuộc:

```bash
pip install -r requirements.txt
```

3. Chạy ứng dụng:

```bash
streamlit run app.py
```

Ứng dụng sẽ mở tại `http://localhost:8501`.

## Chạy bằng Docker

```bash
docker compose up -d --build
```

## Cấu trúc chính của dự án

- `app.py` — Entrypoint của Streamlit.
- `pages/` — Các trang phụ cho chế độ multi-page.
- `utils/` — Hàm tiện ích, ví dụ: `utils/charts.py` chứa các hàm vẽ Plotly cho Streamlit.
- `data/` — CSV mẫu (ví dụ `ohlcv_data.csv`, `trade_data.csv`).
- `assets/` — Tài nguyên tĩnh.
- `tests/` — Unit tests (ví dụ `tests/test_utils.py`).

## Ví dụ sử dụng nhanh

Trong mã (ví dụ `app.py`), bạn có thể gọi:

```py
from src.utils.charts import Charts

# df là pandas.DataFrame có cột tương ứng
Charts.candlestick_chart(df, 'timestamp', 'open', 'high', 'low', 'close', 'Biểu đồ nến')
```
