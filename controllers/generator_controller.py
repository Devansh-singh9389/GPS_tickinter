import threading, queue, tkinter as tk
from tkinter import filedialog
from services.generator_service import GeneratorService
from views.tab_generator import GeneratorView
from views.components import MultiSelectDeleteDialog
from core.config import DATA_DIR_BINARY
from tkinter import messagebox

class GeneratorController:
    def __init__(self, parent, app_state):
        self.state = app_state
        self.svc = GeneratorService()
        self.q = queue.Queue()
        self.view = GeneratorView(parent, self, app_state)
        self.view.pack(fill=tk.BOTH, expand=True)
        self._busy = False

    def browse_exe(self):
        path = filedialog.askopenfilename()
        if path: self.view.exe_var.set(path)

    def browse_nav(self):
        path = filedialog.askopenfilename()
        if path: self.view.nav_file_var.set(path)

    def browse_output(self):
        path = filedialog.asksaveasfilename()
        if path: self.view.output_file_var.set(path)

    def browse_csv(self):
        path = filedialog.askopenfilename()
        if path: self.view.csv_file_var.set(path)

    def browse_nmea(self):
        path = filedialog.askopenfilename()
        if path: self.view.nmea_file_var.set(path)

    def start_generate(self):
        if self._busy: return
        self._set_busy(True)
        
        # Build command array safely in controller
        cmd = [self.view.exe_var.get(), "-e", self.view.nav_file_var.get()]
        mode = self.view.motion_mode_var.get()
        if mode == "static":
            if self.view.static_coord_var.get() == "ecef": cmd += ["-c", f"{self.view.ecef_x_var.get()},{self.view.ecef_y_var.get()},{self.view.ecef_z_var.get()}"]
            else: cmd += ["-l", f"{self.view.llh_lat_var.get()},{self.view.llh_lon_var.get()},{self.view.llh_hgt_var.get()}"]
        elif mode == "csv": cmd += ["-u" if self.view.traj_format_var.get() == "ecef" else "-x", self.view.csv_file_var.get()]
        elif mode == "nmea": cmd += ["-g", self.view.nmea_file_var.get()]
        
        cmd += ["-d", self.view.duration_var.get(), "-s", self.view.sample_rate_var.get(), "-b", self.view.iq_bits_var.get(), "-o", self.view.output_file_var.get()]

        threading.Thread(target=self.svc.generate, args=(
            cmd, self.view.output_file_var.get(),
            lambda tag, msg: self.q.put({"t": "l", "tag": tag, "m": msg}),
            lambda s, p: self.q.put({"t": "d", "s": s, "p": p})), daemon=True).start()
        self._poll()

    def stop_generate(self):
        self.svc.stop_process()

    def _poll(self):
        try:
            while True:
                msg = self.q.get_nowait()
                if msg["t"] == "l": self.view.log_line(msg["m"], msg["tag"])
                elif msg["t"] == "d":
                    self._set_busy(False)
                    if msg["s"]:
                        self.state.latest_bin_path.set(msg["p"])
                        self.view.log_line(f"Success: {msg['p']}", "success")
                    return
        except queue.Empty: pass
        if self._busy: self.view.after(100, self._poll)

    def _set_busy(self, busy):
        self._busy = busy
        self.view.generate_btn.config(state=tk.DISABLED if busy else tk.NORMAL)
        self.view.stop_btn.config(state=tk.NORMAL if busy else tk.DISABLED)
        if busy: self.view.process_progress.start(12)
        else: self.view.process_progress.stop()

    def start_generate(self):
        if self._busy: return
        self._set_busy(True)
        
        # 1. Base command (exe and nav file)
        cmd = [self.view.exe_var.get(), "-e", self.view.nav_file_var.get()]
        
        # 2. Location & Movement Flags
        mode = self.view.motion_mode_var.get()
        if mode == "static":
            if self.view.static_coord_var.get() == "ecef": 
                cmd += ["-c", f"{self.view.ecef_x_var.get()},{self.view.ecef_y_var.get()},{self.view.ecef_z_var.get()}"]
            else: 
                cmd += ["-l", f"{self.view.llh_lat_var.get()},{self.view.llh_lon_var.get()},{self.view.llh_hgt_var.get()}"]
        elif mode == "csv": 
            flag = "-u" if self.view.traj_format_var.get() == "ecef" else "-x"
            cmd += [flag, self.view.csv_file_var.get()]
        elif mode == "nmea": 
            cmd += ["-g", self.view.nmea_file_var.get()]
        
        # 3. Hardware / Output Parameters
        cmd += ["-d", self.view.duration_var.get(), "-s", self.view.sample_rate_var.get(), "-b", self.view.iq_bits_var.get()]
        
        # Output handling (-o)
        out_target = self.view.output_file_var.get().strip()
        if out_target and out_target != "-":
            cmd += ["-o", out_target]
        elif out_target == "-":
            cmd += ["-o", "-"] # Stream to stdout

        # 4. Optional Time Overrides
        if self.view.start_time_var.get().strip():
            cmd += ["-t", self.view.start_time_var.get().strip()]
        if self.view.toc_time_var.get().strip():
            cmd += ["-T", self.view.toc_time_var.get().strip()]
        if self.view.leap_sec_var.get().strip():
            cmd += ["-L", self.view.leap_sec_var.get().strip()]

        # 5. Advanced Physics Checkboxes
        if self.view.disable_iono_var.get():
            cmd += ["-i"]
        if self.view.disable_pathloss_var.get():
            cmd += ["-p"]
        if self.view.verbose_var.get():
            cmd += ["-v"]

        # Run the thread
        threading.Thread(target=self.svc.generate, args=(
            cmd, out_target,
            lambda tag, msg: self.q.put({"t": "l", "tag": tag, "m": msg}),
            lambda s, p: self.q.put({"t": "d", "s": s, "p": p})), daemon=True).start()
        self._poll()

    def clear_bins(self):
        if self._busy:
            return
            
        # 1. Find all .bin files in the directory
        bin_dir = DATA_DIR_BINARY
        if not bin_dir.exists():
            messagebox.showinfo("Clear BINs", "Binary directory does not exist yet.")
            return
            
        files = list(bin_dir.glob("*.bin"))
        
        # 2. Define what happens when the user clicks "Delete Selected" in the dialog
        def on_delete_confirmed(selected_files):
            if not selected_files:
                return
            
            deleted_count = 0
            for file_path in selected_files:
                try:
                    file_path.unlink()
                    deleted_count += 1
                    # Clear shared state if we just deleted the active file
                    if self.state.latest_bin_path.get() == str(file_path):
                        self.state.latest_bin_path.set("")
                except Exception as e:
                    self.view.log_line(f"Failed to delete {file_path.name}: {e}", "error")
            
            self.view.log_line(f"Successfully deleted {deleted_count} BIN files.", "success")

        # 3. Open the Dialog!
        MultiSelectDeleteDialog(self.view, "Manage BIN Files", files, on_delete_confirmed)


    