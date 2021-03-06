from PyQt5.QtWidgets import QLineEdit, QWidget, QHBoxLayout, QPushButton
from PyQt5 import QtCore


class CommandLine(QLineEdit):
    """Widget to simulate a command line interface. Stores past
    commands, support enter to send and up and down arrow navigation.

    attributes:
        current: int, index of current command
        commands: list, list of previous commands
    """
    sendCommand = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current = -1
        self.commands = ['']

    def keyPressEvent(self, QKeyEvent):
        """Handles return, up, and down arrow key presses.
        """
        key = QKeyEvent.key()
        if key == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_Enter:
            self.send_command()
        elif key == QtCore.Qt.Key_Up:
            self.current -= 1
            if self.current < -len(self.commands):
                self.current = -len(self.commands)
            self.setText(self.commands[self.current])
        elif key == QtCore.Qt.Key_Down:
            self.current += 1
            if self.current > -1:
                self.current = -1
            self.setText(self.commands[self.current])
        else:
            super().keyPressEvent(QKeyEvent)

    def send_command(self, q=None):
        """Adds the current text to list of commands, clears the
        command line, and moves current index to -1. Subclasses should
        overwrite this to actually send the command, and call this
        method after to handle command storage.
        """
        command = self.text()
        if not (command.isspace() or command == ''):
            self.commands.insert(-1, command)
        self.setText('')
        self.current = -1
        self.sendCommand.emit(command)


class CommandLineWidget(QWidget):
    sendCommand = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(CommandLineWidget, self).__init__(parent)
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.commandLine = CommandLine(self)
        self.layout.addWidget(self.commandLine)
        self.sendButton = QPushButton(self)
        self.sendButton.setText("Send")
        self.layout.addWidget(self.sendButton)
        self.sendButton.clicked.connect(self.commandLine.send_command)
        self.commandLine.sendCommand.connect(self.sendCommand)
