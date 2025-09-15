import platform
import psutil
import subprocess
import os
from typing import Dict, Any, List

def get_system_info() -> Dict[str, Any]:
    uname = platform.uname()
    info = {
        "Sistema": uname.system,
        "Nombre equipo": uname.node,
        "Versión": platform.version(),
        "Release": uname.release,
        "Arquitectura": platform.architecture()[0],
        "CPU (logical)": psutil.cpu_count(logical=True),
        "CPU (physical)": psutil.cpu_count(logical=False),
        "RAM total (GB)": round(psutil.virtual_memory().total / (1024**3), 2),
    }
    return info

def list_installed_apps() -> List[Dict[str, str]]:
    """
    Intenta obtener aplicaciones instaladas leyendo claves de registro Uninstall (Windows).
    Si falla devuelve lista vacía.
    """
    apps = []
    if os.name != "nt":
        return apps
    try:
        import winreg
        def _read_key(root, path):
            try:
                with winreg.OpenKey(root, path) as key:
                    i = 0
                    while True:
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                        except OSError:
                            break
                        subpath = path + "\\" + subkey_name
                        try:
                            with winreg.OpenKey(root, subpath) as sk:
                                try:
                                    display_name, _ = winreg.QueryValueEx(sk, "DisplayName")
                                except OSError:
                                    display_name = None
                                try:
                                    display_version, _ = winreg.QueryValueEx(sk, "DisplayVersion")
                                except OSError:
                                    display_version = None
                                if display_name:
                                    apps.append({"name": display_name, "version": display_version or ""})
                        except Exception:
                            pass
                        i += 1
            except Exception:
                pass

        paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        ]
        for root, path in paths:
            _read_key(root, path)
    except Exception:
        # Si no está winreg o falla, devolver vacío
        pass
    # Eliminar duplicados simples
    seen = set()
    filtered = []
    for a in apps:
        key = (a["name"], a.get("version", ""))
        if key not in seen:
            seen.add(key)
            filtered.append(a)
    return filtered
