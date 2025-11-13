import socket
import threading
import time
import io
import struct
import json

from PIL import ImageGrab
from .audio_capture import AudioCapture


class RemoteAccessServer:
    def __init__(self):
        self.running = False

        self.server_socket = None
        self.thread = None

        self.clients = []

        self.port = 8080

        self.audio_recorder = AudioCapture()
        self.audio_enabled = False
        self.audio_device = 0

    def start_server(self, port=8080, audio_enabled=False, audio_device=0):
        try:
            self.port = port
            self.audio_enabled = audio_enabled
            self.audio_device = audio_device

            self.server_socket = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(
                socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            self.server_socket.bind(('0.0.0.0', port))
            self.server_socket.listen(5)

            self.server_socket.settimeout(1.0)

            self.running = True

            if self.audio_enabled:
                self.audio_recorder.start_recording(device_index=audio_device)

            self.thread = threading.Thread(target=self._accept_clients)

            self.thread.daemon = True
            self.thread.start()

            return True

        except Exception as e:
            print(f'[START_SERVER_ERROR]: {e}')
            return False

    def stop_server(self):
        self.running = False

        if self.audio_enabled:
            self.audio_recorder.stop_recording()

        for client_socket, addr in self.clients:
            try:
                client_socket.close()

            except:
                pass

        self.clients.clear()

        if self.server_socket:
            self.server_socket.close()

        if self.thread:
            self.thread.join(timeout=3.0)

        return True

    def _accept_clients(self):
        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()

                print(f'Подключен клиент: {addr}')

                self.clients.append((client_socket, addr))

                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, addr)
                )

                client_thread.daemon = True
                client_thread.start()

            except socket.timeout:
                continue

            except Exception as e:
                if self.running:
                    print(f'[_ACCEPT_CLIENTS_ERROR]: {e}')

                break

    def _handle_client(self, client_socket, addr):
        try:
            welcome_msg = {
                'type': 'system',
                'message': 'Вы присоединились к SecureStream Remote Access',
                'timestamp': time.time()
            }

            welcome_json = json.dumps(welcome_msg).encode('utf-8')
            data_type = struct.pack('>B', 255)
            client_socket.sendall(data_type)

            welcome_size = struct.pack('>L', len(welcome_json))
            client_socket.sendall(welcome_size)
            client_socket.sendall(welcome_json)

            while self.running:
                try:
                    img = ImageGrab.grab()
                    if img.mode in ('RGBA', 'LA', 'P'):
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        rgb_img = img.convert('RGB')
                        img = rgb_img
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')

                    img_bytes = io.BytesIO()

                    img.save(img_bytes, format='JPEG', quality=70)
                    img_data = img_bytes.getvalue()
                    print(
                        f"Server: Захвачен экран, размер: {len(img_data)} байт")

                    data_type = struct.pack('>B', 0)
                    client_socket.sendall(data_type)

                    size_data = struct.pack('>L', len(img_data))
                    client_socket.sendall(size_data)
                    print(
                        f"Server: Отправлен размер данных: {len(img_data)} байт")

                    client_socket.sendall(img_data)
                    print(
                        f"Server: Отправлены данные изображения: {len(img_data)} байт")

                    if self.audio_enabled:
                        audio_data = self._get_audio_data()
                        if audio_data:
                            audio_type = struct.pack('>B', 1)
                            client_socket.sendall(audio_type)

                            audio_size = struct.pack('>L', len(audio_data))
                            client_socket.sendall(audio_size)
                            client_socket.sendall(audio_data)
                            print(
                                f"Server: Отправлены аудио данные: {len(audio_data)} байт")

                    client_socket.settimeout(1.0)

                    try:
                        data = client_socket.recv(1, socket.MSG_PEEK)

                    except socket.timeout:
                        pass

                    except:
                        break

                    time.sleep(0.1)

                except Exception as e:
                    print(f'Ошибка при отправке данных клиенту {addr}: {e}')
                    break

        except Exception as e:
            print(f'Ошибка обработки клиента {addr}: {e}')

        finally:
            if (client_socket, addr) in self.clients:
                self.clients.remove((client_socket, addr))

            client_socket.close()

            print(f'Клиент отключен: {addr}')

    def _get_audio_data(self):
        try:
            if self.audio_enabled and hasattr(self.audio_recorder, 'audio_data'):
                if self.audio_recorder.audio_data:
                    import numpy as np
                    audio_chunk = self.audio_recorder.audio_data[-1] if self.audio_recorder.audio_data else None
                    if audio_chunk is not None:
                        if not isinstance(audio_chunk, np.ndarray):
                            return None
                        if audio_chunk.dtype != np.int16:
                            if audio_chunk.dtype == np.float32:
                                audio_chunk = (
                                    audio_chunk * 32767).astype(np.int16)
                            elif audio_chunk.dtype == np.float64:
                                audio_chunk = (
                                    audio_chunk * 32767).astype(np.int16)
                            else:
                                audio_chunk = audio_chunk.astype(np.int16)
                        return audio_chunk.tobytes()
            return None
        except Exception as e:
            print(f"Ошибка получения аудио данных: {e}")
            import traceback
            traceback.print_exc()
            return None

    def get_available_audio_devices(self):
        return self.audio_recorder.get_available_devices()

    def set_audio_settings(self, enabled, device_index=0):
        self.audio_enabled = enabled
        self.audio_device = device_index

    def get_server_status(self):
        status = {
            'running': self.running,
            'port': self.port,
            'clients_connected': len(self.clients),
            'audio_enabled': self.audio_enabled
        }

        if self.audio_enabled:
            audio_status = self.audio_recorder.get_recording_status()
            status.update({
                'audio_recording': audio_status['recording'],
                'audio_sample_rate': audio_status['sample_rate'],
                'audio_channels': audio_status['channels']
            })

        return status
