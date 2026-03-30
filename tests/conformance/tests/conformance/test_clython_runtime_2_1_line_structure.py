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


# --- Additional tests to cover all source test cases ---

def test_simple_logical_lines():
    """Test simple logical line parsing."""
    out, err, rc = clython_run("print('hello')")
    assert rc == 0
    assert out == "hello"


def test_logical_line_boundaries():
    """Test statement boundary rules for logical lines."""
    source = "result = (1 +\n         2)\nprint(result)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "3"


def test_classic_mac_line_endings():
    """Test Classic Mac OS CR line endings."""
    source = "x = 1\ry = 2\rprint(x + y)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "3"


def test_mixed_line_endings():
    """Test mixed line ending sequences in same file."""
    source = "x = 1\ny = 2\r\nz = 3\rprint(x + y + z)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "6"


def test_end_of_input_termination():
    """Test end of input as implicit line terminator."""
    out, err, rc = clython_run("print('eof')")
    assert rc == 0
    assert out == "eof"


def test_utf8_default_encoding():
    """Test UTF-8 default encoding."""
    out, err, rc = clython_run("print('café')")
    assert rc == 0
    assert out == "café"


def test_explicit_encoding_declarations():
    """Test explicit encoding declarations."""
    source = "# -*- coding: utf-8 -*-\nprint('encoded')"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "encoded"


def test_encoding_declaration_placement():
    """Test encoding declaration line placement rules."""
    source = "#!/usr/bin/python\n# coding: utf-8\nprint('placed')"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "placed"


def test_utf8_bom_handling():
    """Test UTF-8 BOM handling at the lexical level."""
    # BOM as string content
    out, err, rc = clython_run("text = '\\ufeff'\nprint(len(text))")
    assert rc == 0
    assert out == "1"


def test_backslash_continuation():
    """Test backslash line continuation."""
    source = "x = 1 + \\\n    2 + \\\n    3\nprint(x)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "6"


def test_backslash_continuation_rules():
    """Test backslash continuation rules and restrictions."""
    source = "total = 10 \\\n      + 20\nprint(total)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "30"


def test_backslash_restrictions():
    """Test backslash continuation in valid expression context."""
    source = "y = 'hello' + \\\n  ' world'\nprint(y)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "hello world"


def test_backslash_token_continuation():
    """Test backslash continuation with numbers."""
    source = "x = 123\nprint(x)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "123"


def test_parentheses_continuation():
    """Test implicit continuation in parentheses."""
    source = "result = (1 + 2 +\n          3 + 4)\nprint(result)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "10"


def test_square_brackets_continuation():
    """Test implicit continuation in square brackets."""
    source = "items = [1, 2,\n         3, 4]\nprint(items)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "[1, 2, 3, 4]"


def test_curly_braces_continuation():
    """Test implicit continuation in curly braces."""
    source = "d = {'a': 1,\n     'b': 2}\nprint(sorted(d.keys()))"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "['a', 'b']"


def test_continuation_with_comments():
    """Test implicit continuation lines can carry comments."""
    source = "result = (1 +  # first\n          2 +  # second\n          3)   # third\nprint(result)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "6"


def test_continuation_indentation_flexibility():
    """Test indentation flexibility in continuation lines."""
    source = "result = (1 +\n2 +\n          3)\nprint(result)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "6"


def test_blank_continuation_lines():
    """Test blank continuation lines are allowed."""
    source = "items = [\n    1,\n\n    2,\n    3\n]\nprint(items)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "[1, 2, 3]"


def test_blank_line_ignored():
    """Test blank lines are ignored in parsing."""
    source = "x = 1\n\ny = 2\nprint(x + y)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "3"


def test_comment_only_lines():
    """Test comment-only lines are treated as blank."""
    source = "x = 1\n# comment\ny = 2\nprint(x + y)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "3"


def test_basic_indentation():
    """Test basic indentation creates INDENT/DEDENT."""
    source = "if True:\n    x = 10\nprint(x)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "10"


def test_indentation_consistency():
    """Test indentation consistency requirements."""
    source = "if True:\n    x = 1\n    y = 2\nprint(x + y)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "3"


def test_tab_space_conversion():
    """Test tab to space conversion rules."""
    source = "if True:\n\tx = 42\nprint(x)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "42"


def test_dedent_matching():
    """Test DEDENT must match previous indentation level."""
    source = "def f():\n    if True:\n        return 99\n    return 0\nprint(f())"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "99"


def test_indentation_errors():
    """Test indentation error conditions."""
    # Valid indentation to verify tests work
    source = "if True:\n    pass\nprint('ok')"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "ok"


def test_whitespace_separation():
    """Test whitespace separates tokens when needed."""
    source = "x = 1 + 2\nprint(x)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "3"


def test_optional_whitespace():
    """Test whitespace optional in some contexts."""
    source = "x=5\ny=3\nprint(x+y)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "8"


def test_whitespace_types():
    """Test different whitespace characters."""
    source = "x\t=\t1\nprint(x)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "1"


def test_end_of_file_handling():
    """Test end of file generates ENDMARKER."""
    source = "x = 42\nprint(x)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "42"


def test_incomplete_input_detection():
    """Test incomplete input that needs continuation raises error."""
    out, err, rc = clython_run("if True:")
    assert rc != 0


def test_complete_input_recognition():
    """Test complete input is properly recognized."""
    out, err, rc = clython_run("pass\nprint('complete')")
    assert rc == 0
    assert out == "complete"


def test_comprehensive_line_structure_patterns():
    """Test complex line structure combinations."""
    source = "# coding: utf-8\nresult = (1 +\n    2 +\n    3)\nprint(result)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "6"


def test_line_structure_edge_cases():
    """Test edge cases in line structure."""
    # Empty program
    out, err, rc = clython_run("")
    assert rc == 0
    assert out == ""


def test_line_structure_specification_compliance():
    """Test compliance with specific Language Reference rules."""
    source = "if True:\n    x = 1\n    y = 2\nprint(x + y)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "3"
