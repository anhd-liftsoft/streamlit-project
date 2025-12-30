import pandas as pd
from bokeh.plotting import figure
from bokeh.models.tools import RangeTool
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, DatetimeTickFormatter, HoverTool, Range1d, Span

from .calculation import Calculation


class AdvancedChartUtils:
    """
    Class for building advanced charts
    """
    @staticmethod
    def build_bokeh_ohlcv(df: pd.DataFrame) -> column:
        """
        Build Bokeh OHLCV chart with candlesticks, volume, and RSI subplots.
        Args:
            df: DataFrame containing OHLCV data with at least the following columns:
                'open_time', 'open', 'high', 'low', 'close', 'volume'.
                Additional columns for indicators (e.g. MA, EMA, RSI) can be included.
        Returns:
            A Bokeh layout object containing the OHLCV chart with subplots.
        """

        df = df.copy()

        df = Calculation.add_ma(df, price_col='close', spans=(7, 25))
        df = Calculation.add_ema(df, price_col='close', spans=(7, 25, 99, 200))
        df = Calculation.add_rsi(df, price_col='close', periods=(6, 12, 24))

        w = 250

        df["inc"] = df["close"] >= df["open"]
        df["dec"] = ~df["inc"]

        # ===== Colors =====
        C = {
            "wick": "#6B7280",
            "inc": "#22C55E",         # green
            "dec": "#EF4444",         # red
            "volume_inc": "#60A5FA",  # blue-ish
            "volume_dec": "#FCA5A5",  # light red
            "ma_7": "#F59E0B",        # amber
            "ma_25": "#D97706",       # orange
            "ema_7": "#3B82F6",       # blue
            "ema_25": "#1D4ED8",      # indigo
            "ema_99": "#A855F7",      # purple
            "ema_200": "#111827",     # near black
            "rsi_6": "#10B981",       # emerald
            "rsi_12": "#06B6D4",      # cyan
            "rsi_24": "#8B5CF6",      # violet
            "rsi_30_70": "#9CA3AF",   # gray
            "range_fill": "#93C5FD",
        }

        source_all = ColumnDataSource(df)
        source_inc = ColumnDataSource(df[df["inc"]])
        source_dec = ColumnDataSource(df[df["dec"]])

        x0, x1 = df["open_time"].iloc[0], df["open_time"].iloc[-1]
        x_range = Range1d(x0, x1)

        # ===== Panel 1: Candlestick + MA/EMA =====
        p1 = figure(
            x_axis_type="datetime",
            height=520,
            tools="pan,wheel_zoom,box_zoom,reset,save",
            active_scroll="wheel_zoom",
            x_range=x_range,
            title="OHLCV (Bokeh)",
            sizing_mode="stretch_width"
        )

        p1_y_min = float(df["low"].min())
        p1_y_max = float(df["high"].max())
        pad = (p1_y_max - p1_y_min) * 0.05

        p1.y_range = Range1d(
            start=p1_y_min - pad,
            end=p1_y_max + pad,
            bounds=(p1_y_min - pad, p1_y_max + pad)
        )

        # wicks
        wick_r = p1.segment(
            x0="open_time", y0="high",
            x1="open_time", y1="low",
            source=source_all,
            line_color=C["wick"],
            line_alpha=0.9,
            legend_label="High-Low"
        )

        # candle bodies
        candle_up_r = p1.vbar(
            x="open_time", width=w,
            top="close", bottom="open",
            source=source_inc,
            fill_color=C["inc"], line_color=C["inc"],
            fill_alpha=0.9,
            legend_label="Candle Up"
        )
        candle_down_r = p1.vbar(
            x="open_time", width=w,
            top="open", bottom="close",
            source=source_dec,
            fill_color=C["dec"], line_color=C["dec"],
            fill_alpha=0.9,
            legend_label="Candle Down"
        )

        p1.add_tools(HoverTool(
            renderers=[wick_r, candle_up_r, candle_down_r],
            tooltips=[
                ("time", "@open_time{%F %T}"),
                ("open", "@open{0.0000}"),
                ("high", "@high{0.0000}"),
                ("low", "@low{0.0000}"),
                ("close", "@close{0.0000}"),
                ("vol", "@volume{0,0}"),
            ],
            formatters={"@open_time": "datetime"},
            mode="mouse"
        ))

        # MA/EMA lines
        line_specs = [
            ("ma_7", "MA 7", C["ma_7"]),
            ("ma_25", "MA 25", C["ma_25"]),
            ("ema_7", "EMA 7", C["ema_7"]),
            ("ema_25", "EMA 25", C["ema_25"]),
            ("ema_99", "EMA 99", C["ema_99"]),
            ("ema_200", "EMA 200", C["ema_200"]),
        ]
        for col, name, color in line_specs:
            if col in df.columns:
                r = p1.line(
                    "open_time", col, source=source_all,
                    line_width=2,
                    line_color=color,
                    legend_label=name
                )

                # Hover riêng cho từng đường (chỉ hiện khi trỏ vào đúng đường đó)
                p1.add_tools(HoverTool(
                    renderers=[r],
                    tooltips=[
                        ("Time", "@open_time{%F %T}"),
                        (name, f"@{{{col}}}{{0.0000}}"),
                    ],
                    formatters={"@open_time": "datetime"},
                    mode="mouse"
                ))

        p1.legend.click_policy = "hide"
        p1.yaxis.axis_label = "Price"
        p1.xaxis.formatter = DatetimeTickFormatter(
            minutes="%H:%M",
            hours="%H:%M",
            days="%Y-%m-%d",
            months="%Y-%m",
            years="%Y"
        )

        # ===== Panel 2: Volume (tô màu theo nến tăng/giảm) =====
        p2 = figure(
            x_axis_type="datetime",
            height=220,
            tools="pan,wheel_zoom,box_zoom,reset,save",
            active_scroll="wheel_zoom",
            x_range=p1.x_range,
            sizing_mode="stretch_width"
        )

        p2_y_min = 0.0
        p2_y_max = float(df["volume"].max())
        pad = p2_y_max * 0.1
        p2.y_range = Range1d(
            start=p2_y_min,
            end=p2_y_max + pad,
            bounds=(p2_y_min, p2_y_max + pad)
        )

        p2.vbar(
            x="open_time", top="volume", width=w,
            source=source_inc,
            fill_color=C["volume_inc"], line_color=C["volume_inc"],
            fill_alpha=0.6,
            legend_label="Volume Up"
        )
        p2.vbar(
            x="open_time", top="volume", width=w,
            source=source_dec,
            fill_color=C["volume_dec"], line_color=C["volume_dec"],
            fill_alpha=0.6,
            legend_label="Volume Down"
        )

        p2.yaxis.axis_label = "Volume"
        p2.xaxis.visible = False
        p2.legend.click_policy = "hide"

        p2.add_tools(HoverTool(
            tooltips=[
                ("time", "@open_time{%F %T}"),
                ("volume", "@volume{0,0}"),
            ],
            formatters={"@open_time": "datetime"},
            mode="mouse"
        ))

        # ===== Panel 3: RSI =====
        p3 = figure(
            x_axis_type="datetime",
            height=220,
            tools="pan,wheel_zoom,box_zoom,reset,save",
            active_scroll="wheel_zoom",
            x_range=p1.x_range,
            sizing_mode="stretch_width"
        )

        p3_y_min = 0.0
        p3_y_max = 100.0
        pad = (p3_y_max - p3_y_min) * 0.05
        p3.y_range = Range1d(
            start=p3_y_min - pad,
            end=p3_y_max + pad,
            bounds=(p3_y_min - pad, p3_y_max + pad)
        )

        rsi_specs = [
            ("rsi_6", "RSI 6", C["rsi_6"]),
            ("rsi_12", "RSI 12", C["rsi_12"]),
            ("rsi_24", "RSI 24", C["rsi_24"]),
        ]
        for col, name, color in rsi_specs:
            if col in df.columns:
                r = p3.line(
                    "open_time", col, source=source_all,
                    line_width=2,
                    line_color=color,
                    legend_label=name
                )

                p3.add_tools(HoverTool(
                    renderers=[r],
                    tooltips=[
                        ("time", "@open_time{%F %T}"),
                        (name, f"@{{{col}}}{{0.00}}"),
                    ],
                    formatters={"@open_time": "datetime"},
                    mode="mouse"
                ))

        # RSI thresholds
        p3.add_layout(Span(location=30, dimension="width", line_color=C["rsi_30_70"], line_dash="dashed", line_width=1))
        p3.add_layout(Span(location=70, dimension="width", line_color=C["rsi_30_70"], line_dash="dashed", line_width=1))

        p3.yaxis.axis_label = "RSI"
        p3.legend.click_policy = "hide"

        # ===== RangeTool (mini overview + kéo để zoom) =====
        select = figure(
            height=120,
            x_axis_type="datetime",
            y_range=p2.y_range,
            x_range=Range1d(x0, x1),
            tools="",
            toolbar_location=None,
            sizing_mode="stretch_width"
        )
        select.vbar(x="open_time", top="volume", width=w, source=source_all, fill_alpha=0.25)

        range_tool = RangeTool(x_range=p1.x_range)
        range_tool.overlay.fill_color = C["range_fill"]
        range_tool.overlay.fill_alpha = 0.25
        select.add_tools(range_tool)

        return column(p1, p2, p3, select, sizing_mode="stretch_width")
