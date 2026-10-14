"""
Utility functions for AutoCrack
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def get_app_path():
    """Get the absolute path to the app directory"""
    return Path(__file__).parent.parent


def get_tool_path(tool_name):
    """Get the path to a specific tool executable"""
    app_path = get_app_path()
    tool_paths = {
        'zip2john': app_path / 'tools' / 'john' / 'run' / 'zip2john.exe',
        'rar2john': app_path / 'tools' / 'john' / 'run' / 'rar2john.exe',
        'pdf2john': app_path / 'tools' / 'john' / 'run' / 'pdf2john.py',
        'john': app_path / 'tools' / 'john' / 'run' / 'john.exe',
        'hashcat': app_path / 'tools' / 'hashcat' / 'hashcat.exe'
    }
    return tool_paths.get(tool_name)


def ensure_tool_exists(tool_name):
    """Check if a tool exists, raise error if not"""
    tool_path = get_tool_path(tool_name)
    if not tool_path or not tool_path.exists():
        raise FileNotFoundError(f"Tool not found: {tool_name} at {tool_path}")
    return tool_path


def get_temp_path():
    """Get the temp directory path"""
    temp_dir = get_app_path() / 'temp'
    temp_dir.mkdir(exist_ok=True)
    return temp_dir


def get_hash_path(filename=None):
    """Get hash storage directory"""
    hash_dir = get_app_path() / 'hashes'
    hash_dir.mkdir(exist_ok=True)
    if filename:
        return hash_dir / filename
    return hash_dir


def get_session_path(session_name=None):
    """Get session storage directory"""
    session_dir = get_app_path() / 'sessions'
    session_dir.mkdir(exist_ok=True)
    if session_name:
        return session_dir / f"{session_name}.json"
    return session_dir


def sanitize_filename(filename):
    """Remove invalid characters from filename"""
    invalid_chars = '<>:"|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def escape_path(path):
    """Escape path for command line (Windows)"""
    if ' ' in str(path):
        return f'"{path}"'
    return str(path)


def validate_archive_path(archive_path):
    """Validate that archive file exists and has valid extension"""
    archive_path = Path(archive_path)
    
    if not archive_path.exists():
        raise FileNotFoundError(f"Archive file not found: {archive_path}")
    
    valid_extensions = {'.zip', '.rar', '.7z', '.pdf'}
    if archive_path.suffix.lower() not in valid_extensions:
        raise ValueError(f"Unsupported archive format: {archive_path.suffix}")
    
    return archive_path


def get_archive_metadata(archive_path):
    """Get archive file metadata"""
    archive_path = Path(archive_path)
    return {
        'path': str(archive_path),
        'name': archive_path.name,
        'extension': archive_path.suffix.lower(),
        'size': archive_path.stat().st_size,
        'created': datetime.fromtimestamp(archive_path.stat().st_ctime).isoformat(),
        'modified': datetime.fromtimestamp(archive_path.stat().st_mtime).isoformat()
    }


def load_json(filepath):
    """Load JSON file"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to load JSON from {filepath}: {e}")
        return None


def save_json(data, filepath):
    """Save data as JSON"""
    try:
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        logging.info(f"Saved JSON to {filepath}")
        return True
    except Exception as e:
        logging.error(f"Failed to save JSON to {filepath}: {e}")
        return False


def format_bytes(bytes_value):
    """Convert bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_value < 1024:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024
    return f"{bytes_value:.2f} TB"


def format_time(seconds):
    """Convert seconds to human-readable time format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def parse_speed(speed_str):
    """Parse speed string like '1.5G/s' to number"""
    try:
        speed_str = speed_str.strip().upper()
        multipliers = {'B': 1, 'K': 1e3, 'M': 1e6, 'G': 1e9, 'T': 1e12}
        
        for unit, multiplier in multipliers.items():
            if unit in speed_str:
                num = float(speed_str.replace(unit, '').replace('/S', '').strip())
                return num * multiplier
        return float(speed_str)
    except:
        return 0


def get_logger(name):
    """Get a logger instance"""
    return logging.getLogger(name)


def clean_temp_files(pattern='*'):
    """Clean temporary files"""
    temp_dir = get_temp_path()
    try:
        for file in temp_dir.glob(pattern):
            if file.is_file():
                file.unlink()
                logging.info(f"Deleted temp file: {file}")
    except Exception as e:
        logging.error(f"Failed to clean temp files: {e}")
