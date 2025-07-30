# main.py

import sys
import os # os 모듈 추가
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout, QFrame, QMessageBox, QDesktopWidget,
    QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QIcon # QIcon 추가

# --- 아이콘 경로를 위한 BASE_DIR 추가 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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

# --- 메인 윈도우 클래스 ---
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("부동산 PF 예측 시스템")

        # --- 아이콘 설정 코드 추가 ---
        icon_path = os.path.join(BASE_DIR, 'image.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        # --------------------------
        
        self.setMinimumSize(900, 650)  # 윈도우용 크기 증가
        self.font_name = "Apple SD Gothic Neo" if sys.platform == "darwin" else "Malgun Gothic"
        self.setFont(QFont(self.font_name))
        self.setStyleSheet(f"QWidget {{ background-color: #f5f7fa; }}")
        
        self.risk_window = None; self.vacancy_window = None
        self.init_ui()
        self.center_window()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(45)  # 간격 증가
        main_layout.setContentsMargins(55, 45, 55, 55)  # 여백 증가

        title_frame = QFrame()
        title_frame.setMinimumHeight(160)  # 높이 증가
        title_frame.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #667eea, stop:1 #764ba2);
            border-radius: 15px;
        """)
        
        title_layout = QVBoxLayout(title_frame)
        title_layout.setContentsMargins(35, 25, 35, 25)  # 여백 증가
        title_layout.setAlignment(Qt.AlignCenter)

        main_title = QLabel("🏢 부동산 PF 예측 시스템")
        main_title.setStyleSheet(f"font-size: 28px; font-weight: bold; color: white; background: transparent;")  # 폰트 크기 증가
        main_title.setAlignment(Qt.AlignCenter)
        
        sub_title = QLabel("AI 모델을 활용한 기업 리스크 및 부동산 분양률 예측")
        sub_title.setStyleSheet(f"font-size: 14px; color: rgba(255, 255, 255, 0.9); background: transparent; padding-top: 8px;")  # 폰트 크기 및 패딩 증가
        sub_title.setAlignment(Qt.AlignCenter)
        
        title_layout.addWidget(main_title)
        title_layout.addWidget(sub_title)
        self.add_shadow(title_frame)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(45)  # 버튼 간격 증가
        button_layout.setAlignment(Qt.AlignCenter)
        
        risk_btn = self.create_main_button("🏢 기업 부도 예측", "기업의 재무 데이터를 분석하여\n부도 위험도를 예측합니다.", "#e74c3c", "#c0392b", self.open_risk_predictor)
        vacancy_btn = self.create_main_button("🏠 부동산 분양률 예측", "프로젝트의 주요 정보를 기반으로\n초기 분양률을 예측합니다.", "#3498db", "#2980b9", self.open_vacancy_predictor)
        
        button_layout.addWidget(risk_btn)
        button_layout.addWidget(vacancy_btn)

        info_label = QLabel("💡 각 버튼을 클릭하여 원하는 예측 모드를 선택하세요.")
        info_label.setFont(QFont(self.font_name, 11))  # 폰트 크기 증가
        info_label.setStyleSheet("color: #7f8c8d;")
        info_label.setAlignment(Qt.AlignCenter)
        
        main_layout.addWidget(title_frame)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(info_label, 0, Qt.AlignCenter)
        main_layout.addStretch()

    def create_main_button(self, title, description, bg_color, hover_color, on_click):
        btn = QPushButton()
        btn.setFixedSize(320, 220)  # 버튼 크기 증가
        btn.clicked.connect(on_click)
        btn.setStyleSheet(f"""
            QPushButton {{ background-color: {bg_color}; border: none; border-radius: 15px; }}
            QPushButton:hover {{ background-color: {hover_color}; }}
        """)
        layout = QVBoxLayout(btn)
        layout.setContentsMargins(25, 15, 25, 15)  # 여백 증가
        
        title_label = QLabel(title)
        title_label.setWordWrap(True); title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"font-size: 20px; font-weight: bold; color: white; background: transparent; padding-bottom: 8px;")  # 폰트 크기 및 패딩 증가
        
        desc_label = QLabel(description)
        desc_label.setWordWrap(True); desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet(f"font-size: 14px; color: rgba(255, 255, 255, 0.9); background: transparent; line-height: 1.6;")  # 폰트 크기 증가

        layout.addStretch(1); layout.addWidget(title_label); layout.addWidget(desc_label); layout.addStretch(1)
        self.add_shadow(btn)
        return btn

    def add_shadow(self, widget):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25); shadow.setXOffset(0); shadow.setYOffset(5); shadow.setColor(QColor(0, 0, 0, 60))
        widget.setGraphicsEffect(shadow)

    def center_window(self):
        qr = self.frameGeometry(); cp = QDesktopWidget().availableGeometry().center(); qr.moveCenter(cp); self.move(qr.topLeft())

    def open_risk_predictor(self):
        try:
            if RISK_PREDICTOR_AVAILABLE:
                if self.risk_window is None or not self.risk_window.isVisible(): self.risk_window = RiskPredictorWindow()
                self.risk_window.show(); self.risk_window.activateWindow()
            else: QMessageBox.warning(self, "파일 없음", "risk_predictor.py 파일을 찾을 수 없습니다.")
        except Exception as e: QMessageBox.critical(self, "오류", f"기업 부도 예측 창을 여는 중 오류가 발생했습니다: {e}")

    def open_vacancy_predictor(self):
        try:
            if VACANCY_PREDICTOR_AVAILABLE:
                if self.vacancy_window is None or not self.vacancy_window.isVisible(): self.vacancy_window = VacancyPredictorWindow()
                self.vacancy_window.show(); self.vacancy_window.activateWindow()
            else: QMessageBox.warning(self, "파일 없음", "vacancy_predictor.py 파일을 찾을 수 없습니다.")
        except Exception as e: QMessageBox.critical(self, "오류", f"부동산 분양률 예측 창을 여는 중 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    app = QApplication.instance() or QApplication(sys.argv)
    if VACANCY_PREDICTOR_AVAILABLE:
        if not initialize_models_and_data(): sys.exit(-1)
    main_window = MainWindow(); main_window.show()
    sys.exit(app.exec_())