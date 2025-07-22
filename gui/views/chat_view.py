import asyncio
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtCore import Qt, QEvent
from core.transformers_backend import Chatbot

class ChatView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        layout.addWidget(QLabel("AI Chat Interface"))

        # Read-only log
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setAcceptRichText(True)
        font = QFont()
        font.setPointSize(12)
        self.log.setFont(font)
        layout.addWidget(self.log)

        # Input box
        self.input = QTextEdit()
        font_in = QFont()
        font_in.setPointSize(12)
        self.input.setFont(font_in)
        self.input.setFixedHeight(80)
        layout.addWidget(self.input)

        # Send button
        self.send_btn = QPushButton("Send")
        font_btn = QFont()
        font_btn.setPointSize(11)
        self.send_btn.setFont(font_btn)
        layout.addWidget(self.send_btn)

        # Initialize chatbot
        model_dir = "Llama-3.2-1B"
        self.chatbot = Chatbot(model_dir=model_dir)

        # Connect send action and Enter key
        self.send_btn.clicked.connect(self._send_message)
        self.input.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj is self.input and event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter) and not (event.modifiers() & Qt.ShiftModifier):
                self._send_message()
                return True
        return super().eventFilter(obj, event)

    def _append_message(self, sender: str, text: str, alignment: Qt.Alignment):
        cursor = self.log.textCursor()
        cursor.movePosition(QTextCursor.End)
        fmt = cursor.blockFormat()
        fmt.setAlignment(alignment)
        cursor.setBlockFormat(fmt)
        cursor.insertHtml(f"<b>{sender}:</b> {text}")
        cursor.insertBlock(); cursor.insertBlock()  # extra spacing
        self.log.setTextCursor(cursor)

    def _send_message(self):
        # Collect user text and display
        text = self.input.toPlainText().strip()
        if not text:
            return
        self.input.clear()
        self._append_message("You", text, Qt.AlignRight)
        # Schedule AI response asynchronously
        asyncio.ensure_future(self._ai_reply(text))

    async def _ai_reply(self, text: str):
        # offload compute to thread
        reply = await asyncio.to_thread(self.chatbot.generate, text)
        self._append_message("AI", reply, Qt.AlignLeft)
