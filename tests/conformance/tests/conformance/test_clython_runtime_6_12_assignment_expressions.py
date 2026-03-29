"""
Clython runtime tests for Section 6.12: Assignment Expressions (Walrus Operator).

Tests the := operator through the Clython binary. Requires Python 3.8+.
"""

import os
import subprocess
import pytest
import sys

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
# Basic walrus operator
# ---------------------------------------------------------------------------

def test_walrus_in_if_condition():
    """Walrus operator assigns and tests in if condition."""
    source = (
        "items = [1, 2, 3]\n"
        "if (n := len(items)) > 2:\n"
        "    print(n)\n"
    )
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "3"


@pytest.mark.xfail(reason="re module fails to load in Clython (ParseError in re source)")
def test_walrus_variable_available_after():
    """Variable bound by := is available after the expression."""
    source = (
        "import re\n"
        "text = 'hello123'\n"
        "if (m := re.search(r'\\d+', text)):\n"
        "    print(m.group())\n"
    )
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "123"


def test_walrus_assigns_value():
    """The walrus expression evaluates to the assigned value."""
    source = "x = (y := 42); print(x, y)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "42 42"


def test_walrus_in_while_loop():
    """Walrus operator in while loop condition."""
    source = (
        "data = [3, 2, 1, 0]\n"
        "i = 0\n"
        "total = 0\n"
        "while (v := data[i]) > 0:\n"
        "    total += v\n"
        "    i += 1\n"
        "print(total)\n"
    )
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "6"


def test_walrus_false_branch():
    """Walrus in if: false branch when assigned value is falsy."""
    source = (
        "x = 0\n"
        "if (y := x):\n"
        "    print('truthy')\n"
        "else:\n"
        "    print('falsy:', y)\n"
    )
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "falsy: 0"


# ---------------------------------------------------------------------------
# Walrus in comprehensions
# ---------------------------------------------------------------------------

def test_walrus_in_list_comprehension_filter():
    """Walrus operator in list comprehension filter."""
    source = (
        "def double(x): return x * 2\n"
        "result = [y for x in range(5) if (y := double(x)) > 4]\n"
        "print(result)\n"
    )
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "[6, 8]"


def test_walrus_in_list_comprehension_value():
    """Walrus operator used to compute value and reuse in comprehension."""
    source = (
        "result = [(y, y*y) for x in range(4) if (y := x + 1) > 1]\n"
        "print(result)\n"
    )
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "[(2, 4), (3, 9), (4, 16)]"


# ---------------------------------------------------------------------------
# Walrus combined with boolean operators
# ---------------------------------------------------------------------------

def test_walrus_and_boolean():
    """Walrus used with and operator."""
    source = (
        "data = [1, 2, 3]\n"
        "if (n := len(data)) and n > 1:\n"
        "    print('multiple:', n)\n"
    )
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "multiple: 3"


def test_walrus_or_fallback():
    """Walrus combined with or for fallback."""
    source = (
        "def get_value(key, d): return d.get(key)\n"
        "d = {'x': 10}\n"
        "v = (result := get_value('x', d)) or 0\n"
        "print(result, v)\n"
    )
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "10 10"


# ---------------------------------------------------------------------------
# Walrus with multiple expressions
# ---------------------------------------------------------------------------

def test_two_walrus_in_condition():
    """Two walrus operators in same condition."""
    source = (
        "def f(): return 3\n"
        "def g(): return 4\n"
        "if (a := f()) and (b := g()):\n"
        "    print(a + b)\n"
    )
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "7"


def test_walrus_in_arithmetic():
    """Walrus operator result used in arithmetic."""
    source = "result = (x := 6) * 7; print(x, result)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "6 42"


# ---------------------------------------------------------------------------
# Error conditions
# ---------------------------------------------------------------------------

def test_walrus_attribute_target_raises():
    """Assignment to attribute via := should raise an error (SyntaxError or LexerError)."""
    source = "obj = type('O', (), {})()\nif (obj.x := 5): pass"
    out, err, rc = clython_run(source)
    assert rc != 0


def test_walrus_at_statement_level_ok():
    """Walrus at statement level (expression statement) is valid Python."""
    source = "(x := 5)"
    out, err, rc = clython_run(source)
    # Statement-level walrus is valid syntax — just verify it runs without error
    assert rc == 0


def test_walrus_result_is_correct_type():
    """Value bound by walrus has correct type."""
    source = (
        "if (s := 'hello'):\n"
        "    print(type(s).__name__)\n"
    )
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "str"


def test_walrus_in_function_call_arg():
    """Walrus used inside a function call argument."""
    source = "print((x := 5) + 1, x)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "6 5"


def test_walrus_loop_accumulate():
    """Walrus in loop to accumulate results."""
    source = (
        "nums = [1, 2, 3, 4, 5]\n"
        "total = 0\n"
        "for n in nums:\n"
        "    if (doubled := n * 2) > 4:\n"
        "        total += doubled\n"
        "print(total)\n"
    )
    out, err, rc = clython_run(source)
    assert rc == 0
    # n=3 -> 6, n=4 -> 8, n=5 -> 10 => 24
    assert out == "24"
