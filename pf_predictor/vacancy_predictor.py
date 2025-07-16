import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
    QLineEdit, QPushButton, QFrame, QMessageBox, QDesktopWidget, 
    QShortcut, QComboBox, QCheckBox, QGridLayout, QGroupBox, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QDoubleValidator, QKeySequence, QIntValidator

# 예측 결과 창 import
try:
    from vacancy_result import VacancyResultWindow
    RESULT_WINDOW_AVAILABLE = True
except ImportError:
    RESULT_WINDOW_AVAILABLE = False
    print("⚠️ vacancy_result.py 파일이 없습니다. 간단한 결과 메시지로 표시됩니다.")


class VacancyPredictorWindow(QWidget):
    prediction_completed = pyqtSignal(str, str, str)  # 검색 기록용 시그널
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🏠 부동산 분양률 예측")
        
        # 창 크기 설정 (더 큰 크기로 조정)
        self.setMinimumSize(1000, 800)
        self.resize(1200, 900)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f8ff;
                font-family: 'Malgun Gothic', Arial, sans-serif;
            }
        """)
        
        # 창 관리 관련 변수들
        self.is_fullscreen = False
        self.normal_geometry = None
        self.dragging = False
        self.drag_position = None
        self.snap_threshold = 50
        
        # 입력 필드들을 저장할 딕셔너리
        self.inputs = {}
        
        self.init_ui()
        self.center_window()
        self.setup_shortcuts()
    
    def init_ui(self):
        # 메인 레이아웃
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)
        
        # 헤더 영역
        header = self.create_header()
        main_layout.addWidget(header)
        
        # 프로젝트명 입력 섹션
        project_section = self.create_project_section()
        main_layout.addWidget(project_section)
        
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
        
        # 각 그룹별 입력 필드 생성
        input_groups = [
            ("📍 위치 정보", self.create_location_group()),
            ("🏢 건물 정보", self.create_building_group()),
            ("🏫 교육 시설", self.create_education_group()),
            ("🏥 생활 편의", self.create_convenience_group()),
            ("💰 경제 지표", self.create_economic_group()),
            ("🏠 부동산 정보", self.create_property_group())
        ]
        
        for group_title, group_widget in input_groups:
            content_layout.addWidget(group_widget)
        
        scroll_content.setLayout(content_layout)
        scroll_area.setWidget(scroll_content)
        
        # 버튼 영역
        button_frame = self.create_button_frame()
        
        # 레이아웃 구성
        main_layout.addWidget(scroll_area, 1)
        main_layout.addWidget(button_frame, 0)
        
        self.setLayout(main_layout)
    
    def create_header(self):
        """헤더 영역 생성"""
        header = QFrame()
        header.setFixedHeight(90)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #007bff, stop:1 #0056b3);
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(20, 10, 20, 10)
        
        # 좌측 타이틀 영역
        title_layout = QVBoxLayout()
        title_layout.setSpacing(3)
        
        title = QLabel("🏠 부동산 분양률 예측")
        title.setFont(QFont("Malgun Gothic", 17, QFont.Bold))
        title.setStyleSheet("color: white; margin: 0; padding: 3px 0;")
        
        subtitle = QLabel("상세한 입지 조건을 분석하여 분양률을 예측합니다")
        subtitle.setFont(QFont("Malgun Gothic", 10))
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.9); margin: 0; padding: 2px 0;")
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        
        # 우측 버튼 영역
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setAlignment(Qt.AlignRight | Qt.AlignCenter)
        
        # 버튼들
        buttons = [
            ("🧹", "모든 입력 초기화 (Ctrl+Shift+C)", self.clear_inputs),
            ("❓", "단축키 도움말", self.show_help),
            ("⛶", "전체화면 (F11)", self.toggle_fullscreen)
        ]
        
        for text, tooltip, func in buttons:
            btn = QPushButton(text)
            btn.setFixedSize(32, 32)
            btn.setFont(QFont("Arial", 12))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.15);
                    color: white;
                    border: 1px solid rgba(255, 255, 255, 0.25);
                    border-radius: 16px;
                    margin: 2px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.25);
                    border: 1px solid rgba(255, 255, 255, 0.4);
                }
            """)
            btn.setToolTip(tooltip)
            btn.clicked.connect(func)
            button_layout.addWidget(btn)
        
        # 메인 레이아웃 구성
        main_layout.addLayout(title_layout, 1)
        main_layout.addLayout(button_layout, 0)
        
        header.setLayout(main_layout)
        
        # 헤더 드래그 이벤트
        header.mousePressEvent = self.header_mouse_press_event
        header.mouseMoveEvent = self.header_mouse_move_event
        header.mouseReleaseEvent = self.header_mouse_release_event
        
        return header
    
    def create_project_section(self):
        """프로젝트명 입력 섹션"""
        section = QFrame()
        section.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #b8daff;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # 프로젝트명 라벨
        project_label = QLabel("🏠 프로젝트명:")
        project_label.setFont(QFont("Malgun Gothic", 13, QFont.Bold))
        project_label.setStyleSheet("color: #2c3e50; margin-bottom: 8px;")
        
        # 프로젝트명 입력 필드
        self.project_input = QLineEdit()
        self.project_input.setPlaceholderText("아파트 단지명을 입력하세요 (예: 래미안 강남)")
        self.project_input.setFixedHeight(45)
        self.project_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #b8daff;
                border-radius: 8px;
                padding: 12px 15px;
                font-size: 13px;
                color: #2c3e50;
                background-color: white;
                selection-background-color: #007bff;
            }
            QLineEdit:focus {
                border: 2px solid #007bff;
                background-color: #f8f9ff;
            }
        """)
        
        layout.addWidget(project_label)
        layout.addWidget(self.project_input)
        section.setLayout(layout)
        
        return section
    
    def create_location_group(self):
        """위치 정보 그룹"""
        group = self.create_group_box("📍 위치 정보")
        layout = QGridLayout()
        layout.setSpacing(15)
        
        # 시군구 선택
        layout.addWidget(QLabel("시군구:"), 0, 0)
        self.inputs['district'] = QComboBox()
        self.inputs['district'].addItems([
            "강남구", "강동구", "강북구", "강서구", "관악구", "광진구", "구로구", "금천구",
            "노원구", "도봉구", "동대문구", "동작구", "마포구", "서대문구", "서초구",
            "성동구", "성북구", "송파구", "양천구", "영등포구", "용산구", "은평구",
            "종로구", "중구", "중랑구"
        ])
        self.inputs['district'].setFixedHeight(35)
        self.inputs['district'].setStyleSheet(self.get_combo_style())
        layout.addWidget(self.inputs['district'], 0, 1)
        
        # 역세권 (500m 이내)
        layout.addWidget(QLabel("역세권 (500m 이내):"), 0, 2)
        self.inputs['subway_nearby'] = QCheckBox("지하철역 있음")
        self.inputs['subway_nearby'].setStyleSheet(self.get_checkbox_style())
        layout.addWidget(self.inputs['subway_nearby'], 0, 3)
        
        # 버스정류장 유무
        layout.addWidget(QLabel("버스정류장:"), 1, 0)
        self.inputs['bus_stop'] = QCheckBox("버스정류장 있음")
        self.inputs['bus_stop'].setStyleSheet(self.get_checkbox_style())
        layout.addWidget(self.inputs['bus_stop'], 1, 1)
        
        # 접면도로 수
        layout.addWidget(QLabel("접면도로 수:"), 1, 2)
        self.inputs['road_count'] = QLineEdit()
        self.inputs['road_count'].setPlaceholderText("개")
        self.inputs['road_count'].setValidator(QIntValidator(1, 10))
        self.inputs['road_count'].setFixedHeight(35)
        self.inputs['road_count'].setStyleSheet(self.get_input_style())
        layout.addWidget(self.inputs['road_count'], 1, 3)
        
        group.setLayout(layout)
        return group
    
    def create_building_group(self):
        """건물 정보 그룹"""
        group = self.create_group_box("🏢 건물 정보")
        layout = QGridLayout()
        layout.setSpacing(15)
        
        # 부대시설 수
        layout.addWidget(QLabel("부대시설 수:"), 0, 0)
        self.inputs['facilities_count'] = QLineEdit()
        self.inputs['facilities_count'].setPlaceholderText("개")
        self.inputs['facilities_count'].setValidator(QIntValidator(0, 50))
        self.inputs['facilities_count'].setFixedHeight(35)
        self.inputs['facilities_count'].setStyleSheet(self.get_input_style())
        layout.addWidget(self.inputs['facilities_count'], 0, 1)
        
        # 공원 유무
        layout.addWidget(QLabel("공원 (500m 이내):"), 0, 2)
        self.inputs['park_nearby'] = QCheckBox("공원 있음")
        self.inputs['park_nearby'].setStyleSheet(self.get_checkbox_style())
        layout.addWidget(self.inputs['park_nearby'], 0, 3)
        
        # 평균 분양면적
        layout.addWidget(QLabel("평균 분양면적:"), 1, 0)
        self.inputs['avg_area'] = QLineEdit()
        self.inputs['avg_area'].setPlaceholderText("평")
        self.inputs['avg_area'].setValidator(QDoubleValidator(10.0, 200.0, 1))
        self.inputs['avg_area'].setFixedHeight(35)
        self.inputs['avg_area'].setStyleSheet(self.get_input_style())
        layout.addWidget(self.inputs['avg_area'], 1, 1)
        
        # 평균 분양단가
        layout.addWidget(QLabel("평균 분양단가:"), 1, 2)
        self.inputs['avg_price_per_area'] = QLineEdit()
        self.inputs['avg_price_per_area'].setPlaceholderText("만원/평")
        self.inputs['avg_price_per_area'].setValidator(QDoubleValidator(1000.0, 20000.0, 0))
        self.inputs['avg_price_per_area'].setFixedHeight(35)
        self.inputs['avg_price_per_area'].setStyleSheet(self.get_input_style())
        layout.addWidget(self.inputs['avg_price_per_area'], 1, 3)
        
        group.setLayout(layout)
        return group
    
    def create_education_group(self):
        """교육 시설 그룹"""
        group = self.create_group_box("🏫 교육 시설")
        layout = QGridLayout()
        layout.setSpacing(15)
        
        # 학교 유무 체크박스들
        schools = [
            ("초등학교", "elementary_school"),
            ("중학교", "middle_school"),
            ("고등학교", "high_school")
        ]
        
        for i, (name, key) in enumerate(schools):
            layout.addWidget(QLabel(f"{name} (500m 이내):"), 0, i*2)
            self.inputs[key] = QCheckBox(f"{name} 있음")
            self.inputs[key].setStyleSheet(self.get_checkbox_style())
            layout.addWidget(self.inputs[key], 0, i*2+1)
        
        group.setLayout(layout)
        return group
    
    def create_convenience_group(self):
        """생활 편의 그룹"""
        group = self.create_group_box("🏥 생활 편의")
        layout = QGridLayout()
        layout.setSpacing(15)
        
        # 병원 유무
        layout.addWidget(QLabel("병원 (500m 이내):"), 0, 0)
        self.inputs['hospital_nearby'] = QCheckBox("병원 있음")
        self.inputs['hospital_nearby'].setStyleSheet(self.get_checkbox_style())
        layout.addWidget(self.inputs['hospital_nearby'], 0, 1)
        
        group.setLayout(layout)
        return group
    
    def create_economic_group(self):
        """경제 지표 그룹"""
        group = self.create_group_box("💰 경제 지표")
        layout = QGridLayout()
        layout.setSpacing(15)
        
        # 해당시점 금리
        layout.addWidget(QLabel("해당시점 금리:"), 0, 0)
        self.inputs['interest_rate'] = QLineEdit()
        self.inputs['interest_rate'].setPlaceholderText("% (예: 3.5)")
        self.inputs['interest_rate'].setValidator(QDoubleValidator(0.0, 20.0, 2))
        self.inputs['interest_rate'].setFixedHeight(35)
        self.inputs['interest_rate'].setStyleSheet(self.get_input_style())
        layout.addWidget(self.inputs['interest_rate'], 0, 1)
        
        # 해당시점 환율
        layout.addWidget(QLabel("해당시점 환율:"), 0, 2)
        self.inputs['exchange_rate'] = QLineEdit()
        self.inputs['exchange_rate'].setPlaceholderText("원 (예: 1350)")
        self.inputs['exchange_rate'].setValidator(QDoubleValidator(1000.0, 2000.0, 0))
        self.inputs['exchange_rate'].setFixedHeight(35)
        self.inputs['exchange_rate'].setStyleSheet(self.get_input_style())
        layout.addWidget(self.inputs['exchange_rate'], 0, 3)
        
        group.setLayout(layout)
        return group
    
    def create_property_group(self):
        """부동산 정보 그룹"""
        group = self.create_group_box("🏠 부동산 정보")
        layout = QGridLayout()
        layout.setSpacing(15)
        
        # 주변시세 평균
        layout.addWidget(QLabel("주변시세 평균:"), 0, 0)
        self.inputs['nearby_avg_price'] = QLineEdit()
        self.inputs['nearby_avg_price'].setPlaceholderText("만원/평")
        self.inputs['nearby_avg_price'].setValidator(QDoubleValidator(1000.0, 20000.0, 0))
        self.inputs['nearby_avg_price'].setFixedHeight(35)
        self.inputs['nearby_avg_price'].setStyleSheet(self.get_input_style())
        layout.addWidget(self.inputs['nearby_avg_price'], 0, 1)
        
        group.setLayout(layout)
        return group
    
    def create_group_box(self, title):
        """그룹박스 생성"""
        group = QGroupBox(title)
        group.setFont(QFont("Malgun Gothic", 12, QFont.Bold))
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #b8daff;
                border-radius: 10px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: #2c3e50;
                background-color: white;
            }
        """)
        return group
    
    def create_button_frame(self):
        """버튼 프레임 생성"""
        button_frame = QFrame()
        button_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #b8daff;
                padding: 15px;
            }
        """)
        
        button_layout = QHBoxLayout()
        
        # 초기화 버튼
        clear_btn = QPushButton("🔄 초기화")
        clear_btn.setFixedHeight(50)
        clear_btn.setFont(QFont("Malgun Gothic", 11, QFont.Bold))
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 25px;
                padding: 15px 25px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        clear_btn.clicked.connect(self.clear_inputs)
        
        # 예측 버튼
        predict_btn = QPushButton("📈 분양률 예측")
        predict_btn.setFixedHeight(50)
        predict_btn.setFont(QFont("Malgun Gothic", 12, QFont.Bold))
        predict_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #007bff, stop:1 #0056b3);
                color: white;
                border: none;
                border-radius: 25px;
                padding: 15px 35px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0056b3, stop:1 #004085);
            }
        """)
        predict_btn.clicked.connect(self.predict_vacancy)
        
        button_layout.addWidget(clear_btn)
        button_layout.addStretch()
        button_layout.addWidget(predict_btn)
        
        button_frame.setLayout(button_layout)
        return button_frame
    
    def get_input_style(self):
        """입력 필드 스타일"""
        return """
            QLineEdit {
                border: 1px solid #b8daff;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
                color: #2c3e50;
                background-color: white;
                selection-background-color: #007bff;
            }
            QLineEdit:focus {
                border: 2px solid #007bff;
                background-color: #f8f9ff;
            }
        """
    
    def get_combo_style(self):
        """콤보박스 스타일"""
        return """
            QComboBox {
                border: 1px solid #b8daff;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
                color: #2c3e50;
                background-color: white;
                min-width: 120px;
            }
            QComboBox:focus {
                border: 2px solid #007bff;
            }
        """
    
    def get_checkbox_style(self):
        """체크박스 스타일"""
        return """
            QCheckBox {
                font-size: 12px;
                color: #2c3e50;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #b8daff;
                border-radius: 3px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #007bff;
                border: 2px solid #007bff;
            }
        """
    
    def center_window(self):
        """창을 화면 중앙에 배치"""
        screen = QApplication.desktop().screenGeometry()
        window = self.geometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        self.move(x, y)
    
    def setup_shortcuts(self):
        """키보드 단축키 설정"""
        shortcuts = [
            ("F11", self.toggle_fullscreen),
            ("Ctrl+0", self.reset_window_size),
            ("Ctrl+Shift+C", self.clear_inputs),
            ("Escape", self.exit_fullscreen)
        ]
        
        for key, func in shortcuts:
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.activated.connect(func)
    
    def toggle_fullscreen(self):
        """전체화면 토글"""
        if self.is_fullscreen:
            self.exit_fullscreen()
        else:
            self.enter_fullscreen()
    
    def enter_fullscreen(self):
        """전체화면 진입"""
        if not self.is_fullscreen:
            self.normal_geometry = self.geometry()
            self.showFullScreen()
            self.is_fullscreen = True
    
    def exit_fullscreen(self):
        """전체화면 종료"""
        if self.is_fullscreen:
            self.showNormal()
            if self.normal_geometry:
                self.setGeometry(self.normal_geometry)
            self.is_fullscreen = False
    
    def reset_window_size(self):
        """창 크기 초기화"""
        if not self.is_fullscreen:
            self.resize(1200, 900)
            self.center_window()
    
    def show_help(self):
        """도움말 표시"""
        help_text = """
🎯 부동산 분양률 예측 도움말

📝 입력 항목:
• 위치 정보: 시군구, 역세권, 버스정류장, 접면도로 수
• 건물 정보: 부대시설, 공원, 분양면적, 분양단가
• 교육 시설: 초중고등학교 유무
• 생활 편의: 병원 유무
• 경제 지표: 금리, 환율
• 부동산 정보: 주변시세

🖥️ 단축키:
• F11: 전체화면 토글
• Ctrl+0: 창 크기 초기화
• Ctrl+Shift+C: 모든 입력 초기화
• Esc: 전체화면 종료

💡 분양률 예측 기준:
• 75% 이상: 매우 안정적
• 60-75%: 안정적
• 45-60%: 주의 필요
• 45% 미만: 위험
        """
        
        self.show_message_box("🎯 도움말", help_text.strip(), QMessageBox.Information, "#007bff")
    
    def header_mouse_press_event(self, event):
        """헤더 마우스 이벤트"""
        if event.button() == Qt.LeftButton and not self.is_fullscreen:
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
    
    def header_mouse_move_event(self, event):
        """헤더 마우스 이동"""
        if event.buttons() == Qt.LeftButton and self.dragging and not self.is_fullscreen:
            self.move(event.globalPos() - self.drag_position)
    
    def header_mouse_release_event(self, event):
        """헤더 마우스 해제"""
        self.dragging = False
    
    def clear_inputs(self):
        """모든 입력 초기화"""
        # 입력 내용 확인
        has_input = (self.project_input.text().strip() or
                    any(isinstance(widget, QLineEdit) and widget.text().strip() 
                        for widget in self.inputs.values()) or
                    any(isinstance(widget, QCheckBox) and widget.isChecked() 
                        for widget in self.inputs.values()))
        
        if has_input:
            reply = QMessageBox.question(self, "입력 초기화 확인", 
                                       "모든 입력 내용을 초기화하시겠습니까?",
                                       QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                # 프로젝트명 초기화
                self.project_input.clear()
                
                # 모든 입력 위젯 초기화
                for widget in self.inputs.values():
                    if isinstance(widget, QLineEdit):
                        widget.clear()
                    elif isinstance(widget, QCheckBox):
                        widget.setChecked(False)
                    elif isinstance(widget, QComboBox):
                        widget.setCurrentIndex(0)
                
                self.show_message_box("완료", "모든 입력이 초기화되었습니다.", 
                                    QMessageBox.Information, "#28a745")
        else:
            self.show_message_box("알림", "초기화할 입력 내용이 없습니다.", 
                                QMessageBox.Information, "#17a2b8")
    
    def predict_vacancy(self):
        """분양률 예측 실행"""
        try:
            # 프로젝트명 검증
            project_name = self.project_input.text().strip()
            if not project_name:
                self.show_error("프로젝트명을 입력해주세요.")
                self.project_input.setFocus()
                return
            
            # 입력값 수집 및 검증
            input_data = self.collect_input_data()
            
            if not self.validate_input_data(input_data):
                return
            
            # 분양률 계산
            vacancy_rate = self.calculate_vacancy_rate(input_data)
            
            # 등급 및 상태 결정
            grade, status = self.determine_grade_and_status(vacancy_rate)
            
            # 예측 결과 데이터 구성
            prediction_data = {
                'vacancy_rate': vacancy_rate,
                'grade': grade,
                'status': status
            }
            
            # 검색 기록에 추가
            self.prediction_completed.emit("부동산", project_name, f"분양률: {vacancy_rate:.1f}%")
            
            # 예측 결과 창 열기
            if RESULT_WINDOW_AVAILABLE:
                try:
                    self.result_window = VacancyResultWindow(prediction_data, input_data, project_name)
                    self.result_window.show()
                    
                    self.show_message_box("✅ 예측 완료", 
                                        f"'{project_name}' 분양률 예측이 완료되었습니다!\n\n상세한 결과는 새 창에서 확인하세요.",
                                        QMessageBox.Information, "#28a745")
                except Exception as e:
                    print(f"예측 결과 창 열기 오류: {e}")
                    self.show_simple_result(project_name, vacancy_rate, grade, status)
            else:
                self.show_simple_result(project_name, vacancy_rate, grade, status)
                
        except Exception as e:
            self.show_message_box("예측 오류", f"예측 중 오류가 발생했습니다:\n{str(e)}", 
                                QMessageBox.Critical, "#dc3545")
    
    def collect_input_data(self):
        """입력 데이터 수집"""
        input_data = {}
        
        # 텍스트 입력값들
        text_inputs = [
            'road_count', 'facilities_count', 'avg_area', 'avg_price_per_area',
            'interest_rate', 'exchange_rate', 'nearby_avg_price'
        ]
        
        for key in text_inputs:
            value = self.inputs[key].text().strip()
            input_data[key] = float(value) if value else 0.0
        
        # 체크박스 값들
        checkbox_inputs = [
            'subway_nearby', 'bus_stop', 'park_nearby', 'elementary_school',
            'middle_school', 'high_school', 'hospital_nearby'
        ]
        
        for key in checkbox_inputs:
            input_data[key] = self.inputs[key].isChecked()
        
        # 콤보박스 값
        input_data['district'] = self.inputs['district'].currentText()
        
        return input_data
    
    def validate_input_data(self, input_data):
        """입력 데이터 검증"""
        required_fields = [
            ('road_count', '접면도로 수'),
            ('facilities_count', '부대시설 수'),
            ('avg_area', '평균 분양면적'),
            ('avg_price_per_area', '평균 분양단가'),
            ('interest_rate', '해당시점 금리'),
            ('exchange_rate', '해당시점 환율'),
            ('nearby_avg_price', '주변시세 평균')
        ]
        
        for key, name in required_fields:
            if input_data[key] == 0.0:
                self.show_error(f"'{name}' 값을 입력해주세요.")
                if key in self.inputs:
                    self.inputs[key].setFocus()
                return False
        
        return True
    
    def calculate_vacancy_rate(self, data):
        """분양률 계산"""
        # 기본 점수 계산
        base_score = 50.0
        
        # 위치 점수 (최대 20점)
        location_score = 0
        if data['subway_nearby']: location_score += 8
        if data['bus_stop']: location_score += 4
        location_score += min(data['road_count'] * 2, 8)
        
        # 편의시설 점수 (최대 15점)
        convenience_score = 0
        if data['park_nearby']: convenience_score += 3
        if data['hospital_nearby']: convenience_score += 4
        convenience_score += min(data['facilities_count'] * 0.5, 8)
        
        # 교육시설 점수 (최대 10점)
        education_score = 0
        if data['elementary_school']: education_score += 4
        if data['middle_school']: education_score += 3
        if data['high_school']: education_score += 3
        
        # 가격 경쟁력 점수 (최대 10점)
        price_competitiveness = 0
        if data['nearby_avg_price'] > 0:
            price_ratio = data['avg_price_per_area'] / data['nearby_avg_price']
            if price_ratio < 0.9:
                price_competitiveness = 10
            elif price_ratio < 1.0:
                price_competitiveness = 8
            elif price_ratio < 1.1:
                price_competitiveness = 6
            elif price_ratio < 1.2:
                price_competitiveness = 4
            else:
                price_competitiveness = 2
        
        # 경제 지표 조정 (최대 -5점 ~ +5점)
        economic_adjustment = 0
        if data['interest_rate'] < 2.0:
            economic_adjustment += 3
        elif data['interest_rate'] < 3.0:
            economic_adjustment += 1
        elif data['interest_rate'] > 5.0:
            economic_adjustment -= 3
        elif data['interest_rate'] > 4.0:
            economic_adjustment -= 1
        
        # 최종 점수 계산
        total_score = (base_score + location_score + convenience_score + 
                      education_score + price_competitiveness + economic_adjustment)
        
        # 분양률로 변환 (30-95% 범위)
        vacancy_rate = min(max(total_score * 0.9, 30), 95)
        
        return vacancy_rate
    
    def determine_grade_and_status(self, vacancy_rate):
        """등급 및 상태 결정"""
        if vacancy_rate >= 75:
            return "우수", "매우 안정"
        elif vacancy_rate >= 60:
            return "양호", "안정"
        elif vacancy_rate >= 45:
            return "보통", "주의"
        else:
            return "미흡", "위험"
    
    def show_simple_result(self, project_name, vacancy_rate, grade, status):
        """간단한 결과 표시"""
        emoji = "✅" if vacancy_rate >= 60 else "⚠️" if vacancy_rate >= 45 else "🚨"
        color = "#28a745" if vacancy_rate >= 60 else "#ffc107" if vacancy_rate >= 45 else "#dc3545"
        
        result_msg = f"""
{emoji} {project_name} 분양률 예측 완료!

📊 예측 결과:
• 예상 분양률: {vacancy_rate:.1f}%
• 등급: {grade}
• 상태: {status}

💡 이 결과는 입력된 조건들을 종합적으로 분석한 예측값입니다.
실제 시장 상황에 따라 결과가 달라질 수 있습니다.
        """
        
        self.show_message_box(f"{emoji} 분양률 예측 완료", result_msg.strip(), 
                            QMessageBox.Information, color)
    
    def show_error(self, message):
        """오류 메시지 표시"""
        self.show_message_box("입력 오류", message, QMessageBox.Warning, "#dc3545")
    
    def show_message_box(self, title, message, icon, button_color):
        """메시지 박스 표시"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(icon)
        
        button_hover = {
            "#28a745": "#218838",
            "#dc3545": "#c82333", 
            "#007bff": "#0056b3",
            "#17a2b8": "#138496",
            "#ffc107": "#e0a800"
        }.get(button_color, "#0056b3")
        
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: white;
                color: black;
            }}
            QMessageBox QLabel {{
                color: black;
                font-family: 'Malgun Gothic';
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VacancyPredictorWindow()
    window.show()
    sys.exit(app.exec_())