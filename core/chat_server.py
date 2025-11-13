import socket
import threading
import json
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal


class ChatServer(QObject):
    message_received = pyqtSignal(str, str)
    user_list_updated = pyqtSignal(list)
    connection_status_changed = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.running = False
        self.server_socket = None
        self.clients = {}
        self.thread = None
        self.port = 8081

    def start_server(self, port=8081):
        try:
            self.port = port
            self.server_socket = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(
                socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('0.0.0.0', port))
            self.server_socket.listen(5)
            self.server_socket.settimeout(1.0)

            self.running = True
            self.thread = threading.Thread(target=self._accept_clients)
            self.thread.daemon = True
            self.thread.start()

            self.connection_status_changed.emit(True)
            return True

        except Exception as e:
            print(f"Ошибка запуска чат-сервера: {e}")
            return False

    def stop_server(self):
        self.running = False

        if self.clients:
            shutdown_msg = {
                'type': 'system',
                'message': 'Сервер чата выключается',
                'username': 'Система',
                'timestamp': datetime.now().isoformat()
            }
            self._broadcast(json.dumps(shutdown_msg))

        for client_socket in list(self.clients.keys()):
            try:
                client_socket.close()
            except:
                pass
        self.clients.clear()

        if self.server_socket:
            self.server_socket.close()

        if self.thread:
            self.thread.join(timeout=3.0)

        self.user_list_updated.emit([])
        self.connection_status_changed.emit(False)
        return True

    def _accept_clients(self):
        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()
                print(f"Новое подключение к чату: {addr}")

                temp_username = f"User_{addr[0].replace('.', '_')}_{len(self.clients) + 1}"

                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, temp_username, addr)
                )
                client_thread.daemon = True
                client_thread.start()

            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"Ошибка при принятии подключения к чату: {e}")
                break

    def _handle_client(self, client_socket, username, addr):
        try:
            self.clients[client_socket] = {
                'username': username,
                'address': addr,
                'join_time': datetime.now()
            }

            welcome_msg = {
                'type': 'system',
                'message': f'Добро пожаловать в чат! Ваше имя: {username}',
                'username': 'Система',
                'timestamp': datetime.now().isoformat()
            }
            client_socket.send(json.dumps(welcome_msg).encode('utf-8'))

            self._broadcast_user_list()

            join_msg = {
                'type': 'system',
                'message': f'{username} присоединился к чату',
                'username': 'Система',
                'timestamp': datetime.now().isoformat()
            }
            self._broadcast(json.dumps(join_msg))
            self.message_received.emit(
                'Система', f'{username} присоединился к чату')

            while self.running:
                try:
                    data = client_socket.recv(1024).decode('utf-8')
                    if not data:
                        break

                    message_data = json.loads(data)

                    if message_data.get('type') == 'message':
                        message = message_data.get('message', '').strip()
                        if message:
                            broadcast_msg = {
                                'type': 'message',
                                'username': username,
                                'message': message,
                                'timestamp': datetime.now().isoformat()
                            }
                            self._broadcast(json.dumps(broadcast_msg))
                            self.message_received.emit(username, message)

                    elif message_data.get('type') == 'rename':
                        new_username = message_data.get('username', '').strip()
                        if new_username and new_username != username:
                            old_username = username
                            username = new_username
                            self.clients[client_socket]['username'] = username
                            self._broadcast_user_list()

                            rename_msg = {
                                'type': 'system',
                                'message': f'{old_username} сменил имя на {username}',
                                'username': 'Система',
                                'timestamp': datetime.now().isoformat()
                            }
                            self._broadcast(json.dumps(rename_msg))
                            self.message_received.emit(
                                'Система', f'{old_username} сменил имя на {username}')

                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    print(f"Ошибка обработки сообщения от {username}: {e}")
                    break

        except Exception as e:
            print(f"Ошибка обработки клиента чата {username}: {e}")
        finally:
            if client_socket in self.clients:
                disconnected_user = self.clients[client_socket]['username']
                del self.clients[client_socket]
                client_socket.close()

                if self.running:
                    leave_msg = {
                        'type': 'system',
                        'message': f'{disconnected_user} покинул чат',
                        'username': 'Система',
                        'timestamp': datetime.now().isoformat()
                    }
                    self._broadcast(json.dumps(leave_msg))
                    self.message_received.emit(
                        'Система', f'{disconnected_user} покинул чат')
                    self._broadcast_user_list()

    def _broadcast(self, message):
        disconnected_clients = []

        for client_socket in self.clients.keys():
            try:
                client_socket.send(message.encode('utf-8'))
            except:
                disconnected_clients.append(client_socket)

        for client_socket in disconnected_clients:
            if client_socket in self.clients:
                del self.clients[client_socket]

    def _broadcast_user_list(self):
        user_list = [info['username'] for info in self.clients.values()]
        user_list_msg = {
            'type': 'user_list',
            'users': user_list,
            'timestamp': datetime.now().isoformat()
        }
        self._broadcast(json.dumps(user_list_msg))
        self.user_list_updated.emit(user_list)

    def send_message(self, username, message):
        if self.running and self.clients:
            server_msg = {
                'type': 'message',
                'username': username,
                'message': message,
                'timestamp': datetime.now().isoformat()
            }
            self._broadcast(json.dumps(server_msg))
            self.message_received.emit(username, message)

    def get_server_status(self):
        return {
            "running": self.running,
            "port": self.port,
            "users_connected": len(self.clients),
            "users": [info['username'] for info in self.clients.values()]
        }
