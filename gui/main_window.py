# from PySide6.QtWidgets import (
#     QMainWindow, QStatusBar, QFileDialog,
#     QStackedWidget, QToolBar, QMessageBox
# )
# from PySide6.QtCore import Qt
# from PySide6.QtGui import QAction
# from gui.views.plot_view import PlotView
# from gui.views.chat_view import ChatView
# from gui.views.help_view import HelpView
# from core.data_loader import load_dataset

# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("AI Dataset Analyzer")
#         self.resize(1200, 800)

#         self._createMenuBar()
#         self._createToolBar()
#         self._createStatusBar()
#         self._createCentralWidget()

#     def _createMenuBar(self):
#         menuBar = self.menuBar()
#         fileMenu = menuBar.addMenu("File")

#         openAction = QAction("Open Dataset", self)
#         openAction.triggered.connect(self.openDataset)
#         fileMenu.addAction(openAction)

#         # Help menu
#         helpMenu = menuBar.addMenu("Help")
#         openHelpAction = QAction("Open Help", self)
#         openHelpAction.triggered.connect(lambda: self.stack.setCurrentIndex(2))
#         helpMenu.addAction(openHelpAction)

#     def _createToolBar(self):
#         toolBar = QToolBar("Main Toolbar")
#         toolBar.setMovable(False)  # Prevent toolbar from being moved
#         toolBar.setFloatable(False)  # Prevent toolbar from being floated
#         self.addToolBar(Qt.TopToolBarArea, toolBar)
        
#         # Add toolbar actions
#         openAction = QAction("Open Dataset", self)
#         openAction.triggered.connect(self.openDataset)
#         toolBar.addAction(openAction)
        
#         toolBar.addSeparator()
        
#         # Add view switching actions
#         plotAction = QAction("Plots", self)
#         plotAction.triggered.connect(lambda: self.stack.setCurrentIndex(0))
#         toolBar.addAction(plotAction)
        
#         chatAction = QAction("Chat", self)
#         chatAction.triggered.connect(lambda: self.stack.setCurrentIndex(1))
#         toolBar.addAction(chatAction)

#         helpAction = QAction("Help", self)
#         helpAction.triggered.connect(lambda: self.stack.setCurrentIndex(2))
#         toolBar.addAction(helpAction)

#     def _createStatusBar(self):
#         statusBar = QStatusBar()
#         self.setStatusBar(statusBar)

#     def _createCentralWidget(self):
#         self.stack = QStackedWidget()
#         # instantiate views
#         self.plotView = PlotView()
#         self.chatView = ChatView(plot_view=self.plotView)
#         self.helpView = HelpView()

#         # add to stack
#         self.stack.addWidget(self.plotView)
#         self.stack.addWidget(self.chatView)
#         self.stack.addWidget(self.helpView)

#         self.setCentralWidget(self.stack)
        
#         # Set chat view as the default first screen
#         self.stack.setCurrentIndex(1)  # Chat view is at index 1



#     def openDataset(self):
#         fileName, _ = QFileDialog.getOpenFileName(
#             self, "Open Dataset", "", "CSV Files (*.csv);;All Files (*)"
#         )
#         if fileName:
#             df = load_dataset(fileName)
#             # distribute to views
#             self.plotView.set_dataframe(df)
#             self.chatView.set_dataframe(df)

#     def showHelpDialog(self):
#         # Kept for backward compatibility; open full Help view instead
#         self.stack.setCurrentIndex(2)



##main_window.py####
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
from gui.views.help_view import HelpView
from core.data_loader import load_dataset

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Dataset Analyzer")
        self.resize(1400, 900)  # Slightly larger to accommodate side-by-side layout

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
        openHelpAction = QAction("Open Help", self)
        openHelpAction.triggered.connect(lambda: self.stack.setCurrentIndex(4))  # Help view is at index 4
        helpMenu.addAction(openHelpAction)
        
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
        
        # Add view switching actions - simplified navigation
        chatAction = QAction("AI Chat & Plots", self)
        chatAction.triggered.connect(lambda: self.stack.setCurrentIndex(3))
        toolBar.addAction(chatAction)
        
        dataAction = QAction("Raw Data", self)
        dataAction.triggered.connect(lambda: self.stack.setCurrentIndex(0))
        toolBar.addAction(dataAction)
        
        statsAction = QAction("Statistics", self)
        statsAction.triggered.connect(lambda: self.stack.setCurrentIndex(1))
        toolBar.addAction(statsAction)
        
        helpAction = QAction("Help", self)
        helpAction.triggered.connect(lambda: self.stack.setCurrentIndex(4))
        toolBar.addAction(helpAction)

    def _createStatusBar(self):
        statusBar = QStatusBar()
        self.setStatusBar(statusBar)

    def _createCentralWidget(self):
        self.stack = QStackedWidget()
        # instantiate views
        self.dataView = DataView()
        self.statsView = StatsView()
        self.plotView = PlotView()  # Keep for backward compatibility
        self.chatView = ChatView(plot_view=self.plotView)
        self.helpView = HelpView()

        # add to stack
        self.stack.addWidget(self.dataView)      # Index 0
        self.stack.addWidget(self.statsView)     # Index 1
        self.stack.addWidget(self.plotView)      # Index 2 - Keep for backward compatibility
        self.stack.addWidget(self.chatView)      # Index 3
        self.stack.addWidget(self.helpView)      # Index 4

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
            
            # Update status bar to show loaded dataset
            self.statusBar().showMessage(f"Dataset loaded: {fileName}")

    def showHelpDialog(self):
        # Open full Help view instead of dialog
        self.stack.setCurrentIndex(4)