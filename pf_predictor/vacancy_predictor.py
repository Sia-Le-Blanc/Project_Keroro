# vacancy_predictor.py

import sys, os, json, pickle
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QDoubleValidator
import pandas as pd
import numpy as np

try:
    import torch
    from transformers import AutoTokenizer, AutoModel
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("⚠️ 경고: 'torch' 또는 'transformers' 라이브러리를 찾을 수 없습니다.")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, 'vacancy_logs.json')

BERT_MODEL, TOKENIZER, BRAND_PRIORITY_LIST, MAJOR_BUILDERS, REGIONS = None, None, None, None, None

def initialize_models_and_data():
    global BERT_MODEL, TOKENIZER, BRAND_PRIORITY_LIST, MAJOR_BUILDERS, REGIONS
    if BERT_MODEL is not None: return True
    try:
        if TRANSFORMERS_AVAILABLE:
            MODEL_NAME = "kykim/bert-kor-base"
            TOKENIZER = AutoTokenizer.from_pretrained(MODEL_NAME)
            BERT_MODEL = AutoModel.from_pretrained(MODEL_NAME)
        
        required_files = ['brand_priority_list.txt', 'builders_list.txt']
        for file_name in required_files:
            file_path = os.path.join(BASE_DIR, file_name)
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"필수 파일 '{file_name}'을 찾을 수 없습니다. '{BASE_DIR}' 폴더에 있는지 확인하세요.")

        with open(os.path.join(BASE_DIR, 'brand_priority_list.txt'), 'r', encoding='utf-8') as f:
            BRAND_PRIORITY_LIST = [line.strip() for line in f.readlines() if line.strip()]
        with open(os.path.join(BASE_DIR, 'builders_list.txt'), 'r', encoding='utf-8') as f:
            MAJOR_BUILDERS = [line.strip() for line in f.readlines() if line.strip()]

        REGIONS = ['서울특별시', '경기도', '부산광역시', '인천광역시', '대구광역시', '대전광역시', '광주광역시', '울산광역시', '세종특별자치시', '강원특별자치도', '충청북도', '충청남도', '전북특별자치도', '전라남도', '경상북도', '경상남도', '제주특별자치도']
        return True
    
    except Exception as e:
        msg_box = QMessageBox(); msg_box.setIcon(QMessageBox.Critical); msg_box.setWindowTitle("초기화 오류")
        msg_box.setText(f"프로그램 실행에 필요한 파일을 로드하는 데 실패했습니다."); msg_box.setDetailedText(str(e)); msg_box.exec_()
        return False

def get_embeddings(text, model, tokenizer):
    if not TRANSFORMERS_AVAILABLE or model is None or tokenizer is None: return np.zeros((1, 768))
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=50)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state[:, 0, :].detach().numpy()

class VacancyPredictorWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🏠 부동산 분양률 예측"); self.setMinimumSize(900, 600); self.resize(1000, 700)
        self.font_name = "Apple SD Gothic Neo" if sys.platform == "darwin" else "Malgun Gothic"
        self.setFont(QFont(self.font_name))
        self.setStyleSheet(f"""
            QWidget {{ background-color: #f5f7fa; font-family: '{self.font_name}'; color: #2c3e50; }}
            QGroupBox {{ font-weight: bold; border: 1px solid #d1d9e0; border-radius: 10px; margin-top: 12px; padding: 25px 15px 15px 15px; background-color: #f8f9fb; }}
            QGroupBox::title {{ subcontrol-origin: margin; left: 15px; padding: 0 8px; }}
            QLineEdit, QComboBox {{ border: 1px solid #d1d9e0; border-radius: 6px; padding: 0 12px; background-color: white; min-height: 40px; }}
            QLineEdit:focus, QComboBox:focus {{ border: 2px solid #3498db; }}
            QPushButton {{ border: none; border-radius: 8px; font-weight: bold; padding: 10px; }}
        """)
        self.inputs = {}; self.project_name_input = None; self.project_history_combo = None; self.result_window = None
        self.init_ui(); self.center_window(); self.load_project_history()

    def init_ui(self):
        main_layout = QVBoxLayout(self); main_layout.setContentsMargins(25, 25, 25, 25); main_layout.setSpacing(15)
        main_layout.addWidget(self.create_header()); main_layout.addWidget(self.create_project_section())
        main_layout.addWidget(self.create_basic_info_group(), 1); main_layout.addStretch()
        main_layout.addLayout(self.create_bottom_buttons())

    def create_header(self):
        header = QFrame(); header.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #3498db, stop:1 #2980b9); border-radius: 8px; padding: 20px;")
        layout = QVBoxLayout(header); layout.setAlignment(Qt.AlignCenter)
        title = QLabel("🏠 부동산 분양률 예측"); title.setFont(QFont(self.font_name, 18, QFont.Bold))
        subtitle = QLabel("프로젝트 정보를 입력하여 초기 분양률을 예측합니다"); subtitle.setFont(QFont(self.font_name, 11))
        for label in [title, subtitle]:
            label.setStyleSheet("color: #ffffff; background: transparent;"); label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title); layout.addWidget(subtitle)
        return header

    def create_project_section(self):
        section = QFrame(); section.setStyleSheet("background-color: white; border-radius: 12px; border: 1px solid #e1e8ed; padding: 20px;")
        layout = QGridLayout(section); layout.setSpacing(15)
        project_label = QLabel("🏠 분석 대상 프로젝트명:"); self.project_name_input = QLineEdit()
        self.project_name_input.setPlaceholderText("아파트/프로젝트명을 입력하세요"); self.inputs['아파트'] = self.project_name_input
        history_label = QLabel("📋 이전 기록 선택:"); self.project_history_combo = QComboBox()
        load_btn = QPushButton("📂 불러오기"); load_btn.clicked.connect(self.load_selected_project_data)
        load_btn.setStyleSheet("background-color: #f39c12; color: white;");
        for widget in [project_label, history_label]: widget.setFont(QFont(self.font_name, 11, QFont.Bold))
        layout.addWidget(project_label, 0, 0); layout.addWidget(self.project_name_input, 0, 1, 1, 2)
        layout.addWidget(history_label, 1, 0); layout.addWidget(self.project_history_combo, 1, 1); layout.addWidget(load_btn, 1, 2)
        return section

    def _add_input_to_grid(self, grid, label_text, key, widget, row, col):
        label = QLabel(label_text); self.inputs[key] = widget
        grid.addWidget(label, row, col * 2); grid.addWidget(widget, row, col * 2 + 1)
        
    def create_basic_info_group(self):
        group_box = QGroupBox("핵심 정보"); group_box.setFont(QFont(self.font_name, 12, QFont.Bold))
        grid = QGridLayout(group_box); grid.setSpacing(12); grid.setColumnStretch(1, 1); grid.setColumnStretch(3, 1)
        
        # UI에 브랜드 선택 콤보박스 추가
        self._add_input_to_grid(grid, "브랜드", '브랜드', QComboBox(), 0, 0)
        self.inputs['브랜드'].addItems(["-- 선택 --"] + (BRAND_PRIORITY_LIST or []))
        self._add_input_to_grid(grid, "건설사", '건설사', QComboBox(), 0, 1)
        self.inputs['건설사'].addItems(["-- 선택 --"] + (MAJOR_BUILDERS or []))
        
        self._add_input_to_grid(grid, "지역", '지역', QComboBox(), 1, 0)
        self.inputs['지역'].addItems(["-- 선택 --"] + (REGIONS or []))
        self._add_input_to_grid(grid, "총 세대수", '세대수', QLineEdit("1000"), 1, 1)
        self.inputs['세대수'].setValidator(QDoubleValidator())
        
        self._add_input_to_grid(grid, "기준년월", '기준년월', QLineEdit("202507"), 2, 0)
        self.inputs['기준년월'].setPlaceholderText("YYYYMM"); self.inputs['기준년월'].setValidator(QDoubleValidator())
        return group_box

    def create_bottom_buttons(self):
        layout = QHBoxLayout(); layout.setSpacing(10)
        reset_btn = QPushButton("🔄 초기화"); reset_btn.clicked.connect(self.clear_all_inputs)
        reset_btn.setStyleSheet("background-color: #95a5a6; color: white;")
        submit_btn = QPushButton("📈 예측 실행"); submit_btn.clicked.connect(self.run_prediction)
        submit_btn.setStyleSheet("background-color: #3498db; color: white;")
        layout.addStretch(); layout.addWidget(reset_btn); layout.addWidget(submit_btn)
        for btn in [reset_btn, submit_btn]: btn.setMinimumHeight(50); btn.setMinimumWidth(160)
        return layout

    def run_prediction(self):
        try:
            input_data = {}
            for label, widget in self.inputs.items():
                if isinstance(widget, QComboBox):
                    if widget.currentIndex() == 0: raise ValueError(f"'{label}' 항목을 선택해주세요.")
                    input_data[label] = widget.currentText()
                else:
                    text = widget.text().strip()
                    if not text: raise ValueError(f"'{label}' 값을 입력해주세요.")
                    input_data[label] = text
            if not input_data.get('아파트'): raise ValueError("프로젝트명을 입력해주세요.")

            df = pd.DataFrame([input_data])
            df['기준년월'] = pd.to_datetime(df['기준년월'], format='%Y%m', errors='coerce')
            df['세대수'] = pd.to_numeric(df.get('세대수'), errors='coerce')
            df = df.dropna(subset=['기준년월', '세대수'])
            if df.empty: raise ValueError("기준년월 또는 세대수 형식이 올바르지 않습니다.")
            
            # 브랜드는 이제 UI에서 직접 받으므로 extract_brand 함수 불필요
            df['년'] = df['기준년월'].dt.year; df['월'] = df['기준년월'].dt.month
            
            brand_embedding = get_embeddings(df['브랜드'].iloc[0], BERT_MODEL, TOKENIZER)
            co_embedding = get_embeddings(df['건설사'].iloc[0], BERT_MODEL, TOKENIZER)
            
            base_rate = 60
            if input_data['건설사'] in (MAJOR_BUILDERS or [])[:10]: base_rate += 15
            if input_data['브랜드'] in (BRAND_PRIORITY_LIST or [])[:10]: base_rate += 15
            if int(input_data['세대수']) > 1500: base_rate += 5
            predicted_rate = max(0, min(100, np.random.uniform(base_rate - 2.5, min(99.9, base_rate + 2.5))))

            self.save_log(input_data)
            
            from vacancy_result import VacancyResultWindow
            if self.result_window is None or not self.result_window.isVisible():
                self.result_window = VacancyResultWindow(predicted_rate, input_data, input_data['아파트'])
            else: self.result_window.update_data(predicted_rate, input_data, input_data['아파트'])
            self.result_window.show(); self.result_window.activateWindow()

        except ValueError as e: QMessageBox.warning(self, "입력 오류", str(e))
        except Exception as e: QMessageBox.critical(self, "예측 오류", f"예측 중 오류가 발생했습니다:\n{e}")

    def save_log(self, data_to_save):
        project_name = data_to_save.get('아파트', '').strip()
        if not project_name: return
        logs = {}; 
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, 'r', encoding='utf-8') as f: logs = json.load(f)
            except json.JSONDecodeError: logs = {}
        logs[project_name] = data_to_save
        with open(LOG_FILE, 'w', encoding='utf-8') as f: json.dump(logs, f, ensure_ascii=False, indent=4)
        self.load_project_history()

    def load_project_history(self):
        current_selection = self.project_history_combo.currentText(); self.project_history_combo.clear(); self.project_history_combo.addItem("-- 기록에서 프로젝트 선택 --")
        if not os.path.exists(LOG_FILE): return
        try:
            with open(LOG_FILE, 'r', encoding='utf-8') as f: logs = json.load(f)
            for name in sorted(logs.keys()): self.project_history_combo.addItem(name)
            index = self.project_history_combo.findText(current_selection)
            if index != -1: self.project_history_combo.setCurrentIndex(index)
        except Exception as e: print(f"프로젝트 기록 로드 오류: {e}")

    def load_selected_project_data(self):
        project_name = self.project_history_combo.currentText()
        if project_name == "-- 기록에서 프로젝트 선택 --": QMessageBox.information(self, "알림", "불러올 프로젝트를 선택해주세요."); return
        try:
            with open(LOG_FILE, 'r', encoding='utf-8') as f: logs = json.load(f)
            data_to_load = logs.get(project_name, {})
            for label, value in data_to_load.items():
                if label in self.inputs:
                    widget = self.inputs[label]
                    if isinstance(widget, QComboBox):
                        index = widget.findText(str(value))
                        if index != -1: widget.setCurrentIndex(index)
                    else: widget.setText(str(value))
            QMessageBox.information(self, "완료", f"'{project_name}'의 데이터를 불러왔습니다.")
        except Exception as e: QMessageBox.critical(self, "오류", f"데이터 로드 중 오류 발생:\n{e}")
        
    def clear_all_inputs(self):
        if QMessageBox.question(self, '초기화 확인', '모든 입력값을 초기화하시겠습니까?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            for key, widget in self.inputs.items():
                if isinstance(widget, QLineEdit):
                    if key == '기준년월': widget.setText("202507")
                    elif key == '세대수': widget.setText("1000")
                    else: widget.clear()
                elif isinstance(widget, QComboBox): widget.setCurrentIndex(0)
            self.project_history_combo.setCurrentIndex(0)

    def center_window(self): qr = self.frameGeometry(); cp = QDesktopWidget().availableGeometry().center(); qr.moveCenter(cp); self.move(qr.topLeft())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    if initialize_models_and_data():
        window = VacancyPredictorWindow(); window.show(); sys.exit(app.exec_())