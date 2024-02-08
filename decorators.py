import time
from typing import Callable
from python_datalogger import DataLogger


def logger(function: Callable):
    default_logger = DataLogger(name="DefaultLogger", level="ERROR", propagate=True)
    method_name = function.__name__

    def wrapper(*args, **kwargs):
        try:
            result = function(*args, **kwargs)
            return result
        except Exception as exception:
            default_logger.log_error(f"{method_name} - {exception}")
            del default_logger

    return wrapper


def timer(function: Callable):
    method_name = function.__name__

    def wrapper(*args, **kwargs):
        before = time.time()
        result = function(*args, **kwargs)
        after = time.time()
        print(f"\n{method_name} - took {str(after - before)[:9]} seconds to execute.\n")
        return result
    return wrapper
