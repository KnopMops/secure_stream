STYLES = """
QMainWindow {
    background-color: #2b2b2b;
    color: #ffffff;
}

QWidget {
    background-color: #2b2b2b;
    color: #ffffff;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 12px;
}

QTabWidget::pane {
    border: 1px solid #444444;
    background-color: #353535;
    border-radius: 6px;
    margin-top: 2px;
}

QTabWidget::tab-bar {
    alignment: center;
}

QTabBar::tab {
    background-color: #3c3c3c;
    color: #cccccc;
    padding: 10px 20px;
    margin: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    border: 1px solid #444444;
    min-width: 120px;
}

QTabBar::tab:selected {
    background-color: #505050;
    color: #ffffff;
    border-bottom: 2px solid #4CAF50;
}

QTabBar::tab:hover {
    background-color: #484848;
}

QGroupBox {
    font-weight: bold;
    border: 2px solid #444444;
    border-radius: 8px;
    margin-top: 15px;
    padding-top: 20px;
    color: #eeeeee;
    font-size: 13px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 0 15px;
    background-color: #353535;
    border: 1px solid #444444;
    border-radius: 4px;
}

QPushButton {
    background-color: #4CAF50;
    color: white;
    border: none;
    padding: 10px 15px;
    border-radius: 6px;
    font-weight: bold;
    min-width: 120px;
    font-size: 12px;
}

QPushButton:hover {
    background-color: #45a049;
    border: 1px solid #5cb860;
}

QPushButton:pressed {
    background-color: #3d8b40;
}

QPushButton:disabled {
    background-color: #555555;
    color: #999999;
}

QPushButton[class="record"] {
    background-color: #f44336;
    font-size: 14px;
    padding: 12px 20px;
}

QPushButton[class="record"]:hover {
    background-color: #da190b;
}

QPushButton[class="stop"] {
    background-color: #ff9800;
}

QPushButton[class="stop"]:hover {
    background-color: #e68900;
}

QComboBox {
    background-color: #353535;
    color: #ffffff;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 8px;
    min-width: 150px;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 25px;
    border-left-width: 1px;
    border-left-color: #555555;
    border-left-style: solid;
    border-top-right-radius: 4px;
    border-bottom-right-radius: 4px;
}

QComboBox QAbstractItemView {
    background-color: #353535;
    color: #ffffff;
    border: 1px solid #555555;
    selection-background-color: #4CAF50;
}

QSpinBox {
    background-color: #353535;
    color: #ffffff;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 8px;
    min-width: 80px;
}

QSpinBox::up-button, QSpinBox::down-button {
    background-color: #444444;
    border: 1px solid #555555;
    width: 20px;
}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background-color: #4CAF50;
}

QTextEdit {
    background-color: #353535;
    color: #ffffff;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 8px;
    font-family: 'Consolas', 'Monaco', monospace;
}

QLineEdit {
    background-color: #353535;
    color: #ffffff;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 8px;
}

QLineEdit:focus {
    border: 1px solid #4CAF50;
}

QListWidget {
    background-color: #353535;
    color: #ffffff;
    border: 1px solid #555555;
    border-radius: 4px;
    padding: 4px;
}

QListWidget::item {
    padding: 8px;
    border-bottom: 1px solid #444444;
}

QListWidget::item:selected {
    background-color: #4CAF50;
    color: white;
    border-radius: 3px;
}

QLabel {
    color: #ffffff;
    padding: 4px;
}

QLabel[class="title"] {
    font-size: 14px;
    font-weight: bold;
    color: #4CAF50;
}

QLabel[class="status"] {
    font-weight: bold;
    padding: 6px 12px;
    border-radius: 4px;
}

QLabel[class="status-active"] {
    background-color: #4CAF50;
    color: white;
}

QLabel[class="status-inactive"] {
    background-color: #f44336;
    color: white;
}

QSplitter::handle {
    background-color: #444444;
    width: 2px;
}

QSplitter::handle:hover {
    background-color: #4CAF50;
}

QScrollBar:vertical {
    border: none;
    background-color: #353535;
    width: 12px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #4CAF50;
    min-height: 20px;
    border-radius: 6px;
}

QScrollBar:horizontal {
    border: none;
    background-color: #353535;
    height: 12px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background-color: #4CAF50;
    min-width: 20px;
    border-radius: 6px;
}

QFrame[class="separator"] {
    background-color: #444444;
    max-height: 1px;
    min-height: 1px;
}

QCheckBox {
    color: #ffffff;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
}

QCheckBox::indicator:unchecked {
    border: 1px solid #555555;
    background-color: #353535;
    border-radius: 3px;
}

QCheckBox::indicator:checked {
    border: 1px solid #4CAF50;
    background-color: #4CAF50;
    border-radius: 3px;
}

QProgressBar {
    border: 1px solid #444444;
    border-radius: 4px;
    background-color: #353535;
    text-align: center;
    color: white;
}

QProgressBar::chunk {
    background-color: #4CAF50;
    border-radius: 3px;
}

/* Специальные стили для настроек */
SettingsTab {
    background-color: #2b2b2b;
}

QTabWidget QWidget {
    background-color: #2b2b2b;
}
"""
