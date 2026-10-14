"""
Hash type detection and Hashcat mode mapping
"""
import re
import logging

logger = logging.getLogger(__name__)


class HashModeDetector:
    """Detect hash types and map to Hashcat modes"""
    
    # Hash type to Hashcat mode mapping
    HASH_MODE_MAP = {
        'rar5': 13000,      # RAR5
        'rar3': 13100,      # RAR3
        'pkzip2': 17200,    # ZIP2 (most common for modern ZIP)
        'zip': 17200,       # Standard ZIP
        'zip-encrypted': 23001,  # ZIP (with encryption)
        'pdf': 10500,       # PDF 1.4-1.6 (default, most common)
        'pdf14': 10500,     # PDF 1.4-1.6 (Acrobat 5-8), R=3
        'pdf11': 10400,     # PDF 1.1-1.3 (Acrobat 2-4), R=2
        'pdf17l3': 10600,   # PDF 1.7 Level 3 (Acrobat 9), R=5
        'pdf17l8': 10700,   # PDF 1.7 Level 8 (Acrobat 10+), R=6
        '7z': 11600,        # 7z
    }
    
    # Hash format patterns for detection
    HASH_PATTERNS = {
        'rar5': r'^\$rar5\$',
        'rar3': r'^\$rar3\$',
        'pkzip2': r'^\$pkzip2\$',
        'zip': r'^\$zip\$',
        'pdf': r'^\$pdf\$',
        '7z': r'^\$7z\$',
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def detect_hash_type(self, hash_string):
        """Detect hash type from hash string"""
        if not hash_string:
            raise ValueError("Empty hash string")
        
        hash_string = hash_string.strip()
        
        # Debug logging
        self.logger.info(f"[DETECTOR] Hash length: {len(hash_string)}")
        self.logger.info(f"[DETECTOR] First 50 chars: {hash_string[:50]}")
        self.logger.info(f"[DETECTOR] Last 50 chars: {hash_string[-50:]}")
        self.logger.info(f"[DETECTOR] Starts with $: {hash_string.startswith('$')}")
        
        # Check against patterns
        for hash_type, pattern in self.HASH_PATTERNS.items():
            if re.match(pattern, hash_string):
                self.logger.info(f"Detected hash type: {hash_type}")
                return hash_type
        
        # Try to extract hash type marker with $
        match = re.match(r'\$([a-z0-9]+)\$', hash_string)
        if match:
            detected_type = match.group(1)
            self.logger.warning(f"Unknown hash type marker: {detected_type}")
            return detected_type
        
        # Handle RAR3 and other formats (hex-only hashes)
        if re.match(r'^[a-f0-9]{20,}$', hash_string, re.IGNORECASE):
            # Likely RAR3 format
            self.logger.info("Detected RAR3 (hex format)")
            return 'rar3'
        
        # Additional debug - check character composition
        hex_chars = sum(1 for c in hash_string if c in '0123456789abcdefABCDEF')
        self.logger.error(f"[DETECTOR] Hash format not recognised!")
        self.logger.error(f"[DETECTOR] Hash length: {len(hash_string)}")
        self.logger.error(f"[DETECTOR] Hex characters: {hex_chars}/{len(hash_string)}")
        self.logger.error(f"[DETECTOR] Full hash: {hash_string}")
        
        raise ValueError(f"Cannot detect hash type from: {hash_string[:100]}")
    
    def get_hashcat_mode(self, hash_type):
        """Get Hashcat mode for hash type"""
        if hash_type not in self.HASH_MODE_MAP:
            raise ValueError(f"Unknown hash type: {hash_type}")
        
        mode = self.HASH_MODE_MAP[hash_type]
        self.logger.info(f"Hash type '{hash_type}' -> Hashcat mode {mode}")
        return mode
    
    def detect_and_get_mode(self, hash_string):
        """Detect hash type and return Hashcat mode"""
        hash_type = self.detect_hash_type(hash_string)
        
        # For PDF hashes, determine the exact sub-type from V/R values
        if hash_type == 'pdf' and hash_string.startswith('$pdf$'):
            hash_type = self._detect_pdf_subtype(hash_string)
        
        mode = self.get_hashcat_mode(hash_type)
        return hash_type, mode
    
    def _detect_pdf_subtype(self, hash_string):
        """Determine the PDF encryption sub-type from the hash.
        
        Hash format: $pdf$V*R*keylen*P*...
        Hashcat modes:
          10400 = PDF 1.1-1.3 (V=1, R=2)
          10500 = PDF 1.4-1.6 (V=2, R=3)
          10600 = PDF 1.7 Level 3 (V=5, R=5)
          10700 = PDF 1.7 Level 8 (V=5, R=6)
        """
        try:
            # Remove $pdf$ prefix and split by *
            parts = hash_string[5:].split('*')
            if len(parts) >= 2:
                V = int(parts[0])
                R = int(parts[1])
                
                self.logger.info(f"[DETECTOR] PDF V={V}, R={R}")
                
                if R == 6:
                    return 'pdf17l8'   # Mode 10700
                elif R == 5:
                    return 'pdf17l3'   # Mode 10600
                elif R == 2:
                    return 'pdf11'     # Mode 10400
                else:
                    return 'pdf14'     # Mode 10500 (R=3, most common)
        except (ValueError, IndexError) as e:
            self.logger.warning(f"[DETECTOR] Could not parse PDF V/R values: {e}")
        
        return 'pdf'  # Fallback to default PDF mode
    
    def get_mode_info(self, mode):
        """Get information about a Hashcat mode"""
        mode_info = {
            13000: {
                'name': 'RAR5',
                'description': 'RAR5 Compressed Archive',
                'type': 'rar',
                'benchmark': True
            },
            13100: {
                'name': 'RAR3',
                'description': 'RAR3 Compressed Archive',
                'type': 'rar',
                'benchmark': True
            },
            17200: {
                'name': 'ZIP2',
                'description': 'ZIP (Encrypted, PKWARE)',
                'type': 'zip',
                'benchmark': True
            },
            23001: {
                'name': 'ZIP (Encrypted)',
                'description': 'ZIP with Traditional Encryption',
                'type': 'zip',
                'benchmark': False
            },
            10500: {
                'name': 'PDF 1.4-1.6',
                'description': 'PDF (Acrobat 5-8)',
                'type': 'pdf',
                'benchmark': True
            },
            10400: {
                'name': 'PDF 1.1-1.3',
                'description': 'PDF (Acrobat 2-4)',
                'type': 'pdf',
                'benchmark': True
            },
            10600: {
                'name': 'PDF 1.7 L3',
                'description': 'PDF 1.7 Level 3 (Acrobat 9)',
                'type': 'pdf',
                'benchmark': True
            },
            10700: {
                'name': 'PDF 1.7 L8',
                'description': 'PDF 1.7 Level 8 (Acrobat 10+)',
                'type': 'pdf',
                'benchmark': True
            },
            11600: {
                'name': '7z',
                'description': '7z Archive',
                'type': '7z',
                'benchmark': True
            }
        }
        
        return mode_info.get(mode, {
            'name': f'Mode {mode}',
            'description': 'Unknown',
            'type': 'unknown',
            'benchmark': False
        })
    
    def list_supported_modes(self):
        """List all supported hash types and modes"""
        modes = []
        for hash_type, mode in self.HASH_MODE_MAP.items():
            info = self.get_mode_info(mode)
            modes.append({
                'hash_type': hash_type,
                'mode': mode,
                'name': info['name'],
                'description': info['description']
            })
        return modes
