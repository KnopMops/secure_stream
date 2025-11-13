import socket
import threading
import json
import cv2
import numpy as np
import time
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QLabel


class RemoteClient(QObject):
    connection_status_changed = pyqtSignal(bool)
    screen_frame_received = pyqtSignal(QPixmap)
    audio_data_received = pyqtSignal(bytes)
    error_occurred = pyqtSignal(str)
    server_info_received = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.connected = False
        self.socket = None
        self.server_host = "localhost"
        self.server_port = 8080
        self.thread = None
        self.frame_timer = QTimer()
        self.frame_timer.timeout.connect(self._request_frame)
        self.current_frame = None

    def connect_to_server(self, host, port):
        try:
            self.server_host = host
            self.server_port = port

            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))

            self.connected = True
            self.thread = threading.Thread(target=self._listen_for_data)
            self.thread.daemon = True
            self.thread.start()

            self._send_command("get_info")

            self.connection_status_changed.emit(True)
            return True

        except Exception as e:
            self.error_occurred.emit(f"Ошибка подключения: {e}")
            return False

    def disconnect_from_server(self):
        try:
            self.connected = False
            self.frame_timer.stop()

            if self.socket:
                try:
                    self.socket.shutdown(socket.SHUT_RDWR)
                except:
                    pass
                try:
                    self.socket.close()
                except:
                    pass
                self.socket = None

            if self.thread:
                self.thread.join(timeout=2.0)

            self.connection_status_changed.emit(False)
            return True
        except Exception as e:
            print(f"Ошибка при отключении: {e}")
            return False

    def start_screen_stream(self, fps=10):
        if self.connected:
            self._send_command("start_stream", {"fps": fps})
            self.frame_timer.start(int(1000 / fps))

    def stop_screen_stream(self):
        if self.connected:
            self._send_command("stop_stream")
            self.frame_timer.stop()

    def _send_command(self, command, data=None):
        if self.connected and self.socket:
            try:
                message = {
                    "command": command,
                    "data": data or {},
                    "timestamp": time.time()
                }
                self.socket.send(json.dumps(message).encode('utf-8'))
            except Exception as e:
                self.error_occurred.emit(f"Ошибка отправки команды: {e}")

    def _request_frame(self):
        if self.connected:
            self._send_command("get_frame")

    def _listen_for_data(self):
        print("RemoteClient: Начинаем прослушивание данных от сервера")

        while self.connected:
            try:
                data_type = self.socket.recv(1)
                if not data_type:
                    print("RemoteClient: Нет данных от сервера")
                    break

                data_type = int.from_bytes(data_type, byteorder='big')

                size_data = self.socket.recv(4)
                if not size_data:
                    print("RemoteClient: Нет размера данных")
                    break

                data_size = int.from_bytes(size_data, byteorder='big')
                print(
                    f"RemoteClient: Получен размер данных: {data_size} байт, тип: {data_type}")

                received_data = b''
                while len(received_data) < data_size:
                    chunk = self.socket.recv(
                        min(data_size - len(received_data), 4096))
                    if not chunk:
                        break
                    received_data += chunk

                if len(received_data) == data_size:
                    print(
                        f"RemoteClient: Получены данные: {len(received_data)} байт")

                    if data_type == 255:
                        print("RemoteClient: Обрабатываем приветственное сообщение")
                        self._process_received_data(received_data)
                    elif data_type == 0:
                        print("RemoteClient: Обрабатываем кадр экрана")
                        self._decode_frame(received_data)
                    elif data_type == 1:
                        print("RemoteClient: Обрабатываем аудио данные")
                        self.audio_data_received.emit(received_data)
                else:
                    print(
                        f"RemoteClient: Неполные данные: {len(received_data)}/{data_size}")

            except Exception as e:
                if self.connected:
                    print(f"RemoteClient: Ошибка получения данных: {e}")
                    self.error_occurred.emit(f"Ошибка получения данных: {e}")
                break

    def _process_received_data(self, data):
        try:
            try:
                message = json.loads(data.decode('utf-8'))
                if message.get('type') == 'info':
                    self.server_info_received.emit(message.get('data', {}))
                return
            except:
                pass

            self._decode_frame(data)

        except Exception as e:
            self.error_occurred.emit(f"Ошибка обработки данных: {e}")

    def _decode_frame(self, frame_data):
        try:
            print(
                f"RemoteClient: Декодируем кадр размером {len(frame_data)} байт")
            nparr = np.frombuffer(frame_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if frame is not None:
                print(f"RemoteClient: Кадр декодирован: {frame.shape}")
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame_rgb.shape
                bytes_per_line = ch * w

                qt_image = QImage(frame_rgb.data, w, h,
                                  bytes_per_line, QImage.Format.Format_RGB888)
                pixmap = QPixmap.fromImage(qt_image)

                print("RemoteClient: Отправляем кадр в UI")
                self.screen_frame_received.emit(pixmap)
            else:
                print("RemoteClient: Не удалось декодировать кадр")

        except Exception as e:
            print(f"RemoteClient: Ошибка декодирования кадра: {e}")
            self.error_occurred.emit(f"Ошибка декодирования кадра: {e}")

    def send_mouse_click(self, x, y, button="left"):
        if self.connected:
            self._send_command("mouse_click", {
                "x": x, "y": y, "button": button
            })

    def send_mouse_move(self, x, y):
        if self.connected:
            self._send_command("mouse_move", {
                "x": x, "y": y
            })

    def send_key_press(self, key):
        if self.connected:
            self._send_command("key_press", {
                "key": key
            })

    def get_connection_status(self):
        return {
            "connected": self.connected,
            "host": self.server_host,
            "port": self.server_port
        }
