import logging
from app.config.logging import RequestIdFilter

logger = logging.getLogger("app")
logger.addFilter(RequestIdFilter())
