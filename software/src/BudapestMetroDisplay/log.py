#  MIT License
#
#  Copyright (c) 2024 [fullname]
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"),
#  to deal in the Software without restriction, including without limitation
#  the rights to use, copy, modify, merge, publish, distribute, sublicense,
#  and/or sell copies of the Software, and to permit persons to whom
#  the Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included
#  in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#  ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#  OTHER DEALINGS IN THE SOFTWARE.

from datetime import datetime
# Define logger globally
import logging
from logging.handlers import RotatingFileHandler
import os

from BudapestMetroDisplay.main import settings

logger = logging.getLogger(__name__)

# Define the custom log level
TRACE_LEVEL = 5


def add_logging_level(level_name, level_num, method_name=None):
    """
    Comprehensively adds a new logging level to the `logging` module and the
    currently configured logging class.

    `level_name` becomes an attribute of the `logging` module with the value
    `level_num`. `method_name` becomes a convenience method for both `logging`
    itself and the class returned by `logging.getLoggerClass()` (usually just
    `logging.Logger`). If `method_name` is not specified, `level_name.lower()` is
    used.

    To avoid accidental clobberings of existing attributes, this method will
    raise an `AttributeError` if the level name is already an attribute of the
    `logging` module or if the method name is already present

    Example
    -------
    >>> add_logging_level('TRACE', logging.DEBUG - 5)
    >>> logging.getLogger(__name__).setLevel("TRACE")
    >>> logging.getLogger(__name__).trace('that worked')
    >>> logging.trace('so did this')
    >>> logging.TRACE
    5

    """
    if not method_name:
        method_name = level_name.lower()

    if hasattr(logging, level_name):
        raise AttributeError("{} already defined in logging module".format(level_name))
    if hasattr(logging, method_name):
        raise AttributeError("{} already defined in logging module".format(method_name))
    if hasattr(logging.getLoggerClass(), method_name):
        raise AttributeError("{} already defined in logger class".format(method_name))

    # This method was inspired by the answers to Stack Overflow post
    # http://stackoverflow.com/q/2183233/2988730, especially
    # http://stackoverflow.com/a/13638084/2988730
    def log_for_level(self, message, *args, **kwargs):
        if self.isEnabledFor(level_num):
            self._log(level_num, message, args, **kwargs)

    def log_to_root(message, *args, **kwargs):
        logging.log(level_num, message, *args, **kwargs)

    logging.addLevelName(level_num, level_name)
    setattr(logging, level_name, level_num)
    setattr(logging.getLoggerClass(), method_name, log_for_level)
    setattr(logging, method_name, log_to_root)


def setup_logging(parser):
    global logger

    # Define custom log level
    add_logging_level("TRACE", logging.DEBUG - 5)

    # Create logger instance
    logger = logging.getLogger()

    # Parse command-line arguments
    args = parser.parse_args()
    if args.trace:
        logger.setLevel(logging.TRACE)  # type: ignore[attr-defined]
    elif args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # Create a rotating file handler
    file_handler = RotatingFileHandler(
        os.path.join(settings.log.path, "application.log"),
        maxBytes=5 * 1024 * 1024,  # 5 MB file size limit
        backupCount=10,  # Keep up to 10 backup log files
    )

    # Create a rotating file handler
    file_handler_error = RotatingFileHandler(
        os.path.join(settings.log.path, "application_error.log"),
        maxBytes=5 * 1024 * 1024,  # 5 MB file size limit
        backupCount=5,  # Keep up to 5 backup log files
    )

    # Create a temporary logger for adding the start entry
    start_logger = logging.getLogger("start_logger")
    start_logger.setLevel(logging.INFO)  # Temporarily allow INFO for this logger
    # Add handler to the logger
    start_logger.addHandler(file_handler)
    start_logger.addHandler(file_handler_error)
    # Add a custom log entry at program start to separate runs
    separator = "=" * 50
    start_logger.info(separator)
    start_logger.info(f"Program started at {datetime.now()}")
    start_logger.info(separator)
    # Remove the handler after logging the start messages
    start_logger.removeHandler(file_handler)
    start_logger.removeHandler(file_handler_error)

    # Capture only WARNING and higher
    file_handler_error.setLevel(logging.WARNING)

    # Create a console handler (prints to stdout)
    console_handler = logging.StreamHandler()

    # Create a logging format
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(threadName)s: %(message)s"
    )
    file_handler.setFormatter(formatter)
    file_handler_error.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to the logger (without using basicConfig())
    if not logger.hasHandlers():  # Prevent adding handlers multiple times
        logger.addHandler(file_handler)
        logger.addHandler(file_handler_error)
        logger.addHandler(console_handler)

    if logger.getEffectiveLevel() == logging.TRACE:  # type: ignore[attr-defined]
        logger.trace("Trace level logging enabled")  # type: ignore[attr-defined]
    elif logger.getEffectiveLevel() == logging.DEBUG:
        logger.debug("Debug level logging enabled")

    return logger


def log_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        # Don't log KeyboardInterrupt exceptions
        logger.info("Program interrupted by user, exiting...")
        return
    # Log the exception details
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
