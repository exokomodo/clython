"""
Clython runtime tests for Section 6.6: Unary Arithmetic and Bitwise Operations.

Tests +, -, and ~ operators through the Clython binary.
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
# Unary plus
# ---------------------------------------------------------------------------

def test_unary_plus_positive_int():
    """Unary plus on a positive integer."""
    out, err, rc = clython_run("print(+5)")
    assert rc == 0
    assert out == "5"


def test_unary_plus_negative_int():
    """Unary plus on a negative integer is a no-op."""
    out, err, rc = clython_run("x = -3; print(+x)")
    assert rc == 0
    assert out == "-3"


def test_unary_plus_float():
    """Unary plus on a float."""
    out, err, rc = clython_run("print(+3.14)")
    assert rc == 0
    assert out == "3.14"


def test_unary_plus_zero():
    """Unary plus on zero."""
    out, err, rc = clython_run("print(+0)")
    assert rc == 0
    assert out == "0"


# ---------------------------------------------------------------------------
# Unary minus
# ---------------------------------------------------------------------------

def test_unary_minus_positive_int():
    """Unary minus negates a positive integer."""
    out, err, rc = clython_run("print(-5)")
    assert rc == 0
    assert out == "-5"


def test_unary_minus_negative_int():
    """Unary minus of a negative integer gives positive."""
    out, err, rc = clython_run("x = -3; print(-x)")
    assert rc == 0
    assert out == "3"


def test_unary_minus_float():
    """Unary minus on a float."""
    out, err, rc = clython_run("print(-2.5)")
    assert rc == 0
    assert out == "-2.5"


def test_unary_minus_zero():
    """Unary minus of zero is zero."""
    out, err, rc = clython_run("print(-0)")
    assert rc == 0
    assert out == "0"


def test_double_unary_minus():
    """Double unary minus cancels out."""
    out, err, rc = clython_run("print(--5)")
    assert rc == 0
    assert out == "5"


# ---------------------------------------------------------------------------
# Bitwise NOT (~)
# ---------------------------------------------------------------------------

def test_bitwise_not_zero():
    """~0 == -1."""
    out, err, rc = clython_run("print(~0)")
    assert rc == 0
    assert out == "-1"


def test_bitwise_not_one():
    """~1 == -2."""
    out, err, rc = clython_run("print(~1)")
    assert rc == 0
    assert out == "-2"


def test_bitwise_not_positive():
    """~n == -(n+1)."""
    out, err, rc = clython_run("print(~7)")
    assert rc == 0
    assert out == "-8"


def test_bitwise_not_negative():
    """~(-1) == 0."""
    out, err, rc = clython_run("print(~(-1))")
    assert rc == 0
    assert out == "0"


def test_double_bitwise_not():
    """~~x == x."""
    out, err, rc = clython_run("x = 42; print(~~x)")
    assert rc == 0
    assert out == "42"


def test_bitwise_not_with_mask():
    """~x & 0xFF should give byte complement."""
    out, err, rc = clython_run("print(~0xF0 & 0xFF)")
    assert rc == 0
    assert out == "15"


# ---------------------------------------------------------------------------
# Precedence with power operator
# ---------------------------------------------------------------------------

def test_unary_minus_power_precedence():
    """-2 ** 2 is -(2**2) = -4."""
    out, err, rc = clython_run("print(-2 ** 2)")
    assert rc == 0
    assert out == "-4"


def test_unary_minus_parenthesized_base():
    """(-2) ** 2 is 4."""
    out, err, rc = clython_run("print((-2) ** 2)")
    assert rc == 0
    assert out == "4"


# ---------------------------------------------------------------------------
# Unary in expressions
# ---------------------------------------------------------------------------

def test_unary_minus_in_arithmetic():
    """Unary minus combined with addition."""
    out, err, rc = clython_run("print(-3 + 10)")
    assert rc == 0
    assert out == "7"


def test_unary_minus_in_list_comprehension():
    """Negation in a list comprehension."""
    out, err, rc = clython_run("print([-x for x in [1, 2, 3]])")
    assert rc == 0
    assert out == "[-1, -2, -3]"


def test_unary_not_in_expression():
    """~x used to invert bits in an expression."""
    out, err, rc = clython_run("x = 0b1010; print(~x & 0b1111)")
    assert rc == 0
    # ~0b1010 = ...11110101, & 0b1111 = 0b0101 = 5
    assert out == "5"


def test_unary_plus_in_function():
    """Unary plus returned from function."""
    source = "def f(n): return +n\nprint(f(-7))"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "-7"


def test_mixed_unary_operators():
    """Mixing + and - unary operators."""
    out, err, rc = clython_run("x = 4; print(-+x)")
    assert rc == 0
    assert out == "-4"


def test_unary_minus_bool():
    """-True == -1."""
    out, err, rc = clython_run("print(-True)")
    assert rc == 0
    assert out == "-1"


def test_bitwise_not_bool():
    """~True == -2."""
    out, err, rc = clython_run("print(~True)")
    assert rc == 0
    assert out == "-2"
