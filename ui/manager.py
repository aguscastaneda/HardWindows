from PyQt5 import QtWidgets, QtCore
from core.system_utils import list_installed_apps, get_system_info, open_application, close_application, uninstall_application
from core.cache_utils import clear_temp
from core.permissions import is_admin, get_current_user, lock_screen, logoff
import psutil

class ManagerPage(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        main = QtWidgets.QVBoxLayout(self)
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(15)
        
        # Título
        title = QtWidgets.QLabel("Manager - Usuario")
        title.setObjectName("titleLabel")
        title.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        main.addWidget(title)

        # Splitter principal vertical: arriba apps, abajo almacenamiento/seguridad
        main_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        main_splitter.setChildrenCollapsible(False)

        # Arriba: panel de aplicaciones a todo el ancho
        apps_panel = QtWidgets.QWidget()
        apps_layout = QtWidgets.QVBoxLayout(apps_panel)
        apps_layout.setSpacing(10)

        lbl_apps = QtWidgets.QLabel("Aplicaciones instaladas")
        lbl_apps.setStyleSheet("font-weight: bold; font-size: 14px; color: #00c8ff;")
        apps_layout.addWidget(lbl_apps)

        self.apps_list = QtWidgets.QListWidget()
        self.apps_list.setStyleSheet("""
            QListWidget {
                background-color: #1a1a2e;
                color: #ffffff;
                border: 1px solid #2e2e3e;
                border-radius: 6px;
                padding: 6px;
            }
            QListWidget::item:selected {
                background-color: #00c8ff;
                color: #000000;
            }
        """)
        self.apps_list.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        apps_layout.addWidget(self.apps_list, 1)

        btns_apps = QtWidgets.QHBoxLayout()
        self.btn_refresh = QtWidgets.QPushButton("Actualizar")
        self.btn_open = QtWidgets.QPushButton("Abrir")
        self.btn_close = QtWidgets.QPushButton("Cerrar")
        self.btn_uninstall = QtWidgets.QPushButton("Desinstalar")
        for b in (self.btn_refresh, self.btn_open, self.btn_close, self.btn_uninstall):
            b.setStyleSheet("padding: 6px; font-weight: bold;")
            btns_apps.addWidget(b)
        apps_layout.addLayout(btns_apps, 0)

        # Conectar señales de apps
        self.btn_refresh.clicked.connect(self.load_apps)
        self.btn_open.clicked.connect(self.on_open_app)
        self.btn_close.clicked.connect(self.on_close_app)
        self.btn_uninstall.clicked.connect(self.on_uninstall_app)

        main_splitter.addWidget(apps_panel)

        # Abajo: splitter horizontal entre almacenamiento y seguridad
        bottom_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        bottom_splitter.setChildrenCollapsible(False)

        # Almacenamiento (card)
        storage_card = QtWidgets.QFrame()
        storage_card.setFrameShape(QtWidgets.QFrame.NoFrame)
        storage_layout = QtWidgets.QVBoxLayout(storage_card)
        storage_layout.setContentsMargins(0, 0, 0, 0)
        storage_layout.setSpacing(8)

        lbl_storage = QtWidgets.QLabel("Almacenamiento")
        lbl_storage.setStyleSheet("font-weight: bold; font-size: 14px; color: #00c8ff;")
        storage_layout.addWidget(lbl_storage)

        self.storage_info = QtWidgets.QTextEdit("")
        self.storage_info.setReadOnly(True)
        self.storage_info.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a2e;
                color: #ffffff;
                border: 1px solid #2e2e3e;
                border-radius: 6px;
                padding: 6px;
            }
        """)
        self.storage_info.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        storage_layout.addWidget(self.storage_info, 1)

        btn_clear_cache = QtWidgets.QPushButton("Borrar caché (temp)")
        btn_clear_cache.setStyleSheet("padding: 8px; font-weight: bold;")
        btn_clear_cache.clicked.connect(self.on_clear_cache)
        storage_layout.addWidget(btn_clear_cache, 0)

        # Seguridad (card)
        security_card = QtWidgets.QFrame()
        security_card.setFrameShape(QtWidgets.QFrame.NoFrame)
        security_layout = QtWidgets.QVBoxLayout(security_card)
        security_layout.setContentsMargins(0, 0, 0, 0)
        security_layout.setSpacing(8)

        lbl_security = QtWidgets.QLabel("Seguridad")
        lbl_security.setStyleSheet("font-weight: bold; font-size: 14px; color: #00c8ff;")
        security_layout.addWidget(lbl_security)

        self.security_info = QtWidgets.QLabel("")
        self.security_info.setStyleSheet("""
            QLabel {
                background-color: #222233;
                color: #ffffff;
                border: 1px solid #333355;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        self.security_info.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.security_info.setMinimumHeight(120)
        security_layout.addWidget(self.security_info, 1)

        sec_btns = QtWidgets.QHBoxLayout()
        self.btn_lock = QtWidgets.QPushButton("Bloquear pantalla")
        self.btn_logoff = QtWidgets.QPushButton("Cerrar sesión")
        for b in (self.btn_lock, self.btn_logoff):
            b.setStyleSheet("padding: 8px; font-weight: bold;")
            sec_btns.addWidget(b)
        security_layout.addLayout(sec_btns, 0)

        # Señales de seguridad
        self.btn_lock.clicked.connect(self.on_lock)
        self.btn_logoff.clicked.connect(self.on_logoff)

        bottom_splitter.addWidget(storage_card)
        bottom_splitter.addWidget(security_card)
        bottom_splitter.setStretchFactor(0, 1)
        bottom_splitter.setStretchFactor(1, 1)

        main_splitter.addWidget(bottom_splitter)
        main_splitter.setStretchFactor(0, 3)  # Arriba más alto
        main_splitter.setStretchFactor(1, 2)  # Abajo un poco menos

        main.addWidget(main_splitter)

        # Inicializar
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
            path = a.get("path", "")
            self.apps_list.addItem(f"{name} | {version} | {path}")

    def load_system(self):
        info = get_system_info()
        text = ""
        for k, v in info.items():
            text += f"{k}: {v}\n"
        # Resumen de discos
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
        self.storage_info.setPlainText(text)

        # Seguridad
        user = get_current_user()
        admin = "Sí" if is_admin() else "No"
        self.security_info.setText(f"Usuario actual: {user}\nPermisos de administrador: {admin}")

    def on_clear_cache(self):
        if not is_admin():
            QtWidgets.QMessageBox.warning(self, "Permisos insuficientes", "Se requieren permisos de administrador...")
            return
        deleted, freed = clear_temp()
        msg = f"Archivos eliminados: {deleted}\nEspacio liberado: {freed / (1024**2):.2f} MB"
        QtWidgets.QMessageBox.information(self, "Cache limpiada", msg)
        self.load_system()

    def on_open_app(self):
        item = self.apps_list.currentItem()
        if not item:
            return
        parts = [p.strip() for p in item.text().split("|")]
        path = parts[2] if len(parts) > 2 else ""
        target = path or parts[0]
        if not open_application(target):
            QtWidgets.QMessageBox.warning(self, "Error", "No se pudo abrir la aplicación seleccionada.")

    def on_close_app(self):
        item = self.apps_list.currentItem()
        if not item:
            return
        parts = [p.strip() for p in item.text().split("|")]
        name = parts[0]
        if not close_application(name):
            QtWidgets.QMessageBox.warning(self, "Error", "No se pudo cerrar la aplicación seleccionada.")

    def on_uninstall_app(self):
        item = self.apps_list.currentItem()
        if not item:
            return
        parts = [p.strip() for p in item.text().split("|")]
        name = parts[0]
        confirm = QtWidgets.QMessageBox.question(self, "Confirmar desinstalación", 
                                                 f"¿Seguro que deseas desinstalar {name}?")
        if confirm == QtWidgets.QMessageBox.Yes:
            if not uninstall_application(name):
                QtWidgets.QMessageBox.warning(self, "Error", "No se pudo desinstalar la aplicación seleccionada.")
            else:
                self.load_apps()

    def on_lock(self):
        if not lock_screen():
            QtWidgets.QMessageBox.warning(self, "Error", "No se pudo bloquear la pantalla.")

    def on_logoff(self):
        if not is_admin():
            QtWidgets.QMessageBox.warning(self, "Permisos insuficientes", "Se requieren permisos para cerrar sesión.")
            return
        if not logoff():
            QtWidgets.QMessageBox.warning(self, "Error", "No se pudo cerrar la sesión.")
