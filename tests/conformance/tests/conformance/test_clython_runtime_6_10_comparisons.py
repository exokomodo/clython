"""
Clython runtime tests for Section 6.10: Comparisons.

Tests ==, !=, <, <=, >, >=, is, is not, in, not in through the Clython binary.
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


# ---------------------------------------------------------------------------
# Equality and inequality
# ---------------------------------------------------------------------------

def test_equality_true():
    """== returns True for equal values."""
    out, err, rc = clython_run("print(1 == 1)")
    assert rc == 0
    assert out == "True"


def test_equality_false():
    """== returns False for unequal values."""
    out, err, rc = clython_run("print(1 == 2)")
    assert rc == 0
    assert out == "False"


def test_inequality_true():
    """!= returns True for unequal values."""
    out, err, rc = clython_run("print(1 != 2)")
    assert rc == 0
    assert out == "True"


def test_inequality_false():
    """!= returns False for equal values."""
    out, err, rc = clython_run("print(1 != 1)")
    assert rc == 0
    assert out == "False"


def test_int_float_equality():
    """Integer and float equality."""
    out, err, rc = clython_run("print(1 == 1.0)")
    assert rc == 0
    assert out == "True"


def test_string_equality():
    """String equality."""
    out, err, rc = clython_run("print('hello' == 'hello')")
    assert rc == 0
    assert out == "True"


def test_list_equality():
    """List equality is value-based."""
    out, err, rc = clython_run("print([1, 2, 3] == [1, 2, 3])")
    assert rc == 0
    assert out == "True"


# ---------------------------------------------------------------------------
# Ordering operators
# ---------------------------------------------------------------------------

def test_less_than_true():
    """< returns True."""
    out, err, rc = clython_run("print(3 < 5)")
    assert rc == 0
    assert out == "True"


def test_less_than_false():
    """< returns False."""
    out, err, rc = clython_run("print(5 < 3)")
    assert rc == 0
    assert out == "False"


def test_less_equal():
    """<= returns True for equal values."""
    out, err, rc = clython_run("print(3 <= 3)")
    assert rc == 0
    assert out == "True"


def test_greater_than():
    """> works correctly."""
    out, err, rc = clython_run("print(5 > 3)")
    assert rc == 0
    assert out == "True"


def test_greater_equal():
    """>= returns True for greater or equal."""
    out, err, rc = clython_run("print(5 >= 5)")
    assert rc == 0
    assert out == "True"


def test_string_ordering():
    """Strings are compared lexicographically."""
    out, err, rc = clython_run("print('abc' < 'abd')")
    assert rc == 0
    assert out == "True"


# ---------------------------------------------------------------------------
# Chained comparisons
# ---------------------------------------------------------------------------

def test_chained_comparison_true():
    """Chained comparison: 1 < 2 < 3."""
    out, err, rc = clython_run("print(1 < 2 < 3)")
    assert rc == 0
    assert out == "True"


def test_chained_comparison_false():
    """Chained comparison fails in the middle."""
    out, err, rc = clython_run("print(1 < 3 < 2)")
    assert rc == 0
    assert out == "False"


def test_chained_range_check():
    """Range check with chained comparison."""
    out, err, rc = clython_run("x = 5; print(0 <= x < 10)")
    assert rc == 0
    assert out == "True"


def test_chained_equality():
    """Chained equality: 1 == 1 == 1."""
    out, err, rc = clython_run("print(1 == 1 == 1)")
    assert rc == 0
    assert out == "True"


# ---------------------------------------------------------------------------
# Identity operators (is, is not)
# ---------------------------------------------------------------------------

def test_is_none():
    """x is None."""
    out, err, rc = clython_run("x = None; print(x is None)")
    assert rc == 0
    assert out == "True"


def test_is_not_none():
    """x is not None."""
    out, err, rc = clython_run("x = 42; print(x is not None)")
    assert rc == 0
    assert out == "True"


def test_is_same_object():
    """is True when both names refer to same object."""
    out, err, rc = clython_run("x = [1, 2]; y = x; print(x is y)")
    assert rc == 0
    assert out == "True"


def test_is_different_objects():
    """is False when two equal but distinct objects."""
    out, err, rc = clython_run("x = [1, 2]; y = [1, 2]; print(x is y)")
    assert rc == 0
    assert out == "False"


def test_is_true_singleton():
    """True is True."""
    out, err, rc = clython_run("print(True is True)")
    assert rc == 0
    assert out == "True"


# ---------------------------------------------------------------------------
# Membership operators (in, not in)
# ---------------------------------------------------------------------------

def test_in_list():
    """in returns True when item is in list."""
    out, err, rc = clython_run("print(2 in [1, 2, 3])")
    assert rc == 0
    assert out == "True"


def test_not_in_list():
    """not in returns True when item is absent."""
    out, err, rc = clython_run("print(5 not in [1, 2, 3])")
    assert rc == 0
    assert out == "True"


def test_in_string():
    """Substring membership test."""
    out, err, rc = clython_run("print('ell' in 'hello')")
    assert rc == 0
    assert out == "True"


def test_in_dict_checks_keys():
    """in tests dict keys."""
    out, err, rc = clython_run("d = {'a': 1}; print('a' in d)")
    assert rc == 0
    assert out == "True"


def test_in_set():
    """in works with sets."""
    out, err, rc = clython_run("print(3 in {1, 2, 3, 4})")
    assert rc == 0
    assert out == "True"


# ---------------------------------------------------------------------------
# Comparisons in context
# ---------------------------------------------------------------------------

def test_comparison_in_if():
    """Comparison used in if statement."""
    source = "x = 10\nif x > 5:\n    print('big')\nelse:\n    print('small')"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "big"


def test_comparison_result_assigned():
    """Comparison result assigned to variable."""
    out, err, rc = clython_run("result = 3 < 5; print(result)")
    assert rc == 0
    assert out == "True"


def test_ordering_incompatible_types_raises():
    """Ordering incompatible types should raise TypeError."""
    out, err, rc = clython_run("print('a' < 1)")
    assert rc != 0
