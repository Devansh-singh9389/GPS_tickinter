from pathlib import Path
from services.base_service import BaseService

class GeneratorService(BaseService):
    def generate(self, cmd, output_file, log_q, done_q):
        output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        code = self.run_command(cmd, cwd=output_file.parent, log_queue=log_q)
        if code == 0 and output_file.exists():
            done_q(True, str(output_file))
        else:
            done_q(False, "Simulation process failed or stopped.")