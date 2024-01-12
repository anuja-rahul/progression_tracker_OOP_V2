"""
#!/usr/bin/env python3
backend info logging
progression_tracker_OOP_V2/datalogger.py
"""
import os
import logging
import datetime as dt


class DataLogger:
    """
    Records and log any type of requests specified by the user
    levels = (debug, info, warning, error, critical)
    """

    log_path = f"{os.getcwd()}/logs"
    levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }

    def __init__(self, name: str = "DataLogger", propagate: bool = False, level: str = "DEBUG"):

        DataLogger.init_env()
        DataLogger.set_logger(DataLogger.levels[level.upper()])
        self.__today = dt.datetime.today()
        self.filename = f"{DataLogger.log_path}/{self.__today.day:02d}-{self.__today.month:02d}-{self.__today.year}.log"
        self.logger = logging.getLogger(name)
        self.logger.propagate = propagate   # Disables logger from displaying in console
        self.file_handler = logging.FileHandler(self.filename)
        self.formatter = logging.Formatter("%(asctime)s: %(name)s - %(levelname)s - %(message)s")
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)

    @classmethod
    def init_env(cls):
        try:
            os.mkdir(DataLogger.log_path)
        except FileExistsError:
            pass

    @staticmethod
    def set_logger(level) -> None:
        """Set the logging security level to DEBUG."""
        for handler in logging.root.handlers:
            logging.root.removeHandler(handler)
        logging.basicConfig(level=level)

    def log_debug(self, info: str) -> None:
        """log a debug log."""
        self.logger.debug(info)

    def log_info(self, info: str) -> None:
        """log an info log."""
        self.logger.info(info)

    def log_warning(self, info: str) -> None:
        """log a warning log."""
        self.logger.warning(info)

    def log_error(self, info: str) -> None:
        """log an error log."""
        self.logger.error(info)

    def log_critical(self, info: str) -> None:
        """log a critical log."""
        self.logger.critical(info)

    def __repr__(self):
        return f"[logger={self.logger.name}, propagate={self.logger.propagate}, path={self.filename}]"
