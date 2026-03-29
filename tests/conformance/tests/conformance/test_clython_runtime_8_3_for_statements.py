"""Clython runtime conformance tests — Section 8.3: For Statements.

Tests that the Clython interpreter correctly executes Python 3 for statements,
including iteration over various types, target unpacking, for/else, break,
continue, and nested for loops.
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


# ── Basic for ─────────────────────────────────────────────────────────────

class TestBasicFor:
    def test_for_range(self):
        out, _, rc = clython_run(
            "result = []\nfor i in range(5):\n    result.append(i)\nprint(result)"
        )
        assert rc == 0 and out == "[0, 1, 2, 3, 4]"

    def test_for_list(self):
        out, _, rc = clython_run(
            "total = 0\nfor x in [10, 20, 30]:\n    total += x\nprint(total)"
        )
        assert rc == 0 and out == "60"

    def test_for_string_chars(self):
        out, _, rc = clython_run(
            "result = []\nfor c in 'abc':\n    result.append(c)\nprint(result)"
        )
        assert rc == 0 and out == "['a', 'b', 'c']"

    def test_for_tuple(self):
        out, _, rc = clython_run(
            "result = []\nfor x in (1, 2, 3):\n    result.append(x * 2)\nprint(result)"
        )
        assert rc == 0 and out == "[2, 4, 6]"

    def test_for_empty_iterable(self):
        out, _, rc = clython_run(
            "count = 0\nfor x in []:\n    count += 1\nprint(count)"
        )
        assert rc == 0 and out == "0"

    def test_for_dict_keys(self):
        out, _, rc = clython_run(
            "d = {'a': 1, 'b': 2}\nfor k in d:\n    print(k, d[k])"
        )
        assert rc == 0 and "a 1" in out and "b 2" in out

    def test_for_dict_items(self):
        out, _, rc = clython_run(
            "d = {'x': 1, 'y': 2}\nfor k, v in d.items():\n    print(k, v)"
        )
        assert rc == 0 and "x 1" in out and "y 2" in out

    def test_for_dict_values(self):
        out, _, rc = clython_run(
            "d = {'a': 10, 'b': 20}\ntotal = 0\nfor v in d.values():\n    total += v\nprint(total)"
        )
        assert rc == 0 and out == "30"

    def test_for_range_step(self):
        out, _, rc = clython_run(
            "result = []\nfor i in range(0, 10, 2):\n    result.append(i)\nprint(result)"
        )
        assert rc == 0 and out == "[0, 2, 4, 6, 8]"

    def test_for_range_reverse(self):
        out, _, rc = clython_run(
            "result = []\nfor i in range(5, 0, -1):\n    result.append(i)\nprint(result)"
        )
        assert rc == 0 and out == "[5, 4, 3, 2, 1]"


# ── Target unpacking ──────────────────────────────────────────────────────

class TestForTargetUnpacking:
    def test_tuple_unpacking(self):
        out, _, rc = clython_run(
            "pairs = [(1, 'a'), (2, 'b')]\nfor num, letter in pairs:\n    print(num, letter)"
        )
        assert rc == 0 and out == "1 a\n2 b"

    def test_enumerate_unpacking(self):
        out, _, rc = clython_run(
            "for i, v in enumerate(['a', 'b', 'c']):\n    print(i, v)"
        )
        assert rc == 0 and out == "0 a\n1 b\n2 c"

    def test_zip_unpacking(self):
        out, _, rc = clython_run(
            "for a, b in zip([1, 2, 3], ['a', 'b', 'c']):\n    print(a, b)"
        )
        assert rc == 0 and out == "1 a\n2 b\n3 c"

    def test_nested_unpacking(self):
        out, _, rc = clython_run(
            "data = [(1, (2, 3)), (4, (5, 6))]\nfor a, (b, c) in data:\n    print(a, b, c)"
        )
        assert rc == 0 and out == "1 2 3\n4 5 6"

    def test_starred_unpacking(self):
        out, _, rc = clython_run(
            "for first, *rest in [(1, 2, 3), (4, 5, 6)]:\n    print(first, rest)"
        )
        assert rc == 0 and out == "1 [2, 3]\n4 [5, 6]"

    def test_three_element_unpacking(self):
        out, _, rc = clython_run(
            "for x, y, z in [(1, 2, 3), (4, 5, 6)]:\n    print(x + y + z)"
        )
        assert rc == 0 and out == "6\n15"

    def test_underscore_discard(self):
        out, _, rc = clython_run(
            "result = []\nfor _, v in [(1, 'a'), (2, 'b')]:\n    result.append(v)\nprint(result)"
        )
        assert rc == 0 and out == "['a', 'b']"


# ── For/else ──────────────────────────────────────────────────────────────

class TestForElse:
    def test_else_runs_after_exhausted(self):
        out, _, rc = clython_run(
            "for i in range(3):\n    pass\nelse:\n    print('completed')"
        )
        assert rc == 0 and out == "completed"

    def test_else_runs_on_empty_iterable(self):
        out, _, rc = clython_run(
            "for x in []:\n    pass\nelse:\n    print('else ran')"
        )
        assert rc == 0 and out == "else ran"

    def test_else_skipped_on_break(self):
        out, _, rc = clython_run(
            "for i in range(5):\n    if i == 2:\n        break\nelse:\n    print('no break')\nprint(i)"
        )
        assert rc == 0 and out == "2"

    def test_continue_does_not_skip_else(self):
        out, _, rc = clython_run(
            "for i in range(3):\n    continue\nelse:\n    print('done')"
        )
        assert rc == 0 and out == "done"

    def test_else_with_search_pattern(self):
        """Classic search-and-found pattern using for/else"""
        out, _, rc = clython_run(
            "target = 7\nfor x in [1, 3, 5, 7, 9]:\n    if x == target:\n        print('found')\n        break\nelse:\n    print('not found')"
        )
        assert rc == 0 and out == "found"

    def test_else_not_found_pattern(self):
        out, _, rc = clython_run(
            "target = 4\nfor x in [1, 3, 5, 7, 9]:\n    if x == target:\n        print('found')\n        break\nelse:\n    print('not found')"
        )
        assert rc == 0 and out == "not found"


# ── Break and continue ────────────────────────────────────────────────────

class TestForBreakContinue:
    def test_break_exits_loop(self):
        out, _, rc = clython_run(
            "for i in range(100):\n    if i == 5:\n        break\nprint(i)"
        )
        assert rc == 0 and out == "5"

    def test_continue_skips_rest(self):
        out, _, rc = clython_run(
            "result = []\nfor i in range(5):\n    if i == 2:\n        continue\n    result.append(i)\nprint(result)"
        )
        assert rc == 0 and out == "[0, 1, 3, 4]"

    def test_continue_even_numbers(self):
        out, _, rc = clython_run(
            "result = []\nfor i in range(10):\n    if i % 2 == 0:\n        continue\n    result.append(i)\nprint(result)"
        )
        assert rc == 0 and out == "[1, 3, 5, 7, 9]"


# ── Nested for ────────────────────────────────────────────────────────────

class TestNestedFor:
    def test_nested_for_cartesian(self):
        out, _, rc = clython_run(
            "result = []\nfor i in range(3):\n    for j in range(3):\n        if i == j:\n            result.append(i)\nprint(result)"
        )
        assert rc == 0 and out == "[0, 1, 2]"

    def test_nested_for_matrix_sum(self):
        out, _, rc = clython_run(
            "matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]\ntotal = 0\nfor row in matrix:\n    for x in row:\n        total += x\nprint(total)"
        )
        assert rc == 0 and out == "45"

    def test_nested_for_break_inner_only(self):
        out, _, rc = clython_run(
            "outer_break = False\nresult = []\nfor i in range(5):\n    for j in range(5):\n        if j == 2:\n            break\n        result.append((i, j))\nprint(len(result))"
        )
        assert rc == 0 and out == "10"

    def test_nested_for_with_enumerate(self):
        out, _, rc = clython_run(
            "matrix = [['a', 'b'], ['c', 'd']]\nfor i, row in enumerate(matrix):\n    for j, val in enumerate(row):\n        print(i, j, val)"
        )
        assert rc == 0 and out == "0 0 a\n0 1 b\n1 0 c\n1 1 d"

    def test_nested_for_else_inner(self):
        """else on inner for applies to inner loop only"""
        out, _, rc = clython_run(
            "messages = []\nfor i in range(3):\n    for j in range(3):\n        if i == j:\n            break\n    else:\n        messages.append(i)\nprint(messages)"
        )
        assert rc == 0 and out == "[]"


# ── Iterables and functions ───────────────────────────────────────────────

class TestForIterables:
    def test_for_reversed(self):
        out, _, rc = clython_run(
            "result = []\nfor i in reversed([1, 2, 3]):\n    result.append(i)\nprint(result)"
        )
        assert rc == 0 and out == "[3, 2, 1]"

    def test_for_sorted(self):
        out, _, rc = clython_run(
            "result = []\nfor x in sorted([3, 1, 4, 1, 5, 9, 2, 6]):\n    result.append(x)\nprint(result)"
        )
        assert rc == 0 and out == "[1, 1, 2, 3, 4, 5, 6, 9]"

    def test_for_map(self):
        out, _, rc = clython_run(
            "result = list(map(lambda x: x * 2, range(5)))\nprint(result)"
        )
        assert rc == 0 and out == "[0, 2, 4, 6, 8]"

    def test_for_filter(self):
        out, _, rc = clython_run(
            "result = list(filter(lambda x: x % 2 == 0, range(10)))\nprint(result)"
        )
        assert rc == 0 and out == "[0, 2, 4, 6, 8]"

    def test_for_set_iteration(self):
        out, _, rc = clython_run(
            "result = sorted([x for x in {3, 1, 2}])\nprint(result)"
        )
        assert rc == 0 and out == "[1, 2, 3]"

    def test_for_list_comprehension(self):
        out, _, rc = clython_run(
            "squares = [x**2 for x in range(6)]\nprint(squares)"
        )
        assert rc == 0 and out == "[0, 1, 4, 9, 16, 25]"

    def test_for_list_comprehension_filter(self):
        out, _, rc = clython_run(
            "evens = [x for x in range(10) if x % 2 == 0]\nprint(evens)"
        )
        assert rc == 0 and out == "[0, 2, 4, 6, 8]"
