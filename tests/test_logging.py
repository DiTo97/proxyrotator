import logging

import pytest

from saferequests.logging import (
    get_logger,
    get_verbosity,
    set_propagation,
    set_verbosity_debug,
    set_verbosity_error,
    set_verbosity_info,
    set_verbosity_warning,
)


@pytest.fixture
def logger() -> logging.Logger:
    return get_logger()


def test_set_verbosity_info(logger: logging.Logger):
    set_verbosity_info()

    assert logger.getEffectiveLevel() == logging.INFO
    assert get_verbosity() == logging.INFO


def test_set_verbosity_warning(logger: logging.Logger):
    set_verbosity_warning()

    assert logger.getEffectiveLevel() == logging.WARNING
    assert get_verbosity() == logging.WARNING


def test_set_verbosity_debug(logger: logging.Logger):
    set_verbosity_debug()

    assert logger.getEffectiveLevel() == logging.DEBUG
    assert get_verbosity() == logging.DEBUG


def test_set_verbosity_error(logger: logging.Logger):
    set_verbosity_error()

    assert logger.getEffectiveLevel() == logging.ERROR
    assert get_verbosity() == logging.ERROR


def test_set_propagation_enable(logger: logging.Logger):
    set_propagation(True)
    assert logger.propagate is True


def test_set_propagation_disable(logger: logging.Logger):
    set_propagation(False)
    assert logger.propagate is False
