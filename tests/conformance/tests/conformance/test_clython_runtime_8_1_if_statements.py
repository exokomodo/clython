"""Clython runtime conformance tests — Section 8.1: If Statements.

Tests that the Clython interpreter correctly executes Python 3 if statements,
including basic if, if/else, if/elif/else, nested if, chained comparisons,
and various truthiness checks.
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


# ── Basic if ──────────────────────────────────────────────────────────────

class TestBasicIf:
    def test_if_true_executes_body(self):
        out, _, rc = clython_run("if True:\n    print('yes')")
        assert rc == 0 and out == "yes"

    def test_if_false_skips_body(self):
        out, _, rc = clython_run("if False:\n    print('yes')\nprint('done')")
        assert rc == 0 and out == "done"

    def test_if_nonzero_is_truthy(self):
        out, _, rc = clython_run("if 1:\n    print('truthy')")
        assert rc == 0 and out == "truthy"

    def test_if_zero_is_falsy(self):
        out, _, rc = clython_run("if 0:\n    print('truthy')\nelse:\n    print('falsy')")
        assert rc == 0 and out == "falsy"

    def test_if_nonempty_list_is_truthy(self):
        out, _, rc = clython_run("if [1, 2]:\n    print('truthy')\nelse:\n    print('falsy')")
        assert rc == 0 and out == "truthy"

    def test_if_empty_list_is_falsy(self):
        out, _, rc = clython_run("if []:\n    print('truthy')\nelse:\n    print('falsy')")
        assert rc == 0 and out == "falsy"

    def test_if_empty_string_is_falsy(self):
        out, _, rc = clython_run("if '':\n    print('truthy')\nelse:\n    print('falsy')")
        assert rc == 0 and out == "falsy"

    def test_if_nonempty_string_is_truthy(self):
        out, _, rc = clython_run("if 'hello':\n    print('truthy')\nelse:\n    print('falsy')")
        assert rc == 0 and out == "truthy"

    def test_if_none_is_falsy(self):
        out, _, rc = clython_run("if None:\n    print('truthy')\nelse:\n    print('falsy')")
        assert rc == 0 and out == "falsy"

    def test_if_empty_dict_is_falsy(self):
        out, _, rc = clython_run("if {}:\n    print('truthy')\nelse:\n    print('falsy')")
        assert rc == 0 and out == "falsy"


# ── If/else ───────────────────────────────────────────────────────────────

class TestIfElse:
    def test_if_else_true_branch(self):
        out, _, rc = clython_run("if True:\n    print('yes')\nelse:\n    print('no')")
        assert rc == 0 and out == "yes"

    def test_if_else_false_branch(self):
        out, _, rc = clython_run("if False:\n    print('yes')\nelse:\n    print('no')")
        assert rc == 0 and out == "no"

    def test_if_else_variable(self):
        out, _, rc = clython_run(
            "x = 7\nif x > 10:\n    print('big')\nelse:\n    print('small')"
        )
        assert rc == 0 and out == "small"


# ── If/elif/else ──────────────────────────────────────────────────────────

class TestIfElifElse:
    def test_first_branch_taken(self):
        out, _, rc = clython_run(
            "x = 15\nif x > 10:\n    print('big')\nelif x > 5:\n    print('medium')\nelse:\n    print('small')"
        )
        assert rc == 0 and out == "big"

    def test_elif_branch_taken(self):
        out, _, rc = clython_run(
            "x = 7\nif x > 10:\n    print('big')\nelif x > 5:\n    print('medium')\nelse:\n    print('small')"
        )
        assert rc == 0 and out == "medium"

    def test_else_branch_taken(self):
        out, _, rc = clython_run(
            "x = 3\nif x > 10:\n    print('big')\nelif x > 5:\n    print('medium')\nelse:\n    print('small')"
        )
        assert rc == 0 and out == "small"

    def test_multiple_elif_first_match_wins(self):
        out, _, rc = clython_run(
            "x = 3\n"
            "if x == 1:\n    print('one')\n"
            "elif x == 2:\n    print('two')\n"
            "elif x == 3:\n    print('three')\n"
            "elif x == 4:\n    print('four')\n"
            "else:\n    print('other')"
        )
        assert rc == 0 and out == "three"

    def test_elif_without_else(self):
        out, _, rc = clython_run(
            "x = 99\nif x == 1:\n    print('one')\nelif x == 2:\n    print('two')\nprint('done')"
        )
        assert rc == 0 and out == "done"


# ── Nested if ─────────────────────────────────────────────────────────────

class TestNestedIf:
    def test_nested_if_both_true(self):
        out, _, rc = clython_run(
            "x = 5\nif x > 0:\n    if x > 3:\n        print('big positive')\n    else:\n        print('small positive')"
        )
        assert rc == 0 and out == "big positive"

    def test_nested_if_outer_true_inner_false(self):
        out, _, rc = clython_run(
            "x = 2\nif x > 0:\n    if x > 3:\n        print('big positive')\n    else:\n        print('small positive')"
        )
        assert rc == 0 and out == "small positive"

    def test_nested_if_outer_false(self):
        out, _, rc = clython_run(
            "x = -1\nif x > 0:\n    if x > 3:\n        print('big positive')\n    else:\n        print('small positive')\nelse:\n    print('negative')"
        )
        assert rc == 0 and out == "negative"

    def test_nested_elif_structure(self):
        out, _, rc = clython_run(
            "role = 'user'\nlevel = 'admin'\n"
            "if role == 'admin':\n    print('admin')\n"
            "elif role == 'user':\n"
            "    if level == 'admin':\n        print('power user')\n"
            "    else:\n        print('normal user')\n"
            "else:\n    print('guest')"
        )
        assert rc == 0 and out == "power user"


# ── Condition expressions ─────────────────────────────────────────────────

class TestConditionExpressions:
    def test_and_both_true(self):
        out, _, rc = clython_run(
            "x, y = 5, 10\nif x > 0 and y > 0:\n    print('both positive')"
        )
        assert rc == 0 and out == "both positive"

    def test_and_short_circuit(self):
        out, _, rc = clython_run(
            "x = -1\nif x > 0 and (1/0):\n    print('yes')\nelse:\n    print('no')"
        )
        assert rc == 0 and out == "no"

    def test_or_first_true(self):
        out, _, rc = clython_run(
            "x, y = -1, 10\nif x > 0 or y > 0:\n    print('at least one')"
        )
        assert rc == 0 and out == "at least one"

    def test_or_short_circuit(self):
        out, _, rc = clython_run(
            "x = 1\nif x > 0 or (1/0):\n    print('yes')\nelse:\n    print('no')"
        )
        assert rc == 0 and out == "yes"

    def test_not_condition(self):
        out, _, rc = clython_run("if not False:\n    print('yes')")
        assert rc == 0 and out == "yes"

    def test_double_negation(self):
        out, _, rc = clython_run("if not not True:\n    print('yes')")
        assert rc == 0 and out == "yes"

    def test_chained_comparison_in_range(self):
        out, _, rc = clython_run(
            "x = 5\nif 0 < x < 10:\n    print('in range')\nelse:\n    print('out')"
        )
        assert rc == 0 and out == "in range"

    def test_chained_comparison_out_of_range(self):
        out, _, rc = clython_run(
            "x = 15\nif 0 < x < 10:\n    print('in range')\nelse:\n    print('out')"
        )
        assert rc == 0 and out == "out"

    def test_is_none(self):
        out, _, rc = clython_run(
            "x = None\nif x is None:\n    print('none')\nelse:\n    print('not none')"
        )
        assert rc == 0 and out == "none"

    def test_is_not_none(self):
        out, _, rc = clython_run(
            "x = 42\nif x is not None:\n    print('has value')\nelse:\n    print('none')"
        )
        assert rc == 0 and out == "has value"

    def test_in_membership(self):
        out, _, rc = clython_run(
            "if 3 in [1, 2, 3, 4]:\n    print('found')\nelse:\n    print('missing')"
        )
        assert rc == 0 and out == "found"

    def test_not_in_membership(self):
        out, _, rc = clython_run(
            "if 5 not in [1, 2, 3]:\n    print('missing')\nelse:\n    print('found')"
        )
        assert rc == 0 and out == "missing"

    def test_comparison_operators(self):
        out, _, rc = clython_run(
            "results = []\n"
            "results.append(1 == 1)\n"
            "results.append(1 != 2)\n"
            "results.append(1 < 2)\n"
            "results.append(2 > 1)\n"
            "results.append(1 <= 1)\n"
            "results.append(2 >= 2)\n"
            "print(all(results))"
        )
        assert rc == 0 and out == "True"

    def test_walrus_operator_in_if(self):
        out, _, rc = clython_run(
            "data = [1, 2, 3]\nif (n := len(data)) > 2:\n    print(n)"
        )
        assert rc == 0 and out == "3"

    def test_if_with_function_call_condition(self):
        out, _, rc = clython_run(
            "def is_even(n):\n    return n % 2 == 0\n"
            "if is_even(4):\n    print('even')\nelse:\n    print('odd')"
        )
        assert rc == 0 and out == "even"

    def test_multiline_condition(self):
        out, _, rc = clython_run(
            "x = 5\ny = 10\nif (\n    x > 0 and\n    y > 0\n):\n    print('yes')"
        )
        assert rc == 0 and out == "yes"
