import subprocess
import re
import threading
from services.base_service import BaseService

class GeneratorService(BaseService):
    def __init__(self):
        super().__init__()
        self._stop_event = threading.Event()
        self.process = None

    def stop_process(self):
        """Sets the stop event and terminates the running generation process."""
        self._stop_event.set()
        if self.process:
            try:
                self.process.terminate()
            except Exception:
                pass

    def generate(self, cmd, out_target, duration_sec, log_q, done_q, prog_q):
        """Runs the generator and reads raw unbuffered binary to catch live progress."""
        self._stop_event.clear()
        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=0
            )
            
            # FIXED: Added =? to the regex to catch "Time into run = 123.4" safely!
            prog_re = re.compile(r"Time into run\s*=?\s*([\d\.]+)")
            buffer = ""
            
            while True:
                if self._stop_event.is_set():
                    break
                
                char_b = self.process.stdout.read(1)
                
                if not char_b and self.process.poll() is not None:
                    if buffer.strip():
                        log_q("info", buffer.strip())
                    break
                
                try:
                    char = char_b.decode('utf-8', errors='ignore')
                except Exception:
                    continue
                    
                if char == '\r' or char == '\n':
                    clean_line = buffer.strip()
                    buffer = "" 
                    if not clean_line: continue
                    
                    match = prog_re.search(clean_line)
                    if match:
                        current_time = float(match.group(1))
                        progress = current_time / duration_sec
                        prog_q(min(progress, 1.0)) # Sends percentage to the UI bar
                    else:
                        log_q("info", clean_line) 
                else:
                    buffer += char

            self.process.wait()
            
            if self._stop_event.is_set():
                done_q(False, "Generation stopped by user.")
            elif self.process.returncode == 0:
                done_q(True, out_target)
            else:
                done_q(False, f"Process failed with code {self.process.returncode}")
                
        except Exception as e:
            done_q(False, str(e))