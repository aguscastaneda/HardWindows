import os
import ctypes

def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def shutdown_now():
    os.system("shutdown /s /t 0")

def restart_now():
    os.system("shutdown /r /t 0")
    