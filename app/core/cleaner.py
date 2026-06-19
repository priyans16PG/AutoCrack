"""
Hash cleaning and validation
"""
import re
import logging

logger = logging.getLogger(__name__)


class HashCleaner:
    """Clean and validate password hashes"""
    
    # Hash format patterns
    HASH_PATTERNS = {
        'rar5': r'^\$rar5\$.*',
        'rar3': r'^\$rar3\$.*',
        'pkzip': r'^\$pkzip2\$.*',
        'zip': r'^\$zip\$.*',
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def remove_filename_prefix(self, hash_string):
        """Remove filename prefix from hash (e.g., 'C:\\archive.rar:$rar5$...' -> '$rar5$...')"""
        # Look for the hash marker ($) and extract from there
        match = re.search(r'\$(rar[35]|pkzip|zip|pdf|7z)\$', hash_string)
        if match:
            return hash_string[match.start():].strip()
        
        # Fallback: if no $ found, try to find path:hash pattern
        # Find the last colon followed by alphanumeric (likely the hash start)
        match = re.search(r':([a-zA-Z0-9$].*?)$', hash_string)
        if match:
            return match.group(1).strip()
        
        return hash_string.strip()
    
    def clean_hash(self, raw_hash):
        """Clean raw hash output"""
        if not raw_hash:
            self.logger.error("[CLEANER] Raw hash is empty - archive may not be password-protected")
            raise ValueError("Empty hash input - the archive may not be password-protected or is not a valid archive format")
        
        # Split into lines and filter empty lines
        lines = [line.strip() for line in raw_hash.split('\n') if line.strip()]
        
        if not lines:
            self.logger.error("[CLEANER] No valid hash lines found after splitting")
            raise ValueError("No valid hash lines found")
        
        self.logger.info(f"[CLEANER] Processing {len(lines)} hash lines")
        
        # Process first line (usually the valid one)
        cleaned_hash = self.remove_filename_prefix(lines[0])
        
        if not cleaned_hash:
            self.logger.error("[CLEANER] Hash is empty after removing filename prefix")
            raise ValueError("Hash is empty after cleaning - extraction may have failed")
        
        self.logger.info(f"[CLEANER] Cleaned hash (first 100 chars): {cleaned_hash[:100]}...")
        return cleaned_hash
    
    def validate_hash_format(self, hash_string):
        """Validate hash format - more lenient for different RAR formats"""
        if not hash_string or not isinstance(hash_string, str):
            raise ValueError("Invalid hash format")
        
        # Hash should have at least some length (be more flexible)
        if len(hash_string) < 10:
            raise ValueError("Hash is too short")
        
        # Check for common hash markers ($ or hex characters for RAR3/older formats)
        if not (hash_string.startswith('$') or hash_string[0].isalnum()):
            raise ValueError("Hash format not recognized")
        
        return True
    
    def extract_hash_type(self, hash_string):
        """Extract hash type from hash string"""
        # Look for hash type indicator
        if hash_string.startswith('$rar5$'):
            return 'rar5'
        elif hash_string.startswith('$rar3$'):
            return 'rar3'
        elif hash_string.startswith('$pkzip2$'):
            return 'pkzip2'
        elif hash_string.startswith('$zip$'):
            return 'zip'
        else:
            # Try to extract from hash structure
            match = re.match(r'\$([a-z0-9]+)\$', hash_string)
            if match:
                return match.group(1)
            return 'unknown'
    
    def remove_duplicate_lines(self, text):
        """Remove duplicate lines, keep first occurrence"""
        lines = text.split('\n')
        seen = set()
        result = []
        
        for line in lines:
            line = line.strip()
            if line and line not in seen:
                seen.add(line)
                result.append(line)
        
        return '\n'.join(result)
    
    def clean_and_validate(self, raw_hash):
        """Complete cleaning and validation pipeline"""
        try:
            # Remove duplicates
            clean = self.remove_duplicate_lines(raw_hash)
            
            # Clean first line
            cleaned_hash = self.clean_hash(clean)
            
            # Debug logging before validation
            self.logger.info(f"[CLEANER] Cleaned hash length: {len(cleaned_hash)}")
            self.logger.info(f"[CLEANER] First 50 chars: {cleaned_hash[:50]}")
            self.logger.info(f"[CLEANER] Starts with $: {cleaned_hash.startswith('$')}")
            
            # Validate format
            self.validate_hash_format(cleaned_hash)
            
            self.logger.info(f"[CLEANER] Validation passed, returning hash")
            return cleaned_hash
            
        except Exception as e:
            self.logger.error(f"[CLEANER] Hash cleaning failed: {e}")
            raise


def clean_hash_file(input_file, output_file=None):
    """Clean a hash file"""
    with open(input_file, 'r') as f:
        raw_content = f.read()
    
    cleaner = HashCleaner()
    cleaned_hash = cleaner.clean_and_validate(raw_content)
    
    if output_file is None:
        output_file = str(input_file).replace('_raw.txt', '_clean.txt')
    
    with open(output_file, 'w') as f:
        f.write(cleaned_hash)
    
    logger.info(f"Cleaned hash saved to: {output_file}")
    return cleaned_hash, output_file
