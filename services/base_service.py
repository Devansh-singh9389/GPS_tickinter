import subprocess
import shlex

class BaseService:
    def __init__(self):
        self.current_process = None

    def run_command(self, cmd, cwd=None, env=None, log_queue=None) -> int:
        if log_queue: log_queue("muted", "$ " + " ".join(shlex.quote(str(p)) for p in cmd))
        try:
            self.current_process = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, env=env)
            for line in self.current_process.stdout:
                if log_queue: log_queue("info", line.rstrip())
            return self.current_process.wait()
        except OSError as exc:
            if log_queue: log_queue("error", f"Process start failed: {exc}")
            return 127
        finally:
            self.current_process = None

    def stop_process(self):
        if self.current_process and self.current_process.poll() is None:
            self.current_process.terminate()