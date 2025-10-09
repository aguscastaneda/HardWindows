import platform
import psutil
from typing import Dict, Any

def get_system_info() -> Dict[str, Any]:
    uname = platform.uname()
    info = {
        "sistema": uname.system,
        "version": platform.version(),
        "release": uname.release,
        "arquitectura": platform.architecture()[0],
        "equipo": uname.node,
        "procesadores_logicos": psutil.cpu_count(logical=True),
        "procesadores_fisicos": psutil.cpu_count(logical=False),
        "ram_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
    }
    return info
