from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QGroupBox, QLabel, QComboBox, QMessageBox,
                             QProgressBar, QFrame, QCheckBox)
from PyQt6.QtCore import QTimer, pyqtSlot


class CameraTab(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.recording_time = 0
        self.init_ui()
        self.setup_timers()
        self.refresh_camera_list()

    def init_ui(self):
        layout = QVBoxLayout()

        control_group = QGroupBox("Управление записью с веб-камеры")
        control_layout = QVBoxLayout()

        button_layout = QHBoxLayout()
        self.record_btn = QPushButton("🎬 Начать запись с камеры")
        self.record_btn.setProperty("class", "record")
        self.record_btn.clicked.connect(self.toggle_camera_recording)

        button_layout.addWidget(self.record_btn)
        control_layout.addLayout(button_layout)

        self.recording_progress = QProgressBar()
        self.recording_progress.setVisible(False)
        self.recording_progress.setFormat("Запись: %v сек")
        control_layout.addWidget(self.recording_progress)

        control_group.setLayout(control_layout)

        camera_group = QGroupBox("Выбор камеры")
        camera_layout = QVBoxLayout()

        camera_select_layout = QHBoxLayout()
        camera_select_layout.addWidget(QLabel("Доступные камеры:"))
        self.camera_combo = QComboBox()
        camera_select_layout.addWidget(self.camera_combo)

        refresh_btn = QPushButton("🔄 Обновить список")
        refresh_btn.clicked.connect(self.refresh_camera_list)
        camera_select_layout.addWidget(refresh_btn)

        camera_layout.addLayout(camera_select_layout)
        camera_group.setLayout(camera_layout)

        settings_group = QGroupBox("Настройки записи")
        settings_layout = QVBoxLayout()

        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("Качество записи:"))
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["Высокое", "Среднее", "Низкое"])
        quality_layout.addWidget(self.quality_combo)
        quality_layout.addStretch()

        audio_layout = QHBoxLayout()
        self.audio_checkbox = QCheckBox("Записывать аудио")
        self.audio_checkbox.stateChanged.connect(self.on_audio_toggled)
        audio_layout.addWidget(self.audio_checkbox)
        audio_layout.addStretch()

        audio_device_layout = QHBoxLayout()
        audio_device_layout.addWidget(QLabel("Аудио устройство:"))
        self.audio_device_combo = QComboBox()
        self.audio_device_combo.setEnabled(False)
        audio_device_layout.addWidget(self.audio_device_combo)
        audio_device_layout.addStretch()

        merge_layout = QHBoxLayout()
        self.merge_checkbox = QCheckBox("Склеивать видео и аудио в MP4")
        self.merge_checkbox.setChecked(True)
        merge_layout.addWidget(self.merge_checkbox)
        merge_layout.addStretch()

        settings_layout.addLayout(quality_layout)
        settings_layout.addLayout(audio_layout)
        settings_layout.addLayout(audio_device_layout)
        settings_layout.addLayout(merge_layout)
        settings_group.setLayout(settings_layout)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)

        info_group = QGroupBox("Информация")
        info_layout = QVBoxLayout()
        self.info_label = QLabel("Выберите камеру для начала записи")
        self.info_label.setWordWrap(True)
        info_layout.addWidget(self.info_label)
        info_group.setLayout(info_layout)

        layout.addWidget(control_group)
        layout.addWidget(camera_group)
        layout.addWidget(settings_group)
        layout.addWidget(separator)
        layout.addWidget(info_group)
        layout.addStretch()

        self.setLayout(layout)
        self.load_audio_devices()

    def setup_timers(self):
        self.recording_timer = QTimer()
        self.recording_timer.timeout.connect(self.update_recording_time)

    def load_audio_devices(self):
        try:
            devices = self.parent.camera_recorder.get_available_audio_devices()
            self.audio_device_combo.clear()

            for device in devices:
                self.audio_device_combo.addItem(
                    f"{device['name']} ({device['sample_rate']} Hz)",
                    device['index']
                )
        except Exception as e:
            print(f"Ошибка загрузки аудио устройств: {e}")
            self.audio_device_combo.addItem("Микрофон по умолчанию", 0)

    def on_audio_toggled(self, state):
        enabled = state == 2
        self.audio_device_combo.setEnabled(enabled)

        if enabled and self.audio_device_combo.count() == 0:
            self.load_audio_devices()

    @pyqtSlot()
    def update_recording_time(self):
        if self.parent.camera_recorder.recording:
            self.recording_time += 1
            self.recording_progress.setValue(self.recording_time)

    def refresh_camera_list(self):
        self.camera_combo.clear()
        cameras = self.parent.camera_recorder.get_available_cameras()

        if cameras:
            for camera in cameras:
                self.camera_combo.addItem(
                    f"{camera['name']} ({camera['resolution']})",
                    camera['index']
                )
            self.info_label.setText(f"Найдено {len(cameras)} камер(ы)")
        else:
            self.camera_combo.addItem("Камеры не найдены", -1)
            self.info_label.setText(
                "Камеры не обнаружены. Проверьте подключение.")

    def toggle_camera_recording(self):
        if not self.parent.camera_recorder.recording:
            camera_index = self.camera_combo.currentData()
            if camera_index == -1:
                QMessageBox.warning(
                    self, "Ошибка", "Не выбрана доступная камера!")
                return

            path = self.parent.settings_tab.camera_path_label.text()
            if path == "Не выбрано":
                QMessageBox.warning(
                    self, "Ошибка", "Сначала выберите путь для сохранения в настройках!")
                return

            quality_map = {"Высокое": "high",
                           "Среднее": "medium", "Низкое": "low"}
            quality = quality_map[self.quality_combo.currentText()]

            audio_enabled = self.audio_checkbox.isChecked()
            audio_device = 0
            if audio_enabled and self.audio_device_combo.currentIndex() >= 0:
                audio_device = self.audio_device_combo.currentData()

            merge_enabled = self.merge_checkbox.isChecked()

            if self.parent.camera_recorder.start_recording(camera_index, path, quality, audio_enabled, audio_device, merge_enabled):
                self.record_btn.setText("⏹️ Остановить запись")
                self.record_btn.setProperty("class", "stop")
                self.recording_progress.setVisible(True)
                self.recording_time = 0
                self.recording_timer.start(1000)
                self.info_label.setText("Запись с камеры запущена...")

                self.parent.database.set_setting(
                    'camera', 'quality', self.quality_combo.currentText())

            else:
                QMessageBox.warning(
                    self, "Ошибка", "Не удалось начать запись с камеры!")
        else:
            if self.parent.camera_recorder.stop_recording():
                self.record_btn.setText("🎬 Начать запись с камеры")
                self.record_btn.setProperty("class", "record")
                self.recording_progress.setVisible(False)
                self.recording_timer.stop()
                self.info_label.setText(
                    f"Запись завершена. Длительность: {self.recording_time} сек")
            else:
                QMessageBox.warning(
                    self, "Ошибка", "Не удалось остановить запись!")
