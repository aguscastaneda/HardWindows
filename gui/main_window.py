import tkinter as tk
from tkinter import ttk
from gui.system_tab import SystemTab
from gui.monitor_tab import MonitorTab
from gui.processes_tab import ProcessesTab
from gui.actions_tab import ActionsTab

APP_TITLE = "Gestor de Sistema Windows"

def run_app():
    root = tk.Tk()
    root.title(APP_TITLE)
    root.geometry("900x600")

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    tab_system = SystemTab(notebook)
    tab_monitor = MonitorTab(notebook)
    tab_processes = ProcessesTab(notebook)
    tab_actions = ActionsTab(notebook)

    notebook.add(tab_system, text="Resumen del sistema")
    notebook.add(tab_monitor, text="Monitor en vivo")
    notebook.add(tab_processes, text="Procesos")
    notebook.add(tab_actions, text="Acciones")

    root.mainloop()
