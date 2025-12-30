import pandas as pd
import streamlit as st

DATA_DIR = "/app/data/"


class DataLoader:
    """
    Collection of static data loading helpers.
    """

    @st.cache_data(ttl=60)
    @staticmethod
    def load_csv(name: str) -> pd.DataFrame:
        """
        Load a CSV file from the data directory.
        Args:
            name (str): CSV file name.
        Returns:
            pd.DataFrame: Data from the CSV file.
        """
        if not name.endswith(".csv"):
            name += ".csv"
        path = DATA_DIR + name
        return pd.read_csv(path)
