"""
Section 7.3: Assert Statements - Clython Runtime Test Suite

Tests that Clython actually executes assert statements correctly at runtime.
Uses subprocess-based execution via CLYTHON_BIN.
"""

import os
import subprocess
import pytest

CLYTHON_BIN = os.environ.get("CLYTHON_BIN")


def clython_run(source: str, *, timeout: int = 10):
    result = subprocess.run(
        [CLYTHON_BIN, "-c", source],
        capture_output=True, text=True, timeout=timeout
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode


pytestmark = pytest.mark.skipif(
    not CLYTHON_BIN, reason="CLYTHON_BIN not set — skipping Clython-specific tests"
)


def test_assert_true_passes():
    """assert True does not raise"""
    out, err, rc = clython_run("assert True\nprint('ok')")
    assert rc == 0
    assert out == "ok"


def test_assert_false_raises():
    """assert False raises AssertionError"""
    out, err, rc = clython_run(
        "try:\n"
        "    assert False\n"
        "except AssertionError:\n"
        "    print('caught')"
    )
    assert rc == 0
    assert out == "caught"


def test_assert_with_message():
    """assert False, 'msg' raises AssertionError with message"""
    out, err, rc = clython_run(
        "try:\n"
        "    assert False, 'my message'\n"
        "except AssertionError as e:\n"
        "    print(str(e))"
    )
    assert rc == 0
    assert out == "my message"


def test_assert_condition_true():
    """assert on true comparison passes"""
    out, err, rc = clython_run("assert 1 == 1\nprint('ok')")
    assert rc == 0
    assert out == "ok"


def test_assert_condition_false():
    """assert on false comparison raises"""
    out, err, rc = clython_run(
        "try:\n"
        "    assert 1 == 2\n"
        "except AssertionError:\n"
        "    print('raised')"
    )
    assert rc == 0
    assert out == "raised"


def test_assert_variable():
    """assert variable value"""
    out, err, rc = clython_run(
        "x = 5\n"
        "assert x > 0\n"
        "print('positive')"
    )
    assert rc == 0
    assert out == "positive"


def test_assert_zero_falsy():
    """assert 0 raises (0 is falsy)"""
    out, err, rc = clython_run(
        "try:\n"
        "    assert 0\n"
        "except AssertionError:\n"
        "    print('zero is falsy')"
    )
    assert rc == 0
    assert out == "zero is falsy"


def test_assert_empty_list_falsy():
    """assert [] raises (empty list is falsy)"""
    out, err, rc = clython_run(
        "try:\n"
        "    assert []\n"
        "except AssertionError:\n"
        "    print('empty list is falsy')"
    )
    assert rc == 0
    assert out == "empty list is falsy"


def test_assert_non_empty_truthy():
    """assert non-empty list passes"""
    out, err, rc = clython_run("assert [1, 2, 3]\nprint('truthy')")
    assert rc == 0
    assert out == "truthy"


def test_assert_string_message():
    """assert with string message from variable"""
    out, err, rc = clython_run(
        "msg = 'custom error'\n"
        "try:\n"
        "    assert False, msg\n"
        "except AssertionError as e:\n"
        "    print(e)"
    )
    assert rc == 0
    assert out == "custom error"


def test_assert_fstring_message():
    """assert with f-string message"""
    out, err, rc = clython_run(
        "x = 42\n"
        "try:\n"
        "    assert x < 0, f'expected negative, got {x}'\n"
        "except AssertionError as e:\n"
        "    print(e)"
    )
    assert rc == 0
    assert out == "expected negative, got 42"


def test_assert_function_call():
    """assert with function call result"""
    out, err, rc = clython_run(
        "def is_positive(x): return x > 0\n"
        "assert is_positive(5)\n"
        "print('ok')"
    )
    assert rc == 0
    assert out == "ok"


def test_assert_isinstance():
    """assert isinstance check"""
    out, err, rc = clython_run(
        "x = 42\n"
        "assert isinstance(x, int)\n"
        "print('is int')"
    )
    assert rc == 0
    assert out == "is int"


def test_assert_in_function():
    """assert statement inside function"""
    out, err, rc = clython_run(
        "def validate(x):\n"
        "    assert x >= 0, 'must be non-negative'\n"
        "    return x * 2\n"
        "print(validate(5))\n"
        "try:\n"
        "    validate(-1)\n"
        "except AssertionError as e:\n"
        "    print('caught:', e)"
    )
    assert rc == 0
    assert out == "10\ncaught: must be non-negative"


def test_assert_multiple():
    """Multiple assert statements"""
    out, err, rc = clython_run(
        "x = 5\n"
        "assert x > 0\n"
        "assert x < 10\n"
        "assert isinstance(x, int)\n"
        "print('all passed')"
    )
    assert rc == 0
    assert out == "all passed"


def test_assert_complex_condition():
    """assert with complex boolean condition"""
    out, err, rc = clython_run(
        "x, y = 3, 4\n"
        "assert x > 0 and y > 0\n"
        "assert x + y == 7\n"
        "print('ok')"
    )
    assert rc == 0
    assert out == "ok"


def test_assert_in_loop():
    """assert inside loop"""
    out, err, rc = clython_run(
        "for i in range(1, 5):\n"
        "    assert i > 0, f'{i} not positive'\n"
        "print('all positive')"
    )
    assert rc == 0
    assert out == "all positive"


def test_assert_not_in():
    """assert not in membership check"""
    out, err, rc = clython_run(
        "blacklist = ['bad', 'evil']\n"
        "word = 'good'\n"
        "assert word not in blacklist\n"
        "print('safe')"
    )
    assert rc == 0
    assert out == "safe"


def test_assert_none_check():
    """assert value is not None"""
    out, err, rc = clython_run(
        "result = 42\n"
        "assert result is not None\n"
        "print('not none')"
    )
    assert rc == 0
    assert out == "not none"


def test_assert_length():
    """assert len() check"""
    out, err, rc = clython_run(
        "items = [1, 2, 3]\n"
        "assert len(items) == 3\n"
        "print('length ok')"
    )
    assert rc == 0
    assert out == "length ok"


def test_assert_is_assertionerror_type():
    """AssertionError is subclass of Exception"""
    out, err, rc = clython_run(
        "try:\n"
        "    assert False, 'test'\n"
        "except Exception as e:\n"
        "    print(type(e).__name__)"
    )
    assert rc == 0
    assert out == "AssertionError"


def test_assert_no_message_empty_str():
    """assert False with no message: exception message is empty"""
    out, err, rc = clython_run(
        "try:\n"
        "    assert False\n"
        "except AssertionError as e:\n"
        "    print(repr(str(e)))"
    )
    assert rc == 0
    assert out == "''"


def test_assert_all_truthy():
    """assert all() on list of truthy values"""
    out, err, rc = clython_run(
        "items = [1, 2, 3, 4]\n"
        "assert all(x > 0 for x in items)\n"
        "print('all positive')"
    )
    assert rc == 0
    assert out == "all positive"
