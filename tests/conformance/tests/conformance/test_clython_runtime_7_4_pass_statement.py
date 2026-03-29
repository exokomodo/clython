"""Clython runtime tests — Section 7.4: Pass Statement.

Tests that the Clython interpreter correctly executes pass statements
as null operations in various contexts.
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


class TestPassStatementRuntime:
    def test_module_level_pass(self):
        """pass at module level is a no-op"""
        out, err, rc = clython_run("pass\nprint('ok')")
        assert rc == 0
        assert out == "ok"

    def test_pass_in_empty_function(self):
        """pass as sole body of function"""
        out, err, rc = clython_run(
            "def f():\n    pass\nf()\nprint('ok')"
        )
        assert rc == 0
        assert out == "ok"

    def test_pass_function_returns_none(self):
        """function with only pass returns None"""
        out, err, rc = clython_run(
            "def f():\n    pass\nprint(f() is None)"
        )
        assert rc == 0
        assert out == "True"

    def test_pass_in_empty_class(self):
        """pass as sole body of class"""
        out, err, rc = clython_run(
            "class C:\n    pass\nprint(C.__name__)"
        )
        assert rc == 0
        assert out == "C"

    def test_pass_in_if_block(self):
        """pass in if block is null operation"""
        out, err, rc = clython_run(
            "if True:\n    pass\nprint('after')"
        )
        assert rc == 0
        assert out == "after"

    def test_pass_in_else_block(self):
        """pass in else block is null operation"""
        out, err, rc = clython_run(
            "if False:\n    print('bad')\nelse:\n    pass\nprint('ok')"
        )
        assert rc == 0
        assert out == "ok"

    def test_pass_in_for_loop(self):
        """pass in for loop body"""
        out, err, rc = clython_run(
            "for i in range(3):\n    pass\nprint('done')"
        )
        assert rc == 0
        assert out == "done"

    def test_pass_in_while_loop(self):
        """pass in while loop body"""
        out, err, rc = clython_run(
            "i = 0\nwhile i < 3:\n    pass\n    i += 1\nprint(i)"
        )
        assert rc == 0
        assert out == "3"

    def test_pass_in_try_block(self):
        """pass in try block"""
        out, err, rc = clython_run(
            "try:\n    pass\nexcept Exception:\n    pass\nprint('ok')"
        )
        assert rc == 0
        assert out == "ok"

    def test_pass_in_except_block(self):
        """pass in except block silences exception"""
        out, err, rc = clython_run(
            "try:\n    raise ValueError('x')\nexcept ValueError:\n    pass\nprint('ok')"
        )
        assert rc == 0
        assert out == "ok"

    def test_pass_does_not_affect_variable(self):
        """pass does not alter local variable"""
        out, err, rc = clython_run(
            "x = 42\npass\nprint(x)"
        )
        assert rc == 0
        assert out == "42"

    def test_multiple_pass_statements(self):
        """multiple consecutive pass statements are all no-ops"""
        out, err, rc = clython_run(
            "def f():\n    pass\n    pass\n    pass\nf()\nprint('ok')"
        )
        assert rc == 0
        assert out == "ok"

    def test_pass_after_statement(self):
        """pass after a real statement has no effect"""
        out, err, rc = clython_run(
            "x = 10\npass\nprint(x)"
        )
        assert rc == 0
        assert out == "10"

    def test_pass_before_statement(self):
        """pass before a real statement has no effect"""
        out, err, rc = clython_run(
            "pass\nx = 10\nprint(x)"
        )
        assert rc == 0
        assert out == "10"

    def test_pass_in_nested_function(self):
        """pass in a nested (inner) function body"""
        out, err, rc = clython_run(
            "def outer():\n    def inner():\n        pass\n    return inner\nouter()()\nprint('ok')"
        )
        assert rc == 0
        assert out == "ok"

    def test_pass_in_method(self):
        """pass in a class method body"""
        out, err, rc = clython_run(
            "class C:\n    def m(self):\n        pass\nC().m()\nprint('ok')"
        )
        assert rc == 0
        assert out == "ok"

    @pytest.mark.xfail(reason="contextlib.contextmanager not supported in Clython")
    def test_pass_in_with_block(self):
        """pass as body of with statement"""
        out, err, rc = clython_run(
            "import contextlib\n"
            "@contextlib.contextmanager\n"
            "def ctx():\n    yield\n"
            "with ctx():\n    pass\nprint('ok')"
        )
        assert rc == 0
        assert out == "ok"

    def test_pass_in_finally_block(self):
        """pass in finally block"""
        out, err, rc = clython_run(
            "try:\n    pass\nfinally:\n    pass\nprint('ok')"
        )
        assert rc == 0
        assert out == "ok"

    def test_pass_empty_loop_iterations(self):
        """loop with pass body iterates correct number of times"""
        out, err, rc = clython_run(
            "count = 0\nfor i in range(5):\n    pass\n    count += 1\nprint(count)"
        )
        assert rc == 0
        assert out == "5"
