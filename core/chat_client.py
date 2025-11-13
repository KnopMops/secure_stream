import socket
import threading
import json
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal


class ChatClient(QObject):
    message_received = pyqtSignal(str, str)
    user_list_updated = pyqtSignal(list)
    connection_status_changed = pyqtSignal(bool)
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.connected = False
        self.socket = None
        self.username = "Клиент"
        self.server_host = "localhost"
        self.server_port = 8081
        self.thread = None

    def connect_to_server(self, host, port, username="Клиент"):
        try:
            self.server_host = host
            self.server_port = port
            self.username = username

            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))

            self.connected = True
            self.thread = threading.Thread(target=self._listen_for_messages)
            self.thread.daemon = True
            self.thread.start()

            self.connection_status_changed.emit(True)
            return True

        except Exception as e:
            self.error_occurred.emit(f"Ошибка подключения: {e}")
            return False

    def disconnect_from_server(self):
        self.connected = False

        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None

        if self.thread:
            self.thread.join(timeout=2.0)

        self.connection_status_changed.emit(False)

    def _listen_for_messages(self):
        while self.connected:
            try:
                data = self.socket.recv(1024).decode('utf-8')
                if not data:
                    break

                message_data = json.loads(data)

                if message_data.get('type') == 'message':
                    username = message_data.get('username', '')
                    message = message_data.get('message', '')
                    self.message_received.emit(username, message)

                elif message_data.get('type') == 'system':
                    username = message_data.get('username', 'Система')
                    message = message_data.get('message', '')
                    self.message_received.emit(username, message)

                elif message_data.get('type') == 'user_list':
                    users = message_data.get('users', [])
                    self.user_list_updated.emit(users)

            except json.JSONDecodeError:
                continue
            except Exception as e:
                if self.connected:
                    self.error_occurred.emit(
                        f"Ошибка получения сообщения: {e}")
                break

    def send_message(self, message):
        if self.connected and self.socket:
            try:
                message_data = {
                    'type': 'message',
                    'message': message,
                    'username': self.username,
                    'timestamp': datetime.now().isoformat()
                }
                self.socket.send(json.dumps(message_data).encode('utf-8'))
                return True
            except Exception as e:
                self.error_occurred.emit(f"Ошибка отправки сообщения: {e}")
                return False
        return False

    def change_username(self, new_username):
        if self.connected and self.socket:
            try:
                rename_data = {
                    'type': 'rename',
                    'username': new_username,
                    'timestamp': datetime.now().isoformat()
                }
                self.socket.send(json.dumps(rename_data).encode('utf-8'))
                self.username = new_username
                return True
            except Exception as e:
                self.error_occurred.emit(f"Ошибка смены имени: {e}")
                return False
        return False

    def get_connection_status(self):
        return {
            "connected": self.connected,
            "host": self.server_host,
            "port": self.server_port,
            "username": self.username
        }
