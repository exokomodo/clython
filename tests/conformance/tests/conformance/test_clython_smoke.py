"""
Clython smoke tests — basic interpreter functionality.

These tests run through the Clython binary (CLYTHON_BIN) and verify
that the interpreter handles fundamental Python constructs.
Unlike the CPython-native tests that use ast.parse/eval/exec directly,
these shell out to Clython.
"""

import os
import subprocess
import pytest

CLYTHON_BIN = os.environ.get("CLYTHON_BIN")

pytestmark = pytest.mark.skipif(
    not CLYTHON_BIN, reason="CLYTHON_BIN not set — skipping Clython-specific tests"
)


def clython_run(source: str, timeout: float = 30.0):
    """Run source through Clython, return (stdout, stderr, returncode)."""
    result = subprocess.run(
        [CLYTHON_BIN, "-c", source],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode


def clython_parse(source: str, timeout: float = 30.0):
    """Parse source through Clython, return (stdout, stderr, returncode)."""
    result = subprocess.run(
        [CLYTHON_BIN, "--parse-only", "-c", source],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode


# ── Section 2: Lexical Analysis ──────────────────────────────────────────────


class TestClythonLexicalBasics:
    """Basic lexer/parser smoke tests."""

    def test_integer_literal(self):
        stdout, stderr, rc = clython_run("print(42)")
        assert rc == 0 and stdout == "42", f"got rc={rc}, stdout={stdout!r}, stderr={stderr!r}"

    def test_string_literal(self):
        stdout, stderr, rc = clython_run("print('hello')")
        assert rc == 0 and stdout == "hello", f"got rc={rc}, stdout={stdout!r}, stderr={stderr!r}"

    def test_float_literal(self):
        stdout, stderr, rc = clython_run("print(3.14)")
        assert rc == 0 and stdout == "3.14", f"got rc={rc}, stdout={stdout!r}, stderr={stderr!r}"

    def test_boolean_true(self):
        stdout, stderr, rc = clython_run("print(True)")
        assert rc == 0 and stdout == "True", f"got rc={rc}, stdout={stdout!r}, stderr={stderr!r}"

    def test_boolean_false(self):
        stdout, stderr, rc = clython_run("print(False)")
        assert rc == 0 and stdout == "False", f"got rc={rc}, stdout={stdout!r}, stderr={stderr!r}"

    def test_none_literal(self):
        stdout, stderr, rc = clython_run("print(None)")
        assert rc == 0 and stdout == "None", f"got rc={rc}, stdout={stdout!r}, stderr={stderr!r}"


# ── Section 6: Expressions ───────────────────────────────────────────────────


class TestClythonExpressions:
    """Expression evaluation smoke tests."""

    def test_addition(self):
        stdout, stderr, rc = clython_run("print(1 + 2)")
        assert rc == 0 and stdout == "3", f"got rc={rc}, stdout={stdout!r}, stderr={stderr!r}"

    def test_subtraction(self):
        stdout, stderr, rc = clython_run("print(10 - 3)")
        assert rc == 0 and stdout == "7", f"got rc={rc}, stdout={stdout!r}, stderr={stderr!r}"

    def test_multiplication(self):
        stdout, stderr, rc = clython_run("print(6 * 7)")
        assert rc == 0 and stdout == "42", f"got rc={rc}, stdout={stdout!r}, stderr={stderr!r}"

    def test_division(self):
        stdout, stderr, rc = clython_run("print(10 / 4)")
        assert rc == 0 and stdout == "2.5", f"got rc={rc}, stdout={stdout!r}, stderr={stderr!r}"

    def test_integer_division(self):
        stdout, stderr, rc = clython_run("print(10 // 3)")
        assert rc == 0 and stdout == "3", f"got rc={rc}, stdout={stdout!r}, stderr={stderr!r}"

    def test_modulo(self):
        stdout, stderr, rc = clython_run("print(10 % 3)")
        assert rc == 0 and stdout == "1", f"got rc={rc}, stdout={stdout!r}, stderr={stderr!r}"

    def test_power(self):
        stdout, stderr, rc = clython_run("print(2 ** 10)")
        assert rc == 0 and stdout == "1024", f"got rc={rc}, stdout={stdout!r}, stderr={stderr!r}"

    def test_comparison(self):
        stdout, stderr, rc = clython_run("print(1 < 2)")
        assert rc == 0 and stdout == "True", f"got rc={rc}, stdout={stdout!r}, stderr={stderr!r}"

    def test_string_concatenation(self):
        stdout, stderr, rc = clython_run("print('hello' + ' ' + 'world')")
        assert rc == 0 and stdout == "hello world", f"got rc={rc}, stdout={stdout!r}, stderr={stderr!r}"

    def test_negation(self):
        stdout, stderr, rc = clython_run("print(-42)")
        assert rc == 0 and stdout == "-42", f"got rc={rc}, stdout={stdout!r}, stderr={stderr!r}"


# ── Section 7: Simple Statements ─────────────────────────────────────────────


class TestClythonSimpleStatements:
    """Simple statement smoke tests."""

    def test_assignment(self):
        stdout, stderr, rc = clython_run("x = 42\nprint(x)")
        assert rc == 0 and stdout == "42", f"got rc={rc}, stdout={stdout!r}, stderr={stderr!r}"

    def test_multiple_assignment(self):
        stdout, stderr, rc = clython_run("x = y = 10\nprint(x + y)")
        assert rc == 0 and stdout == "20", f"got rc={rc}, stdout={stdout!r}, stderr={stderr!r}"

    def test_augmented_assignment(self):
        stdout, stderr, rc = clython_run("x = 5\nx += 3\nprint(x)")
        assert rc == 0 and stdout == "8", f"got rc={rc}, stdout={stdout!r}, stderr={stderr!r}"

    def test_pass_statement(self):
        stdout, stderr, rc = clython_run("pass")
        assert rc == 0, f"got rc={rc}, stderr={stderr!r}"


# ── Section 8: Compound Statements ───────────────────────────────────────────


class TestClythonCompoundStatements:
    """Compound statement smoke tests."""

    def test_if_true(self):
        stdout, stderr, rc = clython_run("if True:\n    print('yes')")
        assert rc == 0 and stdout == "yes", f"got rc={rc}, stdout={stdout!r}, stderr={stderr!r}"

    def test_if_else(self):
        stdout, stderr, rc = clython_run("if False:\n    print('no')\nelse:\n    print('yes')")
        assert rc == 0 and stdout == "yes", f"got rc={rc}, stdout={stdout!r}, stderr={stderr!r}"

    def test_while_loop(self):
        stdout, stderr, rc = clython_run("i = 0\nwhile i < 3:\n    print(i)\n    i += 1")
        assert rc == 0 and stdout == "0\n1\n2", f"got rc={rc}, stdout={stdout!r}, stderr={stderr!r}"

    def test_for_loop(self):
        stdout, stderr, rc = clython_run("for i in [1, 2, 3]:\n    print(i)")
        assert rc == 0 and stdout == "1\n2\n3", f"got rc={rc}, stdout={stdout!r}, stderr={stderr!r}"

    def test_function_def(self):
        stdout, stderr, rc = clython_run("def f(x):\n    return x + 1\nprint(f(5))")
        assert rc == 0 and stdout == "6", f"got rc={rc}, stdout={stdout!r}, stderr={stderr!r}"


# ── Parse-only tests ─────────────────────────────────────────────────────────


class TestClythonParseOnly:
    """Verify the parser accepts valid Python without executing."""

    def test_parse_simple_expression(self):
        stdout, stderr, rc = clython_parse("1 + 2")
        assert rc == 0, f"parse failed: rc={rc}, stderr={stderr!r}"

    def test_parse_function_def(self):
        stdout, stderr, rc = clython_parse("def foo(x, y):\n    return x + y")
        assert rc == 0, f"parse failed: rc={rc}, stderr={stderr!r}"

    def test_parse_class_def(self):
        stdout, stderr, rc = clython_parse("class Foo:\n    pass")
        assert rc == 0, f"parse failed: rc={rc}, stderr={stderr!r}"

    def test_parse_import(self):
        stdout, stderr, rc = clython_parse("import os")
        assert rc == 0, f"parse failed: rc={rc}, stderr={stderr!r}"

    def test_parse_invalid_syntax(self):
        stdout, stderr, rc = clython_parse("def 123bad():")
        assert rc == 2, f"expected syntax error (rc=2), got rc={rc}"
