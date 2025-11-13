from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton
from PyQt6.QtCore import pyqtSignal


class ChatWidget(QWidget):
    message_sent = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)

        input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Введите сообщение...")
        self.message_input.returnPressed.connect(self.send_message)

        self.send_button = QPushButton("Отправить")
        self.send_button.clicked.connect(self.send_message)

        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)
        layout.addLayout(input_layout)

        self.setLayout(layout)

    def send_message(self):
        message = self.message_input.text().strip()
        if message:
            self.message_sent.emit(message)
            self.message_input.clear()

    def add_message(self, username, message, message_type="text"):
        if message_type == "system":
            formatted_message = f'<span style="color: #ff9800;"><b>{username}:</b> {message}</span>'
        else:
            formatted_message = f'<b>{username}:</b> {message}'

        self.chat_display.append(formatted_message)

        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
