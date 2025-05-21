import logging
import sys
from colorama import Fore, Style, init as colorama_init

colorama_init(autoreset=True)

class CustomFormatter(logging.Formatter):
    format_str = (
        f"%(asctime)s - {Style.BRIGHT}%(levelname)s{Style.NORMAL} from "
        f"%(name)s: %(message)s {Style.BRIGHT}(%(filename)s:%(lineno)d){Style.NORMAL}"
    )

    FORMATS = {
        logging.DEBUG: Fore.BLUE + format_str + Style.RESET_ALL,
        logging.INFO: Fore.GREEN + format_str + Style.RESET_ALL,
        logging.WARNING: Fore.YELLOW + format_str + Style.RESET_ALL,
        logging.ERROR: Fore.RED + format_str + Style.RESET_ALL,
        logging.CRITICAL: Style.BRIGHT + Fore.RED + format_str + Style.RESET_ALL,
    }

    def format(self, record: logging.LogRecord):
        log_fmt = self.FORMATS.get(record.levelno, self.format_str)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

class CustomLogger(logging.Logger):


    def __init__(self, name: str, level: int = logging.DEBUG):
        super().__init__(name, level)

        self.setLevel(level)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(CustomFormatter())

        self.addHandler(console_handler)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": CustomFormatter,
        },
        "access": {
            "()": CustomFormatter,
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
            'level': 'DEBUG',

        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            'level': 'DEBUG',
        },
    },
    "loggers": {
        "uvicorn": {"handlers": ["default"], "level": "DEBUG", "propagate": False},
        "uvicorn.error": {"level": "INFO"},
        "uvicorn.access": {"handlers": ["access"], "level": "DEBUG", "propagate": False},
    },
}