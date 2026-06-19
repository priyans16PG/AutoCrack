"""
Hashcat cracking engine
"""
import subprocess
import threading
import logging
from pathlib import Path
from queue import Queue
from core import utils, parser

logger = logging.getLogger(__name__)


class CrackerState:
    """Represents the state of a cracking session"""
    IDLE = 'idle'
    RUNNING = 'running'
    PAUSED = 'paused'
    STOPPED = 'stopped'
    COMPLETED = 'completed'
    ERROR = 'error'


class Cracker:
    """Hashcat cracking engine"""
    
    def __init__(self, hash_file, hash_mode, attack_mode='3'):
        self.hash_file = str(hash_file)
        self.hash_mode = hash_mode
        self.attack_mode = attack_mode
        self.state = CrackerState.IDLE
        self.process = None
        self.output_queue = Queue()
        self.parser = parser.HashcatOutputParser()
        self.logger = logging.getLogger(__name__)
        self.session_name = None
    
    def generate_mask_sequence(self, mask, min_len, max_len):
        """Generate mask sequence for incremental attack"""
        masks = []
        for length in range(min_len, max_len + 1):
            masks.append(mask[:length])
        return masks
    
    def build_command(self, mask=None, wordlist=None, increment=False, 
                      device_id=1, rules=None, hybrid=False):
        """Build hashcat command line"""
        try:
            hashcat_path = utils.ensure_tool_exists('hashcat')
        except FileNotFoundError:
            raise FileNotFoundError("Hashcat not found in tools/hashcat/ directory")
        
        cmd = [str(hashcat_path)]
        
        # Basic options
        cmd.extend(['-m', str(self.hash_mode)])
        cmd.extend(['-a', str(self.attack_mode)])
        # Skip device validation with --force to avoid GPU/OpenCL errors
        cmd.append('--force')
        cmd.append('-O')  # Optimization for fast hashing
        
        # Hash file - DO NOT use escape_path here.
        # subprocess.Popen with a list of args handles spaces in paths
        # automatically. Wrapping in quotes causes hashcat to see literal
        # quote characters as part of the filename -> "Separator unmatched".
        cmd.append(self.hash_file)
        
        # Attack-specific options
        if self.attack_mode == '3':  # Brute force with mask
            if increment:
                cmd.append('--increment')
            if mask:
                cmd.append(mask)
                self.logger.info(f"[CRACKER] Mask attack with: {mask}")
        
        elif self.attack_mode == '0':  # Dictionary
            if wordlist:
                cmd.append(str(wordlist))
        
        elif self.attack_mode == '1':  # Combination
            if wordlist:
                cmd.append(str(wordlist))
                cmd.append(str(wordlist))
        
        elif self.attack_mode == '6':  # Hybrid (dict + mask)
            if wordlist:
                cmd.append(str(wordlist))
            if mask:
                cmd.append(mask)
        
        elif self.attack_mode == '7':  # Hybrid (mask + dict)
            if mask:
                cmd.append(mask)
            if wordlist:
                cmd.append(str(wordlist))
        
        # Rules
        if rules:
            cmd.extend(['-r', str(rules)])
        
        # Session management for resume capability
        if self.session_name:
            cmd.extend(['--session', self.session_name])
            cmd.append('--restore')
        
        # Output options
        cmd.extend(['--outfile-format', '2,3'])  # Hash:Password format
        
        self.logger.info(f"Hashcat command: {' '.join(cmd)}")
        return cmd
    
    def start_attack(self, mask=None, wordlist=None, increment=False, 
                     device_id=1, rules=None, hybrid=False):
        """Start cracking attack"""
        if self.state == CrackerState.RUNNING:
            raise RuntimeError("Attack already running")
        
        self.state = CrackerState.RUNNING
        cmd = self.build_command(
            mask=mask,
            wordlist=wordlist,
            increment=increment,
            device_id=device_id,
            rules=rules,
            hybrid=hybrid
        )
        
        try:
            # Get hashcat directory to use as working directory
            from pathlib import Path
            hashcat_path = utils.ensure_tool_exists('hashcat')
            hashcat_dir = Path(hashcat_path).parent
            
            # Remove potfile before new attack to get fresh results
            potfile_path = hashcat_dir / 'hashcat.potfile'
            if potfile_path.exists():
                try:
                    potfile_path.unlink()
                    self.logger.info("[CRACKER] Cleared potfile for fresh attack")
                except Exception as e:
                    self.logger.warning(f"[CRACKER] Could not clear potfile: {e}")
            
            self.logger.info(f"[CRACKER] Running from directory: {hashcat_dir}")
            
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                cwd=str(hashcat_dir)  # Set working directory
            )
            
            # Start thread to read output
            read_thread = threading.Thread(target=self._read_output, daemon=True)
            read_thread.start()
            
            self.logger.info("Attack started")
            return True
            
        except Exception as e:
            self.state = CrackerState.ERROR
            self.logger.error(f"Failed to start attack: {e}")
            raise
    
    def _read_output(self):
        """Read output from hashcat process"""
        if not self.process:
            self.logger.error("[CRACKER] No process to read from")
            return
        
        try:
            self.logger.info("[CRACKER] Starting output reading thread")
            while self.state in (CrackerState.RUNNING, CrackerState.PAUSED):
                line = self.process.stdout.readline()
                if not line:
                    self.logger.info("[CRACKER] No more output from process")
                    # Also read any remaining stderr
                    remaining_err = self.process.stderr.read()
                    if remaining_err:
                        self.logger.error(f"[CRACKER] Remaining stderr: {remaining_err}")
                    break
                
                self.logger.info(f"[CRACKER] Line: {line[:100]}")
                self.output_queue.put(('stdout', line.strip()))
                
                # Check for password found
                if ':' in line and not line.startswith('Session'):
                    pwd = self.parser.parse_hash_found(line)
                    if pwd:
                        self.output_queue.put(('password', pwd))
            
            # Wait for process to complete
            if self.process.poll() is None:
                self.process.wait()
            
            # Read remaining output
            remaining = self.process.stdout.read()
            if remaining:
                for line in remaining.split('\n'):
                    if line.strip():
                        self.output_queue.put(('stdout', line.strip()))
            
            # Read stderr for errors
            errors = self.process.stderr.read()
            if errors:
                for line in errors.split('\n'):
                    if line.strip():
                        self.output_queue.put(('stderr', line.strip()))
            
            # Determine final state
            if self.state == CrackerState.RUNNING:
                if self.process.returncode == 0:
                    self.state = CrackerState.COMPLETED
                    # After successful completion, try to show results from potfile
                    self.logger.info("[CRACKER] Attack completed, checking for results...")
                    self.show_results()
                else:
                    self.state = CrackerState.ERROR
            
            self.logger.info(f"Process completed with return code: {self.process.returncode}")
            
        except Exception as e:
            self.logger.error(f"Error reading output: {e}")
            self.state = CrackerState.ERROR
    
    def pause(self):
        """Pause attack"""
        if self.state != CrackerState.RUNNING:
            return False
        
        try:
            self.state = CrackerState.PAUSED
            self.logger.info("Attack paused")
            return True
        except Exception as e:
            self.logger.error(f"Failed to pause: {e}")
            return False
    
    def resume(self):
        """Resume attack"""
        if self.state != CrackerState.PAUSED:
            return False
        
        self.state = CrackerState.RUNNING
        self.logger.info("Attack resumed")
        return True
    
    def stop(self):
        """Stop attack"""
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            except Exception as e:
                self.logger.error(f"Error stopping process: {e}")
        
        self.state = CrackerState.STOPPED
        self.logger.info("Attack stopped")
    
    def get_output(self):
        """Get queued output (non-blocking)"""
        output = []
        while not self.output_queue.empty():
            try:
                output.append(self.output_queue.get_nowait())
            except:
                break
        return output
    
    def get_state(self):
        """Get current state"""
        return self.state
    
    def is_running(self):
        """Check if attack is running"""
        if self.state != CrackerState.RUNNING:
            return False
        
        # Also check if process is actually running
        if self.process and self.process.poll() is not None:
            # Process has finished
            self.logger.info(f"[CRACKER] Process finished with return code: {self.process.returncode}")
            if self.process.returncode == 0:
                self.state = CrackerState.COMPLETED
            else:
                self.state = CrackerState.ERROR
            return False
        
        return True
    
    def is_completed(self):
        """Check if attack is completed"""
        return self.state in (CrackerState.COMPLETED, CrackerState.ERROR)
    
    def show_results(self):
        """Display recovered passwords using --show flag"""
        try:
            from pathlib import Path
            hashcat_path = utils.ensure_tool_exists('hashcat')
            hashcat_dir = Path(hashcat_path).parent
            
            # Build --show command to display results from potfile
            cmd = [str(hashcat_path), '--show', str(self.hash_file)]
            
            self.logger.info(f"[CRACKER] Running --show to display results...")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(hashcat_dir),
                timeout=10
            )
            
            if result.stdout:
                self.logger.info(f"[CRACKER] Results from --show:\n{result.stdout}")
                # Parse each result line
                for line in result.stdout.strip().split('\n'):
                    if line and ':' in line:
                        pwd = self.parser.parse_hash_found(line)
                        if pwd:
                            self.output_queue.put(('password', pwd))
                            self.logger.info(f"[CRACKER] Recovered password: {pwd}")
            
            if result.stderr:
                self.logger.error(f"[CRACKER] --show stderr: {result.stderr}")
                
        except Exception as e:
            self.logger.error(f"[CRACKER] Error showing results: {e}")
