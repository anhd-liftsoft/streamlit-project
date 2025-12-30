"""
Module manages filter for streamlit app

Supported filter types:
    - multiselect: Select multiple values from list
    - selectbox: Select one value from list
    - range: Slider select range of values
    - daterange: Select date range
    - timerange: Select time range (hour:minute)
    - text: Input text to search
    - checkbox: Checkbox true/false
"""

import streamlit as st
import pandas as pd
from datetime import time


def render_filters(filters: list[dict], scope: str) -> dict:
    """
    Render các filter widgets trong Streamlit sidebar.

    Args:
        filters: List of dictionary describe filter. Each filter has keys:
            - 'key' (required): Unique key for filter.
            - 'type' (required): Filter type ('multiselect', 'selectbox',
              'range', 'daterange', 'timerange', 'text', 'checkbox').
            - 'label' (optional): Label to display. Default is key.
            - 'options' (for multiselect/selectbox): List of options.
            - 'min', 'max' (for range): Min/max value.
            - 'default' (optional): Default value.
            - 'default_start', 'default_end' (for timerange): Default time.
        scope: Namespace to avoid session_state conflict between pages.
            Example: 'trades', 'overview'.

    Returns:
        Dictionary with key is filter key and value is current value of filter.
    """
    values = {}

    for f in filters:
        key = f"{scope}:{f['key']}"
        label = f.get("label", f["key"])
        type = f["type"]

        if type == "multiselect":
            values[f["key"]] = st.multiselect(label, f["options"], default=f.get("default", []), key=key)

        elif type == "selectbox":
            values[f["key"]] = st.selectbox(label, f["options"], index=f.get("index", 0), key=key)

        elif type == "range":
            values[f["key"]] = st.slider(
                label,
                min_value=f["min"],
                max_value=f["max"],
                value=f.get("default", (f["min"], f["max"])),
                key=key
            )

        elif type == "daterange":
            values[f["key"]] = st.date_input(label, value=f["default"], key=key)

        elif type == "timerange":
            default_start = f.get("default_start", time(0, 0))
            default_end = f.get("default_end", time(23, 59))
            col1, col2 = st.columns(2)
            with col1:
                start_time = st.time_input(
                    f"{label} - Từ",
                    value=default_start,
                    key=f"{key}_start",
                    step=60
                )
            with col2:
                end_time = st.time_input(
                    f"{label} - Đến",
                    value=default_end,
                    key=f"{key}_end",
                    step=60
                )
            values[f["key"]] = (start_time, end_time)

        elif type == "text":
            values[f["key"]] = st.text_input(label, value=f.get("default", ""), key=key)

        elif type == "checkbox":
            values[f["key"]] = st.checkbox(label, value=f.get("default", False), key=key)

        else:
            st.warning(f"Unknown filter type: {type}")
    return values


def apply_filters(df: pd.DataFrame, filters: list[dict], values: dict) -> pd.DataFrame:
    """
    Apply filters to DataFrame and return filtered data.

    Args:
        df: DataFrame cần lọc.
        filters: List of dictionary describe filter. Each filter has keys:
            - 'key' (required): Key of filter, must match with key in values.
            - 'type' (required): Filter type ('multiselect', 'selectbox',
              'range', 'daterange', 'timerange', 'text', 'checkbox').
            - 'column' (optional): Column name in DataFrame. Default is key.
            - 'all_value' (optional): Value representing "all" (skip filter).
        values: Dictionary containing current filter values, returned from
            render_filters().

    Returns:
        DataFrame after applying filters.

    Note:
        - With 'timerange', supports time range across midnight
          (e.g., 22:00 - 06:00).
        - With 'text', case-insensitive search.
        - With 'multiselect/selectbox', if value is 'all_value' then
          filter will be skipped.
    """
    mask = pd.Series(True, index=df.index)
    for f in filters:
        col = f.get("column", f["key"])
        key = f["key"]
        type = f["type"]
        value = values.get(key)

        if type in ("multiselect", "selectbox"):
            # Skip filtering if value is the "all_value" (e.g., "All")
            all_val = f.get("all_value")
            if value == all_val:
                continue

            if isinstance(value, list) and len(value) > 0:
                mask &= df[col].isin(value)
            elif value is not None:
                mask &= df[col].eq(value)

        elif type == "range":
            lo, hi = value
            mask &= df[col].between(lo, hi)

        elif type == "text":
            if value and value.strip():
                mask &= df[col].astype(str).str.contains(value.strip(), case=False, na=False)

        elif type == "checkbox":
            if value is True:
                mask &= df[col].astype(bool)

        elif type == "daterange":
            start, end = value
            mask &= df[col].dt.date.between(start, end)

        elif type == "timerange":
            start_time, end_time = value
            col_time = df[col].dt.time
            if start_time <= end_time:
                mask &= (col_time >= start_time) & (col_time <= end_time)
            else:
                mask &= (col_time >= start_time) | (col_time <= end_time)

    return df[mask]
