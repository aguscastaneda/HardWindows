from PyQt5 import QtWidgets, QtCore
from core.system_utils import list_installed_apps, get_system_info
from core.cache_utils import clear_temp
from core.permissions import is_admin
import shutil
import psutil
import os

class ManagerPage(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        main = QtWidgets.QVBoxLayout(self)
        title = QtWidgets.QLabel("Manager - Usuario")
        title.setObjectName("titleLabel")
        main.addWidget(title)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        left = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left)

        # Installed apps list
        left_layout.addWidget(QtWidgets.QLabel("Aplicaciones instaladas"))
        self.apps_list = QtWidgets.QListWidget()
        left_layout.addWidget(self.apps_list)

        btn_open = QtWidgets.QPushButton("Actualizar lista")
        btn_open.clicked.connect(self.load_apps)
        left_layout.addWidget(btn_open)

        right = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right)

        # Storage
        right_layout.addWidget(QtWidgets.QLabel("Almacenamiento"))
        self.storage_info = QtWidgets.QLabel("")
        right_layout.addWidget(self.storage_info)

        btn_clear_cache = QtWidgets.QPushButton("Borrar caché (temp)")
        btn_clear_cache.clicked.connect(self.on_clear_cache)
        right_layout.addWidget(btn_clear_cache)

        # filler
        right_layout.addStretch(1)

        splitter.addWidget(left)
        splitter.addWidget(right)
        main.addWidget(splitter)

        self.load_system()
        self.load_apps()

    def load_apps(self):
        self.apps_list.clear()
        apps = list_installed_apps()
        if not apps:
            self.apps_list.addItem("No se encontraron aplicaciones instaladas (o falta permiso).")
            return
        for a in apps:
            name = a.get("name", "Sin nombre")
            version = a.get("version", "")
            self.apps_list.addItem(f"{name} {version}")

    def load_system(self):
        info = get_system_info()
        text = ""
        for k, v in info.items():
            text += f"{k}: {v}\n"
        # disk usage summary
        try:
            parts = psutil.disk_partitions()
            for p in parts:
                try:
                    u = psutil.disk_usage(p.mountpoint)
                    text += f"Partición {p.device} ({p.mountpoint}): {u.percent}%\n"
                except Exception:
                    continue
        except Exception:
            pass
        self.storage_info.setText(text)

    def on_clear_cache(self):
        if not is_admin():
            QtWidgets.QMessageBox.warning(self, "Permisos insuficientes", "Se requieren permisos de administrador...")
            return
        deleted, freed = clear_temp()
        msg = f"Archivos eliminados: {deleted}\nEspacio liberado: {freed / (1024**2):.2f} MB"
        QtWidgets.QMessageBox.information(self, "Cache limpiada", msg)
    