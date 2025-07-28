import sys
import json
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QFrame, QMessageBox, QDesktopWidget,
    QShortcut, QComboBox, QGridLayout, QGroupBox, QScrollArea
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QDoubleValidator, QKeySequence, QIntValidator

# ML/데이터 처리 라이브러리 임포트
try:
    import pandas as pd
    import numpy as np
    import tensorflow as tf
    import joblib
except ImportError as e:
    QMessageBox.critical(None, "라이브러리 오류",
                         f"필수 라이브러리가 설치되지 않았습니다: {e.name}\n"
                         f"터미널에서 'pip install tensorflow pandas scikit-learn joblib' 명령어를 실행하여 설치해주세요.",
                         QMessageBox.Ok)
    sys.exit()

# 예측 결과 창 import
try:
    from vacancy_result import VacancyResultWindow
    RESULT_WINDOW_AVAILABLE = True
except ImportError:
    RESULT_WINDOW_AVAILABLE = False
    print("⚠️ vacancy_result.py 파일이 없습니다. 간단한 결과 메시지로 표시됩니다.")

class VacancyPredictorWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🏠 부동산 분양률 예측 (ML 모델 기반)")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        self.setStyleSheet("QWidget { background-color: #f5f7fa; font-family: 'Malgun Gothic'; }")

        self.inputs = {}
        self.model = None
        self.preprocessor = None
        self.median_values = None
        self.model_features = None

        if not self._load_model_assets():
            QTimer.singleShot(0, self.close)
            return

        self.init_ui()
        self.center_window()

    def _load_model_assets(self):
        assets_path = 'model_assets'
        model_file = os.path.join(assets_path, 'apartment_sales_rate_prediction_model.keras')
        preprocessor_file = os.path.join(assets_path, 'final_preprocessor.joblib')
        median_file = os.path.join(assets_path, 'final_median_values.json')
        features_file = os.path.join(assets_path, 'model_features.json')

        try:
            if not os.path.exists(assets_path):
                 raise FileNotFoundError(f"'{assets_path}' 폴더를 찾을 수 없습니다.")
            self.model = tf.keras.models.load_model(model_file)
            self.preprocessor = joblib.load(preprocessor_file)
            with open(median_file, 'r', encoding='utf-8') as f: self.median_values = json.load(f)
            with open(features_file, 'r', encoding='utf-8') as f: self.model_features = json.load(f)
            return True
        except Exception as e:
            QMessageBox.critical(None, "모델 로딩 오류", f"모델 자산 로딩 중 오류가 발생했습니다:\n{e}", QMessageBox.Ok)
            return False

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(15)

        header = self.create_header()
        main_layout.addWidget(header)

        project_section = self.create_project_section()
        main_layout.addWidget(project_section)

        card_container = QFrame()
        card_container.setStyleSheet("background-color: white; border-radius: 12px; border: 1px solid #e1e8ed;")
        card_layout = QVBoxLayout(card_container)
        card_layout.setContentsMargins(20, 20, 20, 20)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        scroll_content = QWidget()
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setSpacing(20)
        
        content_layout.addWidget(self.create_basic_info_group())
        content_layout.addWidget(self.create_price_info_group())
        content_layout.addWidget(self.create_convenience_env_group())
        content_layout.addWidget(self.create_edu_transport_env_group())
        
        scroll_area.setWidget(scroll_content)
        card_layout.addWidget(scroll_area)
        main_layout.addWidget(card_container, 1)

        button_container = self.create_button_frame()
        main_layout.addWidget(button_container)

    def create_header(self):
        header = QFrame()
        header.setFixedHeight(100)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #e74c3c, stop:1 #c0392b);
                border-radius: 6px; padding: 8px;
            }
        """)
        main_layout = QHBoxLayout(header)
        main_layout.setContentsMargins(15, 8, 15, 8)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(1)
        title_layout.setContentsMargins(5, 0, 0, 0)
        
        title = QLabel("🏠 부동산 분양률 예측")
        title.setFont(QFont("Malgun Gothic", 16, QFont.Bold))
        title.setStyleSheet("color: white; background: transparent;")

        subtitle = QLabel("머신러닝 모델을 사용하여 분양률을 정밀하게 예측합니다")
        subtitle.setFont(QFont("Malgun Gothic", 9))
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.85); background: transparent;")

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        main_layout.addLayout(title_layout, 1)
        return header
    
    def create_project_section(self):
        section = QFrame()
        section.setStyleSheet("background-color: white; border-radius: 12px; border: 1px solid #e1e8ed; padding: 20px;")
        layout = QHBoxLayout(section)
        layout.setSpacing(15)

        project_label = QLabel("🏢 프로젝트명:")
        project_label.setFont(QFont("Malgun Gothic", 12, QFont.Bold))
        project_label.setStyleSheet("color: #2c3e50; background: transparent;")

        self.inputs['아파트'] = QLineEdit()
        self.inputs['아파트'].setPlaceholderText("분석할 아파트명을 입력하세요")
        self.inputs['아파트'].setFixedHeight(40)
        self.inputs['아파트'].setStyleSheet(self.get_line_edit_style())
        
        layout.addWidget(project_label)
        layout.addWidget(self.inputs['아파트'], 1)
        return section

    def create_input_field(self, layout, row, col, label_text, key, validator=None, placeholder="0"):
        label = QLabel(label_text)
        label.setFont(QFont("Malgun Gothic", 9))
        label.setStyleSheet("color: #34495e; font-weight: normal; padding-top: 5px;")
        
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)
        if validator: line_edit.setValidator(validator)
        line_edit.setFixedHeight(35)
        line_edit.setStyleSheet(self.get_line_edit_style())
        
        self.inputs[key] = line_edit
        
        item_layout = QVBoxLayout()
        item_layout.setContentsMargins(0,0,0,0)
        item_layout.setSpacing(4)
        item_layout.addWidget(label)
        item_layout.addWidget(line_edit)
        
        layout.addLayout(item_layout, row, col)

    def create_combo_field(self, layout, row, col, label_text, key, items):
        label = QLabel(label_text)
        label.setFont(QFont("Malgun Gothic", 9))
        label.setStyleSheet("color: #34495e; font-weight: normal; padding-top: 5px;")

        combo = QComboBox()
        combo.addItems(items)
        combo.setFixedHeight(35)
        combo.setStyleSheet(self.get_combo_style())

        self.inputs[key] = combo
        
        item_layout = QVBoxLayout()
        item_layout.setContentsMargins(0,0,0,0)
        item_layout.setSpacing(4)
        item_layout.addWidget(label)
        item_layout.addWidget(combo)
        
        layout.addLayout(item_layout, row, col)
    
    def create_group_box(self, title):
        group_box = QGroupBox(title)
        group_box.setFont(QFont("Malgun Gothic", 11, QFont.Bold))
        group_box.setStyleSheet("""
            QGroupBox {
                border: 1px solid #d1d9e0; border-radius: 10px; margin-top: 12px;
                padding: 20px 15px 15px 15px; background-color: #f8f9fb;
            }
            QGroupBox::title {
                subcontrol-origin: margin; left: 15px; padding: 0 8px;
                color: #2c3e50; background-color: #f8f9fb;
            }
        """)
        return group_box

    def create_basic_info_group(self):
        group = self.create_group_box("1. 기본 정보")
        layout = QGridLayout(group)
        layout.setSpacing(15)
        self.create_input_field(layout, 0, 0, "기준 년도", "년", QIntValidator(2000, 2050), "예: 2023")
        self.create_input_field(layout, 0, 1, "기준 월", "월", QIntValidator(1, 12), "예: 11")
        self.create_input_field(layout, 1, 0, "지역", "지역", placeholder="예: 서울특별시 서초구")
        self.create_input_field(layout, 1, 1, "건설사", "건설사", placeholder="예: 삼성물산")
        self.create_combo_field(layout, 2, 0, "준공 여부", "준공여부", ["미준공", "준공"])
        self.create_input_field(layout, 2, 1, "총 세대수", "세대수", QIntValidator())
        self.create_input_field(layout, 3, 0, "공급면적(㎡)", "공급면적(㎡)", QDoubleValidator(0, 9999, 2))
        self.create_input_field(layout, 3, 1, "전용면적(㎡)", "전용면적(㎡)", QDoubleValidator(0, 9999, 2))
        self.create_input_field(layout, 4, 0, "일반분양 세대수", "일반분양", QIntValidator())
        self.create_input_field(layout, 4, 1, "특별분양 세대수", "특별분양", QIntValidator())
        self.create_input_field(layout, 5, 0, "미분양수", "미분양수", QIntValidator())
        return group
    
    def create_price_info_group(self):
        group = self.create_group_box("2. 가격/금융 정보")
        layout = QGridLayout(group)
        layout.setSpacing(15)
        self.create_input_field(layout, 0, 0, "분양가(만원)", "분양가(만원)", QDoubleValidator(0, 999999, 2))
        self.create_input_field(layout, 0, 1, "주변시세 평균(만원)", "주변시세 평균(만원)", QDoubleValidator(0, 999999, 2))
        self.create_input_field(layout, 1, 0, "금리(%)", "금리", QDoubleValidator(0, 100, 2))
        self.create_input_field(layout, 1, 1, "환율(원/달러)", "환율", QDoubleValidator(0, 9999, 2))
        return group

    def create_convenience_env_group(self):
        group = self.create_group_box("3. 주변 환경 (생활 편의)")
        layout = QGridLayout(group)
        layout.setSpacing(15)
        items = [
            ("대형마트(1.5km)", "대형마트 - 1.5km 이내"), ("대형쇼핑(3km)", "대형쇼핑 - 3km 이내"),
            ("편의점(500m)", "편의점 - 500m 이내"), ("은행(1km)", "은행 - 1km 이내"),
            ("공원(1.5km)", "공원 - 1.5km 이내"), ("관공서(1.5km)", "관공서 - 1.5km 이내"),
            ("상급병원(1.5km)", "상급병원 - 1.5km 이내"), ("상권(3km)", "상권 - 3km 이내"),
        ]
        for i, (label, key) in enumerate(items): self.create_input_field(layout, i // 2, i % 2, label, key, QIntValidator())
        return group
        
    def create_edu_transport_env_group(self):
        group = self.create_group_box("4. 주변 환경 (교육/교통)")
        layout = QGridLayout(group)
        layout.setSpacing(15)
        items = [
            ("어린이집", "어린이집"), ("유치원", "유치원"), ("초등학교(2km)", "초등학교(2km 이내)"),
            ("중학교(2km)", "중학교(2km 이내)"), ("고등학교(2km)", "고등학교(2km 이내)"),
            ("지하철역(1.5km)", "지하철 - 반경 1.5km 이내"), ("버스정류장(500m)", "버스 - 반경 500m 이내"),
            ("고속철도역(10km)", "고속철도 - 10km 이내"), ("고속도로IC(10km)", "고속도로IC - 10km 이내"),
        ]
        for i, (label, key) in enumerate(items): self.create_input_field(layout, i // 2, i % 2, label, key, QIntValidator())
        return group

    def create_button_frame(self):
        container = QFrame()
        container.setStyleSheet("background-color: white; border-radius: 12px; border: 1px solid #e1e8ed; padding: 15px;")
        layout = QHBoxLayout(container)

        clear_btn = QPushButton("🔄 초기화")
        clear_btn.setFixedHeight(45)
        clear_btn.setFont(QFont("Malgun Gothic", 11))
        clear_btn.setStyleSheet(self.get_button_style("#95a5a6", "#7f8c8d"))
        clear_btn.clicked.connect(self.clear_inputs)
        
        predict_btn = QPushButton("🔍 예측 실행")
        predict_btn.setFixedHeight(45)
        predict_btn.setFont(QFont("Malgun Gothic", 12, QFont.Bold))
        predict_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #667eea, stop:1 #764ba2);
                color: white; border: none; border-radius: 22px; padding: 12px 30px;
            }
            QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #5a6fd8, stop:1 #6a4190); }
        """)
        predict_btn.clicked.connect(self.run_prediction)

        layout.addStretch()
        layout.addWidget(clear_btn)
        layout.addWidget(predict_btn)
        return container

    def run_prediction(self):
        try:
            input_dict = self.collect_and_validate_inputs()
            if input_dict is None: return
        except ValueError as e:
            self.show_message_box("입력 오류", str(e), QMessageBox.Warning)
            return

        input_df = pd.DataFrame([input_dict])
        project_name = input_df.iloc[0]['아파트']
        if not project_name:
            self.show_message_box("입력 오류", "프로젝트명(아파트명)을 입력해주세요.", QMessageBox.Warning)
            self.inputs['아파트'].setFocus()
            return

        input_df = self.calculate_derived_features(input_df)
        
        numerical_features = self.model_features.get('numerical_features', [])
        for col in numerical_features:
            if col not in input_df or pd.isna(input_df.loc[0, col]):
                input_df[col] = self.median_values.get(col)

        try:
            model_inputs = self.prepare_model_inputs(input_df)
            prediction = self.model.predict(model_inputs)
            predicted_rate = prediction[0][0] * 100
        except Exception as e:
            self.show_message_box("예측 오류", f"모델 예측 중 오류가 발생했습니다:\n{e}", QMessageBox.Critical)
            return
            
        grade, status = self.determine_grade_and_status(predicted_rate)
        prediction_data = {'vacancy_rate': predicted_rate, 'grade': grade, 'status': status}
        original_input_data = self.get_ui_data_for_result_window(input_dict)

        if RESULT_WINDOW_AVAILABLE:
            self.result_window = VacancyResultWindow(prediction_data, original_input_data, project_name)
            self.result_window.show()
        else:
            self.show_simple_result(project_name, predicted_rate, grade, status)

    def collect_and_validate_inputs(self):
        input_dict = {}
        for key, widget in self.inputs.items():
            if isinstance(widget, QLineEdit):
                value_str = widget.text().strip()
                if not value_str:
                    input_dict[key] = np.nan
                    continue
                try:
                    if isinstance(widget.validator(), QDoubleValidator): input_dict[key] = float(value_str)
                    elif isinstance(widget.validator(), QIntValidator): input_dict[key] = int(value_str)
                    else: input_dict[key] = value_str
                except ValueError:
                    raise ValueError(f"'{key}' 필드에 올바른 숫자 형식을 입력해주세요.")
            elif isinstance(widget, QComboBox):
                input_dict[key] = widget.currentText()
        
        if input_dict.get("분양가(만원)") == 0: input_dict["분양가(만원)"] = 1.0
        return input_dict

    def calculate_derived_features(self, df):
        # NaN 값을 처리하기 위해 astype(float) 사용
        price = df['분양가(만원)'].astype(float).fillna(0)
        nearby_price = df['주변시세 평균(만원)'].astype(float).fillna(0)

        # 시세차익 자동 계산
        df['시세차익(만원)'] = price - nearby_price
        
        df['시세초과여부'] = (price > nearby_price).astype(str)
        df['시세초과비율'] = price / nearby_price.replace(0, 1)
        df['시세차익률'] = df['시세차익(만원)'] / price.replace(0, 1)
        df['전용률'] = df['전용면적(㎡)'].astype(float).fillna(0) / df['공급면적(㎡)'].astype(float).fillna(1).replace(0,1)
        df['특별분양유무'] = (df['특별분양'].astype(float).fillna(0) > 0).astype(int).astype(str)
        
        def get_interest_rate_bracket(rate):
            if pd.isna(rate): return '기타'
            rate = float(rate)
            if 1 <= rate < 2.5: return '1~2.5%'
            if 2.5 <= rate < 3.0: return '2.5~3.0%'
            if 3.0 <= rate < 3.5: return '3.0~3.5%'
            if rate >= 3.5: return '3.5%~'
            return '기타'
        df['금리구간'] = df['금리'].apply(get_interest_rate_bracket)
        return df

    def prepare_model_inputs(self, df):
        numerical_features = self.model_features.get('numerical_features', [])
        onehot_features = self.model_features.get('onehot_features', [])
        embedding_features = self.model_features.get('embedding_features', [])
        
        features_for_preprocessor = numerical_features + onehot_features
        # 누락된 열이 있다면 NaN으로 채워서 추가
        for col in features_for_preprocessor:
            if col not in df:
                df[col] = np.nan
        
        df_for_preprocessing = df[features_for_preprocessor]
        processed_numeric_ohe = self.preprocessor.transform(df_for_preprocessing)
        
        model_inputs = { self.model.input_names[0]: processed_numeric_ohe }
        for i, feature_name in enumerate(embedding_features):
            model_input_name = self.model.input_names[i + 1] 
            model_inputs[model_input_name] = tf.constant(df[feature_name].fillna('').values, dtype=tf.string)
            
        return model_inputs

    def get_ui_data_for_result_window(self, data):
        def get_val(key, default=0): return data.get(key, default) if not pd.isna(data.get(key)) else default
        gonggeup = get_val('공급면적(㎡)', 1)
        return {
            'district': get_val('지역', 'N/A'),
            'subway_nearby': get_val('지하철 - 반경 1.5km 이내') > 0,
            'bus_stop': get_val('버스 - 반경 500m 이내') > 0,
            'facilities_count': get_val('편의점 - 500m 이내') + get_val('대형마트 - 1.5km 이내'),
            'park_nearby': get_val('공원 - 1.5km 이내') > 0,
            'avg_area': get_val('전용면적(㎡)') / 3.3058,
            'avg_price_per_area': (get_val('분양가(만원)') / (gonggeup / 3.3058)),
            'elementary_school': get_val('초등학교(2km 이내)') > 0,
            'middle_school': get_val('중학교(2km 이내)') > 0,
            'high_school': get_val('고등학교(2km 이내)') > 0,
            'hospital_nearby': get_val('상급병원 - 1.5km 이내') > 0,
            'interest_rate': get_val('금리'), 'exchange_rate': get_val('환율'),
            'nearby_avg_price': (get_val('주변시세 평균(만원)') / (gonggeup / 3.3058)),
        }

    def determine_grade_and_status(self, rate):
        if rate >= 75: return "우수", "매우 안정"
        if rate >= 60: return "양호", "안정"
        if rate >= 45: return "보통", "주의"
        return "미흡", "위험"
        
    def show_simple_result(self, project, rate, grade, status):
        msg = f"'{project}' 예측 결과:\n\n- 예상 분양률: {rate:.2f}%\n- 등급: {grade}\n- 상태: {status}"
        self.show_message_box("예측 완료", msg, QMessageBox.Information)

    def clear_inputs(self):
        for widget in self.inputs.values():
            if isinstance(widget, QLineEdit): widget.clear()
            elif isinstance(widget, QComboBox): widget.setCurrentIndex(0)
    
    def center_window(self):
        screen_rect = QApplication.desktop().screenGeometry()
        self.move((screen_rect.width() - self.width()) // 2, (screen_rect.height() - self.height()) // 2)

    def show_message_box(self, title, message, icon):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(icon)
        msg_box.setStyleSheet("QLabel{min-width: 300px; font-size: 11px;}");
        msg_box.exec_()
    
    def get_line_edit_style(self):
        return """
            QLineEdit {
                border: 1px solid #d1d9e0; border-radius: 6px; padding: 8px 12px;
                font-size: 11px; color: #2c3e50; background-color: white;
            }
            QLineEdit:focus { border: 2px solid #667eea; background-color: #f8f9ff; }
            QLineEdit:hover { border: 1px solid #667eea; }
        """

    def get_combo_style(self):
        return """
            QComboBox {
                border: 1px solid #d1d9e0; border-radius: 6px; padding: 8px 12px;
                font-size: 11px; color: #2c3e50; background-color: white;
            }
            QComboBox:hover { border: 1px solid #667eea; }
        """
        
    def get_button_style(self, bg, hover_bg):
        return f"""
            QPushButton {{ 
                background-color: {bg}; color: white; border: none; 
                border-radius: 22px; padding: 12px 20px; font-weight: bold; 
            }}
            QPushButton:hover {{ background-color: {hover_bg}; }}
        """

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VacancyPredictorWindow()
    if hasattr(window, 'model') and window.model:
        window.show()
        sys.exit(app.exec_())