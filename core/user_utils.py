import subprocess
import shlex
from typing import Tuple, Optional, List
from .permissions import is_admin


def list_local_users() -> List[str]:
    """
    Lista usuarios locales usando 'net user' (Windows).
    """
    try:
        out = subprocess.check_output(["net", "user"], shell=True, text=True, stderr=subprocess.DEVNULL)
        lines = out.splitlines()
        users: List[str] = []
        in_list = False
        for line in lines:
            if "------" in line:
                in_list = True
                continue
            if in_list:
                text = line.strip()
                if not text:
                    # fin habitual de la lista
                    break
                lower = text.lower()
                # cortar si aparece mensaje final (multi-idioma)
                if lower.startswith("the command completed") or "comando" in lower and "complet" in lower:
                    break
                parts = line.split()
                users.extend(parts)
        # filtrar cuentas del sistema conocidas
        blacklist = {
            "defaultaccount", "defaultuser0", "guest", "invitado", "wdagutilityaccount", "$",
        }
        filtered: List[str] = []
        for u in users:
            uname = u.strip()
            if not uname:
                continue
            low = uname.lower()
            if low in blacklist:
                continue
            if low.endswith("$"):
                continue
            # Excluir tokens sueltos de mensajes
            if low in {"se", "ha", "completado", "el", "comando", "correctamente." , "correctamente"}:
                continue
            filtered.append(uname)
        return filtered
    except Exception:
        return []


def create_user(username: str, password: str) -> Tuple[bool, str]:
    if not is_admin():
        return False, "Se requieren permisos de administrador"
    try:
        cmd = f'net user "{username}" "{password}" /add'
        subprocess.check_call(cmd, shell=True)
        return True, "Usuario creado"
    except subprocess.CalledProcessError as e:
        return False, f"Error: {e}"


def delete_user(username: str) -> Tuple[bool, str]:
    if not is_admin():
        return False, "Se requieren permisos de administrador"
    try:
        cmd = f'net user "{username}" /delete'
        subprocess.check_call(cmd, shell=True)
        return True, "Usuario eliminado"
    except subprocess.CalledProcessError as e:
        return False, f"Error: {e}"


def change_password(username: str, new_password: str) -> Tuple[bool, str]:
    """Cambia la contraseña de un usuario local usando 'net user'."""
    if not is_admin():
        return False, "Se requieren permisos de administrador"
    if not username or not new_password:
        return False, "Usuario y nueva contraseña son obligatorios"
    try:
        cmd = f'net user "{username}" "{new_password}"'
        subprocess.check_call(cmd, shell=True)
        return True, "Contraseña actualizada"
    except subprocess.CalledProcessError as e:
        return False, f"Error: {e}"
