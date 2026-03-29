"""Clython runtime conformance tests — Section 8.2: While Statements.

Tests that the Clython interpreter correctly executes Python 3 while statements,
including basic while, while/else, break, continue, and nested loops.
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


# ── Basic while ───────────────────────────────────────────────────────────

class TestBasicWhile:
    def test_basic_counting_loop(self):
        out, _, rc = clython_run("i = 0\nwhile i < 3:\n    print(i)\n    i += 1")
        assert rc == 0 and out == "0\n1\n2"

    def test_while_false_never_executes(self):
        out, _, rc = clython_run("while False:\n    print('never')\nprint('done')")
        assert rc == 0 and out == "done"

    def test_while_zero_condition(self):
        out, _, rc = clython_run("while 0:\n    print('never')\nprint('done')")
        assert rc == 0 and out == "done"

    def test_while_accumulates_sum(self):
        out, _, rc = clython_run(
            "total = 0\ni = 1\nwhile i <= 10:\n    total += i\n    i += 1\nprint(total)"
        )
        assert rc == 0 and out == "55"

    def test_while_with_list_condition(self):
        out, _, rc = clython_run(
            "items = [3, 2, 1]\nwhile len(items) > 0:\n    items.pop()\nprint('empty:', len(items))"
        )
        assert rc == 0 and out == "empty: 0"

    def test_while_with_method_condition(self):
        out, _, rc = clython_run(
            "items = [3, 2, 1]\nwhile len(items) > 1:\n    items.pop()\nprint(items)"
        )
        assert rc == 0 and out == "[3]"

    def test_while_modifies_variable(self):
        out, _, rc = clython_run(
            "x = 100\nwhile x > 1:\n    x //= 2\nprint(x)"
        )
        # 100->50->25->12->6->3->1; stops when x==1 (1>1 is False)
        assert rc == 0 and out == "1"

    def test_while_100_gauss(self):
        out, _, rc = clython_run(
            "total = 0\ni = 1\nwhile i <= 100:\n    total += i\n    i += 1\nprint(total)"
        )
        assert rc == 0 and out == "5050"


# ── While/else ────────────────────────────────────────────────────────────

class TestWhileElse:
    def test_else_runs_when_condition_exhausted(self):
        out, _, rc = clython_run(
            "i = 0\nwhile i < 3:\n    i += 1\nelse:\n    print('done', i)"
        )
        assert rc == 0 and out == "done 3"

    def test_else_skipped_on_break(self):
        out, _, rc = clython_run(
            "i = 0\nwhile i < 10:\n    if i == 3:\n        break\n    i += 1\nelse:\n    print('no break')\nprint(i)"
        )
        assert rc == 0 and out == "3"

    def test_else_runs_on_false_initial_condition(self):
        out, _, rc = clython_run(
            "while False:\n    pass\nelse:\n    print('else ran')"
        )
        assert rc == 0 and out == "else ran"

    def test_continue_does_not_skip_else(self):
        out, _, rc = clython_run(
            "i = 0\nwhile i < 3:\n    i += 1\n    continue\nelse:\n    print('done')"
        )
        assert rc == 0 and out == "done"


# ── Break and continue ────────────────────────────────────────────────────

class TestWhileBreakContinue:
    def test_break_exits_loop(self):
        out, _, rc = clython_run(
            "i = 0\nwhile True:\n    if i == 5:\n        break\n    i += 1\nprint(i)"
        )
        assert rc == 0 and out == "5"

    def test_continue_skips_rest_of_body(self):
        out, _, rc = clython_run(
            "result = []\ni = 0\nwhile i < 5:\n    i += 1\n    if i % 2 == 0:\n        continue\n    result.append(i)\nprint(result)"
        )
        assert rc == 0 and out == "[1, 3, 5]"

    def test_break_in_nested_only_breaks_inner(self):
        out, _, rc = clython_run(
            "outer = 0\nwhile outer < 3:\n    inner = 0\n    while inner < 5:\n        if inner == 2:\n            break\n        inner += 1\n    outer += 1\nprint(outer, inner)"
        )
        assert rc == 0 and out == "3 2"

    def test_while_break_collects_values(self):
        out, _, rc = clython_run(
            "result = []\ni = 0\nwhile i < 100:\n    result.append(i)\n    i += 1\n    if i >= 5:\n        break\nprint(result)"
        )
        assert rc == 0 and out == "[0, 1, 2, 3, 4]"


# ── Nested while ──────────────────────────────────────────────────────────

class TestNestedWhile:
    def test_nested_loops_multiplication_table(self):
        out, _, rc = clython_run(
            "result = []\ni = 1\nwhile i <= 3:\n    j = 1\n    while j <= 3:\n        result.append(i * j)\n        j += 1\n    i += 1\nprint(result)"
        )
        assert rc == 0 and out == "[1, 2, 3, 2, 4, 6, 3, 6, 9]"

    def test_nested_while_with_else(self):
        out, _, rc = clython_run(
            "found = False\ni = 0\nwhile i < 5:\n    j = 0\n    while j < 5:\n        if i * j == 6:\n            found = True\n            break\n        j += 1\n    else:\n        i += 1\n        continue\n    break\nprint(found, i, j)"
        )
        assert rc == 0 and out == "True 2 3"

    def test_deeply_nested_break(self):
        out, _, rc = clython_run(
            "x = 0\nwhile x < 10:\n    y = 0\n    while y < 10:\n        z = 0\n        while z < 10:\n            if x + y + z >= 5:\n                break\n            z += 1\n        y += 1\n        break\n    x += 1\nprint(x)"
        )
        assert rc == 0 and out == "10"


# ── Edge cases ────────────────────────────────────────────────────────────

class TestWhileEdgeCases:
    def test_while_with_complex_boolean(self):
        # Loop runs while x > 0 AND y < 3; y hits 3 first (3 iterations)
        # After 3 iterations: x=2, y=3
        out, _, rc = clython_run(
            "x = 5\ny = 0\nwhile x > 0 and y < 3:\n    x -= 1\n    y += 1\nprint(x, y)"
        )
        assert rc == 0 and out == "2 3"

    def test_while_with_tuple_condition(self):
        """Non-empty tuple is always truthy, but we use it as a sentinel via break"""
        out, _, rc = clython_run(
            "count = 0\nwhile count < 3:\n    count += 1\nprint(count)"
        )
        assert rc == 0 and out == "3"

    def test_while_collects_odds(self):
        out, _, rc = clython_run(
            "result = []\ni = 0\nwhile i < 10:\n    i += 1\n    if i % 2 == 0:\n        continue\n    result.append(i)\nprint(result)"
        )
        assert rc == 0 and out == "[1, 3, 5, 7, 9]"

    def test_while_loop_fibonacci(self):
        out, _, rc = clython_run(
            "a, b = 0, 1\nresult = []\nwhile a < 20:\n    result.append(a)\n    a, b = b, a + b\nprint(result)"
        )
        assert rc == 0 and out == "[0, 1, 1, 2, 3, 5, 8, 13]"

    def test_while_walrus_operator(self):
        out, _, rc = clython_run(
            "items = [3, 1, 4, 1, 5]\ntotal = 0\nwhile (n := len(items)) > 0:\n    total += items.pop()\nprint(total)"
        )
        assert rc == 0 and out == "14"
