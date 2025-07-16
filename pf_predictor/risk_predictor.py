import sys
import pickle
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QLineEdit, QPushButton,
    QTextEdit, QFormLayout, QMessageBox, QScrollArea, QFrame
)
from PyQt5.QtGui import QDoubleValidator
import os


class RiskPredictorWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("기업 리스크 예측")
        self.setFixedSize(700, 800)

        # 📌 CSV 기반 피처 순서
        self.features = [
            '연체기관수_3년', '연체기관수_1년', '연체기관수_6개월', '연체기관수_3개월',
            '연체과목수_3개월발생', '연체과목수_3개월유지', '연체기관수_전체',
            '최장연체일수_3개월', '최장연체일수_6개월', '최장연체일수_1년', '최장연체일수_3년',
            '연체경험', '유동자산', '비유동자산', '자산총계', '유동부채', '비유동부채',
            '부채총계', '매출액', '매출총이익', '영업손익', '당기순이익', '영업활동현금흐름',
            '재무비율_부채비율', '재무비율_유동비율', '재무비율_자기자본비율',
            '재무비율_영업이익율', '재무비율_자기자본이익률(ROE)', 'EBITDA마진율',
            '영업이익증가율', '당기순이익증가율', 'EBITDA증가율', '설립일자', '사업장소유여부',
            '소유건축물건수', '소유건축물권리침해여부', '기업신용평가등급(구간화)', '공공정보_유지여부'
        ]

        # 📌 모델 로딩
        model_path = os.path.join(os.path.dirname(__file__), "final_risk_model.pkl")
        with open(model_path, "rb") as f:
            self.model = pickle.load(f)

        # 📌 스크롤 가능한 입력 폼 생성
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        scroll_content = QFrame()
        self.form_layout = QFormLayout(scroll_content)
        self.inputs = {}

        for feature in self.features:
            line_edit = QLineEdit()
            line_edit.setValidator(QDoubleValidator())
            self.inputs[feature] = line_edit
            self.form_layout.addRow(QLabel(feature), line_edit)

        self.scroll_area.setWidget(scroll_content)

        # 📌 결과 및 버튼
        self.predict_btn = QPushButton("리스크 예측 실행")
        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        self.predict_btn.clicked.connect(self.predict_risk)

        # 📌 전체 레이아웃
        layout = QVBoxLayout()
        layout.addWidget(self.scroll_area)
        layout.addWidget(self.predict_btn)
        layout.addWidget(QLabel("예측 결과:"))
        layout.addWidget(self.result_box)
        self.setLayout(layout)

    def predict_risk(self):
        try:
            input_values = []
            for feature in self.features:
                text = self.inputs[feature].text()
                if text == '':
                    QMessageBox.warning(self, "입력 오류", f"'{feature}' 값을 입력해주세요.")
                    return
                input_values.append(float(text))

            input_df = pd.DataFrame([input_values], columns=self.features)
            prediction = self.model.predict(input_df)[0]
            proba = self.model.predict_proba(input_df)[0]

            label = "부도 위험 있음" if prediction == 1 else "정상"
            confidence = round(proba[prediction] * 100, 2)
            self.result_box.setText(f"📌 예측 결과: {label}\n📈 신뢰도: {confidence}%")

        except Exception as e:
            QMessageBox.critical(self, "예측 오류", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RiskPredictorWindow()
    window.show()
    sys.exit(app.exec_())
