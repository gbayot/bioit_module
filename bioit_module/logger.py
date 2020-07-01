import logging


def build_logger(filename, level="INFO"):
    root_logger = logging.getLogger()

    if root_logger.handlers:
        return root_logger

    log_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)-5.5s]  %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    root_logger.setLevel(level)

    file_handler = logging.FileHandler(filename)
    file_handler.setFormatter(log_formatter)
    root_logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)

    return root_logger
