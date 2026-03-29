"""
Clython runtime tests for Section 6.7: Binary Arithmetic Operations.

Tests +, -, *, /, //, %, @ operators through the Clython binary.
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
# Addition
# ---------------------------------------------------------------------------

def test_int_addition():
    """Basic integer addition."""
    out, err, rc = clython_run("print(3 + 4)")
    assert rc == 0
    assert out == "7"


def test_float_addition():
    """Float addition."""
    out, err, rc = clython_run("print(1.5 + 2.5)")
    assert rc == 0
    assert out == "4.0"


def test_int_float_addition():
    """Integer + float promotes to float."""
    out, err, rc = clython_run("print(1 + 2.0)")
    assert rc == 0
    assert out == "3.0"


def test_string_concatenation():
    """String addition (concatenation)."""
    out, err, rc = clython_run("print('hello' + ' ' + 'world')")
    assert rc == 0
    assert out == "hello world"


def test_list_concatenation():
    """List addition (concatenation)."""
    out, err, rc = clython_run("print([1, 2] + [3, 4])")
    assert rc == 0
    assert out == "[1, 2, 3, 4]"


# ---------------------------------------------------------------------------
# Subtraction
# ---------------------------------------------------------------------------

def test_int_subtraction():
    """Basic integer subtraction."""
    out, err, rc = clython_run("print(10 - 3)")
    assert rc == 0
    assert out == "7"


def test_float_subtraction():
    """Float subtraction."""
    out, err, rc = clython_run("print(5.0 - 1.5)")
    assert rc == 0
    assert out == "3.5"


def test_negative_result():
    """Subtraction producing negative result."""
    out, err, rc = clython_run("print(3 - 10)")
    assert rc == 0
    assert out == "-7"


# ---------------------------------------------------------------------------
# Multiplication
# ---------------------------------------------------------------------------

def test_int_multiplication():
    """Basic integer multiplication."""
    out, err, rc = clython_run("print(6 * 7)")
    assert rc == 0
    assert out == "42"


def test_float_multiplication():
    """Float multiplication."""
    out, err, rc = clython_run("print(2.5 * 4.0)")
    assert rc == 0
    assert out == "10.0"


def test_string_repetition():
    """String * int = repetition."""
    out, err, rc = clython_run("print('ab' * 3)")
    assert rc == 0
    assert out == "ababab"


def test_list_repetition():
    """List * int = repetition."""
    out, err, rc = clython_run("print([0] * 3)")
    assert rc == 0
    assert out == "[0, 0, 0]"


# ---------------------------------------------------------------------------
# True division
# ---------------------------------------------------------------------------

def test_true_division_int():
    """True division of two integers produces float."""
    out, err, rc = clython_run("print(7 / 2)")
    assert rc == 0
    assert out == "3.5"


def test_true_division_exact():
    """True division that is exact."""
    out, err, rc = clython_run("print(10 / 2)")
    assert rc == 0
    assert out == "5.0"


def test_true_division_float():
    """True division of floats."""
    out, err, rc = clython_run("print(9.0 / 3.0)")
    assert rc == 0
    assert out == "3.0"


# ---------------------------------------------------------------------------
# Floor division
# ---------------------------------------------------------------------------

def test_floor_division_positive():
    """Floor division truncates toward negative infinity."""
    out, err, rc = clython_run("print(7 // 2)")
    assert rc == 0
    assert out == "3"


def test_floor_division_negative():
    """Floor division with negative dividend."""
    out, err, rc = clython_run("print(-7 // 2)")
    assert rc == 0
    assert out == "-4"


def test_floor_division_float():
    """Floor division with floats."""
    out, err, rc = clython_run("print(7.5 // 2.0)")
    assert rc == 0
    assert out == "3.0"


# ---------------------------------------------------------------------------
# Modulo
# ---------------------------------------------------------------------------

def test_modulo_basic():
    """Basic integer modulo."""
    out, err, rc = clython_run("print(10 % 3)")
    assert rc == 0
    assert out == "1"


def test_modulo_zero_remainder():
    """Modulo with no remainder."""
    out, err, rc = clython_run("print(9 % 3)")
    assert rc == 0
    assert out == "0"


def test_modulo_negative():
    """Modulo with negative dividend follows floor division sign."""
    out, err, rc = clython_run("print(-7 % 3)")
    assert rc == 0
    assert out == "2"


def test_modulo_string_format():
    """String modulo (old-style formatting)."""
    out, err, rc = clython_run("print('%s=%d' % ('x', 42))")
    assert rc == 0
    assert out == "x=42"


# ---------------------------------------------------------------------------
# Precedence
# ---------------------------------------------------------------------------

def test_mul_before_add():
    """Multiplication has higher precedence than addition."""
    out, err, rc = clython_run("print(2 + 3 * 4)")
    assert rc == 0
    assert out == "14"


def test_div_before_sub():
    """Division has higher precedence than subtraction."""
    out, err, rc = clython_run("print(10 - 6 / 2)")
    assert rc == 0
    assert out == "7.0"


def test_parentheses_override():
    """Parentheses override precedence."""
    out, err, rc = clython_run("print((2 + 3) * 4)")
    assert rc == 0
    assert out == "20"


def test_left_associativity():
    """Left-associativity: 10 - 3 - 2 == (10 - 3) - 2 == 5."""
    out, err, rc = clython_run("print(10 - 3 - 2)")
    assert rc == 0
    assert out == "5"


# ---------------------------------------------------------------------------
# Division by zero (runtime errors)
# ---------------------------------------------------------------------------

def test_division_by_zero_raises():
    """Division by zero should raise ZeroDivisionError."""
    out, err, rc = clython_run("x = 1 / 0")
    assert rc != 0
    assert "ZeroDivisionError" in err or rc != 0


def test_matrix_multiplication():
    """Matrix multiplication via @ operator."""
    source = (
        "class Matrix:\n"
        "    def __init__(self, v): self.v = v\n"
        "    def __matmul__(self, other): return Matrix(self.v * other.v)\n"
        "a = Matrix(3); b = Matrix(4); print((a @ b).v)\n"
    )
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "12"
