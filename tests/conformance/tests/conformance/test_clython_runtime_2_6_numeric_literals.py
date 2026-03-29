"""
Clython runtime conformance tests for Section 2.6: Numeric Literals.

These tests run code through the Clython binary and verify output/behavior.
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


def test_decimal_zero():
    out, err, rc = clython_run("print(0)")
    assert rc == 0
    assert out == "0"


def test_decimal_positive():
    out, err, rc = clython_run("print(123)")
    assert rc == 0
    assert out == "123"


def test_leading_zeros_forbidden():
    """Leading zeros in non-zero decimal integers are not allowed."""
    _, _, rc = clython_run("print(01)")
    assert rc != 0


def test_multiple_zeros_allowed():
    """Zero with extra zeros (00) is allowed per spec."""
    out, err, rc = clython_run("print(00)")
    assert rc == 0
    assert out == "0"


def test_binary_zero():
    out, err, rc = clython_run("print(0b0)")
    assert rc == 0
    assert out == "0"


def test_binary_value():
    out, err, rc = clython_run("print(0b1010)")
    assert rc == 0
    assert out == "10"


def test_binary_uppercase_prefix():
    out, err, rc = clython_run("print(0B1111)")
    assert rc == 0
    assert out == "15"


def test_binary_invalid_digit():
    """Binary literals only allow 0 and 1."""
    _, _, rc = clython_run("print(0b2)")
    assert rc != 0


def test_octal_value():
    out, err, rc = clython_run("print(0o77)")
    assert rc == 0
    assert out == "63"


def test_octal_uppercase_prefix():
    out, err, rc = clython_run("print(0O377)")
    assert rc == 0
    assert out == "255"


def test_octal_invalid_digit():
    """Octal literals only allow 0-7."""
    _, _, rc = clython_run("print(0o8)")
    assert rc != 0


def test_hex_lowercase():
    out, err, rc = clython_run("print(0xff)")
    assert rc == 0
    assert out == "255"


def test_hex_uppercase_digits():
    out, err, rc = clython_run("print(0xFF)")
    assert rc == 0
    assert out == "255"


def test_hex_mixed_case():
    out, err, rc = clython_run("print(0xDeAdBeEf)")
    assert rc == 0
    assert out == "3735928559"


def test_float_standard():
    out, err, rc = clython_run("print(3.14)")
    assert rc == 0
    assert out == "3.14"


def test_float_no_leading():
    out, err, rc = clython_run("print(.5)")
    assert rc == 0
    assert out == "0.5"


def test_float_no_trailing():
    out, err, rc = clython_run("print(5.)")
    assert rc == 0
    assert out == "5.0"


def test_float_exponent():
    out, err, rc = clython_run("print(1e3)")
    assert rc == 0
    assert out == "1000.0"


def test_float_negative_exponent():
    out, err, rc = clython_run("print(2e-3)")
    assert rc == 0
    assert out == "0.002"


def test_imaginary_integer():
    out, err, rc = clython_run("print(5j)")
    assert rc == 0
    assert out == "5j"


def test_imaginary_float():
    out, err, rc = clython_run("print(3.14j)")
    assert rc == 0
    assert out == "3.14j"


def test_imaginary_uppercase_j():
    out, err, rc = clython_run("print(2J)")
    assert rc == 0
    assert out == "2j"


def test_underscore_separator_decimal():
    out, err, rc = clython_run("print(1_000_000)")
    assert rc == 0
    assert out == "1000000"


def test_underscore_separator_hex():
    out, err, rc = clython_run("print(0xdead_beef)")
    assert rc == 0
    assert out == "3735928559"


def test_underscore_separator_float():
    out, err, rc = clython_run("print(1_234.5)")
    assert rc == 0
    assert out == "1234.5"


def test_large_integer_arbitrary_precision():
    out, err, rc = clython_run("print(10 ** 30)")
    assert rc == 0
    assert out == "1000000000000000000000000000000"
