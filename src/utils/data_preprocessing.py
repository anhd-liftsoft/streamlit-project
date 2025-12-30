import pandas as pd


class DataPreprocessor:
    @staticmethod
    def convert_to_datetime(df: pd.DataFrame, column: str, unit: str = None) -> pd.DataFrame:
        """
        Convert a timestamp column to datetime.
        Args:
            df (pd.DataFrame): DataFrame containing the data.
            column (str): Name of the timestamp column to convert.
            unit (str): Unit of the timestamp (default is 'us' - microseconds).
        Returns:
            pd.DataFrame: DataFrame with the timestamp column converted to datetime.
        """
        if unit:
            df[column] = pd.to_datetime(df[column], unit=unit)
        else:
            df[column] = pd.to_datetime(df[column])
        return df
