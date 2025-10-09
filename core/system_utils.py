import platform
import psutil
import subprocess
import os
from typing import Dict, Any, List, Optional

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
                                # Extraer posibles rutas para abrir o icono
                                try:
                                    install_location, _ = winreg.QueryValueEx(sk, "InstallLocation")
                                except OSError:
                                    install_location = None
                                try:
                                    display_icon, _ = winreg.QueryValueEx(sk, "DisplayIcon")
                                except OSError:
                                    display_icon = None
                                try:
                                    uninstall_string, _ = winreg.QueryValueEx(sk, "UninstallString")
                                except OSError:
                                    uninstall_string = None
                                if display_name:
                                    path_guess = ""
                                    # Preferir ejecutable en DisplayIcon, si existe
                                    if display_icon and os.path.exists(display_icon.split(",")[0].strip('"')):
                                        path_guess = display_icon.split(",")[0].strip('"')
                                    elif install_location and os.path.isdir(install_location):
                                        path_guess = install_location
                                    apps.append({
                                        "name": display_name,
                                        "version": display_version or "",
                                        "path": path_guess,
                                        "uninstall": uninstall_string or "",
                                    })
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
        key = (a.get("name", ""), a.get("version", ""))
        if key not in seen:
            seen.add(key)
            filtered.append(a)
    return filtered


# --- App control helpers (Windows best-effort) ---
def _is_windows() -> bool:
    return os.name == "nt"

def open_application(target: str) -> bool:
    """
    Abre una aplicación. Si 'target' es una ruta a un .exe la abre directamente.
    Si es un nombre, intenta buscar en PATH o en Program Files.
    """
    if not _is_windows():
        return False
    try:
        # Ruta directa
        if os.path.isfile(target):
            os.startfile(target)  # type: ignore[attr-defined]
            return True

        # Si llega "Nombre | C:\ruta\app.exe", extraer ruta si está presente
        if "|" in target:
            maybe_path = target.split("|")[-1].strip()
            if os.path.isfile(maybe_path):
                os.startfile(maybe_path)  # type: ignore[attr-defined]
                return True

        # Intento: usar start sin ventana
        subprocess.Popen(["cmd", "/c", "start", "", target], shell=True)
        return True
    except Exception:
        return False

def close_application(name_or_exe: str) -> bool:
    """
    Intenta cerrar una aplicación por nombre de proceso (sin ruta). Usa taskkill /IM.
    Acepta nombres como "notepad.exe" o "notepad".
    """
    if not _is_windows():
        return False
    try:
        exe = name_or_exe.strip().lower()
        if exe.endswith(".exe"):
            image = exe
        else:
            image = exe + ".exe"
        # /F fuerza; /T incluye procesos hijo
        result = subprocess.run(["taskkill", "/IM", image, "/F", "/T"], capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False

def uninstall_application(display_name: str) -> bool:
    """
    Intenta iniciar el desinstalador usando claves de registro Uninstall (Quiet/UninstallString).
    """
    if not _is_windows():
        return False
    try:
        import winreg  # type: ignore

        def _iter_uninstall_entries():
            paths = [
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
                (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            ]
            for root, path in paths:
                try:
                    with winreg.OpenKey(root, path) as key:
                        i = 0
                        while True:
                            try:
                                subkey_name = winreg.EnumKey(key, i)
                            except OSError:
                                break
                            i += 1
                            subpath = path + "\\" + subkey_name
                            yield root, subpath
                except Exception:
                    continue

        target_lower = display_name.strip().lower()
        for root, subpath in _iter_uninstall_entries():
            try:
                with winreg.OpenKey(root, subpath) as sk:
                    try:
                        dname, _ = winreg.QueryValueEx(sk, "DisplayName")
                    except OSError:
                        continue
                    if dname.strip().lower() != target_lower:
                        continue
                    # Preferir QuietUninstallString, luego UninstallString
                    uninstall_cmd = None
                    for key_name in ("QuietUninstallString", "UninstallString"):
                        try:
                            uninstall_cmd, _ = winreg.QueryValueEx(sk, key_name)
                            if uninstall_cmd:
                                break
                        except OSError:
                            continue
                    if not uninstall_cmd:
                        continue
                    # Ejecutar desinstalador
                    # Usar cmd /c para comandos con argumentos/espacios
                    subprocess.Popen(["cmd", "/c", uninstall_cmd], shell=True)
                    return True
            except Exception:
                continue
        return False
    except Exception:
        return False
