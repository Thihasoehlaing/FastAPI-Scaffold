import logging
import sys


def setup_logging():
    handler = logging.StreamHandler(sys.stdout)
    fmt = "%(asctime)s %(levelname)s %(name)s [req=%(request_id)s] %(message)s"
    formatter = logging.Formatter(fmt=fmt, datefmt="%Y-%m-%dT%H:%M:%S%z")
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    # Avoid duplicate handlers on reload
    if not any(isinstance(h, logging.StreamHandler) for h in root.handlers):
        root.addHandler(handler)


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        # Provide default when no request context
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        return True
