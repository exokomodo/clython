"""Clython conformance tests — Section 7: Simple Statements.

Tests that the Clython interpreter correctly implements Python 3.12 simple
statements: expression statements, assignments, assert, pass, del, return,
yield, raise, break, continue, import, global, nonlocal.
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


# ── 7.1 Expression Statements ─────────────────────────────────────────────

class TestSection71ExpressionStatements:
    def test_standalone_expression(self):
        out, _, rc = clython_run("x = 5\nx")
        assert rc == 0  # no output, no error

    def test_function_call_as_statement(self):
        out, _, rc = clython_run("print('hello')")
        assert rc == 0 and out == "hello"

    def test_multiple_expression_statements(self):
        out, _, rc = clython_run("x = 1\ny = 2\nprint(x + y)")
        assert rc == 0 and out == "3"


# ── 7.2 Assignment Statements ─────────────────────────────────────────────

class TestSection72AssignmentStatements:
    def test_simple_assignment(self):
        out, _, rc = clython_run("x = 42\nprint(x)")
        assert rc == 0 and out == "42"

    def test_multiple_targets(self):
        out, _, rc = clython_run("x = y = 10\nprint(x, y)")
        assert rc == 0 and out == "10 10"

    def test_tuple_unpacking(self):
        out, _, rc = clython_run("a, b = 1, 2\nprint(a, b)")
        assert rc == 0 and out == "1 2"

    def test_tuple_unpacking_list(self):
        out, _, rc = clython_run("a, b, c = [10, 20, 30]\nprint(a, b, c)")
        assert rc == 0 and out == "10 20 30"

    def test_swap(self):
        out, _, rc = clython_run("a, b = 1, 2\na, b = b, a\nprint(a, b)")
        assert rc == 0 and out == "2 1"

    def test_augmented_assignment_add(self):
        out, _, rc = clython_run("x = 5\nx += 3\nprint(x)")
        assert rc == 0 and out == "8"

    def test_augmented_assignment_mul(self):
        out, _, rc = clython_run("x = 4\nx *= 3\nprint(x)")
        assert rc == 0 and out == "12"

    def test_augmented_assignment_sub(self):
        out, _, rc = clython_run("x = 10\nx -= 3\nprint(x)")
        assert rc == 0 and out == "7"

    def test_augmented_assignment_floordiv(self):
        out, _, rc = clython_run("x = 17\nx //= 3\nprint(x)")
        assert rc == 0 and out == "5"

    def test_augmented_assignment_mod(self):
        out, _, rc = clython_run("x = 17\nx %= 5\nprint(x)")
        assert rc == 0 and out == "2"

    def test_augmented_assignment_pow(self):
        out, _, rc = clython_run("x = 2\nx **= 10\nprint(x)")
        assert rc == 0 and out == "1024"

    def test_list_item_assignment(self):
        out, _, rc = clython_run("x = [1, 2, 3]\nx[1] = 99\nprint(x)")
        assert rc == 0 and out == "[1, 99, 3]"

    def test_dict_item_assignment(self):
        out, _, rc = clython_run("d = {'a': 1}\nd['b'] = 2\nprint(d['b'])")
        assert rc == 0 and out == "2"

    def test_nested_unpacking(self):
        out, _, rc = clython_run("(a, b), c = [1, 2], 3\nprint(a, b, c)")
        assert rc == 0 and out == "1 2 3"

    def test_starred_unpacking(self):
        out, _, rc = clython_run("a, *b, c = [1, 2, 3, 4, 5]\nprint(a, b, c)")
        assert rc == 0 and out == "1 [2, 3, 4] 5"


# ── 7.3 Assert Statement ──────────────────────────────────────────────────

class TestSection73AssertStatement:
    def test_assert_true(self):
        out, _, rc = clython_run("assert True")
        assert rc == 0

    def test_assert_false(self):
        _, err, rc = clython_run("assert False")
        assert rc != 0 and "AssertionError" in err or "AssertError" in err

    def test_assert_with_message(self):
        _, err, rc = clython_run("assert False, 'custom message'")
        assert rc != 0 and "custom message" in err

    def test_assert_expression(self):
        out, _, rc = clython_run("x = 5\nassert x > 0\nprint('ok')")
        assert rc == 0 and out == "ok"

    def test_assert_caught_by_except(self):
        out, _, rc = clython_run(
            "try:\n    assert False, 'oops'\nexcept AssertionError as e:\n    print('caught:', e)"
        )
        assert rc == 0 and "caught:" in out


# ── 7.4 Pass Statement ────────────────────────────────────────────────────

class TestSection74PassStatement:
    def test_pass_standalone(self):
        out, _, rc = clython_run("pass\nprint('ok')")
        assert rc == 0 and out == "ok"

    def test_pass_in_function(self):
        out, _, rc = clython_run("def f():\n    pass\nf()\nprint('ok')")
        assert rc == 0 and out == "ok"

    def test_pass_in_if(self):
        out, _, rc = clython_run("if True:\n    pass\nprint('ok')")
        assert rc == 0 and out == "ok"

    def test_pass_in_class(self):
        out, _, rc = clython_run("class C:\n    pass\nprint(type(C).__name__)")
        assert rc == 0


# ── 7.5 Del Statement ─────────────────────────────────────────────────────

class TestSection75DelStatement:
    def test_del_variable(self):
        out, _, rc = clython_run(
            "x = 5\ndel x\ntry:\n    print(x)\nexcept NameError:\n    print('deleted')"
        )
        assert rc == 0 and out == "deleted"

    def test_del_list_item(self):
        out, _, rc = clython_run("x = [1, 2, 3]\ndel x[1]\nprint(x)")
        assert rc == 0 and out == "[1, 3]"

    def test_del_dict_item(self):
        out, _, rc = clython_run("d = {'a': 1, 'b': 2}\ndel d['a']\nprint(len(d))")
        assert rc == 0 and out == "1"


# ── 7.6 Return Statement ──────────────────────────────────────────────────

class TestSection76ReturnStatement:
    def test_return_value(self):
        out, _, rc = clython_run("def f():\n    return 42\nprint(f())")
        assert rc == 0 and out == "42"

    def test_return_none(self):
        out, _, rc = clython_run("def f():\n    return\nprint(f())")
        assert rc == 0 and out == "None"

    def test_implicit_return(self):
        out, _, rc = clython_run("def f():\n    x = 1\nprint(f())")
        assert rc == 0 and out == "None"

    def test_return_tuple(self):
        out, _, rc = clython_run("def f():\n    return 1, 2, 3\nprint(f())")
        assert rc == 0 and out == "(1, 2, 3)"

    def test_return_in_loop(self):
        out, _, rc = clython_run(
            "def f():\n    for i in range(10):\n        if i == 5:\n            return i\nprint(f())"
        )
        assert rc == 0 and out == "5"


# ── 7.8 Raise Statement ───────────────────────────────────────────────────

class TestSection78RaiseStatement:
    def test_raise_exception(self):
        _, err, rc = clython_run("raise ValueError('test')")
        assert rc != 0 and "ValueError" in err and "test" in err

    def test_raise_caught(self):
        out, _, rc = clython_run(
            "try:\n    raise ValueError('boom')\nexcept ValueError as e:\n    print('caught:', e)"
        )
        assert rc == 0 and "caught: boom" in out

    def test_raise_base_exception(self):
        out, _, rc = clython_run(
            "try:\n    raise Exception('generic')\nexcept Exception as e:\n    print('caught:', e)"
        )
        assert rc == 0 and "caught: generic" in out

    def test_bare_raise(self):
        out, _, rc = clython_run(
            "try:\n    try:\n        raise ValueError('inner')\n    except ValueError:\n        raise\nexcept ValueError as e:\n    print('re-raised:', e)"
        )
        assert rc == 0 and "re-raised: inner" in out

    def test_raise_type_error(self):
        out, _, rc = clython_run(
            "try:\n    raise TypeError('bad type')\nexcept TypeError as e:\n    print('caught:', e)"
        )
        assert rc == 0 and "caught: bad type" in out


# ── 7.9 Break Statement ───────────────────────────────────────────────────

class TestSection79BreakStatement:
    def test_break_while(self):
        out, _, rc = clython_run(
            "i = 0\nwhile True:\n    if i == 3:\n        break\n    i += 1\nprint(i)"
        )
        assert rc == 0 and out == "3"

    def test_break_for(self):
        out, _, rc = clython_run(
            "for i in range(10):\n    if i == 5:\n        break\nprint(i)"
        )
        assert rc == 0 and out == "5"

    def test_break_nested(self):
        out, _, rc = clython_run(
            "found = False\nfor i in range(5):\n    for j in range(5):\n        if j == 2:\n            break\n    if i == 3:\n        found = True\n        break\nprint(i, found)"
        )
        assert rc == 0 and out == "3 True"


# ── 7.10 Continue Statement ───────────────────────────────────────────────

class TestSection710ContinueStatement:
    def test_continue_for(self):
        out, _, rc = clython_run(
            "result = []\nfor i in range(6):\n    if i % 2 == 0:\n        continue\n    result.append(i)\nprint(result)"
        )
        assert rc == 0 and out == "[1, 3, 5]"

    def test_continue_while(self):
        out, _, rc = clython_run(
            "i = 0\nresult = []\nwhile i < 6:\n    i += 1\n    if i % 2 == 0:\n        continue\n    result.append(i)\nprint(result)"
        )
        assert rc == 0 and out == "[1, 3, 5]"


# ── 7.11 Import Statement ─────────────────────────────────────────────────

class TestSection711ImportStatement:
    def test_import_math(self):
        out, _, rc = clython_run("import math\nprint(math.pi > 3)")
        assert rc == 0 and out == "True"

    def test_from_import(self):
        out, _, rc = clython_run("from math import sqrt\nprint(int(sqrt(16)))")
        assert rc == 0 and out == "4"

    def test_import_as(self):
        out, _, rc = clython_run("import math as m\nprint(m.pi > 3)")
        assert rc == 0 and out == "True"

    def test_import_not_found(self):
        out, _, rc = clython_run(
            "try:\n    import nonexistent_module_xyz\nexcept ImportError:\n    print('caught')"
        )
        assert rc == 0 and out == "caught"


# ── 7.12 Global Statement ─────────────────────────────────────────────────

class TestSection712GlobalStatement:
    def test_global_modify(self):
        out, _, rc = clython_run(
            "x = 10\ndef f():\n    global x\n    x = 20\nf()\nprint(x)"
        )
        assert rc == 0 and out == "20"

    def test_global_create(self):
        out, _, rc = clython_run(
            "def f():\n    global y\n    y = 99\nf()\nprint(y)"
        )
        assert rc == 0 and out == "99"


# ── 7.13 Nonlocal Statement ───────────────────────────────────────────────

class TestSection713NonlocalStatement:
    def test_nonlocal_modify(self):
        out, _, rc = clython_run(
            "def outer():\n    x = 10\n    def inner():\n        nonlocal x\n        x = 20\n    inner()\n    return x\nprint(outer())"
        )
        assert rc == 0 and out == "20"

    def test_nonlocal_counter(self):
        out, _, rc = clython_run(
            "def make_counter():\n    count = 0\n    def inc():\n        nonlocal count\n        count += 1\n        return count\n    return inc\nc = make_counter()\nprint(c(), c(), c())"
        )
        assert rc == 0 and out == "1 2 3"


# ── Try/Except (runtime errors) ───────────────────────────────────────────

class TestSection7TryExceptRuntime:
    """Tests that runtime-raised errors (ZeroDivisionError, IndexError, etc.)
    are catchable by try/except, not just explicit raise."""

    def test_catch_zero_division(self):
        out, _, rc = clython_run(
            "try:\n    1/0\nexcept ZeroDivisionError:\n    print('caught')"
        )
        assert rc == 0 and out == "caught"

    def test_catch_zero_division_with_binding(self):
        out, _, rc = clython_run(
            "try:\n    1/0\nexcept ZeroDivisionError as e:\n    print('caught:', e)"
        )
        assert rc == 0 and "caught: division by zero" in out

    def test_catch_index_error(self):
        out, _, rc = clython_run(
            "try:\n    x = [1,2,3]\n    print(x[10])\nexcept IndexError:\n    print('caught')"
        )
        assert rc == 0 and out == "caught"

    def test_catch_key_error(self):
        out, _, rc = clython_run(
            "try:\n    d = {}\n    d['missing']\nexcept KeyError:\n    print('caught')"
        )
        assert rc == 0 and out == "caught"

    def test_catch_name_error(self):
        out, _, rc = clython_run(
            "try:\n    print(undefined_var)\nexcept NameError:\n    print('caught')"
        )
        assert rc == 0 and out == "caught"

    def test_catch_attribute_error(self):
        out, _, rc = clython_run(
            "try:\n    x = 5\n    x.nonexistent\nexcept AttributeError:\n    print('caught')"
        )
        assert rc == 0 and out == "caught"

    def test_bare_except_catches_runtime(self):
        out, _, rc = clython_run(
            "try:\n    1/0\nexcept:\n    print('caught')"
        )
        assert rc == 0 and out == "caught"

    def test_exception_hierarchy(self):
        """ArithmeticError should catch ZeroDivisionError."""
        out, _, rc = clython_run(
            "try:\n    1/0\nexcept ArithmeticError:\n    print('caught by parent')"
        )
        assert rc == 0 and out == "caught by parent"

    def test_finally_with_runtime_error(self):
        out, _, rc = clython_run(
            "try:\n    1/0\nexcept ZeroDivisionError:\n    print('caught')\nfinally:\n    print('finally')"
        )
        assert rc == 0 and out == "caught\nfinally"

    def test_else_clause(self):
        out, _, rc = clython_run(
            "try:\n    x = 1\nexcept:\n    print('error')\nelse:\n    print('no error')"
        )
        assert rc == 0 and out == "no error"

    def test_else_not_run_on_exception(self):
        out, _, rc = clython_run(
            "try:\n    1/0\nexcept ZeroDivisionError:\n    print('caught')\nelse:\n    print('no error')"
        )
        assert rc == 0 and out == "caught"
