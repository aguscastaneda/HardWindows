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
        pass

    seen = set()
    filtered = []
    for a in apps:
        key = (a.get("name", ""), a.get("version", ""))
        if key not in seen:
            seen.add(key)
            filtered.append(a)
    return filtered



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

        if os.path.isfile(target):
            os.startfile(target) 
            return True

        if "|" in target:
            maybe_path = target.split("|")[-1].strip()
            if os.path.isfile(maybe_path):
                os.startfile(maybe_path) 
                return True

        subprocess.Popen(["cmd", "/c", "start", "", target], shell=True)
        return True
    except Exception:
        return False

def close_application(name_or_exe: str) -> bool:
    """
    Cierra una aplicación por nombre de proceso (sin ruta) o ejecutable.
    1) Intenta con taskkill /IM.
    2) Si falla, hace fallback buscando procesos con psutil por nombre y termina.
    """
    if not _is_windows():
        return False
    try:
        exe = name_or_exe.strip().lower()
        if exe.endswith(".exe"):
            image = exe
        else:
            image = exe + ".exe"

        # Intento 1: taskkill por imagen
        result = subprocess.run(["taskkill", "/IM", image, "/F", "/T"], capture_output=True, text=True)
        if result.returncode == 0:
            return True

        # Intento 2: psutil – matar por coincidencia de nombre
        killed_any = False
        for proc in psutil.process_iter(attrs=["pid", "name"]):
            try:
                pname = (proc.info.get("name") or "").strip().lower()
                if pname == image or pname == exe or pname.endswith("\\" + image):
                    try:
                        proc.terminate()
                        try:
                            proc.wait(timeout=2)
                        except psutil.TimeoutExpired:
                            proc.kill()
                        killed_any = True
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return killed_any
    except Exception:
        return False

def uninstall_application(display_name: str) -> bool:
    """
    Intenta iniciar el desinstalador usando claves de registro Uninstall (Quiet/UninstallString).
    """
    if not _is_windows():
        return False
    try:
        import winreg

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

                    subprocess.Popen(["cmd", "/c", uninstall_cmd], shell=True)
                    return True
            except Exception:
                continue
        return False
    except Exception:
        return False
