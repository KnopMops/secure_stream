import cv2
import threading
import time
import os

from datetime import datetime
from .audio_capture import AudioCapture
from .video_processor import VideoProcessor


class CameraRecorder:
    def __init__(self):
        self.recording = False

        self.cap = None
        self.thread = None

        self.available_cameras = []

        self.audio_recorder = AudioCapture()
        self.audio_enabled = False
        self.audio_device = 0

        self.video_processor = VideoProcessor()
        self.merge_enabled = True

    def get_available_cameras(self):
        self.available_cameras = []

        for i in range(5):
            cap = cv2.VideoCapture(i)

            if cap.isOpened():
                ret, frame = cap.read()

                if ret:
                    self.available_cameras.append({
                        'index': i,
                        'name': f'Камера {i}',
                        'resolution': f'{int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}'
                    })

                    cap.release()

        return self.available_cameras if self.available_cameras else [{'index': 0, 'name': 'Камера не найдена', 'resolution': 'Нет'}]

    def start_recording(self, camera_index, save_path, quality='high', audio_enabled=False, audio_device=0, merge_enabled=True):
        try:
            self.cap = cv2.VideoCapture(camera_index)

            if not self.cap.isOpened():
                return False

            frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            fps = self.cap.get(cv2.CAP_PROP_FPS)

            if fps <= 0:
                fps = 30

            if quality == "low":
                codec = 'XVID'
                frame_width = frame_width // 2
                frame_height = frame_height // 2
            elif quality == "medium":
                codec = 'XVID'
                frame_width = int(frame_width * 0.75)
                frame_height = int(frame_height * 0.75)
            else:
                codec = 'MJPG'

            if not os.path.exists(save_path):
                os.makedirs(save_path)

            fourcc = cv2.VideoWriter_fourcc(*codec)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(
                save_path, f"camera_record_{timestamp}.avi")

            self.out = cv2.VideoWriter(
                filename, fourcc, fps, (frame_width, frame_height))

            self.video_filename = filename

            self.audio_enabled = audio_enabled
            self.audio_device = audio_device
            self.save_path = save_path
            self.merge_enabled = merge_enabled

            if self.audio_enabled:
                self.audio_recorder.start_recording(device_index=audio_device)

            self.recording = True

            self.thread = threading.Thread(target=self._record_camera)
            self.thread.daemon = True

            self.thread.start()

            return True

        except Exception as e:
            print(f'Ошибка при запуске записи с камеры: {e}')
            return False

    def stop_recording(self):
        self.recording = False

        if self.audio_enabled:
            self.audio_recorder.stop_recording()

        if self.thread:
            self.thread.join(timeout=3.0)

        if self.cap:
            self.cap.release()

        if hasattr(self, 'out'):
            self.out.release()

        return True

    def _record_camera(self):
        frame_count = 0

        while self.recording and self.cap.isOpened():
            try:
                ret, frame = self.cap.read()

                if ret:
                    if hasattr(self, 'out'):
                        self.out.write(frame)

                    frame_count += 1

                else:
                    break

                time.sleep(0.03)

            except Exception as e:
                print(f'Ошибка при записи кадра с камеры: {e}')
                break

        audio_filename = None
        if self.audio_enabled:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_path = getattr(self, 'save_path', 'recordings/camera')
            audio_filename = os.path.join(
                save_path, f'camera_audio_{timestamp}.wav')
            self.audio_recorder.save_audio(audio_filename)

        print(f'Запись с камеры завершена. Сохранено кадров: {frame_count}')

        if self.merge_enabled and self.audio_enabled and audio_filename and os.path.exists(audio_filename):
            video_filename = getattr(self, 'video_filename', None)
            if video_filename:
                self._merge_video_audio(
                    video_filename, audio_filename, save_path)

    def get_recording_status(self):
        status = {
            'recording': self.recording,
            'camera_available': self.cap.isOpened() if self.cap else False,
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
                video_path, audio_path, output_path, 'high'
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
