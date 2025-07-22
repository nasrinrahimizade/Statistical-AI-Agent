# gui/views/stats_view.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class StatsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # Placeholder label until you compute real stats
        self.placeholder = QLabel("Statistics will appear here")
        layout.addWidget(self.placeholder)

    def set_dataframe(self, df):
        """
        df is a pandas.DataFrame.
        Here you’ll compute whatever stats you need (mean, std, etc.)
        and update child widgets.
        """
        # Example: just show number of rows
        n = len(df)
        self.placeholder.setText(f"Loaded {n} rows; stats coming soon…")
