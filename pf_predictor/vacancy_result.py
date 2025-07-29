# vacancy_result.py

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import seaborn as sns
import matplotlib.pyplot as plt

class VacancyResultWindow(QWidget):
    def __init__(self, predicted_rate, input_data, project_name="N/A"):
        super().__init__()
        self.font_name = "Apple SD Gothic Neo" if sys.platform == "darwin" else "Malgun Gothic"
        plt.rcParams['font.family'] = [self.font_name]
        plt.rcParams['axes.unicode_minus'] = False
        self.main_layout = QVBoxLayout(self)
        self.setup_ui()
        self.update_data(predicted_rate, input_data, project_name)
        self.center_window()

    def setup_ui(self):
        self.setMinimumSize(800, 600); self.resize(800, 700)
        self.setStyleSheet(f"QWidget {{ background-color: #f5f7fa; font-family: '{self.font_name}'; }}")
        self.main_layout.setContentsMargins(25, 25, 25, 25); self.main_layout.setSpacing(20)

    def update_data(self, predicted_rate, input_data, project_name):
        self.predicted_rate = predicted_rate; self.input_data = input_data; self.project_name = project_name
        self.setWindowTitle(f"🏠 {self.project_name} - 분양률 예측 결과")
        while self.main_layout.count():
            item = self.main_layout.takeAt(0); widget = item.widget()
            if widget: widget.deleteLater()
            else:
                layout = item.layout()
                if layout: self.clear_layout(layout)
        self.main_layout.addWidget(self.create_header()); self.main_layout.addWidget(self.create_result_card())
        bottom_layout = QHBoxLayout(); bottom_layout.setSpacing(15)
        bottom_layout.addWidget(self.create_analysis_card()); bottom_layout.addWidget(self.create_input_summary_card(), 1)
        self.main_layout.addLayout(bottom_layout)
    
    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0); widget = item.widget()
            if widget: widget.deleteLater()
            else: self.clear_layout(item.layout())

    def create_header(self):
        header = QFrame(); header.setMinimumHeight(100)
        header.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #3498db, stop:1 #2980b9); border-radius: 8px; padding: 20px;")
        layout = QVBoxLayout(header); layout.setAlignment(Qt.AlignCenter)
        title = QLabel(f"📈 {self.project_name} - 분양률 예측 결과"); title.setFont(QFont(self.font_name, 18, QFont.Bold))
        subtitle = QLabel("AI 모델 분석을 통한 초기 분양률 예측 리포트"); subtitle.setFont(QFont(self.font_name, 11))
        for label in [title, subtitle]:
            label.setStyleSheet("color: #ffffff; background: transparent;"); label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title); layout.addWidget(subtitle)
        return header

    def create_result_card(self):
        card = QFrame(); card.setStyleSheet("background-color: white; border-radius: 12px; border: 1px solid #e1e8ed; padding: 20px;")
        layout = QHBoxLayout(card); layout.setSpacing(20)
        chart_canvas = self.create_gauge_chart(); chart_canvas.setFixedSize(250, 180)
        layout.addWidget(chart_canvas, 0, Qt.AlignCenter)
        text_layout = QVBoxLayout(); text_layout.setAlignment(Qt.AlignCenter); text_layout.setSpacing(5)
        result_label = QLabel("예상 초기 분양률"); result_label.setFont(QFont(self.font_name, 18)); result_label.setStyleSheet("color: #34495e;")
        rate_label = QLabel(f"{self.predicted_rate:.1f}%"); rate_label.setFont(QFont(self.font_name, 52, QFont.Bold)); rate_label.setStyleSheet("color: #3498db;")
        text_layout.addWidget(result_label); text_layout.addWidget(rate_label)
        layout.addStretch(1); layout.addLayout(text_layout); layout.addStretch(1)
        return card

    def create_gauge_chart(self):
        fig = Figure(figsize=(3, 2), dpi=100, facecolor='white'); ax = fig.add_subplot(111); rate = self.predicted_rate
        if rate < 60: color = "#e74c3c"
        elif rate < 80: color = "#f39c12"
        else: color = "#27ae60"
        sns.set_palette([color, "#EAEAEA"])
        wedges, _ = ax.pie([rate, 100 - rate], startangle=90, counterclock=False, wedgeprops={'width': 0.4, 'edgecolor': 'w'})
        wedges[0].set_edgecolor(color); wedges[0].set_linewidth(1)
        ax.text(0, 0, f"{rate:.0f}%", ha='center', va='center', fontsize=24, fontweight='bold', color="#34495e")
        fig.tight_layout(pad=0); return FigureCanvas(fig)

    def generate_analysis_text(self):
        rate = self.predicted_rate
        if rate >= 95: return "<strong>최우수</strong>: 시장의 폭발적인 관심이 예상되며, <strong>단기 완판 가능성</strong>이 매우 높습니다."
        elif rate >= 80: return "<strong>우수</strong>: 안정적인 분양 성과가 기대됩니다. <strong>사업성이 매우 양호</strong>한 수준입니다."
        elif rate >= 60: return "<strong>보통</strong>: 초기 분양은 무난하게 진행될 것이나, 일부 미분양 가능성이 존재합니다."
        else: return "<strong>주의</strong>: 초기 분양에 어려움이 예상됩니다. <strong>사업성 재검토</strong>가 필요합니다."

    def create_analysis_card(self):
        card = QGroupBox("💡 AI 종합 분석"); card.setFont(QFont(self.font_name, 12, QFont.Bold))
        card.setStyleSheet("QGroupBox { border: 1px solid #e1e8ed; border-radius: 12px; margin-top: 10px; background-color: white; } QGroupBox::title { subcontrol-origin: margin; left: 15px; padding: 5px 10px; }")
        layout = QVBoxLayout(card); icon_label = QLabel(); rate = self.predicted_rate
        if rate >= 80: icon_label.setText("✅")
        elif rate >= 60: icon_label.setText("🤔")
        else: icon_label.setText("⚠️")
        icon_label.setFont(QFont(self.font_name, 24)); icon_label.setAlignment(Qt.AlignCenter)
        analysis_label = QLabel(self.generate_analysis_text()); analysis_label.setWordWrap(True)
        analysis_label.setFont(QFont(self.font_name, 11)); analysis_label.setStyleSheet("line-height: 150%;"); analysis_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label); layout.addWidget(analysis_label); layout.addStretch()
        return card
        
    def create_input_summary_card(self):
        card = QGroupBox("📝 주요 입력 정보"); card.setFont(QFont(self.font_name, 12, QFont.Bold))
        card.setStyleSheet("QGroupBox { border: 1px solid #e1e8ed; border-radius: 12px; margin-top: 10px; background-color: white; } QGroupBox::title { subcontrol-origin: margin; left: 15px; padding: 5px 10px; }")
        grid = QGridLayout(card); grid.setSpacing(10)
        # 브랜드 정보를 요약에 추가
        summary_items = {"브랜드": self.input_data.get('브랜드', 'N/A'), "건설사": self.input_data.get('건설사', 'N/A'), "지역": self.input_data.get('지역', 'N/A'), "총 세대수": f"{self.input_data.get('세대수')} 세대", "기준년월": self.input_data.get('기준년월', 'N/A')}
        row = 0
        for label, value in summary_items.items():
            label_widget = QLabel(f"<strong>{label}</strong>"); label_widget.setFont(QFont(self.font_name, 10))
            value_widget = QLabel(str(value)); value_widget.setFont(QFont(self.font_name, 10)); value_widget.setAlignment(Qt.AlignRight)
            grid.addWidget(label_widget, row, 0); grid.addWidget(value_widget, row, 1); row += 1
        return card

    def center_window(self): qr = self.frameGeometry(); cp = QDesktopWidget().availableGeometry().center(); qr.moveCenter(cp); self.move(qr.topLeft())

if __name__ == '__main__':
    app = QApplication(sys.argv); sample_rate = 85.0
    sample_input = {'아파트': '샘플 아파트', '브랜드': '래미안', '건설사': '삼성물산', '지역': '서울특별시', '세대수': '1500', '기준년월': '202401'}
    window = VacancyResultWindow(sample_rate, sample_input, "샘플 아파트"); window.show(); sys.exit(app.exec_())