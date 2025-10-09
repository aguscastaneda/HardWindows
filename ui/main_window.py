import os
from PyQt5 import QtWidgets, QtGui, QtCore
from widgets.navigation_bar import NavigationBar
from widgets.footer import Footer
from ui.home import HomePage
from ui.manager import ManagerPage
from ui.register_editor import RegisterEditorPage
from ui.policies import PoliciesPage

APP_TITLE = "HardWindows"

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.setMinimumSize(1000, 650)
        self._central = QtWidgets.QWidget()
        self.setCentralWidget(self._central)
        layout = QtWidgets.QHBoxLayout(self._central)
        layout.setContentsMargins(0, 0, 0, 0)

        # Side navigation
        self.nav = NavigationBar()
        self.nav.button_clicked.connect(self.on_nav_clicked)
        layout.addWidget(self.nav, 0)

        # Main stack
        self.stack = QtWidgets.QStackedWidget()
        layout.addWidget(self.stack, 1)

        # Pages
        self.home = HomePage()
        self.manager = ManagerPage()
        self.register_editor = RegisterEditorPage()
        self.policies = PoliciesPage()

        self.stack.addWidget(self.home)
        self.stack.addWidget(self.manager)
        self.stack.addWidget(self.register_editor)
        self.stack.addWidget(self.policies)

        # Footer
        self.footer = Footer()
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.stack)
        vbox.addWidget(self.footer)
        vbox.setStretch(0, 1)
        vbox.setStretch(1, 0)

        # replace right side
        layout.addLayout(vbox, 1)

        # default page
        self.nav.set_active("home")
        self.stack.setCurrentWidget(self.home)

    def on_nav_clicked(self, key):
        if key == "home":
            self.stack.setCurrentWidget(self.home)
        elif key == "manager":
            self.stack.setCurrentWidget(self.manager)
        elif key == "registry":
            self.stack.setCurrentWidget(self.register_editor)
        elif key == "policies":
            self.stack.setCurrentWidget(self.policies)
        