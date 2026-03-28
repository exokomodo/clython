"""Clython conformance tests — Section 9: Top-level Components.

Tests that the Clython interpreter correctly handles top-level execution:
complete programs, file input, and expression evaluation via -c flag.
"""
import os
import subprocess
import tempfile
import pytest

CLYTHON_BIN = os.environ.get("CLYTHON_BIN")

def clython_run(source: str, *, timeout: int = 10):
    """Run source through Clython via -c, return (stdout, stderr, returncode)."""
    result = subprocess.run(
        [CLYTHON_BIN, "-c", source],
        capture_output=True, text=True, timeout=timeout
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def clython_run_file(source: str, *, timeout: int = 10):
    """Run source as a .py file through Clython, return (stdout, stderr, returncode)."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(source)
        f.flush()
        result = subprocess.run(
            [CLYTHON_BIN, f.name],
            capture_output=True, text=True, timeout=timeout
        )
    os.unlink(f.name)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

pytestmark = pytest.mark.skipif(
    not CLYTHON_BIN, reason="CLYTHON_BIN not set — skipping Clython-specific tests"
)


# ── 9.1 Complete programs ─────────────────────────────────────────────────

class TestSection91CompletePrograms:
    def test_simple_program(self):
        out, _, rc = clython_run("print('hello world')")
        assert rc == 0 and out == "hello world"

    def test_multiline_program(self):
        out, _, rc = clython_run("x = 1\ny = 2\nprint(x + y)")
        assert rc == 0 and out == "3"

    def test_program_with_functions(self):
        out, _, rc = clython_run("def add(a, b):\n    return a + b\nprint(add(3, 4))")
        assert rc == 0 and out == "7"

    def test_program_with_classes(self):
        out, _, rc = clython_run("class C:\n    def __init__(self, x):\n        self.x = x\nprint(C(42).x)")
        assert rc == 0 and out == "42"

    def test_program_exit_code_success(self):
        _, _, rc = clython_run("x = 1")
        assert rc == 0

    def test_program_exit_code_error(self):
        _, _, rc = clython_run("raise ValueError('fail')")
        assert rc != 0


# ── 9.2 File input ────────────────────────────────────────────────────────

class TestSection92FileInput:
    def test_file_execution(self):
        out, _, rc = clython_run_file("print('from file')")
        assert rc == 0 and out == "from file"

    def test_file_multiline(self):
        out, _, rc = clython_run_file("x = 10\ny = 20\nprint(x * y)")
        assert rc == 0 and out == "200"

    def test_file_with_function(self):
        out, _, rc = clython_run_file("def greet(name):\n    return 'Hello, ' + name\nprint(greet('World'))")
        assert rc == 0 and out == "Hello, World"

    def test_file_with_imports(self):
        out, _, rc = clython_run_file("import math\nprint(int(math.pi))")
        assert rc == 0 and out == "3"

    def test_file_error_exits_nonzero(self):
        _, _, rc = clython_run_file("raise RuntimeError('boom')")
        assert rc != 0


# ── 9.3 Expression input (via -c) ────────────────────────────────────────

class TestSection93ExpressionInput:
    def test_c_flag_expression(self):
        out, _, rc = clython_run("print(2 + 2)")
        assert rc == 0 and out == "4"

    def test_c_flag_complex_expression(self):
        out, _, rc = clython_run("result = [x**2 for x in range(5)]\nprint(result)")
        assert rc == 0 and out == "[0, 1, 4, 9, 16]"

    def test_c_flag_multiple_statements(self):
        out, _, rc = clython_run("a = 'hello'\nb = 'world'\nprint(a + ' ' + b)")
        assert rc == 0 and out == "hello world"

    def test_c_flag_syntax_error(self):
        _, err, rc = clython_run("def def")
        assert rc != 0 and "SyntaxError" in err
