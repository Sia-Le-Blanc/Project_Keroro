from sklearn.preprocessing import LabelEncoder
import pandas as pd

class MyEncoder:
    def __init__(self):
        self.encoders = {}

    def fit_transform(self, df: pd.DataFrame, columns: list):
        df_encoded = df.copy()
        for col in columns:
            le = LabelEncoder()
            df_encoded[col] = le.fit_transform(df[col].astype(str))
            self.encoders[col] = le
        return df_encoded

    def transform(self, df: pd.DataFrame):
        df_encoded = df.copy()
        for col, le in self.encoders.items():
            if col in df.columns:
                df_encoded[col] = le.transform(df[col].astype(str))
        return df_encoded

    def inverse_transform(self, df: pd.DataFrame):
        df_decoded = df.copy()
        for col, le in self.encoders.items():
            if col in df.columns:
                df_decoded[col] = le.inverse_transform(df[col])
        return df_decoded

    def inverse_transform_column(self, series: pd.Series, col_name: str):
        """
        단일 컬럼 Series를 역변환. 해당 컬럼에 대한 LabelEncoder가 저장되어 있어야 함.
        """
        if col_name not in self.encoders:
            raise ValueError(f"[{col_name}]에 대한 인코더가 존재하지 않습니다.")
        le = self.encoders[col_name]
        return le.inverse_transform(series)
