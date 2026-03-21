"""Local development mock for the rpi-rgb-led-matrix display.

Opens a scaled-up Tkinter window that mirrors what the LED panels would show.
The main rotation loop runs normally — this just replaces SetImage().
"""

import queue
import threading
import tkinter as tk
from PIL import Image, ImageTk

SCALE = 8  # 64×64 → 512×512 preview window


class MockMatrix:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self._queue = queue.Queue(maxsize=1)
        self._ready = threading.Event()
        self._thread = threading.Thread(target=self._run_tk, daemon=True)
        self._thread.start()
        self._ready.wait()  # Block until Tk window is up

    def SetImage(self, image):
        scaled = image.resize((self.cols * SCALE, self.rows * SCALE), Image.NEAREST)
        try:
            self._queue.put_nowait(scaled)
        except queue.Full:
            pass  # Drop frame if display is busy

    def _run_tk(self):
        self._root = tk.Tk()
        self._root.title("FF LED Scoreboard — Local Preview")
        self._root.resizable(False, False)
        self._root.configure(bg="black")

        blank = Image.new("RGB", (self.cols * SCALE, self.rows * SCALE), (0, 0, 0))
        self._photo = ImageTk.PhotoImage(blank)
        self._label = tk.Label(self._root, image=self._photo, bg="black", bd=0)
        self._label.pack()

        self._ready.set()
        self._root.after(50, self._poll)
        self._root.mainloop()

    def _poll(self):
        try:
            img = self._queue.get_nowait()
            self._photo = ImageTk.PhotoImage(img)
            self._label.configure(image=self._photo)
        except queue.Empty:
            pass
        self._root.after(50, self._poll)
