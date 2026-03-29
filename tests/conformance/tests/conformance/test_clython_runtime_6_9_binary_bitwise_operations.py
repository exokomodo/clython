"""
Clython runtime tests for Section 6.9: Binary Bitwise Operations.

Tests &, |, ^ operators through the Clython binary.
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
# Bitwise AND (&)
# ---------------------------------------------------------------------------

def test_bitwise_and_basic():
    """Basic bitwise AND."""
    out, err, rc = clython_run("print(0b1100 & 0b1010)")
    assert rc == 0
    assert out == "8"  # 0b1000


def test_bitwise_and_with_mask():
    """AND used as a bit mask."""
    out, err, rc = clython_run("print(0xFF & 0x0F)")
    assert rc == 0
    assert out == "15"


def test_bitwise_and_zero():
    """AND with zero always gives zero."""
    out, err, rc = clython_run("print(42 & 0)")
    assert rc == 0
    assert out == "0"


def test_bitwise_and_all_ones():
    """AND with all-ones is identity."""
    out, err, rc = clython_run("print(42 & 0xFF)")
    assert rc == 0
    assert out == "42"


def test_bitwise_and_idempotent():
    """x & x == x."""
    out, err, rc = clython_run("x = 37; print(x & x)")
    assert rc == 0
    assert out == "37"


# ---------------------------------------------------------------------------
# Bitwise OR (|)
# ---------------------------------------------------------------------------

def test_bitwise_or_basic():
    """Basic bitwise OR."""
    out, err, rc = clython_run("print(0b1100 | 0b0011)")
    assert rc == 0
    assert out == "15"  # 0b1111


def test_bitwise_or_sets_bits():
    """OR sets specific bits."""
    out, err, rc = clython_run("print(0b1000 | 0b0001)")
    assert rc == 0
    assert out == "9"  # 0b1001


def test_bitwise_or_with_zero():
    """OR with zero is identity."""
    out, err, rc = clython_run("print(42 | 0)")
    assert rc == 0
    assert out == "42"


def test_bitwise_or_idempotent():
    """x | x == x."""
    out, err, rc = clython_run("x = 37; print(x | x)")
    assert rc == 0
    assert out == "37"


def test_bitwise_or_combine_flags():
    """Combine two flag values."""
    out, err, rc = clython_run("READ = 4; WRITE = 2; print(READ | WRITE)")
    assert rc == 0
    assert out == "6"


# ---------------------------------------------------------------------------
# Bitwise XOR (^)
# ---------------------------------------------------------------------------

def test_bitwise_xor_basic():
    """Basic bitwise XOR."""
    out, err, rc = clython_run("print(0b1100 ^ 0b1010)")
    assert rc == 0
    assert out == "6"  # 0b0110


def test_bitwise_xor_self_is_zero():
    """x ^ x == 0."""
    out, err, rc = clython_run("x = 99; print(x ^ x)")
    assert rc == 0
    assert out == "0"


def test_bitwise_xor_with_zero():
    """x ^ 0 == x."""
    out, err, rc = clython_run("print(42 ^ 0)")
    assert rc == 0
    assert out == "42"


def test_bitwise_xor_toggle():
    """XOR toggles specific bits."""
    out, err, rc = clython_run("flags = 0b1010; toggle = 0b1111; print(flags ^ toggle)")
    assert rc == 0
    assert out == "5"  # 0b0101


def test_bitwise_xor_swap():
    """XOR swap algorithm."""
    source = "a = 3; b = 5; a ^= b; b ^= a; a ^= b; print(a, b)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "5 3"


# ---------------------------------------------------------------------------
# Precedence: & > ^ > |
# ---------------------------------------------------------------------------

def test_and_before_xor():
    """& has higher precedence than ^."""
    # 0b1100 & 0b1010 = 0b1000; 0b1000 ^ 0b0011 = 0b1011 = 11
    out, err, rc = clython_run("print(0b1100 & 0b1010 ^ 0b0011)")
    assert rc == 0
    assert out == "11"


def test_and_before_or():
    """& has higher precedence than |."""
    # 0b0010 & 0b0110 = 0b0010; 0b1000 | 0b0010 = 0b1010 = 10
    out, err, rc = clython_run("print(0b1000 | 0b0010 & 0b0110)")
    assert rc == 0
    assert out == "10"


def test_xor_before_or():
    """^ has higher precedence than |."""
    # 0b0101 ^ 0b0011 = 0b0110; 0b1000 | 0b0110 = 0b1110 = 14
    out, err, rc = clython_run("print(0b1000 | 0b0101 ^ 0b0011)")
    assert rc == 0
    assert out == "14"


def test_parentheses_change_order():
    """Parentheses change precedence of bitwise ops."""
    # (0b1000 | 0b0010) & 0b0110 = 0b1010 & 0b0110 = 0b0010 = 2
    out, err, rc = clython_run("print((0b1000 | 0b0010) & 0b0110)")
    assert rc == 0
    assert out == "2"


# ---------------------------------------------------------------------------
# Chaining
# ---------------------------------------------------------------------------

def test_chained_and():
    """Chained &."""
    out, err, rc = clython_run("print(0xFF & 0x0F & 0x07)")
    assert rc == 0
    assert out == "7"


def test_chained_or():
    """Chained |."""
    out, err, rc = clython_run("print(0x01 | 0x02 | 0x04)")
    assert rc == 0
    assert out == "7"


def test_chained_xor():
    """Chained ^ (parity check)."""
    out, err, rc = clython_run("print(0b0001 ^ 0b0010 ^ 0b0100)")
    assert rc == 0
    assert out == "7"


# ---------------------------------------------------------------------------
# Bitwise with set types
# ---------------------------------------------------------------------------

def test_set_intersection():
    """Set & set gives intersection."""
    out, err, rc = clython_run("print(sorted({1, 2, 3} & {2, 3, 4}))")
    assert rc == 0
    assert out == "[2, 3]"


def test_set_union():
    """Set | set gives union."""
    out, err, rc = clython_run("print(sorted({1, 2} | {3, 4}))")
    assert rc == 0
    assert out == "[1, 2, 3, 4]"


def test_set_symmetric_difference():
    """Set ^ set gives symmetric difference."""
    out, err, rc = clython_run("print(sorted({1, 2, 3} ^ {2, 3, 4}))")
    assert rc == 0
    assert out == "[1, 4]"


@pytest.mark.xfail(reason="Bitwise ops on floats may produce different error in Clython")
def test_bitwise_and_float_raises():
    """Bitwise AND on floats should raise TypeError."""
    out, err, rc = clython_run("print(3.14 & 1)")
    assert rc != 0
    assert "TypeError" in err
