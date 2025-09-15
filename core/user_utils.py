import subprocess
import shlex
from typing import Tuple, Optional
from .permissions import is_admin


def list_local_users() -> list:
    """
    Lista usuarios locales usando 'net user' (Windows).
    """
    try:
        out = subprocess.check_output(["net", "user"], shell=True, text=True, stderr=subprocess.DEVNULL)
        lines = out.splitlines()
        users = []
        in_list = False
        for line in lines:
            if "------" in line:
                in_list = True
                continue
            if in_list:
                if line.strip() == "":
                    break
                parts = line.split()
                users.extend(parts)
        return users
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
