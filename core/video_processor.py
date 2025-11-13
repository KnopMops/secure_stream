import os
import subprocess
import shutil
from datetime import datetime
from typing import Optional, Dict, List


class VideoProcessor:
    def __init__(self):
        self.ffmpeg_path = self._find_ffmpeg()
        self.enabled = self.ffmpeg_path is not None

    def _find_ffmpeg(self) -> Optional[str]:
        possible_paths = [
            'ffmpeg',
            'ffmpeg.exe',
            r'C:\ffmpeg\bin\ffmpeg.exe',
            '/usr/bin/ffmpeg',
            '/usr/local/bin/ffmpeg',
        ]

        for path in possible_paths:
            if shutil.which(path):
                return path

        return None

    def is_available(self) -> bool:
        return self.enabled

    def get_ffmpeg_info(self) -> Dict:
        if not self.enabled:
            return {
                'available': False,
                'path': None,
                'version': None,
                'error': 'FFmpeg не найден'
            }

        try:
            result = subprocess.run(
                [self.ffmpeg_path, '-version'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                return {
                    'available': True,
                    'path': self.ffmpeg_path,
                    'version': version_line,
                    'error': None
                }
            else:
                return {
                    'available': False,
                    'path': self.ffmpeg_path,
                    'version': None,
                    'error': f'Ошибка запуска: {result.stderr}'
                }
        except Exception as e:
            return {
                'available': False,
                'path': self.ffmpeg_path,
                'version': None,
                'error': f'Исключение: {str(e)}'
            }

    def merge_video_audio(self, video_path: str, audio_path: str,
                          output_path: str, quality: str = 'high') -> Dict:
        if not self.enabled:
            return {
                'success': False,
                'error': 'FFmpeg недоступен',
                'output_file': None
            }

        try:
            if not os.path.exists(video_path):
                return {
                    'success': False,
                    'error': f'Видео файл не найден: {video_path}',
                    'output_file': None
                }

            if not os.path.exists(audio_path):
                return {
                    'success': False,
                    'error': f'Аудио файл не найден: {audio_path}',
                    'output_file': None
                }

            quality_settings = {
                'high': ['-c:v', 'libx264', '-crf', '18', '-preset', 'slow'],
                'medium': ['-c:v', 'libx264', '-crf', '23', '-preset', 'medium'],
                'low': ['-c:v', 'libx264', '-crf', '28', '-preset', 'fast']
            }

            settings = quality_settings.get(
                quality, quality_settings['medium'])

            cmd = [
                self.ffmpeg_path,
                '-i', video_path,
                '-i', audio_path,
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-strict', 'experimental',
                '-shortest',
                '-y',
            ] + settings + [output_path]

            print(f"Выполняем команду FFmpeg: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0 and os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                return {
                    'success': True,
                    'error': None,
                    'output_file': output_path,
                    'file_size': file_size,
                    'ffmpeg_output': result.stdout
                }
            else:
                return {
                    'success': False,
                    'error': f'Ошибка FFmpeg: {result.stderr}',
                    'output_file': None,
                    'ffmpeg_output': result.stdout
                }

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Превышено время ожидания FFmpeg',
                'output_file': None
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Исключение: {str(e)}',
                'output_file': None
            }

    def convert_to_mp4(self, input_path: str, output_path: str,
                       quality: str = 'high') -> Dict:
        if not self.enabled:
            return {
                'success': False,
                'error': 'FFmpeg недоступен',
                'output_file': None
            }

        try:
            if not os.path.exists(input_path):
                return {
                    'success': False,
                    'error': f'Входной файл не найден: {input_path}',
                    'output_file': None
                }

            quality_settings = {
                'high': ['-c:v', 'libx264', '-crf', '18', '-preset', 'slow'],
                'medium': ['-c:v', 'libx264', '-crf', '23', '-preset', 'medium'],
                'low': ['-c:v', 'libx264', '-crf', '28', '-preset', 'fast']
            }

            settings = quality_settings.get(
                quality, quality_settings['medium'])

            cmd = [
                self.ffmpeg_path,
                '-i', input_path,
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-y'
            ] + settings + [output_path]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0 and os.path.exists(output_path):
                return {
                    'success': True,
                    'error': None,
                    'output_file': output_path
                }
            else:
                return {
                    'success': False,
                    'error': f'Ошибка конвертации: {result.stderr}',
                    'output_file': None
                }

        except Exception as e:
            return {
                'success': False,
                'error': f'Исключение: {str(e)}',
                'output_file': None
            }

    def get_video_info(self, video_path: str) -> Dict:
        if not self.enabled:
            return {'error': 'FFmpeg недоступен'}

        try:
            cmd = [
                self.ffmpeg_path,
                '-i', video_path,
                '-f', 'null',
                '-'
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            info = {}
            lines = result.stderr.split('\n')

            for line in lines:
                if 'Duration:' in line:
                    duration_part = line.split('Duration:')[
                        1].split(',')[0].strip()
                    info['duration'] = duration_part
                elif 'Stream #' in line and 'Video:' in line:
                    if 'x' in line:
                        parts = line.split('x')
                        if len(parts) >= 2:
                            try:
                                width = int(parts[0].split()[-1])
                                height = int(parts[1].split()[0])
                                info['resolution'] = f"{width}x{height}"
                            except:
                                pass

            return info

        except Exception as e:
            return {'error': f'Ошибка получения информации: {str(e)}'}

    def cleanup_temp_files(self, *file_paths):
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"Удален временный файл: {file_path}")
            except Exception as e:
                print(f"Ошибка удаления файла {file_path}: {e}")
