# gui/views/data_view.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableView

class DataView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.table = QTableView()
        layout.addWidget(self.table)

    def set_dataframe(self, df):
        # TODO: convert `df` (a pandas.DataFrame) into a Qt model
        # and attach it to self.table.setModel(...)
        pass
