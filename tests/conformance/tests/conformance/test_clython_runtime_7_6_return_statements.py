"""
Section 7.6: Return Statements - Clython Runtime Test Suite

Tests that Clython actually executes return statements correctly at runtime.
Uses subprocess-based execution via CLYTHON_BIN.
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


def test_return_integer():
    """Function returns an integer"""
    out, err, rc = clython_run("def f(): return 42\nprint(f())")
    assert rc == 0
    assert out == "42"


def test_return_string():
    """Function returns a string"""
    out, err, rc = clython_run("def f(): return 'hello'\nprint(f())")
    assert rc == 0
    assert out == "hello"


def test_return_none_explicit():
    """Explicit return None"""
    out, err, rc = clython_run("def f(): return None\nprint(f() is None)")
    assert rc == 0
    assert out == "True"


def test_bare_return_gives_none():
    """Bare return produces None"""
    out, err, rc = clython_run("def f(): return\nprint(f() is None)")
    assert rc == 0
    assert out == "True"


def test_no_return_gives_none():
    """Function without return produces None"""
    out, err, rc = clython_run("def f(): pass\nprint(f() is None)")
    assert rc == 0
    assert out == "True"


def test_return_expression():
    """Return arithmetic expression"""
    out, err, rc = clython_run("def f(x, y): return x * y + 1\nprint(f(3, 4))")
    assert rc == 0
    assert out == "13"


def test_return_list():
    """Return a list"""
    out, err, rc = clython_run("def f(): return [1, 2, 3]\nprint(f())")
    assert rc == 0
    assert out == "[1, 2, 3]"


def test_return_dict():
    """Return a dictionary"""
    out, err, rc = clython_run("def f(): return {'a': 1, 'b': 2}\nprint(f()['a'])")
    assert rc == 0
    assert out == "1"


def test_return_tuple():
    """Return a tuple (multiple values)"""
    out, err, rc = clython_run("def f(): return 1, 2, 3\nprint(f())")
    assert rc == 0
    assert out == "(1, 2, 3)"


def test_return_multiple_values_unpack():
    """Return multiple values, unpack at call site"""
    out, err, rc = clython_run(
        "def get_pair(): return 10, 20\n"
        "a, b = get_pair()\n"
        "print(a, b)"
    )
    assert rc == 0
    assert out == "10 20"


def test_early_return():
    """Early return short-circuits execution"""
    out, err, rc = clython_run(
        "def f(x):\n"
        "    if x < 0: return 'neg'\n"
        "    return 'non-neg'\n"
        "print(f(-5))\n"
        "print(f(5))"
    )
    assert rc == 0
    assert out == "neg\nnon-neg"


def test_multiple_return_paths():
    """Function with multiple conditional return paths"""
    out, err, rc = clython_run(
        "def classify(x):\n"
        "    if x > 0: return 'positive'\n"
        "    elif x < 0: return 'negative'\n"
        "    else: return 'zero'\n"
        "print(classify(1))\n"
        "print(classify(-1))\n"
        "print(classify(0))"
    )
    assert rc == 0
    assert out == "positive\nnegative\nzero"


def test_return_from_loop():
    """Return from inside a loop"""
    out, err, rc = clython_run(
        "def find(items, target):\n"
        "    for item in items:\n"
        "        if item == target: return item\n"
        "    return None\n"
        "print(find([1, 2, 3], 2))\n"
        "print(find([1, 2, 3], 9))"
    )
    assert rc == 0
    assert out == "2\nNone"


def test_return_from_nested_loop():
    """Return from nested loops"""
    out, err, rc = clython_run(
        "def find_pair(matrix, val):\n"
        "    for i, row in enumerate(matrix):\n"
        "        for j, x in enumerate(row):\n"
        "            if x == val: return (i, j)\n"
        "    return None\n"
        "m = [[1,2],[3,4]]\n"
        "print(find_pair(m, 3))"
    )
    assert rc == 0
    assert out == "(1, 0)"


def test_return_function_call():
    """Return result of function call"""
    out, err, rc = clython_run(
        "def double(x): return x * 2\n"
        "def quad(x): return double(double(x))\n"
        "print(quad(3))"
    )
    assert rc == 0
    assert out == "12"


def test_return_in_method():
    """Return statement in class method"""
    out, err, rc = clython_run(
        "class Calc:\n"
        "    def add(self, a, b): return a + b\n"
        "c = Calc()\n"
        "print(c.add(5, 7))"
    )
    assert rc == 0
    assert out == "12"


def test_return_in_async_function():
    """Return in async function"""
    out, err, rc = clython_run(
        "import asyncio\n"
        "async def f(): return 99\n"
        "print(asyncio.run(f()))"
    )
    assert rc == 0
    assert out == "99"


def test_return_in_try_except():
    """Return from try block"""
    out, err, rc = clython_run(
        "def safe_div(a, b):\n"
        "    try:\n"
        "        return a // b\n"
        "    except ZeroDivisionError:\n"
        "        return None\n"
        "print(safe_div(10, 2))\n"
        "print(safe_div(10, 0))"
    )
    assert rc == 0
    assert out == "5\nNone"


def test_return_in_generator_becomes_stopiteration():
    """Return in generator raises StopIteration"""
    out, err, rc = clython_run(
        "def gen():\n"
        "    yield 1\n"
        "    yield 2\n"
        "    return\n"
        "g = gen()\n"
        "print(next(g))\n"
        "print(next(g))\n"
        "try:\n"
        "    next(g)\n"
        "except StopIteration:\n"
        "    print('stopped')"
    )
    assert rc == 0
    assert out == "1\n2\nstopped"


def test_recursive_return():
    """Recursive function with return"""
    out, err, rc = clython_run(
        "def fib(n):\n"
        "    if n <= 1: return n\n"
        "    return fib(n-1) + fib(n-2)\n"
        "print(fib(10))"
    )
    assert rc == 0
    assert out == "55"


def test_return_list_comprehension():
    """Return list comprehension"""
    out, err, rc = clython_run(
        "def squares(n): return [x**2 for x in range(n)]\n"
        "print(squares(5))"
    )
    assert rc == 0
    assert out == "[0, 1, 4, 9, 16]"


def test_return_conditional_expression():
    """Return conditional (ternary) expression"""
    out, err, rc = clython_run(
        "def abs_val(x): return x if x >= 0 else -x\n"
        "print(abs_val(-5))\n"
        "print(abs_val(5))"
    )
    assert rc == 0
    assert out == "5\n5"


def test_return_from_finally():
    """Return in try/finally runs finally first"""
    out, err, rc = clython_run(
        "steps = []\n"
        "def f():\n"
        "    try:\n"
        "        steps.append('try')\n"
        "        return 'result'\n"
        "    finally:\n"
        "        steps.append('finally')\n"
        "val = f()\n"
        "print(val)\n"
        "print(steps)"
    )
    assert rc == 0
    assert out == "result\n['try', 'finally']"
