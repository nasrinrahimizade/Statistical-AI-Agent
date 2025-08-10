###chat_view.py###

import asyncio
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                              QPushButton, QLabel, QScrollArea, QFrame, QDialog)
from PySide6.QtGui import QFont, QTextCursor, QPixmap
from PySide6.QtCore import Qt, QEvent, QSize
from datetime import datetime
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from io import BytesIO
from PySide6.QtGui import QFont, QTextCursor, QPixmap, QIcon  # Add QIcon here
from PySide6.QtCore import Qt, QEvent, QSize  # QSize should already be imported

from core.transformers_backend import Chatbot
from core.ml_plotter import (get_plotting_engine, prepare_example_plot, prepare_boxplot_accelerometer,
                            prepare_temperature_histogram, prepare_correlation_matrix,
                            prepare_time_series_analysis, prepare_frequency_domain_plot,
                            prepare_scatter_plot_features)

class PlotDialog(QDialog):
    """Dialog to show enlarged plot"""
    def __init__(self, figure, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Plot View")
        self.resize(800, 600)
        
        layout = QVBoxLayout(self)
        canvas = FigureCanvas(figure)
        layout.addWidget(canvas)
        canvas.draw()

class ClickablePlotWidget(QWidget):
    """Widget that displays a plot thumbnail and can be clicked to enlarge"""
    def __init__(self, figure, parent=None):
        super().__init__(parent)
        self.figure = figure
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Create a small canvas for the thumbnail
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMaximumSize(400, 300)
        self.canvas.setMinimumSize(300, 200)
        
        # Make it clickable
        self.canvas.mousePressEvent = self.on_click
        self.canvas.setCursor(Qt.PointingHandCursor)
        
        layout.addWidget(self.canvas)
        
        # Add a label to indicate it's clickable
        click_label = QLabel("Click to enlarge")
        click_label.setAlignment(Qt.AlignCenter)
        click_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(click_label)
        
        self.canvas.draw()
    
    def on_click(self, event):
        """Handle click to show enlarged plot"""
        dialog = PlotDialog(self.figure, self)
        dialog.exec()

class InlinePlotWidget(QWidget):
    """Small plot widget that appears inline in chat"""
    def __init__(self, figure, plot_name="Plot", parent=None):
        super().__init__(parent)
        self.figure = figure
        self.plot_name = plot_name
        self.parent_chat = parent
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Create a properly sized figure for inline display with better spacing
        from matplotlib.figure import Figure
        small_fig = Figure(figsize=(5, 3.5), dpi=80)
        small_fig.subplots_adjust(left=0.12, bottom=0.15, right=0.95, top=0.85, hspace=0.3, wspace=0.3)
        
        # Copy the original plot to the new figure with improved formatting
        if hasattr(self.figure, 'axes') and len(self.figure.axes) > 0:
            orig_ax = self.figure.axes[0]
            new_ax = small_fig.add_subplot(111)
            
            # Copy plot elements (this is a simplified copy, might need adjustment based on plot type)
            for line in orig_ax.get_lines():
                new_ax.plot(line.get_xdata(), line.get_ydata(), 
                          color=line.get_color(), linewidth=line.get_linewidth(),
                          linestyle=line.get_linestyle(), marker=line.get_marker())
            
            # Copy title with proper spacing
            title_text = orig_ax.get_title()
            if title_text:
                new_ax.set_title(title_text, fontsize=10, pad=15)  # Added padding
            
            # Copy labels with proper formatting
            xlabel = orig_ax.get_xlabel()
            ylabel = orig_ax.get_ylabel()
            if xlabel:
                new_ax.set_xlabel(xlabel, fontsize=8)
            if ylabel:
                new_ax.set_ylabel(ylabel, fontsize=8)
            
            # Improve tick formatting
            new_ax.tick_params(labelsize=7)
            
            # Copy other plot types (scatter, bar, etc.)
            for collection in orig_ax.collections:
                if hasattr(collection, 'get_offsets'):  # Scatter plot
                    offsets = collection.get_offsets()
                    if len(offsets) > 0:
                        new_ax.scatter(offsets[:, 0], offsets[:, 1], 
                                     c=collection.get_facecolors()[0] if len(collection.get_facecolors()) > 0 else 'blue',
                                     s=20, alpha=0.7)
            
            # Copy bar plots
            for patch in orig_ax.patches:
                if hasattr(patch, 'get_x') and hasattr(patch, 'get_height'):
                    new_ax.add_patch(patch)
        
        self.canvas = FigureCanvas(small_fig)
        self.canvas.setFixedSize(400, 280)  # Slightly larger for better text spacing
        
        # Make it clickable
        self.canvas.mousePressEvent = self.on_click
        self.canvas.setCursor(Qt.PointingHandCursor)
        
        # Add border and styling
        self.canvas.setStyleSheet("""
            QWidget {
                border: 2px solid #cccccc;
                border-radius: 5px;
                background-color: white;
            }
            QWidget:hover {
                border: 2px solid #0078d4;
            }
        """)
        
        layout.addWidget(self.canvas)
        
        # Add a label with more spacing
        click_label = QLabel(f"📊 {self.plot_name} (click to enlarge)")
        click_label.setAlignment(Qt.AlignCenter)
        click_label.setStyleSheet("color: #666; font-size: 10px; padding: 5px; margin-top: 5px;")
        layout.addWidget(click_label)
        
        self.canvas.draw()
    
    def on_click(self, event):
        """Handle click to show enlarged plot in right panel"""
        # Show in right panel
        if hasattr(self.parent_chat, '_show_plot_in_right_panel'):
            self.parent_chat._show_plot_in_right_panel(self.figure, self.plot_name)

class ChatView(QWidget):
    def __init__(self, parent=None, plot_view=None):
        super().__init__(parent)
        self.plot_view = plot_view  # Keep reference for backward compatibility
        
        # Initialize plotting engine
        self.plotting_engine = get_plotting_engine()
        
        # Track fullscreen state
        self.plot_area_fullscreen = False
        self.plot_area_normal_size = None
        
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
        """Setup the chat interface UI with closeable plot area"""
        main_layout = QHBoxLayout(self)
        self.setLayout(main_layout)
        
        # Left side - Chat (main area)
        self.chat_widget = QWidget()
        chat_layout = QVBoxLayout(self.chat_widget)
        
        # Title
        title = QLabel("AI Chat Assistant")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        chat_layout.addWidget(title)
        
        # Chat display area with scroll
        chat_scroll = QScrollArea()
        chat_scroll.setWidgetResizable(True)
        chat_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        chat_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Container for chat messages and inline plots
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_layout.setSpacing(10)
        
        chat_scroll.setWidget(self.chat_container)
        chat_layout.addWidget(chat_scroll)
        
        # Input area
        self.input_field = QTextEdit()
        self.input_field.setMaximumHeight(100)
        input_font = QFont()
        input_font.setPointSize(12)
        self.input_field.setFont(input_font)
        self.input_field.setPlaceholderText("Type your message here...")
        chat_layout.addWidget(self.input_field)
        
        # Send button
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self._send_message)
        chat_layout.addWidget(self.send_button)
        
        main_layout.addWidget(self.chat_widget, 1)  # Equal width with plot area
        
        # Right side - Plot area (closeable and resizable)
        self.plot_area = QWidget()
        self.plot_area.setMinimumWidth(300)  # Allow resizing but set minimum
        plot_layout = QVBoxLayout(self.plot_area)
        
        # Header with buttons
        header_layout = QHBoxLayout()
        plot_title = QLabel("Current Plot")
        plot_title_font = QFont()
        plot_title_font.setPointSize(14)
        plot_title_font.setBold(True)
        plot_title.setFont(plot_title_font)
        header_layout.addWidget(plot_title)
        
        # Add stretch to push buttons to the right
        header_layout.addStretch()
        
        # Fullscreen toggle button
        self.fullscreen_btn = QPushButton()
        self.fullscreen_btn.setMaximumSize(25, 25)
        self.fullscreen_btn.setToolTip("Toggle Fullscreen")

        # Set maximize icon initially
        
        maximize_icon = QIcon("icons/minimize.svg")
        self.fullscreen_btn.setIcon(maximize_icon)
        self.fullscreen_btn.setIconSize(QSize(16, 16))

        self.fullscreen_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        self.fullscreen_btn.clicked.connect(self._toggle_fullscreen)
        header_layout.addWidget(self.fullscreen_btn)
        
        # Close button
        self.close_plot_btn = QPushButton("✕")
        self.close_plot_btn.setMaximumSize(25, 25)
        self.close_plot_btn.setToolTip("Close Plot Panel")
        self.close_plot_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff4444;
                color: white;
                border: none;
                border-radius: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #cc3333;
            }
        """)
        self.close_plot_btn.clicked.connect(self._close_plot_area)
        header_layout.addWidget(self.close_plot_btn)
        
        plot_layout.addLayout(header_layout)
        
        # Single plot display area (no scroll, just one plot)
        self.current_plot_widget = QWidget()
        self.current_plot_layout = QVBoxLayout(self.current_plot_widget)
        self.current_plot_layout.setContentsMargins(5, 5, 5, 5)
        
        plot_layout.addWidget(self.current_plot_widget)
        
        main_layout.addWidget(self.plot_area, 1)  # Equal width with chat initially
        
        # Initially hide the plot area
        self.plot_area.hide()
        
        # Install event filter for Enter key handling
        self.input_field.installEventFilter(self)
        
        # Welcome message
        self._append_message("AI Assistant", "Hello! I'm your AI assistant. I can help you analyze sensor data and create visualizations. Try asking me to show plots or analyze specific sensors!")

    def eventFilter(self, obj, event):
        """Handle Enter key press in input field"""
        if obj is self.input_field and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Return and not (event.modifiers() & Qt.ShiftModifier):
                self._send_message()
                return True
        return super().eventFilter(obj, event)

    def _toggle_fullscreen(self):
        """Toggle fullscreen mode for the plot area"""
        if not self.plot_area_fullscreen:
            # Enter fullscreen mode
            self.plot_area_fullscreen = True
            
            # Store current layout proportions
            sizes = self.layout().sizes() if hasattr(self.layout(), 'sizes') else None
            self.plot_area_normal_size = sizes
            
            # Hide chat widget and make plot area take full space
            self.chat_widget.hide()
            minimize_icon = QIcon("icons/maximize.svg")
            self.fullscreen_btn.setIcon(minimize_icon)
            
        else:
            # Exit fullscreen mode
            self.plot_area_fullscreen = False
            
            # Show chat widget again
            self.chat_widget.show()
            maximize_icon = QIcon("icons/minimize.svg")
            self.fullscreen_btn.setIcon(maximize_icon)

    def _close_plot_area(self):
        """Close the right plot panel"""
        self.plot_area.hide()
        # Reset fullscreen state when closing
        if self.plot_area_fullscreen:
            self.plot_area_fullscreen = False
            self.chat_widget.show()
            maximize_icon = QIcon("icons/minimize.svg")
            self.fullscreen_btn.setIcon(maximize_icon)

    def _append_message(self, sender: str, message: str):
        """Append a message to the chat display"""
        # Create message widget
        message_widget = QWidget()
        message_layout = QVBoxLayout(message_widget)
        message_layout.setContentsMargins(10, 5, 10, 5)
        
        # Create message label
        timestamp = datetime.now().strftime("%H:%M")
        message_label = QLabel(f"[{timestamp}] {sender}: {message}")
        message_label.setWordWrap(True)
        
        # Style based on sender
        if sender == "You":
            message_label.setStyleSheet("""
                QLabel {
                    background-color: #e3f2fd;
                    padding: 8px;
                    border-radius: 10px;
                    border: 1px solid #bbdefb;
                }
            """)
            message_label.setAlignment(Qt.AlignRight)
        elif sender == "AI Assistant":
            message_label.setStyleSheet("""
                QLabel {
                    background-color: #f5f5f5;
                    padding: 8px;
                    border-radius: 10px;
                    border: 1px solid #e0e0e0;
                }
            """)
            message_label.setAlignment(Qt.AlignLeft)
        else:  # System messages
            message_label.setStyleSheet("""
                QLabel {
                    background-color: #fff3e0;
                    padding: 8px;
                    border-radius: 10px;
                    border-1px solid #ffcc02;
                    color: #e65100;
                }
            """)
            message_label.setAlignment(Qt.AlignCenter)
        
        message_layout.addWidget(message_label)
        
        # Add to chat layout
        self.chat_layout.addWidget(message_widget)
        
        # Scroll to bottom
        self.chat_container.adjustSize()

    def _add_inline_plot(self, figure, plot_name="Generated Plot"):
        """Add a small plot directly below the last message"""
        # Improve figure layout before creating inline plot
        figure.tight_layout(pad=2.0)  # Add padding around the plot
        
        plot_widget = InlinePlotWidget(figure, plot_name, self)
        
        # Create container with proper alignment and spacing
        plot_container = QWidget()
        plot_container_layout = QVBoxLayout(plot_container)
        plot_container_layout.setContentsMargins(10, 15, 10, 15)  # Add vertical spacing
        
        # Center the plot
        h_layout = QHBoxLayout()
        h_layout.addStretch()  # Left spacer
        h_layout.addWidget(plot_widget)
        h_layout.addStretch()  # Right spacer
        
        plot_container_layout.addLayout(h_layout)
        
        # Add to chat layout
        self.chat_layout.addWidget(plot_container)
        self.chat_container.adjustSize()

    def _show_plot_in_right_panel(self, figure, plot_name="Generated Plot"):
        """Show a single plot in the right panel, replacing any previous plot"""
        # Show the plot area if it's hidden
        self.plot_area.show()
        
        # Clear the current plot widget
        for i in reversed(range(self.current_plot_layout.count())):
            child = self.current_plot_layout.itemAt(i).widget()
            if child:
                child.deleteLater()
        
        # Create plot name label with proper spacing
        name_label = QLabel(plot_name)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet("font-weight: bold; padding: 15px; font-size: 14px; margin-bottom: 10px;")
        self.current_plot_layout.addWidget(name_label)
        
        # CREATE A FRESH FIGURE - this is the key fix
        from matplotlib.figure import Figure
        new_fig = Figure(figsize=(8, 6), dpi=100)
        new_fig.subplots_adjust(left=0.1, bottom=0.1, right=0.95, top=0.9, hspace=0.3, wspace=0.3)
        
        # Copy the plot data from original figure to new figure
        if hasattr(figure, 'axes') and len(figure.axes) > 0:
            orig_ax = figure.axes[0]
            new_ax = new_fig.add_subplot(111)
            
            # Copy all plot elements to the fresh figure
            for line in orig_ax.get_lines():
                new_ax.plot(line.get_xdata(), line.get_ydata(), 
                        color=line.get_color(), linewidth=line.get_linewidth(),
                        linestyle=line.get_linestyle(), marker=line.get_marker())
            
            # Copy scatter plots
            for collection in orig_ax.collections:
                if hasattr(collection, 'get_offsets'):
                    offsets = collection.get_offsets()
                    if len(offsets) > 0:
                        new_ax.scatter(offsets[:, 0], offsets[:, 1], 
                                    c=collection.get_facecolors()[0] if len(collection.get_facecolors()) > 0 else 'blue')
            
            # Copy bar plots
            for patch in orig_ax.patches:
                if hasattr(patch, 'get_x') and hasattr(patch, 'get_height'):
                    new_ax.bar(patch.get_x(), patch.get_height(), 
                            width=patch.get_width(), color=patch.get_facecolor())
            
            # Copy labels and title
            new_ax.set_title(orig_ax.get_title(), fontsize=14, pad=20)
            new_ax.set_xlabel(orig_ax.get_xlabel(), fontsize=12)
            new_ax.set_ylabel(orig_ax.get_ylabel(), fontsize=12)
            
            # Set axis limits
            new_ax.set_xlim(orig_ax.get_xlim())
            new_ax.set_ylim(orig_ax.get_ylim())
        
        # Create canvas with the fresh figure
        canvas = FigureCanvas(new_fig)
        canvas.setMinimumSize(400, 300)
        
        # Add the canvas
        self.current_plot_layout.addWidget(canvas)
        
        # Add stretch to push everything to top
        self.current_plot_layout.addStretch()
        
        canvas.draw()

    def _send_message(self):
        """Send the current message"""
        message = self.input_field.toPlainText().strip()
        if not message:
            return
        
        # Display user message
        self._append_message("You", message)
        
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
            self._append_message("AI Assistant", ai_response)
            
            # Check for plot triggers
            self._check_plot_triggers(ai_response, user_message)
            
        except Exception as e:
            error_msg = f"Error getting AI response: {str(e)}"
            self._append_message("System", error_msg)

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
        """Generate default plot and display it inline"""
        try:
            fig = prepare_example_plot()
            self._add_inline_plot(fig, "Sales Analysis")
            
            # Also send to plot view for backward compatibility
            if self.plot_view:
                self.plot_view.show_plot(fig)
                
            self._append_message("System", "Generated plot above. Click on it to view in the right panel.")
        except Exception as e:
            self._append_message("System", f"Error displaying plot: {str(e)}")

    def trigger_natural_plot_request(self, request: str):
        """Handle natural language plot requests using the plotting engine"""
        try:
            # Use the plotting engine to handle the request
            fig = self.plotting_engine.handle_plot_request(request)
            plot_name = f"Plot: {request[:30]}..."
            self._add_inline_plot(fig, plot_name)
            
            # Also send to plot view for backward compatibility
            if self.plot_view:
                self.plot_view.show_plot(fig)
                
            self._append_message("System", f"Generated plot above. Click to view in the right panel.")
        except Exception as e:
            self._append_message("System", f"Error generating plot: {str(e)}")

    def trigger_specific_plot(self, plot_type: str):
        """Generate and display a specific type of plot"""
        try:
            plot_function = self.plot_mapping.get(plot_type, prepare_example_plot)
            fig = plot_function()
            
            plot_names = {
                'boxplot': 'Accelerometer Comparison',
                'histogram': 'Temperature Distribution',
                'correlation': 'Feature Correlation Matrix',
                'time series': 'Time Series Analysis',
                'frequency': 'Frequency Domain Analysis',
                'scatter': 'Feature Relationships'
            }
            plot_name = plot_names.get(plot_type, 'Data Analysis')
            
            self._add_inline_plot(fig, plot_name)
            
            # Also send to plot view for backward compatibility
            if self.plot_view:
                self.plot_view.show_plot(fig)
                
            self._append_message("System", f"Generated {plot_name.lower()} plot above. Click to view in the right panel.")
        except Exception as e:
            self._append_message("System", f"Error displaying {plot_type} plot: {str(e)}")

    def show_sales_plot(self):
        """Alias for trigger_plot_display for backward compatibility"""
        self.trigger_plot_display()
    
    def set_dataframe(self, df):
        """Set the dataframe for analysis"""
        # Store the dataframe for use in plotting
        self.dataframe = df
        if hasattr(self.plotting_engine, 'set_dataframe'):
            self.plotting_engine.set_dataframe(df)