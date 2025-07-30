# vacancy_result.py

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QFont, QColor, QPainter, QCursor, QPixmap, QRegion
from PyQt5.QtPrintSupport import QPrinter
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

class VacancyResultWindow(QWidget):
    def __init__(self, predicted_rate, input_data, project_name="N/A"):
        super().__init__()
        self.font_name = "Apple SD Gothic Neo" if sys.platform == "darwin" else "Malgun Gothic"
        plt.rcParams['font.family'] = [self.font_name]
        plt.rcParams['axes.unicode_minus'] = False
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.container_widget = QWidget()
        self.main_layout.addWidget(self.container_widget)

        self.setup_ui_base()
        self.update_data(predicted_rate, input_data, project_name)
        self.center_window()

    def setup_ui_base(self):
        self.setMinimumSize(950, 800)  # 크기 증가
        self.resize(1000, 850)  # 기본 크기 증가
        self.setStyleSheet(f"QWidget {{ background-color: #f8f9fa; font-family: '{self.font_name}'; color: #212529; }}")

    def update_data(self, predicted_rate, input_data, project_name):
        self.predicted_rate = predicted_rate
        self.input_data = input_data
        self.project_name = project_name
        self.setWindowTitle(f"📈 {self.project_name} - 분양률 예측 결과")

        old_container = self.container_widget
        
        self.container_widget = QWidget()
        container_layout = QVBoxLayout(self.container_widget)
        container_layout.setContentsMargins(0,0,0,0)
        container_layout.setSpacing(0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        scroll_content = QWidget()
        scroll_area.setWidget(scroll_content)
        
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(30, 30, 30, 30)  # 여백 증가
        content_layout.setSpacing(22)  # 간격 증가

        content_layout.addWidget(self.create_header())
        content_layout.addWidget(self.create_result_card())

        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(22)  # 간격 증가
        bottom_layout.addWidget(self.create_analysis_card())
        bottom_layout.addWidget(self.create_input_summary_card())

        content_layout.addLayout(bottom_layout)
        content_layout.addStretch()
        
        container_layout.addWidget(scroll_area)
        container_layout.addWidget(self.create_bottom_buttons())

        self.main_layout.replaceWidget(old_container, self.container_widget)
        old_container.deleteLater()

    def add_shadow_effect(self, widget):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 5)
        widget.setGraphicsEffect(shadow)
        return widget

    # --- 색상 결정 로직을 위한 새로운 함수 ---
    def get_rate_color(self):
        rate = self.predicted_rate
        if rate >= 85: return "#2980b9"  # 진한 파랑
        elif rate >= 80: return "#3498db"  # 파랑
        elif rate >= 70: return "#28a745"  # 초록
        elif rate >= 60: return "#fd7e14"  # 주황
        else: return "#dc3545"      # 빨강

    def create_header(self):
        header = QFrame(); header.setFixedHeight(110)  # 높이 증가
        header.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #3498db, stop:1 #2980b9);
            border-radius: 8px;
        """)

        layout = QVBoxLayout(header); layout.setAlignment(Qt.AlignCenter)
        title = QLabel(f"📈 {self.project_name} - 분양률 예측 결과"); title.setFont(QFont(self.font_name, 20, QFont.Bold))  # 폰트 크기 증가
        subtitle = QLabel("AI 모델 분석을 통한 분양률 예측 리포트"); subtitle.setFont(QFont(self.font_name, 12))  # 폰트 크기 증가

        for label in [title, subtitle]:
            label.setStyleSheet("color: #ffffff; background: transparent;"); label.setAlignment(Qt.AlignCenter)

        layout.addWidget(title); layout.addWidget(subtitle)
        return self.add_shadow_effect(header)

    def create_result_card(self):
        card = QFrame()
        card.setStyleSheet("background-color: white; border-radius: 12px;")
        layout = QHBoxLayout(card)
        layout.setContentsMargins(40, 30, 50, 30)  # 여백 증가
        layout.setSpacing(25)  # 간격 증가

        chart_canvas = self.create_gauge_chart()
        chart_canvas.setFixedSize(220, 165)  # 차트 크기 증가

        text_layout = QVBoxLayout()
        text_layout.setAlignment(Qt.AlignCenter)
        text_layout.setSpacing(0)

        label = QLabel("예상 분양률"); label.setFont(QFont(self.font_name, 17)); label.setStyleSheet("color: #495057;")  # 폰트 크기 증가
        
        # get_rate_color 함수를 사용하여 색상 설정
        color = self.get_rate_color()
        
        rate_label = QLabel(f"{self.predicted_rate:.1f}%"); rate_label.setFont(QFont(self.font_name, 75, QFont.Bold)); rate_label.setStyleSheet(f"color: {color};")  # 폰트 크기 증가

        text_layout.addWidget(label, alignment=Qt.AlignCenter); text_layout.addWidget(rate_label, alignment=Qt.AlignCenter)
        layout.addWidget(chart_canvas, 0, Qt.AlignCenter); layout.addSpacing(25); layout.addLayout(text_layout)  # 간격 증가
        return self.add_shadow_effect(card)

    def create_gauge_chart(self):
        fig = Figure(figsize=(2.2, 1.65), dpi=100); fig.patch.set_alpha(0)  # 크기 증가
        ax = fig.add_subplot(111); ax.patch.set_alpha(0)

        # get_rate_color 함수를 사용하여 색상 설정
        color = self.get_rate_color()
        
        ax.pie([self.predicted_rate, 100 - self.predicted_rate], radius=1.0, colors=[color, '#f1f3f5'], startangle=90,
               counterclock=False, wedgeprops={'width': 0.25, 'edgecolor': 'white'})
        ax.text(0, 0, f"{self.predicted_rate:.0f}%", ha='center', va='center', fontsize=22, fontweight='bold', color="#343a40")  # 폰트 크기 증가
        return FigureCanvas(fig)

    def create_analysis_card(self):
        card = QFrame(); card.setStyleSheet("background-color: white; border-radius: 12px;")
        layout = QVBoxLayout(card); layout.setContentsMargins(25, 25, 25, 25); layout.setSpacing(18)  # 여백과 간격 증가

        title_label = QLabel("💡 AI 종합 분석"); title_label.setFont(QFont(self.font_name, 15, QFont.Bold))  # 폰트 크기 증가
        
        rate = self.predicted_rate
        if rate >= 85: text = "<strong>최우수</strong>: 매우 높은 계약률입니다. 안정적인 자금 흐름이 기대되며, 단기 완판 가능성이 높습니다."
        elif rate >= 70: text = "<strong>우수</strong>: 양호한 계약률입니다. <strong>주요 시중은행의 중도금 대출 승인 요구 조건(약 70%)을 충족</strong>하여 안정적인 사업 진행이 예상됩니다."
        elif rate >= 60: text = "<strong>보통</strong>: 다소 아쉬운 계약률입니다. <strong>1금융권의 중도금 대출이 어려울 수 있으며</strong>, 지방은행 또는 제2금융권과의 협약이 필요할 수 있습니다."
        else: text = "<strong>주의</strong>: 계약률이 저조합니다. <strong>중도금 대출 협약에 난항이 예상</strong>되며, 고금리 자금 조달 시 사업비 부담이 가중될 수 있습니다. <strong>공사 지연 리스크 관리</strong>가 필요합니다."

        text_widget = QLabel(text); text_widget.setFont(QFont(self.font_name, 12)); text_widget.setWordWrap(True)  # 폰트 크기 증가
        text_widget.setAlignment(Qt.AlignCenter)
        text_widget.setStyleSheet("background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; padding: 22px; line-height: 1.6;")  # 패딩 증가
        
        layout.addWidget(title_label); layout.addWidget(text_widget)
        return self.add_shadow_effect(card)

    def create_input_summary_card(self):
        card = QFrame(); card.setStyleSheet("background-color: white; border-radius: 12px;")
        layout = QVBoxLayout(card); layout.setContentsMargins(25, 25, 25, 25); layout.setSpacing(18)  # 여백과 간격 증가
        
        title_label = QLabel("📝 주요 입력 정보"); title_label.setFont(QFont(self.font_name, 15, QFont.Bold))  # 폰트 크기 증가
        grid = QGridLayout(); grid.setSpacing(15)  # 간격 증가
        
        summary_items = {
            "브랜드": self.input_data.get('브랜드', 'N/A'), "건설사": self.input_data.get('건설사', 'N/A'),
            "지역": self.input_data.get('지역', 'N/A'), "총 세대수": f"{self.input_data.get('세대수')} 세대",
            "기준년월": self.input_data.get('기준년월', 'N/A')
        }
        for row, (label, value) in enumerate(summary_items.items()):
            label_widget = QLabel(label); label_widget.setFont(QFont(self.font_name, 11, QFont.Bold)); label_widget.setStyleSheet("color: #495057;")  # 폰트 크기 증가
            value_widget = QLabel(str(value)); value_widget.setFont(QFont(self.font_name, 11)); value_widget.setAlignment(Qt.AlignCenter)  # 폰트 크기 증가
            value_widget.setStyleSheet("background-color: #f1f3f5; border-radius: 8px; padding: 10px 15px; color: #343a40;")  # 패딩 증가
            grid.addWidget(label_widget, row, 0); grid.addWidget(value_widget, row, 1)
        
        layout.addWidget(title_label); layout.addLayout(grid)
        return self.add_shadow_effect(card)

    def create_bottom_buttons(self):
        frame = QFrame()
        frame.setStyleSheet("background-color: #ffffff; border-top: 1px solid #e9ecef;")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(30,18,30,18)  # 여백 증가
        pdf_btn = QPushButton("📄 PDF로 저장"); pdf_btn.clicked.connect(self.save_to_pdf)
        close_btn = QPushButton("❌ 닫기"); close_btn.clicked.connect(self.close)
        for btn in [pdf_btn, close_btn]:
            btn.setMinimumHeight(48); btn.setFont(QFont(self.font_name, 12, QFont.Bold)); btn.setCursor(QCursor(Qt.PointingHandCursor))  # 높이 및 폰트 크기 증가
            btn.setMinimumWidth(140)  # 너비 증가
        pdf_btn.setStyleSheet("QPushButton { background-color: #343a40; color: white; border: none; border-radius: 8px; padding: 0 22px; } QPushButton:hover { background-color: #495057; }")  # 패딩 증가
        close_btn.setStyleSheet("QPushButton { background-color: #ced4da; color: #343a40; border: none; border-radius: 8px; padding: 0 22px; } QPushButton:hover { background-color: #adb5bd; }")  # 패딩 증가
        layout.addStretch(); layout.addWidget(pdf_btn); layout.addWidget(close_btn)
        return frame

    def save_to_pdf(self):
        default_filename = f"{self.project_name}_분양률_예측_리포트.pdf"
        filename, _ = QFileDialog.getSaveFileName(self, "PDF로 저장", default_filename, "PDF Files (*.pdf)")
        if not filename: return
        
        try:
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(filename)
            printer.setPageSize(QPrinter.A4)

            painter = QPainter()
            if not painter.begin(printer):
                raise IOError("PDF 출력을 시작할 수 없습니다.")

            content_to_save = self.container_widget
            pixmap = QPixmap(content_to_save.size())
            content_to_save.render(pixmap)

            page_rect = painter.viewport()
            scaled_pixmap = pixmap.scaledToWidth(page_rect.width(), Qt.SmoothTransformation)

            painter.drawPixmap(0, 0, scaled_pixmap)
            
            painter.end()
            QMessageBox.information(self, "저장 완료", f"PDF 리포트가 성공적으로 저장되었습니다:\n{filename}")

        except Exception as e:
            QMessageBox.critical(self, "PDF 저장 오류", f"PDF를 저장하는 중 오류가 발생했습니다:\n{e}")

    def center_window(self):
        qr = self.frameGeometry(); cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp); self.move(qr.topLeft())