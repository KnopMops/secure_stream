from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QGroupBox, QLabel, QSpinBox, QTextEdit, QMessageBox,
                             QFrame, QSplitter, QCheckBox, QComboBox)
from PyQt6.QtCore import Qt


class RemoteTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        splitter = QSplitter(Qt.Orientation.Vertical)

        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)

        remote_group = QGroupBox("Управление сервером удаленного доступа")
        remote_layout = QVBoxLayout()

        server_control_layout = QHBoxLayout()
        self.remote_btn = QPushButton("🚀 Запустить сервер")
        self.remote_btn.clicked.connect(self.toggle_remote_server)

        server_control_layout.addWidget(self.remote_btn)
        server_control_layout.addStretch()

        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Статус сервера:"))
        self.status_label = QLabel("❌ Неактивно")
        self.status_label.setProperty("class", "status status-inactive")
        status_layout.addWidget(self.status_label)

        status_layout.addWidget(QLabel("Подключенные клиенты:"))
        self.clients_label = QLabel("0")
        self.clients_label.setProperty("class", "status")
        status_layout.addWidget(self.clients_label)
        status_layout.addStretch()

        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("Порт сервера:"))
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1000, 65535)
        self.port_spin.setValue(8080)
        port_layout.addWidget(self.port_spin)
        port_layout.addStretch()

        audio_layout = QHBoxLayout()
        audio_device_layout = QHBoxLayout()
        audio_device_layout.addWidget(QLabel("Микрофон:"))
        self.audio_device_combo = QComboBox()
        self.audio_device_combo.setEnabled(True)
        audio_device_layout.addWidget(self.audio_device_combo)

        refresh_audio_btn = QPushButton("🔄")
        refresh_audio_btn.setToolTip("Обновить список микрофонов")
        refresh_audio_btn.setMaximumWidth(40)
        refresh_audio_btn.clicked.connect(self.load_audio_devices)
        audio_device_layout.addWidget(refresh_audio_btn)

        audio_device_layout.addStretch()

        self.audio_checkbox = QCheckBox("Транслировать звук с микрофона")
        self.audio_checkbox.stateChanged.connect(self.on_audio_toggled)
        audio_layout.addWidget(self.audio_checkbox)
        audio_layout.addStretch()

        remote_layout.addLayout(server_control_layout)
        remote_layout.addLayout(status_layout)
        remote_layout.addLayout(port_layout)
        remote_layout.addLayout(audio_layout)
        remote_layout.addLayout(audio_device_layout)
        remote_group.setLayout(remote_layout)

        top_layout.addWidget(remote_group)

        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)

        log_group = QGroupBox("Лог активности системы")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(300)
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)

        bottom_layout.addWidget(log_group)

        splitter.addWidget(top_widget)
        splitter.addWidget(bottom_widget)
        splitter.setSizes([400, 200])

        layout.addWidget(splitter)
        self.setLayout(layout)

        self.load_settings()
        self.load_audio_devices()

    def load_settings(self):
        port = self.parent.database.get_setting('remote', 'port', '8080')
        self.port_spin.setValue(int(port))

    def toggle_remote_server(self):
        if not self.parent.remote_server.running:
            port = self.port_spin.value()

            audio_enabled = self.audio_checkbox.isChecked()
            audio_device = 0
            if audio_enabled and self.audio_device_combo.currentIndex() >= 0:
                audio_device = self.audio_device_combo.currentData()

            if self.parent.remote_server.start_server(port, audio_enabled, audio_device):
                self.remote_btn.setText("⏹️ Остановить сервер")
                self.status_label.setText("✅ Активно")
                self.status_label.setProperty("class", "status status-active")

                audio_text = " с аудио" if audio_enabled else ""
                self.log_text.append(
                    f"[{self.get_timestamp()}] 🌐 Сервер запущен на порту {port}{audio_text}")

                self.parent.database.set_setting('remote', 'port', str(port))
                self.parent.database.set_setting(
                    'remote', 'audio_enabled', str(audio_enabled))
                self.parent.database.set_setting(
                    'remote', 'audio_device', str(audio_device))

            else:
                QMessageBox.warning(
                    self, "Ошибка", "Не удалось запустить сервер! Возможно, порт занят.")
        else:
            if self.parent.remote_server.stop_server():
                self.remote_btn.setText("🚀 Запустить сервер")
                self.status_label.setText("❌ Неактивно")
                self.status_label.setProperty(
                    "class", "status status-inactive")
                self.clients_label.setText("0")
                self.log_text.append(
                    f"[{self.get_timestamp()}] 🌐 Сервер остановлен")
            else:
                QMessageBox.warning(
                    self, "Ошибка", "Не удалось остановить сервер!")

    def get_timestamp(self):
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")

    def update_server_status(self):
        if self.parent.remote_server.running:
            status = self.parent.remote_server.get_server_status()
            self.clients_label.setText(str(status['clients_connected']))

    def on_audio_toggled(self, state):
        pass

    def load_audio_devices(self):
        try:
            self.audio_device_combo.clear()

            devices = self.parent.remote_server.get_available_audio_devices()

            if not devices:
                self.audio_device_combo.addItem("Микрофоны не найдены", 0)
                return

            current_selected = self.audio_device_combo.currentData()

            for device in devices:
                self.audio_device_combo.addItem(
                    device['name'], device['index'])

            if current_selected is None:
                audio_enabled = self.parent.database.get_setting(
                    'remote', 'audio_enabled', 'false')
                audio_device = int(self.parent.database.get_setting(
                    'remote', 'audio_device', '0'))

                self.audio_checkbox.setChecked(audio_enabled == 'true')

                for i in range(self.audio_device_combo.count()):
                    if self.audio_device_combo.itemData(i) == audio_device:
                        self.audio_device_combo.setCurrentIndex(i)
                        break

        except Exception as e:
            print(f"Ошибка загрузки аудио устройств: {e}")
            import traceback
            traceback.print_exc()
            self.audio_device_combo.clear()
            self.audio_device_combo.addItem("Ошибка загрузки устройств", 0)
