# gui/views/plot_view.py

from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
from matplotlib.figure import Figure

class PlotView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # Set up a Matplotlib canvas
        self.figure = Figure()
        self.canvas = Canvas(self.figure)
        layout.addWidget(self.canvas)

    def set_dataframe(self, df):
        """
        df is a pandas.DataFrame.
        Here you can plot things like time series or histograms.
        """
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        # Example stub: empty plot with title
        ax.set_title("Plots will appear here")
        self.canvas.draw()
