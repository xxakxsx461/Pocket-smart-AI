import json
import threading
from pathlib import Path
from typing import Optional, List, Dict, Any
from app.config import settings

class StorageService:
    def __init__(self, data_dir: Path = settings.DATA_DIR):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.users_file = self.data_dir / 'users.json'
        self.history_file = self.data_dir / 'history.json'
        self._lock = threading.Lock()
        
        self._init_file(self.users_file, [])
        self._init_file(self.history_file, [])

    def _init_file(self, filepath: Path, default_content: Any):
        if not filepath.exists():
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(default_content, f, indent=2)

    def _read_json(self, filepath: Path) -> List[Dict[str, Any]]:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []

    def _write_json(self, filepath: Path, data: Any):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # ------------------ User Operations ------------------
    def save_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            users = self._read_json(self.users_file)
            # Check existing
            for u in users:
                if u['username'].lower() == user_data['username'].lower():
                    raise ValueError('Username already exists')
                if u['email'].lower() == user_data['email'].lower():
                    raise ValueError('Email already exists')
            users.append(user_data)
            self._write_json(self.users_file, users)
            return user_data

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            users = self._read_json(self.users_file)
            for u in users:
                if u['username'].lower() == username.lower():
                    return u
            return None

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            users = self._read_json(self.users_file)
            for u in users:
                if u['email'].lower() == email.lower():
                    return u
            return None

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            users = self._read_json(self.users_file)
            for u in users:
                if u['id'] == user_id:
                    return u
            return None

    # ------------------ History & Plan Operations ------------------
    def save_history(self, history_data: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            history = self._read_json(self.history_file)
            history.insert(0, history_data)  # newest first
            self._write_json(self.history_file, history)
            return history_data

    def get_history(self, user_id: Optional[str] = None, planner_type: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._lock:
            history = self._read_json(self.history_file)
            filtered = history
            if user_id:
                filtered = [h for h in filtered if h.get('user_id') == user_id]
            if planner_type:
                filtered = [h for h in filtered if h.get('planner_type') == planner_type]
            return filtered

    def get_history_by_id(self, plan_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            history = self._read_json(self.history_file)
            for h in history:
                if h['id'] == plan_id:
                    return h
            return None

    def delete_history(self, plan_id: str, user_id: Optional[str] = None) -> bool:
        with self._lock:
            history = self._read_json(self.history_file)
            initial_len = len(history)
            if user_id:
                history = [h for h in history if not (h['id'] == plan_id and h.get('user_id') == user_id)]
            else:
                history = [h for h in history if h['id'] != plan_id]
            if len(history) < initial_len:
                self._write_json(self.history_file, history)
                return True
            return False

storage = StorageService()
