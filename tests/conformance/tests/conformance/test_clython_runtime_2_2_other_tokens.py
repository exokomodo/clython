"""
Clython Runtime Tests: Section 2.2 - Other Tokens

Tests tokenization of identifiers, numbers, strings, and operators via the Clython binary.
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


# --- NAME tokens ---

def test_simple_identifier():
    out, err, rc = clython_run("variable = 99; print(variable)")
    assert rc == 0
    assert out == "99"


def test_underscore_identifier():
    out, err, rc = clython_run("_private = 7; print(_private)")
    assert rc == 0
    assert out == "7"


def test_dunder_identifier():
    out, err, rc = clython_run("__val__ = 3; print(__val__)")
    assert rc == 0
    assert out == "3"


def test_camel_case_identifier():
    out, err, rc = clython_run("MyVar = 'camel'; print(MyVar)")
    assert rc == 0
    assert out == "camel"


def test_identifier_with_digits():
    out, err, rc = clython_run("var123 = 42; print(var123)")
    assert rc == 0
    assert out == "42"


# --- NUMBER tokens ---

def test_decimal_integer():
    out, err, rc = clython_run("print(1234567890)")
    assert rc == 0
    assert out == "1234567890"


def test_zero():
    out, err, rc = clython_run("print(0)")
    assert rc == 0
    assert out == "0"


def test_hex_integer():
    out, err, rc = clython_run("print(0x1a2b)")
    assert rc == 0
    assert out == "6699"


def test_octal_integer():
    out, err, rc = clython_run("print(0o755)")
    assert rc == 0
    assert out == "493"


def test_binary_integer():
    out, err, rc = clython_run("print(0b1010)")
    assert rc == 0
    assert out == "10"


def test_float_literal():
    out, err, rc = clython_run("print(3.14)")
    assert rc == 0
    assert out == "3.14"


def test_float_leading_dot():
    out, err, rc = clython_run("print(.5)")
    assert rc == 0
    assert out == "0.5"


def test_float_trailing_dot():
    out, err, rc = clython_run("print(10.)")
    assert rc == 0
    assert out == "10.0"


def test_scientific_notation():
    out, err, rc = clython_run("print(1e3)")
    assert rc == 0
    assert out == "1000.0"


def test_scientific_negative_exponent():
    out, err, rc = clython_run("print(2.5e-1)")
    assert rc == 0
    assert out == "0.25"


def test_complex_number():
    out, err, rc = clython_run("print(3j)")
    assert rc == 0
    assert out == "3j"


def test_numeric_underscore_separator():
    out, err, rc = clython_run("print(1_000_000)")
    assert rc == 0
    assert out == "1000000"


# --- STRING tokens ---

def test_single_quoted_string():
    out, err, rc = clython_run("print('hello')")
    assert rc == 0
    assert out == "hello"


def test_double_quoted_string():
    out, err, rc = clython_run('print("world")')
    assert rc == 0
    assert out == "world"


def test_triple_single_quoted_string():
    out, err, rc = clython_run("print('''triple''')")
    assert rc == 0
    assert out == "triple"


def test_triple_double_quoted_string():
    out, err, rc = clython_run('print("""triple double""")')
    assert rc == 0
    assert out == "triple double"


def test_raw_string():
    out, err, rc = clython_run(r"print(r'\n is not a newline')")
    assert rc == 0
    assert out == r"\n is not a newline"


def test_bytes_literal():
    out, err, rc = clython_run("print(b'bytes')")
    assert rc == 0
    assert out == "b'bytes'"


def test_fstring():
    out, err, rc = clython_run("x = 7; print(f'value is {x}')")
    assert rc == 0
    assert out == "value is 7"


def test_string_concatenation():
    out, err, rc = clython_run("print('hello' + ' ' + 'world')")
    assert rc == 0
    assert out == "hello world"


# --- OP tokens ---

def test_double_star_power():
    out, err, rc = clython_run("print(2 ** 10)")
    assert rc == 0
    assert out == "1024"


def test_floor_division():
    out, err, rc = clython_run("print(7 // 2)")
    assert rc == 0
    assert out == "3"


def test_modulo():
    out, err, rc = clython_run("print(10 % 3)")
    assert rc == 0
    assert out == "1"


def test_augmented_assignment_operators():
    source = """
x = 10
x += 5
x -= 2
x *= 3
print(x)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "39"


def test_comparison_operators():
    source = """
print(1 == 1)
print(1 != 2)
print(1 < 2)
print(2 > 1)
print(1 <= 1)
print(2 >= 2)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True\nTrue\nTrue\nTrue\nTrue\nTrue"


def test_bitwise_operators():
    source = """
a = 0b1100
b = 0b1010
print(bin(a & b))
print(bin(a | b))
print(bin(a ^ b))
print(bin(~a & 0xf))
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "0b1000\n0b1110\n0b110\n0b11"


def test_shift_operators():
    out, err, rc = clython_run("print(1 << 4, 256 >> 3)")
    assert rc == 0
    assert out == "16 32"


def test_longest_match_double_equals():
    """== should be a single token, not = ="""
    out, err, rc = clython_run("print(1 == 1)")
    assert rc == 0
    assert out == "True"


def test_longest_match_double_star():
    """** should be power operator, not * *"""
    out, err, rc = clython_run("print(2**8)")
    assert rc == 0
    assert out == "256"


def test_longest_match_floor_div():
    """// should be floor division, not / /"""
    out, err, rc = clython_run("print(10//3)")
    assert rc == 0
    assert out == "3"


def test_delimiter_parentheses():
    out, err, rc = clython_run("print((1 + 2) * 3)")
    assert rc == 0
    assert out == "9"


def test_delimiter_brackets():
    out, err, rc = clython_run("lst = [1,2,3]; print(lst[1])")
    assert rc == 0
    assert out == "2"


def test_delimiter_braces():
    out, err, rc = clython_run("d = {'k': 'v'}; print(d['k'])")
    assert rc == 0
    assert out == "v"


def test_matrix_multiply_operator():
    source = """
class M:
    def __matmul__(self, o): return 'matmul'
a = M(); b = M()
print(a @ b)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "matmul"
