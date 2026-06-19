from services.base_service import BaseService

class HackRFService(BaseService):
    def run_transfer(self, cmd, log_q, done_q):
        """Executes the dynamically built hackrf_transfer command."""
        code = self.run_command(cmd, log_queue=log_q)
        if code == 0:
            done_q(True, "HackRF transfer completed successfully.")
        else:
            done_q(False, "HackRF transfer stopped or encountered an error.")

    def check_hardware(self) -> bool:
            """Silently executes hackrf_info to check if a device is connected."""
            import subprocess
            try:
                # Run hackrf_info with a timeout so it never hangs indefinitely
                result = subprocess.run(
                    ["hackrf_info"], 
                    capture_output=True, 
                    text=True, 
                    timeout=1.5
                )
                # If the tool successfully executes and finds a device sequence
                if result.returncode == 0 and "Serial number" in result.stdout:
                    return True
                return False
            except Exception:
                return False