import logging
import sys
from typing import Any

from loguru import logger

from app.infra.config import LoggingConfig


class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_back and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


class Logger:
    def __init__(self, console_config: LoggingConfig):
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO)
        logger.remove()
        # Requests bind trace_id via TraceIdMiddleware; everything else logs "-".
        logger.configure(extra={"trace_id": "-"})

        logger.add(
            sys.stdout,
            format=console_config.format,
            level=console_config.level,
            enqueue=console_config.enqueue,
            backtrace=console_config.backtrace,
            diagnose=console_config.diagnose,
        )

        loggers = ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi", "asyncio", "starlette")
        for logger_name in loggers:
            logging_logger = logging.getLogger(logger_name)
            logging_logger.handlers = []
            logging_logger.propagate = True

    @staticmethod
    def get_logger() -> Any:
        return logger
