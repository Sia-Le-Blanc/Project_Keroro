import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, 
    QVBoxLayout, QHBoxLayout, QFrame, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

# Import 오류 처리
try:
    from risk_predictor import RiskPredictorWindow
    RISK_PREDICTOR_AVAILABLE = True
except ImportError:
    RISK_PREDICTOR_AVAILABLE = False
    print("⚠️ risk_predictor_new.py 파일이 없습니다. 임시 창을 표시합니다.")

try:
    from vacancy_predictor import VacancyPredictorWindow  
    VACANCY_PREDICTOR_AVAILABLE = True
except ImportError:
    VACANCY_PREDICTOR_AVAILABLE = False
    print("⚠️ vacancy_predictor.py 파일이 없습니다. 임시 창을 표시합니다.")


# 임시 클래스들 (실제 파일이 없을 때 사용)
class TempRiskPredictorWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🏢 기업 부도 예측 (임시)")
        self.setFixedSize(500, 300)
        self.setStyleSheet("background-color: #f5f7fa; font-family: 'Malgun Gothic';")
        
        layout = QVBoxLayout()
        
        title = QLabel("🏢 기업 부도 예측")
        title.setFont(QFont("Malgun Gothic", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #e74c3c; margin: 20px;")
        
        message = QLabel("risk_predictor_new.py 파일을 생성해주세요!\n\n"
                        "Artifact에서 생성한 risk_predictor_new.py 코드를\n"
                        "별도 파일로 저장하면 정상 작동합니다.")
        message.setFont(QFont("Malgun Gothic", 12))
        message.setAlignment(Qt.AlignCenter)
        message.setStyleSheet("color: #666; line-height: 1.6;")
        
        close_btn = QPushButton("확인")
        close_btn.setFixedSize(100, 40)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        close_btn.clicked.connect(self.close)
        
        layout.addWidget(title)
        layout.addWidget(message)
        layout.addWidget(close_btn, alignment=Qt.AlignCenter)
        layout.addStretch()
        
        self.setLayout(layout)
        self.center_window()
    
    def center_window(self):
        screen = QApplication.desktop().screenGeometry()
        window = self.geometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        self.move(x, y)


class TempVacancyPredictorWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🏠 부동산 분양률 예측 (임시)")
        self.setFixedSize(500, 300)
        self.setStyleSheet("background-color: #f5f7fa; font-family: 'Malgun Gothic';")
        
        layout = QVBoxLayout()
        
        title = QLabel("🏠 부동산 분양률 예측")
        title.setFont(QFont("Malgun Gothic", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #3498db; margin: 20px;")
        
        message = QLabel("vacancy_predictor.py 파일을 생성해주세요!\n\n"
                        "아직 구현되지 않은 기능입니다.\n"
                        "곧 추가될 예정입니다.")
        message.setFont(QFont("Malgun Gothic", 12))
        message.setAlignment(Qt.AlignCenter)
        message.setStyleSheet("color: #666; line-height: 1.6;")
        
        close_btn = QPushButton("확인")
        close_btn.setFixedSize(100, 40)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        close_btn.clicked.connect(self.close)
        
        layout.addWidget(title)
        layout.addWidget(message)
        layout.addWidget(close_btn, alignment=Qt.AlignCenter)
        layout.addStretch()
        
        self.setLayout(layout)
        self.center_window()
    
    def center_window(self):
        screen = QApplication.desktop().screenGeometry()
        window = self.geometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        self.move(x, y)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("부동산 PF 예측 시스템")
        self.setFixedSize(800, 500)
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f7fa;
                font-family: 'Malgun Gothic', Arial, sans-serif;
            }
        """)
        
        self.init_ui()
        
        # 창을 화면 중앙에 배치
        self.center_window()
    
    def init_ui(self):
        # 메인 레이아웃
        main_layout = QVBoxLayout()
        main_layout.setSpacing(30)
        main_layout.setContentsMargins(50, 50, 50, 50)
        
        # 제목 영역
        title_frame = QFrame()
        title_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 15px;
                padding: 20px;
            }
        """)
        
        title_layout = QVBoxLayout()
        title_layout.setAlignment(Qt.AlignCenter)
        
        # 메인 타이틀
        main_title = QLabel("🏢 부동산 PF 예측 시스템")
        main_title.setFont(QFont("Malgun Gothic", 24, QFont.Bold))
        main_title.setStyleSheet("color: white; margin: 10px 0;")
        main_title.setAlignment(Qt.AlignCenter)
        
        # 서브 타이틀
        sub_title = QLabel("기업 리스크와 분양률을 AI로 예측합니다")
        sub_title.setFont(QFont("Malgun Gothic", 12))
        sub_title.setStyleSheet("color: rgba(255, 255, 255, 0.9);")
        sub_title.setAlignment(Qt.AlignCenter)
        
        title_layout.addWidget(main_title)
        title_layout.addWidget(sub_title)
        title_frame.setLayout(title_layout)
        
        # 버튼 영역
        button_layout = QHBoxLayout()
        button_layout.setSpacing(40)
        button_layout.setAlignment(Qt.AlignCenter)
        
        # 기업 부도 예측 버튼
        risk_btn = QPushButton()
        risk_btn.setText("🏢\n기업 부도 예측\n\n기업의 재무 데이터를 분석하여\n부도 위험도를 예측합니다")
        risk_btn.setFixedSize(280, 200)
        risk_btn.setFont(QFont("Malgun Gothic", 12, QFont.Bold))
        risk_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 20px;
                text-align: center;
                line-height: 1.5;
            }
            QPushButton:hover {
                background-color: #c0392b;
                transform: scale(1.05);
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        risk_btn.clicked.connect(self.open_risk_predictor)
        
        # 부동산 분양률 예측 버튼
        vacancy_btn = QPushButton()
        vacancy_btn.setText("🏠\n부동산 분양률 예측\n\n부동산 프로젝트의\n분양률을 예측합니다")
        vacancy_btn.setFixedSize(280, 200)
        vacancy_btn.setFont(QFont("Malgun Gothic", 12, QFont.Bold))
        vacancy_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 20px;
                text-align: center;
                line-height: 1.5;
            }
            QPushButton:hover {
                background-color: #2980b9;
                transform: scale(1.05);
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        vacancy_btn.clicked.connect(self.open_vacancy_predictor)
        
        button_layout.addWidget(risk_btn)
        button_layout.addWidget(vacancy_btn)
        
        # 하단 정보
        info_label = QLabel("💡 각 버튼을 클릭하여 원하는 예측 모드를 선택하세요")
        info_label.setFont(QFont("Malgun Gothic", 10))
        info_label.setStyleSheet("color: #7f8c8d; margin-top: 20px;")
        info_label.setAlignment(Qt.AlignCenter)
        
        # 레이아웃 구성
        main_layout.addWidget(title_frame)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(info_label)
        main_layout.addStretch()
        
        self.setLayout(main_layout)
    
    def center_window(self):
        """창을 화면 중앙에 배치"""
        screen = QApplication.desktop().screenGeometry()
        window = self.geometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        self.move(x, y)
    
    def open_risk_predictor(self):
        """기업 부도 예측 창 열기"""
        try:
            if RISK_PREDICTOR_AVAILABLE:
                self.risk_window = RiskPredictorWindow()
                self.risk_window.show()
                print("✅ 기업 부도 예측 창이 열렸습니다.")
            else:
                # 임시 창 표시
                self.temp_risk_window = TempRiskPredictorWindow()
                self.temp_risk_window.show()
                print("⚠️ 임시 창을 표시합니다. risk_predictor_new.py 파일을 생성해주세요.")
                
        except Exception as e:
            error_msg = f"기업 부도 예측 창 열기 오류: {e}"
            print(error_msg)
            QMessageBox.critical(self, "오류", error_msg)
    
    def open_vacancy_predictor(self):
        """부동산 분양률 예측 창 열기"""
        try:
            if VACANCY_PREDICTOR_AVAILABLE:
                self.vacancy_window = VacancyPredictorWindow()
                self.vacancy_window.show()
                print("✅ 부동산 분양률 예측 창이 열렸습니다.")
            else:
                # 임시 창 표시
                self.temp_vacancy_window = TempVacancyPredictorWindow()
                self.temp_vacancy_window.show()
                print("⚠️ 임시 창을 표시합니다. vacancy_predictor.py 파일을 생성해주세요.")
                
        except Exception as e:
            error_msg = f"부동산 분양률 예측 창 열기 오류: {e}"
            print(error_msg)
            QMessageBox.critical(self, "오류", error_msg)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 애플리케이션 설정
    app.setApplicationName("부동산 PF 예측 시스템")
    app.setApplicationVersion("1.0")
    
    # 메인 창 생성 및 표시
    main_window = MainWindow()
    main_window.show()
    
    sys.exit(app.exec_())