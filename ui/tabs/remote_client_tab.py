from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QGroupBox, QLabel, QSpinBox, QLineEdit, QSplitter,
                             QFrame, QMessageBox, QScrollArea, QComboBox)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QPixmap, QMouseEvent
import threading
from ..widgets.video_player import VideoPlayer


class RemoteClientTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self._audio_stream = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        control_group = QGroupBox("Подключение к серверу")
        control_layout = QVBoxLayout()

        connection_layout = QHBoxLayout()
        connection_layout.addWidget(QLabel("IP сервера:"))

        self.server_ip_input = QLineEdit()
        self.server_ip_input.setText("localhost")
        self.server_ip_input.setPlaceholderText("192.168.1.100")
        connection_layout.addWidget(self.server_ip_input)

        connection_layout.addWidget(QLabel("Порт:"))
        self.server_port_spin = QSpinBox()
        self.server_port_spin.setRange(1000, 65535)
        self.server_port_spin.setValue(8080)
        connection_layout.addWidget(self.server_port_spin)

        connection_layout.addWidget(QLabel("Имя клиента:"))
        self.client_name_input = QLineEdit()
        self.client_name_input.setText("Клиент")
        self.client_name_input.setPlaceholderText("Введите имя")
        connection_layout.addWidget(self.client_name_input)

        connection_layout.addStretch()

        self.connect_btn = QPushButton("🔗 Подключиться")
        self.connect_btn.clicked.connect(self.toggle_connection)
        connection_layout.addWidget(self.connect_btn)

        self.info_btn = QPushButton("ℹ️ Информация")
        self.info_btn.clicked.connect(self.show_connection_info)
        connection_layout.addWidget(self.info_btn)

        control_layout.addLayout(connection_layout)

        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Статус:"))
        self.status_label = QLabel("❌ Не подключен")
        self.status_label.setProperty("class", "status status-inactive")
        status_layout.addWidget(self.status_label)

        status_layout.addWidget(QLabel("FPS:"))
        self.fps_spin = QSpinBox()
        self.fps_spin.setRange(1, 30)
        self.fps_spin.setValue(10)
        self.fps_spin.setEnabled(False)
        status_layout.addWidget(self.fps_spin)

        status_layout.addStretch()

        control_layout.addLayout(status_layout)
        control_group.setLayout(control_layout)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        screen_frame = QFrame()
        screen_layout = QVBoxLayout(screen_frame)

        screen_layout.addWidget(QLabel("🖥️ Экран сервера:"))

        self.video_player = VideoPlayer(self)
        self.video_player.fullscreen_requested.connect(self.toggle_fullscreen)

        self.video_player.volume_changed.connect(self.on_volume_changed)

        self.parent.remote_client.audio_data_received.connect(
            self.on_audio_received)

        screen_layout.addWidget(self.video_player)

        info_frame = QFrame()
        info_layout = QVBoxLayout(info_frame)

        info_group = QGroupBox("Информация о сервере")
        info_group_layout = QVBoxLayout()

        self.server_info_label = QLabel("Нет подключения")
        self.server_info_label.setWordWrap(True)
        info_group_layout.addWidget(self.server_info_label)

        info_group.setLayout(info_group_layout)
        info_layout.addWidget(info_group)

        control_group = QGroupBox("Подключение к серверу")
        control_group_layout = QVBoxLayout()

        connection_fields_layout = QHBoxLayout()
        connection_fields_layout.addWidget(QLabel("Хост:"))

        self.host_input = QLineEdit()
        self.host_input.setText("localhost")
        self.host_input.setPlaceholderText("192.168.1.100")
        connection_fields_layout.addWidget(self.host_input)

        connection_fields_layout.addWidget(QLabel("Порт:"))
        self.port_input = QSpinBox()
        self.port_input.setRange(1000, 65535)
        self.port_input.setValue(8080)
        connection_fields_layout.addWidget(self.port_input)

        self.connect_btn_simple = QPushButton("🔗 Подключиться")
        self.connect_btn_simple.clicked.connect(self.connect_to_server)
        connection_fields_layout.addWidget(self.connect_btn_simple)

        control_group_layout.addLayout(connection_fields_layout)
        control_group.setLayout(control_group_layout)
        info_layout.addWidget(control_group)

        stats_group = QGroupBox("Статистика")
        stats_layout = QVBoxLayout()

        self.fps_counter_label = QLabel("FPS: 0")
        self.resolution_label = QLabel("Разрешение: -")
        self.connection_time_label = QLabel("Время подключения: -")

        stats_layout.addWidget(self.fps_counter_label)
        stats_layout.addWidget(self.resolution_label)
        stats_layout.addWidget(self.connection_time_label)

        stats_group.setLayout(stats_layout)
        info_layout.addWidget(stats_group)

        info_layout.addStretch()

        splitter.addWidget(screen_frame)
        splitter.addWidget(info_frame)
        splitter.setSizes([700, 300])

        layout.addWidget(control_group)
        layout.addWidget(splitter)

        self.setLayout(layout)

    def load_settings(self):
        try:
            if hasattr(self, 'server_ip_input'):
                server_ip = self.parent.database.get_setting(
                    'remote_client', 'server_ip', 'localhost')
                self.server_ip_input.setText(server_ip)

            if hasattr(self, 'server_port_spin'):
                server_port = self.parent.database.get_setting(
                    'remote_client', 'server_port', '8080')
                self.server_port_spin.setValue(int(server_port))

            if hasattr(self, 'client_name_input'):
                client_name = self.parent.database.get_setting(
                    'remote_client', 'client_name', 'Клиент')
                self.client_name_input.setText(client_name)

            if hasattr(self, 'host_input'):
                host = self.parent.database.get_setting(
                    'remote_client', 'host', 'localhost')
                self.host_input.setText(host)

            if hasattr(self, 'port_input'):
                port = self.parent.database.get_setting(
                    'remote_client', 'port', '8080')
                self.port_input.setValue(int(port))

        except Exception as e:
            print(f"Ошибка загрузки настроек: {e}")

    def toggle_connection(self):
        if not hasattr(self, '_settings_loaded'):
            self.load_settings()
            self._settings_loaded = True

        if not self.parent.remote_client.connected:
            host = self.server_ip_input.text().strip() if hasattr(
                self, 'server_ip_input') else "localhost"
            port = self.server_port_spin.value() if hasattr(
                self, 'server_port_spin') else 8080
            client_name = self.client_name_input.text().strip() if hasattr(
                self, 'client_name_input') else "Клиент"

            if not host:
                host = "localhost"
            if not client_name:
                client_name = "Клиент"

            if self.parent.remote_client.connect_to_server(host, port):
                self.connect_btn.setText("🔌 Отключиться")
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(100, self.update_status_connected)
                self.fps_spin.setEnabled(True)

                self.server_ip_input.setVisible(False)
                self.server_port_spin.setVisible(False)
                self.client_name_input.setVisible(False)
                self.info_btn.setVisible(False)

                fps = self.fps_spin.value()
                self.parent.remote_client.start_screen_stream(fps)

                self.parent.database.set_setting(
                    'remote_client', 'server_ip', host)
                self.parent.database.set_setting(
                    'remote_client', 'server_port', str(port))
                self.parent.database.set_setting(
                    'remote_client', 'client_name', self.client_name_input.text())
            else:
                QMessageBox.warning(
                    self, "Ошибка", "Не удалось подключиться к серверу!")
        else:
            self._close_audio_stream()

            if self.parent.remote_client.disconnect_from_server():
                self.connect_btn.setText("🔗 Подключиться")
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(100, self.update_status_disconnected)
                self.fps_spin.setEnabled(False)

                self.server_ip_input.setVisible(True)
                self.server_port_spin.setVisible(True)
                self.client_name_input.setVisible(True)
                self.info_btn.setVisible(True)

                if hasattr(self, 'video_player') and self.video_player:
                    self.video_player.clear_display()
                self.server_info_label.setText("Нет подключения")
            else:
                QMessageBox.warning(
                    self, "Ошибка", "Не удалось отключиться от сервера!")

    @pyqtSlot(QPixmap)
    def display_screen_frame(self, pixmap):
        if hasattr(self, 'video_player') and self.video_player:
            try:
                self.video_player.display_frame(pixmap)
            except Exception as e:
                print(f"Ошибка отображения кадра: {e}")

    @pyqtSlot(dict)
    def display_server_info(self, info):
        if hasattr(self, 'server_info_label') and self.server_info_label:
            try:
                info_text = f"<b>Сервер:</b> {info.get('hostname', 'Неизвестно')}<br>"
                info_text += f"<b>ОС:</b> {info.get('os', 'Неизвестно')}<br>"
                info_text += f"<b>Разрешение:</b> {info.get('resolution', 'Неизвестно')}<br>"
                info_text += f"<b>Версия:</b> {info.get('version', 'Неизвестно')}"
                self.server_info_label.setText(info_text)
            except Exception as e:
                print(f"Ошибка отображения информации о сервере: {e}")

    @pyqtSlot(str)
    def show_error(self, error_message):
        QMessageBox.warning(self, "Ошибка", error_message)

    def connect_to_server(self):
        host = self.host_input.text().strip()
        port = self.port_input.value()

        if not host:
            QMessageBox.warning(self, "Ошибка", "Введите хост сервера!")
            return

        if port < 1000 or port > 65535:
            QMessageBox.warning(
                self, "Ошибка", "Порт должен быть от 1000 до 65535!")
            return

        if self.parent.remote_client.connect_to_server(host, port):
            self.connect_btn_simple.setText("🔌 Отключиться")
            self.connect_btn_simple.clicked.disconnect()
            self.connect_btn_simple.clicked.connect(
                self.disconnect_from_server)

            if hasattr(self, 'host_input') and self.host_input:
                self.host_input.setVisible(False)
            if hasattr(self, 'port_input') and self.port_input:
                self.port_input.setVisible(False)

            fps = 10
            if hasattr(self, 'fps_spin') and self.fps_spin:
                try:
                    fps = self.fps_spin.value()
                except:
                    fps = 10
            self.parent.remote_client.start_screen_stream(fps)

            self.parent.database.set_setting('remote_client', 'host', host)
            self.parent.database.set_setting(
                'remote_client', 'port', str(port))

            from PyQt6.QtCore import QTimer
            QTimer.singleShot(100, self.update_status_connected)

            QMessageBox.information(
                self, "Успех", "Подключение к серверу установлено!")
        else:
            QMessageBox.warning(
                self, "Ошибка", "Не удалось подключиться к серверу!")

    def disconnect_from_server(self):
        self._close_audio_stream()

        if self.parent.remote_client.disconnect_from_server():
            self.connect_btn_simple.setText("🔗 Подключиться")
            self.connect_btn_simple.clicked.disconnect()
            self.connect_btn_simple.clicked.connect(self.connect_to_server)

            if hasattr(self, 'host_input') and self.host_input:
                self.host_input.setVisible(True)
            if hasattr(self, 'port_input') and self.port_input:
                self.port_input.setVisible(True)

            from PyQt6.QtCore import QTimer
            QTimer.singleShot(100, self.update_status_disconnected)

            if hasattr(self, 'video_player') and self.video_player:
                self.video_player.clear_display()
            if hasattr(self, 'server_info_label') and self.server_info_label:
                self.server_info_label.setText("Нет подключения")

            QMessageBox.information(
                self, "Информация", "Отключение от сервера выполнено!")
        else:
            QMessageBox.warning(
                self, "Ошибка", "Не удалось отключиться от сервера!")

    def update_status_connected(self):
        try:
            if hasattr(self, 'status_label') and self.status_label:
                try:
                    self.status_label.setText("✅ Подключен")
                    self.status_label.setProperty(
                        "class", "status status-active")
                except RuntimeError:
                    pass

        except Exception as e:
            if "deleted" not in str(e).lower():
                print(f"Ошибка обновления статуса подключения: {e}")

    def update_status_disconnected(self):
        try:
            if hasattr(self, 'status_label') and self.status_label:
                try:
                    self.status_label.setText("❌ Не подключен")
                    self.status_label.setProperty(
                        "class", "status status-inactive")
                except RuntimeError:
                    pass
        except Exception as e:
            if "deleted" not in str(e).lower():
                print(f"Ошибка обновления статуса отключения: {e}")

    def show_connection_info(self):
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit

        dialog = QDialog(self)
        dialog.setWindowTitle("Информация о подключении")
        dialog.setModal(True)
        dialog.resize(500, 400)

        layout = QVBoxLayout()

        title_label = QLabel("ℹ️ Информация о подключении к серверу")
        title_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)

        settings_text = QTextEdit()
        settings_text.setReadOnly(True)

        info_text = f"""<b>Текущие настройки подключения:</b><br><br>
        <b>IP сервера:</b> {self.server_ip_input.text()}<br>
        <b>Порт:</b> {self.server_port_spin.value()}<br>
        <b>Имя клиента:</b> {self.client_name_input.text()}<br>
        <b>FPS:</b> {self.fps_spin.value()}<br><br>
        
        <b>Статус подключения:</b> {"✅ Подключен" if self.parent.remote_client.connected else "❌ Не подключен"}<br><br>
        
        <b>Как подключиться:</b><br>
        1. Убедитесь, что сервер удаленного доступа запущен<br>
        2. Введите правильный IP адрес сервера<br>
        3. Укажите порт сервера (по умолчанию 8080)<br>
        4. Введите имя для идентификации<br>
        5. Нажмите "🔗 Подключиться"<br><br>
        
        <b>Возможные проблемы:</b><br>
        • Сервер не запущен - проверьте вкладку "🌐 Удаленный доступ"<br>
        • Неправильный IP - убедитесь, что IP сервера корректен<br>
        • Порт занят - попробуйте другой порт<br>
        • Брандмауэр блокирует соединение<br><br>
        
        <b>Функции после подключения:</b><br>
        • Просмотр экрана сервера в реальном времени<br>
        • Управление мышью (клики передаются на сервер)<br>
        • Настройка FPS для оптимизации<br>
        • Автоматическое переподключение при обрыве связи"""

        settings_text.setHtml(info_text)
        layout.addWidget(settings_text)

        button_layout = QHBoxLayout()
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dialog.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

        dialog.setLayout(layout)
        dialog.exec()

    def toggle_fullscreen(self):
        if hasattr(self, 'video_player') and self.video_player:
            self.video_player.toggle_fullscreen()

    def toggle_play_pause(self):
        if hasattr(self, 'video_player') and self.video_player:
            self.video_player.toggle_play_pause()

    def on_volume_changed(self, volume):
        print(f"Громкость изменена на: {volume}%")

    def on_audio_received(self, audio_data):
        try:
            if not hasattr(self, '_audio_stream') or self._audio_stream is None:
                try:
                    import sounddevice as sd
                    import numpy as np

                    self._audio_sample_rate = 44100
                    self._audio_channels = 2

                    self._audio_stream = sd.OutputStream(
                        samplerate=self._audio_sample_rate,
                        channels=self._audio_channels,
                        dtype=np.int16
                    )
                    self._audio_stream.start()
                    print("Аудио поток воспроизведения запущен")
                except Exception as e:
                    print(f"Ошибка инициализации аудио потока: {e}")
                    return

            try:
                import numpy as np
                import sounddevice as sd

                audio_array = np.frombuffer(audio_data, dtype=np.int16)

                if len(audio_array) > 0:
                    audio_array = audio_array.reshape(-1, self._audio_channels)

                    if self._audio_stream and self._audio_stream.active:
                        self._audio_stream.write(audio_array)

            except Exception as e:
                print(f"Ошибка воспроизведения аудио: {e}")

        except Exception as e:
            print(f"Ошибка обработки аудио: {e}")

    def _close_audio_stream(self):
        try:
            if hasattr(self, '_audio_stream') and self._audio_stream is not None:
                try:
                    self._audio_stream.stop()
                    self._audio_stream.close()
                    print("Аудио поток воспроизведения остановлен")
                except:
                    pass
                self._audio_stream = None
        except Exception as e:
            print(f"Ошибка закрытия аудио потока: {e}")

    def update_connection_status(self, connected):
        try:
            if hasattr(self, 'video_player') and self.video_player:
                try:
                    self.video_player.set_connection_status(connected)
                except RuntimeError:
                    pass

            if hasattr(self, 'status_label') and self.status_label:
                try:
                    if connected:
                        self.status_label.setText("✅ Подключен")
                        self.status_label.setProperty(
                            "class", "status status-active")
                    else:
                        self.status_label.setText("❌ Не подключен")
                        self.status_label.setProperty(
                            "class", "status status-inactive")
                except RuntimeError:
                    pass
        except Exception as e:
            if "deleted" not in str(e).lower():
                print(f"Ошибка обновления статуса подключения: {e}")

    def mousePressEvent(self, event):
        if (hasattr(self, 'video_player') and self.video_player and
            hasattr(self.video_player, 'video_label') and
            self.parent.remote_client.connected and
            self.video_player.video_label.pixmap() and
                event.button() == Qt.MouseButton.LeftButton):

            video_label = self.video_player.video_label
            screen_pos = video_label.mapFromGlobal(
                event.globalPosition().toPoint())

            if video_label.pixmap():
                pixmap_size = video_label.pixmap().size()
                label_size = video_label.size()

                if label_size.width() > 0 and label_size.height() > 0:
                    scale_x = pixmap_size.width() / label_size.width()
                    scale_y = pixmap_size.height() / label_size.height()

                    x = int(screen_pos.x() * scale_x)
                    y = int(screen_pos.y() * scale_y)

                    self.parent.remote_client.send_mouse_click(x, y, "left")

        super().mousePressEvent(event)
