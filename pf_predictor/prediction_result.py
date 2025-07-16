import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
    QFrame, QScrollArea, QGridLayout, QPushButton, QGroupBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QPainter
import matplotlib
matplotlib.use('Qt5Agg')

# 한글 폰트 설정
plt.rcParams['font.family'] = ['Malgun Gothic', 'DejaVu Sans', 'AppleGothic']
plt.rcParams['axes.unicode_minus'] = False


class PredictionResultWindow(QWidget):
    def __init__(self, prediction_data, input_data):
        super().__init__()
        self.prediction_data = prediction_data
        self.input_data = input_data
        
        self.setWindowTitle("📊 기업 부도 예측 결과")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f7fa;
                font-family: 'Malgun Gothic', Arial, sans-serif;
            }
        """)
        
        self.init_ui()
        self.center_window()
    
    def init_ui(self):
        # 메인 레이아웃
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)
        
        # 헤더 영역
        header = self.create_header()
        main_layout.addWidget(header)
        
        # 스크롤 영역
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #f0f0f0;
                width: 12px;
                border-radius: 6px;
                margin: 2px;
            }
            QScrollBar::handle:vertical {
                background-color: #c0c0c0;
                border-radius: 6px;
                min-height: 25px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a0a0a0;
            }
        """)
        
        # 스크롤 내용
        scroll_content = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setSpacing(20)
        
        # 예측 결과 카드 (메인)
        result_card = self.create_result_card()
        content_layout.addWidget(result_card)
        
        # 차트 영역
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(15)
        
        # 연체 현황 차트
        debt_chart = self.create_debt_chart()
        charts_layout.addWidget(debt_chart)
        
        # 재무 건전성 차트
        financial_chart = self.create_financial_chart()
        charts_layout.addWidget(financial_chart)
        
        content_layout.addLayout(charts_layout)
        
        # 상세 분석 카드
        analysis_card = self.create_analysis_card()
        content_layout.addWidget(analysis_card)
        
        scroll_content.setLayout(content_layout)
        scroll_area.setWidget(scroll_content)
        
        # 하단 버튼 영역
        button_layout = QHBoxLayout()
        
        # PDF 저장 버튼
        pdf_btn = QPushButton("📄 PDF로 저장")
        pdf_btn.setFixedHeight(45)
        pdf_btn.setFont(QFont("Malgun Gothic", 11))
        pdf_btn.setStyleSheet("""
            QPushButton {
                background-color: #34495e;
                color: white;
                border: none;
                border-radius: 22px;
                padding: 12px 25px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2c3e50;
            }
        """)
        
        # 새 예측 버튼
        new_prediction_btn = QPushButton("🔄 새 예측")
        new_prediction_btn.setFixedHeight(45)
        new_prediction_btn.setFont(QFont("Malgun Gothic", 11))
        new_prediction_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 22px;
                padding: 12px 25px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        new_prediction_btn.clicked.connect(self.close)
        
        # 닫기 버튼
        close_btn = QPushButton("❌ 닫기")
        close_btn.setFixedHeight(45)
        close_btn.setFont(QFont("Malgun Gothic", 11))
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 22px;
                padding: 12px 25px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        close_btn.clicked.connect(self.close)
        
        button_layout.addWidget(pdf_btn)
        button_layout.addStretch()
        button_layout.addWidget(new_prediction_btn)
        button_layout.addWidget(close_btn)
        
        # 메인 레이아웃 구성
        main_layout.addWidget(scroll_area, 1)
        main_layout.addLayout(button_layout, 0)
        
        self.setLayout(main_layout)
    
    def create_header(self):
        """헤더 영역 생성"""
        header = QFrame()
        header.setFixedHeight(70)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #e74c3c, stop:1 #c0392b);
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setAlignment(Qt.AlignCenter)
        
        title = QLabel("📊 기업 부도 예측 결과")
        title.setFont(QFont("Malgun Gothic", 18, QFont.Bold))
        title.setStyleSheet("color: white; margin: 0;")
        title.setAlignment(Qt.AlignCenter)
        
        subtitle = QLabel(f"예측 확률: {self.prediction_data['probability']:.1%} | "
                         f"위험도: {self.prediction_data['risk_level']}")
        subtitle.setFont(QFont("Malgun Gothic", 11))
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.9); margin: 0;")
        subtitle.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(title)
        layout.addWidget(subtitle)
        header.setLayout(layout)
        
        return header
    
    def create_result_card(self):
        """메인 예측 결과 카드"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                border: 1px solid #e1e8ed;
                padding: 30px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        
        # 결과 아이콘 및 상태
        probability = self.prediction_data['probability']
        is_risky = probability > 0.5
        
        if is_risky:
            status_emoji = "🚨"
            status_text = "부도 위험"
            status_color = "#e74c3c"
        else:
            status_emoji = "✅"
            status_text = "안전"
            status_color = "#27ae60"
        
        # 상태 표시
        status_label = QLabel(f"{status_emoji} {status_text}")
        status_label.setFont(QFont("Malgun Gothic", 28, QFont.Bold))
        status_label.setStyleSheet(f"color: {status_color}; margin: 10px 0;")
        status_label.setAlignment(Qt.AlignCenter)
        
        # 확률 표시
        prob_label = QLabel(f"부도 확률: {probability:.1%}")
        prob_label.setFont(QFont("Malgun Gothic", 24, QFont.Bold))
        prob_label.setStyleSheet("color: #2c3e50; margin: 5px 0;")
        prob_label.setAlignment(Qt.AlignCenter)
        
        # 위험도 표시
        risk_label = QLabel(f"위험도: {self.prediction_data['risk_level']}")
        risk_label.setFont(QFont("Malgun Gothic", 16))
        risk_label.setStyleSheet("color: #7f8c8d; margin: 5px 0;")
        risk_label.setAlignment(Qt.AlignCenter)
        
        # 신뢰도 게이지
        confidence_frame = self.create_confidence_gauge(probability)
        
        layout.addWidget(status_label)
        layout.addWidget(prob_label)
        layout.addWidget(risk_label)
        layout.addWidget(confidence_frame)
        
        card.setLayout(layout)
        return card
    
    def create_confidence_gauge(self, probability):
        """신뢰도 게이지 생성"""
        frame = QFrame()
        frame.setFixedHeight(80)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        # 게이지 바
        gauge_frame = QFrame()
        gauge_frame.setFixedSize(400, 20)
        gauge_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #ecf0f1;
                border-radius: 10px;
                border: 1px solid #d5dbdb;
            }}
        """)
        
        # 게이지 내부 (확률에 따른 색상)
        gauge_fill = QFrame(gauge_frame)
        fill_width = int(400 * probability)
        gauge_fill.setGeometry(0, 0, fill_width, 20)
        
        if probability < 0.3:
            fill_color = "#27ae60"  # 녹색
        elif probability < 0.7:
            fill_color = "#f39c12"  # 주황색
        else:
            fill_color = "#e74c3c"  # 빨간색
            
        gauge_fill.setStyleSheet(f"""
            QFrame {{
                background-color: {fill_color};
                border-radius: 10px;
            }}
        """)
        
        # 게이지 라벨
        gauge_label = QLabel(f"예측 신뢰도: {probability:.1%}")
        gauge_label.setFont(QFont("Malgun Gothic", 12))
        gauge_label.setStyleSheet("color: #34495e; margin-top: 10px;")
        gauge_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(gauge_frame)
        layout.addWidget(gauge_label)
        frame.setLayout(layout)
        
        return frame
    
    def create_debt_chart(self):
        """연체 현황 차트"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e1e8ed;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # 제목
        title = QLabel("📈 연체 현황 분석")
        title.setFont(QFont("Malgun Gothic", 14, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 15px;")
        
        # matplotlib 차트
        fig = Figure(figsize=(6, 4), dpi=100)
        canvas = FigureCanvas(fig)
        
        ax = fig.add_subplot(111)
        
        # 연체 데이터 (입력 데이터에서 추출)
        debt_categories = ['3개월', '6개월', '1년', '3년']
        debt_values = [
            self.input_data.get('최장연체일수_3개월', 0),
            self.input_data.get('최장연체일수_6개월', 0),
            self.input_data.get('최장연체일수_1년', 0),
            self.input_data.get('최장연체일수_3년', 0)
        ]
        
        colors = ['#3498db', '#e67e22', '#e74c3c', '#9b59b6']
        bars = ax.bar(debt_categories, debt_values, color=colors, alpha=0.8)
        
        ax.set_title('기간별 최장 연체일수', fontsize=12, fontweight='bold', pad=20)
        ax.set_ylabel('연체일수 (일)', fontsize=10)
        ax.set_xlabel('기간', fontsize=10)
        
        # 값 표시
        for bar, value in zip(bars, debt_values):
            if value > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                       f'{value:.0f}일', ha='center', va='bottom', fontsize=9)
        
        fig.tight_layout()
        
        layout.addWidget(title)
        layout.addWidget(canvas)
        card.setLayout(layout)
        
        return card
    
    def create_financial_chart(self):
        """재무 건전성 차트"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e1e8ed;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # 제목
        title = QLabel("💰 재무 건전성 지표")
        title.setFont(QFont("Malgun Gothic", 14, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 15px;")
        
        # matplotlib 차트
        fig = Figure(figsize=(6, 4), dpi=100)
        canvas = FigureCanvas(fig)
        
        ax = fig.add_subplot(111)
        
        # 재무비율 데이터
        debt_ratio = self.input_data.get('재무비율_부채비율', 0)
        current_ratio = self.input_data.get('재무비율_유동비율', 0)
        
        categories = ['부채비율', '유동비율']
        values = [debt_ratio, current_ratio]
        reference = [50, 100]  # 기준값
        
        x = np.arange(len(categories))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, values, width, label='실제값', color='#e74c3c', alpha=0.8)
        bars2 = ax.bar(x + width/2, reference, width, label='권장기준', color='#95a5a6', alpha=0.6)
        
        ax.set_title('재무비율 분석', fontsize=12, fontweight='bold', pad=20)
        ax.set_ylabel('비율 (%)', fontsize=10)
        ax.set_xticks(x)
        ax.set_xticklabels(categories)
        ax.legend()
        
        # 값 표시
        for bar, value in zip(bars1, values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                   f'{value:.1f}%', ha='center', va='bottom', fontsize=9)
        
        for bar, value in zip(bars2, reference):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                   f'{value}%', ha='center', va='bottom', fontsize=9)
        
        fig.tight_layout()
        
        layout.addWidget(title)
        layout.addWidget(canvas)
        card.setLayout(layout)
        
        return card
    
    def create_analysis_card(self):
        """상세 분석 카드"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e1e8ed;
                padding: 25px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # 제목
        title = QLabel("🔍 상세 분석 결과")
        title.setFont(QFont("Malgun Gothic", 16, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        
        # 분석 내용을 그리드로 배치
        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)
        
        # 주요 위험 요소
        risk_group = self.create_info_group("⚠️ 주요 위험 요소", [
            f"부채비율: {self.input_data.get('재무비율_부채비율', 0):.1f}% (기준: 50% 이하)",
            f"연체 기관수: {self.input_data.get('연체기관수_전체', 0):.0f}개",
            f"최장 연체일수: {max([self.input_data.get('최장연체일수_3개월', 0), self.input_data.get('최장연체일수_6개월', 0), self.input_data.get('최장연체일수_1년', 0), self.input_data.get('최장연체일수_3년', 0)]):.0f}일"
        ])
        
        # 재무 현황
        financial_group = self.create_info_group("💼 재무 현황", [
            f"자산총계: {self.input_data.get('자산총계', 0):,.0f} 백만원",
            f"부채총계: {self.input_data.get('부채총계', 0):,.0f} 백만원",
            f"매출액: {self.input_data.get('매출액', 0):,.0f} 백만원",
            f"당기순이익: {self.input_data.get('당기순이익', 0):,.0f} 백만원"
        ])
        
        # 개선 권고사항
        recommendations = []
        debt_ratio = self.input_data.get('재무비율_부채비율', 0)
        
        if debt_ratio > 70:
            recommendations.append("부채비율이 높습니다. 부채 감축을 권장합니다.")
        if self.input_data.get('연체기관수_전체', 0) > 0:
            recommendations.append("연체 이력이 있습니다. 신용 관리가 필요합니다.")
        if self.input_data.get('당기순이익', 0) < 0:
            recommendations.append("수익성 개선이 필요합니다.")
        
        if not recommendations:
            recommendations.append("전반적으로 양호한 재무 상태입니다.")
        
        recommendation_group = self.create_info_group("💡 개선 권고사항", recommendations)
        
        grid_layout.addWidget(risk_group, 0, 0)
        grid_layout.addWidget(financial_group, 0, 1)
        grid_layout.addWidget(recommendation_group, 1, 0, 1, 2)
        
        layout.addWidget(title)
        layout.addLayout(grid_layout)
        card.setLayout(layout)
        
        return card
    
    def create_info_group(self, title, items):
        """정보 그룹 생성"""
        group = QGroupBox(title)
        group.setFont(QFont("Malgun Gothic", 12, QFont.Bold))
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #d1d9e0;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: #f8f9fb;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: #2c3e50;
                background-color: #f8f9fb;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        for item in items:
            label = QLabel(f"• {item}")
            label.setFont(QFont("Malgun Gothic", 10))
            label.setStyleSheet("color: #34495e; padding: 2px 0;")
            label.setWordWrap(True)
            layout.addWidget(label)
        
        group.setLayout(layout)
        return group
    
    def center_window(self):
        """창을 화면 중앙에 배치"""
        screen = QApplication.desktop().screenGeometry()
        window = self.geometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        self.move(x, y)


if __name__ == "__main__":
    # 테스트용
    app = QApplication(sys.argv)
    
    # 샘플 데이터
    sample_prediction = {
        'probability': 0.75,
        'risk_level': '높음',
        'prediction': True
    }
    
    sample_input = {
        '재무비율_부채비율': 85.5,
        '재무비율_유동비율': 120.3,
        '연체기관수_전체': 2,
        '최장연체일수_3개월': 15,
        '최장연체일수_6개월': 30,
        '최장연체일수_1년': 45,
        '최장연체일수_3년': 60,
        '자산총계': 50000,
        '부채총계': 42750,
        '매출액': 120000,
        '당기순이익': -5000
    }
    
    window = PredictionResultWindow(sample_prediction, sample_input)
    window.show()
    
    sys.exit(app.exec_())