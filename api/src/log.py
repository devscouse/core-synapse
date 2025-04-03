import logging
from colorlog import ColoredFormatter


def logging_config():
    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    formatter = ColoredFormatter(
        "%(log_color)s%(levelname)-8s %(asctime)s%(reset)s [%(name)s.%(funcName)s()] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        reset=True,
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)

    # Loggers that have their own handler are reset to use our handler for consistency
    for logger_name in ("uvicorn.error", "uvicorn.access", "uvicorn", "fastapi"):
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()
        logger.addHandler(console_handler)
