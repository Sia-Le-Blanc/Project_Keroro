import sys
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QFrame, QScrollArea, QGridLayout, QPushButton, QGroupBox, QFileDialog, QDesktopWidget
)
from PyQt5.QtCore import Qt, QRect, QPoint
from PyQt5.QtGui import QFont, QPixmap, QPainter
from PyQt5.QtPrintSupport import QPrinter
import matplotlib

# ▼▼▼ 폰트 문제 해결 ▼▼▼
# 시스템에 맞는 폰트 목록을 설정
if sys.platform == "darwin": # macOS
    font_name = "Apple SD Gothic Neo"
else: # Windows 등 다른 OS
    font_name = "Malgun Gothic"
plt.rcParams['font.family'] = [font_name]
plt.rcParams['axes.unicode_minus'] = False
# ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲

class PredictionResultWindow(QWidget):
    def __init__(self, prediction_data, input_data, company_name="N/A"):
        super().__init__()
        self.prediction_data = prediction_data
        self.input_data = input_data
        self.company_name = company_name

        self.setWindowTitle(f"📊 {self.company_name} - 기업 부도 예측 결과")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)

        self.setFont(QFont(font_name))
        self.setStyleSheet(f"""
            QWidget {{
                background-color: #f5f7fa;
                font-family: '{font_name}';
                color: #000000;
            }}
        """)

        self.scroll_content = QWidget()
        self.init_ui()
        self.center_window()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)
        main_layout.addWidget(self.create_header())
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        content_layout = QVBoxLayout(self.scroll_content)
        content_layout.setSpacing(20)
        content_layout.addWidget(self.create_result_card())
        
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(15)
        charts_layout.addWidget(self.create_chart_card("📈 연체 현황 분석", self.create_debt_chart))
        charts_layout.addWidget(self.create_chart_card("💰 재무 건전성 지표", self.create_financial_chart))
        content_layout.addLayout(charts_layout)
        
        content_layout.addWidget(self.create_analysis_card())
        
        scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(scroll_area, 1)
        main_layout.addLayout(self.create_bottom_buttons(), 0)

    # --- 이하 UI 및 유틸리티 함수 (큰 변경 없음) ---
    def center_window(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def save_to_pdf(self):
        default_filename = os.path.join(os.path.expanduser("~"), "Desktop", f"{self.company_name}_부도예측_리포트.pdf")
        filename, _ = QFileDialog.getSaveFileName(self, "PDF로 저장", default_filename, "PDF Files (*.pdf)")
        if not filename: return

        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(filename)
        printer.setPageSize(QPrinter.A4)
        printer.setFullPage(True)
        
        target_size = self.scroll_content.sizeHint()
        pixmap = QPixmap(target_size)
        pixmap.fill(Qt.white)
        self.scroll_content.render(pixmap)
        
        painter = QPainter()
        if not painter.begin(printer): return

        page_rect = painter.viewport()
        pixmap_rect = pixmap.rect()
        ratio = page_rect.width() / pixmap_rect.width()
        scaled_height = int(pixmap_rect.height() * ratio)
        target_rect = QRect(0, 0, page_rect.width(), scaled_height)
        painter.drawPixmap(target_rect, pixmap, pixmap_rect)
        painter.end()
        
        try: os.startfile(os.path.dirname(filename))
        except AttributeError: print(f"PDF 저장 완료: {os.path.dirname(filename)}")

    def create_header(self):
        header = QFrame()
        header.setFixedHeight(70)
        header.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #e74c3c, stop:1 #c0392b); border-radius: 8px; padding: 10px;")
        layout = QVBoxLayout(header)
        layout.setSpacing(5)
        layout.setAlignment(Qt.AlignCenter)
        title = QLabel(f"📊 {self.company_name} 부도 예측 결과")
        title.setFont(QFont(self.font().family(), 18, QFont.Bold))
        title.setStyleSheet("color: #ffffff; background: transparent;")
        subtitle = QLabel(f"예측 확률: {self.prediction_data['probability']:.1%} | 위험도: {self.prediction_data['risk_level']}")
        subtitle.setFont(QFont(self.font().family(), 11))
        subtitle.setStyleSheet("color: #ffffff; background: transparent;")
        for label in [title, subtitle]: label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        return header

    def create_bottom_buttons(self):
        button_layout = QHBoxLayout()
        pdf_btn = QPushButton("📄 PDF로 저장")
        new_prediction_btn = QPushButton("🔄 새 예측")
        close_btn = QPushButton("❌ 닫기")
        pdf_btn.clicked.connect(self.save_to_pdf)
        new_prediction_btn.clicked.connect(self.close)
        close_btn.clicked.connect(self.close)

        buttons_styles = {
            pdf_btn: "background-color: #34495e; color: #ffffff;",
            new_prediction_btn: "background-color: #3498db; color: #ffffff;",
            close_btn: "background-color: #95a5a6; color: #ffffff;"
        }
        for btn, style in buttons_styles.items():
            btn.setFixedHeight(45)
            btn.setFont(QFont(self.font().family(), 11, QFont.Bold))
            btn.setStyleSheet(f"QPushButton {{ {style} border: none; border-radius: 22px; padding: 12px 25px; }} QPushButton:hover {{ background-color: #2c3e50; }}")

        button_layout.addWidget(pdf_btn)
        button_layout.addStretch()
        button_layout.addWidget(new_prediction_btn)
        button_layout.addWidget(close_btn)
        return button_layout

    def create_result_card(self):
        card = QFrame()
        card.setStyleSheet("background-color: white; border-radius: 15px; border: 1px solid #e1e8ed; padding: 30px;")
        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        probability = self.prediction_data['probability']
        status_emoji, status_text, status_color = ("🚨", "부도 위험", "#e74c3c") if probability > 0.5 else ("✅", "안전", "#27ae60")
        status_label = QLabel(f"{status_emoji} {status_text}")
        status_label.setFont(QFont(self.font().family(), 28, QFont.Bold))
        status_label.setStyleSheet(f"color: {status_color};")
        prob_label = QLabel(f"부도 확률: {probability:.1%}")
        prob_label.setFont(QFont(self.font().family(), 24, QFont.Bold))
        risk_label = QLabel(f"위험도: {self.prediction_data['risk_level']}")
        risk_label.setFont(QFont(self.font().family(), 16))
        risk_label.setStyleSheet("color: #7f8c8d;")
        for label in [status_label, prob_label, risk_label]: label.setAlignment(Qt.AlignCenter)
        layout.addWidget(status_label)
        layout.addWidget(prob_label)
        layout.addWidget(risk_label)
        layout.addWidget(self.create_confidence_gauge(probability))
        return card

    def create_confidence_gauge(self, probability):
        frame = QFrame()
        frame.setFixedHeight(80)
        layout = QVBoxLayout(frame)
        layout.setAlignment(Qt.AlignCenter)
        gauge_frame = QFrame()
        gauge_frame.setFixedSize(400, 20)
        gauge_frame.setStyleSheet("background-color: #ecf0f1; border-radius: 10px; border: 1px solid #d5dbdb;")
        gauge_fill = QFrame(gauge_frame)
        gauge_fill.setGeometry(0, 0, int(400 * probability), 20)
        if probability < 0.3: fill_color = "#27ae60"
        elif probability < 0.7: fill_color = "#f39c12"
        else: fill_color = "#e74c3c"
        gauge_fill.setStyleSheet(f"background-color: {fill_color}; border-radius: 10px;")
        gauge_label = QLabel(f"예측 신뢰도: {probability:.1%}")
        gauge_label.setFont(QFont(self.font().family(), 12))
        gauge_label.setStyleSheet("color: #34495e; margin-top: 10px;")
        gauge_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(gauge_frame)
        layout.addWidget(gauge_label)
        return frame

    def create_chart_card(self, title_text, create_chart_function):
        card = QFrame()
        card.setStyleSheet("background-color: white; border-radius: 12px; border: 1px solid #e1e8ed; padding: 20px;")
        layout = QVBoxLayout(card)
        title = QLabel(title_text)
        title.setFont(QFont(self.font().family(), 14, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 15px;")
        canvas = create_chart_function()
        layout.addWidget(title)
        layout.addWidget(canvas)
        return card

    def create_debt_chart(self):
        fig = Figure(figsize=(6, 4), dpi=100, facecolor='white')
        ax = fig.add_subplot(111)
        categories = ['3개월', '6개월', '1년', '3년']
        values = [self.input_data.get(f'최장연체일수_{cat}', 0) for cat in categories]
        bars = ax.bar(categories, values, color=['#3498db', '#e67e22', '#e74c3c', '#9b59b6'], alpha=0.8)
        ax.set_title('기간별 최장 연체일수', fontsize=12, fontweight='bold')
        ax.set_ylabel('연체일수 (일)', fontsize=10)
        for bar in bars:
            height = bar.get_height()
            if height > 0: ax.text(bar.get_x() + bar.get_width()/2., height, f'{height:.0f}일', ha='center', va='bottom', fontsize=9)
        fig.tight_layout()
        return FigureCanvas(fig)

    def create_financial_chart(self):
        fig = Figure(figsize=(6, 4), dpi=100, facecolor='white')
        ax = fig.add_subplot(111)
        categories = ['부채비율', '유동비율']
        values = [self.input_data.get('재무비율_부채비율', 0), self.input_data.get('재무비율_유동비율', 0)]
        reference = [50, 100]
        x = np.arange(len(categories))
        width = 0.35
        bars1 = ax.bar(x - width/2, values, width, label='실제값', color='#e74c3c', alpha=0.8)
        bars2 = ax.bar(x + width/2, reference, width, label='권장기준', color='#95a5a6', alpha=0.6)
        ax.set_title('재무비율 분석', fontsize=12, fontweight='bold')
        ax.set_ylabel('비율 (%)', fontsize=10)
        ax.set_xticks(x)
        ax.set_xticklabels(categories)
        ax.legend()
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height, f'{height:.1f}%', ha='center', va='bottom', fontsize=9)
        fig.tight_layout()
        return FigureCanvas(fig)

    def create_analysis_card(self):
        card = QFrame()
        card.setStyleSheet("background-color: white; border-radius: 12px; border: 1px solid #e1e8ed; padding: 25px;")
        layout = QVBoxLayout(card)
        layout.setSpacing(15)
        title = QLabel("🔍 상세 분석 결과")
        title.setFont(QFont(self.font().family(), 16, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        grid = QGridLayout()
        grid.setSpacing(20)
        risk_items = [f"부채비율: {self.input_data.get('재무비율_부채비율', 0):.1f}% (기준: 50% 이하)", f"연체 기관수: {self.input_data.get('연체기관수_전체', 0):.0f}개", f"최장 연체일수: {max(self.input_data.get(f'최장연체일수_{cat}', 0) for cat in ['3개월', '6개월', '1년', '3년']):.0f}일"]
        grid.addWidget(self.create_info_group("⚠️ 주요 위험 요소", risk_items), 0, 0)
        financial_items = [f"자산총계: {self.input_data.get('자산총계', 0):,.0f} 백만원", f"부채총계: {self.input_data.get('부채총계', 0):,.0f} 백만원", f"매출액: {self.input_data.get('매출액', 0):,.0f} 백만원", f"당기순이익: {self.input_data.get('당기순이익', 0):,.0f} 백만원"]
        grid.addWidget(self.create_info_group("💼 재무 현황", financial_items), 0, 1)
        recom_items = []
        if self.input_data.get('재무비율_부채비율', 0) > 70: recom_items.append("부채비율이 높습니다. 부채 감축을 권장합니다.")
        if self.input_data.get('연체기관수_전체', 0) > 0: recom_items.append("연체 이력이 있습니다. 신용 관리가 필요합니다.")
        if self.input_data.get('당기순이익', 0) < 0: recom_items.append("수익성 개선이 필요합니다.")
        if not recom_items: recom_items.append("전반적으로 양호한 재무 상태입니다.")
        grid.addWidget(self.create_info_group("💡 개선 권고사항", recom_items), 1, 0, 1, 2)
        layout.addWidget(title)
        layout.addLayout(grid)
        return card

    def create_info_group(self, title, items):
        group = QGroupBox(title)
        group.setFont(QFont(self.font().family(), 12, QFont.Bold))
        group.setStyleSheet("QGroupBox { border: 1px solid #d1d9e0; border-radius: 8px; margin-top: 12px; padding: 20px 15px 10px 15px; background-color: #f8f9fb; } QGroupBox::title { subcontrol-origin: margin; left: 15px; padding: 0 8px; color: #2c3e50; }")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)
        for item in items:
            label = QLabel(f"• {item}")
            label.setFont(QFont(self.font().family(), 10))
            label.setStyleSheet("color: #34495e; padding: 2px 0;")
            label.setWordWrap(True)
            layout.addWidget(label)
        return group

if __name__ == "__main__":
    app = QApplication(sys.argv)
    sample_pred = {'probability': 0.75, 'risk_level': '높음'}
    sample_in = {'재무비율_부채비율': 85.5, '재무비율_유동비율': 120.3, '연체기관수_전체': 2, '최장연체일수_3개월': 15, '최장연체일수_6개월': 30, '최장연체일수_1년': 45, '최장연체일수_3년': 60, '자산총계': 50000, '부채총계': 42750, '매출액': 120000, '당기순이익': -5000}
    window = PredictionResultWindow(sample_pred, sample_in, "샘플전자")
    window.show()
    sys.exit(app.exec_())