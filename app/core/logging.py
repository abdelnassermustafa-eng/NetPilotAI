from loguru import logger
import sys

from app.core.config import settings

def configure_logging() -> None:
    """
    Configure global logging for NetPilot AI using Loguru.
    """

    # Remove default handlers
    logger.remove()

    # Add stdout logging
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:"
            "<cyan>{function}</cyan>:"
            "<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
    )

# Run config immediately on import
configure_logging()
