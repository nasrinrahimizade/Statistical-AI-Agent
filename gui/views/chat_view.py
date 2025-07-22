# gui/views/chat_view.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtCore import Qt

class ChatView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("AI Chat Interface"))

        # Read-only log; accepts rich text
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setAcceptRichText(True)
        # Increase chat log font size
        log_font = QFont()
        log_font.setPointSize(11)
        self.log.setFont(log_font)
        layout.addWidget(self.log)

        # Input area
        self.input = QTextEdit()
        input_font = QFont()
        input_font.setPointSize(11)
        self.input.setFont(input_font)
        self.input.setFixedHeight(80)
        layout.addWidget(self.input)

        # Send button
        self.send_btn = QPushButton("Send")
        btn_font = QFont()
        btn_font.setPointSize(11)
        self.send_btn.setFont(btn_font)
        layout.addWidget(self.send_btn)

        # Hook up the send action
        self.send_btn.clicked.connect(self.on_send_clicked)

    def _append_message(self, sender: str, text: str, alignment):
        cursor = self.log.textCursor()
        cursor.movePosition(QTextCursor.End)
        block_fmt = cursor.blockFormat()
        block_fmt.setAlignment(alignment)
        cursor.setBlockFormat(block_fmt)
        cursor.insertHtml(f'<b>{sender}:</b> {text}')
        cursor.insertBlock()
        self.log.setTextCursor(cursor)

    def set_dataframe(self, df):
        # Show dataset loaded message as user message (right-aligned)
        msg = f"Dataset loaded with {len(df)} rows."
        self._append_message("You", msg, Qt.AlignRight)

    def on_send_clicked(self):
        user_text = self.input.toPlainText().strip()
        if not user_text:
            return

        # Append the user's message
        self._append_message("You", user_text, Qt.AlignRight)
        self.input.clear()

        # TODO: Replace this stub with real AI backend call
        ai_response = f"Echo: {user_text}"

        # Append the AI's response
        self._append_message("AI", ai_response, Qt.AlignLeft)

    def on_send_clicked(self):
        user_text = self.input.toPlainText().strip()
        if not user_text:
            return

        # Append the user's message, right-aligned via block format
        cursor = self.log.textCursor()
        cursor.movePosition(QTextCursor.End)
        block_fmt = cursor.blockFormat()
        block_fmt.setAlignment(Qt.AlignRight)
        cursor.setBlockFormat(block_fmt)
        cursor.insertHtml(f'<b>You:</b> {user_text}')
        cursor.insertBlock()
        self.log.setTextCursor(cursor)
        self.input.clear()

        # TODO: Replace this stub with real AI backend call
        ai_response = f"Echo: {user_text}"

        # Append the AI's response, left-aligned via block format
        cursor = self.log.textCursor()
        cursor.movePosition(QTextCursor.End)
        block_fmt = cursor.blockFormat()
        block_fmt.setAlignment(Qt.AlignLeft)
        cursor.setBlockFormat(block_fmt)
        cursor.insertHtml(f'<b>AI:</b> {ai_response}')
        cursor.insertBlock()
        self.log.setTextCursor(cursor)
