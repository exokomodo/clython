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


# ── 9.1 Complete Programs (extended) ──────────────────────────────────────

class TestSection91CompleteProgramsExtended:
    """Additional complete program tests from AST conformance suite."""

    def test_program_with_all_compound_statements(self):
        """A program using if, for, while, def, class, try"""
        out, _, rc = clython_run(
            "class Acc:\n"
            "    def __init__(self):\n"
            "        self.v = 0\n"
            "    def add(self, n):\n"
            "        self.v += n\n"
            "a = Acc()\n"
            "for i in range(5):\n"
            "    if i % 2 == 0:\n"
            "        a.add(i)\n"
            "try:\n"
            "    print(a.v)\n"
            "except:\n"
            "    print('error')"
        )
        assert rc == 0 and out == "6"

    def test_program_with_nested_functions(self):
        out, _, rc = clython_run(
            "def compose(f, g):\n"
            "    def h(x):\n"
            "        return f(g(x))\n"
            "    return h\n"
            "double = lambda x: x * 2\n"
            "inc = lambda x: x + 1\n"
            "print(compose(double, inc)(3))"
        )
        assert rc == 0 and out == "8"

    def test_empty_program(self):
        """An empty program should succeed with no output."""
        out, _, rc = clython_run("")
        assert rc == 0 and out == ""

    def test_comment_only_program(self):
        out, _, rc = clython_run("# just a comment\n")
        assert rc == 0 and out == ""

    def test_main_guard_pattern(self):
        out, _, rc = clython_run_file(
            "def main():\n"
            "    print('main ran')\n"
            "if __name__ == '__main__':\n"
            "    main()"
        )
        assert rc == 0 and out == "main ran"

    def test_multiple_print_statements(self):
        out, _, rc = clython_run("print('a')\nprint('b')\nprint('c')")
        assert rc == 0 and out == "a\nb\nc"

    def test_program_execution_order(self):
        """Top-level statements execute in order."""
        out, _, rc = clython_run(
            "results = []\n"
            "results.append(1)\n"
            "def f():\n    results.append(2)\n"
            "results.append(3)\n"
            "f()\n"
            "results.append(4)\n"
            "print(results)"
        )
        assert rc == 0 and out == "[1, 3, 2, 4]"


# ── 9.2 File Input (extended) ─────────────────────────────────────────────

class TestSection92FileInputExtended:
    """Additional file input tests from AST conformance suite."""

    def test_file_with_classes_and_methods(self):
        out, _, rc = clython_run_file(
            "class Stack:\n"
            "    def __init__(self):\n"
            "        self._items = []\n"
            "    def push(self, x):\n"
            "        self._items.append(x)\n"
            "    def pop(self):\n"
            "        return self._items.pop()\n"
            "    def size(self):\n"
            "        return len(self._items)\n"
            "s = Stack()\n"
            "s.push(10)\n"
            "s.push(20)\n"
            "print(s.pop(), s.size())"
        )
        assert rc == 0 and out == "20 1"

    def test_file_with_multiple_functions(self):
        out, _, rc = clython_run_file(
            "def is_even(n):\n"
            "    return n % 2 == 0\n"
            "def filter_evens(lst):\n"
            "    return [x for x in lst if is_even(x)]\n"
            "print(filter_evens([1, 2, 3, 4, 5, 6]))"
        )
        assert rc == 0 and out == "[2, 4, 6]"

    def test_file_with_exception_handling(self):
        out, _, rc = clython_run_file(
            "def safe_div(a, b):\n"
            "    try:\n"
            "        return a / b\n"
            "    except ZeroDivisionError:\n"
            "        return 'inf'\n"
            "print(safe_div(10, 2))\n"
            "print(safe_div(1, 0))"
        )
        assert rc == 0 and out == "5.0\ninf"

    def test_file_with_global_and_local_scope(self):
        out, _, rc = clython_run_file(
            "x = 'global'\n"
            "def f():\n"
            "    x = 'local'\n"
            "    print(x)\n"
            "f()\n"
            "print(x)"
        )
        assert rc == 0 and out == "local\nglobal"

    def test_file_blank_lines_and_comments(self):
        out, _, rc = clython_run_file(
            "# header comment\n"
            "\n"
            "x = 1\n"
            "\n"
            "# another comment\n"
            "y = 2\n"
            "\n"
            "print(x + y)"
        )
        assert rc == 0 and out == "3"


# ── 9.3 Expression Input (extended) ───────────────────────────────────────

class TestSection93ExpressionInputExtended:
    """Additional expression input tests from AST conformance suite."""

    def test_c_flag_with_import(self):
        out, _, rc = clython_run("import math\nprint(int(math.sqrt(16)))")
        assert rc == 0 and out == "4"

    def test_c_flag_with_for_loop(self):
        out, _, rc = clython_run("for i in range(3):\n    print(i)")
        assert rc == 0 and out == "0\n1\n2"

    def test_c_flag_with_while(self):
        out, _, rc = clython_run("i = 3\nwhile i > 0:\n    print(i)\n    i -= 1")
        assert rc == 0 and out == "3\n2\n1"

    def test_c_flag_with_try_except(self):
        out, _, rc = clython_run(
            "try:\n    print(1/0)\nexcept ZeroDivisionError:\n    print('caught')"
        )
        assert rc == 0 and out == "caught"

    def test_c_flag_name_error(self):
        _, err, rc = clython_run("print(undefined_variable)")
        assert rc != 0

    def test_c_flag_type_error(self):
        _, err, rc = clython_run("'hello' + 5")
        assert rc != 0

    def test_c_flag_semicolon_separation(self):
        """Multiple statements separated by semicolons."""
        out, _, rc = clython_run("x = 1; y = 2; print(x + y)")
        assert rc == 0 and out == "3"
