import datetime
import threading
import queue
import tkinter as tk
from tkinter import messagebox
from services.brdc_service import BRDCService
from views.tab_brdc import BRDCDownloaderView
from core.config import save_settings, DATA_DIR_BRDCS
from views.components import MultiSelectDeleteDialog

class BRDCController:
    def __init__(self, parent, app_state):
        self.state = app_state
        self.svc = BRDCService()
        self.q = queue.Queue()

        # --- FIXED: We are now passing app_state to the View! ---
        self.view = BRDCDownloaderView(parent, self, app_state)

        self.view.pack(fill=tk.BOTH, expand=True)

    def start_download(self):
        user, pwd = self.view.username_var.get().strip(), self.view.password_var.get().strip()
        if not user or not pwd: 
            return self.view.log_line("Missing credentials", "error")
        
        # Save credentials to local cache immediately upon clicking download
        save_settings({
            "nasa_username": user,
            "nasa_password": pwd
        })
        
        date = datetime.datetime.now(datetime.UTC).date() if self.view.date_mode.get() == "today" else datetime.date(int(self.view.year_var.get()), int(self.view.month_var.get()), int(self.view.day_var.get()))
        
        self.view.download_btn.config(state=tk.DISABLED)
        self.view.progress_label.config(text="Connecting...")
        
        threading.Thread(target=self.svc.download, args=(user, pwd, date, 
            lambda v: self.q.put({"t": "p", "v": v}),
            lambda tag, msg: self.q.put({"t": "l", "tag": tag, "m": msg}),
            lambda s, p: self.q.put({"t": "d", "s": s, "p": p})), daemon=True).start()
        self._poll()

    def _poll(self):
        try:
            while True:
                msg = self.q.get_nowait()
                if msg["t"] == "p": 
                    self.view.progress_var.set(msg["v"])
                    pct = int(msg["v"] * 100)
                    self.view.progress_label.config(text=f"Downloading... {pct}%" if pct < 100 else "Decompressing...")
                elif msg["t"] == "l": 
                    self.view.log_line(msg["m"], msg["tag"])
                elif msg["t"] == "d":
                    if msg["s"]: 
                        self.state.latest_brdc_path.set(msg["p"])
                        self.view.log_line(f"Saved to: {msg['p']}", "success")
                        self.view.progress_label.config(text="Complete")
                    else:
                        self.view.log_line(f"ERROR: {msg['p']}", "error")
                        self.view.progress_label.config(text="Failed")
                    
                    self.view.download_btn.config(state=tk.NORMAL)
                    return
        except queue.Empty: 
            pass
            
        self.view.after(100, self._poll)

    def clear_brdc_files(self):
        """Opens a dialog allowing the user to select which BRDC files to delete."""
        if not DATA_DIR_BRDCS.exists():
            messagebox.showinfo("Clear BRDCs", "BRDC directory does not exist yet.")
            return
            
        # Get all files containing 'n' (handles .24n, .25n, etc)
        files = list(DATA_DIR_BRDCS.glob("*.*n*"))
        
        def on_delete_confirmed(selected_files):
            if not selected_files:
                return
            
            deleted_count = 0
            for file_path in selected_files:
                try:
                    file_path.unlink()
                    deleted_count += 1
                    # Clear shared state if we just deleted the active file
                    if self.state.latest_brdc_path.get() == str(file_path):
                        self.state.latest_brdc_path.set("")
                except Exception as e:
                    self.view.log_line(f"Failed to delete {file_path.name}: {e}", "error")
            
            self.view.log_line(f"Successfully deleted {deleted_count} BRDC files.", "success")

        # Open the Custom Checkbox Dialog
        MultiSelectDeleteDialog(self.view, "Manage BRDC Files", files, on_delete_confirmed)
        
        