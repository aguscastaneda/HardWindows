from PyQt5 import QtWidgets, QtCore
from core.monitor import Monitor

class Footer(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("footer")
        
        # Layout principal
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(20)

        # Estado del sistema
        self.lbl_status = QtWidgets.QLabel("Estado del sistema: inicializando...")
        self.lbl_status.setStyleSheet("""
            QLabel {
                color: #00c8ff;
                font-size: 18px;
                font-weight: bold;
                background-color: #1a1a2e;
                border-radius: 6px;
                padding: 10px 16px;
            }
        """)
        layout.addWidget(self.lbl_status)

        layout.addStretch(1)

        # Monitor para CPU/RAM
        self.monitor = Monitor(history_max=60)  
        self.monitor.sample()

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(2000)  # cada 2 segundos

    def _tick(self):
        self.monitor.sample()
        snap = self.monitor.snapshot()

        cpu = snap['cpu']
        ram = snap['ram']

        # Colores dinamicos segun nivel de uso
        def colorize(value):
            if value < 50:
                return "#00ff88"   # verde
            elif value < 80:
                return "#ffcc00"   # amarillo
            else:
                return "#ff5555"   # rojo

        cpu_color = colorize(cpu)
        ram_color = colorize(ram)

        self.lbl_status.setText(
            f"<span style='color:{cpu_color}'>CPU {cpu:.0f}%</span> - "
            f"<span style='color:{ram_color}'>RAM {ram:.0f}%</span>"
        )
