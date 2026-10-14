"""
Hash extraction from archive files (ZIP/RAR) and PDF documents
"""
import subprocess
import struct
from pathlib import Path
import logging
from core import utils

logger = logging.getLogger(__name__)


class ArchiveExtractor:
    """Extract hashes from ZIP, RAR archives and PDF documents"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def detect_archive_type(self, archive_path):
        """Detect archive type from extension"""
        archive_path = Path(archive_path)
        extension = archive_path.suffix.lower()
        
        type_map = {
            '.zip': 'zip',
            '.rar': 'rar',
            '.7z': '7z',
            '.pdf': 'pdf'
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
        elif archive_type == 'pdf':
            return self.extract_pdf_hash(archive_path)
        else:
            raise ValueError(f"Extraction not yet implemented for: {archive_type}")
    
    def extract_pdf_hash(self, archive_path):
        """Extract hash from a password-protected PDF file.
        
        Uses a built-in Python implementation that reads the PDF encryption
        dictionary and formats it as a hashcat-compatible $pdf$ hash.
        Falls back to pdf2john.py from John the Ripper tools if available.
        """
        unescaped_path = str(archive_path)
        
        try:
            file_path = Path(unescaped_path)
            if not file_path.exists():
                raise FileNotFoundError(f"PDF file not found: {unescaped_path}")
            if not file_path.is_file():
                raise ValueError(f"Path is not a file: {unescaped_path}")
            
            self.logger.info(f"[EXTRACTOR] Attempting built-in PDF hash extraction for: {unescaped_path}")
            
            # Try built-in extraction first
            try:
                pdf_hash = self._extract_pdf_hash_builtin(unescaped_path)
                if pdf_hash:
                    self.logger.info(f"[EXTRACTOR] Built-in PDF extraction succeeded")
                    return pdf_hash
            except Exception as e:
                self.logger.warning(f"[EXTRACTOR] Built-in PDF extraction failed: {e}, trying pdf2john...")
            
            # Fallback: try pdf2john.py via Python interpreter
            try:
                tool_path = utils.get_tool_path('pdf2john')
                if tool_path and tool_path.exists():
                    import sys
                    python_exe = sys.executable
                    self.logger.info(f"[EXTRACTOR] Running: {python_exe} {tool_path} {unescaped_path}")
                    result = subprocess.run(
                        [python_exe, str(tool_path), unescaped_path],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    if result.stdout and result.stdout.strip():
                        return result.stdout.strip()
                    if result.stderr:
                        self.logger.warning(f"[EXTRACTOR] pdf2john stderr: {result.stderr}")
            except Exception as e:
                self.logger.warning(f"[EXTRACTOR] pdf2john fallback failed: {e}")
            
            raise RuntimeError(
                "Could not extract hash from PDF. "
                "The file may not be password-protected or uses an unsupported encryption."
            )
            
        except subprocess.TimeoutExpired:
            raise TimeoutError("PDF hash extraction timed out (>30s)")
        except (FileNotFoundError, ValueError, RuntimeError):
            raise
        except Exception as e:
            self.logger.error(f"[EXTRACTOR] PDF extraction error: {e}", exc_info=True)
            raise
    
    def _extract_pdf_hash_builtin(self, pdf_path):
        """Pure-Python PDF hash extractor.
        
        Reads the PDF trailer and encryption dictionary to build a
        hashcat-compatible hash string in the format:
        $pdf$V*R*keylen*P*encrypt_meta*id_len*id*u_len*u_hash*o_len*o_hash
        """
        with open(pdf_path, 'rb') as f:
            data = f.read()
        
        # Verify this is a PDF
        if not data.startswith(b'%PDF'):
            raise ValueError("Not a valid PDF file")
        
        # Find the Encrypt dictionary reference
        encrypt_dict = data
        import re
        
        # Search for /Encrypt in trailer or cross-reference stream
        encrypt_match = re.search(rb'/Encrypt\s+(\d+)\s+(\d+)\s+R', data)
        if encrypt_match:
            obj_id = encrypt_match.group(1)
            obj_gen = encrypt_match.group(2)
            # Find the object: obj_id obj_gen obj ... endobj
            obj_pattern = re.compile(rb'\b' + obj_id + rb'\s+' + obj_gen + rb'\s+obj\b(.*?)\bendobj\b', re.DOTALL)
            obj_match = obj_pattern.search(data)
            if obj_match:
                encrypt_dict = obj_match.group(1)
        else:
            # Check for inline encrypt dictionary
            encrypt_match = re.search(rb'/Encrypt\s*<<', data)
            if encrypt_match:
                # Grab a 1000-byte window to avoid complex << >> parsing.
                # This ensures we get the full dictionary without cutting off 
                # strings that end near the dictionary's closing brackets.
                start_idx = encrypt_match.start()
                encrypt_dict = data[start_idx:start_idx + 1000]
            else:
                raise ValueError("PDF is not password-protected (no /Encrypt entry found)")
        
        # Extract encryption parameters from the encryption dictionary
        # V (algorithm version)
        v_match = re.search(rb'/V\s+(\d+)', encrypt_dict)
        V = int(v_match.group(1)) if v_match else 1
        
        # R (revision)
        r_match = re.search(rb'/R\s+(\d+)', encrypt_dict)
        R = int(r_match.group(1)) if r_match else 2
        
        # Key length
        length_match = re.search(rb'/Length\s+(\d+)', encrypt_dict)
        key_length = int(length_match.group(1)) if length_match else 40
        # Length is in bits for the encryption key, convert to bytes
        if key_length > 16:  # If it looks like bits
            key_length_bytes = key_length // 8
        else:
            key_length_bytes = key_length
        
        # P (permissions)
        p_match = re.search(rb'/P\s+(-?\d+)', encrypt_dict)
        P = int(p_match.group(1)) if p_match else -1
        
        # EncryptMetadata (default is true/1)
        # However, for older PDFs (R=2), it's often effectively 0
        encrypt_meta = 1
        em_match = re.search(rb'/EncryptMetadata\s+(true|false)', encrypt_dict, re.IGNORECASE)
        if em_match and em_match.group(1).lower() == b'false':
            encrypt_meta = 0
        elif R == 2:
            # Hashcat example hashes for R=2 often use 0 for encrypt_meta if not specified
            encrypt_meta = 0
        
        # Document ID (from trailer)
        id_hex = ''
        id_match = re.search(rb'/ID\s*\[\s*<([0-9a-fA-F]+)>', data)
        if id_match:
            id_hex = id_match.group(1).decode('ascii').lower()
        else:
            # Try string-based ID
            id_match = re.search(rb'/ID\s*\[\s*\((.+?)\)', data, re.DOTALL)
            if id_match:
                id_hex = id_match.group(1).hex()
        
        if not id_hex:
            raise ValueError("Could not find document ID")
        
        id_len = len(id_hex) // 2
        
        # U string (user password hash)
        u_hex = self._extract_pdf_string(encrypt_dict, b'/U')
        if not u_hex:
            raise ValueError("Could not find /U (user password) entry")
        u_len = len(u_hex) // 2
        
        # O string (owner password hash)
        o_hex = self._extract_pdf_string(encrypt_dict, b'/O')
        if not o_hex:
            raise ValueError("Could not find /O (owner password) entry")
        o_len = len(o_hex) // 2
        
        # Build hashcat-compatible hash
        # Format: $pdf$V*R*keylen*P*encrypt_meta*id_len*id*u_len*u_hash*o_len*o_hash
        pdf_hash = f"$pdf${V}*{R}*{key_length}*{P}*{encrypt_meta}*{id_len}*{id_hex}*{u_len}*{u_hex}*{o_len}*{o_hex}"
        
        self.logger.info(f"[EXTRACTOR] Built PDF hash: V={V}, R={R}, KeyLen={key_length}, P={P}")
        self.logger.info(f"[EXTRACTOR] PDF hash length: {len(pdf_hash)}")
        
        return pdf_hash
    
    def _extract_pdf_string(self, data, key):
        """Extract a hex-encoded PDF string value for a given key (e.g. /U, /O).
        
        Handles both hex-encoded <...> and literal (...) string formats.
        """
        import re
        
        # Try hex string format: /Key <hex>
        pattern = re.escape(key) + rb'\s*<([0-9a-fA-F]+)>'
        match = re.search(pattern, data)
        if match:
            return match.group(1).decode('ascii').lower()
        
        # Try literal string format: /Key (...)
        # Need to handle escaped characters and nested parentheses
        pattern = re.escape(key) + rb'\s*\('
        match = re.search(pattern, data)
        if match:
            start = match.end()
            result = bytearray()
            i = start
            depth = 1
            while i < len(data) and depth > 0:
                byte = data[i]
                if byte == ord('('):
                    depth += 1
                    result.append(byte)
                elif byte == ord(')'):
                    depth -= 1
                    if depth > 0:
                        result.append(byte)
                elif byte == ord('\\'):
                    # Handle escape sequences
                    i += 1
                    if i < len(data):
                        escaped = data[i]
                        escape_map = {
                            ord('n'): ord('\n'), ord('r'): ord('\r'),
                            ord('t'): ord('\t'), ord('b'): ord('\b'),
                            ord('f'): ord('\f'),
                            ord('('): ord('('), ord(')'): ord(')'),
                            ord('\\'): ord('\\')
                        }
                        if escaped in escape_map:
                            result.append(escape_map[escaped])
                        elif ord('0') <= escaped <= ord('7'):
                            # Octal escape
                            octal = chr(escaped)
                            for _ in range(2):
                                if i + 1 < len(data) and ord('0') <= data[i + 1] <= ord('7'):
                                    i += 1
                                    octal += chr(data[i])
                                else:
                                    break
                            result.append(int(octal, 8))
                        else:
                            result.append(escaped)
                else:
                    result.append(byte)
                i += 1
            
            return bytes(result).hex()
        
        return None
    
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
