# gui/views/model_view.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class ModelView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # Placeholder until you hook up your model
        self.placeholder = QLabel("Model summary will appear here")
        layout.addWidget(self.placeholder)

    def set_dataframe(self, df):
        """
        df is a pandas.DataFrame.
        Here you’ll train or evaluate your discriminative model
        (e.g. logistic regression), compute feature importances or scores,
        and update child widgets.
        """
        # Example stub:
        n = len(df)
        self.placeholder.setText(f"Ready to train on {n} samples…")
