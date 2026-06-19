from services.base_service import BaseService

class HackRFService(BaseService):
    def transmit(self, bin_file, freq, sr, tx, if_gain, log_q, done_q):
        cmd = [
            "hackrf_transfer", 
            "-t", str(bin_file), 
            "-f", str(freq), 
            "-s", str(sr), 
            "-x", str(tx), 
            "-a", "1", 
            "-l", "8", 
            "-g", str(if_gain)
        ]
        code = self.run_command(cmd, log_queue=log_q)
        if code == 0:
            done_q(True, "Transmission completed.")
        else:
            done_q(False, "Transmission stopped or failed.")

    def run_transfer(self, cmd, log_q, done_q):
        """Executes the dynamically built hackrf_transfer command."""
        code = self.run_command(cmd, log_queue=log_q)
        if code == 0:
            done_q(True, "HackRF transfer completed successfully.")
        else:
            done_q(False, "HackRF transfer stopped or encountered an error.")

    