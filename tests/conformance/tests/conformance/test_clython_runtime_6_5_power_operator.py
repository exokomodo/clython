"""
Clython runtime tests for Section 6.5: Power Operator.

Tests the ** operator through the Clython binary.
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
# Basic power operations
# ---------------------------------------------------------------------------

def test_int_power_int():
    """Integer raised to integer power."""
    out, err, rc = clython_run("print(2 ** 3)")
    assert rc == 0
    assert out == "8"


def test_power_zero():
    """Any number to the power of 0 is 1."""
    out, err, rc = clython_run("print(5 ** 0)")
    assert rc == 0
    assert out == "1"


def test_power_one():
    """Any number to the power of 1 is itself."""
    out, err, rc = clython_run("print(7 ** 1)")
    assert rc == 0
    assert out == "7"


def test_power_square():
    """Square of an integer."""
    out, err, rc = clython_run("print(9 ** 2)")
    assert rc == 0
    assert out == "81"


def test_power_large():
    """Large power — Python bigints."""
    out, err, rc = clython_run("print(2 ** 10)")
    assert rc == 0
    assert out == "1024"


def test_float_power():
    """Float raised to integer power."""
    out, err, rc = clython_run("print(2.0 ** 3)")
    assert rc == 0
    assert out == "8.0"


def test_float_exponent():
    """Integer raised to float power (square root)."""
    out, err, rc = clython_run("print(4 ** 0.5)")
    assert rc == 0
    assert out == "2.0"


# ---------------------------------------------------------------------------
# Right-associativity
# ---------------------------------------------------------------------------

def test_right_associative_simple():
    """2 ** 3 ** 2 should be 2 ** 9 = 512."""
    out, err, rc = clython_run("print(2 ** 3 ** 2)")
    assert rc == 0
    assert out == "512"


def test_left_grouped_power():
    """(2 ** 3) ** 2 should be 8 ** 2 = 64."""
    out, err, rc = clython_run("print((2 ** 3) ** 2)")
    assert rc == 0
    assert out == "64"


def test_right_associative_vars():
    """Right-associativity with variable assignment and check."""
    source = "a = 2; b = 3; c = 2; print(a ** b ** c)"
    out, err, rc = clython_run(source)
    assert rc == 0
    # 2 ** (3 ** 2) = 2 ** 9 = 512
    assert out == "512"


# ---------------------------------------------------------------------------
# Precedence
# ---------------------------------------------------------------------------

def test_power_before_unary_minus():
    """-2 ** 2 should be -(2**2) = -4, not (-2)**2 = 4."""
    out, err, rc = clython_run("print(-2 ** 2)")
    assert rc == 0
    assert out == "-4"


def test_power_before_addition():
    """Power is evaluated before addition."""
    out, err, rc = clython_run("print(2 + 3 ** 2)")
    assert rc == 0
    # 2 + 9 = 11
    assert out == "11"


def test_power_before_multiplication():
    """Power is evaluated before multiplication."""
    out, err, rc = clython_run("print(2 * 3 ** 2)")
    assert rc == 0
    # 2 * 9 = 18
    assert out == "18"


def test_parentheses_override_power_precedence():
    """Parentheses force addition before exponentiation."""
    out, err, rc = clython_run("print((2 + 3) ** 2)")
    assert rc == 0
    assert out == "25"


# ---------------------------------------------------------------------------
# Negative bases
# ---------------------------------------------------------------------------

def test_negative_base_even_exponent():
    """(-2) ** 2 = 4."""
    out, err, rc = clython_run("print((-2) ** 2)")
    assert rc == 0
    assert out == "4"


def test_negative_base_odd_exponent():
    """(-2) ** 3 = -8."""
    out, err, rc = clython_run("print((-2) ** 3)")
    assert rc == 0
    assert out == "-8"


# ---------------------------------------------------------------------------
# Builtin pow() cross-check
# ---------------------------------------------------------------------------

@pytest.mark.xfail(reason="pow() builtin is not defined in Clython")
def test_power_equals_pow_builtin():
    """a**b should equal pow(a, b)."""
    source = "print((3 ** 4) == pow(3, 4))"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True"


# ---------------------------------------------------------------------------
# Power in context
# ---------------------------------------------------------------------------

def test_power_in_list_comprehension():
    """Power operator inside a list comprehension."""
    out, err, rc = clython_run("print([x ** 2 for x in range(4)])")
    assert rc == 0
    assert out == "[0, 1, 4, 9]"


def test_power_accumulate_with_sum():
    """Sum of squares via list comprehension + sum."""
    out, err, rc = clython_run("print(sum(x ** 2 for x in range(4)))")
    assert rc == 0
    assert out == "14"


def test_power_in_function():
    """User-defined function using power."""
    source = "def square(n): return n ** 2\nprint(square(7))"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "49"


def test_power_modulo():
    """Modular exponentiation via chained ops."""
    out, err, rc = clython_run("print((2 ** 10) % 1000)")
    assert rc == 0
    assert out == "24"


def test_power_zero_base():
    """0 ** positive = 0."""
    out, err, rc = clython_run("print(0 ** 5)")
    assert rc == 0
    assert out == "0"


def test_complex_power():
    """Complex number raised to integer power."""
    out, err, rc = clython_run("print((1+1j) ** 2)")
    assert rc == 0
    # (1+1j)**2 ≈ 2j (Clython may include floating point noise)
    assert "2j" in out
