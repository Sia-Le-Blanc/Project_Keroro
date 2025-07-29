# prediction_result.py

import sys, os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QPainter
from PyQt5.QtPrintSupport import QPrinter

class PredictionResultWindow(QWidget):
    def __init__(self, prediction_data, input_data, company_name="N/A"):
        super().__init__()
        self.font_name = "Apple SD Gothic Neo" if sys.platform == "darwin" else "Malgun Gothic"
        plt.rcParams['font.family'] = [self.font_name]
        plt.rcParams['axes.unicode_minus'] = False
        self.scroll_content = QWidget()
        self.main_layout = QVBoxLayout(self)
        self.setup_ui()
        self.update_data(prediction_data, input_data, company_name)
        self.center_window()

    def setup_ui(self):
        self.setMinimumSize(1000, 700); self.resize(1200, 800)
        self.setFont(QFont(self.font_name))
        self.setStyleSheet(f"QWidget {{ background-color: #f5f7fa; font-family: '{self.font_name}'; color: #2c3e50; }}")
        self.main_layout.setContentsMargins(25, 25, 25, 25); self.main_layout.setSpacing(20)
        self.header_widget = QWidget(); self.main_content_widget = QWidget()
        scroll_area = QScrollArea(); scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        scroll_area.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.header_widget); self.main_layout.addWidget(scroll_area, 1); self.main_layout.addLayout(self.create_bottom_buttons())

    def update_data(self, prediction_data, input_data, company_name):
        self.prediction_data = prediction_data; self.input_data = input_data; self.company_name = company_name
        self.setWindowTitle(f"📊 {self.company_name} - 기업 부도 예측 결과")
        self.clear_layout(self.main_layout); self.scroll_content = QWidget(); self.setup_ui()
        new_header = self.create_header(); old_header = self.header_widget
        self.main_layout.replaceWidget(old_header, new_header); old_header.deleteLater(); self.header_widget = new_header
        content_layout = QVBoxLayout(self.scroll_content)
        content_layout.setSpacing(20); content_layout.setContentsMargins(5, 5, 5, 5)
        content_layout.addWidget(self.create_result_card())
        charts_layout = QHBoxLayout(); charts_layout.setSpacing(15)
        charts_layout.addWidget(self.create_chart_card("📈 연체 현황 분석", self.create_debt_chart))
        charts_layout.addWidget(self.create_chart_card("💰 재무 건전성 지표", self.create_financial_chart))
        content_layout.addLayout(charts_layout); content_layout.addWidget(self.create_analysis_card())

    def clear_layout(self, layout):
        if layout is None: return
        while layout.count():
            item = layout.takeAt(0); widget = item.widget()
            if widget is not None: widget.deleteLater()
            else: self.clear_layout(item.layout())
    
    def create_header(self):
        header = QFrame(); header.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #e74c3c, stop:1 #c0392b); border-radius: 8px; padding: 20px;")
        layout = QVBoxLayout(header); layout.setAlignment(Qt.AlignCenter)
        title = QLabel(f"📊 {self.company_name} - 기업 부도 예측 결과"); title.setFont(QFont(self.font_name, 18, QFont.Bold))
        risk_level = self.prediction_data.get('risk_level', 'N/A'); probability = self.prediction_data.get('probability', 0)
        subtitle = QLabel(f"예측 확률: {probability:.1%} | 위험도: {risk_level}"); subtitle.setFont(QFont(self.font_name, 11))
        for label in [title, subtitle]:
            label.setStyleSheet("color: #ffffff; background: transparent;"); label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title); layout.addWidget(subtitle)
        return header

    def create_bottom_buttons(self):
        layout = QHBoxLayout(); pdf_btn = QPushButton("📄 PDF로 저장"); pdf_btn.clicked.connect(self.save_to_pdf)
        pdf_btn.setStyleSheet("background-color: #34495e; color: white;"); close_btn = QPushButton("❌ 닫기")
        close_btn.clicked.connect(self.close); close_btn.setStyleSheet("background-color: #95a5a6; color: white;")
        layout.addStretch(); layout.addWidget(pdf_btn); layout.addWidget(close_btn)
        for btn in [pdf_btn, close_btn]:
            btn.setMinimumHeight(45); btn.setMinimumWidth(150); btn.setFont(QFont(self.font_name, 11, QFont.Bold))
            btn.setStyleSheet(f"{btn.styleSheet()} border-radius: 22px; padding: 0 25px;")
        return layout

    def create_result_card(self):
        card = QFrame(); card.setStyleSheet("background-color: white; border-radius: 12px; border: 1px solid #e1e8ed; padding: 25px;")
        layout = QVBoxLayout(card); layout.setAlignment(Qt.AlignCenter); layout.setSpacing(15)
        probability = self.prediction_data['probability']; is_danger = probability > 0.5
        status_emoji, status_text, status_color = ("🚨", "부도 위험", "#e74c3c") if is_danger else ("✅", "안전", "#27ae60")
        status_label = QLabel(f"{status_emoji} {status_text}"); status_label.setFont(QFont(self.font_name, 28, QFont.Bold)); status_label.setStyleSheet(f"color: {status_color};")
        prob_label = QLabel(f"부도 확률: {probability:.1%}"); prob_label.setFont(QFont(self.font_name, 24, QFont.Bold))
        risk_label = QLabel(f"위험도: {self.prediction_data['risk_level']}"); risk_label.setFont(QFont(self.font_name, 16, QFont.Normal)); risk_label.setStyleSheet("color: #7f8c8d;")
        for label in [status_label, prob_label, risk_label]: label.setAlignment(Qt.AlignCenter)
        layout.addWidget(status_label); layout.addWidget(prob_label); layout.addWidget(risk_label); layout.addWidget(self.create_confidence_gauge(probability))
        return card

    def create_confidence_gauge(self, probability):
        frame = QFrame(); frame.setMinimumHeight(60); layout = QVBoxLayout(frame); layout.setAlignment(Qt.AlignCenter); layout.setSpacing(10)
        gauge_label = QLabel("위험도 수준"); gauge_label.setFont(QFont(self.font_name, 11)); gauge_frame = QFrame()
        gauge_frame.setFixedSize(400, 20); gauge_frame.setStyleSheet("background-color: #ecf0f1; border-radius: 10px;")
        gauge_fill = QFrame(gauge_frame); gauge_fill.setGeometry(0, 0, int(400 * probability), 20)
        if probability < 0.3: fill_color = "#27ae60"
        elif probability < 0.7: fill_color = "#f39c12"
        else: fill_color = "#e74c3c"
        gauge_fill.setStyleSheet(f"background-color: {fill_color}; border-radius: 10px;"); layout.addWidget(gauge_label); layout.addWidget(gauge_frame)
        return frame

    def create_chart_card(self, title_text, create_chart_function):
        card = QGroupBox(title_text); card.setFont(QFont(self.font_name, 14, QFont.Bold))
        card.setStyleSheet("QGroupBox { border: 1px solid #e1e8ed; border-radius: 12px; margin-top: 10px; background-color: white; } QGroupBox::title { subcontrol-origin: margin; left: 15px; padding: 5px 10px; }")
        layout = QVBoxLayout(card); layout.setContentsMargins(15, 15, 15, 15); layout.setSpacing(10)
        canvas = create_chart_function(); canvas.setMinimumHeight(300); layout.addWidget(canvas)
        return card

    def create_debt_chart(self):
        fig = Figure(figsize=(6, 4), facecolor='white'); ax = fig.add_subplot(111)
        categories = ['3개월', '6개월', '1년', '3년']; values = [self.input_data.get(f'최장연체일수_{cat}', 0) for cat in categories]
        colors = ['#3498db', '#e67e22', '#e74c3c', '#9b59b6']; bars = ax.bar(categories, values, color=colors, alpha=0.8)
        ax.set_title('기간별 최장 연체일수', fontsize=12, fontweight='bold', pad=15); ax.set_ylabel('연체일수 (일)', fontsize=10)
        ax.tick_params(axis='x', labelsize=9); ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
        for bar in bars:
            height = bar.get_height()
            if height > 0: ax.text(bar.get_x() + bar.get_width()/2., height, f'{height:.0f}일', ha='center', va='bottom', fontsize=9, fontweight='bold')
        fig.tight_layout(); return FigureCanvas(fig)

    def create_financial_chart(self):
        fig = Figure(figsize=(6, 4), facecolor='white'); ax = fig.add_subplot(111)
        categories = ['부채비율', '유동비율']; values = [self.input_data.get('재무비율_부채비율', 0), self.input_data.get('재무비율_유동비율', 0)]; reference = [100, 200]
        x = np.arange(len(categories)); width = 0.35; colors = ['#e74c3c', '#27ae60']
        bars1 = ax.bar(x - width/2, values, width, label='입력값', color=colors, alpha=0.8)
        bars2 = ax.bar(x + width/2, reference, width, label='권장기준', color='#bdc3c7', alpha=0.6)
        ax.set_title('주요 재무비율 분석', fontsize=12, fontweight='bold', pad=15); ax.set_ylabel('비율 (%)', fontsize=10)
        ax.set_xticks(x); ax.set_xticklabels(categories); ax.legend(); ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
        for bar in bars1:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height, f'{height:.0f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')
        fig.tight_layout(); return FigureCanvas(fig)

    def create_analysis_card(self):
        card = QGroupBox("🔍 AI 종합 분석 및 권고"); card.setFont(QFont(self.font_name, 14, QFont.Bold))
        card.setStyleSheet("QGroupBox { border: 1px solid #e1e8ed; border-radius: 12px; margin-top: 10px; background-color: white; } QGroupBox::title { subcontrol-origin: margin; left: 15px; padding: 5px 10px; }")
        layout = QGridLayout(card); layout.setSpacing(20); layout.setContentsMargins(20, 25, 20, 20)
        risk_items = [f"부채비율: {self.input_data.get('재무비율_부채비율', 0):.1f}% (권장: 100% 이하)", f"유동비율: {self.input_data.get('재무비율_유동비율', 0):.1f}% (권장: 200% 이상)", f"연체 기관수: {self.input_data.get('연체기관수_전체', 0):.0f}개"]
        layout.addWidget(self.create_info_group("⚠️ 주요 위험 요소", risk_items), 0, 0)
        financial_items = [f"자산총계: {self.input_data.get('자산총계', 0):,.0f} 백만원", f"부채총계: {self.input_data.get('부채총계', 0):,.0f} 백만원", f"매출액: {self.input_data.get('매출액', 0):,.0f} 백만원", f"당기순이익: {self.input_data.get('당기순이익', 0):,.0f} 백만원"]
        layout.addWidget(self.create_info_group("💼 재무 현황", financial_items), 0, 1)
        recom_items = []; prob = self.prediction_data['probability']
        if prob < 0.3: recom_items.append("전반적으로 재무 상태가 안정적으로 판단됩니다.")
        else:
            if self.input_data.get('재무비율_부채비율', 0) > 100: recom_items.append("부채비율이 권장 기준(100%)을 초과합니다. 부채 구조 개선 및 자본 확충을 고려해야 합니다.")
            if self.input_data.get('재무비율_유동비율', 0) < 200: recom_items.append("유동비율이 권장 기준(200%)에 미치지 못합니다. 단기 지급능력 확보를 위한 유동성 관리가 필요합니다.")
            if self.input_data.get('연체기관수_전체', 0) > 0: recom_items.append("연체 이력이 발견되었습니다. 이는 신용도에 부정적 영향을 미치므로 즉각적인 해결이 중요합니다.")
            if self.input_data.get('당기순이익', 0) < 0: recom_items.append("당기순손실 상태입니다. 원가 절감, 매출 증대 등 수익성 개선 전략이 시급합니다.")
        if not recom_items: recom_items.append("재무 지표를 지속적으로 관리하며 안정성을 유지하는 것이 중요합니다.")
        layout.addWidget(self.create_info_group("💡 개선 권고사항", recom_items), 1, 0, 1, 2)
        return card

    def create_info_group(self, title, items):
        group = QGroupBox(title); group.setFont(QFont(self.font_name, 12, QFont.Bold))
        group.setStyleSheet("QGroupBox { border: 1px solid #e8eaf6; border-radius: 8px; margin-top: 10px; padding: 20px 15px 10px 15px; background-color: #f8f9fb; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; color: #3f51b5; }")
        layout = QVBoxLayout(group); layout.setSpacing(8)
        for item in items:
            label = QLabel(f"• {item}"); label.setFont(QFont(self.font_name, 10))
            label.setStyleSheet("color: #34495e; background: transparent;"); label.setWordWrap(True); layout.addWidget(label)
        return group

    def save_to_pdf(self):
        default_filename = os.path.join(os.path.expanduser("~"), "Desktop", f"{self.company_name}_부도예측_리포트.pdf")
        filename, _ = QFileDialog.getSaveFileName(self, "PDF로 저장", default_filename, "PDF Files (*.pdf)")
        if not filename: return
        printer = QPrinter(QPrinter.HighResolution); printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(filename); printer.setPageSize(QPrinter.A4); printer.setFullPage(True)
        pixmap = self.scroll_content.grab(); painter = QPainter()
        if not painter.begin(printer): QMessageBox.critical(self, "오류", "PDF 출력을 시작할 수 없습니다."); return
        page_rect = painter.viewport(); pixmap_rect = pixmap.rect()
        ratio = page_rect.width() / float(pixmap_rect.width())
        painter.scale(ratio, ratio); painter.drawPixmap(0, 0, pixmap); painter.end()
        QMessageBox.information(self, "저장 완료", f"PDF 리포트가 성공적으로 저장되었습니다:\n{filename}")
    
    def center_window(self): qr = self.frameGeometry(); cp = QDesktopWidget().availableGeometry().center(); qr.moveCenter(cp); self.move(qr.topLeft())

if __name__ == '__main__':
    app = QApplication(sys.argv); sample_pred = {'probability': 0.75, 'risk_level': '매우 높음'}
    sample_input = {'최장연체일수_3개월': 10, '최장연체일수_6개월': 30, '최장연체일수_1년': 90, '최장연체일수_3년': 90, '재무비율_부채비율': 250.5, '재무비율_유동비율': 80.2, '연체기관수_전체': 3, '자산총계': 50000, '부채총계': 35000, '매출액': 80000, '당기순이익': -5000}
    window = PredictionResultWindow(sample_pred, sample_input, "샘플전자"); window.show(); sys.exit(app.exec_())