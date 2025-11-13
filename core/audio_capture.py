import pyaudio
import wave
import threading
import time
import os
from datetime import datetime
import sounddevice as sd
import numpy as np


class AudioRecorder:
    def __init__(self):
        self.recording = False
        self.audio_data = []
        self.thread = None

        self.sample_rate = 44100
        self.channels = 2
        self.chunk_size = 1024
        self.audio_format = pyaudio.paInt16

        self.p = None
        self.stream = None

    def get_available_audio_devices(self):
        devices = []

        if self.p is None:
            self.p = pyaudio.PyAudio()

        try:
            device_count = self.p.get_device_count()

            for i in range(device_count):
                device_info = self.p.get_device_info_by_index(i)

                if device_info['maxInputChannels'] > 0:
                    devices.append({
                        'index': i,
                        'name': device_info['name'],
                        'channels': device_info['maxInputChannels'],
                        'sample_rate': int(device_info['defaultSampleRate'])
                    })

        except Exception as e:
            print(f"Ошибка получения аудио устройств: {e}")

        return devices if devices else [{'index': 0, 'name': 'Микрофон по умолчанию', 'channels': 2, 'sample_rate': 44100}]

    def start_recording(self, device_index=0, sample_rate=44100, channels=2):
        try:
            self.sample_rate = sample_rate
            self.channels = channels
            self.recording = True
            self.audio_data = []

            if self.p is None:
                self.p = pyaudio.PyAudio()

            self.stream = self.p.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self.chunk_size
            )

            self.thread = threading.Thread(target=self._record_audio)
            self.thread.daemon = True
            self.thread.start()

            return True

        except Exception as e:
            print(f"Ошибка запуска записи аудио: {e}")
            return False

    def stop_recording(self):
        self.recording = False

        if self.thread:
            self.thread.join(timeout=3.0)

        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

        return True

    def _record_audio(self):
        try:
            while self.recording and self.stream:
                try:
                    data = self.stream.read(
                        self.chunk_size, exception_on_overflow=False)
                    self.audio_data.append(data)
                except Exception as e:
                    print(f"Ошибка чтения аудио данных: {e}")
                    break

        except Exception as e:
            print(f"Ошибка в потоке записи аудио: {e}")

    def save_audio(self, file_path, format='wav'):
        try:
            if not self.audio_data:
                return None

            if not os.path.exists(os.path.dirname(file_path)):
                os.makedirs(os.path.dirname(file_path))

            if format.lower() == 'wav':
                with wave.open(file_path, 'wb') as wf:
                    wf.setnchannels(self.channels)
                    wf.setsampwidth(self.p.get_sample_size(self.audio_format))
                    wf.setframerate(self.sample_rate)
                    wf.writeframes(b''.join(self.audio_data))

            return file_path

        except Exception as e:
            print(f"Ошибка сохранения аудио: {e}")
            return None

    def get_recording_status(self):
        return {
            'recording': self.recording,
            'sample_rate': self.sample_rate,
            'channels': self.channels,
            'data_length': len(self.audio_data)
        }

    def cleanup(self):
        self.stop_recording()

        if self.p:
            self.p.terminate()
            self.p = None


class AudioCapture:
    def __init__(self):
        self.recording = False
        self.audio_data = []
        self.thread = None
        self.sample_rate = 44100
        self.channels = 2

    def get_available_devices(self):
        try:
            devices = sd.query_devices()
            input_devices = []

            for i, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    input_devices.append({
                        'index': i,
                        'name': device['name'],
                        'channels': device['max_input_channels'],
                        'sample_rate': device['default_samplerate']
                    })

            return input_devices

        except Exception as e:
            print(f"Ошибка получения устройств sounddevice: {e}")
            return [{'index': 0, 'name': 'Микрофон по умолчанию', 'channels': 2, 'sample_rate': 44100}]

    def start_recording(self, device_index=0, sample_rate=44100, channels=2):
        try:
            self.sample_rate = sample_rate
            self.channels = channels
            self.recording = True
            self.audio_data = []

            self.thread = threading.Thread(
                target=self._record_audio,
                args=(device_index,)
            )
            self.thread.daemon = True
            self.thread.start()

            return True

        except Exception as e:
            print(f"Ошибка запуска записи аудио: {e}")
            return False

    def stop_recording(self):
        self.recording = False

        if self.thread:
            self.thread.join(timeout=3.0)

        return True

    def _record_audio(self, device_index):
        try:
            def audio_callback(indata, frames, time, status):
                if self.recording:
                    self.audio_data.append(indata.copy())

            with sd.InputStream(
                device=device_index,
                channels=self.channels,
                samplerate=self.sample_rate,
                callback=audio_callback
            ):
                while self.recording:
                    time.sleep(0.1)

        except Exception as e:
            print(f"Ошибка в потоке записи аудио: {e}")

    def save_audio(self, file_path, format='wav'):
        try:
            if not self.audio_data:
                print("Нет аудио данных для сохранения")
                return None

            if not os.path.exists(os.path.dirname(file_path)):
                os.makedirs(os.path.dirname(file_path))

            audio_array = np.concatenate(self.audio_data, axis=0)

            print(
                f"Сохраняем аудио: {len(audio_array)} сэмплов, {self.sample_rate} Гц")

            if format.lower() == 'wav':
                import soundfile as sf
                sf.write(file_path, audio_array, self.sample_rate)
                print(f"Аудио сохранено в WAV: {file_path}")
            elif format.lower() == 'mp3':
                import soundfile as sf
                sf.write(file_path, audio_array, self.sample_rate)
                print(f"Аудио сохранено в MP3: {file_path}")

            return file_path

        except Exception as e:
            print(f"Ошибка сохранения аудио: {e}")
            import traceback
            traceback.print_exc()
            return None

    def get_recording_status(self):
        return {
            'recording': self.recording,
            'sample_rate': self.sample_rate,
            'channels': self.channels,
            'data_length': len(self.audio_data)
        }
