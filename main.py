import os
import sys

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QDir

from ui.main_window import MainWindow
import styles


def setup_directories():
    directories = [
        'recordings/screen',
        'recordings/camera',
        'screenshots',
        'logs',
        'database'
    ]

    for directory in directories:
        QDir().mkpath(directory)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


def main():
    setup_directories()

    app = QApplication(sys.argv)
    app.setApplicationName("SecureStream")
    app.setApplicationVersion("1.0.0")

    app.setStyleSheet(styles.STYLES)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
