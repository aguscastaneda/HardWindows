import psutil
from typing import List, Dict, Any, Optional

def list_processes() -> List[Dict[str, Any]]:
    out = []
    for proc in psutil.process_iter(attrs=["pid", "name"]):
        try:
            info = proc.info
            out.append({"pid": info["pid"], "name": info.get("name", "")})
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return sorted(out, key=lambda p: p["pid"])

def kill_process(pid: int) -> Optional[str]:
    try:
        proc = psutil.Process(pid)
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except psutil.TimeoutExpired:
            proc.kill()
        return None
    except psutil.NoSuchProcess:
        return "Proceso inexistente"
    except psutil.AccessDenied:
        return "Acceso denegado. Ejecutar como administrador"
    except Exception as e:
        return f"Error: {e}"
