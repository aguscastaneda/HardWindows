from PyQt5 import QtWidgets, QtCore
from widgets.resource_chart import ResourceChart
from core.monitor import Monitor
import psutil

class HomePage(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        header = QtWidgets.QLabel("Monitoreo de recursos")
        header.setObjectName("titleLabel")
        header.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        layout.addWidget(header)

        # Charts area
        charts_container = QtWidgets.QWidget()
        charts_layout = QtWidgets.QHBoxLayout(charts_container)
        charts_layout.setContentsMargins(0, 0, 0, 0)
        charts_layout.setSpacing(20)
        
        self.cpu_chart = ResourceChart(title="CPU (%)")
        self.ram_chart = ResourceChart(title="RAM (%)")
        self.disk_chart = ResourceChart(title="Disco (%)")
        
        # Make charts larger
        self.cpu_chart.setMinimumSize(350, 280)
        self.ram_chart.setMinimumSize(350, 280)
        self.disk_chart.setMinimumSize(350, 280)
        
        # Allow expand
        self.cpu_chart.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.ram_chart.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.disk_chart.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        
        charts_layout.addWidget(self.cpu_chart, 1)
        charts_layout.addWidget(self.ram_chart, 1)
        charts_layout.addWidget(self.disk_chart, 1)
        
        layout.addWidget(charts_container, 1)

        # Report summary - estilo en grilla con labels
        report_container = QtWidgets.QWidget()
        report_layout = QtWidgets.QGridLayout(report_container)
        report_layout.setContentsMargins(10, 10, 10, 10)
        report_layout.setSpacing(20)

        # Labels para métricas
        self.cpu_label = QtWidgets.QLabel("CPU: -- %")
        self.ram_label = QtWidgets.QLabel("RAM: -- %")
        self.disk_label = QtWidgets.QLabel("Disco (root): -- %")
        self.usage_label = QtWidgets.QLabel("Uso disco actual: -- %")

        # Estilo para todas las tarjetas
        style = """
            QLabel {
                background-color: #1e1e2f;
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
                border-radius: 10px;
                padding: 12px;
                border: 1px solid #3a3a4f;
            }
        """
        self.cpu_label.setStyleSheet(style)
        self.ram_label.setStyleSheet(style)
        self.disk_label.setStyleSheet(style)
        self.usage_label.setStyleSheet(style)

        # Distribución en grilla 2x2
        report_layout.addWidget(self.cpu_label, 0, 0)
        report_layout.addWidget(self.ram_label, 0, 1)
        report_layout.addWidget(self.disk_label, 1, 0)
        report_layout.addWidget(self.usage_label, 1, 1)

        layout.addWidget(report_container, 0)

        # Monitor
        self.monitor = Monitor(history_max=180)
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

        # actualizar labels
        du = psutil.disk_usage(".")
        self.cpu_label.setText(f"CPU: {cpu:.1f}%")
        self.ram_label.setText(f"RAM: {ram:.1f}%")
        self.disk_label.setText(f"Disco (root): {disk:.1f}%")
        self.usage_label.setText(f"Uso disco actual: {du.percent:.1f}%")
