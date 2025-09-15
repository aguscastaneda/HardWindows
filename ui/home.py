from PyQt5 import QtWidgets, QtCore
from widgets.resource_chart import ResourceChart
from core.monitor import Monitor
import psutil

class HomePage(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        header = QtWidgets.QLabel("Monitoreo de recursos")
        header.setObjectName("titleLabel")
        layout.addWidget(header)

        # Charts area
        charts_layout = QtWidgets.QHBoxLayout()
        self.cpu_chart = ResourceChart(title="CPU (%)")
        self.ram_chart = ResourceChart(title="RAM (%)")
        self.disk_chart = ResourceChart(title="Disco (%)")
        charts_layout.addWidget(self.cpu_chart)
        charts_layout.addWidget(self.ram_chart)
        charts_layout.addWidget(self.disk_chart)
        layout.addLayout(charts_layout)

        # Report summary
        self.report = QtWidgets.QTextEdit()
        self.report.setReadOnly(True)
        self.report.setFixedHeight(140)
        layout.addWidget(self.report)

        # Monitor
        self.monitor = Monitor(history_max=180)
        # Pre-sample once to initialize psutil counters
        self.monitor.sample()

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(1000)  # 1 segundo

    def _tick(self):
        self.monitor.sample()
        cpu = self.monitor.cpu_hist[-1]
        ram = self.monitor.ram_hist[-1]
        disk = self.monitor.disk_hist[-1]
        # agregar datos a charts
        self.cpu_chart.update_data(list(self.monitor.cpu_hist))
        self.ram_chart.update_data(list(self.monitor.ram_hist))
        self.disk_chart.update_data(list(self.monitor.disk_hist))
        # actualizar report
        text = f"CPU: {cpu:.1f}%\nRAM: {ram:.1f}%\nDisco (root): {disk:.1f}%\n"
        # listar discos
        du = psutil.disk_usage(".")
        text += f"\nUso disco actual: {du.percent:.1f}%\n"
        self.report.setPlainText(text)
