"""Clython conformance tests — Section 4: Execution Model.

Tests that the Clython interpreter correctly implements Python 3.12 execution model:
code blocks, naming and binding (LEGB), global/nonlocal, and exception context.
"""
import os
import subprocess
import pytest

CLYTHON_BIN = os.environ.get("CLYTHON_BIN")

def clython_run(source: str, *, timeout: int = 10):
    """Run source through Clython, return (stdout, stderr, returncode)."""
    result = subprocess.run(
        [CLYTHON_BIN, "-c", source],
        capture_output=True, text=True, timeout=timeout
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode

pytestmark = pytest.mark.skipif(
    not CLYTHON_BIN, reason="CLYTHON_BIN not set — skipping Clython-specific tests"
)


# ── 4.1 Structure of a program ────────────────────────────────────────────

class TestSection41CodeBlocks:
    def test_module_is_code_block(self):
        """Module-level code is a code block."""
        out, _, rc = clython_run("x = 1\ny = 2\nprint(x + y)")
        assert rc == 0 and out == "3"

    def test_function_body_is_code_block(self):
        out, _, rc = clython_run("def f():\n    x = 10\n    return x\nprint(f())")
        assert rc == 0 and out == "10"

    def test_class_body_is_code_block(self):
        out, _, rc = clython_run("class C:\n    x = 42\nprint(C.x)")
        assert rc == 0 and out == "42"


# ── 4.2 Naming and binding ────────────────────────────────────────────────

class TestSection42LEGB:
    def test_local_scope(self):
        out, _, rc = clython_run("def f():\n    x = 1\n    return x\nprint(f())")
        assert rc == 0 and out == "1"

    def test_enclosing_scope(self):
        out, _, rc = clython_run("def outer():\n    x = 10\n    def inner():\n        return x\n    return inner()\nprint(outer())")
        assert rc == 0 and out == "10"

    def test_global_scope(self):
        out, _, rc = clython_run("x = 42\ndef f():\n    return x\nprint(f())")
        assert rc == 0 and out == "42"

    def test_builtin_scope(self):
        out, _, rc = clython_run("def f():\n    return len([1, 2, 3])\nprint(f())")
        assert rc == 0 and out == "3"

    def test_local_shadows_global(self):
        out, _, rc = clython_run("x = 'global'\ndef f():\n    x = 'local'\n    return x\nprint(f())\nprint(x)")
        assert rc == 0 and out == "local\nglobal"

    def test_enclosing_shadows_global(self):
        out, _, rc = clython_run("x = 'global'\ndef outer():\n    x = 'enclosing'\n    def inner():\n        return x\n    return inner()\nprint(outer())")
        assert rc == 0 and out == "enclosing"

    def test_nested_closures(self):
        out, _, rc = clython_run("def a():\n    x = 1\n    def b():\n        def c():\n            return x\n        return c()\n    return b()\nprint(a())")
        assert rc == 0 and out == "1"


class TestSection42GlobalStatement:
    def test_global_write(self):
        out, _, rc = clython_run("x = 0\ndef f():\n    global x\n    x = 42\nf()\nprint(x)")
        assert rc == 0 and out == "42"

    def test_global_read_and_write(self):
        out, _, rc = clython_run("count = 0\ndef inc():\n    global count\n    count += 1\ninc()\ninc()\nprint(count)")
        assert rc == 0 and out == "2"


class TestSection42NonlocalStatement:
    def test_nonlocal_write(self):
        out, _, rc = clython_run("def outer():\n    x = 0\n    def inner():\n        nonlocal x\n        x = 42\n    inner()\n    return x\nprint(outer())")
        assert rc == 0 and out == "42"

    def test_nonlocal_increment(self):
        out, _, rc = clython_run("def counter():\n    n = 0\n    def inc():\n        nonlocal n\n        n += 1\n        return n\n    return inc\nc = counter()\nprint(c())\nprint(c())\nprint(c())")
        assert rc == 0 and out == "1\n2\n3"


class TestSection42NameResolutionErrors:
    def test_undefined_name(self):
        _, err, rc = clython_run("print(undefined_var)")
        assert rc != 0 and "NameError" in err

    def test_undefined_in_function(self):
        _, err, rc = clython_run("def f():\n    return undefined_var\nf()")
        assert rc != 0 and "NameError" in err


# ── 4.3 Exceptions ────────────────────────────────────────────────────────

class TestSection43Exceptions:
    def test_try_except(self):
        out, _, rc = clython_run("try:\n    x = 1 / 0\nexcept ZeroDivisionError:\n    print('caught')")
        assert rc == 0 and out == "caught"

    def test_try_except_as(self):
        out, _, rc = clython_run("try:\n    raise ValueError('oops')\nexcept ValueError as e:\n    print(e)")
        assert rc == 0 and out == "oops"

    def test_try_finally(self):
        out, _, rc = clython_run("try:\n    print('try')\nfinally:\n    print('finally')")
        assert rc == 0 and out == "try\nfinally"

    def test_try_except_finally(self):
        out, _, rc = clython_run("try:\n    x = 1 / 0\nexcept ZeroDivisionError:\n    print('caught')\nfinally:\n    print('done')")
        assert rc == 0 and out == "caught\ndone"

    def test_try_else(self):
        out, _, rc = clython_run("try:\n    x = 1\nexcept:\n    print('error')\nelse:\n    print('ok')")
        assert rc == 0 and out == "ok"

    def test_raise_runtime_error(self):
        _, err, rc = clython_run("raise RuntimeError('boom')")
        assert rc != 0 and "RuntimeError" in err

    def test_exception_in_function(self):
        out, _, rc = clython_run("def f():\n    try:\n        return 1 / 0\n    except ZeroDivisionError:\n        return 'caught'\nprint(f())")
        assert rc == 0 and out == "caught"

    def test_nested_try_except(self):
        out, _, rc = clython_run("try:\n    try:\n        raise ValueError('inner')\n    except ValueError:\n        print('inner caught')\n        raise TypeError('outer')\nexcept TypeError:\n    print('outer caught')")
        assert rc == 0 and out == "inner caught\nouter caught"

    def test_reraise(self):
        out, _, rc = clython_run("try:\n    try:\n        raise ValueError('x')\n    except ValueError:\n        raise\nexcept ValueError as e:\n    print(e)")
        assert rc == 0 and out == "x"
