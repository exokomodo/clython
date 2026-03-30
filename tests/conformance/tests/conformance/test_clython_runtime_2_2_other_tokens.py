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


# --- Additional tests to cover all source test cases ---

def test_simple_name_tokens():
    """Test simple identifier NAME tokens."""
    out, err, rc = clython_run("name = 'hello'\nprint(name)")
    assert rc == 0
    assert out == "hello"


def test_name_token_patterns():
    """Test various identifier patterns generate NAME tokens."""
    source = "_x = 1\nmy_var = 2\nCamelCase = 3\nprint(_x + my_var + CamelCase)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "6"


def test_name_token_unicode():
    """Test Unicode identifier NAME tokens."""
    out, err, rc = clython_run("café = 42\nprint(café)")
    assert rc == 0
    assert out == "42"


def test_keyword_vs_name_tokens():
    """Test keyword recognition vs NAME token generation."""
    out, err, rc = clython_run("if True:\n    print('keyword')")
    assert rc == 0
    assert out == "keyword"


def test_integer_number_tokens():
    """Test integer literal NUMBER tokens."""
    source = "print(42)\nprint(0b1010)\nprint(0o17)\nprint(0xFF)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "42\n10\n15\n255"


def test_float_number_tokens():
    """Test floating-point NUMBER tokens."""
    source = "print(3.14)\nprint(.5)\nprint(5.)\nprint(1e3)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "3.14\n0.5\n5.0\n1000.0"


def test_complex_number_tokens():
    """Test complex number literal tokens."""
    source = "print(1j)\nprint(2.5j)\nprint(type(1j).__name__)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "1j\n2.5j\ncomplex"


def test_number_token_separators():
    """Test underscore separators in NUMBER tokens."""
    source = "print(1_000_000)\nprint(0xFF_AA)\nprint(1_0.0_5)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "1000000\n65450\n10.05"


def test_longest_match_with_numbers():
    """Test longest match for numeric literals."""
    out, err, rc = clython_run("print(1234567890)")
    assert rc == 0
    assert out == "1234567890"


def test_simple_string_tokens():
    """Test simple string literal STRING tokens."""
    source = "print('hello')\nprint(\"world\")"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "hello\nworld"


def test_string_token_prefixes():
    """Test string prefix variations in STRING tokens."""
    source = "print(b'bytes')\nprint(r'raw')"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "b'bytes'\nraw"


def test_bytes_literal_tokens():
    """Test bytes literal tokenization."""
    source = "x = b'hello'\nprint(type(x).__name__)\nprint(len(x))"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "bytes\n5"


def test_fstring_token_prefixes():
    """Test f-string prefix variations."""
    source = "name = 'world'\nprint(f'hello {name}')"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "hello world"


def test_multiline_string_tokens():
    """Test multiline string tokenization."""
    source = 'x = """line1\nline2\nline3"""\nprint(x)'
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "line1\nline2\nline3"


def test_longest_match_with_strings():
    """Test longest match for string literals."""
    out, err, rc = clython_run("print('hello world')")
    assert rc == 0
    assert out == "hello world"


def test_arithmetic_operator_tokens():
    """Test arithmetic operator OP tokens."""
    source = "print(2 + 3)\nprint(10 - 4)\nprint(3 * 4)\nprint(10 / 4)\nprint(10 // 3)\nprint(10 % 3)\nprint(2 ** 8)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "5\n6\n12\n2.5\n3\n1\n256"


def test_comparison_operator_tokens():
    """Test comparison operator OP tokens."""
    source = "print(1 < 2)\nprint(2 > 1)\nprint(1 == 1)\nprint(1 != 2)\nprint(2 >= 2)\nprint(1 <= 2)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True\nTrue\nTrue\nTrue\nTrue\nTrue"


def test_bitwise_operator_tokens():
    """Test bitwise operator OP tokens."""
    source = "print(0b1010 | 0b0101)\nprint(0b1010 & 0b1100)\nprint(0b1010 ^ 0b1100)\nprint(~0)\nprint(1 << 4)\nprint(16 >> 2)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "15\n8\n6\n-1\n16\n4"


def test_assignment_operator_tokens():
    """Test assignment operator OP tokens."""
    source = "x = 10\nx += 5\nprint(x)\nx -= 3\nprint(x)\nx *= 2\nprint(x)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "15\n12\n24"


def test_delimiter_tokens():
    """Test delimiter OP tokens."""
    source = "t = (1, 2, 3)\nprint(t[0])\nd = {'k': 'v'}\nprint(d['k'])"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "1\nv"


def test_matrix_multiplication_token():
    """Test matrix multiplication operator token."""
    source = "class M:\n    def __matmul__(self, o): return 'mm'\na = M()\nprint(a @ a)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "mm"


def test_longest_operator_matching():
    """Test longest match rule for operators."""
    source = "x = 5\nx += 3\nprint(x)\ny = 10\ny //= 3\nprint(y)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "8\n3"


def test_longest_match_disambiguation():
    """Test longest match rule disambiguation."""
    source = "print(1 == 1)\nprint(1 != 2)\nprint(2 >= 2)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True\nTrue\nTrue"


def test_newline_token_generation():
    """Test NEWLINE tokens generated for logical line boundaries."""
    source = "x = 1\ny = 2\nprint(x + y)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "3"


def test_newline_statement_boundaries():
    """Test NEWLINE tokens create statement boundaries."""
    source = "a = 1\nb = 2\nc = a + b\nprint(c)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "3"


def test_newline_in_compound_statements():
    """Test NEWLINE behavior in compound statements."""
    source = "def f():\n    x = 1\n    y = 2\n    return x + y\nprint(f())"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "3"


def test_implicit_newline_at_eof():
    """Test implicit NEWLINE at end of file."""
    out, err, rc = clython_run("print('eof')")
    assert rc == 0
    assert out == "eof"


def test_indent_token_generation():
    """Test INDENT tokens for indentation increases."""
    source = "if True:\n    print('indented')"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "indented"


def test_dedent_token_generation():
    """Test DEDENT tokens for indentation decreases."""
    source = "def f():\n    x = 1\nx = 2\nprint(x)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "2"


def test_indent_dedent_matching():
    """Test INDENT/DEDENT token matching requirements."""
    source = "if True:\n    x = 1\n    y = 2\nprint(x + y)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "3"


def test_nested_indent_dedent():
    """Test nested INDENT/DEDENT token patterns."""
    source = "if True:\n    if True:\n        x = 42\nprint(x)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "42"


def test_whitespace_ignored_between_tokens():
    """Test whitespace is ignored between tokens."""
    source = "x   =   1   +   2\nprint(x)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "3"


def test_whitespace_token_separation():
    """Test whitespace required for token separation."""
    source = "x = 10\ny = 20\nprint(x + y)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "30"


def test_significant_whitespace_preservation():
    """Test significant whitespace in indentation."""
    source = "def f():\n    return 7\nprint(f())"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "7"


def test_automatic_token_boundaries():
    """Test automatic token boundary detection."""
    source = "x=1+2*3\nprint(x)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "7"


def test_token_boundary_with_numbers():
    """Test token boundaries with numeric literals."""
    out, err, rc = clython_run("print(1+2)")
    assert rc == 0
    assert out == "3"


def test_token_boundary_ambiguity_resolution():
    """Test resolution of token boundary ambiguities."""
    out, err, rc = clython_run("x = -1\nprint(x)")
    assert rc == 0
    assert out == "-1"


def test_token_edge_cases():
    """Test edge cases in tokenization."""
    source = "x = 0\nprint(x)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "0"


def test_tokenization_specification_compliance():
    """Test compliance with tokenization specifications."""
    source = "x = 1_000\nprint(x)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "1000"


def test_comprehensive_token_patterns():
    """Test complex token combinations."""
    source = "result = (1 + 2) * 3 - 4 // 2\nprint(result)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "7"
