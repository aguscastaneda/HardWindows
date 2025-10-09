from PyQt5 import QtWidgets
import pyqtgraph as pg

class ResourceChart(QtWidgets.QFrame):
    def __init__(self, title=""):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        self.title = QtWidgets.QLabel(title)
        self.title.setObjectName("titleLabel")
        layout.addWidget(self.title)
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground(None)
        self.curve = self.plot_widget.plot([], pen=pg.mkPen(color=(20,120,220), width=2))
        self.plot_widget.showGrid(x=False, y=True, alpha=0.3)
        layout.addWidget(self.plot_widget)
        self.data = []

    def update_data(self, data):
        self.data = data
        self.curve.setData(self.data)
