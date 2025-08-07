import asyncio
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtCore import Qt, QEvent
from datetime import datetime
from core.transformers_backend import Chatbot
from core.ml_plotter import (get_plotting_engine, prepare_example_plot, prepare_boxplot_accelerometer,
                            prepare_temperature_histogram, prepare_correlation_matrix,
                            prepare_time_series_analysis, prepare_frequency_domain_plot,
                            prepare_scatter_plot_features)

class ChatView(QWidget):
    def __init__(self, parent=None, plot_view=None):
        super().__init__(parent)
        self.plot_view = plot_view  # Store reference to plot view
        
        # Initialize plotting engine
        self.plotting_engine = get_plotting_engine()
        
        # Setup UI
        self.setup_ui()
        
        # Initialize chatbot with model directory
        model_dir = "Llama-3.2-1B"
        self.chatbot = Chatbot(model_dir=model_dir)
        
        # Plot request mapping for backward compatibility
        self.plot_mapping = {
            'boxplot': prepare_boxplot_accelerometer,
            'histogram': prepare_temperature_histogram,
            'correlation': prepare_correlation_matrix,
            'time series': prepare_time_series_analysis,
            'frequency': prepare_frequency_domain_plot,
            'scatter': prepare_scatter_plot_features,
            'default': prepare_example_plot
        }

    def setup_ui(self):
        """Setup the chat interface UI"""
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        
        # Title
        title = QLabel("AI Chat Assistant")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title)
        
        # Chat display area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        chat_font = QFont()
        chat_font.setPointSize(12)
        self.chat_display.setFont(chat_font)
        self.chat_display.setMinimumHeight(300)
        self.layout.addWidget(self.chat_display)
        
        # Input area
        self.input_field = QTextEdit()
        self.input_field.setMaximumHeight(100)
        input_font = QFont()
        input_font.setPointSize(12)
        self.input_field.setFont(input_font)
        self.input_field.setPlaceholderText("Type your message here...")
        self.layout.addWidget(self.input_field)
        
        # Send button
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self._send_message)
        self.layout.addWidget(self.send_button)
        
        # Install event filter for Enter key handling
        self.input_field.installEventFilter(self)
        
        # Welcome message
        self._append_message("AI Assistant", "Hello! I'm your AI assistant. I can help you analyze sensor data and create visualizations. Try asking me to show plots or analyze specific sensors!", Qt.AlignLeft)

    def eventFilter(self, obj, event):
        """Handle Enter key press in input field"""
        if obj is self.input_field and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Return and not (event.modifiers() & Qt.ShiftModifier):
                self._send_message()
                return True
        return super().eventFilter(obj, event)

    def _append_message(self, sender: str, message: str, alignment=Qt.AlignRight):
        """Append a message to the chat display"""
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        # Format the message with proper timestamp
        timestamp = datetime.now().strftime("%H:%M")
        formatted_message = f"[{timestamp}] {sender}: {message}\n\n"
        
        # Insert the message
        cursor.insertText(formatted_message)
        
        # Scroll to bottom
        self.chat_display.setTextCursor(cursor)
        self.chat_display.ensureCursorVisible()

    def _send_message(self):
        """Send the current message"""
        message = self.input_field.toPlainText().strip()
        if not message:
            return
        
        # Display user message
        self._append_message("You", message, Qt.AlignRight)
        
        # Clear input field
        self.input_field.clear()
        
        # Get AI response
        self._ai_reply(message)

    def _ai_reply(self, user_message: str):
        """Get AI response and handle plot triggers"""
        try:
            # Get AI response using the correct method
            ai_response = self.chatbot.generate(user_message)
            
            # Display AI response
            self._append_message("AI Assistant", ai_response, Qt.AlignLeft)
            
            # Check for plot triggers
            self._check_plot_triggers(ai_response, user_message)
            
        except Exception as e:
            error_msg = f"Error getting AI response: {str(e)}"
            self._append_message("System", error_msg, Qt.AlignLeft)

    def _check_plot_triggers(self, ai_response: str, user_message: str):
        """Check AI response for keywords that should trigger plot display"""
        response_lower = ai_response.lower()
        user_lower = user_message.lower()
        
        # Check for general plot trigger
        if "show sales plot" in response_lower:
            self.trigger_plot_display()
            return
        
        # Check for natural language plot requests
        plot_request = self._detect_natural_plot_request(user_lower, response_lower)
        if plot_request:
            self.trigger_natural_plot_request(plot_request)
            return
        
        # Check for specific plot types (backward compatibility)
        plot_type = self._detect_plot_type(response_lower)
        if plot_type:
            self.trigger_specific_plot(plot_type)

    def _detect_natural_plot_request(self, user_message: str, ai_response: str) -> str:
        """Detect natural language plot requests"""
        # Common plot request patterns
        plot_keywords = [
            'show me', 'display', 'plot', 'visualize', 'create', 'generate',
            'boxplot', 'histogram', 'correlation', 'scatter', 'time series',
            'frequency', 'fft', 'distribution', 'comparison'
        ]
        
        # Check if user message contains plot keywords
        for keyword in plot_keywords:
            if keyword in user_message.lower():
                return user_message
        
        # Check if AI response suggests showing a plot
        if any(word in ai_response.lower() for word in ['plot', 'visualization', 'chart', 'graph']):
            return user_message
        
        return None

    def _detect_plot_type(self, response_lower: str) -> str:
        """Detect specific plot type from AI response (backward compatibility)"""
        if any(word in response_lower for word in ['boxplot', 'accelerometer', 'acceleration']):
            return 'boxplot'
        elif any(word in response_lower for word in ['histogram', 'temperature', 'distribution']):
            return 'histogram'
        elif any(word in response_lower for word in ['correlation', 'matrix', 'relationships']):
            return 'correlation'
        elif any(word in response_lower for word in ['time series', 'temporal', 'over time']):
            return 'time series'
        elif any(word in response_lower for word in ['frequency', 'fft', 'spectrum']):
            return 'frequency'
        elif any(word in response_lower for word in ['scatter', 'features', 'relationships']):
            return 'scatter'
        return None

    def trigger_plot_display(self):
        """
        Generate default plot and display it in the plot view
        """
        try:
            fig = prepare_example_plot()
            if self.plot_view:
                self.plot_view.show_plot(fig)
                self._append_message("System", "Generated plot based on your request. Check the Plot section.", Qt.AlignLeft)
            else:
                main_window = self.window()
                if hasattr(main_window, 'plotView'):
                    main_window.plotView.show_plot(fig)
                    main_window.stack.setCurrentIndex(3)
                    self._append_message("System", "Generated plot based on your request. Check the Plot section.", Qt.AlignLeft)
                else:
                    self._append_message("System", "Error: Plot view not available", Qt.AlignLeft)
        except Exception as e:
            self._append_message("System", f"Error displaying plot: {str(e)}", Qt.AlignLeft)

    def trigger_natural_plot_request(self, request: str):
        """Handle natural language plot requests using the plotting engine"""
        try:
            # Use the plotting engine to handle the request
            fig = self.plotting_engine.handle_plot_request(request)
            
            if self.plot_view:
                self.plot_view.show_plot(fig)
                self._append_message("System", f"Generated plot based on your request: '{request}'", Qt.AlignLeft)
            else:
                main_window = self.window()
                if hasattr(main_window, 'plotView'):
                    main_window.plotView.show_plot(fig)
                    main_window.stack.setCurrentIndex(3)
                    self._append_message("System", f"Generated plot based on your request: '{request}'", Qt.AlignLeft)
                else:
                    self._append_message("System", "Error: Plot view not available", Qt.AlignLeft)
        except Exception as e:
            self._append_message("System", f"Error generating plot: {str(e)}", Qt.AlignLeft)

    def trigger_specific_plot(self, plot_type: str):
        """
        Generate and display a specific type of plot
        """
        try:
            plot_function = self.plot_mapping.get(plot_type, prepare_example_plot)
            fig = plot_function()
            if self.plot_view:
                self.plot_view.show_plot(fig)
                plot_names = {
                    'boxplot': 'Accelerometer comparison',
                    'histogram': 'Temperature distribution',
                    'correlation': 'Feature correlation matrix',
                    'time series': 'Time series analysis',
                    'frequency': 'Frequency domain analysis',
                    'scatter': 'Feature relationships'
                }
                plot_name = plot_names.get(plot_type, 'Data analysis')
                self._append_message("System", f"Generated {plot_name} plot. Check the Plot section.", Qt.AlignLeft)
            else:
                main_window = self.window()
                if hasattr(main_window, 'plotView'):
                    main_window.plotView.show_plot(fig)
                    main_window.stack.setCurrentIndex(3)
                    self._append_message("System", f"Generated specific plot. Check the Plot section.", Qt.AlignLeft)
                else:
                    self._append_message("System", "Error: Plot view not available", Qt.AlignLeft)
        except Exception as e:
            self._append_message("System", f"Error displaying {plot_type} plot: {str(e)}", Qt.AlignLeft)

    def show_sales_plot(self):
        """Alias for trigger_plot_display for backward compatibility"""
        self.trigger_plot_display()
