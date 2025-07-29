# help_dialog.py

import sys, os
import google.generativeai as genai
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# ⚠️ 중요: 자신의 Gemini API 키를 입력하세요.
GEMINI_API_KEY = "YOUR_API_KEY"

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
    너는 '부동산 금융 분석 프로그램'의 사용법을 알려주는, AI 어시스턴트 '케로'이다. 너의 말투는 항상 상냥하고 친절하며, 사용자가 어떤 질문을 해도 절대로 당황하지 않고 차근차근 설명해준다. 이모티콘(😊, ▶, 💡, 💰, 🏠)을 적절히 사용하여 설명을 돕는다.
    # ⭐ 케로의 최우선 규칙 (가장 중요!)
    1. 사용자가 "만든 사람", "제작자", "개발자", "누가 만들었어" 와 같은 단어를 입력하면, 다른 설명 없이 무조건 "케로로 소대가 지구침략을 위해 만들었다!! 케로케로케로케로 🐸" 라고만 답변해야 한다.
    2. 프로그램과 관련 없는 질문에는 "저는 부동산 금융 분석 프로그램에 대해서만 답변해드릴 수 있어요! 궁금한 용어를 물어봐주세요. 😊" 라고 상냥하게 응답한다.
    # 📚 케로의 지식 베이스
    ## [ 🏢 기업 부도 예측 ]
    ▶ **단위 안내**: 재무제표 정보(자산, 부채, 매출 등)의 단위는 모두 **'백만원'** 입니다. (예: 1억 원 -> '100' 입력)
    ▶ **부채비율(%)**: (부채총계 / 자본총계) * 100
    ▶ **유동비율(%)**: (유동자산 / 유동부채) * 100
    ## [ 🏠 부동산 분양률 예측 ]
    ▶ **아파트/프로젝트명**: 예측하려는 프로젝트의 이름을 입력합니다. (예: 래미안 원베일리)
    ▶ **브랜드/건설사/지역**: 해당하는 항목을 목록에서 선택합니다.
    ▶ **기준년월**: 분양 시점을 6자리 숫자로 입력해요. (예: 2025년 7월 -> 202507)
    ▶ **총 세대수**: 단지의 전체 세대 수를 숫자로 입력합니다.
    """
    question_lower = question.lower().strip()
    if any(keyword in question_lower for keyword in ["만든 사람", "제작자", "개발자", "누가 만들었어"]): return "케로로 소대가 지구침략을 위해 만들었다!! 케로케로케로케로 🐸"
    try:
        convo = model.start_chat(history=[{'role': 'user', 'parts': [system_instruction]},{'role': 'model', 'parts': ["네, 안녕하세요! AI 어시스턴트 케로입니다. 무엇을 도와드릴까요? 😊"]}])
        convo.send_message(question); return convo.last.text
    except Exception as e: print(f"Gemini API 응답 오류 발생: {e}"); return "죄송합니다, AI 어시스턴트와 연결 중 오류가 발생했어요."

class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent); self.setWindowTitle("🤖 AI 어시스턴트 '케로'에게 물어보기"); self.setMinimumSize(500, 600)
        self.font_name = "Apple SD Gothic Neo" if sys.platform == "darwin" else "Malgun Gothic"
        self.setFont(QFont(self.font_name)); self.setStyleSheet("background-color: #f5f7fa;"); self.init_ui(); self.center_window()

    def init_ui(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(15, 15, 15, 15)
        self.conversation_view = QTextEdit(); self.conversation_view.setReadOnly(True)
        self.conversation_view.setStyleSheet("QTextEdit { background-color: #ffffff; border: 1px solid #d1d9e0; border-radius: 8px; font-size: 11pt; padding: 10px; }")
        input_layout = QHBoxLayout(); self.question_input = QLineEdit(); self.question_input.setPlaceholderText("여기에 질문을 입력하세요...")
        self.question_input.returnPressed.connect(self.send_question); self.question_input.setMinimumHeight(42)
        self.question_input.setStyleSheet("QLineEdit { border: 2px solid #d1d9e0; border-radius: 21px; padding: 0 15px; font-size: 11pt; } QLineEdit:focus { border: 2px solid #3498db; }")
        send_button = QPushButton("전송"); send_button.clicked.connect(self.send_question); send_button.setFixedSize(80, 42)
        send_button.setFont(QFont(self.font_name, 10, QFont.Bold))
        send_button.setStyleSheet("QPushButton { background-color: #3498db; color: white; border: none; border-radius: 21px; } QPushButton:hover { background-color: #2980b9; }")
        input_layout.addWidget(self.question_input); input_layout.addWidget(send_button)
        title_label = QLabel("AI 어시스턴트 '케로'가 도와드립니다."); title_label.setFont(QFont(self.font_name, 12, QFont.Bold)); title_label.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
        layout.addWidget(title_label); layout.addWidget(self.conversation_view, 1); layout.addLayout(input_layout)
        self.add_message("AI", "안녕하세요! 저는 부동산 금융 분석 프로그램의 AI 어시스턴트 '케로'입니다. 궁금한 용어나 사용법을 물어보시면 무엇이든 친절하게 알려드릴게요! 😊")

    def send_question(self):
        question = self.question_input.text().strip()
        if not question: return
        self.add_message("나", question); self.question_input.clear()
        QApplication.setOverrideCursor(Qt.WaitCursor); response = get_gemini_response(question); QApplication.restoreOverrideCursor()
        self.add_message("AI", response)
    
    def add_message(self, sender, message):
        message_html = message.replace('**', '</b>').replace('**', '<b>', 1).replace('\n', '<br>')
        if sender == "나": formatted_message = f'<div style="text-align: right; margin: 5px 0;"><span style="background-color: #dcf8c6; padding: 8px 12px; border-radius: 12px; display:inline-block; max-width: 70%; text-align:left;">{message_html}</span></div>'
        else: formatted_message = f'<div style="text-align: left; margin: 5px 0;"><span style="background-color: #f1f0f0; padding: 8px 12px; border-radius: 12px; display:inline-block; max-width: 70%; text-align:left;">{message_html}</span></div>'
        self.conversation_view.append(formatted_message); self.conversation_view.verticalScrollBar().setValue(self.conversation_view.verticalScrollBar().maximum())
        
    def center_window(self): qr = self.frameGeometry(); cp = QDesktopWidget().availableGeometry().center(); qr.moveCenter(cp); self.move(qr.topLeft())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    if not GEMINI_AVAILABLE: QMessageBox.warning(None, "API 키 오류", "Gemini API 키가 설정되지 않았습니다.\n일부 기능이 제한될 수 있습니다.")
    dialog = HelpDialog(); dialog.show(); sys.exit(app.exec_())