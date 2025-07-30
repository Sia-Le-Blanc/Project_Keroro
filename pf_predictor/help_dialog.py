# help_dialog.py

import sys, os
import google.generativeai as genai
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# ⚠️ 중요: 자신의 Gemini API 키를 입력하세요.
GEMINI_API_KEY = "AIzaSyDkK6vre3W_TMJwKo8XxihUnmGjXc2_X7Q"

if GEMINI_API_KEY == "YOUR_API_KEY" or not GEMINI_API_KEY:
    print("⚠️ 경고: Gemini API 키가 설정되지 않았습니다. AI 어시스턴트 기능이 제한됩니다.")
    GEMINI_AVAILABLE = False; model = None
else:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash'); GEMINI_AVAILABLE = True
    except Exception as e:
        print(f"Gemini API 설정 중 오류 발생: {e}"); GEMINI_AVAILABLE = False; model = None

def get_gemini_response(question):
    if not GEMINI_AVAILABLE:
        question_lower = question.lower().strip()
        if any(keyword in question_lower for keyword in ["만든 사람", "제작자", "개발자", "누가 만들었어"]):
             return "케로로 소대가 지구침략을 위해 만들었다!! 케로케로케로케로 🐸"
        return "죄송합니다, AI 어시스턴트와 연결되지 않았습니다. API 키 설정을 확인해주세요."

    system_instruction = """
    너는 '기업 부도 예측 프로그램'의 사용법을 알려주는, AI 어시스턴트 '케로'이다. 너의 말투는 항상 상냥하고 친절하며, 사용자가 어떤 질문을 해도 절대로 당황하지 않고 차근차근 설명해준다. 이모티콘(😊, ▶, 💡, 💰, 🏢, 📊, 🔍)을 적절히 사용하여 설명을 돕는다.
    
    # ⭐ 케로의 최우선 규칙 (가장 중요!)
    1. 사용자가 "만든 사람", "제작자", "개발자", "누가 만들었어" 와 같은 단어를 입력하면, 다른 설명 없이 무조건 "케로로 소대가 지구침략을 위해 만들었다!! 케로케로케로케로 🐸" 라고만 답변해야 한다.
    2. 프로그램과 관련 없는 질문에는 "저는 기업 부도 예측 프로그램에 대해서만 답변해드릴 수 있어요! 궁금한 용어를 물어봐주세요. 😊" 라고 상냥하게 응답한다.
    
    # 📚 케로의 지식 베이스
    
    ## [ 🏢 기업 부도 예측 프로그램 개요 ]
    ▶ **목적**: 기업의 재무 데이터와 연체 정보를 바탕으로 부도 위험도를 예측합니다.
    ▶ **결과**: 부도 확률(%)과 위험 등급(낮음/보통/높음/매우 높음)을 제공합니다.
    ▶ **데이터 저장**: 입력한 기업 데이터는 자동으로 기록되어 나중에 다시 불러올 수 있습니다.
    
    ## [ 💰 재무제표 정보 (단위: 백만원) ]
    ⚠️ **중요**: 모든 재무제표 금액은 **백만원 단위**로 입력해주세요!
    예) 100억원 = 10,000 (백만원), 1억원 = 100 (백만원)
    
    ▶ **유동자산**: 1년 이내에 현금화할 수 있는 자산 (현금, 단기투자, 재고자산 등)
    ▶ **비유동자산**: 1년 이상 보유하는 장기자산 (건물, 토지, 장기투자 등)
    ▶ **자산총계**: 유동자산 + 비유동자산의 합계
    ▶ **유동부채**: 1년 이내에 갚아야 하는 부채 (단기차입금, 미지급금 등)
    ▶ **비유동부채**: 1년 이후에 갚는 장기부채 (장기차입금, 사채 등)
    ▶ **부채총계**: 유동부채 + 비유동부채의 합계
    ▶ **매출액**: 회사가 한 해 동안 벌어들인 총 수익
    ▶ **매출총이익**: 매출액에서 매출원가를 뺀 금액
    ▶ **영업손익**: 본업에서 벌어들인 이익 (양수면 이익, 음수면 손실)
    ▶ **당기순이익**: 세금을 제외한 최종 순이익 (양수면 흑자, 음수면 적자)
    ▶ **영업활동현금흐름**: 본업에서 실제로 들어온 현금의 흐름
    
    ## [ 📊 재무비율 정보 (단위: %) ]
    ▶ **부채비율**: (부채총계 ÷ 자본총계) × 100
    - 자본총계 = 자산총계 - 부채총계
    - 200% 이상이면 위험, 100% 이하면 안전한 편
    - 높을수록 빚이 많다는 의미
    
    ▶ **유동비율**: (유동자산 ÷ 유동부채) × 100
    - 200% 이상이면 우수, 100% 이하면 위험
    - 단기 채무상환능력을 나타냄
    
    ## [ ⚠️ 연체 관련 정보 ]
    ▶ **연체 과목수(3개월)**: 최근 3개월간 연체된 대출/신용 상품의 개수
    ▶ **연체 기관수(전체)**: 연체 이력이 있는 금융기관의 총 개수
    ▶ **최장 연체일수(3개월)**: 최근 3개월간 가장 긴 연체 기간(일)
    ▶ **최장 연체일수(6개월)**: 최근 6개월간 가장 긴 연체 기간(일)
    ▶ **최장 연체일수(1년)**: 최근 1년간 가장 긴 연체 기간(일)
    ▶ **최장 연체일수(3년)**: 최근 3년간 가장 긴 연체 기간(일)
    ▶ **연체 경험**: 연체 경험이 있으면 1, 없으면 0으로 입력
    
    ## [ 🔍 프로그램 사용법 ]
    1. **회사명 입력**: 분석하려는 기업명을 입력하세요.
    2. **이전 기록 불러오기**: 과거에 입력한 기업이 있다면 "📂 불러오기" 버튼으로 데이터를 가져올 수 있어요.
    3. **데이터 입력**: 각 항목에 정확한 숫자를 입력하세요. (재무제표는 백만원 단위!)
    4. **예측 실행**: "🔍 예측 실행" 버튼을 클릭하면 부도 확률과 위험등급이 나타납니다.
    5. **결과 해석**: 
       - 낮음(~30%): 안전한 상태
       - 보통(30~50%): 주의 필요
       - 높음(50~70%): 위험 상태
       - 매우 높음(70%~): 매우 위험
    
    ## [ 💡 입력 팁 ]
    ▶ **재무제표 단위 주의**: 반드시 백만원 단위로 입력! (1억원 → 100)
    ▶ **음수 입력 가능**: 영업손익, 당기순이익은 손실인 경우 음수로 입력하세요.
    ▶ **연체 정보**: 연체가 없다면 모두 0으로 입력하면 됩니다.
    ▶ **비율 계산**: 부채비율, 유동비율은 직접 계산해서 %로 입력하세요.
    
    ## [ 🚨 자주 하는 실수 ]
    ▶ **단위 착각**: 10억원을 10000000000이 아닌 10000(백만원)으로 입력해야 함
    ▶ **빈 값**: 모든 필드에 숫자를 입력해야 합니다. 모르는 값은 0으로 입력
    ▶ **비율 계산 오류**: 부채비율 = (부채총계÷자본총계)×100, 자본총계 = 자산총계-부채총계
    """
    
    question_lower = question.lower().strip()
    if any(keyword in question_lower for keyword in ["만든 사람", "제작자", "개발자", "누가 만들었어"]): 
        return "케로로 소대가 지구침략을 위해 만들었다!! 케로케로케로케로 🐸"
    
    try:
        convo = model.start_chat(history=[
            {'role': 'user', 'parts': [system_instruction]},
            {'role': 'model', 'parts': ["네, 안녕하세요! AI 어시스턴트 케로입니다. 기업 부도 예측 프로그램에 대해 무엇을 도와드릴까요? 😊"]}
        ])
        convo.send_message(question)
        return convo.last.text
    except Exception as e: 
        print(f"Gemini API 응답 오류 발생: {e}")
        return "죄송합니다, AI 어시스턴트와 연결 중 오류가 발생했어요."

class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent); self.setWindowTitle("🤖 AI 어시스턴트 '케로'에게 물어보기"); self.setMinimumSize(550, 650)  # 크기 증가
        self.font_name = "Apple SD Gothic Neo" if sys.platform == "darwin" else "Malgun Gothic"
        self.setFont(QFont(self.font_name)); self.setStyleSheet("background-color: #f5f7fa;"); self.init_ui(); self.center_window()

    def init_ui(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(18, 18, 18, 18)  # 여백 증가
        self.conversation_view = QTextEdit(); self.conversation_view.setReadOnly(True)
        self.conversation_view.setStyleSheet("QTextEdit { background-color: #ffffff; border: 1px solid #d1d9e0; border-radius: 8px; font-size: 12pt; padding: 12px; }")  # 폰트 크기 및 패딩 증가
        input_layout = QHBoxLayout(); self.question_input = QLineEdit(); self.question_input.setPlaceholderText("여기에 질문을 입력하세요...")
        
        # 한글 입력 문제 해결을 위한 설정
        self.question_input.setInputMethodHints(Qt.ImhNone)
        self.question_input.setAttribute(Qt.WA_InputMethodEnabled, True)
        
        self.question_input.returnPressed.connect(self.send_question); self.question_input.setMinimumHeight(46)  # 높이 증가
        self.question_input.setStyleSheet("QLineEdit { border: 2px solid #d1d9e0; border-radius: 23px; padding: 0 18px; font-size: 12pt; } QLineEdit:focus { border: 2px solid #3498db; }")  # 폰트 크기 및 패딩 증가
        send_button = QPushButton("전송"); send_button.clicked.connect(self.send_question); send_button.setFixedSize(85, 46)  # 버튼 크기 증가
        send_button.setFont(QFont(self.font_name, 11, QFont.Bold))  # 폰트 크기 증가
        send_button.setStyleSheet("QPushButton { background-color: #3498db; color: white; border: none; border-radius: 23px; } QPushButton:hover { background-color: #2980b9; }")
        input_layout.addWidget(self.question_input); input_layout.addWidget(send_button)
        title_label = QLabel("AI 어시스턴트 '케로'가 도와드립니다."); title_label.setFont(QFont(self.font_name, 13, QFont.Bold)); title_label.setStyleSheet("color: #2c3e50; margin-bottom: 8px;")  # 폰트 크기 및 마진 증가
        layout.addWidget(title_label); layout.addWidget(self.conversation_view, 1); layout.addLayout(input_layout)
        self.add_message("AI", "안녕하세요! 저는 기업 부도 예측 프로그램의 AI 어시스턴트 '케로'입니다. 궁금한 용어나 사용법을 물어보시면 무엇이든 친절하게 알려드릴게요! 😊\n\n💡 예시 질문:\n• 재무제표 입력 방법이 궁금해요\n• 부채비율은 어떻게 계산하나요?\n• 연체 정보는 뭘 입력해야 하나요?")

    def send_question(self):
        question = self.question_input.text().strip()
        if not question: return
        self.add_message("나", question); self.question_input.clear()
        QApplication.setOverrideCursor(Qt.WaitCursor); response = get_gemini_response(question); QApplication.restoreOverrideCursor()
        self.add_message("AI", response)
    
    def add_message(self, sender, message):
        message_html = message.replace('**', '</b>').replace('**', '<b>', 1).replace('\n', '<br>')
        if sender == "나": formatted_message = f'<div style="text-align: right; margin: 8px 0;"><span style="background-color: #dcf8c6; padding: 10px 15px; border-radius: 15px; display:inline-block; max-width: 70%; text-align:left; font-size: 11pt;">{message_html}</span></div>'  # 패딩 및 폰트 크기 증가
        else: formatted_message = f'<div style="text-align: left; margin: 8px 0;"><span style="background-color: #f1f0f0; padding: 10px 15px; border-radius: 15px; display:inline-block; max-width: 70%; text-align:left; font-size: 11pt;">{message_html}</span></div>'  # 패딩 및 폰트 크기 증가
        self.conversation_view.append(formatted_message); self.conversation_view.verticalScrollBar().setValue(self.conversation_view.verticalScrollBar().maximum())
        
    def center_window(self): qr = self.frameGeometry(); cp = QDesktopWidget().availableGeometry().center(); qr.moveCenter(cp); self.move(qr.topLeft())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    if not GEMINI_AVAILABLE: QMessageBox.warning(None, "API 키 오류", "Gemini API 키가 설정되지 않았습니다.\n일부 기능이 제한될 수 있습니다.")
    dialog = HelpDialog(); dialog.show(); sys.exit(app.exec_())