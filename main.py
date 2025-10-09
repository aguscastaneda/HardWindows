import sys
import os
from PyQt5 import QtWidgets, QtGui
from ui.main_window import MainWindow
from core.permissions import is_admin
from core.policies import reset_all_to_allowed

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

    # Si es admin, restaurar politicas globales a permitido
    try:
        if is_admin():
            reset_all_to_allowed()
    except Exception:
        pass

    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
