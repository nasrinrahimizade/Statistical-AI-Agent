import sys
from PySide6.QtWidgets import QApplication
from gui.main_window     import MainWindow

def main():
    app    = QApplication(sys.argv)
    window = MainWindow()
    window.show()                    # <— ensures the window is shown
    sys.exit(app.exec())             # <— starts the Qt event loop

if __name__ == "__main__":
    main()
