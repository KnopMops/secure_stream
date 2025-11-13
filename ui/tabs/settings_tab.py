from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QGroupBox, QLabel, QFileDialog, QMessageBox,
                             QLineEdit, QCheckBox, QTabWidget, QTextEdit,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QComboBox)
from PyQt6.QtCore import QTimer
import os
from datetime import datetime


class SettingsTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        layout = QVBoxLayout()

        tabs = QTabWidget()

        paths_tab = QWidget()
        paths_layout = QVBoxLayout(paths_tab)
        paths_layout.addWidget(self.create_paths_group())
        paths_layout.addStretch()

        database_tab = QWidget()
        database_layout = QVBoxLayout(database_tab)
        database_layout.addWidget(self.create_database_group())
        database_layout.addStretch()

        system_tab = QWidget()
        system_layout = QVBoxLayout(system_tab)
        system_layout.addWidget(self.create_system_group())
        system_layout.addStretch()

        ffmpeg_tab = QWidget()
        ffmpeg_layout = QVBoxLayout(ffmpeg_tab)
        ffmpeg_layout.addWidget(self.create_ffmpeg_group())
        ffmpeg_layout.addStretch()

        tabs.addTab(paths_tab, "📁 Пути сохранения")
        tabs.addTab(database_tab, "🗃️ База данных")
        tabs.addTab(system_tab, "⚙️ Система")
        tabs.addTab(ffmpeg_tab, "🎬 FFmpeg")

        layout.addWidget(tabs)
        self.setLayout(layout)

    def create_paths_group(self):
        group = QGroupBox("Настройки путей сохранения")
        layout = QVBoxLayout()

        screen_path_layout = QHBoxLayout()
        screen_path_layout.addWidget(QLabel("Путь для записи экрана:"))
        self.screen_path_label = QLabel("Не выбрано")
        self.screen_path_label.setWordWrap(True)
        screen_path_layout.addWidget(self.screen_path_label, 1)

        screen_path_btn = QPushButton("📁 Выбрать")
        screen_path_btn.clicked.connect(self.select_screen_path)
        screen_path_layout.addWidget(screen_path_btn)

        camera_path_layout = QHBoxLayout()
        camera_path_layout.addWidget(QLabel("Путь для записи с камеры:"))
        self.camera_path_label = QLabel("Не выбрано")
        self.camera_path_label.setWordWrap(True)
        camera_path_layout.addWidget(self.camera_path_label, 1)

        camera_path_btn = QPushButton("📁 Выбрать")
        camera_path_btn.clicked.connect(self.select_camera_path)
        camera_path_layout.addWidget(camera_path_btn)

        screenshot_path_layout = QHBoxLayout()
        screenshot_path_layout.addWidget(QLabel("Путь для скриншотов:"))
        self.screenshot_path_label = QLabel("Не выбрано")
        self.screenshot_path_label.setWordWrap(True)
        screenshot_path_layout.addWidget(self.screenshot_path_label, 1)

        screenshot_path_btn = QPushButton("📁 Выбрать")
        screenshot_path_btn.clicked.connect(self.select_screenshot_path)
        screenshot_path_layout.addWidget(screenshot_path_btn)

        layout.addLayout(screen_path_layout)
        layout.addLayout(camera_path_layout)
        layout.addLayout(screenshot_path_layout)

        group.setLayout(layout)
        return group

    def create_database_group(self):
        group = QGroupBox("Управление базой данных")
        layout = QVBoxLayout()

        stats_layout = QVBoxLayout()
        self.stats_label = QLabel("Загрузка статистики...")
        self.stats_label.setWordWrap(True)
        stats_layout.addWidget(self.stats_label)

        buttons_layout = QHBoxLayout()

        refresh_btn = QPushButton("🔄 Обновить статистику")
        refresh_btn.clicked.connect(self.update_database_stats)

        cleanup_btn = QPushButton("🧹 Очистить старые данные")
        cleanup_btn.clicked.connect(self.cleanup_old_data)

        export_btn = QPushButton("📤 Экспорт логов")
        export_btn.clicked.connect(self.export_logs)

        buttons_layout.addWidget(refresh_btn)
        buttons_layout.addWidget(cleanup_btn)
        buttons_layout.addWidget(export_btn)

        cleanup_layout = QHBoxLayout()
        cleanup_layout.addWidget(QLabel("Очищать данные старше (дней):"))
        self.cleanup_days = QLineEdit("30")
        self.cleanup_days.setMaximumWidth(50)
        cleanup_layout.addWidget(self.cleanup_days)
        cleanup_layout.addStretch()

        layout.addLayout(stats_layout)
        layout.addLayout(buttons_layout)
        layout.addLayout(cleanup_layout)

        group.setLayout(layout)

        QTimer.singleShot(100, self.update_database_stats)

        return group

    def create_system_group(self):
        group = QGroupBox("Системные настройки")
        layout = QVBoxLayout()

        autostart_layout = QHBoxLayout()
        self.autostart_checkbox = QCheckBox(
            "Запускать приложение при старте системы")
        autostart_layout.addWidget(self.autostart_checkbox)
        autostart_layout.addStretch()

        tray_layout = QHBoxLayout()
        self.tray_checkbox = QCheckBox("Сворачивать в системный трей")
        tray_layout.addWidget(self.tray_checkbox)
        tray_layout.addStretch()

        logging_layout = QHBoxLayout()
        self.logging_checkbox = QCheckBox("Включить подробное логирование")
        logging_layout.addWidget(self.logging_checkbox)
        logging_layout.addStretch()

        save_layout = QHBoxLayout()
        save_btn = QPushButton("💾 Сохранить все настройки")
        save_btn.clicked.connect(self.save_settings)
        save_layout.addWidget(save_btn)

        layout.addLayout(autostart_layout)
        layout.addLayout(tray_layout)
        layout.addLayout(logging_layout)
        layout.addLayout(save_layout)

        group.setLayout(layout)
        return group

    def select_screen_path(self):
        path = QFileDialog.getExistingDirectory(
            self, "Выберите папку для сохранения записей экрана")
        if path:
            self.screen_path_label.setText(path)
            self.parent.database.set_setting('paths', 'screen', path)

    def select_camera_path(self):
        path = QFileDialog.getExistingDirectory(
            self, "Выберите папку для сохранения записей с камеры")
        if path:
            self.camera_path_label.setText(path)
            self.parent.database.set_setting('paths', 'camera', path)

    def select_screenshot_path(self):
        path = QFileDialog.getExistingDirectory(
            self, "Выберите папку для сохранения скриншотов")
        if path:
            self.screenshot_path_label.setText(path)
            self.parent.database.set_setting('paths', 'screenshots', path)

    def update_database_stats(self):
        stats = self.parent.database.get_statistics()

        stats_text = f"📊 Статистика базы данных:\n"
        stats_text += f"• Сессии записи: {stats['sessions']['count']}\n"
        stats_text += f"• Общее время записи: {stats['sessions']['total_duration']} сек\n"
        stats_text += f"• Общий размер записей: {self.format_size(stats['sessions']['total_size'])}\n"
        stats_text += f"• Скриншоты: {stats['screenshots']['count']}\n"
        stats_text += f"• Размер скриншотов: {self.format_size(stats['screenshots']['total_size'])}\n"
        stats_text += f"• Сообщения в чате: {stats['chat_messages']}"

        self.stats_label.setText(stats_text)

    def format_size(self, size_bytes):
        if size_bytes == 0:
            return "0 B"

        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1

        return f"{size_bytes:.1f} {size_names[i]}"

    def cleanup_old_data(self):
        try:
            days = int(self.cleanup_days.text())
            if days < 1:
                QMessageBox.warning(
                    self, "Ошибка", "Количество дней должно быть положительным числом!")
                return

            self.parent.database.cleanup_old_data(days)
            self.update_database_stats()
            QMessageBox.information(
                self, "Успех", f"Данные старше {days} дней успешно очищены!")

        except ValueError:
            QMessageBox.warning(
                self, "Ошибка", "Введите корректное число дней!")

    def export_logs(self):
        try:
            path, _ = QFileDialog.getSaveFileName(
                self, "Экспорт логов", "securestream_logs.txt", "Text Files (*.txt)")
            if path:
                logs = self.parent.database.get_system_logs(limit=1000)

                with open(path, 'w', encoding='utf-8') as f:
                    f.write("SecureStream - Логи системы\n")
                    f.write(f"Экспорт от: {datetime.now()}\n")
                    f.write("=" * 50 + "\n\n")

                    for log in reversed(logs):
                        f.write(
                            f"[{log['timestamp']}] {log['level']} - {log['module']}: {log['message']}\n")

                QMessageBox.information(
                    self, "Успех", f"Логи успешно экспортированы в: {path}")

        except Exception as e:
            QMessageBox.warning(
                self, "Ошибка", f"Не удалось экспортировать логи: {e}")

    def load_settings(self):
        screen_path = self.parent.database.get_setting('paths', 'screen', '')
        camera_path = self.parent.database.get_setting('paths', 'camera', '')
        screenshot_path = self.parent.database.get_setting(
            'paths', 'screenshots', '')

        self.screen_path_label.setText(
            screen_path if screen_path else "Не выбрано")
        self.camera_path_label.setText(
            camera_path if camera_path else "Не выбрано")
        self.screenshot_path_label.setText(
            screenshot_path if screenshot_path else "Не выбрано")

        autostart = self.parent.database.get_setting(
            'system', 'autostart', 'false')
        tray = self.parent.database.get_setting('system', 'tray', 'true')
        logging = self.parent.database.get_setting('system', 'logging', 'true')

        self.autostart_checkbox.setChecked(autostart.lower() == 'true')
        self.tray_checkbox.setChecked(tray.lower() == 'true')
        self.logging_checkbox.setChecked(logging.lower() == 'true')

    def save_settings(self):
        self.parent.database.set_setting('system', 'autostart',
                                         'true' if self.autostart_checkbox.isChecked() else 'false',
                                         'Автозапуск приложения')
        self.parent.database.set_setting('system', 'tray',
                                         'true' if self.tray_checkbox.isChecked() else 'false',
                                         'Сворачивание в трей')
        self.parent.database.set_setting('system', 'logging',
                                         'true' if self.logging_checkbox.isChecked() else 'false',
                                         'Подробное логирование')

        QMessageBox.information(self, "Успех", "Настройки успешно сохранены!")

    def create_ffmpeg_group(self):
        group = QGroupBox("Настройки FFmpeg")
        layout = QVBoxLayout()

        status_layout = QVBoxLayout()
        self.ffmpeg_status_label = QLabel("Проверка FFmpeg...")
        self.ffmpeg_status_label.setWordWrap(True)
        status_layout.addWidget(self.ffmpeg_status_label)

        buttons_layout = QHBoxLayout()

        refresh_btn = QPushButton("🔄 Проверить FFmpeg")
        refresh_btn.clicked.connect(self.check_ffmpeg_status)

        test_btn = QPushButton("🧪 Тест склеивания")
        test_btn.clicked.connect(self.test_ffmpeg_merge)

        buttons_layout.addWidget(refresh_btn)
        buttons_layout.addWidget(test_btn)

        merge_layout = QHBoxLayout()
        self.auto_merge_checkbox = QCheckBox(
            "Автоматически склеивать видео и аудио")
        self.auto_merge_checkbox.setChecked(True)
        merge_layout.addWidget(self.auto_merge_checkbox)
        merge_layout.addStretch()

        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("Качество склеивания:"))
        self.merge_quality_combo = QComboBox()
        self.merge_quality_combo.addItems(["Высокое", "Среднее", "Низкое"])
        self.merge_quality_combo.setCurrentText("Высокое")
        quality_layout.addWidget(self.merge_quality_combo)
        quality_layout.addStretch()

        layout.addLayout(status_layout)
        layout.addLayout(buttons_layout)
        layout.addLayout(merge_layout)
        layout.addLayout(quality_layout)

        group.setLayout(layout)

        QTimer.singleShot(100, self.check_ffmpeg_status)

        return group

    def check_ffmpeg_status(self):
        try:
            ffmpeg_info = self.parent.screen_recorder.get_ffmpeg_status()

            if ffmpeg_info['available']:
                status_text = f"✅ FFmpeg доступен\n"
                status_text += f"Путь: {ffmpeg_info['path']}\n"
                status_text += f"Версия: {ffmpeg_info['version']}"
            else:
                status_text = f"❌ FFmpeg недоступен\n"
                status_text += f"Ошибка: {ffmpeg_info['error']}\n\n"
                status_text += "Для установки FFmpeg:\n"
                status_text += "• Windows: скачайте с https://ffmpeg.org/\n"
                status_text += "• Linux: sudo apt install ffmpeg\n"
                status_text += "• macOS: brew install ffmpeg"

            self.ffmpeg_status_label.setText(status_text)

        except Exception as e:
            self.ffmpeg_status_label.setText(f"❌ Ошибка проверки FFmpeg: {e}")

    def test_ffmpeg_merge(self):
        try:
            from PyQt6.QtWidgets import QMessageBox

            test_video = "test_video.avi"
            test_audio = "test_audio.wav"

            with open(test_video, 'w') as f:
                f.write("")
            with open(test_audio, 'w') as f:
                f.write("")

            result = self.parent.screen_recorder.video_processor.merge_video_audio(
                test_video, test_audio, "test_output.mp4", "high"
            )

            import os
            for file in [test_video, test_audio, "test_output.mp4"]:
                if os.path.exists(file):
                    os.remove(file)

            if result['success']:
                QMessageBox.information(
                    self, "Успех", "FFmpeg работает корректно!")
            else:
                QMessageBox.warning(
                    self, "Ошибка", f"Ошибка FFmpeg: {result['error']}")

        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка тестирования: {e}")
