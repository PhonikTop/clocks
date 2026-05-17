import structlog
import sys
from structlog import contextvars
from structlog.dev import ConsoleRenderer
from structlog.processors import (
    TimeStamper,
    add_log_level,
    format_exc_info,
    JSONRenderer,
)
from structlog.stdlib import ProcessorFormatter, add_logger_name

def build_logging(debug: bool = True):
    foreign_pre_chain = [
        structlog.contextvars.merge_contextvars,
        add_log_level,
        TimeStamper(fmt="iso", utc=True),
        format_exc_info,
    ]

    if not debug:
        renderer = JSONRenderer()
        root_level = "INFO"
    else:
        renderer = ConsoleRenderer(colors=True)
        root_level = "DEBUG"

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "struct": {
                "()": ProcessorFormatter,
                "processor": renderer,
                "foreign_pre_chain": foreign_pre_chain,
            },
        },
        "handlers": {
            "default": {
                "level": root_level,
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
                "formatter": "struct",
            },
        },
        "root": {
            "handlers": ["default"],
            "level": root_level,
        },
        "loggers": {
            "django": {"handlers": ["default"], "level": root_level, "propagate": False},
            "django.db.backends": {"handlers": ["default"], "level": "WARNING", "propagate": False},
            "django.template": {"handlers": ["default"], "level": "WARNING", "propagate": False},
            "asgiref": {"handlers": ["default"], "level": "WARNING", "propagate": False},
            "django.request": {"handlers": ["default"], "level": "ERROR", "propagate": False},
            "uvicorn": {"handlers": ["default"], "level": "INFO", "propagate": False},
            "uvicorn.error": {"handlers": ["default"], "level": "INFO", "propagate": False},
            "uvicorn.access": {"handlers": ["default"], "level": "WARN", "propagate": False},
            "channels": {"handlers": ["default"], "level": "INFO", "propagate": False},
        },
    }

