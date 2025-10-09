import tkinter as tk
from tkinter import ttk, messagebox
from core.processes import list_processes, kill_process

class ProcessesTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", padx=10, pady=5)

        btn_refresh = ttk.Button(toolbar, text="Actualizar", command=self.load)
        btn_kill = ttk.Button(toolbar, text="Finalizar proceso", command=self.kill_selected)
        btn_refresh.pack(side="left", padx=5)
        btn_kill.pack(side="left", padx=5)

        self.tree = ttk.Treeview(self, columns=("pid", "name"), show="headings", height=18)
        self.tree.heading("pid", text="PID")
        self.tree.heading("name", text="Nombre")
        self.tree.column("pid", width=100, anchor="center")
        self.tree.column("name", width=500, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.load()

    def load(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for p in list_processes():
            self.tree.insert("", "end", values=(p["pid"], p["name"]))

    def kill_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Seleccione un proceso")
            return
        pid = int(self.tree.item(sel[0], "values")[0])
        err = kill_process(pid)
        if err:
            messagebox.showerror("Error", err)
        else:
            messagebox.showinfo("Listo", f"Proceso {pid} finalizado")
            self.load()
