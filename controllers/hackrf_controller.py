import threading
import queue
import tkinter as tk
from tkinter import filedialog, messagebox
from services.hackrf_service import HackRFService
from views.tab_hackrf import HackRFView
from core.theme import C_SUCCESS, C_ERROR, C_MUTED


class HackRFController:
    def __init__(self, parent, app_state):
        self.state = app_state
        self.svc = HackRFService()
        self.q = queue.Queue()
        self.view = HackRFView(parent, self, app_state)
        self.view.pack(fill=tk.BOTH, expand=True)

        # Start the automatic background hardware detection loop
        self._poll_hardware()

    def _poll_hardware(self):
        # Spawns a background thread to check for hardware connection states.
        def check():
            connected = self.svc.check_hardware()
            # Safely push the UI update execution back to the primary main thread
            if hasattr(self, 'view') and self.view.winfo_exists():
                self.view.after(0, lambda: self._update_hardware_ui(connected))

        threading.Thread(target=check, daemon=True).start()
        poll_rate = self.state.get_setting("hardware_poll_rate_ms", 3000)

        # Reschedule next check in 3000 milliseconds (3 seconds)
        if hasattr(self, 'view') and self.view.winfo_exists():
            self.view.after(poll_rate, self._poll_hardware)

    def select_bin_file(self):
        """Opens the custom modern dialog to pick a previously compiled executable."""
        from views.components import SingleSelectDialog
        from core.config import DATA_DIR_BINARY

        SingleSelectDialog(
            parent=self.view,
            title="Select Executable File",
            directory_path=DATA_DIR_BINARY,
            file_extension_filter="bin",  # Empty string catches all files in the compiled folder
            on_select=lambda filepath: self.view.file_var.set(filepath)
        )

    def _update_hardware_ui(self, connected: bool):
        """Updates the visual color state of the indicator string inside the header."""
        if connected:
            self.view.hw_status_var.set("✅ HackRF Detected")
            self.view.hw_status_lbl.config(fg=C_SUCCESS)
        else:
            self.view.hw_status_var.set("❌ HackRF Disconnected")
            self.view.hw_status_lbl.config(fg=C_ERROR)

    def browse_file(self):
        if self.view.mode_var.get() == "-t":
            path = filedialog.askopenfilename(title="Select File to Transmit")
        else:
            path = filedialog.asksaveasfilename(title="Select Save Location")

        if path:
            self.view.file_var.set(path)

    def start_tx(self):
        target_file = self.view.file_var.get().strip()

        if not target_file and not self.view.cw_var.get().strip():
            messagebox.showwarning("Missing File", "Please select a target file or enable CW mode.")
            return

        self.view.start_btn.config(state=tk.DISABLED)
        self.view.stop_btn.config(state=tk.NORMAL)

        cmd = ["hackrf_transfer"]

        if target_file:
            cmd += [self.view.mode_var.get(), target_file]

        if self.view.mode_var.get() == "-r" and self.view.wav_var.get():
            cmd.append("-w")

        if self.view.freq_var.get().strip(): cmd += ["-f", self.view.freq_var.get().strip()]
        if self.view.sr_var.get().strip():   cmd += ["-s", self.view.sr_var.get().strip()]
        if self.view.bw_var.get().strip():   cmd += ["-b", self.view.bw_var.get().strip()]
        if self.view.force_var.get():        cmd.append("-F")

        cmd += ["-a", self.view.amp_var.get(), "-p", self.view.ant_power_var.get()]

        if self.view.mode_var.get() == "-t":
            if self.view.tx_vga_var.get().strip(): cmd += ["-x", self.view.tx_vga_var.get().strip()]
        else:
            if self.view.rx_lna_var.get().strip(): cmd += ["-l", self.view.rx_lna_var.get().strip()]
            if self.view.rx_vga_var.get().strip(): cmd += ["-g", self.view.rx_vga_var.get().strip()]

        if self.view.serial_var.get().strip():      cmd += ["-d", self.view.serial_var.get().strip()]
        if self.view.hw_trigger_var.get():          cmd.append("-H")
        if self.view.repeat_var.get():              cmd.append("-R")
        if self.view.cw_var.get().strip():          cmd += ["-c", self.view.cw_var.get().strip()]
        if self.view.num_samples_var.get().strip(): cmd += ["-n", self.view.num_samples_var.get().strip()]

        # --- FIXED: Append Frequency Offset (-C) safely ---
        try:
            offset_val = int(self.view.freq_offset_var.get().strip())
            # Only append the flag if the user actually typed a non-zero number
            if offset_val != 0:
                cmd.extend(["-C", str(offset_val)])
        except ValueError:
            import tkinter.messagebox as mb
            mb.showerror("Invalid Input", "Frequency Offset must be a valid number.")
            # Reset buttons if it fails so the user isn't stuck
            self.view.start_btn.config(state=tk.NORMAL)
            self.view.stop_btn.config(state=tk.DISABLED)
            return

        threading.Thread(target=self.svc.run_transfer, args=(
            cmd,
            lambda tag, msg: self.q.put({"t": "l", "tag": tag, "m": msg}),
            lambda s, p: self.q.put({"t": "d", "s": s, "p": p})
        ), daemon=True).start()

        self._poll()

    def stop_tx(self):
        self.svc.stop_process()

    def _poll(self):
        try:
            while True:
                msg = self.q.get_nowait()
                if msg["t"] == "l":
                    self.view.log_line(msg["m"], msg["tag"])
                elif msg["t"] == "d":
                    if msg["s"]:
                        self.view.log_line(msg["p"], "success")
                    else:
                        self.view.log_line(msg["p"], "error")

                    self.view.start_btn.config(state=tk.NORMAL)
                    self.view.stop_btn.config(state=tk.DISABLED)
                    return
        except queue.Empty:
            pass

        self.view.after(100, self._poll)