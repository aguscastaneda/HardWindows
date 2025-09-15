from PyQt5 import QtWidgets, QtCore
from core.monitor import Monitor

class Footer(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("footer")
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)

        self.lbl_status = QtWidgets.QLabel("Estado del sistema: inicializando...")
        layout.addWidget(self.lbl_status)
        layout.addStretch(1)
        self.lbl_user = QtWidgets.QLabel("")
        layout.addWidget(self.lbl_user)

        # minimal monitor to show quick CPU/RAM in footer
        self.monitor = Monitor(history_max=60)
        self.monitor.sample()
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(2000)

    def _tick(self):
        self.monitor.sample()
        snap = self.monitor.snapshot()
        self.lbl_status.setText(f"CPU {snap['cpu']:.0f}% - RAM {snap['ram']:.0f}%")
