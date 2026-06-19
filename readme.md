It is designed to be a quick-reference guide so you always know exactly where to go when you want to add a new feature, change a UI element, or write a new background script.

---

# GNSS Signal Simulator Lab 📡

A Python-based desktop toolchain for RF testing and Navigation Data simulation. It provides a complete pipeline to download BRDC ephemeris data, compile `gps-sdr-sim`, generate GPS baseband signal files (`.bin`), and transmit them via a HackRF One SDR.

## 🏗️ Project Architecture

This project uses a clean **MVC (Model-View-Controller)** pattern combined with a **Service Layer**. This keeps the code highly scalable and prevents the UI from freezing during heavy tasks like compiling C code or downloading files.

If you need to edit the code, here is exactly how the responsibilities are divided:

* **`views/` (The Look):** Pure UI. Only Tkinter buttons, labels, and grids live here. No logic!
* **`services/` (The Heavy Lifting):** All subprocesses, API calls, file downloading, and C-header Regex parsing live here. These run on background threads.
* **`controllers/` (The Brains):** Connects the Views to the Services. When a user clicks a button in the View, the Controller validates it, passes it to the Service, and updates the View's progress bar.
* **`models/` (The Data):** Holds shared state (like the path to the latest `.bin` file) so different tabs can talk to each other.
* **`core/` (The Setup):** Shared colors, fonts, and directory paths.

## 📂 Directory Layout

```text
nav-data-toolchain/
├── main.py                     # 🚀 Run this to start the app
├── requirements.txt            # Python dependencies
├── data/                       # Downloaded BRDC and generated .bin files
├── assets/                     # Icons and static assets
├── core/
│   ├── config.py               # Absolute paths (DATA_DIR, PROJECT_ROOT)
│   └── theme.py                # UI Colors, Fonts, and Styles
├── models/
│   └── app_state.py            # Shared data between tabs
├── services/
│   ├── base_service.py         # Subprocess execution logic
│   ├── brdc_service.py         # NASA API downloads
│   ├── compiler_service.py     # gcc / make wrappers & header editing
│   ├── generator_service.py    # gps-sdr-sim execution
│   └── hackrf_service.py       # hackrf_transfer commands
├── views/
│   ├── components.py           # Reusable custom UI widgets (Buttons, Entries)
│   ├── tab_brdc.py             # UI for Tab 1
│   ├── tab_compiler.py         # UI for Tab 2
│   ├── tab_generator.py        # UI for Tab 3
│   └── tab_hackrf.py           # UI for Tab 4
└── controllers/
    ├── brdc_controller.py      # Logic for Tab 1
    ├── compiler_controller.py  # Logic for Tab 2
    ├── generator_controller.py # Logic for Tab 3
    └── hackrf_controller.py    # Logic for Tab 4

```

## 🛠️ How to Edit & Add Features

**Scenario 1: You want to change a color, font, or button style.**

* Go to `core/theme.py` to change the global color palette.
* Go to `views/components.py` if you want to change the border thickness or hover effects of all buttons across the app.

**Scenario 2: You want to add a new input field to the UI.**

1. Go to the specific file in `views/` (e.g., `tab_compiler.py`).
2. Add a `tk.StringVar()` to hold the data.
3. Draw the `FieldLabel` and `StyledEntry` using the `.grid()` layout.

**Scenario 3: You want to change the command-line arguments sent to `gcc` or `hackrf_transfer`.**

1. Go directly to the relevant file in `services/` (e.g., `hackrf_service.py`).
2. Find the `cmd = [...]` list and add your new flags there.

**Scenario 4: You want to add a brand new Tab.**

1. Create `views/tab_new.py` (Draw the UI).
2. Create `services/new_service.py` (Write the Python logic/subprocesses).
3. Create `controllers/new_controller.py` (Connect the View to the Service).
4. Register the new Controller in `main.py`!

## 🚀 Getting Started

**1. Install dependencies:**

```bash
pip install -r requirements.txt

```

**2. Run the application:**

```bash
python main.py

```

**3. External Requirements:**
Ensure you have the following installed on your system path for all tabs to function correctly:

* `gcc` and `make` (For the Compiler tab)
* `hackrf_transfer` (For the HackRF Transmitter tab)