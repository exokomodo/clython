"""
Clython runtime conformance tests for Section 2.4: Literals.

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


def test_decimal_integer_zero():
    out, err, rc = clython_run("print(0)")
    assert rc == 0
    assert out == "0"


def test_decimal_integer_positive():
    out, err, rc = clython_run("print(42)")
    assert rc == 0
    assert out == "42"


def test_binary_integer_literal():
    out, err, rc = clython_run("print(0b1010)")
    assert rc == 0
    assert out == "10"


def test_binary_integer_uppercase():
    out, err, rc = clython_run("print(0B1111)")
    assert rc == 0
    assert out == "15"


def test_octal_integer_literal():
    out, err, rc = clython_run("print(0o777)")
    assert rc == 0
    assert out == "511"


def test_hexadecimal_integer_lowercase():
    out, err, rc = clython_run("print(0xff)")
    assert rc == 0
    assert out == "255"


def test_hexadecimal_integer_uppercase():
    out, err, rc = clython_run("print(0XFF)")
    assert rc == 0
    assert out == "255"


def test_float_basic():
    out, err, rc = clython_run("print(3.14)")
    assert rc == 0
    assert out == "3.14"


def test_float_no_leading_digit():
    out, err, rc = clython_run("print(.5)")
    assert rc == 0
    assert out == "0.5"


def test_float_no_trailing_digit():
    out, err, rc = clython_run("print(5.)")
    assert rc == 0
    assert out == "5.0"


def test_float_scientific_notation():
    out, err, rc = clython_run("print(1e3)")
    assert rc == 0
    assert out == "1000.0"


def test_float_negative_exponent():
    out, err, rc = clython_run("print(1e-3)")
    assert rc == 0
    assert out == "0.001"


def test_imaginary_literal():
    out, err, rc = clython_run("print(1j)")
    assert rc == 0
    assert out == "1j"


def test_imaginary_float():
    out, err, rc = clython_run("print(2.5j)")
    assert rc == 0
    assert out == "2.5j"


def test_true_literal():
    out, err, rc = clython_run("print(True)")
    assert rc == 0
    assert out == "True"


def test_false_literal():
    out, err, rc = clython_run("print(False)")
    assert rc == 0
    assert out == "False"


def test_none_literal():
    out, err, rc = clython_run("print(None)")
    assert rc == 0
    assert out == "None"


def test_string_literal():
    out, err, rc = clython_run('print("hello")')
    assert rc == 0
    assert out == "hello"


def test_bytes_literal():
    out, err, rc = clython_run('print(b"hello")')
    assert rc == 0
    assert out == "b'hello'"


def test_integer_underscore_separator():
    out, err, rc = clython_run("print(1_000_000)")
    assert rc == 0
    assert out == "1000000"


def test_hex_underscore_separator():
    out, err, rc = clython_run("print(0xFF_AA)")
    assert rc == 0
    assert out == "65450"


def test_large_integer():
    """Python supports arbitrary precision integers."""
    out, err, rc = clython_run("print(123456789012345678901234567890)")
    assert rc == 0
    assert out == "123456789012345678901234567890"


def test_literal_type_int():
    out, err, rc = clython_run("print(type(42).__name__)")
    assert rc == 0
    assert out == "int"


def test_literal_type_float():
    out, err, rc = clython_run("print(type(3.14).__name__)")
    assert rc == 0
    assert out == "float"


def test_literal_type_complex():
    out, err, rc = clython_run("print(type(1j).__name__)")
    assert rc == 0
    assert out == "complex"
