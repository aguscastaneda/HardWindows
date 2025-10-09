import tkinter as tk
from tkinter import ttk
from core.system_info import get_system_info

class SystemTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.tree = ttk.Treeview(self, columns=("clave", "valor"), show="headings")
        self.tree.heading("clave", text="Clave")
        self.tree.heading("valor", text="Valor")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        btn = ttk.Button(self, text="Actualizar", command=self.load_info)
        btn.pack(pady=5)

        self.load_info()

    def load_info(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        info = get_system_info()
        for k, v in info.items():
            self.tree.insert("", "end", values=(k, v))
