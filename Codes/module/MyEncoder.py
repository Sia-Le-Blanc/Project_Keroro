import re
import pandas as pd
import numpy as np

class MyRangeEncoder:
    def __init__(self, mode='middle', nan_value=np.nan):
        assert mode in ['middle', 'mean'], "mode must be 'middle' or 'mean'"
        self.mode = mode
        self.nan_value = nan_value
        self.columns = []
        self.mappings = {}

    def parse_value(self, text):
        try:
            # 단일 숫자
            m = re.match(r"(\d+)[개건]", text)
            if m and "초과" not in text and "이하" not in text:
                return float(m.group(1))

            # 범위
            m = re.match(r"(\d+)[개건]초과 (\d+)[개건]이하", text)
            if m:
                start = int(m.group(1)) + 1
                end = int(m.group(2))
                if self.mode == 'middle':
                    return (start + end) / 2
                elif self.mode == 'mean':
                    return np.mean(list(range(start, end + 1)))

            # 초과
            m = re.match(r"(\d+)[개건] 초과", text)
            if m:
                return int(m.group(1)) + 5

        except:
            pass
        return self.nan_value

    def fit_transform(self, df: pd.DataFrame, columns: list = None):
        df_encoded = df.copy()
        self.columns = []

        # ✅ DataFrame이 들어온 경우 → columns 추출
        if isinstance(columns, pd.DataFrame):
            columns = columns.columns.tolist()

        # ✅ 자동 선택: object/string 컬럼
        if columns is None:
            columns = df.select_dtypes(include=['object', 'string']).columns.tolist()

        for col in columns:
            # ✅ object 또는 string 타입만 처리
            if not (df[col].dtype == 'object' or pd.api.types.is_string_dtype(df[col])):
                continue

            mapping = {}
            for val in df[col].astype(str).unique():
                parsed = self.parse_value(val)
                mapping[val] = parsed
            self.mappings[col] = mapping
            df_encoded[col] = df[col].astype(str).map(mapping)
            self.columns.append(col)

        return df_encoded



    def transform(self, df: pd.DataFrame):
        df_encoded = df.copy()
        for col in self.columns:
            if col in df.columns:
                mapping = self.mappings[col]
                df_encoded[col] = df[col].astype(str).map(mapping)

                if df_encoded[col].isnull().any():
                    new_vals = df[col][df_encoded[col].isnull()].unique()
                    print(f"[경고] '{col}' 컬럼에서 학습되지 않은 값 등장: {new_vals}")

        return df_encoded

    def inverse_transform(self, df: pd.DataFrame):
        df_decoded = df.copy()
        for col in self.columns:
            if col in df.columns:
                reverse_map = {}
                for k, v in self.mappings[col].items():
                    if v not in reverse_map:
                        reverse_map[v] = k
                df_decoded[col] = df[col].map(reverse_map)
        return df_decoded

    def inverse_transform_column(self, series: pd.Series, col_name: str):
        if col_name not in self.mappings:
            raise ValueError(f"[{col_name}]에 대한 인코더가 존재하지 않습니다.")
        reverse_map = {}
        for k, v in self.mappings[col_name].items():
            if v not in reverse_map:
                reverse_map[v] = k
        return series.map(reverse_map)

    def print_mappings(self):
        for col, mapping in self.mappings.items():
            print(f"[{col}] 매핑:")
            for k, v in sorted(mapping.items(), key=lambda x: x[1]):
                print(f"  {k} → {v}")
            print()
