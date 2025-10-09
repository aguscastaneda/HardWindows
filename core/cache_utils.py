import os
import shutil
from typing import Tuple

def _safe_remove_file(path: str) -> Tuple[int, int]:
    try:
        size = os.path.getsize(path)
    except Exception:
        size = 0
    try:
        os.remove(path)
        return 1, size
    except Exception:
        return 0, 0

def _safe_remove_dir(path: str) -> Tuple[int, int]:
    deleted = 0
    freed = 0
    try:
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                d, f = _safe_remove_file(os.path.join(root, name))
                deleted += d
                freed += f
            for name in dirs:
                try:
                    os.rmdir(os.path.join(root, name))
                except Exception:
                    pass
        try:
            os.rmdir(path)
        except Exception:
            pass
    except Exception:
        pass
    return deleted, freed

def clear_temp() -> Tuple[int, int]:
    """
    Elimina archivos temporales comunes de Windows.
    Retorna (cantidad_eliminados, bytes_liberados).
    Requiere permisos elevados para rutas del sistema como C:\\Windows\\Temp y Prefetch.
    """
    deleted_total = 0
    freed_total = 0

    candidates = []
    # Temp del usuario
    user_temp = os.getenv("TEMP") or os.getenv("TMP")
    if user_temp:
        candidates.append(user_temp)
    # Temp del sistema
    candidates.append(r"C:\\Windows\\Temp")
    # Prefetch
    candidates.append(r"C:\\Windows\\Prefetch")


    for path in candidates:
        if not path or not os.path.exists(path):
            continue
        if os.path.isfile(path):
            d, f = _safe_remove_file(path)
            deleted_total += d
            freed_total += f
            continue
        try:
            for name in os.listdir(path):
                full = os.path.join(path, name)
                if os.path.isdir(full):
                    d, f = _safe_remove_dir(full)
                else:
                    d, f = _safe_remove_file(full)
                deleted_total += d
                freed_total += f
        except Exception:
            continue

    return deleted_total, freed_total
