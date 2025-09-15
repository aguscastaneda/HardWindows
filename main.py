import sys
import os
from PyQt5 import QtWidgets, QtGui
from ui.main_window import MainWindow

def load_qss(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""

def main():
    app = QtWidgets.QApplication(sys.argv)
    # Cargar estilo QSS
    qss_path = os.path.join(os.path.dirname(__file__), "assets", "qss", "main.qss")
    qss = load_qss(qss_path)
    if qss:
        app.setStyleSheet(qss)

    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
