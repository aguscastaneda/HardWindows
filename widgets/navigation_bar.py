from PyQt5 import QtWidgets, QtCore, QtGui
import os

class NavigationBar(QtWidgets.QFrame):
    button_clicked = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sideBar")
        self.setFixedWidth(280)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        title = QtWidgets.QLabel("HardWindows")
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        self.btn_home = QtWidgets.QPushButton(" Home")
        self.btn_home.setObjectName("navButton")
        self.btn_home.clicked.connect(lambda: self.emit_key("home"))
        self.btn_manager = QtWidgets.QPushButton(" Manager")
        self.btn_manager.setObjectName("navButton")
        self.btn_manager.clicked.connect(lambda: self.emit_key("manager"))
        self.btn_registry = QtWidgets.QPushButton(" Editor Registro")
        self.btn_registry.setObjectName("navButton")
        self.btn_registry.clicked.connect(lambda: self.emit_key("registry"))
        self.btn_policies = QtWidgets.QPushButton(" Permisos")
        self.btn_policies.setObjectName("navButton")
        self.btn_policies.clicked.connect(lambda: self.emit_key("policies"))
        

        layout.addWidget(self.btn_home)
        layout.addWidget(self.btn_manager)
        layout.addWidget(self.btn_registry)
        layout.addWidget(self.btn_policies)

        layout.addStretch(1)

        ver = QtWidgets.QLabel("v0.1")
        ver.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(ver)

        self.buttons = {
            "home": self.btn_home,
            "manager": self.btn_manager,
            "registry": self.btn_registry,
            "policies": self.btn_policies
        }
        self.set_active("home")

    def emit_key(self, key):
        self.set_active(key)
        self.button_clicked.emit(key)

    def set_active(self, key):
        for k, b in self.buttons.items():
            b.setProperty("active", "true" if k == key else "false")
            b.style().unpolish(b)
            b.style().polish(b)
            b.update()
