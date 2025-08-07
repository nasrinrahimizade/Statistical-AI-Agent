from PySide6.QtWidgets import (
    QMainWindow, QStatusBar, QFileDialog,
    QStackedWidget, QToolBar
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
        toolBar.setMovable(False)  # Prevent toolbar from being moved
        toolBar.setFloatable(False)  # Prevent toolbar from being floated
        self.addToolBar(Qt.TopToolBarArea, toolBar)
        
        # Add toolbar actions
        openAction = QAction("Open Dataset", self)
        openAction.triggered.connect(self.openDataset)
        toolBar.addAction(openAction)
        
        toolBar.addSeparator()
        
        # Add view switching actions
        dataAction = QAction("Data View", self)
        dataAction.triggered.connect(lambda: self.stack.setCurrentIndex(0))
        toolBar.addAction(dataAction)
        
        statsAction = QAction("Statistics", self)
        statsAction.triggered.connect(lambda: self.stack.setCurrentIndex(1))
        toolBar.addAction(statsAction)
        
        modelAction = QAction("Model", self)
        modelAction.triggered.connect(lambda: self.stack.setCurrentIndex(2))
        toolBar.addAction(modelAction)
        
        plotAction = QAction("Plots", self)
        plotAction.triggered.connect(lambda: self.stack.setCurrentIndex(3))
        toolBar.addAction(plotAction)
        
        chatAction = QAction("Chat", self)
        chatAction.triggered.connect(lambda: self.stack.setCurrentIndex(4))
        toolBar.addAction(chatAction)

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
        self.chatView = ChatView(plot_view=self.plotView)

        # add to stack
        self.stack.addWidget(self.dataView)
        self.stack.addWidget(self.statsView)
        self.stack.addWidget(self.modelView)
        self.stack.addWidget(self.plotView)
        self.stack.addWidget(self.chatView)

        self.setCentralWidget(self.stack)
        
        # Set chat view as the default first screen
        self.stack.setCurrentIndex(4)  # Chat view is at index 4



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
