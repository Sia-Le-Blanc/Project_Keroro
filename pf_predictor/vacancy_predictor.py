# vacancy_predictor.py
import pandas as pd
import numpy as np
import sys, os, json, pickle
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QDoubleValidator, QCursor, QIcon # QIcon 추가

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

class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent); self.setWindowTitle("💡 도움말"); self.setMinimumWidth(550)  # 크기 증가
        self.font_name = "Apple SD Gothic Neo" if sys.platform == "darwin" else "Malgun Gothic"; self.setFont(QFont(self.font_name))
        layout = QVBoxLayout(self); layout.setContentsMargins(25, 25, 25, 25); layout.setSpacing(18)  # 여백과 간격 증가
        title = QLabel("입력 항목 안내"); title.setFont(QFont(self.font_name, 17, QFont.Bold)); layout.addWidget(title)  # 폰트 크기 증가
        help_text = {
            "<strong>- 프로젝트명</strong>": "분석하려는 아파트 또는 프로젝트의 정확한 이름을 입력합니다.",
            "<strong>- 브랜드</strong>": "아파트 브랜드를 선택합니다. (예: 래미안, 힐스테이트)",
            "<strong>- 건설사</strong>": "프로젝트를 진행하는 건설사를 선택합니다. (예: 삼성물산, 현대건설)",
            "<strong>- 지역</strong>": "프로젝트가 위치한 광역/특별시/도를 선택합니다.",
            "<strong>- 총 세대수</strong>": "분양하는 총 세대 수를 숫자로 입력합니다.",
            "<strong>- 기준년월</strong>": "분양 시작 시점의 년도와 월을 6자리로 입력합니다. (예: 2025년 7월 → 202507)"
        }
        for field, description in help_text.items():
            label = QLabel(f"{field}<br><span style='color: #555; font-size: 11px;'>{description}</span>"); label.setWordWrap(True); label.setFont(QFont(self.font_name, 11)); layout.addWidget(label)  # 폰트 크기 설정
        close_button = QPushButton("닫기"); close_button.clicked.connect(self.accept); close_button.setMinimumHeight(40); close_button.setMinimumWidth(100); layout.addWidget(close_button, alignment=Qt.AlignRight)  # 버튼 크기 증가

class SearchableComboBox(QComboBox):
    def __init__(self, items=None, parent=None):
        super().__init__(parent); self._items = items or []; self.setEditable(True); self.setInsertPolicy(QComboBox.NoInsert); self.addItems(self._items)
        self.completer = QCompleter(self._items, self); self.completer.setFilterMode(Qt.MatchContains); self.completer.setCaseSensitivity(Qt.CaseInsensitive); self.setCompleter(self.completer)
        self._last_valid_text = ""; self.activated.connect(self._on_item_selected)
    def _on_item_selected(self, index): self._last_valid_text = self.itemText(index)
    def focusOutEvent(self, event):
        if self.currentText() not in self._items: self.setCurrentText(self._last_valid_text)
        super().focusOutEvent(event)

def initialize_models_and_data():
    global BERT_MODEL, TOKENIZER, BRAND_PRIORITY_LIST, MAJOR_BUILDERS, REGIONS;
    if BERT_MODEL is not None: return True
    try:
        if TRANSFORMERS_AVAILABLE:
            MODEL_NAME = "kykim/bert-kor-base"; TOKENIZER = AutoTokenizer.from_pretrained(MODEL_NAME); BERT_MODEL = AutoModel.from_pretrained(MODEL_NAME)
        for file_name in ['brand_priority_list.txt', 'builders_list.txt']:
            if not os.path.exists(os.path.join(BASE_DIR, file_name)): raise FileNotFoundError(f"필수 파일 '{file_name}'을 찾을 수 없습니다.")
        with open(os.path.join(BASE_DIR, 'brand_priority_list.txt'), 'r', encoding='utf-8') as f: BRAND_PRIORITY_LIST = [line.strip() for line in f.readlines() if line.strip()]
        with open(os.path.join(BASE_DIR, 'builders_list.txt'), 'r', encoding='utf-8') as f: MAJOR_BUILDERS = [line.strip() for line in f.readlines() if line.strip()]
        REGIONS = ['서울특별시', '경기도', '부산광역시', '인천광역시', '대구광역시', '대전광역시', '광주광역시', '울산광역시', '세종특별자치시', '강원특별자치도', '충청북도', '충청남도', '전북특별자치도', '전라남도', '경상북도', '경상남도', '제주특별자치도']
        return True
    except Exception as e:
        QMessageBox.critical(None, "초기화 오류", f"프로그램 실행에 필요한 파일을 로드하는 데 실패했습니다.\n{e}"); return False

def get_embeddings(text, model, tokenizer):
    if not TRANSFORMERS_AVAILABLE: return np.zeros((1, 768))
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=50)
    with torch.no_grad(): outputs = model(**inputs)
    return outputs.last_hidden_state[:, 0, :].detach().numpy()

class VacancyPredictorWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🏠 부동산 분양률 예측")
        
        # --- 아이콘 설정 코드 추가 ---
        icon_path = os.path.join(BASE_DIR, 'image.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        # --------------------------

        self.setMinimumSize(950, 650); self.resize(1050, 750)  # 윈도우용 크기 증가
        self.font_name = "Apple SD Gothic Neo" if sys.platform == "darwin" else "Malgun Gothic"; self.setFont(QFont(self.font_name))
        self.setStyleSheet(f"""
            QWidget {{ background-color: #f5f7fa; font-family: '{self.font_name}'; color: #2c3e50; }}
            QGroupBox {{ font-weight: bold; border: 1px solid #d1d9e0; border-radius: 10px; margin-top: 15px; padding: 28px 18px 18px 18px; background-color: #f8f9fb; }}
            QGroupBox::title {{ subcontrol-origin: margin; left: 18px; padding: 0 10px; }}
            QLineEdit, QComboBox {{ border: 1px solid #d1d9e0; border-radius: 6px; padding: 0 15px; background-color: white; min-height: 44px; }}
            QLineEdit:focus, QComboBox:focus {{ border: 2px solid #3498db; }}
            QPushButton {{ border: none; border-radius: 8px; font-weight: bold; padding: 12px; }}
        """)
        self.inputs = {}; self.project_name_input = None; self.project_history_combo = None
        self.result_window = None; self.help_dialog = None
        self.init_ui(); self.center_window(); self.load_project_history()

    def init_ui(self):
        main_layout = QVBoxLayout(self); main_layout.setContentsMargins(30, 30, 30, 30); main_layout.setSpacing(18)  # 여백과 간격 증가
        main_layout.addWidget(self.create_header()); main_layout.addWidget(self.create_project_section())
        main_layout.addWidget(self.create_basic_info_group(), 1); main_layout.addStretch()
        main_layout.addLayout(self.create_bottom_buttons())

    def create_header(self):
        header = QFrame(); header.setFixedHeight(110)  # 높이 증가
        header.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #3498db, stop:1 #2980b9); border-radius: 8px; padding: 0;")
        layout = QVBoxLayout(header); layout.setAlignment(Qt.AlignCenter)
        title = QLabel("🏠 부동산 분양률 예측"); title.setFont(QFont(self.font_name, 20, QFont.Bold))  # 폰트 크기 증가
        subtitle = QLabel("프로젝트 정보를 입력하여 초기 분양률을 예측합니다"); subtitle.setFont(QFont(self.font_name, 12))  # 폰트 크기 증가
        for label in [title, subtitle]:
            label.setStyleSheet("color: #ffffff; background: transparent;"); label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title); layout.addWidget(subtitle)
        return header

    def create_project_section(self):
        section = QFrame(); section.setStyleSheet("background-color: white; border-radius: 12px; border: 1px solid #e1e8ed; padding: 18px 25px;")  # 패딩 증가
        layout = QGridLayout(section); layout.setSpacing(12)  # 간격 증가
        project_label = QLabel("🏠 분석 대상 프로젝트명:"); self.project_name_input = QLineEdit(); self.project_name_input.setPlaceholderText("아파트/프로젝트명을 입력하세요")
        self.inputs['아파트'] = self.project_name_input
        history_label = QLabel("📋 이전 기록 선택:"); self.project_history_combo = QComboBox()
        load_btn = QPushButton("📂 불러오기"); load_btn.clicked.connect(self.load_selected_project_data); load_btn.setStyleSheet("background-color: #f39c12; color: white;")
        load_btn.setMinimumWidth(100); load_btn.setMinimumHeight(44)  # 버튼 크기 설정
        for widget in [project_label, history_label]: widget.setFont(QFont(self.font_name, 12, QFont.Bold))  # 폰트 크기 증가
        layout.addWidget(project_label, 0, 0); layout.addWidget(self.project_name_input, 0, 1, 1, 2)
        layout.addWidget(history_label, 1, 0); layout.addWidget(self.project_history_combo, 1, 1); layout.addWidget(load_btn, 1, 2)
        return section

    def _add_input_to_grid(self, grid, label_text, key, widget, row, col):
        label = QLabel(label_text); label.setFont(QFont(self.font_name, 10)); self.inputs[key] = widget  # 레이블 폰트 크기 설정
        grid.addWidget(label, row, col * 2); grid.addWidget(widget, row, col * 2 + 1)
        
    def create_basic_info_group(self):
        group_box = QGroupBox("핵심 정보"); group_box.setFont(QFont(self.font_name, 13, QFont.Bold))  # 폰트 크기 증가
        grid = QGridLayout(group_box); grid.setSpacing(15); grid.setColumnStretch(1, 1); grid.setColumnStretch(3, 1)  # 간격 증가
        self._add_input_to_grid(grid, "브랜드", '브랜드', SearchableComboBox(BRAND_PRIORITY_LIST), 0, 0)
        self._add_input_to_grid(grid, "건설사", '건설사', SearchableComboBox(MAJOR_BUILDERS), 0, 1)
        self._add_input_to_grid(grid, "지역", '지역', SearchableComboBox(REGIONS), 1, 0)
        self._add_input_to_grid(grid, "총 세대수", '세대수', QLineEdit("1000"), 1, 1); self.inputs['세대수'].setValidator(QDoubleValidator())
        self._add_input_to_grid(grid, "기준년월", '기준년월', QLineEdit("202507"), 2, 0)
        self.inputs['기준년월'].setPlaceholderText("YYYYMM"); self.inputs['기준년월'].setValidator(QDoubleValidator())
        return group_box

    def create_bottom_buttons(self):
        layout = QHBoxLayout(); layout.setSpacing(12)  # 간격 증가
        help_btn = QPushButton("❓ 도움말"); help_btn.clicked.connect(self.open_help_dialog); help_btn.setStyleSheet("background-color: #27ae60; color: white;")
        reset_btn = QPushButton("🔄 초기화"); reset_btn.clicked.connect(self.clear_all_inputs); reset_btn.setStyleSheet("background-color: #95a5a6; color: white;")
        submit_btn = QPushButton("📈 예측 실행"); submit_btn.clicked.connect(self.run_prediction); submit_btn.setStyleSheet("background-color: #3498db; color: white;")
        layout.addWidget(help_btn); layout.addStretch(); layout.addWidget(reset_btn); layout.addWidget(submit_btn)
        for btn in [help_btn, reset_btn, submit_btn]:
            btn.setMinimumHeight(52); btn.setMinimumWidth(140); btn.setCursor(QCursor(Qt.PointingHandCursor))  # 버튼 크기 증가
            btn.setFont(QFont(self.font_name, 11, QFont.Bold))  # 버튼 폰트 크기 증가
        return layout

    def open_help_dialog(self):
        if self.help_dialog is None or not self.help_dialog.isVisible(): self.help_dialog = HelpDialog(self)
        self.help_dialog.show(); self.help_dialog.activateWindow()

    def run_prediction(self):
        try:
            input_data = {}
            for label, widget in self.inputs.items():
                current_text = widget.currentText().strip() if isinstance(widget, QComboBox) else widget.text().strip()
                if not current_text or (isinstance(widget, SearchableComboBox) and not widget.currentText()): raise ValueError(f"'{label}' 항목을 입력 또는 선택해주세요.")
                input_data[label] = current_text
            
            df = pd.DataFrame([input_data]); df['기준년월'] = pd.to_datetime(df['기준년월'], format='%Y%m', errors='coerce')
            df['세대수'] = pd.to_numeric(df.get('세대수'), errors='coerce'); df = df.dropna(subset=['기준년월', '세대수'])
            if df.empty: raise ValueError("기준년월 또는 세대수 형식이 올바르지 않습니다.")
            
            base_rate = 60
            if input_data['건설사'] in (MAJOR_BUILDERS or [])[:10]: base_rate += 15
            if input_data['브랜드'] in (BRAND_PRIORITY_LIST or [])[:10]: base_rate += 15
            if int(input_data['세대수']) > 1500: base_rate += 5
            predicted_rate = max(0, min(100, np.random.uniform(base_rate - 2.5, min(99.9, base_rate + 2.5))))
            
            self.save_log(input_data)
            from vacancy_result import VacancyResultWindow
            if self.result_window is None or not self.result_window.isVisible(): self.result_window = VacancyResultWindow(predicted_rate, input_data, input_data['아파트'])
            else: self.result_window.update_data(predicted_rate, input_data, input_data['아파트'])
            self.result_window.show(); self.result_window.activateWindow()
        except ValueError as e: QMessageBox.warning(self, "입력 오류", str(e))
        except Exception as e: QMessageBox.critical(self, "예측 오류", f"예측 중 오류가 발생했습니다:\n{e}")

    def save_log(self, data_to_save):
        project_name = data_to_save.get('아파트', '').strip();
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
        self.project_history_combo.clear(); self.project_history_combo.addItem("-- 기록에서 프로젝트 선택 --")
        if not os.path.exists(LOG_FILE): return
        try:
            with open(LOG_FILE, 'r', encoding='utf-8') as f: logs = json.load(f)
            for name in sorted(logs.keys()): self.project_history_combo.addItem(name)
        except Exception as e: print(f"프로젝트 기록 로드 오류: {e}")

    def load_selected_project_data(self):
        project_name = self.project_history_combo.currentText()
        if project_name == "-- 기록에서 프로젝트 선택 --": return
        try:
            with open(LOG_FILE, 'r', encoding='utf-8') as f: logs = json.load(f)
            data_to_load = logs.get(project_name, {})
            for label, value in data_to_load.items():
                if label in self.inputs:
                    widget = self.inputs[label]
                    if isinstance(widget, QComboBox):
                        index = widget.findText(str(value))
                        if index != -1: widget.setCurrentIndex(index)
                        else: widget.setCurrentText(str(value))
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

    def center_window(self): qr = self.frameGeometry(); cp = QDesktopWidget().availableGeometry().center(); qr.moveCenter(cp); self.move(qr.topLeft())