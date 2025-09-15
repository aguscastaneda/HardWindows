from tkinter import ttk, messagebox
from core.actions import is_admin, shutdown_now, restart_now

class ActionsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        lbl = ttk.Label(self, text="Acciones críticas del sistema", font=("Segoe UI", 12))
        lbl.pack(pady=10)

        btn_shutdown = ttk.Button(self, text="Apagar ahora", command=self._shutdown)
        btn_restart = ttk.Button(self, text="Reiniciar ahora", command=self._restart)

        btn_shutdown.pack(pady=5)
        btn_restart.pack(pady=5)

    def _check_admin(self) -> bool:
        if not is_admin():
            messagebox.showwarning("Permisos insuficientes",
                                   "Debe ejecutar el programa como administrador para esta acción")
            return False
        return True

    def _shutdown(self):
        if self._check_admin():
            shutdown_now()

    def _restart(self):
        if self._check_admin():
            restart_now()
