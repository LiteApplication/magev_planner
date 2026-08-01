import logging
import os


def setup_logging() -> None:
    """Send this package's log records to stderr.

    Neither uvicorn nor gunicorn configure the root logger, so without this our
    ``logger.info`` calls are dropped and only warnings reach the container log.
    """
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
