import logging
import os

try:
    import watchtower
    HAS_WATCHTOWER = True
except Exception:
    HAS_WATCHTOWER = False


def get_logger(name: str, log_group: str):
    """
    Returns a logger that writes to CloudWatch Logs if available,
    otherwise falls back to standard console logging.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Prevent duplicate handlers if reloaded
    if logger.handlers:
    if not any(isinstance(h, MemoryLogHandler) for h in logger.handlers):
        logger.addHandler(MemoryLogHandler())
        logger.setLevel(logging.INFO)
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    if HAS_WATCHTOWER:
        try:
            handler = watchtower.CloudWatchLogHandler(
                log_group=log_group,
                stream_name=os.getenv("HOSTNAME", "netpilot-backend"),
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        except Exception:
            # Fallback to console if CloudWatch fails
            console = logging.StreamHandler()
            console.setFormatter(formatter)
            logger.addHandler(console)
    else:
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        logger.addHandler(console)

    return logger

# ===============================
# In-memory log buffer (Phase 5.1)
# ===============================
try:
    from app.core.memory_log_handler import MemoryLogHandler

    _memory_handler = MemoryLogHandler()
    _memory_handler.setLevel(logging.INFO)

    logging.getLogger().addHandler(_memory_handler)
except Exception:
    pass
