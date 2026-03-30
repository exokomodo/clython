"""
Clython runtime tests for Section 6.13: Conditional Expressions (Ternary).

Tests x if condition else y through the Clython binary.
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


# ---------------------------------------------------------------------------
# Basic conditional expressions
# ---------------------------------------------------------------------------

def test_conditional_true_branch():
    """True condition selects first value."""
    out, err, rc = clython_run("print('yes' if True else 'no')")
    assert rc == 0
    assert out == "yes"


def test_conditional_false_branch():
    """False condition selects else value."""
    out, err, rc = clython_run("print('yes' if False else 'no')")
    assert rc == 0
    assert out == "no"


def test_conditional_integer_condition():
    """Non-zero integer is truthy."""
    out, err, rc = clython_run("print('big' if 5 else 'zero')")
    assert rc == 0
    assert out == "big"


def test_conditional_zero_is_falsy():
    """Zero selects else branch."""
    out, err, rc = clython_run("print('big' if 0 else 'zero')")
    assert rc == 0
    assert out == "zero"


def test_conditional_none_is_falsy():
    """None is falsy."""
    out, err, rc = clython_run("x = None; print('has value' if x else 'no value')")
    assert rc == 0
    assert out == "no value"


def test_conditional_empty_list_falsy():
    """Empty list is falsy."""
    out, err, rc = clython_run("print('has items' if [] else 'empty')")
    assert rc == 0
    assert out == "empty"


def test_conditional_nonempty_list_truthy():
    """Non-empty list is truthy."""
    out, err, rc = clython_run("print('has items' if [1] else 'empty')")
    assert rc == 0
    assert out == "has items"


# ---------------------------------------------------------------------------
# Conditional with comparison conditions
# ---------------------------------------------------------------------------

def test_conditional_comparison_condition():
    """Comparison expression as condition."""
    out, err, rc = clython_run("x = 10; print('big' if x > 5 else 'small')")
    assert rc == 0
    assert out == "big"


def test_conditional_chained_comparison():
    """Chained comparison as condition."""
    out, err, rc = clython_run("x = 5; print('in range' if 0 < x < 10 else 'out')")
    assert rc == 0
    assert out == "in range"


def test_conditional_equality():
    """Equality comparison as condition."""
    out, err, rc = clython_run("x = 42; print('answer' if x == 42 else 'other')")
    assert rc == 0
    assert out == "answer"


# ---------------------------------------------------------------------------
# Conditional with complex values
# ---------------------------------------------------------------------------

def test_conditional_arithmetic_values():
    """Arithmetic in branches."""
    out, err, rc = clython_run("x = 3; print(x * 2 if x > 0 else -x * 2)")
    assert rc == 0
    assert out == "6"


def test_conditional_function_call_value():
    """Function call in branch."""
    out, err, rc = clython_run("x = -5; print(abs(x) if x < 0 else x)")
    assert rc == 0
    assert out == "5"


def test_conditional_assigned():
    """Conditional expression assigned to variable."""
    out, err, rc = clython_run("x = 3; y = 'odd' if x % 2 else 'even'; print(y)")
    assert rc == 0
    assert out == "odd"


def test_conditional_as_argument():
    """Conditional expression as function argument."""
    out, err, rc = clython_run("x = 5; print('positive' if x > 0 else 'non-positive')")
    assert rc == 0
    assert out == "positive"


def test_conditional_in_list():
    """Conditional expression in a list literal."""
    out, err, rc = clython_run("x = 1; y = [x if x > 0 else 0, x * 2]; print(y)")
    assert rc == 0
    assert out == "[1, 2]"


# ---------------------------------------------------------------------------
# Nesting
# ---------------------------------------------------------------------------

def test_nested_conditional_right_associative():
    """Right-associative nesting: a if c1 else b if c2 else c."""
    source = (
        "x = 2\n"
        "result = 'large' if x > 10 else 'medium' if x > 5 else 'small'\n"
        "print(result)\n"
    )
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "small"


def test_nested_conditional_middle_true():
    """Middle branch selected in nested conditional."""
    source = (
        "x = 7\n"
        "result = 'large' if x > 10 else 'medium' if x > 5 else 'small'\n"
        "print(result)\n"
    )
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "medium"


def test_nested_conditional_first_true():
    """First branch selected in nested conditional."""
    source = (
        "x = 15\n"
        "result = 'large' if x > 10 else 'medium' if x > 5 else 'small'\n"
        "print(result)\n"
    )
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "large"


def test_conditional_in_conditional_value():
    """Conditional expression in value branch of another conditional."""
    source = "x = 3; y = (x if x > 0 else -x) if x != 0 else 999; print(y)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "3"


# ---------------------------------------------------------------------------
# Short-circuit evaluation
# ---------------------------------------------------------------------------

def test_conditional_true_branch_not_evaluated():
    """False branch is not evaluated when condition is true."""
    source = (
        "called = []\n"
        "def side_effect(): called.append(1); return 99\n"
        "result = 42 if True else side_effect()\n"
        "print(result, called)\n"
    )
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "42 []"


def test_conditional_false_branch_not_evaluated():
    """True branch is not evaluated when condition is false."""
    source = (
        "called = []\n"
        "def side_effect(): called.append(1); return 99\n"
        "result = side_effect() if False else 42\n"
        "print(result, called)\n"
    )
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "42 []"


# ---------------------------------------------------------------------------
# Conditional in return / comprehension
# ---------------------------------------------------------------------------

def test_conditional_in_return():
    """Conditional expression in return statement."""
    source = (
        "def sign(x): return 1 if x > 0 else (-1 if x < 0 else 0)\n"
        "print(sign(-5), sign(0), sign(3))\n"
    )
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "-1 0 1"


def test_conditional_in_list_comprehension():
    """Conditional expression in list comprehension value."""
    out, err, rc = clython_run("print([x if x % 2 == 0 else -x for x in range(5)])")
    assert rc == 0
    assert out == "[0, -1, 2, -3, 4]"


def test_conditional_lambda():
    """Conditional expression inside a lambda."""
    source = "f = lambda x: 'even' if x % 2 == 0 else 'odd'\nprint(f(4), f(5))"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "even odd"


def test_conditional_missing_else_raises():
    """Missing else clause should produce a SyntaxError."""
    source = "x = 1 if True"
    out, err, rc = clython_run(source)
    assert rc != 0
