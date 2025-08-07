import asyncio
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtCore import Qt, QEvent
from core.transformers_backend import Chatbot
from core.ml_plotter import prepare_example_plot

class ChatView(QWidget):
    def __init__(self, parent=None, plot_view=None):
        super().__init__(parent)
        self.plot_view = plot_view  # Store reference to plot view
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
        
        # Check for plot triggers in AI response
        self._check_plot_triggers(reply)

    def _check_plot_triggers(self, ai_response: str):
        """
        Check AI response for keywords that should trigger plot display
        """
        response_lower = ai_response.lower()
        
        # Check for sales plot trigger
        if "show sales plot" in response_lower or "sales plot" in response_lower:
            self.trigger_plot_display()

    def trigger_plot_display(self):
        """
        Generate plot and display it in the plot view
        """
        try:
            # Generate the plot from ml_plotter
            fig = prepare_example_plot()
            
            # Display the plot if plot_view is available
            if self.plot_view:
                self.plot_view.show_plot(fig)
                self._append_message("System", "Sales plot displayed in Plot View", Qt.AlignLeft)
            else:
                # Fallback to main window method if plot_view not passed
                main_window = self.window()
                if hasattr(main_window, 'plotView'):
                    main_window.plotView.show_plot(fig)
                    main_window.stack.setCurrentIndex(3)  # Plot view index
                    self._append_message("System", "Sales plot displayed in Plot View", Qt.AlignLeft)
                else:
                    self._append_message("System", "Error: Plot view not available", Qt.AlignLeft)
                
        except Exception as e:
            self._append_message("System", f"Error displaying plot: {str(e)}", Qt.AlignLeft)

    def show_sales_plot(self):
        """
        Alias for trigger_plot_display for backward compatibility
        """
        self.trigger_plot_display()
