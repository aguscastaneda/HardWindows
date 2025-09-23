from PyQt5 import QtWidgets, QtCore
from core.policies import get_all_policies, set_policy_value
from widgets import message_box


class PoliciesPage(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        title = QtWidgets.QLabel("Restricciones de Windows")
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        desc = QtWidgets.QLabel(
            "Activa o desactiva funciones del sistema. 0 = permitido, 1 = bloqueado.\n"
            "Algunos cambios requieren cerrar sesión para aplicarse."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        self.chk_taskmgr = QtWidgets.QCheckBox("Bloquear Administrador de Tareas")
        self.chk_control = QtWidgets.QCheckBox("Bloquear Panel de Control y Configuración")
        self.chk_run = QtWidgets.QCheckBox("Desactivar Ejecutar (Win + R)")
        self.chk_regedit = QtWidgets.QCheckBox("Bloquear Editor de Registro")

        for c in (self.chk_taskmgr, self.chk_control, self.chk_run, self.chk_regedit):
            c.setTristate(False)
            layout.addWidget(c)

        layout.addStretch(1)

        self._loading = False
        self.refresh_states()

        self.chk_taskmgr.toggled.connect(lambda v: self._on_toggle("DisableTaskMgr", v))
        self.chk_control.toggled.connect(lambda v: self._on_toggle("NoControlPanel", v))
        self.chk_run.toggled.connect(lambda v: self._on_toggle("NoRun", v))
        self.chk_regedit.toggled.connect(lambda v: self._on_toggle("DisableRegistryTools", v))

    def refresh_states(self):
        self._loading = True
        states = get_all_policies()
        # Interpretar 1=blocked -> checked; 0/None -> unchecked
        self.chk_taskmgr.setChecked(bool(states.get("DisableTaskMgr") == 1))
        self.chk_control.setChecked(bool(states.get("NoControlPanel") == 1))
        self.chk_run.setChecked(bool(states.get("NoRun") == 1))
        self.chk_regedit.setChecked(bool(states.get("DisableRegistryTools") == 1))
        self._loading = False

    def _on_toggle(self, name: str, is_checked: bool):
        if self._loading:
            return
        ok = set_policy_value(name, blocked=is_checked)
        if not ok:
            message_box.error(self, "Error", "No se pudo aplicar el cambio. Necesita permisos de administrador.")
            # revert switch
            self.refresh_states()
            return
        message_box.warn(self, "Atención", "Algunos cambios requieren cerrar sesión para aplicarse.")


