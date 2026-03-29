"""
Clython runtime tests for Section 6.8: Shifting Operations.

Tests << and >> operators through the Clython binary.
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
# Left shift
# ---------------------------------------------------------------------------

def test_left_shift_by_one():
    """Left shift by 1 doubles the value."""
    out, err, rc = clython_run("print(1 << 1)")
    assert rc == 0
    assert out == "2"


def test_left_shift_by_three():
    """Left shift by 3 multiplies by 8."""
    out, err, rc = clython_run("print(1 << 3)")
    assert rc == 0
    assert out == "8"


def test_left_shift_integer():
    """Left shift of an integer."""
    out, err, rc = clython_run("print(5 << 2)")
    assert rc == 0
    # 5 * 4 = 20
    assert out == "20"


def test_left_shift_zero():
    """Left shift by 0 is identity."""
    out, err, rc = clython_run("print(42 << 0)")
    assert rc == 0
    assert out == "42"


def test_left_shift_large():
    """Large left shift (Python supports arbitrary precision)."""
    out, err, rc = clython_run("print(1 << 10)")
    assert rc == 0
    assert out == "1024"


# ---------------------------------------------------------------------------
# Right shift
# ---------------------------------------------------------------------------

def test_right_shift_by_one():
    """Right shift by 1 halves the value."""
    out, err, rc = clython_run("print(8 >> 1)")
    assert rc == 0
    assert out == "4"


def test_right_shift_by_two():
    """Right shift by 2 divides by 4."""
    out, err, rc = clython_run("print(20 >> 2)")
    assert rc == 0
    assert out == "5"


def test_right_shift_odd():
    """Right shift of odd number truncates."""
    out, err, rc = clython_run("print(7 >> 1)")
    assert rc == 0
    assert out == "3"


def test_right_shift_zero():
    """Right shift by 0 is identity."""
    out, err, rc = clython_run("print(42 >> 0)")
    assert rc == 0
    assert out == "42"


def test_right_shift_to_zero():
    """Sufficient right shift reduces to zero."""
    out, err, rc = clython_run("print(1 >> 5)")
    assert rc == 0
    assert out == "0"


# ---------------------------------------------------------------------------
# Chained shifts
# ---------------------------------------------------------------------------

def test_chained_left_shifts():
    """Chained left shifts: 1 << 2 << 3 is (1<<2)<<3 = 4<<3 = 32."""
    out, err, rc = clython_run("print(1 << 2 << 3)")
    assert rc == 0
    assert out == "32"


def test_chained_right_shifts():
    """Chained right shifts: 64 >> 2 >> 1 is (64>>2)>>1 = 16>>1 = 8."""
    out, err, rc = clython_run("print(64 >> 2 >> 1)")
    assert rc == 0
    assert out == "8"


def test_mixed_shifts():
    """Mixed shifts: 4 << 2 >> 1 is (4<<2)>>1 = 16>>1 = 8."""
    out, err, rc = clython_run("print(4 << 2 >> 1)")
    assert rc == 0
    assert out == "8"


# ---------------------------------------------------------------------------
# Precedence
# ---------------------------------------------------------------------------

def test_shift_vs_addition():
    """Addition has higher precedence than shift: 2 + 3 << 1 = (2+3)<<1 = 10."""
    out, err, rc = clython_run("print(2 + 3 << 1)")
    assert rc == 0
    assert out == "10"


def test_shift_vs_comparison():
    """Shift has higher precedence than comparison."""
    out, err, rc = clython_run("print((1 << 3) > 4)")
    assert rc == 0
    assert out == "True"


def test_parentheses_override_shift_precedence():
    """Parentheses alter shift grouping."""
    out, err, rc = clython_run("print(2 << (1 + 2))")
    assert rc == 0
    # 2 << 3 = 16
    assert out == "16"


# ---------------------------------------------------------------------------
# Bit manipulation patterns
# ---------------------------------------------------------------------------

def test_set_bit():
    """Set bit n using 1 << n."""
    out, err, rc = clython_run("n = 3; print(0 | (1 << n))")
    assert rc == 0
    assert out == "8"


def test_test_bit():
    """Test bit n using >> and &."""
    out, err, rc = clython_run("value = 0b1010; print((value >> 1) & 1)")
    assert rc == 0
    assert out == "1"


def test_powers_of_two_via_shift():
    """Generate powers of 2 using shift."""
    out, err, rc = clython_run("print([1 << i for i in range(5)])")
    assert rc == 0
    assert out == "[1, 2, 4, 8, 16]"


def test_extract_byte():
    """Extract low byte using shift and mask."""
    out, err, rc = clython_run("value = 0x1234; print((value >> 8) & 0xFF)")
    assert rc == 0
    assert out == "18"


def test_pack_bytes():
    """Pack two bytes using shift."""
    out, err, rc = clython_run("high = 0x12; low = 0x34; print((high << 8) | low)")
    assert rc == 0
    assert out == "4660"


# ---------------------------------------------------------------------------
# Error conditions
# ---------------------------------------------------------------------------

def test_negative_shift_count_raises():
    """Shifting by a negative count should raise ValueError."""
    out, err, rc = clython_run("print(1 << -1)")
    assert rc != 0


def test_shift_in_function():
    """Shift inside a function."""
    source = "def double(n): return n << 1\nprint(double(5))"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "10"


def test_float_shift_raises():
    """Shifting a float should raise TypeError."""
    out, err, rc = clython_run("print(3.14 << 1)")
    assert rc != 0
    assert "TypeError" in err
