import os
from pathlib import Path
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QStatusBar, QLabel
from PyQt6.QtCore import QTimer, pyqtSlot

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from core import ScreenRecorder, CameraRecorder, RemoteAccessServer, RemoteClient, ChatServer, ChatClient, DatabaseManager
from ui.tabs.screen_tab import ScreenTab
from ui.tabs.camera_tab import CameraTab
from ui.tabs.remote_tab import RemoteTab
from ui.tabs.remote_client_tab import RemoteClientTab
from ui.tabs.chat_tab import ChatTab
from ui.tabs.settings_tab import SettingsTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(
            "SecureStream - Система мониторинга и удаленного доступа")
        self.setGeometry(100, 100, 1200, 800)

        self.center()

        self.screen_recorder = ScreenRecorder()
        self.camera_recorder = CameraRecorder()
        self.remote_server = RemoteAccessServer()
        self.remote_client = RemoteClient()
        self.chat_server = ChatServer()
        self.chat_client = ChatClient()
        self.database = DatabaseManager()

        self.init_ui()

        self.setWindowIcon(
            QIcon(os.path.join('favicon.ico')))

        self.setup_connections()
        self.start_status_updater()

    def init_ui(self):
        tabs = QTabWidget()

        self.screen_tab = ScreenTab(self)
        self.camera_tab = CameraTab(self)
        self.remote_tab = RemoteTab(self)
        self.remote_client_tab = RemoteClientTab(self)
        self.chat_tab = ChatTab(self)
        self.settings_tab = SettingsTab(self)

        tabs.addTab(self.screen_tab, "📹 Запись экрана")
        tabs.addTab(self.camera_tab, "📷 Веб-камера")
        tabs.addTab(self.remote_tab, "🌐 Удаленный доступ")
        tabs.addTab(self.remote_client_tab, "🖥️ Клиент доступа")
        tabs.addTab(self.chat_tab, "💬 Чат")
        tabs.addTab(self.settings_tab, "⚙️ Настройки")

        self.setCentralWidget(tabs)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.status_label = QLabel("Готов")
        self.recording_status = QLabel("📹: Выкл")
        self.camera_status = QLabel("📷: Выкл")
        self.audio_status = QLabel("🎤: Выкл")
        self.server_status = QLabel("🌐: Выкл")
        self.chat_status = QLabel("💬: Выкл")

        self.status_bar.addPermanentWidget(self.recording_status)
        self.status_bar.addPermanentWidget(self.camera_status)
        self.status_bar.addPermanentWidget(self.audio_status)
        self.status_bar.addPermanentWidget(self.server_status)
        self.status_bar.addPermanentWidget(self.chat_status)
        self.status_bar.addWidget(self.status_label)

    def setup_connections(self):
        self.chat_server.message_received.connect(
            self.chat_tab.display_chat_message)
        self.chat_server.user_list_updated.connect(
            self.chat_tab.update_user_list)
        self.chat_server.connection_status_changed.connect(
            self.update_chat_status)

        self.chat_client.message_received.connect(
            self.chat_tab.display_chat_message)
        self.chat_client.user_list_updated.connect(
            self.chat_tab.update_user_list)
        self.chat_client.connection_status_changed.connect(
            self.update_chat_status)
        self.chat_client.error_occurred.connect(
            self.show_chat_error)

        self.remote_client.screen_frame_received.connect(
            self.remote_client_tab.display_screen_frame)
        self.remote_client.server_info_received.connect(
            self.remote_client_tab.display_server_info)
        self.remote_client.error_occurred.connect(
            self.remote_client_tab.show_error)
        self.remote_client.connection_status_changed.connect(
            self.remote_client_tab.update_connection_status)

    def start_status_updater(self):
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(1000)

    @pyqtSlot()
    def update_status(self):
        screen_status = self.screen_recorder.get_recording_status()
        self.recording_status.setText(
            f"📹: {'Вкл' if screen_status['recording'] else 'Выкл'}")

        camera_status = self.camera_recorder.get_recording_status()
        self.camera_status.setText(
            f"📷: {'Вкл' if camera_status['recording'] else 'Выкл'}")

        screen_audio = screen_status.get(
            'audio_enabled', False) and screen_status.get('audio_recording', False)
        camera_audio = camera_status.get(
            'audio_enabled', False) and camera_status.get('audio_recording', False)
        audio_active = screen_audio or camera_audio
        self.audio_status.setText(f"🎤: {'Вкл' if audio_active else 'Выкл'}")

        server_status = self.remote_server.get_server_status()
        self.server_status.setText(
            f"🌐: {'Вкл' if server_status['running'] else 'Выкл'}")

        stats = self.database.get_statistics()
        stats_text = f"Сессии: {stats['sessions']['count']} | "
        stats_text += f"Скриншоты: {stats['screenshots']['count']} | "
        stats_text += f"Сообщения: {stats['chat_messages']}"
        self.status_label.setText(stats_text)

    @pyqtSlot(bool)
    def update_chat_status(self, is_running):
        if self.chat_server.running:
            chat_status = self.chat_server.get_server_status()
            status_text = "💬: Сервер" if is_running else "💬: Выкл"
            if is_running:
                status_text += f" ({chat_status['users_connected']})"
        elif self.chat_client.connected:
            status_text = "💬: Клиент"
        else:
            status_text = "💬: Выкл"
        self.chat_status.setText(status_text)

    @pyqtSlot(str)
    def show_chat_error(self, error_message):
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.warning(self, "Ошибка чата", error_message)

    @pyqtSlot(bool)
    def update_remote_client_status(self, is_connected):
        try:
            if hasattr(self.remote_client_tab, 'status_label') and self.remote_client_tab.status_label:
                if is_connected:
                    self.remote_client_tab.status_label.setText("✅ Подключен")
                    self.remote_client_tab.status_label.setProperty(
                        "class", "status status-active")
                else:
                    self.remote_client_tab.status_label.setText(
                        "❌ Не подключен")
                    self.remote_client_tab.status_label.setProperty(
                        "class", "status status-inactive")
        except Exception as e:
            print(f"Ошибка обновления статуса клиента: {e}")

    def closeEvent(self, event):
        if self.screen_recorder.recording:
            self.screen_recorder.stop_recording()

        if self.camera_recorder.recording:
            self.camera_recorder.stop_recording()

        if self.remote_server.running:
            self.remote_server.stop_server()

        if self.chat_server.running:
            self.chat_server.stop_server()

        if self.chat_client.connected:
            self.chat_client.disconnect_from_server()

        if self.remote_client.connected:
            self.remote_client.disconnect_from_server()

        self.settings_tab.save_settings()

        if hasattr(self, 'status_timer'):
            self.status_timer.stop()

        event.accept()

    def center(self):
        screen = QApplication.primaryScreen()
        rect = screen.geometry()
        size = self.geometry()
        self.move((rect.width() - size.width()) // 2,
                  (rect.height() - size.height()) // 2)
