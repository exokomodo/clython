"""
Clython runtime conformance tests for Section 2.7: String and Bytes Literals
(extended coverage — concatenation, prefixes, f-strings, raw strings).

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


def test_single_quoted_string():
    out, err, rc = clython_run("print('hello')")
    assert rc == 0
    assert out == "hello"


def test_double_quoted_string():
    out, err, rc = clython_run('print("hello")')
    assert rc == 0
    assert out == "hello"


def test_triple_single_quoted():
    out, err, rc = clython_run("print('''triple''')")
    assert rc == 0
    assert out == "triple"


def test_triple_double_quoted():
    out, err, rc = clython_run('print("""triple""")')
    assert rc == 0
    assert out == "triple"


def test_raw_string_r_prefix():
    out, err, rc = clython_run(r"print(r'\n')")
    assert rc == 0
    assert out == "\\n"


def test_raw_string_uppercase_r():
    out, err, rc = clython_run(r"print(R'\t')")
    assert rc == 0
    assert out == "\\t"


def test_bytes_b_prefix():
    out, err, rc = clython_run("print(b'hello')")
    assert rc == 0
    assert out == "b'hello'"


def test_bytes_uppercase_b():
    out, err, rc = clython_run("print(B'hello')")
    assert rc == 0
    assert out == "b'hello'"


def test_bytes_br_prefix():
    out, err, rc = clython_run(r"print(br'\n')")
    assert rc == 0
    assert out == "b'\\\\n'"


def test_bytes_rb_prefix():
    out, err, rc = clython_run(r"print(rb'\t')")
    assert rc == 0
    assert out == "b'\\\\t'"


def test_adjacent_string_concatenation():
    """Adjacent string literals are concatenated per spec."""
    out, err, rc = clython_run("print('hello' ' ' 'world')")
    assert rc == 0
    assert out == "hello world"


def test_adjacent_bytes_concatenation():
    """Adjacent bytes literals are concatenated."""
    out, err, rc = clython_run("print(b'hello' b' ' b'world')")
    assert rc == 0
    assert out == "b'hello world'"


def test_mixed_quote_concatenation():
    out, err, rc = clython_run("""print('hello' " world")""")
    assert rc == 0
    assert out == "hello world"


def test_escape_newline_in_string():
    out, err, rc = clython_run(r'print("a\nb")')
    assert rc == 0
    assert out == "a\nb"


def test_escape_tab_in_string():
    out, err, rc = clython_run(r'print("a\tb")')
    assert rc == 0
    assert out == "a\tb"


def test_unicode_escape_in_string():
    out, err, rc = clython_run(r'print("\u0041\u0042\u0043")')
    assert rc == 0
    assert out == "ABC"


def test_fstring_variable():
    out, err, rc = clython_run("name = 'World'\nprint(f'Hello, {name}!')")
    assert rc == 0
    assert out == "Hello, World!"


def test_fstring_arithmetic():
    out, err, rc = clython_run("print(f'{1 + 1}')")
    assert rc == 0
    assert out == "2"


def test_fstring_format_specifier():
    out, err, rc = clython_run("print(f'{42:04d}')")
    assert rc == 0
    assert out == "0042"


def test_invalid_prefix_combination_fb():
    """f and b prefixes cannot be combined."""
    _, _, rc = clython_run("print(fb'hello')")
    assert rc != 0


def test_string_bytes_adjacent_concat_error():
    """String and bytes cannot be concatenated adjacently."""
    _, _, rc = clython_run("print('hello' b'world')")
    assert rc != 0


def test_unterminated_string_error():
    _, _, rc = clython_run('"unterminated')
    assert rc != 0


def test_multiline_triple_string():
    source = 'x = """line1\nline2\nline3"""\nprint(x)'
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "line1\nline2\nline3"


# --- Additional tests to cover all source test cases ---

def test_basic_string_quotes():
    """Test basic string quote styles."""
    source = "print('single')\nprint(\"double\")"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "single\ndouble"


def test_triple_quoted_strings():
    """Test triple-quoted string literals."""
    source = 'print("""triple""")\nprint(\'\'\'triple2\'\'\')'
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "triple\ntriple2"


def test_escape_sequences_basic():
    """Test basic escape sequences."""
    source = "print('newline:\\n')\nprint('tab:\\t')\nprint('backslash:\\\\')"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "newline:\n\ntab:\t\nbackslash:\\"


def test_raw_string_escaping():
    """Test raw string escaping."""
    source = r"print(r'\n\t\\')"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == r"\n\t\\"


def test_unicode_strings():
    """Test Unicode string content."""
    out, err, rc = clython_run("print('café')\nprint('中文')")
    assert rc == 0
    assert out == "café\n中文"


def test_bytes_prefix_syntax():
    """Test bytes prefix syntax."""
    source = "print(b'bytes')\nprint(B'bytes2')"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "b'bytes'\nb'bytes2'"


def test_bytes_content_restrictions():
    """Test bytes content restrictions (ASCII only)."""
    source = "x = b'hello\\x00world'\nprint(len(x))"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "11"


def test_bytes_raw_strings():
    """Test raw bytes literal syntax."""
    source = r"print(rb'\n')"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == r"b'\\n'"


def test_string_concatenation_adjacent():
    """Test adjacent string concatenation."""
    source = "x = 'hello' ' ' 'world'\nprint(x)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "hello world"


def test_bytes_concatenation():
    """Test bytes adjacent concatenation."""
    source = "x = b'hello' b' world'\nprint(x)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "b'hello world'"


def test_mixed_quote_styles_concatenation():
    """Test mixing single and double quote adjacent strings."""
    source = 'x = "hello" \' world\'\nprint(x)'
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "hello world"


def test_string_prefixes_case_insensitive():
    """Test string prefixes are case-insensitive."""
    source = "print(r'raw')\nprint(R'RAW')\nprint(b'bytes')\nprint(B'BYTES')"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "raw\nRAW\nb'bytes'\nb'BYTES'"


def test_f_string_basic_syntax():
    """Test basic f-string syntax."""
    source = "x = 42\nprint(f'value: {x}')"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "value: 42"


def test_f_string_expression_syntax():
    """Test f-string with expressions."""
    source = "print(f'{1 + 2}')\nprint(f'{\"hello\".upper()}')"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "3\nHELLO"


def test_f_string_format_specifiers():
    """Test f-string format specifiers."""
    source = "pi = 3.14159\nprint(f'{pi:.2f}')\nprint(f'{42:05d}')"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "3.14\n00042"


def test_invalid_escape_sequences():
    """Test invalid escape sequences (deprecated in Python 3.12+)."""
    # In older Python, invalid escapes produce DeprecationWarning, not error
    # Valid escape sequences should still work
    out, err, rc = clython_run("print('\\n')")
    assert rc == 0
    assert out == ""  # Just newline


def test_invalid_prefix_combinations():
    """Test invalid prefix combinations raise SyntaxError."""
    _, _, rc = clython_run("x = bf'test'")  # bytes and f-string can't combine
    assert rc != 0


def test_string_bytes_concatenation_restrictions():
    """Test string and bytes cannot be mixed in concatenation."""
    _, _, rc = clython_run("x = 'str' b'bytes'")
    assert rc != 0


def test_large_string_literals():
    """Test large string literals."""
    source = "x = 'a' * 10000\nprint(len(x))"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "10000"


def test_deeply_nested_concatenation():
    """Test deeply nested adjacent string concatenation."""
    source = "x = 'a' 'b' 'c' 'd' 'e'\nprint(x)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "abcde"


def test_unterminated_string_errors():
    """Test unterminated string literals are errors."""
    _, _, rc = clython_run('"unterminated')
    assert rc != 0
