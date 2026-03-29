"""Clython runtime tests — Section 7.10: Continue Statement.

Tests that the Clython interpreter correctly skips to the next
loop iteration with continue in various contexts.
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


class TestContinueStatementRuntime:
    def test_continue_skips_iteration(self):
        """continue skips the rest of the current iteration"""
        out, err, rc = clython_run(
            "result = []\n"
            "for i in range(5):\n"
            "    if i == 2:\n"
            "        continue\n"
            "    result.append(i)\n"
            "print(result)"
        )
        assert rc == 0
        assert out == "[0, 1, 3, 4]"

    def test_continue_in_while_loop(self):
        """continue in while loop advances to next iteration"""
        out, err, rc = clython_run(
            "result = []\ni = 0\n"
            "while i < 6:\n"
            "    i += 1\n"
            "    if i % 2 == 0:\n"
            "        continue\n"
            "    result.append(i)\n"
            "print(result)"
        )
        assert rc == 0
        assert out == "[1, 3, 5]"

    def test_continue_does_not_affect_else(self):
        """continue does NOT prevent the loop else clause"""
        out, err, rc = clython_run(
            "for i in range(3):\n"
            "    if i == 1:\n"
            "        continue\n"
            "else:\n"
            "    print('else ran')"
        )
        assert rc == 0
        assert out == "else ran"

    def test_continue_inner_loop_only(self):
        """continue only affects the innermost loop"""
        out, err, rc = clython_run(
            "result = []\n"
            "for i in range(3):\n"
            "    for j in range(3):\n"
            "        if j == 1:\n"
            "            continue\n"
            "        result.append((i, j))\n"
            "print(result)"
        )
        assert rc == 0
        assert out == "[(0, 0), (0, 2), (1, 0), (1, 2), (2, 0), (2, 2)]"

    def test_continue_filter_odds(self):
        """continue to filter odd numbers"""
        out, err, rc = clython_run(
            "evens = []\n"
            "for i in range(10):\n"
            "    if i % 2 != 0:\n"
            "        continue\n"
            "    evens.append(i)\n"
            "print(evens)"
        )
        assert rc == 0
        assert out == "[0, 2, 4, 6, 8]"

    def test_continue_multiple_conditions(self):
        """multiple continue guards"""
        out, err, rc = clython_run(
            "result = []\n"
            "for i in range(10):\n"
            "    if i < 3:\n"
            "        continue\n"
            "    if i > 6:\n"
            "        continue\n"
            "    result.append(i)\n"
            "print(result)"
        )
        assert rc == 0
        assert out == "[3, 4, 5, 6]"

    def test_continue_in_try_except(self):
        """continue inside try/except skips to next iteration"""
        out, err, rc = clython_run(
            "result = []\n"
            "for i in range(5):\n"
            "    try:\n"
            "        if i == 2:\n"
            "            continue\n"
            "    except Exception:\n"
            "        pass\n"
            "    result.append(i)\n"
            "print(result)"
        )
        assert rc == 0
        assert out == "[0, 1, 3, 4]"

    def test_continue_code_after_is_skipped(self):
        """code after continue in same iteration is not executed"""
        out, err, rc = clython_run(
            "executed = []\n"
            "for i in range(4):\n"
            "    if i == 2:\n"
            "        continue\n"
            "    executed.append(i)\n"
            "print(executed)"
        )
        assert rc == 0
        assert out == "[0, 1, 3]"

    def test_continue_counter_still_increments(self):
        """while loop counter still increments when continue is hit"""
        out, err, rc = clython_run(
            "count = 0\niterations = 0\ni = 0\n"
            "while i < 5:\n"
            "    i += 1\n"
            "    iterations += 1\n"
            "    if i % 2 == 0:\n"
            "        continue\n"
            "    count += 1\n"
            "print(iterations, count)"
        )
        assert rc == 0
        assert out == "5 3"

    def test_continue_with_accumulator(self):
        """continue skips accumulation for certain values"""
        out, err, rc = clython_run(
            "total = 0\n"
            "for i in range(1, 11):\n"
            "    if i % 3 == 0:\n"
            "        continue\n"
            "    total += i\n"
            "print(total)"
        )
        assert rc == 0
        # Sum of 1..10 excluding multiples of 3 (3,6,9): 55 - 18 = 37
        assert out == "37"

    def test_continue_nested_with_break(self):
        """continue in inner loop, break in outer loop"""
        out, err, rc = clython_run(
            "result = []\n"
            "for i in range(4):\n"
            "    for j in range(4):\n"
            "        if j == 2:\n"
            "            continue\n"
            "        result.append(j)\n"
            "    if i == 1:\n"
            "        break\n"
            "print(result)"
        )
        assert rc == 0
        assert out == "[0, 1, 3, 0, 1, 3]"

    def test_continue_first_iteration(self):
        """continue on first iteration still runs remaining iterations"""
        out, err, rc = clython_run(
            "result = []\n"
            "for i in range(5):\n"
            "    if i == 0:\n"
            "        continue\n"
            "    result.append(i)\n"
            "print(result)"
        )
        assert rc == 0
        assert out == "[1, 2, 3, 4]"

    def test_continue_last_iteration(self):
        """continue on last iteration produces same result as normal"""
        out, err, rc = clython_run(
            "result = []\n"
            "for i in range(5):\n"
            "    if i == 4:\n"
            "        continue\n"
            "    result.append(i)\n"
            "print(result)"
        )
        assert rc == 0
        assert out == "[0, 1, 2, 3]"

    def test_continue_with_finally(self):
        """continue inside try still runs finally"""
        out, err, rc = clython_run(
            "finally_count = 0\n"
            "for i in range(3):\n"
            "    try:\n"
            "        continue\n"
            "    finally:\n"
            "        finally_count += 1\n"
            "print(finally_count)"
        )
        assert rc == 0
        assert out == "3"

    def test_continue_enumerate(self):
        """continue works correctly with enumerate"""
        out, err, rc = clython_run(
            "result = []\n"
            "for idx, val in enumerate(['a', 'b', 'c', 'd']):\n"
            "    if idx % 2 == 1:\n"
            "        continue\n"
            "    result.append(val)\n"
            "print(result)"
        )
        assert rc == 0
        assert out == "['a', 'c']"
