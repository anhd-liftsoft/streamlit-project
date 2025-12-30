import streamlit as st
from streamlit_bokeh import streamlit_bokeh
from bokeh.models import Range1d

from src.utils.filter import apply_filters, render_filters
from src.utils.data_loader import DataLoader
from src.utils.data_preprocessing import DataPreprocessor
from src.utils.chart import AdvancedChartUtils


TITLE = "Hiển thị dữ liệu klines và biểu đồ nến (Candlestick)"


# Tạo dữ liệu mẫu
df = DataLoader.load_csv("eth_data.csv")
df = DataPreprocessor.convert_to_datetime(df, 'open_time')
df = DataPreprocessor.convert_to_datetime(df, 'close_time')

# =============== Filters ================

scope = "klines"

filters = [
    {
        "key": "open_date",
        "label": "Open Time",
        "type": "daterange",
        "column": "open_time",
        "default": (df['open_time'].min(), df['open_time'].max()),
    },
]

with st.sidebar:
    st.header("Filters")
    vals = render_filters(filters, scope=scope)

    if st.button("Reset this page filters"):
        # xoá key theo scope
        for f in filters:
            st.session_state.pop(f"{scope}:{f['key']}", None)
        st.rerun()

df = apply_filters(df, filters, vals)

# ================ Main Page ===================

st.title(TITLE)

# Dữ liệu OHLCV
st.subheader('Bảng dữ liệu OHLCV')
st.write(f"Tổng số bản ghi trong ohlcv_data: {len(df)}")
st.dataframe(df)

# Vẽ biểu đồ
st.subheader("Biểu đồ nến (Candlestick Chart) từ ohlcv_data")
fig_bokeh = AdvancedChartUtils.build_bokeh_ohlcv(df)
x_min = df['open_time'].min()
x_max = df['open_time'].max()

streamlit_bokeh(fig_bokeh)
