"""Clython runtime tests — Section 7.8: Raise Statements.

Tests that the Clython interpreter correctly raises exceptions,
supports exception chaining, and re-raises.
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


class TestRaiseStatementRuntime:
    def test_raise_exception_class(self):
        """raise ExceptionClass raises an instance of that class"""
        out, err, rc = clython_run(
            "try:\n    raise ValueError\nexcept ValueError:\n    print('caught')"
        )
        assert rc == 0
        assert out == "caught"

    def test_raise_exception_instance(self):
        """raise ExceptionClass('msg') raises with message"""
        out, err, rc = clython_run(
            "try:\n    raise ValueError('bad')\nexcept ValueError as e:\n    print(str(e))"
        )
        assert rc == 0
        assert out == "bad"

    def test_raise_runtime_error(self):
        """raise RuntimeError works"""
        out, err, rc = clython_run(
            "try:\n    raise RuntimeError('oops')\nexcept RuntimeError as e:\n    print(str(e))"
        )
        assert rc == 0
        assert out == "oops"

    def test_raise_type_error(self):
        """raise TypeError works"""
        out, err, rc = clython_run(
            "try:\n    raise TypeError('type mismatch')\nexcept TypeError as e:\n    print(str(e))"
        )
        assert rc == 0
        assert out == "type mismatch"

    def test_raise_bare_reraise(self):
        """bare raise re-raises current exception"""
        out, err, rc = clython_run(
            "try:\n"
            "    try:\n"
            "        raise ValueError('original')\n"
            "    except ValueError:\n"
            "        raise\n"
            "except ValueError as e:\n"
            "    print(str(e))"
        )
        assert rc == 0
        assert out == "original"

    def test_raise_uncaught_exits_nonzero(self):
        """uncaught raise causes non-zero exit"""
        out, err, rc = clython_run("raise ValueError('fail')")
        assert rc != 0

    def test_raise_in_function(self):
        """raise inside a function propagates to caller"""
        out, err, rc = clython_run(
            "def f():\n    raise ValueError('from f')\n"
            "try:\n    f()\nexcept ValueError as e:\n    print(str(e))"
        )
        assert rc == 0
        assert out == "from f"

    def test_raise_exception_has_args(self):
        """exception .args attribute is set correctly"""
        out, err, rc = clython_run(
            "try:\n    raise ValueError('a', 'b')\nexcept ValueError as e:\n    print(e.args)"
        )
        assert rc == 0
        assert out == "('a', 'b')"

    def test_raise_zero_args(self):
        """raise ExceptionClass() with no args has empty args"""
        out, err, rc = clython_run(
            "try:\n    raise ValueError()\nexcept ValueError as e:\n    print(e.args)"
        )
        assert rc == 0
        assert out == "()"

    def test_raise_from_chains_exception(self):
        """raise ... from ... sets __cause__"""
        out, err, rc = clython_run(
            "try:\n"
            "    try:\n"
            "        raise OSError('original')\n"
            "    except OSError as orig:\n"
            "        raise RuntimeError('wrapped') from orig\n"
            "except RuntimeError as e:\n"
            "    print(type(e.__cause__).__name__)"
        )
        assert rc == 0
        assert out == "OSError"

    def test_raise_from_none_suppresses_context(self):
        """raise ... from None sets __suppress_context__"""
        out, err, rc = clython_run(
            "try:\n"
            "    try:\n"
            "        raise OSError('original')\n"
            "    except OSError:\n"
            "        raise RuntimeError('clean') from None\n"
            "except RuntimeError as e:\n"
            "    print(e.__suppress_context__)"
        )
        assert rc == 0
        assert out == "True"

    def test_raise_sets_implicit_context(self):
        """raise inside except sets __context__ implicitly"""
        out, err, rc = clython_run(
            "try:\n"
            "    try:\n"
            "        raise ValueError('first')\n"
            "    except ValueError:\n"
            "        raise RuntimeError('second')\n"
            "except RuntimeError as e:\n"
            "    print(type(e.__context__).__name__)"
        )
        assert rc == 0
        assert out == "ValueError"

    def test_raise_base_exception(self):
        """raise BaseException works (not just Exception)"""
        out, err, rc = clython_run(
            "try:\n    raise BaseException('base')\nexcept BaseException as e:\n    print(str(e))"
        )
        assert rc == 0
        assert out == "base"

    def test_raise_key_error(self):
        """raise KeyError with key value"""
        out, err, rc = clython_run(
            "try:\n    raise KeyError('missing_key')\nexcept KeyError as e:\n    print(repr(e))"
        )
        assert rc == 0
        assert "missing_key" in out

    def test_raise_in_except_different_type(self):
        """raise different exception type inside except"""
        out, err, rc = clython_run(
            "try:\n"
            "    try:\n"
            "        raise ValueError()\n"
            "    except ValueError:\n"
            "        raise TypeError('converted')\n"
            "except TypeError as e:\n"
            "    print(str(e))"
        )
        assert rc == 0
        assert out == "converted"

    def test_raise_in_finally(self):
        """raise in finally overrides try exception"""
        out, err, rc = clython_run(
            "try:\n"
            "    try:\n"
            "        raise ValueError('try')\n"
            "    finally:\n"
            "        raise RuntimeError('finally')\n"
            "except RuntimeError as e:\n"
            "    print(str(e))"
        )
        assert rc == 0
        assert out == "finally"

    def test_custom_exception_class(self):
        """raise custom exception class"""
        out, err, rc = clython_run(
            "class MyError(Exception):\n    pass\n"
            "try:\n    raise MyError('custom')\nexcept MyError as e:\n    print(str(e))"
        )
        assert rc == 0
        assert out == "custom"

    def test_raise_outside_except_bare_raises_runtime_error(self):
        """bare raise outside except raises RuntimeError"""
        out, err, rc = clython_run(
            "try:\n    raise\nexcept RuntimeError:\n    print('RuntimeError')"
        )
        assert rc == 0
        assert out == "RuntimeError"
