"""
Session management and persistence
"""
import json
import logging
from pathlib import Path
from datetime import datetime
from core import utils

logger = logging.getLogger(__name__)


class CrackingSession:
    """Represents a cracking session"""
    
    def __init__(self, session_id=None):
        self.session_id = session_id or self._generate_id()
        self.archive_path = None
        self.hash_file = None
        self.hash_type = None
        self.hash_mode = None
        self.attack_mode = None
        self.mask = None
        self.wordlist = None
        self.increment = False
        self.device_id = 1
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.status = 'new'
        self.progress = 0
        self.speed = None
        self.eta = None
        self.password = None
        self.logger = logging.getLogger(__name__)
    
    def _generate_id(self):
        """Generate unique session ID"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        import random
        random_suffix = ''.join(random.choices('0123456789', k=6))
        return f"session_{timestamp}_{random_suffix}"
    
    def to_dict(self):
        """Convert session to dictionary"""
        return {
            'session_id': self.session_id,
            'archive_path': self.archive_path,
            'hash_file': self.hash_file,
            'hash_type': self.hash_type,
            'hash_mode': self.hash_mode,
            'attack_mode': self.attack_mode,
            'mask': self.mask,
            'wordlist': self.wordlist,
            'increment': self.increment,
            'device_id': self.device_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'status': self.status,
            'progress': self.progress,
            'speed': self.speed,
            'eta': self.eta,
            'password': self.password
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create session from dictionary"""
        session = cls(session_id=data.get('session_id'))
        session.archive_path = data.get('archive_path')
        session.hash_file = data.get('hash_file')
        session.hash_type = data.get('hash_type')
        session.hash_mode = data.get('hash_mode')
        session.attack_mode = data.get('attack_mode')
        session.mask = data.get('mask')
        session.wordlist = data.get('wordlist')
        session.increment = data.get('increment', False)
        session.device_id = data.get('device_id', 1)
        session.created_at = data.get('created_at')
        session.updated_at = data.get('updated_at')
        session.status = data.get('status', 'new')
        session.progress = data.get('progress', 0)
        session.speed = data.get('speed')
        session.eta = data.get('eta')
        session.password = data.get('password')
        return session
    
    def update(self, **kwargs):
        """Update session data"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now().isoformat()
    
    def save(self):
        """Save session to file"""
        try:
            session_file = utils.get_session_path(self.session_id)
            utils.save_json(self.to_dict(), session_file)
            self.logger.info(f"Session saved: {self.session_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save session: {e}")
            return False
    
    @classmethod
    def load(cls, session_id):
        """Load session from file"""
        try:
            session_file = utils.get_session_path(session_id)
            data = utils.load_json(session_file)
            if data:
                return cls.from_dict(data)
        except Exception as e:
            logger.error(f"Failed to load session: {e}")
        return None


class SessionManager:
    """Manage multiple sessions"""
    
    def __init__(self):
        self.sessions = {}
        self.current_session = None
        self.logger = logging.getLogger(__name__)
    
    def create_session(self, session_id=None):
        """Create new session"""
        session = CrackingSession(session_id=session_id)
        self.sessions[session.session_id] = session
        self.current_session = session
        self.logger.info(f"Created session: {session.session_id}")
        return session
    
    def load_session(self, session_id):
        """Load existing session"""
        session = CrackingSession.load(session_id)
        if session:
            self.sessions[session_id] = session
            self.current_session = session
            self.logger.info(f"Loaded session: {session_id}")
            return session
        return None
    
    def get_session(self, session_id=None):
        """Get session by ID or current session"""
        if session_id is None:
            return self.current_session
        return self.sessions.get(session_id)
    
    def list_sessions(self):
        """List all available sessions"""
        session_dir = utils.get_session_path()
        sessions = []
        try:
            for file in session_dir.glob('*.json'):
                data = utils.load_json(file)
                if data:
                    sessions.append(data)
        except Exception as e:
            self.logger.error(f"Failed to list sessions: {e}")
        return sessions
    
    def delete_session(self, session_id):
        """Delete session"""
        try:
            session_file = utils.get_session_path(session_id)
            if session_file.exists():
                session_file.unlink()
                if session_id in self.sessions:
                    del self.sessions[session_id]
                self.logger.info(f"Deleted session: {session_id}")
                return True
        except Exception as e:
            self.logger.error(f"Failed to delete session: {e}")
        return False
    
    def save_all(self):
        """Save all sessions"""
        for session in self.sessions.values():
            session.save()


# Global session manager instance
_session_manager = SessionManager()


def get_session_manager():
    """Get global session manager"""
    return _session_manager
