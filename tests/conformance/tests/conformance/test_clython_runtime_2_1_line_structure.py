"""
Clython Runtime Tests: Section 2.1 - Line Structure

Tests line structure parsing and execution via the Clython binary.
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


def test_single_logical_line():
    out, err, rc = clython_run("print(42)")
    assert rc == 0
    assert out == "42"


def test_multiple_logical_lines():
    out, err, rc = clython_run("x = 1\ny = 2\nprint(x + y)")
    assert rc == 0
    assert out == "3"


def test_blank_lines_ignored():
    out, err, rc = clython_run("x = 1\n\n\ny = 2\n\nprint(x + y)")
    assert rc == 0
    assert out == "3"


def test_comment_lines_ignored():
    source = "# this is a comment\nx = 42\n# another comment\nprint(x)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "42"


def test_windows_line_endings():
    out, err, rc = clython_run("x = 1\r\ny = 2\r\nprint(x + y)")
    assert rc == 0
    assert out == "3"


def test_unix_line_endings():
    out, err, rc = clython_run("x = 1\ny = 2\nprint(x + y)")
    assert rc == 0
    assert out == "3"


def test_implicit_line_join_parens():
    source = "result = (1 +\n          2 +\n          3)\nprint(result)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "6"


def test_implicit_line_join_brackets():
    source = "items = [1,\n         2,\n         3]\nprint(items)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "[1, 2, 3]"


def test_implicit_line_join_braces():
    source = "d = {'a': 1,\n     'b': 2}\nprint(sorted(d.keys()))"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "['a', 'b']"


def test_explicit_line_join_backslash():
    source = "x = 1 + \\\n    2 + \\\n    3\nprint(x)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "6"


def test_continuation_with_comment_in_parens():
    source = "result = (1 +  # first\n          2 +  # second\n          3)   # third\nprint(result)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "6"


def test_indented_block_runs():
    source = "if True:\n    x = 10\nprint(x)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "10"


def test_nested_indentation():
    source = "if True:\n    if True:\n        x = 99\nprint(x)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "99"


def test_dedent_resumes_outer_scope():
    source = "def f():\n    x = 5\n    return x\nprint(f())"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "5"


def test_utf8_string_literal():
    out, err, rc = clython_run("print('café')")
    assert rc == 0
    assert out == "café"


def test_utf8_string_unicode():
    out, err, rc = clython_run("print('你好')")
    assert rc == 0
    assert out == "你好"


def test_coding_declaration_utf8():
    source = "# -*- coding: utf-8 -*-\nprint('hello')"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "hello"


def test_empty_program():
    out, err, rc = clython_run("")
    assert rc == 0
    assert out == ""


def test_whitespace_only_lines():
    out, err, rc = clython_run("x = 1\n   \ny = 2\nprint(x + y)")
    assert rc == 0
    assert out == "3"


def test_tab_indentation():
    source = "def f():\n\treturn 42\nprint(f())"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "42"


def test_multiline_function_call():
    source = "print(\n    'hello',\n    'world'\n)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "hello world"


def test_multiline_list_comprehension():
    source = """result = [
    x * 2
    for x in range(4)
    if x % 2 == 0
]
print(result)"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "[0, 4]"


def test_multiline_dict_comprehension():
    source = """d = {
    k: k * 2
    for k in range(3)
}
print(sorted(d.items()))"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "[(0, 0), (1, 2), (2, 4)]"


def test_shebang_line_ignored():
    source = "#!/usr/bin/env python3\nprint('shebang ok')"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "shebang ok"
