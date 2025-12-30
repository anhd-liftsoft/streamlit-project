import streamlit as st
import pandas as pd
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, Range1d
from bokeh.models.tools import HoverTool
from bokeh.transform import dodge
from streamlit_bokeh import streamlit_bokeh

from src.utils.data_loader import DataLoader
from src.utils.data_preprocessing import DataPreprocessor
from src.utils.filter import apply_filters, render_filters


TITLE = "Hiển thị dữ liệu trade và biểu đồ cột (Bar Chart)"


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
        # xoá key theo scope
        for f in filters:
            st.session_state.pop(f"{scope}:{f['key']}", None)
        st.rerun()

filtered_df = apply_filters(df, filters, vals)

# ================ Main Page ===================

st.title(TITLE)

# Dữ liệu giao dịch
st.subheader('Bảng dữ liệu Giao dịch')
st.write(f"Tổng số bản ghi: {len(filtered_df)}")
st.dataframe(filtered_df)

# Biểu đồ cột
st.subheader("Biểu đồ cột từ trade_data")

df["side"] = df["is_buyer_maker"].map({True: "SELL", False: "BUY"})  # quy ước phổ biến

bucket = "1min"  # "5min", "15min", "1H"...

# Stacked Bar Chart
stacked_df = (df
              .set_index("time")
              .groupby("side")["qty"]
              .resample(bucket)
              .sum()
              .reset_index(name="volume")
              )

fig_stacked = figure(
    title="Khối lượng theo Side",
    x_axis_type="datetime",
    sizing_mode="stretch_width",
    height=100,
)

fig_stacked_max = float(stacked_df["volume"].max())
pad = fig_stacked_max * 0.1
fig_stacked.y_range = Range1d(
    start=0,
    end=fig_stacked_max + pad,
    bounds=(0, fig_stacked_max + pad)
)

fig_stacked.vbar_stack(
    stackers=["BUY", "SELL"],
    x='time',
    width=50000,  # một phút
    color=["green", "red"],
    source=stacked_df.pivot(index='time', columns='side', values='volume').reset_index(),
    legend_label=["BUY", "SELL"],
)

fig_stacked.xaxis.axis_label = 'Time'
fig_stacked.yaxis.axis_label = 'Quantity'
fig_stacked.legend.location = "top_left"
fig_stacked.legend.click_policy = "hide"
fig_stacked.add_tools(HoverTool(
    tooltips=[
        ("time", "@time{%F %T}"),
        ("BUY Volume", "@BUY{0,0}"),
        ("SELL Volume", "@SELL{0,0}"),
    ],
    formatters={"@time": "datetime"},
    mode="mouse"
))

streamlit_bokeh(fig_stacked, use_container_width=True)

# Grouped Bar Chart
grouped_df = (df
              .set_index("time")
              .groupby("side")["qty"]
              .resample(bucket)
              .size()
              .reset_index(name="count")
              )

# Pivot để có BUY và SELL thành các cột riêng
pivot_grouped = grouped_df.pivot(index='time', columns='side', values='count').reset_index()

source_grouped = ColumnDataSource(pivot_grouped)

fig_grouped = figure(
    title="Số lượng theo Side",
    x_axis_type="datetime",
    sizing_mode="stretch_width",
    height=100,
)

fig_grouped_max = float(grouped_df["count"].max())
pad = fig_grouped_max * 0.1
fig_grouped.y_range = Range1d(
    start=0,
    end=fig_grouped_max + pad,
    bounds=(0, fig_grouped_max + pad)
)

# Sử dụng dodge để tạo grouped bars
bar_width = 25000  # nửa phút
buy_bar = fig_grouped.vbar(x=dodge('time', - bar_width / 2, range=fig_grouped.x_range), top='BUY',
                           width=bar_width, source=source_grouped, color="green", legend_label="BUY")
sell_bar = fig_grouped.vbar(x=dodge('time', bar_width / 2, range=fig_grouped.x_range), top='SELL',
                            width=bar_width, source=source_grouped, color="red", legend_label="SELL")

fig_grouped.xaxis.axis_label = 'Time'
fig_grouped.yaxis.axis_label = 'Count'
fig_grouped.legend.location = "top_left"
fig_grouped.legend.click_policy = "hide"
fig_grouped.add_tools(HoverTool(
    renderers=[buy_bar],
    tooltips=[
        ("time", "@time{%F %T}"),
        ("BUY Count", "@BUY{0,0}"),
    ],
    formatters={"@time": "datetime"},
    mode="vline"
))
fig_grouped.add_tools(HoverTool(
    renderers=[sell_bar],
    tooltips=[
        ("time", "@time{%F %T}"),
        ("SELL Count", "@SELL{0,0}"),
    ],
    formatters={"@time": "datetime"},
    mode="mouse"
))

streamlit_bokeh(fig_grouped, use_container_width=True)
