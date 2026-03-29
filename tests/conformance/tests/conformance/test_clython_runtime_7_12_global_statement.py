"""Clython runtime tests — Section 7.12: Global Statement.

Tests that the Clython interpreter correctly implements the global
statement for module-level scope binding within functions.
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


class TestGlobalStatementRuntime:
    def test_global_modify_module_var(self):
        """global allows a function to modify a module-level variable"""
        out, err, rc = clython_run(
            "x = 10\n"
            "def f():\n    global x\n    x = 20\n"
            "f()\nprint(x)"
        )
        assert rc == 0
        assert out == "20"

    def test_without_global_creates_local(self):
        """without global, assignment creates a local variable"""
        out, err, rc = clython_run(
            "x = 10\n"
            "def f():\n    x = 99\n"
            "f()\nprint(x)"
        )
        assert rc == 0
        assert out == "10"

    def test_global_counter_increment(self):
        """global allows incrementing a counter"""
        out, err, rc = clython_run(
            "counter = 0\n"
            "def inc():\n    global counter\n    counter += 1\n"
            "inc()\ninc()\ninc()\nprint(counter)"
        )
        assert rc == 0
        assert out == "3"

    def test_global_multiple_variables(self):
        """global with multiple variable names"""
        out, err, rc = clython_run(
            "a = 1\nb = 2\n"
            "def swap():\n    global a, b\n    a, b = b, a\n"
            "swap()\nprint(a, b)"
        )
        assert rc == 0
        assert out == "2 1"

    def test_global_separate_statements(self):
        """separate global statements for different variables"""
        out, err, rc = clython_run(
            "x = 0\ny = 0\n"
            "def f():\n    global x\n    global y\n    x = 5\n    y = 10\n"
            "f()\nprint(x, y)"
        )
        assert rc == 0
        assert out == "5 10"

    def test_global_read_module_var(self):
        """global allows reading module-level variable (no modification needed)"""
        out, err, rc = clython_run(
            "value = 42\n"
            "def read():\n    global value\n    return value\n"
            "print(read())"
        )
        assert rc == 0
        assert out == "42"

    def test_global_creates_new_module_var(self):
        """global declaration creates a new module-level variable if needed"""
        out, err, rc = clython_run(
            "def create():\n    global new_var\n    new_var = 'hello'\n"
            "create()\nprint(new_var)"
        )
        assert rc == 0
        assert out == "hello"

    def test_global_in_nested_function(self):
        """global in inner function refers to module level, not outer function"""
        out, err, rc = clython_run(
            "x = 'module'\n"
            "def outer():\n"
            "    x = 'outer'\n"
            "    def inner():\n"
            "        global x\n"
            "        x = 'changed'\n"
            "    inner()\n"
            "    return x\n"
            "outer_result = outer()\n"
            "print(outer_result)\n"
            "print(x)"
        )
        assert rc == 0
        assert out == "outer\nchanged"

    def test_global_mutable_object(self):
        """global with mutable object (list) allows mutation"""
        out, err, rc = clython_run(
            "items = []\n"
            "def add(x):\n    global items\n    items.append(x)\n"
            "add(1)\nadd(2)\nadd(3)\nprint(items)"
        )
        assert rc == 0
        assert out == "[1, 2, 3]"

    def test_global_reassign_dict(self):
        """global allows reassigning a dict variable entirely"""
        out, err, rc = clython_run(
            "config = {'debug': False}\n"
            "def enable_debug():\n    global config\n    config = {'debug': True}\n"
            "enable_debug()\nprint(config['debug'])"
        )
        assert rc == 0
        assert out == "True"

    def test_global_in_class_method(self):
        """global inside a class method refers to module scope"""
        out, err, rc = clython_run(
            "counter = 0\n"
            "class C:\n"
            "    def bump(self):\n"
            "        global counter\n"
            "        counter += 1\n"
            "C().bump()\nC().bump()\nprint(counter)"
        )
        assert rc == 0
        assert out == "2"

    def test_global_multiple_functions(self):
        """multiple functions sharing a global variable"""
        out, err, rc = clython_run(
            "total = 0\n"
            "def add(n):\n    global total\n    total += n\n"
            "def reset():\n    global total\n    total = 0\n"
            "add(5)\nadd(3)\nprint(total)\nreset()\nprint(total)"
        )
        assert rc == 0
        assert out == "8\n0"

    def test_global_in_loop(self):
        """global variable modified inside a loop"""
        out, err, rc = clython_run(
            "total = 0\n"
            "def accumulate(values):\n"
            "    global total\n"
            "    for v in values:\n"
            "        total += v\n"
            "accumulate([1, 2, 3, 4, 5])\nprint(total)"
        )
        assert rc == 0
        assert out == "15"

    def test_global_in_exception_handler(self):
        """global modified inside exception handler"""
        out, err, rc = clython_run(
            "errors = 0\n"
            "def safe_divide(a, b):\n"
            "    global errors\n"
            "    try:\n        return a / b\n"
            "    except ZeroDivisionError:\n"
            "        errors += 1\n"
            "        return None\n"
            "safe_divide(1, 0)\nsafe_divide(2, 0)\nprint(errors)"
        )
        assert rc == 0
        assert out == "2"

    def test_global_string_concatenation(self):
        """global string variable can be concatenated"""
        out, err, rc = clython_run(
            "log = ''\n"
            "def append_log(msg):\n    global log\n    log += msg + '\\n'\n"
            "append_log('first')\nappend_log('second')\nprint(log.strip())"
        )
        assert rc == 0
        assert out == "first\nsecond"

    def test_global_flag_pattern(self):
        """classic global flag pattern"""
        out, err, rc = clython_run(
            "found = False\n"
            "def search(items, target):\n"
            "    global found\n"
            "    for item in items:\n"
            "        if item == target:\n"
            "            found = True\n"
            "            break\n"
            "search([1, 2, 3, 4, 5], 3)\nprint(found)"
        )
        assert rc == 0
        assert out == "True"
