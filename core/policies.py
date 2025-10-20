import sys
import subprocess
from typing import Optional, Dict, List, Tuple
import ctypes
import time


def _is_windows() -> bool:
    return sys.platform == "win32"


def _open_or_create_subkey(root, path):
    import winreg
    try:
        return winreg.CreateKeyEx(root, path, 0, winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE)
    except OSError:
        return winreg.OpenKey(root, path, 0, winreg.KEY_QUERY_VALUE)


POLICY_MAP: Dict[str, Dict[str, str]] = {
    "DisableTaskMgr": {"subkey": r"System", "value": "DisableTaskMgr"},
    "NoControlPanel": {"subkey": r"Explorer", "value": "NoControlPanel"},
    "NoRun": {"subkey": r"Explorer", "value": "NoRun"},
    "DisableRegistryTools": {"subkey": r"System", "value": "DisableRegistryTools"},
    "NoWinKeys": {"subkey": r"Explorer", "value": "NoWinKeys"},
}


def get_policy_value(name: str) -> Optional[int]:
    """
    Lee el valor de política desde HKLM. Devuelve 0/1 o None si no se puede leer.
    """
    if not _is_windows():
        return None
    try:
        import winreg
        mapping = POLICY_MAP.get(name)
        if not mapping:
            return None
        full_path = r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\" + mapping["subkey"]
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, full_path, 0, winreg.KEY_QUERY_VALUE) as key:
                val, _ = winreg.QueryValueEx(key, mapping["value"])
                return int(val)
        except OSError:
            return 0
    except Exception:
        return None


def set_policy_value(name: str, blocked: bool) -> bool:
    """
    Escribe 1 (bloqueado) o 0 (permitido) en HKLM para la política dada.
    Requiere privilegios de administrador.
    """
    if not _is_windows():
        return False
    try:
        import winreg
        mapping = POLICY_MAP.get(name)
        if not mapping:
            return False
        full_path = r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\" + mapping["subkey"]
        with _open_or_create_subkey(winreg.HKEY_LOCAL_MACHINE, full_path) as key:
            winreg.SetValueEx(key, mapping["value"], 0, winreg.REG_DWORD, 1 if blocked else 0)
        return True
    except Exception:
        return False


def reset_all_to_allowed() -> bool:
    """Pone todas las políticas gestionadas en 0 (permitido)."""
    if not _is_windows():
        return False
    ok = True
    for name in POLICY_MAP.keys():
        if not set_policy_value(name, blocked=False):
            ok = False
    return ok


def get_all_policies() -> Dict[str, Optional[int]]:
    """Devuelve un dict con el estado actual (0/1/None) de cada política."""
    return {name: get_policy_value(name) for name in POLICY_MAP.keys()}


# ----------------------- Políticas por usuario (HKU\\<SID>) -----------------------

def _wmic_user_sid_map() -> Dict[str, str]:
    """
    Devuelve un mapa {usuario: SID} usando 'wmic useraccount get name,sid'.
    Solo usuarios locales.
    """
    if not _is_windows():
        return {}
    try:
        out = subprocess.check_output(["wmic", "useraccount", "get", "name,sid"], text=True, stderr=subprocess.DEVNULL)
        mapping: Dict[str, str] = {}
        for line in out.splitlines():
            line = line.strip()
            if not line or line.lower().startswith("name"):
                continue
            # Formato: Name               SID
            parts = [p for p in line.split(" ") if p]
            if len(parts) >= 2:
                name = parts[0]
                sid = parts[-1]
                mapping[name] = sid
        return mapping
    except Exception:
        return {}


def list_user_sids(users: Optional[List[str]] = None) -> List[Tuple[str, str]]:
    """
    Lista pares (usuario, SID). Si 'users' es provisto, filtra por esos usuarios.
    """
    mapping = _wmic_user_sid_map()
    out: List[Tuple[str, str]] = []
    if users:
        for u in users:
            sid = mapping.get(u)
            if sid:
                out.append((u, sid))
    else:
        out = sorted(mapping.items(), key=lambda kv: kv[0].lower())
    return out


def _get_profile_path_for_sid(sid: str) -> Optional[str]:
    """Obtiene la ruta del perfil (LocalPath) para un SID usando WMI."""
    if not _is_windows():
        return None
    try:
        # wmic path win32_userprofile where sid='S-1-5-21-...' get localpath /value
        cmd = [
            "wmic",
            "path",
            "win32_userprofile",
            "where",
            f"sid='{sid}'",
            "get",
            "localpath",
            "/value",
        ]
        out = subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
        for line in out.splitlines():
            line = line.strip()
            if line.lower().startswith("localpath="):
                val = line.split("=", 1)[1].strip()
                return val if val else None
        return None
    except Exception:
        return None


def _is_hku_sid_loaded(sid: str) -> bool:
    """Verifica si HKU\\<sid> está montado."""
    if not _is_windows():
        return False
    try:
        # reg query HKU\<SID>
        subprocess.check_output(["reg", "query", f"HKU\\{sid}"], stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False


def _ensure_hku_sid_loaded(sid: str) -> bool:
    """Carga el hive de usuario (NTUSER.DAT) en HKU\\<SID> si no está montado."""
    if not _is_windows():
        return False
    if _is_hku_sid_loaded(sid):
        return True
    profile = _get_profile_path_for_sid(sid)
    if not profile:
        return False
    ntuser = profile.rstrip("\\/") + "\\NTUSER.DAT"
    try:
        # reg load HKU\<SID> "<profile>\NTUSER.DAT"
        subprocess.check_call(["reg", "load", f"HKU\\{sid}", ntuser], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False


def get_policy_value_for_sid(name: str, sid: str) -> Optional[int]:
    """
    Lee la política desde HKU\\<SID>. Devuelve 0/1 o None si no puede leerse.
    """
    if not _is_windows():
        return None
    try:
        import winreg
        mapping = POLICY_MAP.get(name)
        if not mapping:
            return None
        full_path = sid + r"\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\" + mapping["subkey"]
        try:
            with winreg.OpenKey(winreg.HKEY_USERS, full_path, 0, winreg.KEY_QUERY_VALUE) as key:
                val, _ = winreg.QueryValueEx(key, mapping["value"])
                return int(val)
        except OSError:
            # Intentar cargar hive y reintentar una vez
            if _ensure_hku_sid_loaded(sid):
                try:
                    with winreg.OpenKey(winreg.HKEY_USERS, full_path, 0, winreg.KEY_QUERY_VALUE) as key:
                        val, _ = winreg.QueryValueEx(key, mapping["value"])
                        return int(val)
                except OSError:
                    return 0
            return 0
    except Exception:
        return None


def set_policy_value_for_sid(name: str, blocked: bool, sid: str) -> bool:
    """
    Escribe 1/0 en HKU\\<SID> para la política dada. Requiere admin.
    """
    if not _is_windows():
        return False
    try:
        import winreg
        mapping = POLICY_MAP.get(name)
        if not mapping:
            return False
        full_path = sid + r"\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\" + mapping["subkey"]
        try:
            key = winreg.CreateKeyEx(winreg.HKEY_USERS, full_path, 0, winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE)
        except OSError:
            # Si falla, intentar cargar hive y reintentar
            if _ensure_hku_sid_loaded(sid):
                key = winreg.CreateKeyEx(winreg.HKEY_USERS, full_path, 0, winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE)
            else:
                key = winreg.OpenKey(winreg.HKEY_USERS, full_path, 0, winreg.KEY_SET_VALUE)
        with key:
            winreg.SetValueEx(key, mapping["value"], 0, winreg.REG_DWORD, 1 if blocked else 0)
        return True
    except Exception:
        return False


def get_all_policies_for_sid(sid: str) -> Dict[str, Optional[int]]:
    return {name: get_policy_value_for_sid(name, sid) for name in POLICY_MAP.keys()}


# ----------------------- Aplicación inmediata de cambios -----------------------

def _broadcast_setting_change() -> None:
    try:
        HWND_BROADCAST = 0xFFFF
        WM_SETTINGCHANGE = 0x1A
        SMTO_NORMAL = 0x0
        # Notificar cambios de políticas
        for param in ("Policy", "Explorer"):
            ctypes.windll.user32.SendMessageTimeoutW(
                HWND_BROADCAST,
                WM_SETTINGCHANGE,
                0,
                ctypes.c_wchar_p(param),
                SMTO_NORMAL,
                100,
                None,
            )
    except Exception:
        pass


def _restart_explorer() -> bool:
    try:
        # Cerrar explorer para la sesión actual y relanzar
        subprocess.run(["taskkill", "/F", "/IM", "explorer.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(0.5)
        subprocess.Popen(["explorer.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False


def apply_policy_changes(force_refresh: bool = True, restart_shell: bool = False) -> None:
    """
    Intenta que las políticas surtan efecto sin reiniciar: broadcast de cambios y
    opcionalmente reinicio de Explorer.
    """
    _broadcast_setting_change()
    if restart_shell:
        _restart_explorer()

