import logging

from colorama import Fore, Back, Style


class CustomFormatter(logging.Formatter):

    format_str = f"%(asctime)s - {Style.BRIGHT}%(levelname)s{Style.NORMAL} from %(name)s: %(message)s {Style.BRIGHT}(%(filename)s:%(lineno)d){Style.NORMAL}"

    FORMATS = {
        logging.DEBUG: Fore.BLUE + format_str + Style.RESET_ALL,
        logging.INFO: Fore.GREEN + format_str + Style.RESET_ALL,
        logging.WARNING: Fore.YELLOW + format_str + Style.RESET_ALL,
        logging.ERROR: Fore.RED + format_str + Style.RESET_ALL,
        logging.CRITICAL: Style.BRIGHT + Fore.RED + format_str + Style.RESET_ALL,
    }

    def format(self, record: logging.LogRecord):
        # print(record)
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class LogHijack(logging.Filter):
    def filter(self, record: logging.LogRecord):
        print(record)
        logging.getLogger(__name__).handle(record)
        return False


def get_logger(level: int = logging.DEBUG):
    for log in (
        logging.getLogger("uvicorn"),
        logging.getLogger("uvicorn.error"),
        logging.getLogger("uvicorn.access"),
        logging.getLogger("uvicorn.asgi"),
    ):
        log.addFilter(LogHijack())
    logger = logging.getLogger(__name__)
    logger.setLevel(level)

    # create console handler with a higher log level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(CustomFormatter())

    logger.addHandler(console_handler)

    return logger
