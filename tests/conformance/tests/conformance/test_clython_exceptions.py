"""
Clython exception conformance tests.

Tests that the Python exception hierarchy works correctly through
the Clython interpreter. Exercises raise, try/except, exception
chaining, and the built-in exception class hierarchy.

Requires CLYTHON_BIN to be set.
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


# ── Basic raise ──────────────────────────────────────────────────────────────


class TestClythonRaise:
    """Test raise statement behavior."""

    def test_raise_value_error(self):
        """raise ValueError('msg') should produce non-zero exit and error output."""
        stdout, stderr, rc = clython_run("raise ValueError('bad value')")
        assert rc != 0, f"expected non-zero rc, got {rc}"
        assert "ValueError" in stderr, f"expected ValueError in stderr, got: {stderr!r}"

    def test_raise_type_error(self):
        stdout, stderr, rc = clython_run("raise TypeError('wrong type')")
        assert rc != 0
        assert "TypeError" in stderr

    def test_raise_runtime_error(self):
        stdout, stderr, rc = clython_run("raise RuntimeError('oops')")
        assert rc != 0
        assert "RuntimeError" in stderr

    def test_raise_exception_message(self):
        """The error message should appear in stderr."""
        stdout, stderr, rc = clython_run("raise ValueError('specific message here')")
        assert rc != 0
        assert "specific message here" in stderr

    def test_raise_no_args(self):
        """raise ValueError() with no message."""
        stdout, stderr, rc = clython_run("raise ValueError()")
        assert rc != 0
        assert "ValueError" in stderr

    def test_raise_key_error(self):
        stdout, stderr, rc = clython_run("raise KeyError('missing')")
        assert rc != 0
        assert "KeyError" in stderr

    def test_raise_index_error(self):
        stdout, stderr, rc = clython_run("raise IndexError('out of range')")
        assert rc != 0
        assert "IndexError" in stderr

    def test_raise_assertion_error(self):
        stdout, stderr, rc = clython_run("raise AssertionError('failed')")
        assert rc != 0
        assert "AssertionError" in stderr

    def test_raise_name_error(self):
        stdout, stderr, rc = clython_run("raise NameError('x')")
        assert rc != 0
        assert "NameError" in stderr

    def test_raise_zero_division_error(self):
        stdout, stderr, rc = clython_run("raise ZeroDivisionError('div by zero')")
        assert rc != 0
        assert "ZeroDivisionError" in stderr


# ── try / except ─────────────────────────────────────────────────────────────


class TestClythonTryExcept:
    """Test try/except catching exceptions."""

    def test_try_except_catches(self):
        """Basic try/except should catch and recover."""
        stdout, stderr, rc = clython_run(
            "try:\n    raise ValueError('oops')\nexcept ValueError:\n    print('caught')"
        )
        assert rc == 0 and stdout == "caught", f"rc={rc}, stdout={stdout!r}, stderr={stderr!r}"

    def test_try_except_with_variable(self):
        """except ValueError as e: should bind the exception."""
        stdout, stderr, rc = clython_run(
            "try:\n    raise ValueError('hello')\nexcept ValueError as e:\n    print(e)"
        )
        assert rc == 0 and stdout == "hello", f"rc={rc}, stdout={stdout!r}, stderr={stderr!r}"

    def test_try_except_wrong_type(self):
        """except TypeError should not catch ValueError."""
        stdout, stderr, rc = clython_run(
            "try:\n    raise ValueError('oops')\nexcept TypeError:\n    print('wrong')"
        )
        assert rc != 0, f"expected non-zero rc (uncaught ValueError), got {rc}"
        assert "ValueError" in stderr

    def test_try_except_base_class(self):
        """except Exception should catch ValueError (subclass)."""
        stdout, stderr, rc = clython_run(
            "try:\n    raise ValueError('oops')\nexcept Exception:\n    print('caught')"
        )
        assert rc == 0 and stdout == "caught", f"rc={rc}, stdout={stdout!r}, stderr={stderr!r}"

    def test_try_except_multiple_handlers(self):
        """Multiple except clauses, second one matches."""
        stdout, stderr, rc = clython_run(
            "try:\n"
            "    raise KeyError('k')\n"
            "except ValueError:\n"
            "    print('val')\n"
            "except KeyError:\n"
            "    print('key')"
        )
        assert rc == 0 and stdout == "key", f"rc={rc}, stdout={stdout!r}, stderr={stderr!r}"

    def test_try_no_exception(self):
        """try body succeeds — except not entered."""
        stdout, stderr, rc = clython_run(
            "try:\n    print('ok')\nexcept ValueError:\n    print('bad')"
        )
        assert rc == 0 and stdout == "ok", f"rc={rc}, stdout={stdout!r}, stderr={stderr!r}"

    def test_try_finally(self):
        """finally block always runs."""
        stdout, stderr, rc = clython_run(
            "try:\n    print('body')\nfinally:\n    print('cleanup')"
        )
        assert rc == 0 and stdout == "body\ncleanup", f"rc={rc}, stdout={stdout!r}, stderr={stderr!r}"

    def test_try_except_finally(self):
        """except + finally both work."""
        stdout, stderr, rc = clython_run(
            "try:\n"
            "    raise ValueError('x')\n"
            "except ValueError:\n"
            "    print('caught')\n"
            "finally:\n"
            "    print('done')"
        )
        assert rc == 0 and stdout == "caught\ndone", f"rc={rc}, stdout={stdout!r}, stderr={stderr!r}"

    def test_try_else_no_exception(self):
        """else runs when no exception is raised."""
        stdout, stderr, rc = clython_run(
            "try:\n"
            "    x = 1\n"
            "except ValueError:\n"
            "    print('error')\n"
            "else:\n"
            "    print('no error')"
        )
        assert rc == 0 and stdout == "no error", f"rc={rc}, stdout={stdout!r}, stderr={stderr!r}"

    def test_try_else_with_exception(self):
        """else does NOT run when exception is raised."""
        stdout, stderr, rc = clython_run(
            "try:\n"
            "    raise ValueError('x')\n"
            "except ValueError:\n"
            "    print('caught')\n"
            "else:\n"
            "    print('no error')"
        )
        assert rc == 0 and stdout == "caught", f"rc={rc}, stdout={stdout!r}, stderr={stderr!r}"


# ── Bare raise (re-raise) ───────────────────────────────────────────────────


class TestClythonReRaise:
    """Test bare raise to re-raise current exception."""

    def test_bare_raise_in_except(self):
        """Bare raise inside except re-raises the caught exception."""
        stdout, stderr, rc = clython_run(
            "try:\n"
            "    try:\n"
            "        raise ValueError('inner')\n"
            "    except ValueError:\n"
            "        raise\n"
            "except ValueError as e:\n"
            "    print(e)"
        )
        assert rc == 0 and stdout == "inner", f"rc={rc}, stdout={stdout!r}, stderr={stderr!r}"


# ── Exception chaining ──────────────────────────────────────────────────────


class TestClythonExceptionChaining:
    """Test raise ... from ... (exception chaining)."""

    @pytest.mark.xfail(reason="raise...from not yet implemented in evaluator")
    def test_raise_from(self):
        """raise X from Y should chain exceptions."""
        stdout, stderr, rc = clython_run(
            "try:\n"
            "    raise ValueError('new') from KeyError('original')\n"
            "except ValueError as e:\n"
            "    print(type(e).__name__)"
        )
        assert rc == 0 and stdout == "ValueError", f"rc={rc}, stdout={stdout!r}, stderr={stderr!r}"


# ── Implicit exceptions from operations ─────────────────────────────────────


class TestClythonImplicitExceptions:
    """Test exceptions raised by built-in operations."""

    def test_zero_division(self):
        """Division by zero should raise ZeroDivisionError."""
        stdout, stderr, rc = clython_run("x = 1 / 0")
        assert rc != 0
        assert "ZeroDivisionError" in stderr or "division by zero" in stderr.lower()

    def test_name_not_defined(self):
        """Referencing undefined variable should raise NameError."""
        stdout, stderr, rc = clython_run("print(undefined_variable)")
        assert rc != 0
        assert "NameError" in stderr or "not defined" in stderr

    def test_index_out_of_range(self):
        """List index out of range should raise IndexError."""
        stdout, stderr, rc = clython_run("x = [1, 2, 3]\nprint(x[10])")
        assert rc != 0
        assert "IndexError" in stderr or "index" in stderr.lower()

    def test_assert_false(self):
        """assert False should raise AssertionError."""
        stdout, stderr, rc = clython_run("assert False")
        assert rc != 0
        assert "AssertionError" in stderr or "assert" in stderr.lower()

    def test_assert_with_message(self):
        """assert False, 'msg' should include the message."""
        stdout, stderr, rc = clython_run("assert False, 'check failed'")
        assert rc != 0
        assert "check failed" in stderr or "AssertionError" in stderr


# ── Exception hierarchy ─────────────────────────────────────────────────────


class TestClythonExceptionHierarchy:
    """Test exception class inheritance relationships."""

    def test_value_error_is_exception(self):
        """ValueError should be catchable as Exception."""
        stdout, stderr, rc = clython_run(
            "try:\n    raise ValueError('x')\nexcept Exception:\n    print('caught')"
        )
        assert rc == 0 and stdout == "caught"

    def test_key_error_is_lookup_error(self):
        """KeyError should be catchable as LookupError."""
        stdout, stderr, rc = clython_run(
            "try:\n    raise KeyError('k')\nexcept LookupError:\n    print('caught')"
        )
        assert rc == 0 and stdout == "caught"

    def test_index_error_is_lookup_error(self):
        """IndexError should be catchable as LookupError."""
        stdout, stderr, rc = clython_run(
            "try:\n    raise IndexError('i')\nexcept LookupError:\n    print('caught')"
        )
        assert rc == 0 and stdout == "caught"

    def test_zero_division_is_arithmetic_error(self):
        """ZeroDivisionError should be catchable as ArithmeticError."""
        stdout, stderr, rc = clython_run(
            "try:\n    raise ZeroDivisionError('z')\nexcept ArithmeticError:\n    print('caught')"
        )
        assert rc == 0 and stdout == "caught"

    def test_type_error_is_exception(self):
        """TypeError should be catchable as Exception."""
        stdout, stderr, rc = clython_run(
            "try:\n    raise TypeError('t')\nexcept Exception:\n    print('caught')"
        )
        assert rc == 0 and stdout == "caught"
