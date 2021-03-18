from PyQt5.QtWidgets import QDialog, QHBoxLayout, QLabel


class WaitForKeyboard(QDialog):
    def __init__(self, *args, **kwargs):
        super(WaitForKeyboard, self).__init__(*args, **kwargs)
        self.setLayout(QHBoxLayout(self))
        self.label = QLabel("Type any key to identify keyboard/scanner...")
        self.layout().addWidget(self.label)

    def keyPressEvent(self, a0):
        super(WaitForKeyboard, self).keyPressEvent(a0)
        self.done(QDialog.Accepted)
