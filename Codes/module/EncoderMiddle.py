import re
import pandas as pd
import numpy as np

class MyEncoderMiddle:
    def __init__(self):
        self.columns = []
        self.mappings = {}  # {col: {original_str: encoded_value}}

    def parse_value(self, text):
        try:
            # 단일 숫자
            m = re.match(r"(\d+)[개건]", text)
            if m and "초과" not in text and "이하" not in text:
                return float(m.group(1))

            # 범위
            m = re.match(r"(\d+)[개건]초과 (\d+)[개건]이하", text)
            if m:
                lower = int(m.group(1)) + 1
                upper = int(m.group(2))
                return (lower + upper) / 2

            # 초과만 있는 경우
            m = re.match(r"(\d+)[개건] 초과", text)
            if m:
                return int(m.group(1)) + 5

        except:
            pass
        return np.nan

    def fit_transform(self, df: pd.DataFrame, columns: list):
        self.columns = columns
        df_encoded = df.copy()
        for col in columns:
            mapping = {}
            for val in df[col].astype(str).unique():
                encoded = self.parse_value(val)
                mapping[val] = encoded
            self.mappings[col] = mapping
            df_encoded[col] = df[col].astype(str).map(mapping)
        return df_encoded

    def transform(self, df: pd.DataFrame):
        df_encoded = df.copy()
        for col in self.columns:
            if col in df.columns:
                mapping = self.mappings[col]
                df_encoded[col] = df[col].astype(str).map(mapping)
        return df_encoded

    def inverse_transform(self, df: pd.DataFrame):
        df_decoded = df.copy()
        for col in self.columns:
            if col in df.columns:
                reverse_map = {v: k for k, v in self.mappings[col].items()}
                df_decoded[col] = df[col].map(reverse_map)
        return df_decoded
