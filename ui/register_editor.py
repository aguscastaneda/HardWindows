from PyQt5 import QtWidgets, QtCore
import os
from core.user_utils import list_local_users, create_user, delete_user, change_password
from core.permissions import is_admin
import psutil

class RegisterEditorPage(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        title = QtWidgets.QLabel("Editor de Registro - Sistema")
        title.setObjectName("titleLabel")
        title.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        layout.addWidget(title)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        left = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left)
        left_layout.setSpacing(10)

        # Tree de carpetas clave (simplificado): mostrar Program Files, Windows, Users
        lbl_tree = QtWidgets.QLabel("Estructura de carpetas")
        lbl_tree.setStyleSheet("font-weight: bold; font-size: 14px; color: #00c8ff;")
        left_layout.addWidget(lbl_tree)
        self.tree = QtWidgets.QTreeWidget()
        self.tree.setHeaderLabels(["Ruta", "Tipo"])
        self.tree.setStyleSheet(
            """
            QTreeWidget {
                background-color: #1a1a2e;
                color: #ffffff;
                border: 1px solid #2e2e3e;
                border-radius: 6px;
            }
            QTreeWidget::item:selected { background-color: #00c8ff; color: #000000; }
            """
        )
        left_layout.addWidget(self.tree)
        self.load_folder_tree()

        right = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right)
        right_layout.setSpacing(12)

        # ABM usuarios
        lbl_users = QtWidgets.QLabel("Usuarios locales")
        lbl_users.setStyleSheet("font-weight: bold; font-size: 14px; color: #00c8ff;")
        right_layout.addWidget(lbl_users)
        self.users_list = QtWidgets.QListWidget()
        self.users_list.setStyleSheet(
            """
            QListWidget {
                background-color: #1a1a2e;
                color: #ffffff;
                border: 1px solid #2e2e3e;
                border-radius: 6px;
                padding: 6px;
            }
            QListWidget::item:selected { background-color: #00c8ff; color: #000000; }
            """
        )
        right_layout.addWidget(self.users_list)
        self.load_users()

        h = QtWidgets.QHBoxLayout()
        self.user_name = QtWidgets.QLineEdit()
        self.user_name.setPlaceholderText("Nombre")
        self.user_pass = QtWidgets.QLineEdit()
        self.user_pass.setPlaceholderText("Contraseña")
        self.user_pass.setEchoMode(QtWidgets.QLineEdit.Password)
        h.addWidget(self.user_name)
        h.addWidget(self.user_pass)
        right_layout.addLayout(h)

        btn_add = QtWidgets.QPushButton("Crear usuario")
        btn_add.clicked.connect(self.on_create_user)
        btn_del = QtWidgets.QPushButton("Eliminar seleccionado")
        btn_del.clicked.connect(self.on_delete_user)
        for b in (btn_add, btn_del):
            b.setStyleSheet("padding: 8px; font-weight: bold;")
        right_layout.addWidget(btn_add)
        right_layout.addWidget(btn_del)

        # Cambio de contraseña
        lbl_change = QtWidgets.QLabel("Cambiar contraseña")
        lbl_change.setStyleSheet("font-weight: bold; font-size: 14px; color: #00c8ff;")
        right_layout.addWidget(lbl_change)
        change_row = QtWidgets.QHBoxLayout()
        self.new_pass = QtWidgets.QLineEdit()
        self.new_pass.setPlaceholderText("Nueva contraseña")
        self.new_pass.setEchoMode(QtWidgets.QLineEdit.Password)
        btn_change = QtWidgets.QPushButton("Actualizar contraseña")
        btn_change.setStyleSheet("padding: 8px; font-weight: bold;")
        btn_change.clicked.connect(self.on_change_password)
        change_row.addWidget(self.new_pass)
        change_row.addWidget(btn_change)
        right_layout.addLayout(change_row)

        # Process controls
        lbl_proc = QtWidgets.QLabel("Procesos (seleccionar PID y terminar)")
        lbl_proc.setStyleSheet("font-weight: bold; font-size: 14px; color: #00c8ff;")
        right_layout.addWidget(lbl_proc)
        self.proc_table = QtWidgets.QTableWidget(0, 2)
        self.proc_table.setHorizontalHeaderLabels(["PID", "Nombre"])
        self.proc_table.setStyleSheet(
            """
            QTableWidget {
                background-color: #1a1a2e;
                color: #ffffff;
                border: 1px solid #2e2e3e;
                border-radius: 6px;
                gridline-color: #2e2e3e;
            }
            QHeaderView::section {
                background-color: #0b1220;
                color: #bcd7ff;
                padding: 6px;
                border: none;
            }
            """
        )
        right_layout.addWidget(self.proc_table)
        btn_refresh_proc = QtWidgets.QPushButton("Actualizar procesos")
        btn_refresh_proc.clicked.connect(self.load_processes)
        btn_kill = QtWidgets.QPushButton("Terminar proceso seleccionado")
        btn_kill.clicked.connect(self.kill_selected)
        for b in (btn_refresh_proc, btn_kill):
            b.setStyleSheet("padding: 8px; font-weight: bold;")
        right_layout.addWidget(btn_refresh_proc)
        right_layout.addWidget(btn_kill)

        splitter.addWidget(left)
        splitter.addWidget(right)
        layout.addWidget(splitter)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)

        # power buttons
        box = QtWidgets.QHBoxLayout()
        btn_shutdown = QtWidgets.QPushButton("Apagar ahora")
        btn_reboot = QtWidgets.QPushButton("Reiniciar ahora")
        btn_shutdown.clicked.connect(self.on_shutdown)
        btn_reboot.clicked.connect(self.on_reboot)
        for b in (btn_shutdown, btn_reboot):
            b.setStyleSheet("padding: 8px; font-weight: bold;")
        box.addWidget(btn_shutdown)
        box.addWidget(btn_reboot)
        layout.addLayout(box)

        self.load_processes()

    def load_folder_tree(self):
        self.tree.clear()
        roots = [os.getenv("SystemRoot", r"C:\Windows"), os.getenv("ProgramFiles", r"C:\Program Files"), os.path.expanduser("~")]
        for r in roots:
            root_item = QtWidgets.QTreeWidgetItem([r, "Carpeta"])
            self.tree.addTopLevelItem(root_item)
            # listar subcarpetas principales (no profundizar demasiado)
            try:
                for name in os.listdir(r)[:30]:
                    path = os.path.join(r, name)
                    if os.path.isdir(path):
                        child = QtWidgets.QTreeWidgetItem([path, "Carpeta"])
                        root_item.addChild(child)
            except Exception:
                continue

    def load_users(self):
        self.users_list.clear()
        users = list_local_users()
        if not users:
            self.users_list.addItem("No se pudieron listar usuarios.")
            return
        for u in users:
            self.users_list.addItem(u)

    def on_create_user(self):
        name = self.user_name.text().strip()
        pwd = self.user_pass.text().strip()
        if not name or not pwd:
            QtWidgets.QMessageBox.warning(self, "Validación", "Complete nombre y contraseña")
            return
        ok, msg = create_user(name, pwd)
        if ok:
            QtWidgets.QMessageBox.information(self, "Usuario", msg)
            self.load_users()
        else:
            QtWidgets.QMessageBox.warning(self, "Error", msg)

    def on_delete_user(self):
        sel = self.users_list.currentItem()
        if not sel:
            QtWidgets.QMessageBox.warning(self, "Aviso", "Seleccione un usuario")
            return
        username = sel.text()
        ok, msg = delete_user(username)
        if ok:
            QtWidgets.QMessageBox.information(self, "Usuario", msg)
            self.load_users()
        else:
            QtWidgets.QMessageBox.warning(self, "Error", msg)

    def load_processes(self):
        self.proc_table.setRowCount(0)
        for p in psutil.process_iter(attrs=["pid", "name"]):
            try:
                row = self.proc_table.rowCount()
                self.proc_table.insertRow(row)
                self.proc_table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(p.info["pid"])))
                self.proc_table.setItem(row, 1, QtWidgets.QTableWidgetItem(str(p.info.get("name", ""))))
            except Exception:
                continue

    def kill_selected(self):
        sel = self.proc_table.currentRow()
        if sel < 0:
            QtWidgets.QMessageBox.warning(self, "Aviso", "Seleccione un proceso")
            return
        pid_item = self.proc_table.item(sel, 0)
        if not pid_item:
            return
        pid = int(pid_item.text())
        try:
            p = psutil.Process(pid)
            p.terminate()
            p.wait(timeout=3)
            QtWidgets.QMessageBox.information(self, "Listo", f"Proceso {pid} finalizado")
            self.load_processes()
        except psutil.AccessDenied:
            QtWidgets.QMessageBox.warning(self, "Permisos", "Se requieren permisos de administrador...")
        except psutil.NoSuchProcess:
            QtWidgets.QMessageBox.warning(self, "Error", "Proceso inexistente")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", str(e))

    def on_shutdown(self):
        if not is_admin():
            QtWidgets.QMessageBox.warning(self, "Permisos", "Se requieren permisos de administrador...")
            return
        os.system("shutdown /s /t 0")

    def on_reboot(self):
        if not is_admin():
            QtWidgets.QMessageBox.warning(self, "Permisos", "Se requieren permisos de administrador...")
            return
        os.system("shutdown /r /t 0")

    def on_change_password(self):
        sel = self.users_list.currentItem()
        if not sel:
            QtWidgets.QMessageBox.warning(self, "Aviso", "Seleccione un usuario")
            return
        username = sel.text()
        new_pwd = self.new_pass.text().strip()
        if not new_pwd:
            QtWidgets.QMessageBox.warning(self, "Validación", "Ingrese la nueva contraseña")
            return
        ok, msg = change_password(username, new_pwd)
        if ok:
            QtWidgets.QMessageBox.information(self, "Usuario", msg)
            self.new_pass.clear()
        else:
            QtWidgets.QMessageBox.warning(self, "Error", msg)
