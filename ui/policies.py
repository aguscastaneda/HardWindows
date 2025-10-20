from PyQt5 import QtWidgets, QtCore, QtGui
from functools import partial
from core.policies import (
    get_all_policies,
    set_policy_value,
    list_user_sids,
    get_all_policies_for_sid,
    set_policy_value_for_sid,
    apply_policy_changes,
)
from core.user_utils import list_local_users
from widgets import message_box


class PoliciesPage(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Layout principal
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Título
        title = QtWidgets.QLabel("Restricciones de Windows")
        title.setStyleSheet("font-size: 28px; font-weight: 700; color: #ffffff;")
        layout.addWidget(title)

        # Splitter general (divide panel de usuarios y políticas)
        main_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        main_splitter.setChildrenCollapsible(False)
        main_splitter.setHandleWidth(3)
        layout.addWidget(main_splitter, 1)

        # --- PANEL IZQUIERDO: usuarios ---
        users_panel = QtWidgets.QWidget()
        users_layout = QtWidgets.QVBoxLayout(users_panel)
        users_layout.setContentsMargins(10, 10, 10, 10)
        users_layout.setSpacing(10)

        users_panel.setMinimumWidth(230)
        users_panel.setMaximumWidth(280)
        users_panel.setStyleSheet("background-color: #0f172a; border-radius: 8px;")

        users_label = QtWidgets.QLabel("Usuarios del sistema")
        users_label.setStyleSheet("font-weight: bold; color: #cbd5e1; font-size: 14px;")
        users_layout.addWidget(users_label)

        self.users_list = QtWidgets.QListWidget()
        self.users_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.users_list.setStyleSheet("""
            QListWidget {
                background-color: #1e293b; 
                color: #e5e7eb; 
                border: 1px solid #334155; 
                border-radius: 8px;
                padding: 6px;
            }
            QListWidget::item:selected { background-color: #2563eb; color: white; }
        """)
        users_layout.addWidget(self.users_list, 1)

        refresh_users_btn = QtWidgets.QPushButton("Actualizar usuarios")
        refresh_users_btn.setStyleSheet("""
            QPushButton {
                background-color: #00c8ff; 
                color: black; 
                font-weight: bold;
                border-radius: 6px; 
                padding: 6px 10px;
            }
            QPushButton:hover { background-color: #00a6d6; }
        """)
        refresh_users_btn.clicked.connect(self._load_users)
        users_layout.addWidget(refresh_users_btn)

        # --- PANEL DERECHO: políticas ---
        right_container = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_container)
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.setSpacing(15)
        right_container.setStyleSheet("background-color: #0b1220; border-radius: 8px;")

        right_scroll = QtWidgets.QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        right_scroll.setWidget(right_container)
        right_scroll.setStyleSheet("QScrollArea { border: none; }")

        main_splitter.addWidget(users_panel)
        main_splitter.addWidget(right_scroll)
        main_splitter.setStretchFactor(0, 0)
        main_splitter.setStretchFactor(1, 1)

        # Definición de políticas
        self._policies_def = [
            ("DisableTaskMgr", "Bloquear Administrador de Tareas", "Previene el acceso al administrador de tareas"),
            ("NoControlPanel", "Bloquear Panel de Control y Configuración", "Restringe el acceso al panel de control y configuración de Windows"),
            ("NoRun", "Desactivar Ejecutar (Win + R)", "Deshabilita el diálogo Ejecutar accesible con Win+R"),
            ("DisableRegistryTools", "Bloquear Editor de Registro", "Impide el acceso al editor del registro de Windows"),
        ]
        self._policy_keys = [p[0] for p in self._policies_def]

        self.right_layout = right_layout
        self.users_list.itemSelectionChanged.connect(self._rebuild_panels)

        self._load_users()
        self._rebuild_panels()

    # ----------------------------------------------------------
    # FUNCIONES DE LÓGICA (idénticas al original)
    # ----------------------------------------------------------

    def _selected_user_sids(self):
        items = self.users_list.selectedItems()
        users = [i.text() for i in items]
        return list_user_sids(users)

    def _load_users(self):
        self.users_list.clear()
        users = list_local_users()
        for u in users:
            self.users_list.addItem(u)

    def _clear_right_panels(self):
        while self.right_layout.count():
            item = self.right_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

    def _make_policy_item(self, policy_title: str, policy_desc: str, initial_checked: bool, on_change):
        item = QtWidgets.QFrame()
        item.setStyleSheet("""
            QFrame { 
                background-color: #1e293b; 
                border-radius: 10px; 
                border: 1px solid #334155; 
                padding: 16px; 
            }
        """)
        item_layout = QtWidgets.QHBoxLayout(item)
        item_layout.setContentsMargins(10, 10, 10, 10)

        # Columna de texto
        content_col = QtWidgets.QVBoxLayout()
        content_col.setSpacing(4)

        title_label = QtWidgets.QLabel(policy_title)
        title_label.setStyleSheet("color: white; font-weight: 600; font-size: 15px;")
        content_col.addWidget(title_label)

        desc_label = QtWidgets.QLabel(policy_desc)
        desc_label.setStyleSheet("color: #cbd5e1; font-size: 13px;")
        desc_label.setWordWrap(True)
        content_col.addWidget(desc_label)

        item_layout.addLayout(content_col)

        # Switch
        toggle = QtWidgets.QCheckBox()
        toggle.setStyleSheet("""
            QCheckBox::indicator {
                width: 44px; height: 22px; border-radius: 11px;
                background-color: #374151; border: 1px solid #4b5563;
            }
            QCheckBox::indicator:checked {
                background-color: #00c8ff; border: 1px solid #0096cc;
            }
            QCheckBox::indicator:unchecked:hover { background-color: #4b5563; }
            QCheckBox::indicator:checked:hover { background-color: #00a6d6; }
        """)
        toggle.setFixedSize(44, 22)
        toggle.setChecked(initial_checked)
        toggle.stateChanged.connect(on_change)
        item_layout.addWidget(toggle)

        return item

    def _build_system_panel(self):
        box = QtWidgets.QGroupBox("Sistema (global)")
        box.setStyleSheet("""
            QGroupBox { 
                color: #e5e7eb; font-weight: bold; 
                border: 1px solid #334155; border-radius: 8px;
                background-color: #0f172a; margin-top: 10px;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
        """)
        v = QtWidgets.QVBoxLayout(box)
        v.setSpacing(10)
        states = get_all_policies()
        for key, title, desc in self._policies_def:
            initial = bool(states.get(key) == 1)
            on_change = partial(self._on_toggle_system, key)
            v.addWidget(self._make_policy_item(title, desc, initial, on_change))
        v.addStretch(1)
        self.right_layout.addWidget(box)

    def _build_user_panel(self, username: str, sid: str):
        box = QtWidgets.QGroupBox(f"Usuario: {username}")
        box.setStyleSheet("""
            QGroupBox {
                color: #e5e7eb; font-weight: bold;
                border: 1px solid #334155; border-radius: 8px;
                background-color: #0f172a; margin-top: 10px;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
        """)
        v = QtWidgets.QVBoxLayout(box)
        v.setSpacing(10)
        states = get_all_policies_for_sid(sid)
        for key, title, desc in self._policies_def:
            initial = bool(states.get(key) == 1)
            on_change = partial(self._on_toggle_user, key, sid)
            v.addWidget(self._make_policy_item(title, desc, initial, on_change))
        v.addStretch(1)
        self.right_layout.addWidget(box)

    def _rebuild_panels(self):
        self._clear_right_panels()
        selected = self._selected_user_sids()
        if not selected:
            self._build_system_panel()
        else:
            for username, sid in selected:
                self._build_user_panel(username, sid)
        spacer = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.right_layout.addItem(spacer)

    def _on_toggle_system(self, name: str, is_checked: int):
        blocked = is_checked == QtCore.Qt.Checked
        ok = set_policy_value(name, blocked=blocked)
        if not ok:
            message_box.error(self, "Error", "No se pudo aplicar el cambio. Necesita permisos de administrador.")
            self._rebuild_panels()
            return
        apply_policy_changes(restart_shell=False)

    def _on_toggle_user(self, name: str, sid: str, is_checked: int):
        blocked = is_checked == QtCore.Qt.Checked
        ok = set_policy_value_for_sid(name, blocked=blocked, sid=sid)
        if not ok:
            message_box.error(self, "Error", f"No se pudo aplicar el cambio para el usuario seleccionado.")
            self._rebuild_panels()
            return
        apply_policy_changes(restart_shell=False)
