from PyQt5 import QtWidgets

def info(parent, title, message):
    QtWidgets.QMessageBox.information(parent, title, message)

def warn(parent, title, message):
    QtWidgets.QMessageBox.warning(parent, title, message)

def error(parent, title, message):
    QtWidgets.QMessageBox.critical(parent, title, message)
    