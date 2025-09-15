import ctypes
import sys

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
