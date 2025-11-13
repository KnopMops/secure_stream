import json
import os

from typing import Dict, Any


class Config:
    def __init__(self, config_file: str = 'config.json'):
        self.config_file = config_file

        self.default_config = {
            'application': {
                'name': 'SecureStream',
                'version': '1.0.0',
                'auto_start': False,
                'minimize_to_tray': True
            },
            'paths': {
                'recording': 'recordings',
                'screenshots': 'screenshots',
                'logs': 'logs',
                'database': 'database'
            },
            'recording': {
                'screen_quality': 'high',
                'camera_quality': 'medium',
                'default_fps': 30,
                'auto_save': True
            },
            'network': {
                'remote_access_port': 8080,
                'chat_port': 8081,
                'max_clients': 5,
                'timeout': 30
            },
            'ui': {
                'theme': 'dark',
                'language': 'ru',
                'font_size': 12
            }
        }

        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)

            except Exception as e:
                print(f'Ошибка загрузки конфигурации: {e}')
                return self.default_config.copy()

        return self.default_config.copy()

    def save_config(self):
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)

            return True

        except Exception as e:
            print(f"Ошибка сохранения конфигурации: {e}")
            return False

    def get(self, section: str, key: str, default: Any = None) -> Any:
        return self.config.get(section, {}).get(key, default)

    def set(self, section: str, key: str, value: Any):
        if section not in self.config:
            self.config[section] = {}

        self.config[section][key] = value
        self.save_config()

    def get_section(self, section: str) -> Dict[str, Any]:
        return self.config.get(section, {})

    def update_section(self, section: str, values: Dict[str, Any]):
        self.config[section] = values
        self.save_config()
