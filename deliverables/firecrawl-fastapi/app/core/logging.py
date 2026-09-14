"""ตั้งค่า log แบบมีโครงสร้าง — JSON (failsafe เป็น console ถ้าไม่มี structlog)"""
import logging

from app.config.settings import Settings

# structlog เป็น optional — fallback เป็น stdlib logging
try:
    import structlog

    _HAS_STRUCTLOG = True
except Exception:  # pragma: no cover
    _HAS_STRUCTLOG = False


def setup_logging(settings: Settings) -> None:
    if _HAS_STRUCTLOG:
        processors = [
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
        ]
        if settings.log_format == "json":
            processors.append(structlog.processors.JSONRenderer(ensure_ascii=False))
        else:
            processors.append(structlog.dev.ConsoleRenderer())

        structlog.configure(
            processors=processors,
            wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )
    else:  # pragma: no cover
        logging.basicConfig(level=logging.INFO)


def get_logger(name: str = "firecrawl"):
    if _HAS_STRUCTLOG:
        return structlog.get_logger(name)
    return logging.getLogger(name)
