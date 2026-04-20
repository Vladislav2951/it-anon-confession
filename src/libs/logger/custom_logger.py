from enum import Enum
import logging

from colorama import Fore, Style, init


init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    LEVEL_COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        # Сохранение предыдущего формата
        orig_levelname = record.levelname
        orig_msg = record.msg

        color = self.LEVEL_COLORS.get(record.levelno, Fore.WHITE)
        record.levelname = f"{color}{orig_levelname:<8}{Style.RESET_ALL}"
        result = super().format(record)

        # Возвращение оригинального формата
        record.levelname = orig_levelname
        record.msg = orig_msg

        return result


def test_logging():
    """
    Checks the operation of configured logging: levels, colors, and error output.
    """
    logger = logging.getLogger(__name__)

    logger.info("=== Starting Logging Test ===")

    logger.debug("Example of DEBUG log")
    logger.info("Example of INFO log")
    logger.warning("Example of WARNING log")
    logger.error("Example of ERROR log")
    logger.critical("Example of CRITICAL log")

    try:
        result = 10 / 0
    except ZeroDivisionError:
        logger.exception("Exception handling test: Attempted division by zero!")

    logger.info("=== Logging Test Complete ===")


def setup_logging(log_level):
    format = "%(asctime)s %(levelname)-8s %(message)s"
    formatter = ColoredFormatter(format, datefmt="%d-%m-%Y %H:%M:%S")

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    intercept_loggers = [
        None,
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
        # "sqlalchemy.engine",
        "fastapi",
    ]

    for logger_name in intercept_loggers:
        logger = logging.getLogger(logger_name)
        logger.handlers = []  # Очистка старых обработчиков, чтобы логи не дублировались
        logger.addHandler(handler)
        logger.setLevel(log_level)
        logger.propagate = False  # Запрет передачи логов выше по иерархии
