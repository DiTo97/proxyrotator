"""A minimal utility module for centralized logging"""
import logging
from functools import lru_cache


@lru_cache(maxsize=1)
def _get_library_name() -> str:
    return __name__.split(".", maxsplit=1)[0]


def _get_library_root_logger() -> logging.Logger:
    return logging.getLogger(_get_library_name())


def _set_library_root_logger() -> None:
    library_root_logger = _get_library_root_logger()

    library_root_logger.addHandler(logging.StreamHandler())
    library_root_logger.setLevel(logging.WARNING)


def get_logger(name: str | None = None) -> logging.Logger:
    return logging.getLogger(name or _get_library_name())


def get_verbosity() -> int:
    return _get_library_root_logger().getEffectiveLevel()


def set_verbosity(verbosity: int) -> None:
    _get_library_root_logger().setLevel(verbosity)


def set_verbosity_info() -> None:
    set_verbosity(logging.INFO)


def set_verbosity_warning() -> None:
    set_verbosity(logging.WARNING)


def set_verbosity_debug() -> None:
    set_verbosity(logging.DEBUG)


def set_verbosity_error() -> None:
    set_verbosity(logging.ERROR)


def set_propagation(enable: bool) -> None:
    _get_library_root_logger().propagate = enable


_set_library_root_logger()
