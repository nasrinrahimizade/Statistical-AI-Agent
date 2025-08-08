from PySide6.QtWidgets import (
    QMainWindow, QStatusBar, QFileDialog,
    QStackedWidget, QToolBar, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from gui.views.data_view import DataView
from gui.views.stats_view import StatsView
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

        # Help menu
        helpMenu = menuBar.addMenu("Help")
        howItWorksAction = QAction("How the program works", self)
        howItWorksAction.triggered.connect(self.showHelpDialog)
        helpMenu.addAction(howItWorksAction)

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
        
        plotAction = QAction("Plots", self)
        plotAction.triggered.connect(lambda: self.stack.setCurrentIndex(2))
        toolBar.addAction(plotAction)
        
        chatAction = QAction("Chat", self)
        chatAction.triggered.connect(lambda: self.stack.setCurrentIndex(3))
        toolBar.addAction(chatAction)

    def _createStatusBar(self):
        statusBar = QStatusBar()
        self.setStatusBar(statusBar)

    def _createCentralWidget(self):
        self.stack = QStackedWidget()
        # instantiate views
        self.dataView = DataView()
        self.statsView = StatsView()
        self.plotView = PlotView()
        self.chatView = ChatView(plot_view=self.plotView)

        # add to stack
        self.stack.addWidget(self.dataView)
        self.stack.addWidget(self.statsView)
        self.stack.addWidget(self.plotView)
        self.stack.addWidget(self.chatView)

        self.setCentralWidget(self.stack)
        
        # Set chat view as the default first screen
        self.stack.setCurrentIndex(3)  # Chat view is at index 3



    def openDataset(self):
        fileName, _ = QFileDialog.getOpenFileName(
            self, "Open Dataset", "", "CSV Files (*.csv);;All Files (*)"
        )
        if fileName:
            df = load_dataset(fileName)
            # distribute to views
            self.dataView.set_dataframe(df)
            self.statsView.set_dataframe(df)
            self.plotView.set_dataframe(df)
            self.chatView.set_dataframe(df)

    def showHelpDialog(self):
        text = (
            "Statistical AI Agent — How it works\n\n"
            "1) Load data: Use File → Open Dataset to select a CSV.\n"
            "2) Explore:\n"
            "   - Data View: browse the raw table.\n"
            "   - Statistics: see summary metrics.\n"
            "   - Plots: view generated visualizations.\n"
            "   - Chat: ask the AI to analyze data or create plots.\n"
            "3) Ask in natural language (e.g., ‘show correlation matrix’, ‘plot temperature histogram’).\n"
            "4) Results appear in the appropriate view (plots in Plots, stats in Statistics).\n\n"
            "Under the hood: PySide6 GUI, a transformers-based AI model, and a plotting engine integrate "
            "to interpret requests, analyze your dataset, and render visualizations."
        )
        QMessageBox.information(self, "How the program works", text)
