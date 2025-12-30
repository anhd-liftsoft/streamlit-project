import streamlit as st
import pandas as pd
import numpy as np


class Calculation:
    """
    Class for calculation indicators
    """

    @st.cache_data(ttl=60)
    @staticmethod
    def add_ma(
        df: pd.DataFrame,
        price_col: str = "close",
        spans: tuple[int, ...] = (12, 26, 50, 200)
    ) -> pd.DataFrame:
        """
        Calculate EMA for specified time spans and add corresponding columns to DataFrame.

        Args:
            df: DataFrame containing price data.
            price_col: Column name containing price to calculate EMA. Default is 'close'.
            spans: Tuple of time spans to calculate EMA.
                Default is (12, 26, 50, 200).

        Returns:
            DataFrame with EMA columns added.
            Column names have format 'ema_{span}', e.g. 'ema_12', 'ema_26'.
        """
        df = df.copy()
        for s in spans:
            df[f"ma_{s}"] = df[price_col].rolling(window=s, min_periods=s).mean()
        return df

    @st.cache_data(ttl=60)
    @staticmethod
    def add_ema(
        df: pd.DataFrame,
        price_col: str = "close",
        spans: tuple[int, ...] = (12, 26, 50, 200)
    ) -> pd.DataFrame:
        """
        Calculate EMA for specified time spans and add corresponding columns to DataFrame.

        Args:
            df: DataFrame containing price data.
            price_col: Column name containing price to calculate EMA. Default is 'close'.
            spans: Tuple of time spans to calculate EMA.
                Default is (12, 26, 50, 200).

        Returns:
            DataFrame with EMA columns added.
            Column names have format 'ema_{span}', e.g. 'ema_12', 'ema_26'.
        """
        df = df.copy()
        for s in spans:
            df[f"ema_{s}"] = df[price_col].ewm(span=s, adjust=False).mean()
        return df

    @st.cache_data(ttl=60)
    @staticmethod
    def add_rsi(
        df: pd.DataFrame,
        price_col: str = "close",
        periods: tuple[int, ...] = (14,)
    ) -> pd.DataFrame:
        """
        Calculate RSI using Wilder smoothing and add corresponding columns to DataFrame.

        Args:
            df: DataFrame containing price data.
            price_col: Column name containing price to calculate RSI. Default is 'close'.
            periods: Tuple of periods to calculate RSI. Default is (14,).

        Returns:
            DataFrame with RSI columns added.
            Column names have format 'rsi_{period}', e.g. 'rsi_14'.
            RSI values range from 0-100.

        Note:
            RSI > 70 is usually considered Overbought.
            RSI < 30 is usually considered Oversold.
        """
        df = df.copy()
        delta = df[price_col].diff()

        gain = delta.clip(lower=0.0)
        loss = (-delta).clip(lower=0.0)

        # Wilder smoothing
        for period in periods:
            alpha = 1 / period
            avg_gain = gain.ewm(alpha=alpha, adjust=False).mean()
            avg_loss = loss.ewm(alpha=alpha, adjust=False).mean()

            rs = avg_gain / avg_loss.replace(0, np.nan)
            df[f"rsi_{period}"] = 100 - (100 / (1 + rs))
        return df
