from PySide6.QtWidgets import (
    QMainWindow, QStatusBar, QFileDialog,
    QDockWidget, QListWidget, QStackedWidget, QToolBar
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from gui.views.data_view import DataView
from gui.views.stats_view import StatsView
from gui.views.model_view import ModelView
from gui.views.plot_view import PlotView
from gui.views.chat_view import ChatView
from core.data_loader import load_dataset

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Dataset Analyzer")
        self.resize(1200, 800)

        self._createMenuBar()
        self._createToolBar()
        self._createStatusBar()
        self._createCentralWidget()
        self._createDockWidgets()

    def _createMenuBar(self):
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu("File")

        openAction = QAction("Open Dataset", self)
        openAction.triggered.connect(self.openDataset)
        fileMenu.addAction(openAction)

        exitAction = QAction("Exit", self)
        exitAction.triggered.connect(self.close)
        fileMenu.addAction(exitAction)

    def _createToolBar(self):
        toolBar = QToolBar("Main Toolbar")
        self.addToolBar(Qt.TopToolBarArea, toolBar)
        # TODO: add toolbar actions for stats, model, plots, chat

    def _createStatusBar(self):
        statusBar = QStatusBar()
        self.setStatusBar(statusBar)

    def _createCentralWidget(self):
        self.stack = QStackedWidget()
        # instantiate views
        self.dataView = DataView()
        self.statsView = StatsView()
        self.modelView = ModelView()
        self.plotView = PlotView()
        self.chatView = ChatView()

        # add to stack
        self.stack.addWidget(self.dataView)
        self.stack.addWidget(self.statsView)
        self.stack.addWidget(self.modelView)
        self.stack.addWidget(self.plotView)
        self.stack.addWidget(self.chatView)

        self.setCentralWidget(self.stack)

    def _createDockWidgets(self):
        dock = QDockWidget("Views", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        listWidget = QListWidget()
        # Increase font size for better visibility
        font = listWidget.font()
        font.setPointSize(12)
        listWidget.setFont(font)

        views = ["Data View", "Statistics", "Model", "Plots", "Chat"]
        listWidget.addItems(views)
        listWidget.currentRowChanged.connect(self.stack.setCurrentIndex)

        dock.setWidget(listWidget)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)

    def openDataset(self):
        fileName, _ = QFileDialog.getOpenFileName(
            self, "Open Dataset", "", "CSV Files (*.csv);;All Files (*)"
        )
        if fileName:
            df = load_dataset(fileName)
            # distribute to views
            self.dataView.set_dataframe(df)
            self.statsView.set_dataframe(df)
            self.modelView.set_dataframe(df)
            self.plotView.set_dataframe(df)
            self.chatView.set_dataframe(df)
