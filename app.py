import streamlit as st
from src.components.navigation import Navigation


st.set_page_config(page_title="Trang Chủ", layout="wide")

pages = [
    {"file": "pages/home.py", "title": "About"},
    {"file": "pages/candlestick.py", "title": "Candlestick Chart"},
    {"file": "pages/line_chart.py", "title": "Line Chart"},
    {"file": "pages/bar_chart.py", "title": "Bar Chart"},
    {"file": "pages/scatter_plot.py", "title": "Scatter Plot"},
    {"file": "pages/histogram.py", "title": "Histogram"},
    {"file": "pages/box_plot.py", "title": "Box Plot"},
    {"file": "pages/pie_chart.py", "title": "Pie Chart"},
]

nav = Navigation(pages)
nav.render()
