import os
import time
import psutil
from datetime import datetime

_process = psutil.Process(os.getpid())
_start_time = time.time()


def get_runtime_metrics() -> dict:
    """
    Safe, read-only runtime metrics.
    Computed on demand.
    No background state mutation.
    """

    cpu_percent = _process.cpu_percent(interval=0.0)
    mem_info = _process.memory_info()

    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "uptime_seconds": int(time.time() - _start_time),
        "cpu_percent": round(cpu_percent, 2),
        "memory_mb": round(mem_info.rss / (1024 * 1024), 2),
        "pid": _process.pid,
    }

