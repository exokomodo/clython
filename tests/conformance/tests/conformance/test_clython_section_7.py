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


# ══════════════════════════════════════════════════════════════════════════
# Extended tests derived from AST-based conformance suite (Sections 7.x)
# ══════════════════════════════════════════════════════════════════════════


# ── 7.1 Expression Statements (extended) ──────────────────────────────────

class TestSection71ExpressionStatementsExtended:
    """Additional expression statement tests from AST conformance suite."""

    def test_method_call_as_statement(self):
        out, _, rc = clython_run("x = [1, 2]\nx.append(3)\nprint(x)")
        assert rc == 0 and out == "[1, 2, 3]"

    def test_string_method_as_statement(self):
        out, _, rc = clython_run("s = 'hello'\nprint(s.upper())")
        assert rc == 0 and out == "HELLO"

    def test_chained_method_calls(self):
        out, _, rc = clython_run("print('hello world'.title().replace(' ', '_'))")
        assert rc == 0 and out == "Hello_World"

    def test_expression_with_side_effect(self):
        """List.sort() returns None but mutates the list."""
        out, _, rc = clython_run("x = [3, 1, 2]\nx.sort()\nprint(x)")
        assert rc == 0 and out == "[1, 2, 3]"

    def test_multiple_prints(self):
        out, _, rc = clython_run("print('a')\nprint('b')\nprint('c')")
        assert rc == 0 and out == "a\nb\nc"

    def test_augmented_expression_no_output(self):
        """Standalone expression that doesn't produce output."""
        out, _, rc = clython_run("x = 5\nx + 1\nprint(x)")
        assert rc == 0 and out == "5"


# ── 7.2 Assignment Statements (extended) ──────────────────────────────────

class TestSection72AssignmentStatementsExtended:
    """Additional assignment tests from AST conformance suite."""

    def test_augmented_bitwise_and(self):
        out, _, rc = clython_run("x = 0b1111\nx &= 0b1010\nprint(x)")
        assert rc == 0 and out == "10"

    def test_augmented_bitwise_or(self):
        out, _, rc = clython_run("x = 0b1010\nx |= 0b0101\nprint(x)")
        assert rc == 0 and out == "15"

    def test_augmented_bitwise_xor(self):
        out, _, rc = clython_run("x = 0b1111\nx ^= 0b1010\nprint(x)")
        assert rc == 0 and out == "5"

    def test_augmented_lshift(self):
        out, _, rc = clython_run("x = 1\nx <<= 4\nprint(x)")
        assert rc == 0 and out == "16"

    def test_augmented_rshift(self):
        out, _, rc = clython_run("x = 32\nx >>= 3\nprint(x)")
        assert rc == 0 and out == "4"

    def test_augmented_truediv(self):
        out, _, rc = clython_run("x = 10\nx /= 4\nprint(x)")
        assert rc == 0 and out == "2.5"

    def test_chained_assignment_three(self):
        out, _, rc = clython_run("a = b = c = 42\nprint(a, b, c)")
        assert rc == 0 and out == "42 42 42"

    def test_list_slice_assignment(self):
        out, _, rc = clython_run("x = [1, 2, 3, 4, 5]\nx[1:3] = [20, 30]\nprint(x)")
        assert rc == 0 and out == "[1, 20, 30, 4, 5]"

    def test_starred_unpacking_front(self):
        out, _, rc = clython_run("*a, b = [1, 2, 3, 4, 5]\nprint(a, b)")
        assert rc == 0 and out == "[1, 2, 3, 4] 5"

    def test_starred_unpacking_middle(self):
        out, _, rc = clython_run("a, *b, c = 'hello'\nprint(a, b, c)")
        assert rc == 0 and out == "h ['e', 'l', 'l'] o"

    def test_annotated_assignment(self):
        out, _, rc = clython_run("x: int = 42\nprint(x)")
        assert rc == 0 and out == "42"

    def test_walrus_operator(self):
        out, _, rc = clython_run("if (n := 10) > 5:\n    print(n)")
        assert rc == 0 and out == "10"

    def test_augmented_string_concat(self):
        out, _, rc = clython_run("s = 'hello'\ns += ' world'\nprint(s)")
        assert rc == 0 and out == "hello world"

    def test_augmented_list_extend(self):
        out, _, rc = clython_run("x = [1, 2]\nx += [3, 4]\nprint(x)")
        assert rc == 0 and out == "[1, 2, 3, 4]"

    def test_augmented_mul_string(self):
        out, _, rc = clython_run("s = 'ab'\ns *= 3\nprint(s)")
        assert rc == 0 and out == "ababab"

    def test_nested_dict_assignment(self):
        out, _, rc = clython_run("d = {'a': {'b': 1}}\nd['a']['b'] = 99\nprint(d['a']['b'])")
        assert rc == 0 and out == "99"


# ── 7.3 Assert Statement (extended) ───────────────────────────────────────

class TestSection73AssertStatementExtended:
    """Additional assert tests from AST conformance suite."""

    def test_assert_equality(self):
        out, _, rc = clython_run("x = 5\nassert x == 5\nprint('ok')")
        assert rc == 0 and out == "ok"

    def test_assert_membership(self):
        out, _, rc = clython_run("x = [1, 2, 3]\nassert 2 in x\nprint('ok')")
        assert rc == 0 and out == "ok"

    def test_assert_isinstance(self):
        out, _, rc = clython_run("assert isinstance(42, int)\nprint('ok')")
        assert rc == 0 and out == "ok"

    def test_assert_not_none(self):
        out, _, rc = clython_run("x = 'hello'\nassert x is not None\nprint('ok')")
        assert rc == 0 and out == "ok"

    def test_assert_false_with_format_message(self):
        _, err, rc = clython_run("x = 10\nassert x < 5, f'Expected <5, got {x}'")
        assert rc != 0 and "Expected <5, got 10" in err

    def test_assert_in_function(self):
        out, _, rc = clython_run(
            "def validate(x):\n    assert x > 0, 'must be positive'\n    return x\nprint(validate(5))"
        )
        assert rc == 0 and out == "5"

    def test_assert_in_function_fails(self):
        _, err, rc = clython_run(
            "def validate(x):\n    assert x > 0, 'must be positive'\n    return x\nvalidate(-1)"
        )
        assert rc != 0 and "must be positive" in err

    def test_assert_boolean_operations(self):
        out, _, rc = clython_run("assert True and not False\nprint('ok')")
        assert rc == 0 and out == "ok"

    def test_assert_comparison_chain(self):
        out, _, rc = clython_run("x = 5\nassert 0 < x < 10\nprint('ok')")
        assert rc == 0 and out == "ok"


# ── 7.4 Pass Statement (extended) ─────────────────────────────────────────

class TestSection74PassStatementExtended:
    """Additional pass statement tests from AST conformance suite."""

    def test_pass_in_loop(self):
        out, _, rc = clython_run("for i in range(3):\n    pass\nprint('done')")
        assert rc == 0 and out == "done"

    def test_pass_in_while(self):
        out, _, rc = clython_run("i = 0\nwhile i < 0:\n    pass\nprint('done')")
        assert rc == 0 and out == "done"

    def test_pass_in_try_except(self):
        out, _, rc = clython_run("try:\n    1/0\nexcept:\n    pass\nprint('ok')")
        assert rc == 0 and out == "ok"

    def test_pass_in_elif(self):
        out, _, rc = clython_run(
            "x = 5\nif x > 10:\n    pass\nelif x > 0:\n    print('positive')\nelse:\n    pass"
        )
        assert rc == 0 and out == "positive"

    def test_pass_multiple_in_function(self):
        out, _, rc = clython_run("def f():\n    pass\n    pass\n    return 42\nprint(f())")
        assert rc == 0 and out == "42"

    def test_pass_with_docstring(self):
        out, _, rc = clython_run(
            "class C:\n    '''A class.'''\n    pass\nprint(type(C).__name__)"
        )
        assert rc == 0  # Just verify it doesn't crash

    def test_pass_in_nested_if(self):
        out, _, rc = clython_run(
            "for i in range(3):\n    if i == 1:\n        pass\n    else:\n        print(i)"
        )
        assert rc == 0 and out == "0\n2"


# ── 7.5 Del Statement (extended) ──────────────────────────────────────────

class TestSection75DelStatementExtended:
    """Additional del tests from AST conformance suite."""

    def test_del_multiple_variables(self):
        out, _, rc = clython_run(
            "a = 1\nb = 2\nc = 3\ndel a, b, c\ntry:\n    print(a)\nexcept NameError:\n    print('all deleted')"
        )
        assert rc == 0 and out == "all deleted"

    def test_del_list_slice(self):
        out, _, rc = clython_run("x = [1, 2, 3, 4, 5]\ndel x[1:3]\nprint(x)")
        assert rc == 0 and out == "[1, 4, 5]"

    def test_del_dict_key_check(self):
        out, _, rc = clython_run(
            "d = {'a': 1, 'b': 2, 'c': 3}\ndel d['b']\nprint(sorted(d.keys()))"
        )
        assert rc == 0 and out == "['a', 'c']"

    def test_del_and_recreate(self):
        out, _, rc = clython_run("x = 10\ndel x\nx = 20\nprint(x)")
        assert rc == 0 and out == "20"

    def test_del_nested_list(self):
        out, _, rc = clython_run("x = [[1, 2], [3, 4]]\ndel x[0][1]\nprint(x)")
        assert rc == 0 and out == "[[1], [3, 4]]"

    def test_del_nonexistent_raises(self):
        out, _, rc = clython_run(
            "d = {}\ntry:\n    del d['missing']\nexcept KeyError:\n    print('caught')"
        )
        assert rc == 0 and out == "caught"


# ── 7.6 Return Statement (extended) ───────────────────────────────────────

class TestSection76ReturnStatementExtended:
    """Additional return tests from AST conformance suite."""

    def test_return_conditional_expression(self):
        out, _, rc = clython_run(
            "def f(x):\n    return 'positive' if x > 0 else 'non-positive'\nprint(f(5))\nprint(f(-1))"
        )
        assert rc == 0 and out == "positive\nnon-positive"

    def test_return_dict(self):
        out, _, rc = clython_run(
            "def f():\n    return {'a': 1, 'b': 2}\nd = f()\nprint(d['a'], d['b'])"
        )
        assert rc == 0 and out == "1 2"

    def test_return_list_comprehension(self):
        out, _, rc = clython_run(
            "def f():\n    return [x**2 for x in range(5)]\nprint(f())"
        )
        assert rc == 0 and out == "[0, 1, 4, 9, 16]"

    def test_multiple_returns_guard_clauses(self):
        out, _, rc = clython_run(
            "def classify(x):\n    if x < 0:\n        return 'negative'\n    if x == 0:\n        return 'zero'\n    return 'positive'\nprint(classify(-1), classify(0), classify(5))"
        )
        assert rc == 0 and out == "negative zero positive"

    def test_return_from_nested_function(self):
        out, _, rc = clython_run(
            "def outer():\n    def inner():\n        return 42\n    return inner()\nprint(outer())"
        )
        assert rc == 0 and out == "42"

    def test_return_in_try_finally(self):
        """Return in try, finally still executes."""
        out, _, rc = clython_run(
            "def f():\n    try:\n        return 'value'\n    finally:\n        print('finally')\nresult = f()\nprint(result)"
        )
        assert rc == 0
        assert "value" in out and "finally" in out

    def test_return_in_except(self):
        out, _, rc = clython_run(
            "def f():\n    try:\n        1/0\n    except ZeroDivisionError:\n        return 'caught'\nprint(f())"
        )
        assert rc == 0 and out == "caught"

    def test_return_starred_unpacking(self):
        out, _, rc = clython_run(
            "def f():\n    return 1, 2, 3\na, b, c = f()\nprint(a, b, c)"
        )
        assert rc == 0 and out == "1 2 3"


# ── 7.7 Yield Statement ───────────────────────────────────────────────────

class TestSection77YieldStatement:
    """Yield statement tests from AST conformance suite."""

    def test_simple_generator(self):
        out, _, rc = clython_run(
            "def gen():\n    yield 1\n    yield 2\n    yield 3\nprint(list(gen()))"
        )
        assert rc == 0 and out == "[1, 2, 3]"

    def test_yield_in_loop(self):
        out, _, rc = clython_run(
            "def gen(n):\n    for i in range(n):\n        yield i * 2\nprint(list(gen(4)))"
        )
        assert rc == 0 and out == "[0, 2, 4, 6]"

    def test_yield_none(self):
        out, _, rc = clython_run(
            "def gen():\n    yield\nresult = list(gen())\nprint(result)"
        )
        assert rc == 0 and out == "[None]"

    def test_generator_with_condition(self):
        out, _, rc = clython_run(
            "def evens(n):\n    for i in range(n):\n        if i % 2 == 0:\n            yield i\nprint(list(evens(10)))"
        )
        assert rc == 0 and out == "[0, 2, 4, 6, 8]"

    def test_generator_next(self):
        out, _, rc = clython_run(
            "def gen():\n    yield 'a'\n    yield 'b'\ng = gen()\nprint(next(g))\nprint(next(g))"
        )
        assert rc == 0 and out == "a\nb"

    def test_generator_exhaustion(self):
        out, _, rc = clython_run(
            "def gen():\n    yield 1\ng = gen()\nnext(g)\ntry:\n    next(g)\nexcept StopIteration:\n    print('exhausted')"
        )
        assert rc == 0 and out == "exhausted"

    def test_generator_in_for_loop(self):
        out, _, rc = clython_run(
            "def squares(n):\n    for i in range(n):\n        yield i ** 2\nfor s in squares(5):\n    print(s)"
        )
        assert rc == 0 and out == "0\n1\n4\n9\n16"

    def test_generator_with_return(self):
        out, _, rc = clython_run(
            "def gen():\n    yield 1\n    yield 2\n    return\n    yield 3\nprint(list(gen()))"
        )
        assert rc == 0 and out == "[1, 2]"

    def test_yield_from_list(self):
        out, _, rc = clython_run(
            "def gen():\n    yield from [1, 2, 3]\nprint(list(gen()))"
        )
        assert rc == 0 and out == "[1, 2, 3]"

    def test_yield_from_generator(self):
        out, _, rc = clython_run(
            "def inner():\n    yield 1\n    yield 2\ndef outer():\n    yield from inner()\n    yield 3\nprint(list(outer()))"
        )
        assert rc == 0 and out == "[1, 2, 3]"

    def test_yield_from_range(self):
        out, _, rc = clython_run(
            "def gen():\n    yield from range(5)\nprint(list(gen()))"
        )
        assert rc == 0 and out == "[0, 1, 2, 3, 4]"

    @pytest.mark.xfail(reason="generator send() may not be implemented")
    def test_generator_send(self):
        out, _, rc = clython_run(
            "def gen():\n    x = yield 'ready'\n    yield f'got {x}'\ng = gen()\nprint(next(g))\nprint(g.send(42))"
        )
        assert rc == 0 and out == "ready\ngot 42"

    def test_multiple_generators(self):
        out, _, rc = clython_run(
            "def g1():\n    yield 1\n    yield 2\ndef g2():\n    yield 'a'\n    yield 'b'\nprint(list(g1()), list(g2()))"
        )
        assert rc == 0 and out == "[1, 2] ['a', 'b']"

    def test_generator_with_try_except(self):
        out, _, rc = clython_run(
            "def gen():\n    try:\n        yield 1\n        yield 2\n    except:\n        yield 'error'\nprint(list(gen()))"
        )
        assert rc == 0 and out == "[1, 2]"


# ── 7.8 Raise Statement (extended) ────────────────────────────────────────

class TestSection78RaiseStatementExtended:
    """Additional raise tests from AST conformance suite."""

    def test_raise_runtime_error(self):
        out, _, rc = clython_run(
            "try:\n    raise RuntimeError('boom')\nexcept RuntimeError as e:\n    print('caught:', e)"
        )
        assert rc == 0 and "caught: boom" in out

    def test_raise_custom_exception(self):
        out, _, rc = clython_run(
            "class MyError(Exception):\n    pass\ntry:\n    raise MyError('custom')\nexcept MyError as e:\n    print('caught:', e)"
        )
        assert rc == 0 and "caught: custom" in out

    def test_raise_key_error(self):
        out, _, rc = clython_run(
            "try:\n    raise KeyError('missing')\nexcept KeyError as e:\n    print('caught')"
        )
        assert rc == 0 and out == "caught"

    def test_raise_index_error(self):
        out, _, rc = clython_run(
            "try:\n    raise IndexError('out of range')\nexcept IndexError as e:\n    print('caught:', e)"
        )
        assert rc == 0 and "caught: out of range" in out

    def test_raise_from_chaining(self):
        out, _, rc = clython_run(
            "try:\n    try:\n        1/0\n    except ZeroDivisionError as e:\n        raise ValueError('wrapped') from e\nexcept ValueError as e:\n    print('caught:', e)"
        )
        assert rc == 0 and "caught: wrapped" in out

    def test_raise_from_none(self):
        out, _, rc = clython_run(
            "try:\n    try:\n        1/0\n    except:\n        raise ValueError('clean') from None\nexcept ValueError as e:\n    print('caught:', e)"
        )
        assert rc == 0 and "caught: clean" in out

    def test_raise_exception_class_no_args(self):
        out, _, rc = clython_run(
            "try:\n    raise ValueError\nexcept ValueError:\n    print('caught')"
        )
        assert rc == 0 and out == "caught"

    def test_raise_in_function(self):
        out, _, rc = clython_run(
            "def validate(x):\n    if x < 0:\n        raise ValueError('negative')\n    return x\ntry:\n    validate(-1)\nexcept ValueError as e:\n    print('caught:', e)"
        )
        assert rc == 0 and "caught: negative" in out

    def test_raise_parent_catches_child(self):
        """Exception should catch ValueError (parent catches child)."""
        out, _, rc = clython_run(
            "try:\n    raise ValueError('test')\nexcept Exception as e:\n    print('caught:', e)"
        )
        assert rc == 0 and "caught: test" in out


# ── 7.9 Break Statement (extended) ────────────────────────────────────────

class TestSection79BreakStatementExtended:
    """Additional break tests from AST conformance suite."""

    def test_break_for_else_skips_else(self):
        out, _, rc = clython_run(
            "for i in range(5):\n    if i == 3:\n        break\nelse:\n    print('no break')\nprint(i)"
        )
        assert rc == 0 and out == "3"

    def test_break_for_else_runs_else(self):
        out, _, rc = clython_run(
            "for i in range(3):\n    pass\nelse:\n    print('completed')"
        )
        assert rc == 0 and out == "completed"

    def test_break_while_else_skips_else(self):
        out, _, rc = clython_run(
            "i = 0\nwhile i < 10:\n    if i == 5:\n        break\n    i += 1\nelse:\n    print('no break')\nprint(i)"
        )
        assert rc == 0 and out == "5"

    def test_break_while_else_runs_else(self):
        out, _, rc = clython_run(
            "i = 0\nwhile i < 3:\n    i += 1\nelse:\n    print('completed')\nprint(i)"
        )
        assert rc == 0 and out == "completed\n3"

    def test_break_in_try_block(self):
        out, _, rc = clython_run(
            "for i in range(10):\n    try:\n        if i == 3:\n            break\n    except:\n        pass\nprint(i)"
        )
        assert rc == 0 and out == "3"

    def test_break_deeply_nested(self):
        out, _, rc = clython_run(
            "result = []\nfor i in range(3):\n    for j in range(3):\n        for k in range(3):\n            if k == 1:\n                break\n            result.append((i, j, k))\nprint(len(result))"
        )
        assert rc == 0 and out == "9"


# ── 7.10 Continue Statement (extended) ────────────────────────────────────

class TestSection710ContinueStatementExtended:
    """Additional continue tests from AST conformance suite."""

    def test_continue_in_nested_for(self):
        out, _, rc = clython_run(
            "result = []\nfor i in range(3):\n    for j in range(3):\n        if j == 1:\n            continue\n        result.append((i, j))\nprint(len(result))"
        )
        assert rc == 0 and out == "6"

    def test_continue_with_try(self):
        out, _, rc = clython_run(
            "result = []\nfor i in range(5):\n    try:\n        if i == 2:\n            continue\n        result.append(i)\n    except:\n        pass\nprint(result)"
        )
        assert rc == 0 and out == "[0, 1, 3, 4]"

    def test_continue_preserves_else(self):
        """Continue does NOT prevent else clause (only break does)."""
        out, _, rc = clython_run(
            "for i in range(3):\n    if i == 1:\n        continue\nelse:\n    print('completed')"
        )
        assert rc == 0 and out == "completed"

    def test_continue_while_with_counter(self):
        out, _, rc = clython_run(
            "i = 0\nresult = []\nwhile i < 10:\n    i += 1\n    if i % 3 == 0:\n        continue\n    result.append(i)\nprint(result)"
        )
        assert rc == 0 and out == "[1, 2, 4, 5, 7, 8, 10]"

    def test_continue_and_break_together(self):
        out, _, rc = clython_run(
            "result = []\nfor i in range(10):\n    if i % 2 == 0:\n        continue\n    if i > 7:\n        break\n    result.append(i)\nprint(result)"
        )
        assert rc == 0 and out == "[1, 3, 5, 7]"


# ── 7.11 Import Statement (extended) ──────────────────────────────────────

class TestSection711ImportStatementExtended:
    """Additional import tests from AST conformance suite."""

    def test_from_import_multiple(self):
        out, _, rc = clython_run("from math import sqrt, floor\nprint(int(sqrt(16)), floor(3.7))")
        assert rc == 0 and out == "4 3"

    def test_from_import_as(self):
        out, _, rc = clython_run("from math import sqrt as s\nprint(int(s(25)))")
        assert rc == 0 and out == "5"

    @pytest.mark.xfail(reason="dotted imports may not be implemented")
    def test_import_os_path(self):
        out, _, rc = clython_run("import os.path\nprint(type(os.path).__name__)")
        assert rc == 0  # Just verify it doesn't crash

    def test_import_sys(self):
        out, _, rc = clython_run("import sys\nprint(type(sys.version).__name__)")
        assert rc == 0 and out == "str"

    def test_multiple_imports(self):
        out, _, rc = clython_run("import math\nimport sys\nprint(math.pi > 3, type(sys.version).__name__)")
        assert rc == 0 and out == "True str"

    def test_from_import_and_use(self):
        out, _, rc = clython_run("from math import ceil, pi\nprint(ceil(pi))")
        assert rc == 0 and out == "4"

    @pytest.mark.xfail(reason="ModuleNotFoundError may differ from ImportError")
    def test_import_error_type(self):
        out, _, rc = clython_run(
            "try:\n    import nonexistent_xyz_123\nexcept ModuleNotFoundError:\n    print('module not found')"
        )
        assert rc == 0 and out == "module not found"


# ── 7.12 Global Statement (extended) ──────────────────────────────────────

class TestSection712GlobalStatementExtended:
    """Additional global tests from AST conformance suite."""

    def test_global_multiple_names(self):
        out, _, rc = clython_run(
            "a = 1\nb = 2\ndef f():\n    global a, b\n    a = 10\n    b = 20\nf()\nprint(a, b)"
        )
        assert rc == 0 and out == "10 20"

    def test_global_read_before_write(self):
        out, _, rc = clython_run(
            "x = 42\ndef f():\n    global x\n    print(x)\n    x = 99\nf()\nprint(x)"
        )
        assert rc == 0 and out == "42\n99"

    def test_global_in_nested_function(self):
        out, _, rc = clython_run(
            "x = 1\ndef outer():\n    def inner():\n        global x\n        x = 100\n    inner()\nouter()\nprint(x)"
        )
        assert rc == 0 and out == "100"

    def test_global_delete(self):
        out, _, rc = clython_run(
            "x = 42\ndef f():\n    global x\n    del x\nf()\ntry:\n    print(x)\nexcept NameError:\n    print('deleted')"
        )
        assert rc == 0 and out == "deleted"


# ── 7.13 Nonlocal Statement (extended) ────────────────────────────────────

class TestSection713NonlocalStatementExtended:
    """Additional nonlocal tests from AST conformance suite."""

    def test_nonlocal_multiple_names(self):
        out, _, rc = clython_run(
            "def outer():\n    a = 1\n    b = 2\n    def inner():\n        nonlocal a, b\n        a = 10\n        b = 20\n    inner()\n    return a, b\nprint(outer())"
        )
        assert rc == 0 and out == "(10, 20)"

    def test_nonlocal_deeply_nested(self):
        out, _, rc = clython_run(
            "def level1():\n    x = 1\n    def level2():\n        def level3():\n            nonlocal x\n            x = 99\n        level3()\n    level2()\n    return x\nprint(level1())"
        )
        assert rc == 0 and out == "99"

    def test_nonlocal_in_loop(self):
        out, _, rc = clython_run(
            "def f():\n    total = 0\n    def add(x):\n        nonlocal total\n        total += x\n    for i in range(5):\n        add(i)\n    return total\nprint(f())"
        )
        assert rc == 0 and out == "10"

    def test_nonlocal_vs_global(self):
        """Nonlocal binds to enclosing function scope, not global."""
        out, _, rc = clython_run(
            "x = 'global'\ndef outer():\n    x = 'outer'\n    def inner():\n        nonlocal x\n        x = 'inner'\n    inner()\n    return x\nprint(outer())\nprint(x)"
        )
        assert rc == 0 and out == "inner\nglobal"


# ── 7.14 Type Statement ───────────────────────────────────────────────────

class TestSection714TypeStatement:
    """Type statement tests (Python 3.12+) from AST conformance suite."""

    @pytest.mark.xfail(reason="type statement (PEP 695) may not be implemented")
    def test_simple_type_alias(self):
        out, _, rc = clython_run("type Point = tuple[int, int]\nprint(Point)")
        assert rc == 0

    @pytest.mark.xfail(reason="type statement (PEP 695) may not be implemented")
    def test_generic_type_alias(self):
        out, _, rc = clython_run("type Vector[T] = list[T]\nprint(Vector)")
        assert rc == 0

    @pytest.mark.xfail(reason="type statement (PEP 695) may not be implemented")
    def test_type_alias_usage(self):
        out, _, rc = clython_run(
            "type IntList = list[int]\nx: IntList = [1, 2, 3]\nprint(x)"
        )
        assert rc == 0 and out == "[1, 2, 3]"
