import tkinter as tk
from tkinter import ttk
from core.monitor import cpu_percent, ram_percent

class MonitorTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.lbl_cpu = ttk.Label(self, text="CPU: -- %", font=("Segoe UI", 12))
        self.lbl_ram = ttk.Label(self, text="RAM: -- %", font=("Segoe UI", 12))

        self.lbl_cpu.pack(pady=10)
        self.lbl_ram.pack(pady=10)

        self.after(1000, self._tick)

    def _tick(self):
        self.lbl_cpu.config(text=f"CPU: {cpu_percent():.1f} %")
        self.lbl_ram.config(text=f"RAM: {ram_percent():.1f} %")
        self.after(1000, self._tick)
