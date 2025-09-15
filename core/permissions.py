import ctypes
import sys
import os
import getpass

def is_admin() -> bool:
    """
    Devuelve True si la ejecución tiene privilegios de administrador en Windows.
    """
    if sys.platform != "win32":
        return False
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def get_current_user() -> str:
    """
    Devuelve el nombre del usuario actual de forma robusta.
    Intenta os.getlogin(), si falla usa getpass.getuser().
    """
    try:
        return os.getlogin()
    except Exception:
        try:
            return getpass.getuser()
        except Exception:
            return "desconocido"


def lock_screen() -> bool:
    """Bloquea la pantalla en Windows."""
    if sys.platform != "win32":
        return False
    try:
        ctypes.windll.user32.LockWorkStation()
        return True
    except Exception:
        return False


def logoff() -> bool:
    """Cierra la sesión del usuario actual en Windows."""
    if sys.platform != "win32":
        return False
    try:
        import subprocess
        # shutdown /l cierra sesión
        subprocess.Popen(["shutdown", "/l"])
        return True
    except Exception:
        return False
