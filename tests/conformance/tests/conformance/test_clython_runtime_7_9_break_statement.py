"""Clython runtime tests — Section 7.9: Break Statement.

Tests that the Clython interpreter correctly terminates loops
with break in various contexts.
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


class TestBreakStatementRuntime:
    def test_break_for_loop(self):
        """break exits a for loop early"""
        out, err, rc = clython_run(
            "for i in range(10):\n    if i == 3:\n        break\nprint(i)"
        )
        assert rc == 0
        assert out == "3"

    def test_break_while_loop(self):
        """break exits a while loop early"""
        out, err, rc = clython_run(
            "i = 0\nwhile True:\n    if i == 5:\n        break\n    i += 1\nprint(i)"
        )
        assert rc == 0
        assert out == "5"

    def test_break_prevents_else(self):
        """break prevents the loop else clause from executing"""
        out, err, rc = clython_run(
            "for i in range(5):\n    if i == 2:\n        break\nelse:\n    print('else')\nprint('done')"
        )
        assert rc == 0
        assert out == "done"

    def test_no_break_executes_else(self):
        """loop else clause executes when loop finishes without break"""
        out, err, rc = clython_run(
            "for i in range(3):\n    pass\nelse:\n    print('else')"
        )
        assert rc == 0
        assert out == "else"

    def test_break_inner_loop_only(self):
        """break only exits the innermost loop"""
        out, err, rc = clython_run(
            "result = []\n"
            "for i in range(3):\n"
            "    for j in range(3):\n"
            "        if j == 1:\n"
            "            break\n"
            "    result.append(i)\n"
            "print(result)"
        )
        assert rc == 0
        assert out == "[0, 1, 2]"

    def test_break_nested_outer_loop(self):
        """break outer loop after inner completes"""
        out, err, rc = clython_run(
            "found = False\n"
            "for i in range(5):\n"
            "    for j in range(5):\n"
            "        if i == 2 and j == 2:\n"
            "            found = True\n"
            "            break\n"
            "    if found:\n"
            "        break\n"
            "print(i, j)"
        )
        assert rc == 0
        assert out == "2 2"

    def test_break_with_try_except(self):
        """break inside try/except still exits loop"""
        out, err, rc = clython_run(
            "for i in range(5):\n"
            "    try:\n"
            "        if i == 2:\n"
            "            break\n"
            "    except Exception:\n"
            "        pass\n"
            "print(i)"
        )
        assert rc == 0
        assert out == "2"

    def test_break_accumulation_stops(self):
        """values accumulated before break are preserved"""
        out, err, rc = clython_run(
            "result = []\n"
            "for i in range(10):\n"
            "    if i == 4:\n"
            "        break\n"
            "    result.append(i)\n"
            "print(result)"
        )
        assert rc == 0
        assert out == "[0, 1, 2, 3]"

    def test_break_while_accumulation(self):
        """break in while loop stops accumulation correctly"""
        out, err, rc = clython_run(
            "items = []\ni = 0\n"
            "while i < 100:\n"
            "    items.append(i)\n"
            "    if i == 3:\n"
            "        break\n"
            "    i += 1\n"
            "print(items)"
        )
        assert rc == 0
        assert out == "[0, 1, 2, 3]"

    def test_break_multiple_conditions(self):
        """multiple break conditions — first hit exits"""
        out, err, rc = clython_run(
            "for i in range(20):\n"
            "    if i == 5:\n"
            "        break\n"
            "    if i == 10:\n"
            "        break\n"
            "print(i)"
        )
        assert rc == 0
        assert out == "5"

    def test_break_in_conditional(self):
        """break inside if/elif"""
        out, err, rc = clython_run(
            "for i in range(10):\n"
            "    if i < 3:\n"
            "        pass\n"
            "    elif i == 5:\n"
            "        break\n"
            "print(i)"
        )
        assert rc == 0
        assert out == "5"

    def test_break_while_else(self):
        """while-else: break prevents else"""
        out, err, rc = clython_run(
            "i = 0\n"
            "while i < 10:\n"
            "    if i == 3:\n"
            "        break\n"
            "    i += 1\n"
            "else:\n"
            "    print('exhausted')\n"
            "print('exit', i)"
        )
        assert rc == 0
        assert out == "exit 3"

    def test_break_first_iteration(self):
        """break on first iteration — loop body runs once"""
        out, err, rc = clython_run(
            "count = 0\n"
            "for i in range(100):\n"
            "    count += 1\n"
            "    break\n"
            "print(count)"
        )
        assert rc == 0
        assert out == "1"

    def test_break_with_finally(self):
        """break inside try still runs finally"""
        out, err, rc = clython_run(
            "ran_finally = False\n"
            "for i in range(3):\n"
            "    try:\n"
            "        break\n"
            "    finally:\n"
            "        ran_finally = True\n"
            "print(ran_finally)"
        )
        assert rc == 0
        assert out == "True"

    def test_break_search_pattern(self):
        """break in classic search pattern sets flag correctly"""
        out, err, rc = clython_run(
            "data = [1, 3, 5, 7, 9, 6, 11]\n"
            "found = False\n"
            "for x in data:\n"
            "    if x % 2 == 0:\n"
            "        found = True\n"
            "        break\n"
            "print(found, x)"
        )
        assert rc == 0
        assert out == "True 6"
