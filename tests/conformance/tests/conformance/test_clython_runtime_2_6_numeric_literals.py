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


# --- Additional tests to cover all source test cases ---

def test_decimal_integers():
    """Test decimal integer literals."""
    source = "print(0)\nprint(1)\nprint(9999)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "0\n1\n9999"


def test_binary_integers():
    """Test binary integer literals."""
    source = "print(0b0)\nprint(0b1)\nprint(0b1010)\nprint(0B11111111)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "0\n1\n10\n255"


def test_octal_integers():
    """Test octal integer literals."""
    source = "print(0o0)\nprint(0o7)\nprint(0o77)\nprint(0O777)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "0\n7\n63\n511"


def test_hexadecimal_integers():
    """Test hexadecimal integer literals."""
    source = "print(0x0)\nprint(0xf)\nprint(0xFF)\nprint(0XDEADBEEF)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "0\n15\n255\n3735928559"


def test_basic_float_syntax():
    """Test basic floating-point syntax."""
    source = "print(0.0)\nprint(1.0)\nprint(3.14)\nprint(.5)\nprint(5.)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "0.0\n1.0\n3.14\n0.5\n5.0"


def test_exponent_notation():
    """Test exponent notation in floats."""
    source = "print(1e0)\nprint(1e3)\nprint(1e-3)\nprint(1.5e2)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "1.0\n1000.0\n0.001\n150.0"


def test_optional_components():
    """Test optional components of numeric literals."""
    source = "print(1.)\nprint(.1)\nprint(1e1)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "1.0\n0.1\n10.0"


def test_basic_imaginary_syntax():
    """Test basic imaginary literal syntax."""
    source = "print(0j)\nprint(1j)\nprint(2.5j)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "0j\n1j\n2.5j"


def test_imaginary_with_float_syntax():
    """Test imaginary literals with float-like syntax."""
    source = "print(1.0j)\nprint(.5j)\nprint(type(1e2j).__name__)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "1j\n0.5j\ncomplex"


def test_imaginary_decimal_point_omission():
    """Test imaginary literal with omitted decimal point."""
    source = "print(type(1j).__name__)\nprint((1j).real)\nprint((1j).imag)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "complex\n0.0\n1.0"


def test_imaginary_with_underscores():
    """Test imaginary literals with underscores."""
    source = "print(1_000j)\nprint(1_0.0j)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "1000j\n10j"


def test_underscore_grouping_valid():
    """Test valid underscore grouping in numeric literals."""
    source = "print(1_000_000)\nprint(0xFF_FF)\nprint(1_000.0_00)\nprint(1_0e1_0)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "1000000\n65535\n1000.0\n100000000000.0"


def test_underscore_grouping_invalid():
    """Test invalid underscore grouping raises SyntaxError."""
    _, _, rc = clython_run("x = 1__000")  # Double underscore
    assert rc != 0


def test_underscore_in_floats():
    """Test underscores in float literals."""
    source = "print(3.14_15)\nprint(1_0.5)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "3.1415\n10.5"


def test_invalid_numeric_syntax():
    """Test invalid numeric syntax raises errors."""
    _, _, rc = clython_run("x = 0b2")  # Invalid binary digit
    assert rc != 0


def test_large_number_limits():
    """Test large numbers (Python has no integer overflow)."""
    source = "print(2 ** 100)\nprint(type(2**100).__name__)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "1267650600228229401496703205376\nint"


def test_precision_edge_cases():
    """Test floating-point precision edge cases."""
    source = "print(0.1 + 0.2 > 0.3)\nprint(type(0.1 + 0.2).__name__)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True\nfloat"


def test_base_prefix_edge_cases():
    """Test base prefix edge cases."""
    source = "print(0x0 == 0b0 == 0o0 == 0)\nprint(0xa == 0b1010 == 0o12 == 10)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True\nTrue"


def test_suffix_edge_cases():
    """Test suffix edge cases in numeric literals."""
    source = "z = 1j\nprint(type(z).__name__)\nprint(z == complex(0, 1))"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "complex\nTrue"


def test_whitespace_in_literals():
    """Test whitespace around numeric literals."""
    source = "x = 42\ny = 3.14\nz = 1j\nprint(x, y, z)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "42 3.14 1j"


def test_underscore_version_compatibility():
    """Test underscore separators compatibility."""
    source = "print(1_0 == 10)\nprint(1_0.0 == 10.0)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True\nTrue"
