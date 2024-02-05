import logging

from saferequests.logging import (
    _get_library_name,
    _get_library_root_logger,
    _set_library_root_logger,
    get_logger,
    get_verbosity,
    set_propagation,
    set_verbosity,
    set_verbosity_debug,
    set_verbosity_error,
    set_verbosity_info,
    set_verbosity_warning,
)


def test_get_logger_name():
    assert get_logger("testing").name == "testing"
    assert get_logger().name == _get_library_name()


def test_set_verbosity():
    set_verbosity(logging.CRITICAL)

    assert get_logger().getEffectiveLevel() == logging.CRITICAL
    assert get_verbosity() == logging.CRITICAL


def test_get_library_root_logger_name():
    assert _get_library_root_logger().name == _get_library_name()


def test_set_library_root_logger():
    _set_library_root_logger()

    assert get_logger().level == logging.WARNING
    assert isinstance(get_logger().handlers[0], logging.StreamHandler)


def test_set_verbosity_info():
    set_verbosity_info()

    assert get_logger().getEffectiveLevel() == logging.INFO
    assert get_verbosity() == logging.INFO


def test_set_verbosity_warning():
    set_verbosity_warning()

    assert get_logger().getEffectiveLevel() == logging.WARNING
    assert get_verbosity() == logging.WARNING


def test_set_verbosity_debug():
    set_verbosity_debug()

    assert get_logger().getEffectiveLevel() == logging.DEBUG
    assert get_verbosity() == logging.DEBUG


def test_set_verbosity_error():
    set_verbosity_error()

    assert get_logger().getEffectiveLevel() == logging.ERROR
    assert get_verbosity() == logging.ERROR


def test_set_propagation_enable():
    set_propagation(True)
    assert get_logger().propagate is True


def test_set_propagation_disable():
    set_propagation(False)
    assert get_logger().propagate is False
