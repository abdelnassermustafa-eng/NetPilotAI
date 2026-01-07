import logging
from collections import deque
from datetime import datetime

# Fixed-size in-memory log buffer
LOG_BUFFER_SIZE = 500
memory_logs = deque(maxlen=LOG_BUFFER_SIZE)

class MemoryLogHandler(logging.Handler):
    def emit(self, record: logging.LogRecord):
        try:
            memory_logs.append({
                "timestamp": datetime.utcnow().isoformat(),
                "level": record.levelname,
                "message": record.getMessage(),
                "logger": record.name,
            })
        except Exception:
            # Never break logging
            pass
