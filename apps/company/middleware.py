import os
import logging
import datetime
from logging.handlers import RotatingFileHandler
from threading import Lock
from django.utils.deprecation import MiddlewareMixin
# from django.utils.log import get_logger
from django.conf import settings

def should_skip_logging(path):
    """Skip logging for Swagger and static files."""
    return path.startswith("/swagger/") or path.startswith("/static/")

LOG_DIR = os.path.join(settings.BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Thread-safe singleton logger
_logger = None
_logger_lock = Lock()
_current_log_file = None


def get_log_file():
    """Returns today's log file path."""
    today = datetime.date.today().strftime("%Y-%m-%d")
    return os.path.join(LOG_DIR, f"{today}.log")

def is_swagger_request(path: str) -> bool:
    """Check if request is related to Swagger / ReDoc / OpenAPI."""
    return any([
        path.startswith("/swagger"),
        path.startswith("/redoc"),
        path.startswith("/openapi"),  # for drf-spectacular
    ])


def get_logger():
    """Thread-safe singleton logger with daily rotation and memory leak prevention"""
    global _logger, _current_log_file

    current_log_file = get_log_file()

    with _logger_lock:
        # Agar logger yo'q yoki kun o'zgargan bo'lsa
        if _logger is None or _current_log_file != current_log_file:
            # Eski handler'larni close qilish (file descriptor leak oldini olish)
            if _logger is not None:
                for handler in _logger.handlers[:]:
                    handler.close()
                    _logger.removeHandler(handler)

            # Yangi logger yaratish yoki mavjudini olish
            _logger = logging.getLogger("daily_logger")
            _logger.setLevel(logging.INFO)
            _logger.handlers.clear()  # Barcha eski handler'larni o'chirish
            _logger.propagate = False  # Root logger'ga o'tkazmaslik

            # RotatingFileHandler ishlatish (file size limit)
            handler = logging.handlers.RotatingFileHandler(
                current_log_file,
                maxBytes=50 * 1024 * 1024,  # 50MB
                backupCount=5,
                encoding='utf-8'
            )
            formatter = logging.Formatter("[{asctime}] {levelname} {message}", style="{")
            handler.setFormatter(formatter)
            _logger.addHandler(handler)

            _current_log_file = current_log_file

    return _logger


class ExceptionMiddleware(MiddlewareMixin):
    """Logs any unhandled exception."""

    def process_exception(self, request, exception):
        if is_swagger_request(request.path):
            return None  # skip swagger errors

        logger = get_logger()
        logger.exception(exception)
        return None


class RequestResponseLoggingMiddleware(MiddlewareMixin):
    """Logs all requests and responses, except Swagger and binary content."""

    MAX_LOG_LENGTH = 500  # limit logged content size

    def process_request(self, request):
        if should_skip_logging(request.path):
            return None

        logger = get_logger()
        try:
            body = request.body.decode(errors="ignore")
        except Exception:
            body = "<unreadable body>"

        if len(body) > self.MAX_LOG_LENGTH:
            body = body[:self.MAX_LOG_LENGTH] + "... [truncated]"

        logger.info(
            f"REQUEST | {request.method} {request.get_full_path()} | Body: {body}"
        )

    def process_response(self, request, response):
        if should_skip_logging(request.path):
            return response

        logger = get_logger()

        # Skip logging binary responses (images, pdfs, etc.)
        content_type = response.get("Content-Type", "")
        if any(ct in content_type for ct in ["image", "pdf", "octet-stream"]):
            content = f"<binary content skipped: {content_type}>"
        else:
            try:
                content = response.content.decode(errors="ignore")
            except Exception:
                content = "<unreadable content>"

            if len(content) > self.MAX_LOG_LENGTH:
                content = content[:self.MAX_LOG_LENGTH] + "... [truncated]"

        logger.info(
            f"RESPONSE | {request.method} {request.get_full_path()} | "
            f"Status: {response.status_code} | Content: {content}"
        )
        return response
