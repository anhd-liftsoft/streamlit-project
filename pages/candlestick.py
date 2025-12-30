import streamlit as st
from plotly.subplots import make_subplots
import plotly.graph_objects as go

from src.utils.filter import apply_filters, render_filters
from src.utils.data_loader import DataLoader
from src.utils.data_preprocessing import DataPreprocessor
from src.utils.calculation import Calculation


TITLE = "Hiển thị dữ liệu klines và biểu đồ nến (Candlestick)"


# Tạo dữ liệu mẫu
df = DataLoader.load_csv("eth_data.csv")
df = DataPreprocessor.convert_to_datetime(df, 'open_time', unit='us')
df = DataPreprocessor.convert_to_datetime(df, 'close_time', unit='us')

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

# Biểu đồ nến với EMA và Volume
df = Calculation.add_ma(df, price_col='close', spans=(7, 25))
df = Calculation.add_ema(df, price_col='close', spans=(7, 25, 99, 200))
df = Calculation.add_rsi(df, price_col='close', periods=(6, 12, 24))

candle_stick = go.Candlestick(
    x=df['open_time'],
    open=df['open'],
    high=df['high'],
    low=df['low'],
    close=df['close'],
    name='Price Movement Over Time'
)

ma_7_line = go.Scatter(x=df['open_time'], y=df['ma_7'], mode='lines', name='MA 7')
ma_25_line = go.Scatter(x=df['open_time'], y=df['ma_25'], mode='lines', name='MA 25')
ema_7_line = go.Scatter(x=df['open_time'], y=df['ema_7'], mode='lines', name='EMA 7')
ema_25_line = go.Scatter(x=df['open_time'], y=df['ema_25'], mode='lines', name='EMA 25')
ema_99_line = go.Scatter(x=df['open_time'], y=df['ema_99'], mode='lines', name='EMA 99')
ema_200_line = go.Scatter(x=df['open_time'], y=df['ema_200'], mode='lines', name='EMA 200')

volume_bar = go.Bar(
    x=df['open_time'],
    y=df['volume'],
    name='Trading Volume Over Time'
)

rsi_6_line_plot = go.Scatter(x=df['open_time'], y=df['rsi_6'], mode='lines', name='RSI 6')
rsi_12_line_plot = go.Scatter(x=df['open_time'], y=df['rsi_12'], mode='lines', name='RSI 12')
rsi_24_line_plot = go.Scatter(x=df['open_time'], y=df['rsi_24'], mode='lines', name='RSI 24')

fig = make_subplots(
    rows=3, cols=1,
    shared_xaxes=True,
    row_heights=[700, 300, 300],
    vertical_spacing=0.07,
)

fig.add_trace(candle_stick, row=1, col=1)
fig.add_trace(ma_7_line, row=1, col=1)
fig.add_trace(ma_25_line, row=1, col=1)
fig.add_trace(ema_7_line, row=1, col=1)
fig.add_trace(ema_25_line, row=1, col=1)
fig.add_trace(ema_99_line, row=1, col=1)
fig.add_trace(ema_200_line, row=1, col=1)

fig.add_trace(volume_bar, row=2, col=1)

fig.add_trace(rsi_6_line_plot, row=3, col=1)
fig.add_trace(rsi_12_line_plot, row=3, col=1)
fig.add_trace(rsi_24_line_plot, row=3, col=1)

fig.update_yaxes(title_text="Price", row=1, col=1, fixedrange=False)
fig.update_yaxes(title_text="Volume", row=2, col=1)
fig.update_yaxes(title_text="RSI", row=3, col=1)

fig.update_xaxes(title_text="Time", row=2, col=1)

fig.update_layout(xaxis3=dict(rangeslider=dict(visible=True, thickness=0.03)))
fig.for_each_trace(lambda t: t.update(xaxis="x3"))
fig.update_layout(title='OHLCV with EMA and Volume', height=1000, xaxis_rangeslider_visible=False)

st.plotly_chart(fig, use_container_width=True)
