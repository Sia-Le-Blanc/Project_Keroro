import sys
import pickle
import pandas as pd
import json
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
    QLineEdit, QPushButton, QScrollArea, QFrame, QGridLayout,
    QGroupBox, QMessageBox, QDesktopWidget, QShortcut, QComboBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QRect
from PyQt5.QtGui import QFont, QDoubleValidator, QKeySequence, QIcon

# 예측 결과 창 import
try:
    from prediction_result import PredictionResultWindow
    RESULT_WINDOW_AVAILABLE = True
except ImportError:
    RESULT_WINDOW_AVAILABLE = False
    print("⚠️ prediction_result.py 파일이 없습니다. 간단한 결과 메시지로 표시됩니다.")


class RiskPredictorWindow(QWidget):
    prediction_completed = pyqtSignal(str, str, str)  # 검색 기록용 시그널
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🏢 기업 부도 예측")
        
        # 창 크기 설정 (초기 크기 조정)
        self.setMinimumSize(900, 700)  # 최소 크기 증가
        self.resize(1000, 800)  # 초기 크기 증가
        
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f7fa;
                font-family: 'Malgun Gothic', Arial, sans-serif;
            }
        """)
        
        # 창 관리 관련 변수들
        self.is_fullscreen = False
        self.normal_geometry = None
        self.dragging = False
        self.drag_position = None
        self.snap_threshold = 50  # 스냅 감지 임계값 (픽셀)
        
        # 예측 로그 파일 경로
        self.log_file = "prediction_log.json"
        
        # 📌 최적화된 20개 피처 (paste.txt 파이프라인 기준)
        self.feature_groups = {
            "연체 관련 정보": [
                '연체과목수_3개월유지', '연체기관수_전체', '최장연체일수_3개월', 
                '최장연체일수_6개월', '최장연체일수_1년', '최장연체일수_3년', '연체경험'
            ],
            "재무제표 정보": [
                '유동자산', '비유동자산', '자산총계', '유동부채', '비유동부채', 
                '부채총계', '매출액', '매출총이익', '영업손익', '당기순이익', '영업활동현금흐름'
            ],
            "재무비율 정보": [
                '재무비율_부채비율', '재무비율_유동비율'
            ]
        }
        
        # 모든 피처를 하나의 리스트로 합치기
        self.features = []
        for group_features in self.feature_groups.values():
            self.features.extend(group_features)
        
        self.inputs = {}  # 입력 필드 저장
        self.company_name_input = None  # 회사명 입력 필드
        self.company_history_combo = None  # 회사 기록 콤보박스
        
        self.init_ui()
        self.center_window()
        self.setup_shortcuts()
        self.load_company_history()
    
    def init_ui(self):
        # 메인 레이아웃
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(25, 25, 25, 25)  # 여백 줄임
        main_layout.setSpacing(15)  # 간격 줄임
        
        # 헤더 영역
        header = self.create_header()
        main_layout.addWidget(header)
        
        # 회사명 입력 영역
        company_section = self.create_company_section()
        main_layout.addWidget(company_section)
        
        # 메인 카드 컨테이너
        card_container = QFrame()
        card_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e1e8ed;
                padding: 20px;
            }
        """)
        
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
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        
        # 스크롤 내용
        scroll_content = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setSpacing(20)  # 그룹 간 간격 줄임
        
        # 각 그룹별로 입력 필드 생성
        for group_name, features in self.feature_groups.items():
            group_widget = self.create_feature_group(group_name, features)
            content_layout.addWidget(group_widget)
        
        scroll_content.setLayout(content_layout)
        scroll_area.setWidget(scroll_content)
        
        # 카드 레이아웃
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.addWidget(scroll_area)
        card_container.setLayout(card_layout)
        
        # 하단 버튼 영역
        button_container = QFrame()
        button_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e1e8ed;
                padding: 15px;
            }
        """)
        
        button_layout = QHBoxLayout()
        
        # 이전 결과 불러오기 버튼
        load_btn = QPushButton("📂 이전 결과 불러오기")
        load_btn.setFixedHeight(45)
        load_btn.setFont(QFont("Malgun Gothic", 11))
        load_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 22px;
                padding: 12px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
            QPushButton:pressed {
                background-color: #d35400;
            }
        """)
        load_btn.clicked.connect(self.load_previous_result)
        
        # 초기화 버튼
        reset_btn = QPushButton("🔄 초기화")
        reset_btn.setFixedHeight(45)
        reset_btn.setFont(QFont("Malgun Gothic", 11))
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 22px;
                padding: 12px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #6c7b7d;
            }
        """)
        reset_btn.clicked.connect(self.clear_all_inputs)
        
        # Submit 버튼
        submit_btn = QPushButton("🔍 예측 실행")
        submit_btn.setFixedHeight(45)
        submit_btn.setFont(QFont("Malgun Gothic", 12, QFont.Bold))
        submit_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: none;
                border-radius: 22px;
                padding: 12px 30px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5a6fd8, stop:1 #6a4190);
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4a5bc6, stop:1 #5a3580);
                transform: translateY(0px);
            }
        """)
        submit_btn.clicked.connect(self.predict_bankruptcy)
        
        button_layout.addWidget(load_btn)
        button_layout.addWidget(reset_btn)
        button_layout.addStretch()
        button_layout.addWidget(submit_btn)
        button_container.setLayout(button_layout)
        
        # 레이아웃 구성
        main_layout.addWidget(card_container, 1)  # 확장 가능
        main_layout.addWidget(button_container, 0)  # 고정 크기
        
        self.setLayout(main_layout)
    
    def create_header(self):
        """헤더 영역 생성"""
        header = QFrame()
        # ========================================
        # 🔴 빨간 헤더 높이 조절 부분 (현재: 100px)
        # 이 값을 변경하면 헤더 높이가 조절됩니다
        # ========================================
        header.setFixedHeight(100)  # ← 여기서 헤더 높이 조절 (예: 80, 100 등)
        
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #e74c3c, stop:1 #c0392b);
                border-radius: 6px;
                padding: 8px;
            }
        """)
        
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(15, 8, 15, 8)  # 좌우 여백 증가, 상하 여백 줄임
        
        # 좌측 타이틀 영역
        title_layout = QVBoxLayout()
        title_layout.setSpacing(1)
        title_layout.setContentsMargins(5, 0, 0, 0)  # 텍스트 영역 왼쪽 여백 추가
        
        title = QLabel("🏢 기업 부도 위험 예측")
        title.setFont(QFont("Malgun Gothic", 16, QFont.Bold))
        title.setStyleSheet("color: white; margin: 0; padding: 2px 0;")  # 패딩 추가
        
        subtitle = QLabel("기업의 재무 데이터를 입력하여 부도 위험도를 분석합니다")
        subtitle.setFont(QFont("Malgun Gothic", 9))
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.85); margin: 0; padding: 1px 0;")  # 패딩 추가
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        
        # 우측 버튼 영역
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        button_layout.setAlignment(Qt.AlignRight | Qt.AlignCenter)
        button_layout.setContentsMargins(0, 0, 5, 0)  # 버튼 영역 오른쪽 여백 추가
        
        # 입력 초기화 버튼 추가
        clear_btn = QPushButton("🧹")
        clear_btn.setFixedSize(30, 30)
        clear_btn.setFont(QFont("Arial", 11))
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.15);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.25);
                border-radius: 15px;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.25);
                border: 1px solid rgba(255, 255, 255, 0.4);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.35);
            }
        """)
        clear_btn.setToolTip("모든 입력 초기화 (Ctrl+Shift+C)")
        clear_btn.clicked.connect(self.clear_all_inputs)
        
        # 도움말 버튼
        help_btn = QPushButton("❓")
        help_btn.setFixedSize(30, 30)
        help_btn.setFont(QFont("Arial", 10))
        help_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.15);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.25);
                border-radius: 15px;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.25);
                border: 1px solid rgba(255, 255, 255, 0.4);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.35);
            }
        """)
        help_btn.setToolTip("단축키 도움말")
        help_btn.clicked.connect(self.show_help)
        
        # 전체화면 토글 버튼
        fullscreen_btn = QPushButton("⛶")
        fullscreen_btn.setFixedSize(30, 30)
        fullscreen_btn.setFont(QFont("Arial", 12))
        fullscreen_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.15);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.25);
                border-radius: 15px;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.25);
                border: 1px solid rgba(255, 255, 255, 0.4);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.35);
            }
        """)
        fullscreen_btn.setToolTip("전체화면 (F11)")
        fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        
        button_layout.addWidget(clear_btn)
        button_layout.addWidget(help_btn)
        button_layout.addWidget(fullscreen_btn)
        
        # 메인 레이아웃 구성
        main_layout.addLayout(title_layout, 1)
        main_layout.addLayout(button_layout, 0)
        
        header.setLayout(main_layout)
        
        # 헤더에서 드래그 가능하도록 설정
        header.mousePressEvent = self.header_mouse_press_event
        header.mouseMoveEvent = self.header_mouse_move_event
        header.mouseReleaseEvent = self.header_mouse_release_event
        
        return header
    
    def create_company_section(self):
        """회사명 입력 섹션 생성"""
        section = QFrame()
        section.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e1e8ed;
                padding: 20px;
            }
        """)
        
        layout = QHBoxLayout()
        layout.setSpacing(15)
        
        # 회사명 라벨
        company_label = QLabel("🏢 회사명:")
        company_label.setFont(QFont("Malgun Gothic", 12, QFont.Bold))
        company_label.setStyleSheet("color: #2c3e50;")
        
        # 회사명 입력 필드
        self.company_name_input = QLineEdit()
        self.company_name_input.setPlaceholderText("분석할 회사명을 입력하세요")
        self.company_name_input.setFixedHeight(40)
        self.company_name_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #d1d9e0;
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 12px;
                color: #2c3e50;
                background-color: white;
                selection-background-color: #667eea;
            }
            QLineEdit:focus {
                border: 2px solid #667eea;
                background-color: #f8f9ff;
            }
            QLineEdit:hover {
                border: 2px solid #667eea;
            }
        """)
        
        # 이전 기록 콤보박스
        history_label = QLabel("📋 이전 기록:")
        history_label.setFont(QFont("Malgun Gothic", 11))
        history_label.setStyleSheet("color: #7f8c8d;")
        
        self.company_history_combo = QComboBox()
        self.company_history_combo.setFixedHeight(40)
        self.company_history_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #d1d9e0;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 11px;
                color: #2c3e50;
                background-color: white;
                min-width: 200px;
            }
            QComboBox:hover {
                border: 1px solid #667eea;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border: 1px solid #999;
                width: 6px;
                height: 6px;
                border-top: none;
                border-right: none;
                transform: rotate(-45deg);
                margin-right: 8px;
            }
        """)
        self.company_history_combo.currentTextChanged.connect(self.on_company_selected)
        
        layout.addWidget(company_label)
        layout.addWidget(self.company_name_input, 1)
        layout.addWidget(history_label)
        layout.addWidget(self.company_history_combo)
        
        section.setLayout(layout)
        return section
    
    def create_feature_group(self, group_name, features):
        """피처 그룹 위젯 생성"""
        group_box = QGroupBox(group_name)
        group_box.setFont(QFont("Malgun Gothic", 11, QFont.Bold))
        group_box.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #d1d9e0;
                border-radius: 10px;
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
                border-radius: 4px;
            }
        """)
        
        # 그리드 레이아웃 (2열)
        grid_layout = QGridLayout()
        grid_layout.setSpacing(12)  # 간격 줄임
        grid_layout.setContentsMargins(15, 15, 15, 15)
        
        for i, feature in enumerate(features):
            # 라벨
            label = QLabel(self.get_feature_display_name(feature))
            label.setFont(QFont("Malgun Gothic", 9))
            label.setStyleSheet("""
                QLabel {
                    color: #34495e; 
                    font-weight: normal;
                    padding: 2px 0;
                }
            """)
            label.setWordWrap(True)  # 텍스트 줄바꿈 허용
            
            # 입력 필드 (텍스트 색상 검정으로 설정)
            line_edit = QLineEdit()
            line_edit.setPlaceholderText("0")
            line_edit.setValidator(QDoubleValidator())
            line_edit.setFixedHeight(35)  # 높이 고정
            line_edit.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #d1d9e0;
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-size: 11px;
                    color: #2c3e50;
                    background-color: white;
                    selection-background-color: #667eea;
                }
                QLineEdit:focus {
                    border: 2px solid #667eea;
                    background-color: #f8f9ff;
                }
                QLineEdit:hover {
                    border: 1px solid #667eea;
                }
            """)
            
            self.inputs[feature] = line_edit
            
            # 그리드에 배치 (2열 구조)
            row = i // 2
            col = (i % 2) * 2
            
            # 라벨과 입력 필드를 수직으로 배치
            item_widget = QWidget()
            item_layout = QVBoxLayout()
            item_layout.setContentsMargins(0, 0, 0, 0)
            item_layout.setSpacing(4)
            item_layout.addWidget(label)
            item_layout.addWidget(line_edit)
            item_widget.setLayout(item_layout)
            
            grid_layout.addWidget(item_widget, row, col, 1, 2)  # 더 넓게 배치
        
        group_box.setLayout(grid_layout)
        return group_box
    
    def get_feature_display_name(self, feature):
        """피처명을 사용자 친화적으로 변환"""
        display_names = {
            '연체과목수_3개월유지': '연체 과목수 (3개월)',
            '연체기관수_전체': '연체 기관수 (전체)',
            '최장연체일수_3개월': '최장 연체일수 (3개월)',
            '최장연체일수_6개월': '최장 연체일수 (6개월)',
            '최장연체일수_1년': '최장 연체일수 (1년)',
            '최장연체일수_3년': '최장 연체일수 (3년)',
            '연체경험': '연체 경험 여부',
            '유동자산': '유동자산 (백만원)',
            '비유동자산': '비유동자산 (백만원)',
            '자산총계': '자산총계 (백만원)',
            '유동부채': '유동부채 (백만원)',
            '비유동부채': '비유동부채 (백만원)',
            '부채총계': '부채총계 (백만원)',
            '매출액': '매출액 (백만원)',
            '매출총이익': '매출총이익 (백만원)',
            '영업손익': '영업손익 (백만원)',
            '당기순이익': '당기순이익 (백만원)',
            '영업활동현금흐름': '영업활동 현금흐름 (백만원)',
            '재무비율_부채비율': '부채비율 (%)',
            '재무비율_유동비율': '유동비율 (%)'
        }
        return display_names.get(feature, feature)
    
    def center_window(self):
        """창을 화면 중앙에 배치"""
        screen = QApplication.desktop().screenGeometry()
        window = self.geometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        self.move(x, y)
    
    def load_company_history(self):
        """회사 기록 로드"""
        self.company_history_combo.clear()
        self.company_history_combo.addItem("-- 회사 선택 --")
        
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                
                companies = list(logs.keys())
                companies.sort()
                
                for company in companies:
                    last_prediction = logs[company][-1]  # 최신 기록
                    date_str = last_prediction['timestamp'][:10]  # YYYY-MM-DD
                    prob = last_prediction['prediction_result']['probability']
                    self.company_history_combo.addItem(f"{company} ({date_str}, {prob:.1%})")
                    
            except Exception as e:
                print(f"회사 기록 로드 오류: {e}")
    
    def on_company_selected(self, company_text):
        """회사 선택 시 회사명 자동 입력"""
        if company_text and company_text != "-- 회사 선택 --":
            company_name = company_text.split(" (")[0]  # 괄호 앞부분만 추출
            self.company_name_input.setText(company_name)
    
    def load_previous_result(self):
        """이전 결과 불러오기"""
        company_name = self.company_name_input.text().strip()
        
        if not company_name:
            self.show_message_box("알림", "회사명을 입력해주세요.", QMessageBox.Information, "#f39c12")
            return
        
        if not os.path.exists(self.log_file):
            self.show_message_box("알림", f"'{company_name}'의 이전 기록이 없습니다.", QMessageBox.Information, "#f39c12")
            return
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            
            if company_name not in logs:
                self.show_message_box("알림", f"'{company_name}'의 이전 기록이 없습니다.", QMessageBox.Information, "#f39c12")
                return
            
            # 최신 기록 가져오기
            latest_record = logs[company_name][-1]
            input_data = latest_record['input_data']
            prediction_result = latest_record['prediction_result']
            
            # 입력 필드에 데이터 복원
            for feature, value in input_data.items():
                if feature in self.inputs:
                    self.inputs[feature].setText(str(value))
            
            # 예측 결과 창 열기
            if RESULT_WINDOW_AVAILABLE:
                try:
                    self.result_window = PredictionResultWindow(prediction_result, input_data)
                    self.result_window.setWindowTitle(f"📊 {company_name} - 기업 부도 예측 결과 (저장된 기록)")
                    self.result_window.show()
                    
                    self.show_message_box("완료", f"'{company_name}'의 이전 기록을 불러왔습니다.", QMessageBox.Information, "#27ae60")
                    
                except Exception as e:
                    print(f"예측 결과 창 열기 오류: {e}")
                    self.show_simple_result(prediction_result, list(input_data.values()))
            else:
                self.show_simple_result(prediction_result, list(input_data.values()))
                
        except Exception as e:
            self.show_message_box("오류", f"기록 불러오기 중 오류가 발생했습니다:\n{str(e)}", QMessageBox.Critical, "#e74c3c")
    
    def save_prediction_log(self, company_name, input_data, prediction_result):
        """예측 결과 로그 저장"""
        try:
            # 기존 로그 불러오기
            logs = {}
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            
            # 새 기록 추가
            if company_name not in logs:
                logs[company_name] = []
            
            new_record = {
                'timestamp': datetime.now().isoformat(),
                'input_data': input_data,
                'prediction_result': prediction_result
            }
            
            logs[company_name].append(new_record)
            
            # 회사별 최대 10개 기록만 보관
            if len(logs[company_name]) > 10:
                logs[company_name] = logs[company_name][-10:]
            
            # 파일에 저장
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)
            
            # 콤보박스 업데이트
            self.load_company_history()
            
        except Exception as e:
            print(f"예측 로그 저장 오류: {e}")
    
    def predict_bankruptcy(self):
        """부도 예측 실행"""
        try:
            # 회사명 검증
            company_name = self.company_name_input.text().strip()
            if not company_name:
                self.show_message_box("입력 오류", "회사명을 입력해주세요.", QMessageBox.Warning, "#e74c3c")
                self.company_name_input.setFocus()
                return
            
            # 입력값 검증 및 수집
            input_values = []
            input_dict = {}  # 예측 결과 창에 전달할 딕셔너리
            
            for feature in self.features:
                text = self.inputs[feature].text().strip()
                if text == '':
                    self.show_message_box("입력 오류", f"'{self.get_feature_display_name(feature)}' 값을 입력해주세요.", QMessageBox.Warning, "#e74c3c")
                    self.inputs[feature].setFocus()
                    return
                
                try:
                    value = float(text)
                    input_values.append(value)
                    input_dict[feature] = value  # 딕셔너리에도 저장
                except ValueError:
                    self.show_message_box("입력 오류", f"'{self.get_feature_display_name(feature)}'에 올바른 숫자를 입력해주세요.", QMessageBox.Warning, "#e74c3c")
                    self.inputs[feature].setFocus()
                    return
            
            # 예측 실행 (실제 모델 로드 필요)
            # TODO: paste.txt의 BankruptcyPredictionPipeline 사용
            
            # 임시 예측 결과
            prediction_result = self.mock_prediction(input_values)
            
            # 로그 저장
            self.save_prediction_log(company_name, input_dict, prediction_result)
            
            # 검색 기록에 추가
            self.prediction_completed.emit(
                "기업", 
                company_name, 
                f"부도확률: {prediction_result['probability']:.2%}"
            )
            
            # 예측 결과 창 열기
            if RESULT_WINDOW_AVAILABLE:
                try:
                    # 새로운 예측 결과 창 열기
                    self.result_window = PredictionResultWindow(prediction_result, input_dict)
                    self.result_window.setWindowTitle(f"📊 {company_name} - 기업 부도 예측 결과")
                    self.result_window.show()
                    
                    # 간단한 성공 메시지
                    self.show_message_box("✅ 예측 완료", f"'{company_name}' 예측이 완료되었습니다!\n\n상세한 결과는 새 창에서 확인하세요.", QMessageBox.Information, "#27ae60")
                    
                except Exception as e:
                    print(f"예측 결과 창 열기 오류: {e}")
                    # 오류 시 기존 방식으로 표시
                    self.show_simple_result(prediction_result, input_values)
            else:
                # prediction_result.py가 없을 때 기존 방식
                self.show_simple_result(prediction_result, input_values)
            
        except Exception as e:
            self.show_message_box("예측 오류", f"예측 중 오류가 발생했습니다:\n{str(e)}", QMessageBox.Critical, "#c0392b")
    
    def show_simple_result(self, prediction_result, input_values):
        """간단한 결과 표시 (예측 결과 창이 없을 때)"""
        risk_emoji = "🚨" if prediction_result['probability'] > 0.5 else "✅"
        
        result_msg = f"""
{risk_emoji} 예측이 완료되었습니다!

📊 예측 결과:
• 부도 확률: {prediction_result['probability']:.1%}
• 위험도: {prediction_result['risk_level']}
• 결과: {'⚠️ 부도 위험' if prediction_result['prediction'] else '✅ 안정'}

📈 분석 기준:
• 주요 판단 요소: 부채비율 {input_values[-2]:.1f}%
• 기준 임계값: 50% (부도 확률)

💡 참고사항:
이 결과는 입력하신 재무 데이터를 바탕으로 한 
예측 결과이며, 실제 결과와 다를 수 있습니다.

⚠️ prediction_result.py 파일을 생성하면
더 상세한 분석 결과를 확인할 수 있습니다.
        """
        
        button_color = "#e74c3c" if prediction_result['probability'] > 0.5 else "#27ae60"
        self.show_message_box(f"{risk_emoji} 예측 완료", result_msg.strip(), QMessageBox.Information, button_color)
    
    def show_message_box(self, title, message, icon, button_color):
        """스타일이 적용된 메시지 박스 표시"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(icon)
        
        button_hover = {
            "#e74c3c": "#c0392b",
            "#27ae60": "#219a52", 
            "#3498db": "#2980b9",
            "#f39c12": "#e67e22",
            "#c0392b": "#a93226"
        }.get(button_color, "#2980b9")
        
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: white;
                color: black;
            }}
            QMessageBox QLabel {{
                color: black;
                font-family: 'Malgun Gothic', Arial, sans-serif;
                font-size: 11px;
                line-height: 1.4;
            }}
            QMessageBox QPushButton {{
                background-color: {button_color};
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: {button_hover};
            }}
        """)
        msg_box.exec_()
    
    def mock_prediction(self, input_values):
        """임시 예측 결과 생성 (실제 모델 연결 전까지)"""
        # 간단한 규칙 기반 예측
        debt_ratio = input_values[-2] if len(input_values) >= 2 else 50  # 부채비율
        
        if debt_ratio > 80:
            probability = 0.75
            risk_level = "매우 높음"
        elif debt_ratio > 60:
            probability = 0.45
            risk_level = "높음"
        elif debt_ratio > 40:
            probability = 0.25
            risk_level = "보통"
        else:
            probability = 0.1
            risk_level = "낮음"
        
        return {
            "probability": probability,
            "risk_level": risk_level,
            "prediction": probability > 0.5
        }
    
    def clear_all_inputs(self):
        """모든 입력 필드 초기화"""
        # 실제로 입력된 필드가 있는지 확인
        has_input = any(line_edit.text().strip() for line_edit in self.inputs.values()) or self.company_name_input.text().strip()
        
        if has_input:
            # 확인 대화상자
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("입력 초기화 확인")
            msg_box.setText("모든 입력 내용을 초기화하시겠습니까?")
            msg_box.setIcon(QMessageBox.Question)
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg_box.setDefaultButton(QMessageBox.No)
            
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                    color: black;
                }
                QMessageBox QLabel {
                    color: black;
                    font-family: 'Malgun Gothic', Arial, sans-serif;
                    font-size: 12px;
                }
                QMessageBox QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    padding: 8px 20px;
                    border-radius: 4px;
                    font-weight: bold;
                    min-width: 80px;
                }
                QMessageBox QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            
            reply = msg_box.exec_()
            
            if reply == QMessageBox.Yes:
                # 모든 입력 필드 초기화
                for line_edit in self.inputs.values():
                    line_edit.clear()
                self.company_name_input.clear()
                
                self.show_message_box("완료", "모든 입력이 초기화되었습니다.", QMessageBox.Information, "#27ae60")
        else:
            self.show_message_box("알림", "초기화할 입력 내용이 없습니다.", QMessageBox.Information, "#f39c12")
    
    def setup_shortcuts(self):
        """키보드 단축키 설정"""
        # F11: 전체화면 토글
        fullscreen_shortcut = QShortcut(QKeySequence("F11"), self)
        fullscreen_shortcut.activated.connect(self.toggle_fullscreen)
        
        # Ctrl+0: 창 크기 초기화
        reset_size_shortcut = QShortcut(QKeySequence("Ctrl+0"), self)
        reset_size_shortcut.activated.connect(self.reset_window_size)
        
        # Ctrl+Shift+C: 모든 입력 초기화
        clear_shortcut = QShortcut(QKeySequence("Ctrl+Shift+C"), self)
        clear_shortcut.activated.connect(self.clear_all_inputs)
        
        # Esc: 전체화면에서 일반 모드로
        escape_shortcut = QShortcut(QKeySequence("Escape"), self)
        escape_shortcut.activated.connect(self.exit_fullscreen)
    
    def toggle_fullscreen(self):
        """전체화면 토글"""
        if self.is_fullscreen:
            self.exit_fullscreen()
        else:
            self.enter_fullscreen()
    
    def enter_fullscreen(self):
        """전체화면 모드 진입"""
        if not self.is_fullscreen:
            self.normal_geometry = self.geometry()
            self.showFullScreen()
            self.is_fullscreen = True
    
    def exit_fullscreen(self):
        """전체화면 모드 종료"""
        if self.is_fullscreen:
            self.showNormal()
            if self.normal_geometry:
                self.setGeometry(self.normal_geometry)
            self.is_fullscreen = False
    
    def reset_window_size(self):
        """창 크기 초기화"""
        if not self.is_fullscreen:
            self.resize(1000, 800)  # 업데이트된 기본 크기
            self.center_window()
    
    def show_help(self):
        """단축키 도움말 표시"""
        help_text = """
🎯 창 관리 단축키

🖥️ F11              : 전체화면 토글
🔄 Ctrl+0           : 창 크기 초기화 (1000x800)
🧹 Ctrl+Shift+C     : 모든 입력 초기화
⚡ Esc              : 전체화면 종료

🖱️ 마우스 조작

• 빨간색 헤더를 드래그하여 창 이동
• 창을 화면 가장자리로 드래그하면 스냅 기능 활성화
  - 좌측 가장자리: 화면 왼쪽 절반
  - 우측 가장자리: 화면 오른쪽 절반  
  - 상단 가장자리: 전체화면
• 창 모서리를 드래그하여 크기 조절

📝 입력 팁

• 회사명을 먼저 입력하세요
• 숫자만 입력 가능 (소수점 포함)
• 빈 칸이 있으면 예측이 실행되지 않습니다
• 📂 버튼으로 이전 예측 결과를 불러올 수 있습니다
• 🧹 버튼으로 한 번에 모든 입력을 초기화할 수 있습니다

💾 로그 기능

• 회사별로 예측 결과가 자동 저장됩니다
• 최대 10개까지 기록이 보관됩니다
• 콤보박스에서 이전 기록을 선택할 수 있습니다
        """
        
        self.show_message_box("🎯 도움말", help_text.strip(), QMessageBox.Information, "#3498db")
    
    def header_mouse_press_event(self, event):
        """헤더 마우스 눌림 이벤트"""
        if event.button() == Qt.LeftButton and not self.is_fullscreen:
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def header_mouse_move_event(self, event):
        """헤더 마우스 이동 이벤트"""
        if event.buttons() == Qt.LeftButton and self.dragging and not self.is_fullscreen:
            new_pos = event.globalPos() - self.drag_position
            self.move(new_pos)
            
            # 스냅 기능 확인
            self.check_snap_position(event.globalPos())
            event.accept()
    
    def header_mouse_release_event(self, event):
        """헤더 마우스 해제 이벤트"""
        if event.button() == Qt.LeftButton:
            self.dragging = False
            
            # 스냅 적용
            if not self.is_fullscreen:
                self.apply_snap_if_needed(event.globalPos())
            event.accept()
    
    def check_snap_position(self, global_pos):
        """스냅 위치 확인 (시각적 피드백 추가 가능)"""
        screen = QApplication.desktop().screenGeometry()
        
        # 화면 경계 근처인지 확인
        near_left = global_pos.x() < self.snap_threshold
        near_right = global_pos.x() > screen.width() - self.snap_threshold
        near_top = global_pos.y() < self.snap_threshold
        
        # 향후 시각적 가이드 표시 가능
        pass
    
    def apply_snap_if_needed(self, global_pos):
        """필요시 스냅 적용"""
        screen = QApplication.desktop().availableGeometry()
        
        # 좌측 스냅
        if global_pos.x() < self.snap_threshold:
            self.setGeometry(
                screen.x(),
                screen.y(),
                screen.width() // 2,
                screen.height()
            )
        # 우측 스냅
        elif global_pos.x() > screen.width() - self.snap_threshold:
            self.setGeometry(
                screen.x() + screen.width() // 2,
                screen.y(),
                screen.width() // 2,
                screen.height()
            )
        # 상단 스냅 (전체화면)
        elif global_pos.y() < self.snap_threshold:
            self.enter_fullscreen()
    
    def keyPressEvent(self, event):
        """키보드 이벤트 처리"""
        # 추가적인 키보드 이벤트 처리
        super().keyPressEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RiskPredictorWindow()
    window.show()
    sys.exit(app.exec_())