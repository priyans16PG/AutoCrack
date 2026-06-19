"""
Parse hashcat output and extract attack statistics
"""
import re
import logging

logger = logging.getLogger(__name__)


class HashcatOutputParser:
    """Parse hashcat progress and statistics"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def parse_speed(self, line):
        """Parse speed from various formats, preferring aggregate Speed.#*"""
        # Prioritize aggregate speed (Speed.#*) over individual device speeds
        # Pattern for aggregate: "Speed.#*.........:    28636 H/s"
        if 'Speed.#*' in line:
            match = re.search(r'Speed\.#\*[:\s]+([0-9.]+\s*[KMGTHZ]?/?s)', line, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Pattern for device speeds: "Speed.#01........:    25417 H/s"
        if 'Speed.#' in line:
            match = re.search(r'Speed[.\w#]*:\s+([0-9.]+\s*[KMGTHZ]?/?s)', line, re.IGNORECASE)
            if match:
                result = match.group(1).strip()
                # Skip if it's 0 H/s from individual devices
                if result != '0 H/s' and result != '0':
                    return result
        
        return None
    
    def parse_progress(self, line):
        """Parse progress from lines like 'Progress............: 123/1000 (12.30%)' or 'Restore_Point: 0 /1000000 (0.00%)'"""
        # Try different patterns
        patterns = [
            r'Progress[.\w]*:\s+(\d+)/(\d+)\s+\(([0-9.]+)%\)',  # "Progress: 123/1000 (12.30%)"
            r'Restore[._]?Point[:\s]+(\d+)\s+/\s*(\d+)\s+\(([0-9.]+)%\)',  # "Restore_Point: 0 /1000000 (0.00%)"
        ]
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                return {
                    'current': int(match.group(1)),
                    'total': int(match.group(2)),
                    'percentage': float(match.group(3))
                }
        return None
    
    def parse_eta(self, line):
        """Parse ETA from various time formats like 'Time.Estimated.: 1h 23m 45s' or 'Time.Estimated: 0 secs'"""
        # Look for time estimation patterns
        if 'Time' not in line and 'Estimated' not in line:
            return None
            
        eta_str = line
        # Extract time components
        hours = re.search(r'(\d+)\s*h(?:ours?)?', eta_str)
        minutes = re.search(r'(\d+)\s*m(?:inutes?)?', eta_str)
        seconds = re.search(r'(\d+)\s*s(?:ecs?)?', eta_str)
        
        total_seconds = 0
        if hours:
            total_seconds += int(hours.group(1)) * 3600
        if minutes:
            total_seconds += int(minutes.group(1)) * 60
        if seconds:
            total_seconds += int(seconds.group(1))
        
        return total_seconds if total_seconds > 0 else None
    
    def parse_temperature(self, line):
        """Parse GPU temperature from formats like 'Temp.GPU.#1: 65C' or 'Temp.GPU.#1.: 65'"""
        # Try different patterns
        patterns = [
            r'Temp[.\w#]*:\s+(\d+)\s*°?C',  # "Temp.GPU.#1: 65C"
            r'Temp[.\w#]*:\s+(\d+)',         # "Temp.GPU.#1: 65"
        ]
        for pattern in patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                return int(match.group(1))
        return None
    
    def parse_gpu_util(self, line):
        """Parse GPU utilization from formats like 'Util.GPU.#1.: 100%' or 'Util.GPU.#1: 99'"""
        # Try different patterns
        patterns = [
            r'Util[.\w#]*:\s+(\d+)\s*%',  # "Util.GPU.#1.: 100%"
            r'Util[.\w#]*:\s+(\d+)',      # "Util.GPU.#1: 99"
        ]
        for pattern in patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                return int(match.group(1))
        return None
    
    def parse_recovered(self, line):
        """Check if password was recovered"""
        if 'recovered' in line.lower() and '1' in line:
            return True
        return False
    
    def parse_candidate(self, line):
        """Parse candidate password from line like 'Candidate.password.: password123'"""
        # Look for the actual password in hashcat output
        match = re.search(r'Candidate[.\w]*:\s+(.+?)(?:\s|$)', line)
        if match:
            return match.group(1).strip()
        return None
    
    def parse_status_line(self, line):
        """Parse a status line from hashcat output"""
        data = {}
        
        if 'Speed' in line:
            speed = self.parse_speed(line)
            if speed:
                data['speed'] = speed
        
        if 'Progress' in line:
            progress = self.parse_progress(line)
            if progress:
                data['progress'] = progress
        
        if 'Time.Estimated' in line or 'Estimated' in line:
            eta = self.parse_eta(line)
            if eta:
                data['eta'] = eta
        
        if 'Temp' in line:
            temp = self.parse_temperature(line)
            if temp:
                data['temperature'] = temp
        
        if 'Util' in line:
            util = self.parse_gpu_util(line)
            if util:
                data['gpu_util'] = util
        
        if 'Recovered' in line:
            if self.parse_recovered(line):
                data['recovered'] = True
        
        return data if data else None
    
    def parse_hash_found(self, line):
        """Parse hash found line - STRICT format: hash:password
        Only matches actual cracking results, filters system messages"""
        
        # Lines that definitely don't contain password results
        system_keywords = [
            'Device #', 'GPU', 'MCU', 'MB', 'Platform', 'API', '====',
            'NVIDIA', 'Intel', 'https://', 'http://', 'faq', 'ftp',
            'Toolkit', 'CUDA', 'driver', 'runtime', 'For more', 'Session',
            'Falling back', 'Optimized kernel', 'kernel requested',
            'Initializing', 'Started', 'Stopped', 'recovered', 'Warning',
            'Minimum', 'Maximum', 'supported by kernel', 'Counted lines',
            'Parsed Hashes', 'Sorting', 'Removing duplicate', 'Compared',
            'INFO:', 'Please be patient', 'potfile', 'Kernel'
        ]
        
        # Reject lines with system keywords
        if any(x.lower() in line.lower() for x in system_keywords):
            return None
        
        # Must have exactly one colon (hash:password format)
        if line.count(':') != 1:
            return None
        
        # Split by colon
        parts = line.split(':')
        part0 = parts[0].strip()
        part1 = parts[1].strip()
        
        # Reject paths
        if '\\' in part0 or '/' in part0 or part0.startswith('C:'):
            return None
        if '\\' in part1 or '/' in part1 or part1.startswith('http'):
            return None
        
        # Both parts must not be empty
        if not part0 or not part1:
            return None
        
        # Parts shouldn't be too long
        if len(part0) > 100 or len(part1) > 100:
            return None
        
        # Determine which part is hash and which is password
        # Heuristic: shorter numeric parts (4-8 chars) are more likely passwords
        # Longer parts are more likely hashes
        part0_is_likely_password = (len(part0) < len(part1)) and part0.isdigit()
        part1_is_likely_password = (len(part1) < len(part0)) and part1.isdigit()
        
        if part0_is_likely_password:
            # part0 is password (shorter side)
            password = part0
            hash_part = part1
        elif part1_is_likely_password:
            # part1 is password (but this case suggests backwards output, still valid)
            password = part1
            hash_part = part0
        else:
            # Default: assume hash:password format
            hash_part = part0
            password = part1
        
        # Hash part validation
        if not (re.match(r'^[a-f0-9$]+$', hash_part, re.IGNORECASE) or '$' in hash_part or hash_part.isdigit()):
            return None
        
        # Valid password found!
        self.logger.info(f"[PARSER] Found password: {password}")
        return password
    
    def parse_output(self, output_text):
        """Parse complete hashcat output and extract relevant data"""
        lines = output_text.split('\n')
        data = {
            'speed': None,
            'progress': None,
            'eta': None,
            'temperature': None,
            'gpu_util': None,
            'recovered': False,
            'password': None
        }
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for recovered password
            if ':' in line and '$' not in line:
                pwd = self.parse_hash_found(line)
                if pwd:
                    data['password'] = pwd
            
            # Parse status line
            parsed = self.parse_status_line(line)
            if parsed:
                data.update(parsed)
        
        return data
    
    def parse_single_status_update(self, line):
        """Parse a single status line efficiently"""
        update = {}
        
        # Check line for different data points
        if 'Speed' in line:
            match = re.search(r'(\d+\.?\d*\s*[KMGT]?/s)', line)
            if match:
                update['speed'] = match.group(1)
        
        if 'Progress' in line:
            match = re.search(r'(\d+)/(\d+)\s+\(([0-9.]+)%\)', line)
            if match:
                update['progress'] = {
                    'current': int(match.group(1)),
                    'total': int(match.group(2)),
                    'percentage': float(match.group(3))
                }
        
        return update if update else None
