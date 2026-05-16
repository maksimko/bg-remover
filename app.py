import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, ttk

import numpy as np
from PIL import Image
from rembg import remove, new_session
from scipy.ndimage import binary_dilation


def resource_path(relative_path):
    """Get path to bundled resource (works for PyInstaller and dev)."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def setup_model_path():
    """Point rembg to the bundled model when running as .exe."""
    if hasattr(sys, "_MEIPASS"):
        os.environ["U2NET_HOME"] = resource_path("models")


def clean_white_edges(img, border_size=3, white_threshold=240):
    data = np.array(img)
    is_white = (
        (data[:, :, 0] > white_threshold)
        & (data[:, :, 1] > white_threshold)
        & (data[:, :, 2] > white_threshold)
        & (data[:, :, 3] > 0)
    )
    is_transparent = data[:, :, 3] == 0
    border_zone = binary_dilation(is_transparent, iterations=border_size) & ~is_transparent
    cleanup_mask = is_white & border_zone
    data[cleanup_mask, 3] = 0
    return Image.fromarray(data)


IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg")


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Remove Background")
        self.root.geometry("500x400")
        self.root.resizable(False, False)

        self.input_dir = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.border_size = tk.IntVar(value=3)
        self.white_threshold = tk.IntVar(value=240)

        self._build_ui()

    def _build_ui(self):
        pad = {"padx": 10, "pady": 5}

        # Input folder
        tk.Label(self.root, text="Input folder:").pack(anchor="w", **pad)
        f1 = tk.Frame(self.root)
        f1.pack(fill="x", **pad)
        tk.Entry(f1, textvariable=self.input_dir).pack(side="left", fill="x", expand=True)
        tk.Button(f1, text="Browse...", command=self._pick_input).pack(side="right", padx=(5, 0))

        # Output folder
        tk.Label(self.root, text="Output folder:").pack(anchor="w", **pad)
        f2 = tk.Frame(self.root)
        f2.pack(fill="x", **pad)
        tk.Entry(f2, textvariable=self.output_dir).pack(side="left", fill="x", expand=True)
        tk.Button(f2, text="Browse...", command=self._pick_output).pack(side="right", padx=(5, 0))

        # Settings
        sf = tk.LabelFrame(self.root, text="Edge cleanup settings")
        sf.pack(fill="x", **pad)
        tk.Label(sf, text="Border size (px):").grid(row=0, column=0, sticky="w", padx=5, pady=3)
        tk.Spinbox(sf, from_=1, to=20, textvariable=self.border_size, width=5).grid(row=0, column=1, padx=5)
        tk.Label(sf, text="White threshold:").grid(row=1, column=0, sticky="w", padx=5, pady=3)
        tk.Spinbox(sf, from_=180, to=255, textvariable=self.white_threshold, width=5).grid(row=1, column=1, padx=5)

        # Progress
        self.progress = ttk.Progressbar(self.root, mode="determinate")
        self.progress.pack(fill="x", **pad)

        self.status = tk.Label(self.root, text="Ready", anchor="w")
        self.status.pack(fill="x", **pad)

        # Run button
        self.run_btn = tk.Button(self.root, text="Remove Backgrounds", command=self._start, height=2)
        self.run_btn.pack(fill="x", **pad)

    def _pick_input(self):
        d = filedialog.askdirectory(title="Select input folder")
        if d:
            self.input_dir.set(d)
            if not self.output_dir.get():
                self.output_dir.set(os.path.join(d, "processed"))

    def _pick_output(self):
        d = filedialog.askdirectory(title="Select output folder")
        if d:
            self.output_dir.set(d)

    def _start(self):
        input_dir = self.input_dir.get()
        output_dir = self.output_dir.get()
        if not input_dir or not output_dir:
            self.status.config(text="Please select input and output folders.")
            return
        self.run_btn.config(state="disabled")
        threading.Thread(target=self._process, args=(input_dir, output_dir), daemon=True).start()

    def _process(self, input_dir, output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)

            files = [f for f in os.listdir(input_dir) if f.lower().endswith(IMAGE_EXTENSIONS)]
            if not files:
                self._update_status("No images found in input folder.")
                return

            self.root.after(0, lambda: self.progress.config(maximum=len(files), value=0))
            self._update_status("Loading model...")

            session = new_session("isnet-general-use")
            border = self.border_size.get()
            threshold = self.white_threshold.get()

            for i, filename in enumerate(files):
                self._update_status(f"Processing {i + 1}/{len(files)}: {filename}")

                img = Image.open(os.path.join(input_dir, filename))
                no_bg = remove(img, session=session)
                no_bg = clean_white_edges(no_bg, border_size=border, white_threshold=threshold)

                output_name = os.path.splitext(filename)[0] + ".png"
                no_bg.save(os.path.join(output_dir, output_name))

                self.root.after(0, lambda v=i + 1: self.progress.config(value=v))

            self._update_status(f"Done! {len(files)} images processed.")
        except Exception as e:
            self._update_status(f"Error: {e}")
        finally:
            self.root.after(0, lambda: self.run_btn.config(state="normal"))

    def _update_status(self, text):
        self.root.after(0, lambda: self.status.config(text=text))


if __name__ == "__main__":
    setup_model_path()
    root = tk.Tk()
    App(root)
    root.mainloop()
