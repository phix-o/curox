import sys

from loguru import logger

def configure_for_dev():
    """Configures the logger to be more verbose"""

    logger.remove()
    logger.add(sys.stdout, colorize=True, backtrace=False, diagnose=True)
    logger.add(sys.stderr, colorize=True, backtrace=False, diagnose=True, level="ERROR")
    logger.info("Logger configured for dev")


def configure_for_prod():
    """Configures the logger to be less verbose"""

    logger.remove()
    logger.add(sys.stdout, colorize=True, backtrace=False, diagnose=False)
    logger.add(
        sys.stderr, colorize=True, backtrace=False, diagnose=False, level="ERROR"
    )
    logger.info("Logger configured for prod")

