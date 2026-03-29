"""
Clython runtime conformance tests for Section 2.5: String and Bytes Literals.

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


def test_double_quoted_string():
    out, err, rc = clython_run('print("hello")')
    assert rc == 0
    assert out == "hello"


def test_single_quoted_string():
    out, err, rc = clython_run("print('hello')")
    assert rc == 0
    assert out == "hello"


def test_empty_string():
    out, err, rc = clython_run('print("")')
    assert rc == 0
    assert out == ""


def test_triple_double_quoted_string():
    out, err, rc = clython_run('print("""hello""")')
    assert rc == 0
    assert out == "hello"


def test_triple_single_quoted_string():
    out, err, rc = clython_run("print('''hello''')")
    assert rc == 0
    assert out == "hello"


def test_multiline_triple_quoted_string():
    source = 'x = """line1\nline2"""\nprint(x)'
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "line1\nline2"


def test_escape_newline():
    out, err, rc = clython_run(r'print("a\nb")')
    assert rc == 0
    assert out == "a\nb"


def test_escape_tab():
    out, err, rc = clython_run(r'print("a\tb")')
    assert rc == 0
    assert out == "a\tb"


def test_escape_backslash():
    out, err, rc = clython_run(r'print("a\\b")')
    assert rc == 0
    assert out == "a\\b"


def test_escape_unicode():
    out, err, rc = clython_run(r'print("\u0041")')
    assert rc == 0
    assert out == "A"


def test_raw_string_no_escape():
    out, err, rc = clython_run(r"print(r'\n')")
    assert rc == 0
    assert out == "\\n"


def test_raw_string_uppercase():
    out, err, rc = clython_run(r"print(R'\t')")
    assert rc == 0
    assert out == "\\t"


def test_bytes_literal_basic():
    out, err, rc = clython_run("print(b'hello')")
    assert rc == 0
    assert out == "b'hello'"


def test_bytes_literal_uppercase_b():
    out, err, rc = clython_run("print(B'hello')")
    assert rc == 0
    assert out == "b'hello'"


def test_bytes_literal_type():
    out, err, rc = clython_run("print(type(b'hello').__name__)")
    assert rc == 0
    assert out == "bytes"


def test_raw_bytes_literal():
    out, err, rc = clython_run(r"print(rb'\n')")
    assert rc == 0
    assert out == "b'\\\\n'"


def test_adjacent_string_concatenation():
    out, err, rc = clython_run('print("hello" " " "world")')
    assert rc == 0
    assert out == "hello world"


def test_fstring_basic():
    out, err, rc = clython_run("x = 42\nprint(f'value is {x}')")
    assert rc == 0
    assert out == "value is 42"


def test_fstring_expression():
    out, err, rc = clython_run("print(f'{2 + 2}')")
    assert rc == 0
    assert out == "4"


def test_fstring_format_spec():
    out, err, rc = clython_run("print(f'{3.14159:.2f}')")
    assert rc == 0
    assert out == "3.14"


def test_unterminated_string_is_error():
    _, _, rc = clython_run('"unterminated')
    assert rc != 0


def test_string_with_apostrophe():
    out, err, rc = clython_run("""print("it's fine")""")
    assert rc == 0
    assert out == "it's fine"


def test_string_concatenation_type():
    out, err, rc = clython_run('print(type("hello" "world").__name__)')
    assert rc == 0
    assert out == "str"
