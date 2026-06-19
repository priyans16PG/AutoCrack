"""
Hash extraction from archive files (ZIP/RAR)
"""
import subprocess
from pathlib import Path
import logging
from core import utils

logger = logging.getLogger(__name__)


class ArchiveExtractor:
    """Extract hashes from ZIP and RAR archives"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def detect_archive_type(self, archive_path):
        """Detect archive type from extension"""
        archive_path = Path(archive_path)
        extension = archive_path.suffix.lower()
        
        type_map = {
            '.zip': 'zip',
            '.rar': 'rar',
            '.7z': '7z'
        }
        
        archive_type = type_map.get(extension)
        if not archive_type:
            raise ValueError(f"Unsupported archive format: {extension}")
        
        return archive_type
    
    def extract_zip_hash(self, archive_path):
        """Extract hash from ZIP file using zip2john"""
        unescaped_path = str(archive_path)
        
        try:
            # Pre-check: verify file exists and is readable
            file_path = Path(unescaped_path)
            if not file_path.exists():
                raise FileNotFoundError(f"Archive file not found: {unescaped_path}")
            if not file_path.is_file():
                raise ValueError(f"Path is not a file: {unescaped_path}")
            
            tool_path = utils.ensure_tool_exists('zip2john')
            self.logger.info(f"[EXTRACTOR] zip2john tool found at: {tool_path}")
            
            # IMPORTANT: Don't escape path for subprocess list args
            self.logger.info(f"[EXTRACTOR] Running: {tool_path} {unescaped_path}")
            result = subprocess.run(
                [str(tool_path), unescaped_path],  # Don't escape - subprocess handles list args
                capture_output=True,
                text=True,
                timeout=30
            )
            
            self.logger.info(f"[EXTRACTOR] zip2john return code: {result.returncode}")
            self.logger.info(f"[EXTRACTOR] zip2john stderr: {result.stderr}")
            
            if not result.stdout:
                if result.stderr:
                    error_msg = f"zip2john returned no hash. stderr: {result.stderr}"
                else:
                    error_msg = "zip2john returned empty output - file may not be password-protected or is not a valid ZIP archive"
                self.logger.error(f"[EXTRACTOR] {error_msg}")
                raise RuntimeError(error_msg)
            
            # Return the raw hash output
            return result.stdout.strip()
            
        except subprocess.TimeoutExpired:
            raise TimeoutError("zip2john extraction timed out (>30s)")
        except Exception as e:
            self.logger.error(f"[EXTRACTOR] ZIP extraction error: {e}", exc_info=True)
            raise
    
    def extract_rar_hash(self, archive_path):
        """Extract hash from RAR file using rar2john"""
        unescaped_path = str(archive_path)
        
        try:
            # Pre-check: verify file exists and is readable
            file_path = Path(unescaped_path)
            if not file_path.exists():
                raise FileNotFoundError(f"Archive file not found: {unescaped_path}")
            if not file_path.is_file():
                raise ValueError(f"Path is not a file: {unescaped_path}")
            file_size = file_path.stat().st_size
            self.logger.info(f"[EXTRACTOR] File exists: {unescaped_path}, Size: {file_size} bytes")
            
            tool_path = utils.ensure_tool_exists('rar2john')
            self.logger.info(f"[EXTRACTOR] rar2john tool found at: {tool_path}")
            
            # IMPORTANT: Don't escape path for subprocess list args - subprocess handles it
            # Only pass the raw path, subprocess.run with list args handles spaces correctly
            self.logger.info(f"[EXTRACTOR] Running: {tool_path} {unescaped_path}")
            result = subprocess.run(
                [str(tool_path), unescaped_path],  # Don't escape - subprocess handles list args
                capture_output=True,
                text=True,
                timeout=30
            )
            
            self.logger.info(f"[EXTRACTOR] rar2john return code: {result.returncode}")
            self.logger.info(f"[EXTRACTOR] rar2john stdout length: {len(result.stdout)}")
            self.logger.info(f"[EXTRACTOR] rar2john stderr: {result.stderr}")
            
            if not result.stdout:
                if result.stderr:
                    error_msg = f"rar2john returned no hash. stderr: {result.stderr}"
                else:
                    error_msg = "rar2john returned empty output - file may not be password-protected or is not a valid RAR archive"
                self.logger.error(f"[EXTRACTOR] {error_msg}")
                raise RuntimeError(error_msg)
            
            # Return the raw hash output
            output = result.stdout.strip()
            self.logger.info(f"[EXTRACTOR] Successfully extracted hash, length: {len(output)}")
            return output
            
        except subprocess.TimeoutExpired:
            raise TimeoutError("rar2john extraction timed out (>30s)")
        except Exception as e:
            self.logger.error(f"[EXTRACTOR] RAR extraction error: {e}", exc_info=True)
            raise
    
    def extract_hash(self, archive_path):
        """Extract hash from archive (auto-detect type)"""
        archive_path = utils.validate_archive_path(archive_path)
        archive_type = self.detect_archive_type(archive_path)
        
        self.logger.info(f"Extracting {archive_type.upper()} hash from: {archive_path}")
        
        if archive_type == 'zip':
            return self.extract_zip_hash(archive_path)
        elif archive_type == 'rar':
            return self.extract_rar_hash(archive_path)
        else:
            raise ValueError(f"Extraction not yet implemented for: {archive_type}")
    
    def extract_and_save(self, archive_path, output_file=None):
        """Extract hash and save to file"""
        if output_file is None:
            archive_path_obj = Path(archive_path)
            output_file = utils.get_hash_path(f"{archive_path_obj.stem}_raw.txt")
        else:
            output_file = Path(output_file)
        
        # Extract hash
        raw_hash = self.extract_hash(archive_path)
        
        # Debug logging
        self.logger.info(f"[EXTRACTOR] Raw hash length: {len(raw_hash)}")
        self.logger.info(f"[EXTRACTOR] First 50 chars: {raw_hash[:50]}")
        self.logger.info(f"[EXTRACTOR] Full hash:\n{raw_hash}")
        
        # Save to file
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(raw_hash)
        
        self.logger.info(f"Saved raw hash to: {output_file}")
        return str(output_file), raw_hash
