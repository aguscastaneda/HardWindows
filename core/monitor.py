import psutil
from collections import deque
from typing import Deque, Dict, Any

def cpu_percent() -> float:
    return psutil.cpu_percent(interval=None)

def ram_percent() -> float:
    return psutil.virtual_memory().percent

class Monitor:
    def __init__(self, history_max: int = 120):
        self.history_max = history_max
        self.cpu_hist: Deque[float] = deque(maxlen=history_max)
        self.ram_hist: Deque[float] = deque(maxlen=history_max)
        self.disk_hist: Deque[float] = deque(maxlen=history_max)
        self.net_sent_hist: Deque[float] = deque(maxlen=history_max)
        self.net_recv_hist: Deque[float] = deque(maxlen=history_max)
        self._last_net = psutil.net_io_counters()

    def sample(self) -> None:
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent
        # En Windows, la raíz válida suele ser la unidad del cwd; psutil.disk_usage('.') es más seguro
        try:
            disk = psutil.disk_usage('.') .percent
        except Exception:
            disk = 0.0

        net = psutil.net_io_counters()
        sent = (net.bytes_sent - self._last_net.bytes_sent) / 1024.0
        recv = (net.bytes_recv - self._last_net.bytes_recv) / 1024.0
        self._last_net = net

        self.cpu_hist.append(cpu)
        self.ram_hist.append(ram)
        self.disk_hist.append(disk)
        self.net_sent_hist.append(sent)
        self.net_recv_hist.append(recv)

    def snapshot(self) -> Dict[str, Any]:
        return {
            "cpu": self.cpu_hist[-1] if self.cpu_hist else 0.0,
            "ram": self.ram_hist[-1] if self.ram_hist else 0.0,
            "disk": self.disk_hist[-1] if self.disk_hist else 0.0,
            "net_sent_kb": self.net_sent_hist[-1] if self.net_sent_hist else 0.0,
            "net_recv_kb": self.net_recv_hist[-1] if self.net_recv_hist else 0.0,
        }
