from PyQt5.QtWidgets import QMessageBox


class ErrorHandler:
    def __init__(self, parent=None):
        self.error_log = []
        self.parent = parent

    def log_error(self, error):
        self.error_log.append(str(error))
        self.display_error(str(error))

    def display_error(self, error_message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("An error occurred")
        msg.setInformativeText(error_message)
        msg.setWindowTitle("Error")
        msg.exec_()