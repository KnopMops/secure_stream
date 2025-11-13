from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QGroupBox, QLabel, QSpinBox, QTextEdit, QLineEdit,
                             QListWidget, QSplitter, QFrame, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSlot, QTimer
from datetime import datetime


class ChatTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.last_message_id = 0
        self.new_messages_count = 0
        self.is_server_mode = True
        self.auto_refresh_timer = QTimer()
        self.auto_refresh_timer.timeout.connect(self.check_new_messages)
        self.init_ui()
        self.load_settings()
        self.set_server_mode()

    def init_ui(self):
        layout = QVBoxLayout()

        control_group = QGroupBox("Управление чат-сервером")
        control_layout = QVBoxLayout()

        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Режим:"))
        self.server_mode_btn = QPushButton("🖥️ Сервер")
        self.server_mode_btn.setCheckable(True)
        self.server_mode_btn.setChecked(True)
        self.server_mode_btn.clicked.connect(self.set_server_mode)

        self.client_mode_btn = QPushButton("👤 Клиент")
        self.client_mode_btn.setCheckable(True)
        self.client_mode_btn.clicked.connect(self.set_client_mode)

        mode_layout.addWidget(self.server_mode_btn)
        mode_layout.addWidget(self.client_mode_btn)
        mode_layout.addStretch()
        control_layout.addLayout(mode_layout)

        server_control_layout = QHBoxLayout()
        self.chat_btn = QPushButton("💬 Запустить чат-сервер")
        self.chat_btn.clicked.connect(self.toggle_connection)

        server_control_layout.addWidget(self.chat_btn)
        server_control_layout.addStretch()

        connection_layout = QHBoxLayout()
        connection_layout.addWidget(QLabel("IP сервера:"))
        self.server_ip_input = QLineEdit()
        self.server_ip_input.setText("localhost")
        self.server_ip_input.setPlaceholderText("127.0.0.1")
        connection_layout.addWidget(self.server_ip_input)

        connection_layout.addWidget(QLabel("Порт:"))
        self.chat_port_spin = QSpinBox()
        self.chat_port_spin.setRange(1000, 65535)
        self.chat_port_spin.setValue(8081)
        connection_layout.addWidget(self.chat_port_spin)

        connection_layout.addWidget(QLabel("Имя пользователя:"))
        self.username_input = QLineEdit()
        self.username_input.setText("Клиент")
        self.username_input.setPlaceholderText("Введите имя")
        connection_layout.addWidget(self.username_input)

        connection_layout.addStretch()

        refresh_layout = QHBoxLayout()
        refresh_layout.addWidget(QLabel("Интервал автообновления (сек):"))
        self.refresh_interval_spin = QSpinBox()
        self.refresh_interval_spin.setRange(1, 60)
        self.refresh_interval_spin.setValue(2)
        self.refresh_interval_spin.valueChanged.connect(
            self.update_refresh_interval)
        refresh_layout.addWidget(self.refresh_interval_spin)
        refresh_layout.addStretch()

        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Статус чата:"))
        self.chat_status_label = QLabel("❌ Неактивно")
        self.chat_status_label.setProperty("class", "status status-inactive")
        status_layout.addWidget(self.chat_status_label)

        status_layout.addWidget(QLabel("Подключено пользователей:"))
        self.clients_label = QLabel("0")
        self.clients_label.setProperty("class", "status")
        status_layout.addWidget(self.clients_label)
        status_layout.addStretch()

        control_layout.addLayout(server_control_layout)
        control_layout.addLayout(connection_layout)
        control_layout.addLayout(refresh_layout)
        control_layout.addLayout(status_layout)
        control_group.setLayout(control_layout)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        chat_frame = QFrame()
        chat_layout = QVBoxLayout(chat_frame)

        chat_header_layout = QHBoxLayout()
        self.chat_title_label = QLabel("💭 Чат:")
        self.new_messages_label = QLabel("")
        self.new_messages_label.setProperty("class", "new-messages")
        self.new_messages_label.setStyleSheet(
            "color: #ff4444; font-weight: bold;")
        chat_header_layout.addWidget(self.chat_title_label)
        chat_header_layout.addWidget(self.new_messages_label)
        chat_header_layout.addStretch()
        chat_layout.addLayout(chat_header_layout)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.mousePressEvent = self.on_chat_clicked
        chat_layout.addWidget(self.chat_display)

        message_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Введите сообщение...")
        self.message_input.returnPressed.connect(self.send_chat_message)

        self.send_btn = QPushButton("📤 Отправить")
        self.send_btn.clicked.connect(self.send_chat_message)

        message_layout.addWidget(self.message_input)
        message_layout.addWidget(self.send_btn)
        chat_layout.addLayout(message_layout)

        users_frame = QFrame()
        users_layout = QVBoxLayout(users_frame)

        users_layout.addWidget(QLabel("👥 Подключенные пользователи:"))
        self.users_list = QListWidget()
        users_layout.addWidget(self.users_list)

        splitter.addWidget(chat_frame)
        splitter.addWidget(users_frame)
        splitter.setSizes([700, 300])

        layout.addWidget(control_group)
        layout.addWidget(splitter)

        self.setLayout(layout)

    def load_settings(self):
        port = self.parent.database.get_setting('chat', 'port', '8081')
        self.chat_port_spin.setValue(int(port))

        refresh_interval = self.parent.database.get_setting(
            'chat', 'refresh_interval', '2')
        self.refresh_interval_spin.setValue(int(refresh_interval))

        server_ip = self.parent.database.get_setting(
            'chat', 'server_ip', 'localhost')
        self.server_ip_input.setText(server_ip)

        username = self.parent.database.get_setting(
            'chat', 'username', 'Клиент')
        self.username_input.setText(username)

    def toggle_chat_server(self):
        if not self.parent.chat_server.running:
            port = self.chat_port_spin.value()

            if self.parent.chat_server.start_server(port):
                self.chat_btn.setText("⏹️ Остановить чат")
                self.chat_status_label.setText("✅ Активно")
                self.chat_status_label.setProperty(
                    "class", "status status-active")

                self.parent.database.set_setting('chat', 'port', str(port))

                self.load_chat_history()
                interval = self.refresh_interval_spin.value() * 1000
                self.auto_refresh_timer.start(interval)

            else:
                QMessageBox.warning(
                    self, "Ошибка", "Не удалось запустить чат-сервер! Возможно, порт занят.")
        else:
            if self.parent.chat_server.stop_server():
                self.chat_btn.setText("💬 Запустить чат-сервер")
                self.chat_status_label.setText("❌ Неактивно")
                self.chat_status_label.setProperty(
                    "class", "status status-inactive")
                self.users_list.clear()
                self.clients_label.setText("0")
                self.auto_refresh_timer.stop()
            else:
                QMessageBox.warning(
                    self, "Ошибка", "Не удалось остановить чат-сервер!")

    def load_chat_history(self):
        history = self.parent.database.get_chat_history(limit=50)
        if history and len(history) > 0:
            self.last_message_id = history[0]['id']

        for message in history:
            timestamp = datetime.fromisoformat(
                message['timestamp']).strftime("%H:%M:%S")
            username = message['username']
            msg_text = message['message']

            if message['message_type'] == 'system':
                self.chat_display.append(
                    f'<span style="color: #ff9800;">[{timestamp}] <b>{username}:</b> {msg_text}</span>')
            else:
                self.chat_display.append(
                    f'[{timestamp}] <b>{username}:</b> {msg_text}')

        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )

    def send_chat_message(self):
        message = self.message_input.text().strip()
        if message:
            if self.is_server_mode and self.parent.chat_server.running:
                self.parent.chat_server.send_message("Сервер", message)
                self.parent.database.save_chat_message(
                    "Сервер", message, "text")
            elif not self.is_server_mode and self.parent.chat_client.connected:
                if self.parent.chat_client.send_message(message):
                    self.parent.database.save_chat_message(
                        self.parent.chat_client.username, message, "text")
                else:
                    QMessageBox.warning(
                        self, "Ошибка", "Не удалось отправить сообщение!")
            else:
                timestamp = datetime.now().strftime("%H:%M:%S")
                self.chat_display.append(
                    f'<span style="color: #666;">[{timestamp}] <b>Система:</b> {message} (локально)</span>')
                self.parent.database.save_chat_message(
                    "Система", f"{message} (локально)", "system")

            self.message_input.clear()

    @pyqtSlot(str, str)
    def display_chat_message(self, username, message):
        timestamp = datetime.now().strftime("%H:%M:%S")

        if username == "Система":
            self.chat_display.append(
                f'<span style="color: #ff9800;">[{timestamp}] <b>{username}:</b> {message}</span>')
        else:
            self.chat_display.append(
                f'[{timestamp}] <b>{username}:</b> {message}')

        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )

        self.parent.database.save_chat_message(username, message,
                                               "system" if username == "Система" else "text")

    @pyqtSlot(list)
    def update_user_list(self, users):
        self.users_list.clear()

        if self.is_server_mode and self.parent.chat_server.running:
            self.users_list.addItem("🖥️ Сервер")

        for user in users:
            if user != "Сервер":
                self.users_list.addItem(f"👤 {user}")

        total_users = len(users)
        if self.is_server_mode and self.parent.chat_server.running:
            total_users += 1
        self.clients_label.setText(str(total_users))

    def check_new_messages(self):
        try:
            new_messages = self.parent.database.get_chat_messages_after_id(
                self.last_message_id)
            if new_messages:
                self.new_messages_count += len(new_messages)
                self.update_new_messages_indicator()

                for message in new_messages:
                    timestamp = datetime.fromisoformat(
                        message['timestamp']).strftime("%H:%M:%S")
                    username = message['username']
                    msg_text = message['message']

                    if message['message_type'] == 'system':
                        self.chat_display.append(
                            f'<span style="color: #ff9800;">[{timestamp}] <b>{username}:</b> {msg_text}</span>')
                    else:
                        self.chat_display.append(
                            f'[{timestamp}] <b>{username}:</b> {msg_text}')

                    self.last_message_id = message['id']

                self.chat_display.verticalScrollBar().setValue(
                    self.chat_display.verticalScrollBar().maximum()
                )
        except Exception as e:
            print(f"Ошибка проверки новых сообщений: {e}")

    def update_new_messages_indicator(self):
        if self.new_messages_count > 0:
            self.new_messages_label.setText(
                f"({self.new_messages_count} новых)")
        else:
            self.new_messages_label.setText("")

    def clear_new_messages_indicator(self):
        self.new_messages_count = 0
        self.update_new_messages_indicator()

    def on_chat_clicked(self, event):
        self.clear_new_messages_indicator()
        QTextEdit.mousePressEvent(self.chat_display, event)

    def update_refresh_interval(self):
        interval = self.refresh_interval_spin.value()
        self.parent.database.set_setting(
            'chat', 'refresh_interval', str(interval))

        if self.auto_refresh_timer.isActive():
            self.auto_refresh_timer.stop()
            self.auto_refresh_timer.start(interval * 1000)

    def set_server_mode(self):
        self.is_server_mode = True
        self.server_mode_btn.setChecked(True)
        self.client_mode_btn.setChecked(False)
        self.chat_btn.setText("💬 Запустить чат-сервер")
        self.server_ip_input.setEnabled(False)
        self.username_input.setEnabled(False)

    def set_client_mode(self):
        self.is_server_mode = False
        self.server_mode_btn.setChecked(False)
        self.client_mode_btn.setChecked(True)
        self.chat_btn.setText("🔗 Подключиться к серверу")
        self.server_ip_input.setEnabled(True)
        self.username_input.setEnabled(True)

    def toggle_connection(self):
        if self.is_server_mode:
            self.toggle_chat_server()
        else:
            self.toggle_chat_client()

    def toggle_chat_client(self):
        if not self.parent.chat_client.connected:
            host = self.server_ip_input.text().strip()
            port = self.chat_port_spin.value()
            username = self.username_input.text().strip()

            if not host:
                host = "localhost"
            if not username:
                username = "Клиент"

            if self.parent.chat_client.connect_to_server(host, port, username):
                self.chat_btn.setText("🔌 Отключиться от сервера")
                self.chat_status_label.setText("✅ Подключен")
                self.chat_status_label.setProperty(
                    "class", "status status-active")

                self.parent.database.set_setting('chat', 'server_ip', host)
                self.parent.database.set_setting('chat', 'port', str(port))
                self.parent.database.set_setting('chat', 'username', username)

                interval = self.refresh_interval_spin.value() * 1000
                self.auto_refresh_timer.start(interval)

                self.load_chat_history()
            else:
                QMessageBox.warning(
                    self, "Ошибка", "Не удалось подключиться к серверу!")
        else:
            if self.parent.chat_client.disconnect_from_server():
                self.chat_btn.setText("🔗 Подключиться к серверу")
                self.chat_status_label.setText("❌ Неактивно")
                self.chat_status_label.setProperty(
                    "class", "status status-inactive")
                self.users_list.clear()
                self.clients_label.setText("0")
                self.auto_refresh_timer.stop()
            else:
                QMessageBox.warning(
                    self, "Ошибка", "Не удалось отключиться от сервера!")
