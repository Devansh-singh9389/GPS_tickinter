import os, shutil, re
from pathlib import Path
from services.base_service import BaseService

class CompilerService(BaseService):
    def compile_sim(self, src_dir, output_dir, output_exe, motion, phase, sat, chan, opt, cflags, clean, b_mode, log_q, done_q):
        src_path = Path(src_dir)
        out_path = Path(output_dir)
        
        try:
            self._update_header(src_path, motion, phase, sat, chan)
            log_q("success", "Header updated.")
        except Exception as e:
            return done_q(False, str(e))

        exe_name = f"{output_exe}.exe" if os.name == "nt" and not output_exe.endswith(".exe") else output_exe
        final_dest = out_path / exe_name
        env = os.environ.copy()
        env["CFLAGS"] = f"-DUSER_MOTION_SIZE={motion} {opt} {cflags}"

        use_make = b_mode in ("auto", "force_make") and (src_path / "Makefile").exists()
        
        if use_make:
            if clean: self.run_command(["make", "clean"], cwd=src_path, env=env, log_queue=log_q)
            code = self.run_command(["make", f"CFLAGS={env['CFLAGS']}"], cwd=src_path, env=env, log_queue=log_q)
            built_exe = src_path / ("gps-sdr-sim.exe" if os.name == "nt" else "gps-sdr-sim")
        else:
            cmd = ["gcc", *env["CFLAGS"].split(), "-I", str(src_path), "-o", str(final_dest), str(src_path/"gpssim.c")]
            if os.name == "nt" and (src_path/"getopt.c").exists(): cmd.append(str(src_path/"getopt.c"))
            cmd.append("-lm")
            code = self.run_command(cmd, cwd=src_path, log_queue=log_q)
            built_exe = final_dest

        if code == 0 and built_exe.exists():
            if built_exe.resolve() != final_dest.resolve():
                shutil.copy2(built_exe, final_dest)
            done_q(True, str(final_dest))
        else:
            done_q(False, "Build failed.")

    def _update_header(self, src_dir: Path, motion: int, phase: bool, sat: int, chan: int):
        header = src_dir / "gpssim.h"
        if not header.exists(): raise FileNotFoundError("gpssim.h not found")
        
        lines = header.read_text(encoding="utf-8")
        p_prefix = "#define" if phase else "// #define"
        lines = re.sub(r"^(?P<ind>\s*)(?://\s*)?#\s*define\s+FLOAT_CARR_PHASE\b.*", f"\\g<ind>{p_prefix} FLOAT_CARR_PHASE", lines, flags=re.MULTILINE)
        lines = re.sub(r"^(?P<ind>\s*)(?://\s*)?#\s*define\s+USER_MOTION_SIZE\b.*", f"\\g<ind>#define USER_MOTION_SIZE ({motion})", lines, flags=re.MULTILINE)
        lines = re.sub(r"^(?P<ind>\s*)(?://\s*)?#\s*define\s+MAX_SAT\b.*", f"\\g<ind>#define MAX_SAT ({sat})", lines, flags=re.MULTILINE)
        lines = re.sub(r"^(?P<ind>\s*)(?://\s*)?#\s*define\s+MAX_CHAN\b.*", f"\\g<ind>#define MAX_CHAN ({chan})", lines, flags=re.MULTILINE)
        header.write_text(lines, encoding="utf-8")