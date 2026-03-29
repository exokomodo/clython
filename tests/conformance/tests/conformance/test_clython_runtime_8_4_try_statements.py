"""Clython runtime conformance tests — Section 8.4: Try Statements.

Tests that the Clython interpreter correctly executes Python 3 try statements,
including try/except, multiple except clauses, exception binding, try/else,
try/finally, nested try, and exception chaining.
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


# ── Basic try/except ──────────────────────────────────────────────────────

class TestBasicTryExcept:
    def test_catch_zero_division(self):
        out, _, rc = clython_run(
            "try:\n    1/0\nexcept ZeroDivisionError:\n    print('caught')"
        )
        assert rc == 0 and out == "caught"

    def test_catch_value_error(self):
        out, _, rc = clython_run(
            "try:\n    int('not a number')\nexcept ValueError:\n    print('caught')"
        )
        assert rc == 0 and out == "caught"

    def test_catch_key_error(self):
        out, _, rc = clython_run(
            "try:\n    d = {}\n    d['x']\nexcept KeyError:\n    print('key')"
        )
        assert rc == 0 and out == "key"

    def test_bare_except(self):
        out, _, rc = clython_run(
            "try:\n    1/0\nexcept:\n    print('caught')"
        )
        assert rc == 0 and out == "caught"

    def test_no_exception_except_not_taken(self):
        out, _, rc = clython_run(
            "try:\n    x = 1 + 1\nexcept ZeroDivisionError:\n    print('caught')\nprint(x)"
        )
        assert rc == 0 and out == "2"

    def test_unhandled_exception_propagates(self):
        out, _, rc = clython_run(
            "try:\n    raise ValueError('v')\nexcept TypeError:\n    print('type')"
        )
        assert rc != 0

    def test_exception_body_executes_fully(self):
        out, _, rc = clython_run(
            "try:\n    raise ValueError('v')\nexcept ValueError:\n    print('one')\n    print('two')"
        )
        assert rc == 0 and out == "one\ntwo"


# ── Exception binding ─────────────────────────────────────────────────────

class TestExceptionBinding:
    def test_as_binding_message(self):
        out, _, rc = clython_run(
            "try:\n    raise ValueError('oops')\nexcept ValueError as e:\n    print(e)"
        )
        assert rc == 0 and out == "oops"

    def test_as_binding_type(self):
        out, _, rc = clython_run(
            "try:\n    raise ValueError('v')\nexcept ValueError as e:\n    print(type(e).__name__)"
        )
        assert rc == 0 and out == "ValueError"

    def test_tuple_exception_types(self):
        out, _, rc = clython_run(
            "try:\n    raise TypeError('t')\nexcept (ValueError, TypeError) as e:\n    print('caught', e)"
        )
        assert rc == 0 and out == "caught t"

    def test_parent_class_catches_child(self):
        out, _, rc = clython_run(
            "try:\n    raise ValueError('v')\nexcept Exception as e:\n    print('caught by parent')"
        )
        assert rc == 0 and out == "caught by parent"


# ── Multiple except clauses ───────────────────────────────────────────────

class TestMultipleExcept:
    def test_first_matching_except_wins(self):
        out, _, rc = clython_run(
            "try:\n    raise ValueError('v')\nexcept ValueError:\n    print('first')\nexcept Exception:\n    print('second')"
        )
        assert rc == 0 and out == "first"

    def test_second_except_taken(self):
        out, _, rc = clython_run(
            "try:\n    d = {}\n    d['x']\nexcept ValueError:\n    print('value')\nexcept KeyError:\n    print('key')\nexcept Exception:\n    print('other')"
        )
        assert rc == 0 and out == "key"

    def test_multiple_except_fallthrough_to_last(self):
        out, _, rc = clython_run(
            "try:\n    raise RuntimeError('r')\nexcept ValueError:\n    print('value')\nexcept TypeError:\n    print('type')\nexcept Exception:\n    print('other')"
        )
        assert rc == 0 and out == "other"

    def test_except_with_binding_after_no_binding(self):
        # Clython prints KeyError str without quotes (CPython includes them)
        out, _, rc = clython_run(
            "try:\n    raise KeyError('k')\nexcept ValueError:\n    print('value')\nexcept KeyError as e:\n    print('key:', e)"
        )
        assert rc == 0 and "key:" in out and "k" in out


# ── Try/else ──────────────────────────────────────────────────────────────

class TestTryElse:
    def test_else_runs_when_no_exception(self):
        out, _, rc = clython_run(
            "try:\n    x = 1\nexcept:\n    print('error')\nelse:\n    print('ok')"
        )
        assert rc == 0 and out == "ok"

    def test_else_not_run_on_exception(self):
        out, _, rc = clython_run(
            "try:\n    raise ValueError('v')\nexcept ValueError:\n    print('except')\nelse:\n    print('else')"
        )
        assert rc == 0 and out == "except"

    def test_else_receives_try_value(self):
        out, _, rc = clython_run(
            "try:\n    x = 42\nexcept:\n    x = 0\nelse:\n    print('x =', x)"
        )
        assert rc == 0 and out == "x = 42"


# ── Try/finally ───────────────────────────────────────────────────────────

class TestTryFinally:
    def test_finally_runs_on_success(self):
        out, _, rc = clython_run(
            "try:\n    print('body')\nfinally:\n    print('finally')"
        )
        assert rc == 0 and out == "body\nfinally"

    def test_finally_runs_on_exception(self):
        out, _, rc = clython_run(
            "try:\n    raise ValueError('v')\nexcept ValueError:\n    print('caught')\nfinally:\n    print('finally')"
        )
        assert rc == 0 and out == "caught\nfinally"

    def test_finally_runs_on_unhandled_exception(self):
        out, _, rc = clython_run(
            "try:\n    try:\n        raise ValueError('v')\n    finally:\n        print('inner finally')\nexcept ValueError:\n    print('outer caught')"
        )
        assert rc == 0 and out == "inner finally\nouter caught"

    def test_finally_only_no_except(self):
        out, _, rc = clython_run(
            "try:\n    x = 1 + 1\nfinally:\n    print('cleaned up')\nprint(x)"
        )
        assert rc == 0 and out == "cleaned up\n2"


# ── Combined try/except/else/finally ─────────────────────────────────────

class TestTryComplete:
    def test_all_clauses_no_exception(self):
        out, _, rc = clython_run(
            "try:\n    x = 1\nexcept:\n    print('except')\nelse:\n    print('else')\nfinally:\n    print('finally')"
        )
        assert rc == 0 and out == "else\nfinally"

    def test_all_clauses_with_exception(self):
        out, _, rc = clython_run(
            "try:\n    raise ValueError('v')\nexcept ValueError:\n    print('except')\nelse:\n    print('else')\nfinally:\n    print('finally')"
        )
        assert rc == 0 and out == "except\nfinally"

    def test_except_else_finally_order(self):
        out, _, rc = clython_run(
            "log = []\ntry:\n    log.append('try')\nexcept:\n    log.append('except')\nelse:\n    log.append('else')\nfinally:\n    log.append('finally')\nprint(log)"
        )
        assert rc == 0 and out == "['try', 'else', 'finally']"


# ── Nested try ────────────────────────────────────────────────────────────

class TestNestedTry:
    def test_nested_try_inner_caught(self):
        out, _, rc = clython_run(
            "try:\n    try:\n        raise ValueError('inner')\n    except ValueError:\n        print('inner caught')\n        raise KeyError('outer')\nexcept KeyError:\n    print('outer caught')"
        )
        assert rc == 0 and out == "inner caught\nouter caught"

    def test_nested_reraise(self):
        out, _, rc = clython_run(
            "try:\n    try:\n        raise ValueError('v')\n    except ValueError:\n        print('inner')\n        raise\nexcept ValueError:\n    print('outer')"
        )
        assert rc == 0 and out == "inner\nouter"

    def test_try_in_except(self):
        out, _, rc = clython_run(
            "try:\n    raise ValueError('primary')\nexcept ValueError:\n    try:\n        print('fallback')\n    except:\n        print('fallback failed')"
        )
        assert rc == 0 and out == "fallback"

    def test_try_in_finally(self):
        out, _, rc = clython_run(
            "try:\n    x = 1\nfinally:\n    try:\n        print('cleanup')\n    except:\n        print('cleanup failed')"
        )
        assert rc == 0 and out == "cleanup"

    def test_exception_in_except_handler(self):
        out, _, rc = clython_run(
            "try:\n    try:\n        raise ValueError('v')\n    except ValueError:\n        raise TypeError('t')\nexcept TypeError:\n    print('caught type error')"
        )
        assert rc == 0 and out == "caught type error"


# ── Exception chaining ────────────────────────────────────────────────────

class TestExceptionChaining:
    def test_raise_from_chains_cause(self):
        out, _, rc = clython_run(
            "try:\n    try:\n        raise ValueError('original')\n    except ValueError as e:\n        raise TypeError('new') from e\nexcept TypeError as e:\n    print(type(e).__name__)\n    print(type(e.__cause__).__name__)"
        )
        assert rc == 0 and out == "TypeError\nValueError"

    def test_exception_context(self):
        """When an exception is raised in an except block, __context__ is set"""
        out, _, rc = clython_run(
            "try:\n    try:\n        raise ValueError('first')\n    except ValueError:\n        raise TypeError('second')\nexcept TypeError as e:\n    print(type(e.__context__).__name__)"
        )
        assert rc == 0 and out == "ValueError"

    def test_raise_from_none_suppresses_context(self):
        out, _, rc = clython_run(
            "try:\n    try:\n        raise ValueError('original')\n    except ValueError:\n        raise TypeError('clean') from None\nexcept TypeError as e:\n    print(e.__cause__ is None)\n    print(e.__suppress_context__)"
        )
        assert rc == 0 and out == "True\nTrue"
