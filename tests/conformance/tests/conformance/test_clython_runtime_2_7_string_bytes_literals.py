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
