import threading
import queue
import tkinter as tk
from tkinter import filedialog, messagebox
from services.hackrf_service import HackRFService
from views.tab_hackrf import HackRFView

class HackRFController:
    def __init__(self, parent, app_state):
        self.state = app_state
        self.svc = HackRFService()
        self.q = queue.Queue()
        self.view = HackRFView(parent, self, app_state)
        self.view.pack(fill=tk.BOTH, expand=True)

    def browse_file(self):
        # Determine browse behavior based on Tx/Rx mode
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
        
        # Build the dynamic command!
        cmd = ["hackrf_transfer"]
        
        # 1. Mode and File
        cmd += [self.view.mode_var.get(), target_file]
        if self.view.mode_var.get() == "-r" and self.view.wav_var.get():
            cmd.append("-w")

        # 2. Frequency & Hardware
        if self.view.freq_var.get().strip(): cmd += ["-f", self.view.freq_var.get().strip()]
        if self.view.sr_var.get().strip():   cmd += ["-s", self.view.sr_var.get().strip()]
        if self.view.bw_var.get().strip():   cmd += ["-b", self.view.bw_var.get().strip()]
        if self.view.force_var.get():        cmd.append("-F")

        # 3. Amp & Power
        cmd += ["-a", self.view.amp_var.get(), "-p", self.view.ant_power_var.get()]

        # 4. Gain (Apply based on Rx/Tx mode)
        if self.view.mode_var.get() == "-t":
            if self.view.tx_vga_var.get().strip(): cmd += ["-x", self.view.tx_vga_var.get().strip()]
        else:
            if self.view.rx_lna_var.get().strip(): cmd += ["-l", self.view.rx_lna_var.get().strip()]
            if self.view.rx_vga_var.get().strip(): cmd += ["-g", self.view.rx_vga_var.get().strip()]

        # 5. Advanced Sync
        if self.view.serial_var.get().strip():      cmd += ["-d", self.view.serial_var.get().strip()]
        if self.view.hw_trigger_var.get():          cmd.append("-H")
        if self.view.repeat_var.get():              cmd.append("-R")
        if self.view.cw_var.get().strip():          cmd += ["-c", self.view.cw_var.get().strip()]
        if self.view.num_samples_var.get().strip(): cmd += ["-n", self.view.num_samples_var.get().strip()]

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