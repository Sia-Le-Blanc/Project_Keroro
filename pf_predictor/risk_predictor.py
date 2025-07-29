# risk_predictor.py

import sys, os, json
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QDoubleValidator

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class RiskPredictorWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🏢 기업 부도 예측"); self.setMinimumSize(900, 700); self.resize(1000, 800)
        self.font_name = "Apple SD Gothic Neo" if sys.platform == "darwin" else "Malgun Gothic"
        self.setFont(QFont(self.font_name))
        # UI 스타일 통합 관리
        self.setStyleSheet(f"""
            QWidget {{ background-color: #f5f7fa; font-family: '{self.font_name}'; color: #2c3e50; }}
            QGroupBox {{ font-weight: bold; border: 1px solid #d1d9e0; border-radius: 10px; margin-top: 12px; padding: 25px 15px 15px 15px; background-color: #f8f9fb; }}
            QGroupBox::title {{ subcontrol-origin: margin; left: 15px; padding: 0 8px; }}
            QLineEdit, QComboBox {{ border: 1px solid #d1d9e0; border-radius: 6px; padding: 0 12px; background-color: white; min-height: 38px; }}
            QLineEdit:focus, QComboBox:focus {{ border: 2px solid #667eea; }}
            QPushButton {{ border: none; border-radius: 8px; font-weight: bold; padding: 10px; }}
        """)
        self.log_file = os.path.join(BASE_DIR, "prediction_log.json")
        self.feature_groups = {
            "연체 관련 정보": ['연체과목수_3개월유지', '연체기관수_전체', '최장연체일수_3개월', '최장연체일수_6개월', '최장연체일수_1년', '최장연체일수_3년', '연체경험'],
            "재무제표 정보 (단위: 백만원)": ['유동자산', '비유동자산', '자산총계', '유동부채', '비유동부채', '부채총계', '매출액', '매출총이익', '영업손익', '당기순이익', '영업활동현금흐름'],
            "재무비율 정보 (단위: %)": ['재무비율_부채비율', '재무비율_유동비율']
        }
        self.features = [f for group in self.feature_groups.values() for f in group]
        self.inputs = {}; self.company_name_input = None; self.company_history_combo = None
        self.result_window = None; self.help_dialog = None
        self.init_ui(); self.center_window(); self.load_company_history()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25); main_layout.setSpacing(15)
        main_layout.addWidget(self.create_header())
        main_layout.addWidget(self.create_company_section())
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True); scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        scroll_content = QWidget(); scroll_content.setStyleSheet("background-color: white; border-radius: 12px; border: 1px solid #e1e8ed;")
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(20, 20, 20, 20); content_layout.setSpacing(20)
        for group_name, features in self.feature_groups.items(): content_layout.addWidget(self.create_feature_group(group_name, features))
        scroll_area.setWidget(scroll_content); main_layout.addWidget(scroll_area, 1)
        main_layout.addLayout(self.create_bottom_buttons())

    def create_header(self):
        header = QFrame(); header.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #e74c3c, stop:1 #c0392b); border-radius: 8px; padding: 20px;")
        layout = QVBoxLayout(header); layout.setAlignment(Qt.AlignCenter)
        title = QLabel("🏢 기업 부도 위험 예측"); title.setFont(QFont(self.font_name, 18, QFont.Bold))
        subtitle = QLabel("기업의 재무 데이터를 입력하여 부도 위험도를 분석합니다"); subtitle.setFont(QFont(self.font_name, 11))
        for label in [title, subtitle]:
            label.setStyleSheet("color: #ffffff; background: transparent;"); label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title); layout.addWidget(subtitle)
        return header

    def create_company_section(self):
        section = QFrame(); section.setStyleSheet("background-color: white; border-radius: 12px; border: 1px solid #e1e8ed; padding: 20px;")
        layout = QGridLayout(section); layout.setSpacing(15)
        company_label = QLabel("🏢 분석 대상 회사명:"); self.company_name_input = QLineEdit(); self.company_name_input.setPlaceholderText("회사명을 입력하세요")
        history_label = QLabel("📋 이전 기록 선택:"); self.company_history_combo = QComboBox()
        load_btn = QPushButton("📂 불러오기"); load_btn.clicked.connect(self.load_selected_company_data)
        load_btn.setStyleSheet("background-color: #f39c12; color: white;")
        for widget in [company_label, history_label]: widget.setFont(QFont(self.font_name, 11, QFont.Bold))
        layout.addWidget(company_label, 0, 0); layout.addWidget(self.company_name_input, 0, 1, 1, 2)
        layout.addWidget(history_label, 1, 0); layout.addWidget(self.company_history_combo, 1, 1); layout.addWidget(load_btn, 1, 2)
        return section

    def create_feature_group(self, group_name, features):
        group_box = QGroupBox(group_name); group_box.setFont(QFont(self.font_name, 12, QFont.Bold))
        grid = QGridLayout(group_box); grid.setSpacing(12)
        for i, feature in enumerate(features):
            label = QLabel(self.get_feature_display_name(feature)); line_edit = QLineEdit("0")
            line_edit.setValidator(QDoubleValidator()); self.inputs[feature] = line_edit
            row, col = i // 2, (i % 2) * 2
            grid.addWidget(label, row, col); grid.addWidget(line_edit, row, col + 1)
        return group_box

    def create_bottom_buttons(self):
        layout = QHBoxLayout(); layout.setSpacing(10)
        help_btn = QPushButton("❓ 도움말"); help_btn.clicked.connect(self.open_help_dialog)
        help_btn.setStyleSheet("background-color: #27ae60; color: white;")
        reset_btn = QPushButton("🔄 초기화"); reset_btn.clicked.connect(self.clear_all_inputs)
        reset_btn.setStyleSheet("background-color: #95a5a6; color: white;")
        submit_btn = QPushButton("🔍 예측 실행"); submit_btn.clicked.connect(self.predict_bankruptcy)
        submit_btn.setStyleSheet("background-color: #e74c3c; color: white;")
        layout.addWidget(help_btn); layout.addStretch(); layout.addWidget(reset_btn); layout.addWidget(submit_btn)
        for btn in [help_btn, reset_btn, submit_btn]: btn.setMinimumHeight(45)
        return layout

    def predict_bankruptcy(self):
        company_name = self.company_name_input.text().strip()
        if not company_name: self.show_message_box("입력 오류", "회사명을 입력해주세요.", QMessageBox.Warning); return
        input_dict = {}
        try:
            for feature, widget in self.inputs.items():
                text = widget.text().strip()
                if not text: raise ValueError(f"'{self.get_feature_display_name(feature)}' 값을 입력해주세요.")
                input_dict[feature] = float(text)
        except ValueError as e: self.show_message_box("입력 오류", str(e), QMessageBox.Warning); return
        prediction_result = self.mock_prediction(input_dict); self.save_prediction_log(company_name, input_dict, prediction_result)
        try:
            from prediction_result import PredictionResultWindow
            if self.result_window is None or not self.result_window.isVisible(): self.result_window = PredictionResultWindow(prediction_result, input_dict, company_name)
            else: self.result_window.update_data(prediction_result, input_dict, company_name)
            self.result_window.show(); self.result_window.activateWindow()
        except ImportError as e:
            prob_text = f"{prediction_result['probability']:.1%}"
            self.show_message_box("예측 완료", f"'{company_name}'의 부도 확률: {prob_text}\n(결과 창 모듈을 여는 데 실패했습니다: {e})", QMessageBox.Warning)

    def open_help_dialog(self):
        try:
            from help_dialog import HelpDialog
            if self.help_dialog is None or not self.help_dialog.isVisible(): self.help_dialog = HelpDialog(self)
            self.help_dialog.show(); self.help_dialog.activateWindow()
        except ImportError as e: self.show_message_box("오류", f"도움말 창을 여는 데 실패했습니다: {e}", QMessageBox.Critical)

    def get_feature_display_name(self, feature):
        names = {'연체과목수_3개월유지':'연체 과목수(3개월)','연체기관수_전체':'연체 기관수(전체)','최장연체일수_3개월':'최장 연체일수(3개월)','최장연체일수_6개월':'최장 연체일수(6개월)','최장연체일수_1년':'최장 연체일수(1년)','최장연체일수_3년':'최장 연체일수(3년)','연체경험':'연체 경험(0/1)','유동자산':'유동자산','비유동자산':'비유동자산','자산총계':'자산총계','유동부채':'유동부채','비유동부채':'비유동부채','부채총계':'부채총계','매출액':'매출액','매출총이익':'매출총이익','영업손익':'영업손익','당기순이익':'당기순이익','영업활동현금흐름':'영업활동 현금흐름','재무비율_부채비율':'부채비율','재무비율_유동비율':'유동비율'}
        return names.get(feature, feature)
    
    def mock_prediction(self, input_dict):
        debt_ratio = input_dict.get('재무비율_부채비율', 0); overdue_days = input_dict.get('최장연체일수_1년', 0)
        probability = min(max((debt_ratio / 300.0) + (overdue_days / 100.0), 0.05), 0.95)
        if probability > 0.7: risk_level = "매우 높음"
        elif probability > 0.5: risk_level = "높음"
        elif probability > 0.3: risk_level = "보통"
        else: risk_level = "낮음"
        return {"probability": probability, "risk_level": risk_level}

    def save_prediction_log(self, company_name, input_data, prediction_result):
        logs = {}; 
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f: logs = json.load(f)
            except json.JSONDecodeError: pass
        new_log_entry = {'timestamp': datetime.now().isoformat(),'input_data': input_data,'prediction_result': prediction_result}
        if company_name not in logs: logs[company_name] = []
        logs[company_name].append(new_log_entry); logs[company_name] = logs[company_name][-10:]
        with open(self.log_file, 'w', encoding='utf-8') as f: json.dump(logs, f, ensure_ascii=False, indent=4)
        self.load_company_history()

    def load_company_history(self):
        current_selection = self.company_history_combo.currentText(); self.company_history_combo.clear(); self.company_history_combo.addItem("-- 기록에서 회사 선택 --")
        if not os.path.exists(self.log_file): return
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f: logs = json.load(f)
            for company in sorted(logs.keys()): self.company_history_combo.addItem(company)
            index = self.company_history_combo.findText(current_selection)
            if index != -1: self.company_history_combo.setCurrentIndex(index)
        except Exception as e: print(f"회사 기록 로드 오류: {e}")

    def load_selected_company_data(self):
        company_name = self.company_history_combo.currentText()
        if company_name == "-- 기록에서 회사 선택 --": self.show_message_box("알림", "불러올 회사를 선택해주세요.", QMessageBox.Information); return
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f: logs = json.load(f)
            latest_record = logs[company_name][-1]; input_data = latest_record['input_data']
            self.company_name_input.setText(company_name)
            for feature, value in input_data.items():
                if feature in self.inputs: self.inputs[feature].setText(str(value))
            self.show_message_box("완료", f"'{company_name}'의 최근 데이터를 불러왔습니다.", QMessageBox.Information)
        except Exception as e: self.show_message_box("오류", f"데이터 로드 중 오류 발생:\n{e}", QMessageBox.Critical)

    def clear_all_inputs(self):
        if QMessageBox.question(self, '초기화 확인', '모든 입력값을 초기화하시겠습니까?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            self.company_name_input.clear(); self.company_history_combo.setCurrentIndex(0)
            for line_edit in self.inputs.values(): line_edit.setText("0")

    def center_window(self): qr = self.frameGeometry(); cp = QDesktopWidget().availableGeometry().center(); qr.moveCenter(cp); self.move(qr.topLeft())
    def show_message_box(self, title, message, icon):
        msg_box = QMessageBox(self); msg_box.setWindowTitle(title); msg_box.setText(message); msg_box.setIcon(icon)
        msg_box.setFont(QFont(self.font_name, 10)); msg_box.setStyleSheet("QLabel{min-width: 300px;}"); msg_box.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv); window = RiskPredictorWindow(); window.show(); sys.exit(app.exec_())