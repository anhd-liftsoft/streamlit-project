import streamlit as st
import pandas as pd
from bokeh.plotting import figure
from bokeh.models import Range1d
from bokeh.models.tools import HoverTool
from streamlit_bokeh import streamlit_bokeh

from src.utils.filter import apply_filters, render_filters
from src.utils.data_loader import DataLoader
from src.utils.data_preprocessing import DataPreprocessor


TITLE = "Hiển thị dữ liệu trade và biểu đồ đường (Line Chart)"


# Tạo dữ liệu mẫu
df: pd.DataFrame = DataLoader.load_csv("btc_trade_data.csv")
df = DataPreprocessor.convert_to_datetime(df, 'time')

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
        # Xoá key theo scope
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

# Biểu đồ đường cho trade_data
st.subheader("Biểu đồ đường (Line Chart) từ trade_data")
fig = figure(
    title="Line Chart of Price over Time",
    x_axis_type="datetime",
    sizing_mode="stretch_width",
    height=100,
)

y_min = float(df["price"].min())
y_max = float(df["price"].max())
pad = (y_max - y_min) * 0.05

fig.y_range = Range1d(
    start=y_min - pad,
    end=y_max + pad,
    bounds=(y_min - pad, y_max + pad)
)

fig.line(
    x=df["time"],
    y=df["price"],
    line_width=2,
    color="blue",
    legend_label="Price",
)

fig.xaxis.axis_label = 'Time'
fig.yaxis.axis_label = 'Price'
fig.legend.location = "top_left"
fig.legend.click_policy = "hide"
fig.add_tools(HoverTool(
    tooltips=[
        ("time", "@x{%F %T}"),
        ("price", "@y{0,0.00}"),
    ],
    formatters={"@x": "datetime"},
    mode="vline"
))

streamlit_bokeh(fig, use_container_width=True)
