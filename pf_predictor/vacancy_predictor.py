from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QLineEdit, QPushButton, QTextEdit

class VacancyPredictorWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("부동산 전망 예측")
        self.setFixedSize(500, 400)

        layout = QVBoxLayout()

        self.input_label = QLabel("부동산 정보를 입력하세요:")
        self.input_text = QLineEdit()
        self.predict_btn = QPushButton("공실률 예측 실행")
        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)

        self.predict_btn.clicked.connect(self.predict_vacancy)

        layout.addWidget(self.input_label)
        layout.addWidget(self.input_text)
        layout.addWidget(self.predict_btn)
        layout.addWidget(QLabel("예측 결과:"))
        layout.addWidget(self.result_box)

        self.setLayout(layout)

    def predict_vacancy(self):
        real_estate_info = self.input_text.text()
        # 여기에 실제 예측 로직을 연결
        self.result_box.setText(f"[모의 출력] 입력된 정보: {real_estate_info}\n예측 공실률: 7.3%")
