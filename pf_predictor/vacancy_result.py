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
from PyQt5.QtGui import QFont
import matplotlib
matplotlib.use('Qt5Agg')

# 한글 폰트 설정
plt.rcParams['font.family'] = ['Malgun Gothic', 'DejaVu Sans', 'AppleGothic']
plt.rcParams['axes.unicode_minus'] = False


class VacancyResultWindow(QWidget):
    def __init__(self, prediction_data, input_data, project_name):
        super().__init__()
        self.prediction_data = prediction_data
        self.input_data = input_data
        self.project_name = project_name
        
        self.setWindowTitle("📊 부동산 분양률 예측 결과")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f8ff;
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
        
        # 차트 영역 (2x2 그리드)
        charts_layout = QGridLayout()
        charts_layout.setSpacing(15)
        
        # 분양률 게이지 차트
        gauge_chart = self.create_gauge_chart()
        charts_layout.addWidget(gauge_chart, 0, 0)
        
        # 위치 점수 차트
        location_chart = self.create_location_chart()
        charts_layout.addWidget(location_chart, 0, 1)
        
        # 편의시설 분석 차트
        convenience_chart = self.create_convenience_chart()
        charts_layout.addWidget(convenience_chart, 1, 0)
        
        # 경제지표 분석 차트
        economic_chart = self.create_economic_chart()
        charts_layout.addWidget(economic_chart, 1, 1)
        
        content_layout.addLayout(charts_layout)
        
        # 가격 비교 차트
        price_chart = self.create_price_comparison_chart()
        content_layout.addWidget(price_chart)
        
        # 상세 분석 카드
        analysis_card = self.create_analysis_card()
        content_layout.addWidget(analysis_card)
        
        scroll_content.setLayout(content_layout)
        scroll_area.setWidget(scroll_content)
        
        # 하단 버튼 영역
        button_layout = QHBoxLayout()
        
        # 버튼들
        buttons = [
            ("📄 PDF로 저장", "#34495e", "#2c3e50", None),
            ("🔄 새 예측", "#007bff", "#0056b3", self.close),
            ("❌ 닫기", "#95a5a6", "#7f8c8d", self.close)
        ]
        
        for text, color, hover_color, func in buttons:
            btn = QPushButton(text)
            btn.setFixedHeight(45)
            btn.setFont(QFont("Malgun Gothic", 11))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    border-radius: 22px;
                    padding: 12px 25px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {hover_color};
                }}
            """)
            if func:
                btn.clicked.connect(func)
            button_layout.addWidget(btn)
            
            if text == "📄 PDF로 저장":
                button_layout.addStretch()
        
        # 메인 레이아웃 구성
        main_layout.addWidget(scroll_area, 1)
        main_layout.addLayout(button_layout, 0)
        
        self.setLayout(main_layout)
    
    def create_header(self):
        """헤더 영역 생성"""
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #007bff, stop:1 #0056b3);
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignCenter)
        
        title = QLabel("📊 부동산 분양률 예측 결과")
        title.setFont(QFont("Malgun Gothic", 18, QFont.Bold))
        title.setStyleSheet("color: white; margin: 0;")
        title.setAlignment(Qt.AlignCenter)
        
        subtitle = QLabel(f"프로젝트: {self.project_name} | "
                         f"예측 분양률: {self.prediction_data['vacancy_rate']:.1f}% | "
                         f"등급: {self.prediction_data['grade']} | "
                         f"지역: {self.input_data['district']}")
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
                border: 1px solid #b8daff;
                padding: 30px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        
        # 결과 표시
        vacancy_rate = self.prediction_data['vacancy_rate']
        grade = self.prediction_data['grade']
        status = self.prediction_data['status']
        
        # 상태에 따른 이모지와 색상
        if vacancy_rate >= 75:
            status_emoji = "✅"
            status_color = "#28a745"
        elif vacancy_rate >= 60:
            status_emoji = "✅"
            status_color = "#28a745"
        elif vacancy_rate >= 45:
            status_emoji = "⚠️"
            status_color = "#ffc107"
        else:
            status_emoji = "🚨"
            status_color = "#dc3545"
        
        # 상태 표시
        status_label = QLabel(f"{status_emoji} {status}")
        status_label.setFont(QFont("Malgun Gothic", 28, QFont.Bold))
        status_label.setStyleSheet(f"color: {status_color}; margin: 10px 0;")
        status_label.setAlignment(Qt.AlignCenter)
        
        # 분양률 표시
        rate_label = QLabel(f"예상 분양률: {vacancy_rate:.1f}%")
        rate_label.setFont(QFont("Malgun Gothic", 24, QFont.Bold))
        rate_label.setStyleSheet("color: #2c3e50; margin: 5px 0;")
        rate_label.setAlignment(Qt.AlignCenter)
        
        # 등급 표시
        grade_label = QLabel(f"등급: {grade}")
        grade_label.setFont(QFont("Malgun Gothic", 16))
        grade_label.setStyleSheet("color: #7f8c8d; margin: 5px 0;")
        grade_label.setAlignment(Qt.AlignCenter)
        
        # 분양률 게이지
        gauge_frame = self.create_rate_gauge(vacancy_rate)
        
        layout.addWidget(status_label)
        layout.addWidget(rate_label)
        layout.addWidget(grade_label)
        layout.addWidget(gauge_frame)
        
        card.setLayout(layout)
        return card
    
    def create_rate_gauge(self, vacancy_rate):
        """분양률 게이지 생성"""
        frame = QFrame()
        frame.setFixedHeight(80)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        # 게이지 바
        gauge_frame = QFrame()
        gauge_frame.setFixedSize(400, 20)
        gauge_frame.setStyleSheet("""
            QFrame {
                background-color: #ecf0f1;
                border-radius: 10px;
                border: 1px solid #d5dbdb;
            }
        """)
        
        # 게이지 내부
        gauge_fill = QFrame(gauge_frame)
        fill_width = int(400 * (vacancy_rate / 100))
        gauge_fill.setGeometry(0, 0, fill_width, 20)
        
        if vacancy_rate >= 75:
            fill_color = "#28a745"
        elif vacancy_rate >= 60:
            fill_color = "#28a745"
        elif vacancy_rate >= 45:
            fill_color = "#ffc107"
        else:
            fill_color = "#dc3545"
            
        gauge_fill.setStyleSheet(f"""
            QFrame {{
                background-color: {fill_color};
                border-radius: 10px;
            }}
        """)
        
        # 게이지 라벨
        gauge_label = QLabel(f"분양률: {vacancy_rate:.1f}%")
        gauge_label.setFont(QFont("Malgun Gothic", 12))
        gauge_label.setStyleSheet("color: #34495e; margin-top: 10px;")
        gauge_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(gauge_frame)
        layout.addWidget(gauge_label)
        frame.setLayout(layout)
        
        return frame
    
    def create_gauge_chart(self):
        """분양률 게이지 차트"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #b8daff;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout()
        
        title = QLabel("📊 분양률 게이지")
        title.setFont(QFont("Malgun Gothic", 14, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 15px;")
        
        fig = Figure(figsize=(5, 4), dpi=100)
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        
        # 도넛 차트
        vacancy_rate = self.prediction_data['vacancy_rate']
        sizes = [vacancy_rate, 100 - vacancy_rate]
        colors = ['#007bff', '#e9ecef']
        
        wedges, texts = ax.pie(sizes, colors=colors, startangle=90, counterclock=False)
        
        # 중앙 원
        centre_circle = plt.Circle((0,0), 0.70, fc='white')
        ax.add_artist(centre_circle)
        
        # 중앙 텍스트
        ax.text(0, 0, f'{vacancy_rate:.1f}%', ha='center', va='center', 
                fontsize=18, fontweight='bold', color='#2c3e50')
        ax.text(0, -0.3, '분양률', ha='center', va='center', 
                fontsize=10, color='#7f8c8d')
        
        ax.set_title('예상 분양률', fontsize=12, fontweight='bold', pad=20)
        fig.tight_layout()
        
        layout.addWidget(title)
        layout.addWidget(canvas)
        card.setLayout(layout)
        
        return card
    
    def create_location_chart(self):
        """위치 분석 차트"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #b8daff;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout()
        
        title = QLabel("📍 위치 분석")
        title.setFont(QFont("Malgun Gothic", 14, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 15px;")
        
        fig = Figure(figsize=(5, 4), dpi=100)
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        
        # 위치 관련 데이터
        categories = ['지하철', '버스', '접면도로']
        values = [
            10 if self.input_data['subway_nearby'] else 0,
            8 if self.input_data['bus_stop'] else 0,
            min(self.input_data['road_count'] * 2, 10)
        ]
        
        colors = ['#007bff', '#28a745', '#ffc107']
        bars = ax.bar(categories, values, color=colors, alpha=0.8)
        
        ax.set_title('위치 접근성 점수', fontsize=12, fontweight='bold', pad=20)
        ax.set_ylabel('점수 (10점 만점)', fontsize=10)
        ax.set_ylim(0, 10)
        
        # 값 표시
        for bar, value in zip(bars, values):
            if value > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2, 
                       f'{value:.0f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        fig.tight_layout()
        
        layout.addWidget(title)
        layout.addWidget(canvas)
        card.setLayout(layout)
        
        return card
    
    def create_convenience_chart(self):
        """편의시설 분석 차트"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #b8daff;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout()
        
        title = QLabel("🏥 편의시설 분석")
        title.setFont(QFont("Malgun Gothic", 14, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 15px;")
        
        fig = Figure(figsize=(5, 4), dpi=100)
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        
        # 편의시설 데이터
        facilities = ['초등학교', '중학교', '고등학교', '병원', '공원']
        availability = [
            self.input_data['elementary_school'],
            self.input_data['middle_school'],
            self.input_data['high_school'],
            self.input_data['hospital_nearby'],
            self.input_data['park_nearby']
        ]
        
        # 도넛 차트
        available_count = sum(availability)
        sizes = [available_count, len(facilities) - available_count]
        colors = ['#28a745', '#e9ecef']
        labels = ['이용 가능', '이용 불가']
        
        wedges, texts, autotexts = ax.pie(sizes, colors=colors, labels=labels, 
                                         autopct='%1.0f%%', startangle=90)
        
        # 중앙 텍스트
        ax.text(0, 0, f'{available_count}/{len(facilities)}', ha='center', va='center', 
                fontsize=16, fontweight='bold', color='#2c3e50')
        
        ax.set_title('편의시설 이용 현황', fontsize=12, fontweight='bold', pad=20)
        fig.tight_layout()
        
        layout.addWidget(title)
        layout.addWidget(canvas)
        card.setLayout(layout)
        
        return card
    
    def create_economic_chart(self):
        """경제지표 분석 차트"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #b8daff;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout()
        
        title = QLabel("💰 경제지표 분석")
        title.setFont(QFont("Malgun Gothic", 14, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 15px;")
        
        fig = Figure(figsize=(5, 4), dpi=100)
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        
        # 경제지표 데이터
        indicators = ['금리', '환율']
        values = [
            self.input_data['interest_rate'],
            self.input_data['exchange_rate'] / 100  # 환율을 100으로 나누어 스케일 조정
        ]
        reference = [3.0, 13.0]  # 기준값
        
        x = np.arange(len(indicators))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, values, width, label='현재값', color='#007bff', alpha=0.8)
        bars2 = ax.bar(x + width/2, reference, width, label='기준값', color='#95a5a6', alpha=0.6)
        
        ax.set_title('경제지표 비교', fontsize=12, fontweight='bold', pad=20)
        ax.set_ylabel('값', fontsize=10)
        ax.set_xticks(x)
        ax.set_xticklabels(indicators)
        ax.legend()
        
        # 값 표시
        for bar, value in zip(bars1, values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                   f'{value:.1f}', ha='center', va='bottom', fontsize=9)
        
        fig.tight_layout()
        
        layout.addWidget(title)
        layout.addWidget(canvas)
        card.setLayout(layout)
        
        return card
    
    def create_price_comparison_chart(self):
        """가격 비교 차트"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #b8daff;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout()
        
        title = QLabel("💰 가격 비교 분석")
        title.setFont(QFont("Malgun Gothic", 14, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 15px;")
        
        fig = Figure(figsize=(10, 4), dpi=100)
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        
        # 가격 비교 데이터
        price_types = ['분양단가', '주변시세', '시장평균']
        prices = [
            self.input_data['avg_price_per_area'],
            self.input_data['nearby_avg_price'],
            self.input_data['nearby_avg_price'] * 1.05  # 가상의 시장평균
        ]
        
        colors = ['#007bff', '#28a745', '#ffc107']
        bars = ax.bar(price_types, prices, color=colors, alpha=0.8)
        
        ax.set_title('가격 비교 (만원/평)', fontsize=12, fontweight='bold', pad=20)
        ax.set_ylabel('가격 (만원/평)', fontsize=10)
        
        # 값 표시
        for bar, price in zip(bars, prices):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 20, 
                   f'{price:,.0f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # 가격 경쟁력 표시
        if prices[0] < prices[1]:
            competitiveness = "경쟁력 있음"
            comp_color = "green"
        elif prices[0] == prices[1]:
            competitiveness = "적정 수준"
            comp_color = "orange"
        else:
            competitiveness = "높은 가격"
            comp_color = "red"
        
        ax.text(0.5, 0.95, f"가격 경쟁력: {competitiveness}", 
                transform=ax.transAxes, ha='center', va='top',
                fontsize=12, fontweight='bold', color=comp_color)
        
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
                border: 1px solid #b8daff;
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
        
        # 위치 강점 분석
        location_strengths = []
        if self.input_data['subway_nearby']:
            location_strengths.append("지하철 역세권 (500m 이내)")
        if self.input_data['bus_stop']:
            location_strengths.append("버스 정류장 접근 용이")
        if self.input_data['road_count'] >= 2:
            location_strengths.append(f"양호한 도로 접근성 ({self.input_data['road_count']}개 접면)")
        
        if not location_strengths:
            location_strengths.append("기본적인 접근성 확보")
        
        location_group = self.create_info_group("📍 위치 강점", location_strengths)
        
        # 편의시설 분석
        convenience_items = []
        if self.input_data['elementary_school']:
            convenience_items.append("초등학교 근처")
        if self.input_data['middle_school']:
            convenience_items.append("중학교 근처")
        if self.input_data['high_school']:
            convenience_items.append("고등학교 근처")
        if self.input_data['hospital_nearby']:
            convenience_items.append("병원 이용 가능")
        if self.input_data['park_nearby']:
            convenience_items.append("공원 및 녹지 접근")
        if self.input_data['facilities_count'] > 5:
            convenience_items.append(f"풍부한 부대시설 ({self.input_data['facilities_count']}개)")
        
        if not convenience_items:
            convenience_items.append("기본적인 편의시설 확보")
        
        convenience_group = self.create_info_group("🏥 편의시설", convenience_items)
        
        # 투자 권고사항
        vacancy_rate = self.prediction_data['vacancy_rate']
        recommendations = []
        
        if vacancy_rate >= 75:
            recommendations.append("매우 안정적인 분양률 예상")
            recommendations.append("조기 분양 완료 가능성 높음")
            recommendations.append("투자 수익성 우수")
        elif vacancy_rate >= 60:
            recommendations.append("안정적인 분양률 예상")
            recommendations.append("마케팅 강화로 분양률 향상 가능")
            recommendations.append("투자 위험도 낮음")
        elif vacancy_rate >= 45:
            recommendations.append("분양 전략 수정 필요")
            recommendations.append("가격 조정 검토 권장")
            recommendations.append("신중한 투자 결정 필요")
        else:
            recommendations.append("분양 위험 높음")
            recommendations.append("근본적인 조건 개선 필요")
            recommendations.append("투자 재검토 권장")
        
        # 경제 환경 분석
        economic_analysis = []
        if self.input_data['interest_rate'] < 3.0:
            economic_analysis.append("저금리 환경으로 분양에 유리")
        elif self.input_data['interest_rate'] > 5.0:
            economic_analysis.append("고금리 환경으로 분양 부담 증가")
        else:
            economic_analysis.append("적정 수준의 금리 환경")
        
        if self.input_data['exchange_rate'] > 1400:
            economic_analysis.append("원화 약세로 해외 투자 대비 경쟁력 있음")
        elif self.input_data['exchange_rate'] < 1200:
            economic_analysis.append("원화 강세로 해외 투자 선호 가능")
        else:
            economic_analysis.append("안정적인 환율 환경")
        
        recommendation_group = self.create_info_group("💡 투자 권고", recommendations)
        economic_group = self.create_info_group("📊 경제 환경", economic_analysis)
        
        grid_layout.addWidget(location_group, 0, 0)
        grid_layout.addWidget(convenience_group, 0, 1)
        grid_layout.addWidget(recommendation_group, 1, 0)
        grid_layout.addWidget(economic_group, 1, 1)
        
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
                border: 1px solid #b8daff;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: #f8f9ff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: #2c3e50;
                background-color: #f8f9ff;
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
        'vacancy_rate': 78.5,
        'grade': '우수',
        'status': '매우 안정'
    }
    
    sample_input = {
        'district': '강남구',
        'subway_nearby': True,
        'bus_stop': True,
        'road_count': 3,
        'facilities_count': 8,
        'park_nearby': True,
        'avg_area': 84.5,
        'avg_price_per_area': 4200,
        'elementary_school': True,
        'middle_school': True,
        'high_school': False,
        'hospital_nearby': True,
        'interest_rate': 3.5,
        'exchange_rate': 1320,
        'nearby_avg_price': 4500
    }
    
    window = VacancyResultWindow(sample_prediction, sample_input, "래미안 강남")
    window.show()
    
    sys.exit(app.exec_())