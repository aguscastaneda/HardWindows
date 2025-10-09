from PyQt5 import QtWidgets, QtCore, QtGui
from core.policies import get_all_policies, set_policy_value
from widgets import message_box

class PoliciesPage(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 40)
        layout.setSpacing(20)
        
        title = QtWidgets.QLabel("Restricciones de Windows")
        title.setStyleSheet("font-size: 26px; font-weight: 700; color: #ffffff;")
        layout.addWidget(title)
        
        desc = QtWidgets.QLabel(
            "Activa o desactiva funciones del sistema. 0 = permitido, 1 = bloqueado.\n"
            "Algunos cambios requieren cerrar sesión para aplicarse."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #a0a0a0; font-size: 14px; margin-bottom: 8px;")
        layout.addWidget(desc)
        
        container = QtWidgets.QWidget()
        container_layout = QtWidgets.QVBoxLayout(container)
        container_layout.setSpacing(12)
        container_layout.setContentsMargins(0, 0, 0, 0)
        
        item_style = """
        QFrame {
            background-color: #1e293b;
            border-radius: 10px;
            border: 1px solid #334155;
            padding: 16px;
        }
        """
        
        policies = [
            ("DisableTaskMgr", "Bloquear Administrador de Tareas", "Previene el acceso al administrador de tareas"),
            ("NoControlPanel", "Bloquear Panel de Control y Configuración", "Restringe el acceso al panel de control y configuración de Windows"),
            ("NoRun", "Desactivar Ejecutar (Win + R)", "Deshabilita el diálogo Ejecutar accesible con Win+R"),
            ("DisableRegistryTools", "Bloquear Editor de Registro", "Impide el acceso al editor del registro de Windows")
        ]
        
        self.policy_widgets = {}
        
        for policy_key, policy_title, policy_desc in policies:
            item = QtWidgets.QFrame()
            item.setStyleSheet(item_style)
            item_layout = QtWidgets.QHBoxLayout(item)
            item_layout.setContentsMargins(0, 0, 0, 0)
            
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
            
            toggle = QtWidgets.QCheckBox()
            toggle.setStyleSheet("""
                QCheckBox::indicator {
                    width: 40px;
                    height: 20px;
                    border-radius: 10px;
                    background-color: #374151;
                    border: 1px solid #4b5563;
                }
                QCheckBox::indicator:checked {
                    background-color: #00c8ff;
                    border: 1px solid #0096cc;
                }
                QCheckBox::indicator:unchecked:hover {
                    background-color: #4b5563;
                }
                QCheckBox::indicator:checked:hover {
                    background-color: #00a6d6;
                }
                QCheckBox::indicator:pressed {
                    background-color: #00a6d6;
                }
            """)
            toggle.setFixedSize(40, 20)
            
            self.policy_widgets[policy_key] = toggle
            toggle.stateChanged.connect(lambda v, key=policy_key: self._on_toggle(key, v))
            
            item_layout.addWidget(toggle)
            
            container_layout.addWidget(item)
        
        layout.addWidget(container)
        
        self.refresh_states()

    def refresh_states(self):
        states = get_all_policies()
        for key, widget in self.policy_widgets.items():
            checked = bool(states.get(key) == 1)
            widget.setChecked(checked)

    def _on_toggle(self, name: str, is_checked: int):
        is_checked_bool = bool(is_checked)
        
        ok = set_policy_value(name, blocked=is_checked_bool)
        if not ok:
            message_box.error(self, "Error", "No se pudo aplicar el cambio. Necesita permisos de administrador.")
            self.refresh_states()
            return
        
        message_box.warn(self, "Atención", "Algunos cambios requieren cerrar sesión para aplicarse.")


