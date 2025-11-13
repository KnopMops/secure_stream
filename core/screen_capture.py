from multiprocessing.process import parent_process
import cv2
import numpy as np
import threading
import time
import os

from datetime import datetime
from PIL import ImageGrab, PngImagePlugin
from .audio_capture import AudioCapture
from .video_processor import VideoProcessor


class ScreenRecorder:
    def __init__(self):
        self.recording = False
        self.frames = []

        self.thread = None

        self.quality = 'high'
        self.fps = 30

        self.audio_recorder = AudioCapture()
        self.audio_enabled = False
        self.audio_device = 0

        self.video_processor = VideoProcessor()
        self.merge_enabled = True

    def start_recording(self, save_path, fps=30, quality='high', audio_enabled=False, audio_device=0, merge_enabled=True):
        self.recording = True

        self.quality = quality
        self.fps = fps
        self.audio_enabled = audio_enabled
        self.audio_device = audio_device
        self.merge_enabled = merge_enabled

        self.frames = []

        if not os.path.exists(save_path):
            os.makedirs(save_path)

        if self.audio_enabled:
            self.audio_recorder.start_recording(device_index=audio_device)

        self.thread = threading.Thread(
            target=self._record_screen, args=(save_path,))
        self.thread.daemon = True

        self.thread.start()

        return True

    def stop_recording(self):
        self.recording = False

        if self.audio_enabled:
            self.audio_recorder.stop_recording()

        if self.thread:
            self.thread.join(timeout=5.0)

        return True

    def _record_screen(self, save_path):
        try:
            screen_size = ImageGrab.grab().size

            if self.quality == 'low':
                codec = 'XVID'
                quality_factor = 0.6

            elif self.quality == 'medium':
                codec = 'XVID'
                quality_factor = 0.8

            else:
                codec = 'MJPG'
                quality_factor = 1.0

            fourcc = cv2.VideoWriter.fourcc(*codec)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = os.path.join(
                save_path, f'screen_record_{timestamp}.avi')

            out = cv2.VideoWriter(filename, fourcc, self.fps, screen_size)

            frame_count = 0

            while self.recording:
                try:
                    try:
                        img = ImageGrab.grab()
                    except Exception as grab_error:
                        print(f'Ошибка захвата экрана: {grab_error}')
                        time.sleep(1 / self.fps)
                        continue

                    frame = np.array(img)
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                    out.write(frame)
                    frame_count += 1

                    time.sleep(1 / self.fps)

                except Exception as e:
                    print(f'Ошибка при записи кадра: {e}')
                    time.sleep(1 / self.fps)
                    continue

            out.release()

            audio_filename = None
            if self.audio_enabled:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                audio_filename = os.path.join(
                    save_path, f'screen_audio_{timestamp}.wav')
                self.audio_recorder.save_audio(audio_filename)

            print(f'Запись завершена. Сохранено кадров: {frame_count}')

            if self.merge_enabled and self.audio_enabled and audio_filename and os.path.exists(audio_filename):
                self._merge_video_audio(filename, audio_filename, save_path)

        except Exception as e:
            print(f'Ошибка в потоке записи: {e}')

    def take_screenshot(self, save_path, quality='high'):
        try:
            if not os.path.exists(save_path):
                os.makedirs(save_path)

            img = ImageGrab.grab()

            if quality == 'low':
                img = img.resize((img.size[0] // 2, img.size[1] // 2))
            elif quality == 'medium':
                img = img.resize(
                    (int(img.size[0] * 0.75), int(img.size[1] * 0.75)))

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = os.path.join(save_path, f'screenshot_{timestamp}.png')

            metadata = PngImagePlugin.PngInfo()
            metadata.add_text('Software', 'SecureStream v1.0')
            metadata.add_text('CreationTime', datetime.now().isoformat())
            metadata.add_text('Resolution', f'{img.size[0]}x{img.size[1]}')

            img.save(filename, 'PNG', pnginfo=metadata)

            return filename

        except Exception as e:
            print(f'Ошибка при создании скриншота: {e}')
            return None

    def get_recording_status(self):
        status = {
            'recording': self.recording,
            'fps': self.fps,
            'quality': self.quality,
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

    def get_available_audio_devices(self):
        return self.audio_recorder.get_available_devices()

    def set_audio_settings(self, enabled, device_index=0):
        self.audio_enabled = enabled
        self.audio_device = device_index

    def _merge_video_audio(self, video_path, audio_path, save_path):
        try:
            print("Начинаем склеивание видео и аудио...")

            base_name = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(save_path, f"{base_name}_merged.mp4")

            result = self.video_processor.merge_video_audio(
                video_path, audio_path, output_path, self.quality
            )

            if result['success']:
                print(f"✅ Видео и аудио успешно склеены: {output_path}")
                print(f"Размер файла: {result.get('file_size', 0)} байт")

                if os.path.exists(output_path):
                    self.video_processor.cleanup_temp_files(
                        video_path, audio_path)
                    print("Временные файлы удалены")
            else:
                print(f"❌ Ошибка склеивания: {result['error']}")

        except Exception as e:
            print(f"Ошибка при склеивании видео и аудио: {e}")

    def get_ffmpeg_status(self):
        return self.video_processor.get_ffmpeg_info()

    def set_merge_settings(self, enabled):
        self.merge_enabled = enabled
