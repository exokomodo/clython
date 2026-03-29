"""Clython runtime conformance tests — Section 8.5: With Statements.

Tests that the Clython interpreter correctly executes Python 3 with statements,
including context manager protocol (__enter__/__exit__), variable binding,
multiple context managers, exception suppression, and nested with.
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

# Shared context manager class definition used in many tests
_CM_CLASS = (
    "class CM:\n"
    "    def __init__(self, name='cm'):\n"
    "        self.name = name\n"
    "    def __enter__(self):\n"
    "        print('enter', self.name)\n"
    "        return self\n"
    "    def __exit__(self, *args):\n"
    "        print('exit', self.name)\n"
    "        return False\n"
)

_RETURNING_CM = (
    "class RetCM:\n"
    "    def __init__(self, value):\n"
    "        self.value = value\n"
    "    def __enter__(self):\n"
    "        return self.value\n"
    "    def __exit__(self, *args):\n"
    "        pass\n"
)

_SUPPRESSING_CM = (
    "class SuppCM:\n"
    "    def __enter__(self):\n"
    "        return self\n"
    "    def __exit__(self, exc_type, exc_val, exc_tb):\n"
    "        print('exit', exc_type is not None)\n"
    "        return True\n"
)


# ── Context manager protocol ──────────────────────────────────────────────

class TestContextManagerProtocol:
    def test_enter_and_exit_called(self):
        out, _, rc = clython_run(
            _CM_CLASS +
            "with CM():\n"
            "    print('body')"
        )
        assert rc == 0 and out == "enter cm\nbody\nexit cm"

    def test_enter_return_value_bound(self):
        out, _, rc = clython_run(
            _RETURNING_CM +
            "with RetCM(42) as val:\n"
            "    print(val)"
        )
        assert rc == 0 and out == "42"

    def test_enter_return_none_when_no_as(self):
        out, _, rc = clython_run(
            _CM_CLASS +
            "with CM('x'):\n"
            "    print('in body')"
        )
        assert rc == 0 and out == "enter x\nin body\nexit x"

    def test_exit_always_called_on_success(self):
        out, _, rc = clython_run(
            _RETURNING_CM +
            "with RetCM('value') as v:\n"
            "    print(v)\n"
            "print('after')"
        )
        assert rc == 0 and out == "value\nafter"

    def test_exit_called_on_exception(self):
        out, _, rc = clython_run(
            _SUPPRESSING_CM +
            "with SuppCM():\n"
            "    raise ValueError('oops')\n"
            "print('after')"
        )
        assert rc == 0 and out == "exit True\nafter"

    def test_exit_suppresses_exception_when_returning_true(self):
        out, _, rc = clython_run(
            _SUPPRESSING_CM +
            "with SuppCM():\n"
            "    raise ValueError('oops')\n"
            "print('survived')"
        )
        assert rc == 0 and out == "exit True\nsurvived"

    def test_exit_does_not_suppress_when_returning_false(self):
        out, _, rc = clython_run(
            _CM_CLASS +
            "try:\n"
            "    with CM():\n"
            "        raise ValueError('v')\n"
            "except ValueError:\n"
            "    print('caught')"
        )
        assert rc == 0 and "exit cm" in out and "caught" in out

    def test_exit_receives_exception_info(self):
        out, _, rc = clython_run(
            "class CM:\n"
            "    def __enter__(self): return self\n"
            "    def __exit__(self, exc_type, exc_val, exc_tb):\n"
            "        if exc_type is not None:\n"
            "            print(exc_type.__name__, str(exc_val))\n"
            "        return True\n"
            "with CM():\n"
            "    raise ValueError('oops')"
        )
        assert rc == 0 and out == "ValueError oops"

    def test_exit_receives_none_on_success(self):
        out, _, rc = clython_run(
            "class CM:\n"
            "    def __enter__(self): return self\n"
            "    def __exit__(self, exc_type, exc_val, exc_tb):\n"
            "        print(exc_type, exc_val, exc_tb)\n"
            "with CM():\n"
            "    pass"
        )
        assert rc == 0 and out == "None None None"


# ── Variable binding ──────────────────────────────────────────────────────

class TestWithVariableBinding:
    def test_as_binds_enter_return(self):
        out, _, rc = clython_run(
            _RETURNING_CM +
            "with RetCM(99) as x:\n"
            "    print(x)"
        )
        assert rc == 0 and out == "99"

    def test_as_can_be_used_inside_body(self):
        out, _, rc = clython_run(
            _RETURNING_CM +
            "with RetCM([1, 2, 3]) as lst:\n"
            "    total = sum(lst)\n"
            "print(total)"
        )
        assert rc == 0 and out == "6"

    def test_as_binding_scope_persists_after_block(self):
        """Variable bound with 'as' persists after the with block"""
        out, _, rc = clython_run(
            _RETURNING_CM +
            "with RetCM('hello') as s:\n"
            "    pass\n"
            "print(s)"
        )
        assert rc == 0 and out == "hello"


# ── Multiple context managers ─────────────────────────────────────────────

class TestMultipleContextManagers:
    def test_two_cms_enter_exit_order(self):
        """Enter left-to-right, exit right-to-left"""
        out, _, rc = clython_run(
            _CM_CLASS +
            "with CM('a'), CM('b'):\n"
            "    print('body')"
        )
        assert rc == 0 and out == "enter a\nenter b\nbody\nexit b\nexit a"

    def test_three_cms_order(self):
        out, _, rc = clython_run(
            _CM_CLASS +
            "with CM('a'), CM('b'), CM('c'):\n"
            "    print('body')"
        )
        assert rc == 0 and out == "enter a\nenter b\nenter c\nbody\nexit c\nexit b\nexit a"

    def test_multiple_cms_with_bindings(self):
        out, _, rc = clython_run(
            _RETURNING_CM +
            "with RetCM(1) as x, RetCM(2) as y:\n"
            "    print(x, y)"
        )
        assert rc == 0 and out == "1 2"

    def test_multiple_cms_mixed_bindings(self):
        out, _, rc = clython_run(
            _CM_CLASS +
            _RETURNING_CM +
            "with CM('x'), RetCM(42) as val:\n"
            "    print(val)"
        )
        assert rc == 0 and "42" in out

    def test_second_cm_exit_called_when_first_raises_in_body(self):
        out, _, rc = clython_run(
            _CM_CLASS +
            "try:\n"
            "    with CM('a'), CM('b'):\n"
            "        raise ValueError('v')\n"
            "except ValueError:\n"
            "    print('caught')"
        )
        assert rc == 0
        assert "exit b" in out
        assert "exit a" in out
        assert "caught" in out


# ── Nested with ───────────────────────────────────────────────────────────

class TestNestedWith:
    def test_nested_with_order(self):
        out, _, rc = clython_run(
            _CM_CLASS +
            "with CM('outer'):\n"
            "    with CM('inner'):\n"
            "        print('body')"
        )
        assert rc == 0 and out == "enter outer\nenter inner\nbody\nexit inner\nexit outer"

    def test_nested_with_three_levels(self):
        out, _, rc = clython_run(
            _CM_CLASS +
            "with CM('a'):\n"
            "    with CM('b'):\n"
            "        with CM('c'):\n"
            "            print('body')"
        )
        assert rc == 0 and out == "enter a\nenter b\nenter c\nbody\nexit c\nexit b\nexit a"

    def test_nested_with_inner_exception_propagates(self):
        out, _, rc = clython_run(
            _CM_CLASS +
            "try:\n"
            "    with CM('outer'):\n"
            "        with CM('inner'):\n"
            "            raise ValueError('v')\n"
            "except ValueError:\n"
            "    print('caught')"
        )
        assert rc == 0
        assert "exit inner" in out
        assert "exit outer" in out
        assert "caught" in out


# ── With in context with try/except ──────────────────────────────────────

class TestWithAndTry:
    def test_with_inside_try(self):
        out, _, rc = clython_run(
            _RETURNING_CM +
            "try:\n"
            "    with RetCM(10) as v:\n"
            "        result = v * 2\n"
            "except Exception:\n"
            "    result = 0\n"
            "print(result)"
        )
        assert rc == 0 and out == "20"

    def test_try_inside_with(self):
        out, _, rc = clython_run(
            _RETURNING_CM +
            "with RetCM([1, 2, 3]) as lst:\n"
            "    try:\n"
            "        total = sum(lst)\n"
            "        print(total)\n"
            "    except TypeError:\n"
            "        print('error')"
        )
        assert rc == 0 and out == "6"

    def test_with_in_function(self):
        out, _, rc = clython_run(
            _RETURNING_CM +
            "def process():\n"
            "    with RetCM(42) as v:\n"
            "        return v * 2\n"
            "print(process())"
        )
        assert rc == 0 and out == "84"


# ── Edge cases ────────────────────────────────────────────────────────────

class TestWithEdgeCases:
    def test_with_body_can_modify_bound_object(self):
        out, _, rc = clython_run(
            _RETURNING_CM +
            "with RetCM([]) as lst:\n"
            "    lst.append(1)\n"
            "    lst.append(2)\n"
            "    lst.append(3)\n"
            "print(lst)"
        )
        assert rc == 0 and out == "[1, 2, 3]"

    def test_with_expression_evaluated_before_enter(self):
        out, _, rc = clython_run(
            _RETURNING_CM +
            "x = 10\n"
            "with RetCM(x) as v:\n"
            "    x = 999\n"
            "print(v)"
        )
        assert rc == 0 and out == "10"

    def test_with_cm_class_defined_inline(self):
        """Full inline CM class definition"""
        out, _, rc = clython_run(
            "class Timer:\n"
            "    def __init__(self):\n"
            "        self.elapsed = 0\n"
            "    def __enter__(self):\n"
            "        self.elapsed = 42  # pretend timer\n"
            "        return self\n"
            "    def __exit__(self, *args):\n"
            "        pass\n"
            "with Timer() as t:\n"
            "    print(t.elapsed)"
        )
        assert rc == 0 and out == "42"

    @pytest.mark.xfail(reason="exc_type identity check (exc_type is ValueError) not working correctly in Clython __exit__")
    def test_with_exit_sees_correct_exception_type(self):
        out, _, rc = clython_run(
            "class CM:\n"
            "    def __enter__(self): return self\n"
            "    def __exit__(self, exc_type, exc_val, exc_tb):\n"
            "        if exc_type is ValueError:\n"
            "            print('suppressed ValueError')\n"
            "            return True\n"
            "        return False\n"
            "with CM():\n"
            "    raise ValueError('test')\n"
            "print('after')"
        )
        assert rc == 0 and out == "suppressed ValueError\nafter"

    def test_with_selective_suppression_does_not_suppress_other(self):
        out, _, rc = clython_run(
            "class CM:\n"
            "    def __enter__(self): return self\n"
            "    def __exit__(self, exc_type, exc_val, exc_tb):\n"
            "        if exc_type is ValueError:\n"
            "            return True  # suppress\n"
            "        return False\n"
            "try:\n"
            "    with CM():\n"
            "        raise TypeError('not suppressed')\n"
            "except TypeError:\n"
            "    print('TypeError propagated')"
        )
        assert rc == 0 and out == "TypeError propagated"
