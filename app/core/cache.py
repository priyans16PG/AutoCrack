"""
Cache management utilities
"""
import shutil
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """Manage application cache and temporary files"""
    
    def __init__(self):
        self.cache_dirs = [
            Path.home() / ".hashcat",  # Hashcat potfiles
            Path.cwd() / ".cache",      # Local cache
            Path.cwd() / "temp",        # Temp files
            Path.cwd() / "hashes",      # Hash files
        ]
    
    def get_cache_size(self):
        """Get total cache size in bytes"""
        total_size = 0
        for cache_dir in self.cache_dirs:
            if cache_dir.exists():
                try:
                    for filepath in cache_dir.rglob('*'):
                        if filepath.is_file():
                            total_size += filepath.stat().st_size
                except Exception as e:
                    logger.error(f"Error calculating cache size for {cache_dir}: {e}")
        return total_size
    
    def format_size(self, size_bytes):
        """Format bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    
    def get_cache_size_formatted(self):
        """Get formatted cache size"""
        size = self.get_cache_size()
        return self.format_size(size), size
    
    def clear_cache(self):
        """Clear all cache files"""
        cleared_size = 0
        cleared_count = 0
        errors = []
        
        for cache_dir in self.cache_dirs:
            if cache_dir.exists():
                try:
                    for filepath in cache_dir.rglob('*'):
                        if filepath.is_file():
                            try:
                                size = filepath.stat().st_size
                                filepath.unlink()
                                cleared_size += size
                                cleared_count += 1
                                logger.info(f"Deleted cache file: {filepath}")
                            except Exception as e:
                                errors.append(f"Failed to delete {filepath}: {e}")
                    
                    # Try to remove empty directories
                    try:
                        if not any(cache_dir.iterdir()):
                            cache_dir.rmdir()
                            logger.info(f"Removed empty cache directory: {cache_dir}")
                    except:
                        pass
                
                except Exception as e:
                    errors.append(f"Error clearing {cache_dir}: {e}")
                    logger.error(f"Error clearing cache directory {cache_dir}: {e}")
        
        return {
            'success': True,
            'cleared_size': cleared_size,
            'cleared_count': cleared_count,
            'cleared_size_formatted': self.format_size(cleared_size),
            'errors': errors
        }
    
    def cleanup_old_hashes(self):
        """Clean up old hash files (older than 7 days)"""
        import time
        now = time.time()
        week_ago = now - (7 * 24 * 60 * 60)
        
        hash_dir = Path.cwd() / "hashes"
        if not hash_dir.exists():
            return {'deleted': 0, 'size': 0}
        
        deleted_count = 0
        deleted_size = 0
        
        for hash_file in hash_dir.glob('*'):
            if hash_file.is_file():
                try:
                    if hash_file.stat().st_mtime < week_ago:
                        size = hash_file.stat().st_size
                        hash_file.unlink()
                        deleted_count += 1
                        deleted_size += size
                        logger.info(f"Deleted old hash file: {hash_file}")
                except Exception as e:
                    logger.error(f"Error deleting old hash file {hash_file}: {e}")
        
        return {'deleted': deleted_count, 'size': deleted_size, 'size_formatted': self.format_size(deleted_size)}
