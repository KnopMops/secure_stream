import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Optional


class DatabaseManager:
    def __init__(self, db_path: str = "database/securestream.db"):
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recording_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_type TEXT NOT NULL,
                start_time DATETIME NOT NULL,
                end_time DATETIME,
                file_path TEXT,
                duration INTEGER,
                file_size INTEGER,
                settings_json TEXT,
                status TEXT DEFAULT 'completed'
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS screenshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER,
                resolution TEXT,
                quality TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                message TEXT NOT NULL,
                message_type TEXT DEFAULT 'text',
                timestamp DATETIME NOT NULL,
                ip_address TEXT,
                session_id INTEGER,
                FOREIGN KEY (session_id) REFERENCES recording_sessions (id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                log_level TEXT NOT NULL,
                module TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                additional_data TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_settings (
                category TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                description TEXT,
                last_modified DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(category, key)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS media_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE NOT NULL,
                file_type TEXT NOT NULL,
                created_at DATETIME NOT NULL,
                file_size INTEGER,
                duration INTEGER,
                resolution TEXT,
                format TEXT,
                quality TEXT,
                additional_metadata TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audio_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE NOT NULL,
                session_id INTEGER,
                created_at DATETIME NOT NULL,
                file_size INTEGER,
                duration INTEGER,
                sample_rate INTEGER,
                channels INTEGER,
                format TEXT,
                device_name TEXT,
                additional_metadata TEXT,
                FOREIGN KEY (session_id) REFERENCES recording_sessions (id)
            )
        ''')

        conn.commit()
        conn.close()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def start_recording_session(self, session_type: str, settings: Dict) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO recording_sessions 
            (session_type, start_time, settings_json, status)
            VALUES (?, ?, ?, ?)
        ''', (session_type, datetime.now(), json.dumps(settings), 'recording'))

        session_id = cursor.lastrowid
        conn.commit()
        conn.close()

        self._log_system_event(
            'INFO', 'database', f'Started {session_type} session: {session_id}')
        return session_id

    def stop_recording_session(self, session_id: int, file_path: str,
                               duration: int, file_size: int):
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE recording_sessions 
            SET end_time = ?, file_path = ?, duration = ?, file_size = ?, status = 'completed'
            WHERE id = ?
        ''', (datetime.now(), file_path, duration, file_size, session_id))

        conn.commit()
        conn.close()

        self._log_system_event(
            'INFO', 'database', f'Stopped recording session: {session_id}')

    def get_recording_sessions(self, limit: int = 100) -> List[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM recording_sessions 
            ORDER BY start_time DESC 
            LIMIT ?
        ''', (limit,))

        sessions = []
        for row in cursor.fetchall():
            sessions.append({
                'id': row[0],
                'session_type': row[1],
                'start_time': row[2],
                'end_time': row[3],
                'file_path': row[4],
                'duration': row[5],
                'file_size': row[6],
                'settings': json.loads(row[7]) if row[7] else {},
                'status': row[8]
            })

        conn.close()
        return sessions

    def save_screenshot_metadata(self, file_path: str, resolution: str,
                                 quality: str, file_size: int):
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO screenshots 
            (timestamp, file_path, file_size, resolution, quality)
            VALUES (?, ?, ?, ?, ?)
        ''', (datetime.now(), file_path, file_size, resolution, quality))

        conn.commit()
        conn.close()

        self._log_system_event(
            'INFO', 'database', f'Saved screenshot metadata: {file_path}')

    def get_screenshots(self, limit: int = 50) -> List[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM screenshots 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))

        screenshots = []
        for row in cursor.fetchall():
            screenshots.append({
                'id': row[0],
                'timestamp': row[1],
                'file_path': row[2],
                'file_size': row[3],
                'resolution': row[4],
                'quality': row[5],
                'created_at': row[6]
            })

        conn.close()
        return screenshots

    def save_chat_message(self, username: str, message: str,
                          message_type: str = 'text', ip_address: str = None,
                          session_id: int = None):
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO chat_messages 
            (username, message, message_type, timestamp, ip_address, session_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, message, message_type, datetime.now(), ip_address, session_id))

        conn.commit()
        conn.close()

    def get_chat_history(self, limit: int = 200) -> List[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM chat_messages 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))

        messages = []
        for row in cursor.fetchall():
            messages.append({
                'id': row[0],
                'username': row[1],
                'message': row[2],
                'message_type': row[3],
                'timestamp': row[4],
                'ip_address': row[5],
                'session_id': row[6]
            })

        conn.close()
        return list(reversed(messages))

    def get_chat_messages_after_id(self, last_id: int) -> List[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM chat_messages 
            WHERE id > ?
            ORDER BY timestamp ASC
        ''', (last_id,))

        messages = []
        for row in cursor.fetchall():
            messages.append({
                'id': row[0],
                'username': row[1],
                'message': row[2],
                'message_type': row[3],
                'timestamp': row[4],
                'ip_address': row[5],
                'session_id': row[6]
            })

        conn.close()
        return messages

    def get_setting(self, category: str, key: str, default: str = None) -> str:
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT value FROM app_settings 
            WHERE category = ? AND key = ?
        ''', (category, key))

        result = cursor.fetchone()
        conn.close()

        return result[0] if result else default

    def set_setting(self, category: str, key: str, value: str, description: str = None):
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO app_settings 
            (category, key, value, description, last_modified)
            VALUES (?, ?, ?, ?, ?)
        ''', (category, key, value, description, datetime.now()))

        conn.commit()
        conn.close()

    def get_all_settings(self) -> Dict[str, Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            'SELECT category, key, value, description FROM app_settings')

        settings = {}
        for row in cursor.fetchall():
            category, key, value, description = row
            if category not in settings:
                settings[category] = {}
            settings[category][key] = {
                'value': value,
                'description': description
            }

        conn.close()
        return settings

    def _log_system_event(self, level: str, module: str, message: str,
                          additional_data: Dict = None):
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO system_logs 
            (log_level, module, message, additional_data)
            VALUES (?, ?, ?, ?)
        ''', (level, module, message,
              json.dumps(additional_data) if additional_data else None))

        conn.commit()
        conn.close()

    def get_system_logs(self, level: str = None, module: str = None,
                        limit: int = 100) -> List[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()

        query = 'SELECT * FROM system_logs WHERE 1=1'
        params = []

        if level:
            query += ' AND log_level = ?'
            params.append(level)

        if module:
            query += ' AND module = ?'
            params.append(module)

        query += ' ORDER BY timestamp DESC LIMIT ?'
        params.append(limit)

        cursor.execute(query, params)

        logs = []
        for row in cursor.fetchall():
            logs.append({
                'id': row[0],
                'level': row[1],
                'module': row[2],
                'message': row[3],
                'timestamp': row[4],
                'additional_data': json.loads(row[5]) if row[5] else {}
            })

        conn.close()
        return logs

    def save_media_metadata(self, file_path: str, file_type: str,
                            file_size: int, resolution: str = None,
                            duration: int = None, format: str = None,
                            quality: str = None, additional_metadata: Dict = None):
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO media_metadata 
            (file_path, file_type, created_at, file_size, duration, resolution, format, quality, additional_metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (file_path, file_type, datetime.now(), file_size, duration,
              resolution, format, quality,
              json.dumps(additional_metadata) if additional_metadata else None))

        conn.commit()
        conn.close()

    def get_media_files(self, file_type: str = None, limit: int = 100) -> List[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()

        query = 'SELECT * FROM media_metadata WHERE 1=1'
        params = []

        if file_type:
            query += ' AND file_type = ?'
            params.append(file_type)

        query += ' ORDER BY created_at DESC LIMIT ?'
        params.append(limit)

        cursor.execute(query, params)

        media_files = []
        for row in cursor.fetchall():
            media_files.append({
                'id': row[0],
                'file_path': row[1],
                'file_type': row[2],
                'created_at': row[3],
                'file_size': row[4],
                'duration': row[5],
                'resolution': row[6],
                'format': row[7],
                'quality': row[8],
                'additional_metadata': json.loads(row[9]) if row[9] else {}
            })

        conn.close()
        return media_files

    def get_statistics(self) -> Dict:
        conn = self._get_connection()
        cursor = conn.cursor()

        stats = {}

        cursor.execute(
            'SELECT COUNT(*), SUM(duration), SUM(file_size) FROM recording_sessions')
        sessions_count, total_duration, total_size = cursor.fetchone()
        stats['sessions'] = {
            'count': sessions_count or 0,
            'total_duration': total_duration or 0,
            'total_size': total_size or 0
        }

        cursor.execute('SELECT COUNT(*), SUM(file_size) FROM screenshots')
        screenshots_count, screenshots_size = cursor.fetchone()
        stats['screenshots'] = {
            'count': screenshots_count or 0,
            'total_size': screenshots_size or 0
        }

        cursor.execute('SELECT COUNT(*) FROM chat_messages')
        messages_count = cursor.fetchone()[0]
        stats['chat_messages'] = messages_count or 0

        conn.close()
        return stats

    def cleanup_old_data(self, days_old: int = 30):
        conn = self._get_connection()
        cursor = conn.cursor()

        cutoff_date = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
        cutoff_datetime = datetime.fromtimestamp(cutoff_date)

        cursor.execute(
            'DELETE FROM system_logs WHERE timestamp < ?', (cutoff_datetime,))

        cursor.execute(
            'DELETE FROM chat_messages WHERE timestamp < ?', (cutoff_datetime,))

        conn.commit()
        conn.close()

        self._log_system_event(
            'INFO', 'database', f'Cleaned up data older than {days_old} days')

    def save_audio_metadata(self, file_path: str, session_id: int = None,
                            file_size: int = None, duration: int = None,
                            sample_rate: int = None, channels: int = None,
                            format: str = None, device_name: str = None,
                            additional_metadata: Dict = None):
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO audio_metadata 
            (file_path, session_id, created_at, file_size, duration, sample_rate, 
             channels, format, device_name, additional_metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (file_path, session_id, datetime.now(), file_size, duration,
              sample_rate, channels, format, device_name,
              json.dumps(additional_metadata) if additional_metadata else None))

        conn.commit()
        conn.close()

        self._log_system_event(
            'INFO', 'database', f'Saved audio metadata: {file_path}')

    def get_audio_files(self, session_id: int = None, limit: int = 100) -> List[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()

        query = 'SELECT * FROM audio_metadata WHERE 1=1'
        params = []

        if session_id:
            query += ' AND session_id = ?'
            params.append(session_id)

        query += ' ORDER BY created_at DESC LIMIT ?'
        params.append(limit)

        cursor.execute(query, params)

        audio_files = []
        for row in cursor.fetchall():
            audio_files.append({
                'id': row[0],
                'file_path': row[1],
                'session_id': row[2],
                'created_at': row[3],
                'file_size': row[4],
                'duration': row[5],
                'sample_rate': row[6],
                'channels': row[7],
                'format': row[8],
                'device_name': row[9],
                'additional_metadata': json.loads(row[10]) if row[10] else {}
            })

        conn.close()
        return audio_files

    def get_audio_statistics(self) -> Dict:
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT COUNT(*), SUM(file_size), SUM(duration), AVG(sample_rate)
            FROM audio_metadata
        ''')

        count, total_size, total_duration, avg_sample_rate = cursor.fetchone()

        stats = {
            'count': count or 0,
            'total_size': total_size or 0,
            'total_duration': total_duration or 0,
            'avg_sample_rate': avg_sample_rate or 0
        }

        conn.close()
        return stats
