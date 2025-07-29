# main.py

import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout, QFrame, QMessageBox, QDesktopWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# --- 모듈 임포트 ---
try:
    from risk_predictor import RiskPredictorWindow
    RISK_PREDICTOR_AVAILABLE = True
except ImportError:
    RISK_PREDICTOR_AVAILABLE = False
    print("⚠️ 경고: risk_predictor.py 파일을 찾을 수 없습니다.")

try:
    from vacancy_predictor import VacancyPredictorWindow, initialize_models_and_data
    VACANCY_PREDICTOR_AVAILABLE = True
except ImportError:
    VACANCY_PREDICTOR_AVAILABLE = False
    print("⚠️ 경고: vacancy_predictor.py 파일을 찾을 수 없습니다.")

# --- 임시 창 클래스 (모듈이 없을 경우 대체) ---
class TempWindow(QWidget):
    """실제 모듈 파일이 없을 때 표시될 임시 창의 기반 클래스"""
    def __init__(self, title_text, file_name, color):
        super().__init__()
        self.setWindowTitle(title_text + " (임시)")
        self.setFixedSize(500, 300)
        self.setStyleSheet("background-color: #f5f7fa; font-family: 'Malgun Gothic';")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20); layout.setSpacing(15); layout.setAlignment(Qt.AlignCenter)

        title = QLabel(title_text)
        title.setFont(QFont("Malgun Gothic", 18, QFont.Bold)); title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"color: {color}; margin-bottom: 20px;")

        message = QLabel(f"{file_name} 파일을 찾을 수 없습니다.\n프로그램 폴더에 해당 파일이 있는지 확인해주세요.")
        message.setFont(QFont("Malgun Gothic", 12)); message.setAlignment(Qt.AlignCenter)
        message.setStyleSheet("color: #555; line-height: 1.6;")

        close_btn = QPushButton("확인"); close_btn.setFixedSize(120, 40)
        close_btn.setFont(QFont("Malgun Gothic", 10, QFont.Bold))
        close_btn.setStyleSheet(f"QPushButton {{ background-color: {color}; color: white; border: none; border-radius: 20px; }} QPushButton:hover {{ background-color: {color}; filter: brightness(120%); }}")
        close_btn.clicked.connect(self.close)

        layout.addWidget(title); layout.addWidget(message); layout.addStretch(1)
        layout.addWidget(close_btn, 0, Qt.AlignCenter)
        self.center_window()

    def center_window(self):
        qr = self.frameGeometry(); cp = QDesktopWidget().availableGeometry().center(); qr.moveCenter(cp); self.move(qr.topLeft())

class TempRiskPredictorWindow(TempWindow):
    def __init__(self): super().__init__("🏢 기업 부도 예측", "risk_predictor.py", "#e74c3c")
class TempVacancyPredictorWindow(TempWindow):
    def __init__(self): super().__init__("🏠 부동산 분양률 예측", "vacancy_predictor.py", "#3498db")


# --- 메인 윈도우 클래스 ---
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("부동산 PF 예측 시스템"); self.setFixedSize(800, 500)
        self.font_name = "Apple SD Gothic Neo" if sys.platform == "darwin" else "Malgun Gothic"
        # 윈도우 전체에 기본 폰트 적용
        self.setFont(QFont(self.font_name))
        self.setStyleSheet(f"QWidget {{ background-color: #f5f7fa; }}")
        
        self.risk_window = None; self.vacancy_window = None
        self.init_ui(); self.center_window()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(30); main_layout.setContentsMargins(50, 40, 50, 50)

        # --- 타이틀 섹션 ---
        title_frame = QFrame()
        title_frame.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #667eea, stop:1 #764ba2); border-radius: 15px; padding: 20px;")
        title_layout = QVBoxLayout(title_frame); title_layout.setAlignment(Qt.AlignCenter)

        main_title = QLabel("🏢 부동산 PF 예측 시스템")
        # 스타일시트에 폰트 정보 통합 (깨짐 방지)
        main_title.setStyleSheet(f"""
            font-family: '{self.font_name}';
            font-size: 24px;
            font-weight: bold;
            color: white;
            background: transparent;
        """)
        main_title.setAlignment(Qt.AlignCenter)
        
        sub_title = QLabel("AI 모델을 활용한 기업 리스크 및 부동산 분양률 예측")
        sub_title.setStyleSheet(f"""
            font-family: '{self.font_name}';
            font-size: 12px;
            color: rgba(255, 255, 255, 0.9);
            background: transparent;
        """)
        sub_title.setAlignment(Qt.AlignCenter)
        
        title_layout.addWidget(main_title); title_layout.addWidget(sub_title)

        # --- 버튼 섹션 ---
        button_layout = QHBoxLayout(); button_layout.setSpacing(40); button_layout.setAlignment(Qt.AlignCenter)
        risk_btn = self.create_main_button("🏢 기업 부도 예측", "기업의 재무 데이터를 분석하여\n부도 위험도를 예측합니다.", "#e74c3c", "#c0392b", self.open_risk_predictor)
        vacancy_btn = self.create_main_button("🏠 부동산 분양률 예측", "프로젝트의 주요 정보를 기반으로\n초기 분양률을 예측합니다.", "#3498db", "#2980b9", self.open_vacancy_predictor)
        button_layout.addWidget(risk_btn); button_layout.addWidget(vacancy_btn)

        info_label = QLabel("💡 각 버튼을 클릭하여 원하는 예측 모드를 선택하세요.")
        info_label.setFont(QFont(self.font_name, 10)); info_label.setStyleSheet("color: #7f8c8d; margin-top: 15px;"); info_label.setAlignment(Qt.AlignCenter)
        
        main_layout.addWidget(title_frame); main_layout.addLayout(button_layout); main_layout.addWidget(info_label); main_layout.addStretch()

    def create_main_button(self, title, description, bg_color, hover_color, on_click):
        """
        QPushButton 안에 QLabel들을 배치하여 Rich Text를 안정적으로 표시하는 함수
        """
        btn = QPushButton()
        btn.setFixedSize(280, 200)
        btn.clicked.connect(on_click)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                border: none;
                border-radius: 15px;
                padding: 20px;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """)

        # 버튼 내부에 레이아웃과 라벨 추가
        layout = QVBoxLayout(btn)
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(10)
        
        title_label = QLabel(title)
        title_label.setWordWrap(True)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont(self.font_name, 18, QFont.Bold))
        
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setFont(QFont(self.font_name, 12))

        # 라벨의 스타일은 투명 배경과 흰 글씨로 설정
        for label in [title_label, desc_label]:
            label.setStyleSheet("background-color: transparent; color: white;")
        
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addStretch()
        
        return btn

    def center_window(self):
        qr = self.frameGeometry(); cp = QDesktopWidget().availableGeometry().center(); qr.moveCenter(cp); self.move(qr.topLeft())

    def open_risk_predictor(self):
        try:
            if RISK_PREDICTOR_AVAILABLE:
                if self.risk_window is None or not self.risk_window.isVisible(): self.risk_window = RiskPredictorWindow()
                self.risk_window.show(); self.risk_window.activateWindow()
            else: self.temp_risk_window = TempRiskPredictorWindow(); self.temp_risk_window.show()
        except Exception as e: QMessageBox.critical(self, "오류", f"기업 부도 예측 창을 여는 중 오류가 발생했습니다: {e}")

    def open_vacancy_predictor(self):
        try:
            if VACANCY_PREDICTOR_AVAILABLE:
                if self.vacancy_window is None or not self.vacancy_window.isVisible(): self.vacancy_window = VacancyPredictorWindow()
                self.vacancy_window.show(); self.vacancy_window.activateWindow()
            else: self.temp_vacancy_window = TempVacancyPredictorWindow(); self.temp_vacancy_window.show()
        except Exception as e: QMessageBox.critical(self, "오류", f"부동산 분양률 예측 창을 여는 중 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    app = QApplication.instance() or QApplication(sys.argv)
    if VACANCY_PREDICTOR_AVAILABLE:
        if not initialize_models_and_data(): sys.exit(-1)
    main_window = MainWindow(); main_window.show()
    sys.exit(app.exec_())