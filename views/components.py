import tkinter as tk
from tkinter import ttk
from core.theme import *

# --- ADVANCED HOVER TOOLTIP ENGINE ---
def attach_advanced_tooltip(widget: tk.Widget, title: str, description: str) -> None:
    tip = {"window": None, "id": None}
    
    def show(_event):
        if tip["window"] is not None: return
        # 400ms delay so it doesn't flash annoyingly when moving the mouse fast
        tip["id"] = widget.after(400, _show_tooltip)
        
    def _show_tooltip():
        # Position slightly to the right of the label
        x = widget.winfo_rootx() + widget.winfo_width() + 10
        y = widget.winfo_rooty() - 10
        
        win = tk.Toplevel(widget)
        win.wm_overrideredirect(True)
        win.wm_geometry(f"+{x}+{y}")
        win.configure(bg=C_BORDER) 
        
        frame = tk.Frame(win, bg=C_ENTRY_BG, padx=12, pady=10)
        frame.pack(padx=1, pady=1) # Creates a 1px border effect
        
        tk.Label(frame, text=title, font=("Segoe UI", 9, "bold"), fg=C_ACCENT, bg=C_ENTRY_BG, justify=tk.LEFT).pack(anchor="w", pady=(0, 4))
        tk.Label(frame, text=description, font=("Segoe UI", 9), fg=C_TEXT, bg=C_ENTRY_BG, justify=tk.LEFT, wraplength=280).pack(anchor="w")
        
        tip["window"] = win

    def hide(_event):
        if tip["id"]: 
            widget.after_cancel(tip["id"])
            tip["id"] = None
        if tip["window"] is not None:
            tip["window"].destroy()
            tip["window"] = None

    widget.bind("<Enter>", show)
    widget.bind("<Leave>", hide)


class StyledFrame(tk.Frame):
    def __init__(self, parent, **kwargs):
        kwargs.setdefault("bg", C_PANEL)
        super().__init__(parent, **kwargs)

class SectionLabel(tk.Label):
    def __init__(self, parent, text: str, **kwargs):
        super().__init__(parent, text=text.upper(), fg=C_ACCENT, bg=kwargs.pop("bg", C_PANEL), font=("Courier New", 9, "bold"), **kwargs)

# --- SMART LABEL (UPDATED) ---
class FieldLabel(tk.Label):
    def __init__(self, parent, text: str, tooltip_title: str = None, tooltip_desc: str = None, **kwargs):
        # If tooltips are provided, add the "ⓘ" icon to the text
        display_text = f"{text}  ⓘ" if tooltip_title and tooltip_desc else text
        super().__init__(parent, text=display_text, fg=C_TEXT, bg=kwargs.pop("bg", C_PANEL), font=FONT_BODY, **kwargs)
        
        # Automatically attach the hover pop-up
        if tooltip_title and tooltip_desc:
            self.config(cursor="hand2", fg=C_ACCENT2) # Make it look clickable/hoverable
            attach_advanced_tooltip(self, tooltip_title, tooltip_desc)

class StyledEntry(tk.Entry):
    def __init__(self, parent, **kwargs):
        kwargs.setdefault("bg", C_ENTRY_BG)
        kwargs.setdefault("fg", C_TEXT)
        kwargs.setdefault("insertbackground", C_ACCENT)
        kwargs.setdefault("relief", tk.FLAT)
        kwargs.setdefault("font", FONT_BODY)
        kwargs.setdefault("highlightthickness", 1)
        kwargs.setdefault("highlightcolor", C_ACCENT)
        kwargs.setdefault("highlightbackground", C_BORDER)
        super().__init__(parent, **kwargs)

class PrimaryButton(tk.Button):
    def __init__(self, parent, **kwargs):
        kwargs.setdefault("bg", C_ACCENT)
        kwargs.setdefault("fg", C_BG)
        kwargs.setdefault("activebackground", C_ACCENT2)
        kwargs.setdefault("activeforeground", C_BG)
        kwargs.setdefault("relief", tk.FLAT)
        kwargs.setdefault("font", FONT_LABEL)
        kwargs.setdefault("cursor", "hand2")
        kwargs.setdefault("padx", 14)
        kwargs.setdefault("pady", 6)
        super().__init__(parent, **kwargs)
        self.bind("<Enter>", lambda _: self.config(bg=C_ACCENT2))
        self.bind("<Leave>", lambda _: self.config(bg=kwargs["bg"]))

class GhostButton(tk.Button):
    def __init__(self, parent, **kwargs):
        kwargs.setdefault("bg", C_PANEL)
        kwargs.setdefault("fg", C_ACCENT)
        kwargs.setdefault("activebackground", C_BORDER)
        kwargs.setdefault("activeforeground", C_ACCENT)
        kwargs.setdefault("relief", tk.FLAT)
        kwargs.setdefault("font", FONT_BODY)
        kwargs.setdefault("cursor", "hand2")
        kwargs.setdefault("padx", 12)
        kwargs.setdefault("pady", 5)
        kwargs.setdefault("highlightthickness", 1)
        kwargs.setdefault("highlightcolor", C_ACCENT)
        kwargs.setdefault("highlightbackground", C_BORDER)
        super().__init__(parent, **kwargs)
        self.bind("<Enter>", lambda _: self.config(bg=C_BORDER))
        self.bind("<Leave>", lambda _: self.config(bg=C_PANEL))

class Divider(tk.Frame):
    def __init__(self, parent, **kwargs):
        kwargs.setdefault("bg", C_BORDER)
        super().__init__(parent, height=1, **kwargs)

class ScrollableFrame(tk.Frame):
    def __init__(self, parent, **kwargs):
        bg_color = kwargs.get("bg", C_BG)
        super().__init__(parent, bg=bg_color)
        
        self.canvas = tk.Canvas(self, bg=bg_color, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview, width=20)
        self.content = tk.Frame(self.canvas, bg=bg_color)
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.content, anchor="nw")
        
        self.content.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        
        self.bind("<Enter>", self._bind_mouse)
        self.bind("<Leave>", self._unbind_mouse)
        self.canvas.bind("<Enter>", self._bind_mouse)
        self.canvas.bind("<Leave>", self._unbind_mouse)
        self.content.bind("<Enter>", self._bind_mouse)
        self.content.bind("<Leave>", self._unbind_mouse)
        
    def _on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def _on_canvas_configure(self, event):
        if self.canvas.winfo_width() > self.content.winfo_reqwidth():
            self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _bind_mouse(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel) 
        self.canvas.bind_all("<Button-5>", self._on_mousewheel) 

    def _unbind_mouse(self, event):
        x, y = self.winfo_pointerxy()
        widget = self.winfo_containing(x, y)
        if widget is not None and str(widget).startswith(str(self)):
            return
            
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")

# --- ADD THIS TO THE BOTTOM OF views/components.py ---
class MultiSelectDeleteDialog(tk.Toplevel):
    """A custom dialog to select multiple files for deletion."""
    def __init__(self, parent, title, files, on_confirm):
        super().__init__(parent)
        self.title(title)
        self.geometry("1080x720")
        self.configure(bg=C_BG)
        self.transient(parent) # Tie to main window
        self.grab_set()        # Block main window until closed
        
        # Center the dialog
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (450 // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (300 // 2)
        self.geometry(f"+{x}+{y}")

        tk.Label(self, text="Select files to delete:", font=FONT_TITLE, bg=C_BG, fg=C_TEXT).pack(pady=(12, 4), padx=12, anchor="w")
        
        # Scrollable list area
        list_frame = StyledFrame(self)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)
        
        canvas = tk.Canvas(list_frame, bg=C_PANEL, highlightthickness=0)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        scrollable_content = tk.Frame(canvas, bg=C_PANEL)
        
        scrollable_content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_content, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Create a checkbox for every file
        self.check_vars = {}
        if not files:
            tk.Label(scrollable_content, text="No files found in this directory.", bg=C_PANEL, fg=C_MUTED, font=FONT_BODY).pack(pady=10, padx=10)
        else:
            for f in files:
                var = tk.BooleanVar(value=False)
                self.check_vars[f] = var
                chk = tk.Checkbutton(scrollable_content, text=f.name, variable=var, bg=C_PANEL, fg=C_TEXT, selectcolor=C_ENTRY_BG, activebackground=C_PANEL, activeforeground=C_TEXT)
                chk.pack(anchor="w", padx=5, pady=2)

        # Action Buttons
        btn_frame = tk.Frame(self, bg=C_BG)
        btn_frame.pack(fill=tk.X, padx=12, pady=12)
        
        def confirm():
            selected = [f for f, var in self.check_vars.items() if var.get()]
            on_confirm(selected)
            self.destroy()

        PrimaryButton(btn_frame, text="Delete Selected", command=confirm, bg=C_ERROR).pack(side=tk.RIGHT)
        GhostButton(btn_frame, text="Cancel", command=self.destroy).pack(side=tk.RIGHT, padx=8)

