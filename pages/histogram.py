import streamlit as st
import pandas as pd
import plotly.express as px

from src.utils.filter import apply_filters, render_filters
from src.utils.data_loader import DataLoader
from src.utils.data_preprocessing import DataPreprocessor


TITLE = "Hiển thị dữ liệu trade và biểu đồ histogram (Histogram)"


# Tạo dữ liệu mẫu
df: pd.DataFrame = DataLoader.load_csv("btc_trade_data.csv")
df = DataPreprocessor.convert_to_datetime(df, 'time', unit='us')

# =============== Filters ================

scope = "trade"

filters = [
    {
        "key": "price",
        "label": "Price",
        "type": "range",
        "column": "price",
        "min": float(df["price"].min()),
        "max": float(df["price"].max()),
        "default": (df["price"].min(), df["price"].max()),
    },
    {
        "key": "qty",
        "label": "Quantity",
        "type": "range",
        "column": "qty",
        "min": float(df["qty"].min()),
        "max": float(df["qty"].max()),
        "default": (df["qty"].min(), df["qty"].max()),
    },
    {
        "key": "quote_qty",
        "label": "Quote Quantity",
        "type": "range",
        "column": "quote_qty",
        "min": float(df["quote_qty"].min()),
        "max": float(df["quote_qty"].max()),
        "default": (df["quote_qty"].min(), df["quote_qty"].max()),
    },
    {
        "key": "time",
        "label": "Timestamp",
        "type": "timerange",
        "column": "time",
    },
    {
        "key": "is_buyer_maker",
        "label": "Is Buyer Maker",
        "type": "selectbox",
        "column": "is_buyer_maker",
        "options": ["All"] + df["is_buyer_maker"].dropna().unique().tolist(),
        "index": 0,
        "all_value": "All",
    }
]

with st.sidebar:
    st.header("Filters")
    vals = render_filters(filters, scope=scope)

    if st.button("Reset this page filters"):
        # xoá key theo scope
        for f in filters:
            st.session_state.pop(f"{scope}:{f['key']}", None)
        st.rerun()

filtered_df = apply_filters(df, filters, vals)

# ================ Main Page ===================

st.title(TITLE)

# Dữ liệu giao dịch
st.subheader('Bảng dữ liệu Giao dịch')
st.write(f"Tổng số bản ghi trong trade_data: {len(filtered_df)}")
st.dataframe(filtered_df)

# Biểu đồ histogram
st.subheader("Biểu đồ histogram (Histogram) từ trade_data")
fig = px.histogram(
    df,
    x="price",
    nbins=50,
    title="Phân phối giá (Histogram)",
    labels={"price": "Price", "count": "Count"}
)
st.plotly_chart(fig, use_container_width=True)
