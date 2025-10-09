from PyQt5 import QtWidgets, QtCore
import os
from core.user_utils import list_local_users, create_user, delete_user, change_password
from core.permissions import is_admin
from core.policies import get_all_policies, set_policy_value
from widgets import message_box
import psutil

class RegisterEditorPage(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Titulo principal
        title = QtWidgets.QLabel("Editor de Registro - Sistema")
        title.setObjectName("titleLabel")
        title.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: #bcd7ff;")
        layout.addWidget(title)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)

        # Estilo comon para boxes
        group_style = (
            "QGroupBox {"
            "  border: 1px solid #2e2e3e;"
            "  border-radius: 10px;"
            "  margin-top: 18px;"
            "  background-color: #131a2a;"
            "}"
            "QGroupBox::title {"
            "  subcontrol-origin: margin;"
            "  left: 12px;"
            "  padding: 2px 8px;"
            "  color: #00c8ff;"
            "  font-size: 16px;"
            "  font-weight: 600;"
            "}"
        )

        left = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left)
        left_layout.setSpacing(12)



        grp_proc = QtWidgets.QGroupBox("Gestión de Procesos")
        grp_proc.setStyleSheet(group_style)
        grp_proc.setMinimumHeight(580)
        proc_layout = QtWidgets.QVBoxLayout(grp_proc)
        proc_layout.setContentsMargins(12, 12, 12, 12)

        self.proc_table = QtWidgets.QTableWidget(0, 2)
        self.proc_table.setHorizontalHeaderLabels(["Nombre", "PID"])
        self.proc_table.setStyleSheet(
            """
            QTableWidget {
                background-color: #0f1726;
                color: #ffffff;
                border: 1px solid #2e2e3e;
                border-radius: 8px;
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
        header = self.proc_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        proc_layout.addWidget(self.proc_table)

        btns_row = QtWidgets.QHBoxLayout()
        btns_row.setSpacing(8)
        btn_refresh_proc = QtWidgets.QPushButton("Actualizar procesos")
        btn_refresh_proc.clicked.connect(self.load_processes)
        btns_row.addWidget(btn_refresh_proc)

        self.proc_pid_input = QtWidgets.QLineEdit()
        self.proc_pid_input.setPlaceholderText("PID")
        self.proc_pid_input.setFixedWidth(140)
        btns_row.addWidget(self.proc_pid_input)

        btn_kill_by_pid = QtWidgets.QPushButton("Terminar Proceso")
        btn_kill_by_pid.clicked.connect(self.terminate_by_pid)
        btns_row.addWidget(btn_kill_by_pid)
        btns_row.addStretch(1)

        for b in (btn_refresh_proc, btn_kill_by_pid):
            b.setStyleSheet("padding: 8px 12px; font-weight: 600;")

        proc_layout.addLayout(btns_row)
        left_layout.addWidget(grp_proc)

        right = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right)
        right_layout.setSpacing(15)

        grp_users = QtWidgets.QGroupBox("Usuarios locales")
        grp_users.setStyleSheet(group_style)
        grp_users.setMinimumHeight(300)
        users_layout = QtWidgets.QVBoxLayout(grp_users)
        users_layout.setContentsMargins(12, 12, 12, 12)
        self.users_list = QtWidgets.QListWidget()
        self.users_list.setStyleSheet(
            """
            QListWidget {
                background-color: #0f1726;
                color: #ffffff;
                border: 1px solid #2e2e3e;
                border-radius: 8px;
                padding: 6px;
            }
            QListWidget::item:selected { background-color: #00c8ff; color: #000000; }
            """
        )
        users_layout.addWidget(self.users_list)

        h = QtWidgets.QHBoxLayout()
        self.user_name = QtWidgets.QLineEdit()
        self.user_name.setPlaceholderText("Nombre")
        self.user_pass = QtWidgets.QLineEdit()
        self.user_pass.setPlaceholderText("Contraseña")
        self.user_pass.setEchoMode(QtWidgets.QLineEdit.Password)
        h.addWidget(self.user_name)
        h.addWidget(self.user_pass)
        users_layout.addLayout(h)

        btn_add = QtWidgets.QPushButton("Crear usuario")
        btn_add.clicked.connect(self.on_create_user)
        btn_del = QtWidgets.QPushButton("Eliminar seleccionado")
        btn_del.clicked.connect(self.on_delete_user)

        for b in (btn_add, btn_del):
            b.setStyleSheet("padding: 8px 12px; font-weight: 600;")

        users_layout.addWidget(btn_add)
        users_layout.addWidget(btn_del)
        right_layout.addWidget(grp_users)

        grp_pwd = QtWidgets.QGroupBox("Cambiar contraseña")
        grp_pwd.setStyleSheet(group_style)
        grp_pwd.setMinimumHeight(140)
        pwd_layout = QtWidgets.QHBoxLayout(grp_pwd)
        pwd_layout.setContentsMargins(12, 12, 12, 12)
        self.new_pass = QtWidgets.QLineEdit()
        self.new_pass.setPlaceholderText("Nueva contraseña")
        self.new_pass.setEchoMode(QtWidgets.QLineEdit.Password)
        btn_change = QtWidgets.QPushButton("Actualizar contraseña")
        btn_change.setStyleSheet("padding: 8px 12px; font-weight: 600;")
        btn_change.clicked.connect(self.on_change_password)
        pwd_layout.addWidget(self.new_pass)
        pwd_layout.addWidget(btn_change)
        right_layout.addWidget(grp_pwd)

        splitter.addWidget(left)
        splitter.addWidget(right)
        layout.addWidget(splitter)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        box = QtWidgets.QHBoxLayout()
        btn_shutdown = QtWidgets.QPushButton("Apagar ahora")
        btn_reboot = QtWidgets.QPushButton("Reiniciar ahora")
        btn_shutdown.clicked.connect(self.on_shutdown)
        btn_reboot.clicked.connect(self.on_reboot)

        for b in (btn_shutdown, btn_reboot):
            b.setStyleSheet("padding: 8px 12px; font-weight: 600;")

        box.addWidget(btn_shutdown)
        box.addWidget(btn_reboot)
        layout.addLayout(box)

        self.load_users()
        self.load_processes()


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

    def load_processes(self):
        self.proc_table.setRowCount(0)
        for p in psutil.process_iter(attrs=["pid", "name"]):
            try:
                row = self.proc_table.rowCount()
                self.proc_table.insertRow(row)
                self.proc_table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(p.info.get("name", ""))))
                self.proc_table.setItem(row, 1, QtWidgets.QTableWidgetItem(str(p.info["pid"])))
            except Exception:
                continue

    def terminate_by_pid(self):
        pid_text = self.proc_pid_input.text().strip()
        if not pid_text:
            QtWidgets.QMessageBox.warning(self, "Aviso", "Ingrese un PID")
            return
        try:
            pid = int(pid_text)
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Validación", "PID inválido")
            return
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
