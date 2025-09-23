import sys
from typing import Optional, Dict


def _is_windows() -> bool:
    return sys.platform == "win32"


def _open_or_create_subkey(root, path):
    import winreg
    try:
        return winreg.CreateKeyEx(root, path, 0, winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE)
    except OSError:
        # Fallback read-only open (will fail on set)
        return winreg.OpenKey(root, path, 0, winreg.KEY_QUERY_VALUE)


POLICY_MAP: Dict[str, Dict[str, str]] = {
    # key_name: {"subkey": relative path under Policies, "value": value name}
    "DisableTaskMgr": {"subkey": r"System", "value": "DisableTaskMgr"},
    "NoControlPanel": {"subkey": r"Explorer", "value": "NoControlPanel"},
    "NoRun": {"subkey": r"Explorer", "value": "NoRun"},
    "DisableRegistryTools": {"subkey": r"System", "value": "DisableRegistryTools"},
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


