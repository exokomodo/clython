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


# --- Additional tests to cover all source test cases ---

def test_decimal_integer_literals():
    """Test decimal integer literal forms."""
    source = "print(0)\nprint(42)\nprint(1000000)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "0\n42\n1000000"


def test_binary_integer_literals():
    """Test binary integer literal forms."""
    source = "print(0b1010)\nprint(0B1111)\nprint(0b0)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "10\n15\n0"


def test_octal_integer_literals():
    """Test octal integer literal forms."""
    source = "print(0o777)\nprint(0O10)\nprint(0o0)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "511\n8\n0"


def test_hexadecimal_integer_literals():
    """Test hexadecimal integer literal forms."""
    source = "print(0xff)\nprint(0XFF)\nprint(0xDEAD)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "255\n255\n57005"


def test_integer_underscore_separators():
    """Test underscore separators in integer literals."""
    source = "print(1_000_000)\nprint(0xFF_FF)\nprint(0b1111_0000)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "1000000\n65535\n240"


def test_integer_literal_ranges():
    """Test integer literal ranges (arbitrary precision)."""
    source = "print(123456789012345678901234567890)\nprint(2**64)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "123456789012345678901234567890\n18446744073709551616"


def test_basic_float_literals():
    """Test basic floating-point literal forms."""
    source = "print(3.14)\nprint(.5)\nprint(5.)\nprint(0.0)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "3.14\n0.5\n5.0\n0.0"


def test_scientific_notation_literals():
    """Test scientific notation floating-point literals."""
    source = "print(1e3)\nprint(1E-3)\nprint(2.5e2)\nprint(1.5e-2)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "1000.0\n0.001\n250.0\n0.015"


def test_float_underscore_separators():
    """Test underscore separators in float literals."""
    source = "print(1_000.5)\nprint(1.000_5)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "1000.5\n1.0005"


def test_float_literal_precision():
    """Test float literal precision."""
    source = "print(3.141592653589793)\nprint(2.718281828459045)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "3.141592653589793\n2.718281828459045"


def test_basic_imaginary_literals():
    """Test basic imaginary literal forms."""
    source = "print(1j)\nprint(2.5j)\nprint(0j)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "1j\n2.5j\n0j"


def test_complex_number_construction():
    """Test complex number construction from literals."""
    source = "z = 3 + 4j\nprint(z.real)\nprint(z.imag)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "3.0\n4.0"


def test_boolean_literals():
    """Test boolean literal values."""
    source = "print(True)\nprint(False)\nprint(type(True).__name__)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True\nFalse\nbool"


def test_none_literals():
    """Test None literal value."""
    source = "print(None)\nprint(type(None).__name__)\nprint(None is None)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "None\nNoneType\nTrue"


def test_literal_type_consistency():
    """Test literal type consistency."""
    source = "print(type(42).__name__)\nprint(type(3.14).__name__)\nprint(type(True).__name__)\nprint(type(None).__name__)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "int\nfloat\nbool\nNoneType"


def test_literal_value_preservation():
    """Test literal value preservation."""
    source = "x = 255\nprint(x == 0xFF)\nprint(x == 0b11111111)\nprint(x == 0o377)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True\nTrue\nTrue"


def test_literal_ast_structure():
    """Test literal AST structure."""
    source = "x = 42\ny = 3.14\nz = True\nprint(x, y, z)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "42 3.14 True"


def test_literals_in_expressions():
    """Test literals in expressions."""
    source = "print(2 + 3)\nprint(10.0 / 4)\nprint(True and False)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "5\n2.5\nFalse"


def test_literals_in_function_calls():
    """Test literals in function calls."""
    source = "print(max(1, 2, 3))\nprint(min(3.14, 2.71))"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "3\n2.71"


def test_literals_in_data_structures():
    """Test literals in data structures."""
    source = "lst = [1, 2.5, True, None]\nprint(lst)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "[1, 2.5, True, None]"


def test_invalid_integer_literals():
    """Test invalid integer literal syntax."""
    _, _, rc = clython_run("x = 0b2")  # Invalid binary
    assert rc != 0


def test_invalid_float_literals():
    """Test invalid float literal syntax."""
    # Multiple decimal points are a syntax error
    _, _, rc = clython_run("x = 1..3")  # Two dots = syntax error
    assert rc != 0


def test_literal_introspection_capabilities():
    """Test literal introspection capabilities."""
    source = "print(isinstance(42, int))\nprint(isinstance(3.14, float))\nprint(isinstance(True, bool))"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True\nTrue\nTrue"


def test_literal_consistency():
    """Test literal consistency across operations."""
    source = "a = 10\nb = 0b1010\nc = 0o12\nd = 0xA\nprint(a == b == c == d)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True"


def test_comprehensive_literal_patterns():
    """Test comprehensive literal pattern combinations."""
    # 2**10=1024, 0xFF=255, 0b11=3, 0o7=7, 1_000=1000 → 1024+255+3+7+1000=2289
    source = "result = 2**10 + 0xFF + 0b11 + 0o7 + 1_000\nprint(result)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "2289"
