from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QHBoxLayout
import sys
from risk_predictor import RiskPredictorWindow
from vacancy_predictor import VacancyPredictorWindow

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("부동산 PF 예측 시스템")
        self.setFixedSize(600, 300)

        label = QLabel("예측 모드를 선택하세요", self)
        label.setStyleSheet("font-size: 20px; margin-bottom: 30px;")

        risk_btn = QPushButton("기업 리스크 예측", self)
        vacancy_btn = QPushButton("부동산 전망 예측", self)

        risk_btn.setFixedSize(200, 100)
        vacancy_btn.setFixedSize(200, 100)

        risk_btn.clicked.connect(self.open_risk_predictor)
        vacancy_btn.clicked.connect(self.open_vacancy_predictor)

        layout = QHBoxLayout()
        layout.addWidget(risk_btn)
        layout.addWidget(vacancy_btn)

        wrapper = QHBoxLayout()
        wrapper.addLayout(layout)
        self.setLayout(wrapper)

    def open_risk_predictor(self):
        self.risk_window = RiskPredictorWindow()
        self.risk_window.show()

    def open_vacancy_predictor(self):
        self.vacancy_window = VacancyPredictorWindow()
        self.vacancy_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())
