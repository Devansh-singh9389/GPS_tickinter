import threading
import queue
import tkinter as tk
import pathlib
import re
import json
import datetime
import shutil
from tkinter import filedialog, messagebox
from services.generator_service import GeneratorService
from views.tab_generator import GeneratorView
from core.config import DATA_DIR_BINARY
from views.components import MultiSelectDeleteDialog

class GeneratorController:
    def __init__(self, parent, app_state):
        self.state = app_state
        self.svc = GeneratorService()
        self.q = queue.Queue()
        self.view = GeneratorView(parent, self, app_state)
        self.view.pack(fill=tk.BOTH, expand=True)
        
        self._busy = False
        self._user_locked_name = False

        # --- SETUP REACTIVE AUTO-NAMING ---
        triggers = [
            self.view.motion_mode_var, self.view.sample_rate_var, 
            self.view.iq_bits_var, self.view.llh_lat_var, 
            self.view.llh_lon_var, self.view.csv_file_var, 
            self.view.nmea_file_var
        ]
        for var in triggers:
            var.trace_add("write", self.generate_auto_name)
        
        self.generate_auto_name()

    def force_auto_name(self):
        """Unlocks the user override and forces an auto-name generation."""
        self._user_locked_name = False
        self.generate_auto_name()
        self.view.log_line("Output filename auto-generated based on current parameters.", "success")

    def generate_auto_name(self, *args):
        """Builds a smart filename based on current UI parameters."""
        if not self.state.get_setting("auto_name", True):
            return
        if self._user_locked_name or not hasattr(self, 'view'):
            return
            
        mode = self.view.motion_mode_var.get()
        sr = self.view.sample_rate_var.get()
        bits = self.view.iq_bits_var.get()

        try:
            sr_mhz = float(sr) / 1000000
            sr_str = f"{sr_mhz:g}MHz" 
        except ValueError:
            sr_str = f"{sr}Hz"

        if mode == "static":
            if self.view.static_coord_var.get() == "ecef":
                loc_str = "Static_ECEF"
            else:
                lat = self.view.llh_lat_var.get()[:6]
                lon = self.view.llh_lon_var.get()[:7]
                loc_str = f"Static_Lat{lat}_Lon{lon}"
        elif mode == "csv":
            path_str = self.view.csv_file_var.get()
            loc_str = f"Dynamic_{pathlib.Path(path_str).stem}" if path_str else "Dynamic_CSV"
        elif mode == "nmea":
            path_str = self.view.nmea_file_var.get()
            loc_str = f"Dynamic_{pathlib.Path(path_str).stem}" if path_str else "Dynamic_NMEA"
        else:
            loc_str = "GPS_Baseband"

        loc_str = re.sub(r'[^a-zA-Z0-9_\-\.]', '', loc_str).strip('_')

        filename = f"{loc_str}_{sr_str}_{bits}bit.bin"
        
        target_path = DATA_DIR_BINARY / filename
        self.view.output_file_var.set(str(target_path))

    # --- NEW: METADATA SIDECAR GENERATOR ---
    def _save_metadata_sidecar(self, bin_path_str):
        bin_path = pathlib.Path(bin_path_str)
        json_path = bin_path.with_suffix('.json')
        mode = self.view.motion_mode_var.get()

        # Build the structured dictionary
        metadata = {
            "filename": bin_path.name,
            "created_at": datetime.datetime.now(datetime.UTC).isoformat() + "Z",
            "generator_settings": {
                "duration_seconds": self.view.duration_var.get(),
                "sample_rate_hz": self.view.sample_rate_var.get(),
                "iq_bits": self.view.iq_bits_var.get(),
                "motion_mode": mode,
            },
            "physics_flags": {
                "disable_iono": self.view.disable_iono_var.get(),
                "disable_pathloss": self.view.disable_pathloss_var.get(),
                "verbose_mode": self.view.verbose_var.get()
            },
            "time_overrides": {
                "start_time": self.view.start_time_var.get(),
                "toc_time": self.view.toc_time_var.get(),
                "leap_second": self.view.leap_sec_var.get()
            }
        }

        # Inject location data based on the selected mode
        if mode == "static":
            if self.view.static_coord_var.get() == "ecef":
                metadata["generator_settings"]["location"] = {
                    "format": "ECEF",
                    "x": self.view.ecef_x_var.get(),
                    "y": self.view.ecef_y_var.get(),
                    "z": self.view.ecef_z_var.get()
                }
            else:
                metadata["generator_settings"]["location"] = {
                    "format": "LLH",
                    "lat": self.view.llh_lat_var.get(),
                    "lon": self.view.llh_lon_var.get(),
                    "height": self.view.llh_hgt_var.get()
                }
        elif mode == "csv":
            metadata["generator_settings"]["trajectory_file"] = self.view.csv_file_var.get()
            metadata["generator_settings"]["csv_format"] = self.view.traj_format_var.get()
        elif mode == "nmea":
            metadata["generator_settings"]["trajectory_file"] = self.view.nmea_file_var.get()

        # Save to disk
        try:
            with open(json_path, 'w') as f:
                json.dump(metadata, f, indent=4)
            self.view.log_line(f"Metadata sidecar created: {json_path.name}", "muted")
        except Exception as e:
            self.view.log_line(f"Failed to save metadata sidecar: {e}", "warn")

    # --- FILE BROWSING METHODS ---
    def browse_exe(self):
        path = filedialog.askopenfilename(title="Select Compiler Executable")
        if path: self.view.exe_var.set(path)
        
    def browse_nav(self):
        path = filedialog.askopenfilename(title="Select BRDC Navigation File")
        if path: self.view.nav_file_var.set(path)
        
    def browse_csv(self):
        path = filedialog.askopenfilename(title="Select Trajectory CSV", filetypes=[("CSV Files", "*.csv")])
        if path: self.view.csv_file_var.set(path)
        
    def browse_nmea(self):
        path = filedialog.askopenfilename(title="Select NMEA GGA File", filetypes=[("NMEA Files", "*.txt", "*.nmea", "*.log")])
        if path: self.view.nmea_file_var.set(path)

    def browse_output(self):
        path = filedialog.asksaveasfilename(
            title="Save BIN File",
            defaultextension=".bin",
            initialdir=DATA_DIR_BINARY,
            filetypes=[("Binary Files", "*.bin"), ("All Files", "*.*")]
        )
        if path:
            self.view.output_file_var.set(path)
            self._user_locked_name = True 

    # --- CORE LOGIC ---
    def clear_bins(self):
        if self._busy: return
        bin_dir = DATA_DIR_BINARY
        if not bin_dir.exists():
            messagebox.showinfo("Clear BINs", "Binary directory does not exist yet.")
            return
            
        files = list(bin_dir.glob("*.bin"))
        
        def on_delete_confirmed(selected_files):
            if not selected_files: return
            deleted_count = 0
            for file_path in selected_files:
                try:
                    # Delete the .bin file
                    file_path.unlink()
                    deleted_count += 1
                    
                    # --- NEW: Delete the matching .json sidecar if it exists ---
                    sidecar = file_path.with_suffix('.json')
                    if sidecar.exists():
                        sidecar.unlink()

                    # Clear shared state
                    if self.state.latest_bin_path.get() == str(file_path):
                        self.state.latest_bin_path.set("")
                        
                except Exception as e:
                    self.view.log_line(f"Failed to delete {file_path.name}: {e}", "error")
            self.view.log_line(f"Successfully deleted {deleted_count} BIN files and sidecars.", "success")
            
        MultiSelectDeleteDialog(self.view, "Manage BIN Files", files, on_delete_confirmed)

    def start_generate(self):
        if self._busy: return

        # --- GUARDRAIL 3: THE "FAT FINGER" INPUT VALIDATOR ---
        try:
            duration_val = float(self.view.duration_var.get().strip())
            sample_rate_val = float(self.view.sample_rate_var.get().strip())
            bits_val = int(self.view.iq_bits_var.get().strip())
        except ValueError:
            messagebox.showerror("Invalid Input",
                                 "Duration, Sample Rate, and I/Q Bits must be valid numbers (e.g., 300, 2600000, 16).")
            return

        if duration_val <= 0 or sample_rate_val <= 0:
            messagebox.showerror("Invalid Input", "Duration and Sample Rate must be strictly greater than zero.")
            return

        # --- GUARDRAIL 2: THE "DISK SPACE BOMB" CHECKER ---
        # Calculate exactly how massive this binary file will be.
        # Math: Sample_Rate * 2 (I & Q) * (Bits / 8) * Duration
        bytes_per_sample = bits_val / 8
        bytes_per_second = sample_rate_val * 2 * bytes_per_sample
        estimated_total_bytes = bytes_per_second * duration_val

        # Ask the Operating System for the actual free space on the drive
        free_space = shutil.disk_usage(DATA_DIR_BINARY).free

        # We require the estimated size PLUS a 500 MB safety buffer so the OS doesn't crash
        if free_space < (estimated_total_bytes + (500 * 1024 * 1024)):
            req_gb = estimated_total_bytes / (1024 ** 3)
            free_gb = free_space / (1024 ** 3)
            messagebox.showerror(
                "Insufficient Disk Space",
                f"SAFETY ABORT: This simulation will generate a {req_gb:.2f} GB binary file.\n\n"
                f"You only have {free_gb:.2f} GB of free space available on your drive.\n"
                "Please free up some hard drive space or reduce the simulation duration."
            )
            return
        # ----------------------------------------------------

        self._set_busy(True)

        cmd = [self.view.exe_var.get(), "-e", self.view.nav_file_var.get()]

        mode = self.view.motion_mode_var.get()
        if mode == "static":
            if self.view.static_coord_var.get() == "ecef":
                cmd += ["-c", f"{self.view.ecef_x_var.get()},{self.view.ecef_y_var.get()},{self.view.ecef_z_var.get()}"]
            else:
                cmd += ["-l",
                        f"{self.view.llh_lat_var.get()},{self.view.llh_lon_var.get()},{self.view.llh_hgt_var.get()}"]
        elif mode == "csv":
            flag = "-u" if self.view.traj_format_var.get() == "ecef" else "-x"
            cmd += [flag, self.view.csv_file_var.get()]
        elif mode == "nmea":
            cmd += ["-g", self.view.nmea_file_var.get()]

        cmd += ["-d", str(duration_val), "-s", str(sample_rate_val), "-b", str(bits_val)]

        out_target = self.view.output_file_var.get().strip()
        if out_target and out_target != "-":
            cmd += ["-o", out_target]
        elif out_target == "-":
            cmd += ["-o", "-"]

        if self.view.start_time_var.get().strip(): cmd += ["-t", self.view.start_time_var.get().strip()]
        if self.view.toc_time_var.get().strip():   cmd += ["-T", self.view.toc_time_var.get().strip()]
        if self.view.leap_sec_var.get().strip():   cmd += ["-L", self.view.leap_sec_var.get().strip()]

        if self.view.disable_iono_var.get():       cmd += ["-i"]
        if self.view.disable_pathloss_var.get():   cmd += ["-p"]

        # Grab Verbose state straight from global Settings, unless the user manually checked it on the UI
        global_verbose = self.state.get_setting("verbose_logging", False)
        if self.view.verbose_var.get() or global_verbose:
            cmd += ["-v"]

        threading.Thread(target=self.svc.generate, args=(
            cmd, out_target, duration_val,
            lambda tag, msg: self.q.put({"t": "l", "tag": tag, "m": msg}),
            lambda s, p: self.q.put({"t": "d", "s": s, "p": p}),
            lambda v: self.q.put({"t": "p", "v": v})
        ), daemon=True).start()

        self._poll()

    def stop_generate(self):
        self.svc.stop_process()

    def _poll(self):
        try:
            while True:
                msg = self.q.get_nowait()
                if msg["t"] == "l": 
                    self.view.log_line(msg["m"], msg["tag"])
                
                # --- FIXED: Update the DoubleVar instead of the widget ---
                elif msg["t"] == "p":
                    pct = int(msg["v"] * 100)
                    self.view.progress_var.set(pct) 
                    self.view.progress_label.config(text=f"Generating... {pct}%")
                # ---------------------------------------------------------
                
                elif msg["t"] == "d":
                    self._set_busy(False)
                    if msg["s"]:
                        self.state.latest_bin_path.set(msg["p"])
                        self.view.log_line(f"Success: {msg['p']}", "success")
                        if msg["p"] != "-": 
                            self._save_metadata_sidecar(msg["p"])
                    else:
                        self.view.log_line(f"Failed: {msg['p']}", "error")
                    return
        except queue.Empty: pass
        if self._busy: self.view.after(100, self._poll)

    def _set_busy(self, busy):
        self._busy = busy
        self.view.generate_btn.config(state=tk.DISABLED if busy else tk.NORMAL)
        self.view.stop_btn.config(state=tk.NORMAL if busy else tk.DISABLED)
        
        # IMPORTANT: There are absolutely no .start() or .stop() commands here!
        if not busy:
            self.view.progress_var.set(0.0)
            self.view.progress_label.config(text="Idle")
        else:
            self.view.progress_var.set(0.0)
            self.view.progress_label.config(text="Initializing...")

    def select_exe_file(self):
        """Opens the custom modern dialog to pick a previously compiled executable."""
        from views.components import SingleSelectDialog
        from core.config import DATA_DIR_COMPILED

        SingleSelectDialog(
            parent=self.view,
            title="Select Executable File",
            directory_path=DATA_DIR_COMPILED,
            file_extension_filter="",  # Empty string catches all files in the compiled folder
            on_select=lambda filepath: self.view.exe_var.set(filepath)
        )

    def select_nav_file(self):
        """Opens the custom modern dialog to pick a previously downloaded BRDC file."""
        # Importing locally here makes it super easy to copy-paste!
        from views.components import SingleSelectDialog
        from core.config import DATA_DIR_BRDCS

        SingleSelectDialog(
            parent=self.view,
            title="Select Ephemeris (BRDC) File",
            directory_path=DATA_DIR_BRDCS,
            file_extension_filter="n",  # This catches .24n, .25n, etc.
            on_select=lambda filepath: self.view.nav_file_var.set(filepath)
        )

