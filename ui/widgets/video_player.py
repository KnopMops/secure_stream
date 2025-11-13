import sys
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QSlider, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal, QEvent


class VideoPlayer(QWidget):
    fullscreen_requested = pyqtSignal()
    play_pause_requested = pyqtSignal()
    volume_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.parent = parent

        self.is_playing = False
        self.is_fullscreen = False

        self.volume = 50

        self.current_frame = None

        self.fullscreen_window = None
        self.fullscreen_label = None

        self.init_ui()
        self.setup_connections()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.video_container = QFrame()
        self.video_container.setFrameStyle(QFrame.Shape.Box)
        self.video_container.setLineWidth(2)
        self.video_container.setStyleSheet("""
            QFrame {
                background-color: #000000;
                border: 2px solid #333333;
                border-radius: 8px;
            }
        """)

        self.video_label = QLabel("Ожидание подключения...")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 14px;
                background-color: #000000;
                border: none;
            }
        """)
        self.video_label.setMinimumSize(320, 240)
        self.video_label.setScaledContents(True)

        video_layout = QVBoxLayout(self.video_container)
        video_layout.addWidget(self.video_label)

        self.control_panel = self.create_control_panel()

        layout.addWidget(self.video_container)
        layout.addWidget(self.control_panel)

        self.setLayout(layout)

    def create_control_panel(self):
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 4px;
            }
        """)
        panel.setMaximumHeight(60)

        layout = QHBoxLayout(panel)
        layout.setContentsMargins(8, 4, 8, 4)

        self.play_btn = QPushButton("▶️")
        self.play_btn.setFixedSize(32, 32)
        self.play_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                border: none;
                border-radius: 16px;
                font-size: 12px;
                color: white;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.play_btn.clicked.connect(self.toggle_play_pause)

        self.status_label = QLabel("Отключен")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 12px;
                background: transparent;
            }
        """)
        self.status_label.setMinimumWidth(100)

        volume_layout = QHBoxLayout()
        volume_layout.setSpacing(4)

        volume_icon = QLabel("🔊")
        volume_icon.setStyleSheet("color: #ffffff; font-size: 12px;")

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(self.volume)
        self.volume_slider.setMaximumWidth(100)
        self.volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #666666;
                height: 4px;
                background: #333333;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #4CAF50;
                border: 1px solid #4CAF50;
                width: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
            QSlider::handle:horizontal:hover {
                background: #45a049;
            }
        """)
        self.volume_slider.valueChanged.connect(self.on_volume_changed)

        volume_layout.addWidget(volume_icon)
        volume_layout.addWidget(self.volume_slider)

        self.fullscreen_btn = QPushButton("⛶")
        self.fullscreen_btn.setFixedSize(32, 32)
        self.fullscreen_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                border: none;
                border-radius: 16px;
                font-size: 12px;
                color: white;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
        """)
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)

        self.size_label = QLabel("320x240")
        self.size_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 10px;
                background: transparent;
            }
        """)
        self.size_label.setMinimumWidth(60)

        layout.addWidget(self.play_btn)
        layout.addWidget(self.status_label)
        layout.addStretch()
        layout.addLayout(volume_layout)
        layout.addWidget(self.fullscreen_btn)
        layout.addWidget(self.size_label)

        return panel

    def setup_connections(self):
        pass

    def display_frame(self, pixmap):
        if pixmap and not pixmap.isNull():
            self.current_frame = pixmap
            self.video_label.setPixmap(pixmap)

            if self.is_fullscreen and self.fullscreen_window and self.fullscreen_label:
                self.fullscreen_label.setPixmap(pixmap)

            size = pixmap.size()
            self.size_label.setText(f"{size.width()}x{size.height()}")

            if not self.is_playing:
                self.set_playing_status(True)

    def set_playing_status(self, playing):
        self.is_playing = playing

        if playing:
            self.play_btn.setText("⏸️")
            self.status_label.setText("Подключен")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #4CAF50;
                    font-size: 12px;
                    background: transparent;
                }
            """)
        else:
            self.play_btn.setText("▶️")
            self.status_label.setText("Пауза")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #FF9800;
                    font-size: 12px;
                    background: transparent;
                }
            """)

    def set_connection_status(self, connected):
        if connected:
            self.status_label.setText("Подключен")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #4CAF50;
                    font-size: 12px;
                    background: transparent;
                }
            """)
        else:
            self.status_label.setText("Отключен")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #f44336;
                    font-size: 12px;
                    background: transparent;
                }
            """)
            self.play_btn.setText("▶️")
            self.is_playing = False

    def toggle_play_pause(self):
        self.is_playing = not self.is_playing
        self.set_playing_status(self.is_playing)
        self.play_pause_requested.emit()

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen

        if self.is_fullscreen:
            self.fullscreen_btn.setText("⛶")
            self.enter_fullscreen()
        else:
            self.fullscreen_btn.setText("⛶")
            self.exit_fullscreen()

    def enter_fullscreen(self):
        from PyQt6.QtWidgets import QWidget, QVBoxLayout

        self.fullscreen_window = QWidget()
        self.fullscreen_window.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.fullscreen_window.setStyleSheet("background-color: #000000;")

        fullscreen_layout = QVBoxLayout(self.fullscreen_window)
        fullscreen_layout.setContentsMargins(0, 0, 0, 0)

        fullscreen_label = QLabel(self.fullscreen_window)
        fullscreen_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fullscreen_label.setScaledContents(True)
        fullscreen_label.setStyleSheet("background-color: #000000;")

        if self.current_frame and not self.current_frame.isNull():
            fullscreen_label.setPixmap(self.current_frame)

        fullscreen_layout.addWidget(fullscreen_label)

        self.fullscreen_label = fullscreen_label

        self.fullscreen_window.installEventFilter(self)

        self.fullscreen_window.showFullScreen()
        self.fullscreen_requested.emit()

        self.control_panel.hide()

    def exit_fullscreen(self):
        if self.fullscreen_window:
            self.fullscreen_window.close()
            self.fullscreen_window = None
            self.fullscreen_label = None

        self.control_panel.show()

        if self.current_frame and not self.current_frame.isNull():
            self.video_label.setPixmap(self.current_frame)

    def on_volume_changed(self, value):
        self.volume = value
        self.volume_changed.emit(value)

    def get_volume(self):
        return self.volume

    def set_volume(self, volume):
        self.volume = max(0, min(100, volume))
        self.volume_slider.setValue(self.volume)

    def clear_display(self):
        self.video_label.setText("Ожидание подключения...")
        self.current_frame = None
        self.set_connection_status(False)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        if self.current_frame and not self.is_fullscreen:
            self.video_label.setPixmap(self.current_frame)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_F11:
            self.toggle_fullscreen()
        elif event.key() == Qt.Key.Key_Space:
            self.toggle_play_pause()
        elif event.key() == Qt.Key.Key_Escape and self.is_fullscreen:
            self.toggle_fullscreen()
        else:
            super().keyPressEvent(event)

    def eventFilter(self, obj, event):
        if obj == self.fullscreen_window and event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Escape or event.key() == Qt.Key.Key_F11:
                self.toggle_fullscreen()
                return True
        return super().eventFilter(obj, event)
