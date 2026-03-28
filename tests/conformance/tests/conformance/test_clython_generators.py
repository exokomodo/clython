"""
Clython generator tests — yield, yield from, generator expressions, iterator protocol.

Tests generators and the iterator protocol per Python Language Reference §6.2.9.
"""

import os
import subprocess
import pytest

CLYTHON_BIN = os.environ.get("CLYTHON_BIN")

pytestmark = pytest.mark.skipif(
    not CLYTHON_BIN, reason="CLYTHON_BIN not set — skipping Clython-specific tests"
)


def clython_run(source: str, timeout: float = 30.0):
    """Run source through Clython, return (stdout, stderr, returncode)."""
    result = subprocess.run(
        [CLYTHON_BIN, "-c", source],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode


class TestGeneratorBasics:
    """Basic generator function tests."""

    def test_simple_generator(self):
        out, _, rc = clython_run(
            "def gen():\n    yield 1\n    yield 2\n    yield 3\nfor x in gen():\n    print(x)"
        )
        assert rc == 0 and out == "1\n2\n3"

    def test_generator_range(self):
        out, _, rc = clython_run(
            "def count(n):\n    i = 0\n    while i < n:\n        yield i\n        i += 1\n"
            "for x in count(5):\n    print(x)"
        )
        assert rc == 0 and out == "0\n1\n2\n3\n4"

    def test_generator_list_conversion(self):
        out, _, rc = clython_run(
            "def gen():\n    yield 1\n    yield 2\nprint(list(gen()))"
        )
        assert rc == 0 and out == "[1, 2]"

    def test_generator_next(self):
        out, _, rc = clython_run(
            "def gen():\n    yield 10\n    yield 20\ng = gen()\nprint(next(g))\nprint(next(g))"
        )
        assert rc == 0 and out == "10\n20"

    def test_generator_stopiteration(self):
        out, _, rc = clython_run(
            "def gen():\n    yield 1\ng = gen()\nnext(g)\n"
            "try:\n    next(g)\nexcept StopIteration:\n    print('stopped')"
        )
        assert rc == 0 and out == "stopped"

    def test_generator_with_return(self):
        out, _, rc = clython_run(
            "def gen():\n    yield 1\n    return\n    yield 2\nprint(list(gen()))"
        )
        assert rc == 0 and out == "[1]"

    def test_empty_generator(self):
        out, _, rc = clython_run(
            "def gen():\n    return\n    yield\nprint(list(gen()))"
        )
        assert rc == 0 and out == "[]"

    def test_bare_yield(self):
        out, _, rc = clython_run(
            "def gen():\n    yield\n    yield\ng = gen()\nprint(next(g))\nprint(next(g))"
        )
        assert rc == 0 and out == "None\nNone"


class TestGeneratorWithLoops:
    """Generators interacting with loops and control flow."""

    def test_infinite_generator(self):
        out, _, rc = clython_run(
            "def naturals():\n    n = 0\n    while True:\n        yield n\n        n += 1\n"
            "g = naturals()\nresult = []\nfor i in range(5):\n    result.append(next(g))\n"
            "print(result)"
        )
        assert rc == 0 and out == "[0, 1, 2, 3, 4]"

    def test_fibonacci_generator(self):
        out, _, rc = clython_run(
            "def fib():\n    a, b = 0, 1\n    while True:\n        yield a\n        a, b = b, a + b\n"
            "g = fib()\nresult = []\nfor i in range(8):\n    result.append(next(g))\n"
            "print(result)"
        )
        assert rc == 0 and out == "[0, 1, 1, 2, 3, 5, 8, 13]"

    def test_generator_for_loop(self):
        """Generators work with for loops via __iter__/__next__."""
        out, _, rc = clython_run(
            "def squares(n):\n    for i in range(n):\n        yield i * i\n"
            "for s in squares(5):\n    print(s)"
        )
        assert rc == 0 and out == "0\n1\n4\n9\n16"

    def test_multiple_generators(self):
        """Multiple independent generator instances."""
        out, _, rc = clython_run(
            "def count(start):\n    n = start\n    while True:\n        yield n\n        n += 1\n"
            "a = count(0)\nb = count(100)\n"
            "print(next(a))\nprint(next(b))\nprint(next(a))\nprint(next(b))"
        )
        assert rc == 0 and out == "0\n100\n1\n101"


class TestYieldFrom:
    """yield from delegation."""

    def test_yield_from_basic(self):
        out, _, rc = clython_run(
            "def inner():\n    yield 1\n    yield 2\n"
            "def outer():\n    yield from inner()\n    yield 3\n"
            "print(list(outer()))"
        )
        assert rc == 0 and out == "[1, 2, 3]"

    def test_yield_from_list(self):
        out, _, rc = clython_run(
            "def gen():\n    yield from [1, 2, 3]\nprint(list(gen()))"
        )
        assert rc == 0 and out == "[1, 2, 3]"

    def test_yield_from_range(self):
        out, _, rc = clython_run(
            "def gen():\n    yield from range(5)\nprint(list(gen()))"
        )
        assert rc == 0 and out == "[0, 1, 2, 3, 4]"

    def test_yield_from_chain(self):
        """Chaining multiple iterables via yield from."""
        out, _, rc = clython_run(
            "def chain(*iterables):\n    for it in iterables:\n        yield from it\n"
            "print(list(chain([1, 2], [3, 4], [5])))"
        )
        assert rc == 0 and out == "[1, 2, 3, 4, 5]"

    def test_yield_from_nested_generators(self):
        out, _, rc = clython_run(
            "def a():\n    yield 1\n    yield 2\n"
            "def b():\n    yield from a()\n    yield 3\n"
            "def c():\n    yield from b()\n    yield 4\n"
            "print(list(c()))"
        )
        assert rc == 0 and out == "[1, 2, 3, 4]"


class TestGeneratorExpression:
    """Generator expressions (genexps)."""

    def test_genexp_basic(self):
        out, _, rc = clython_run(
            "g = (x*x for x in range(4))\nfor v in g:\n    print(v)"
        )
        assert rc == 0 and out == "0\n1\n4\n9"

    def test_genexp_list(self):
        out, _, rc = clython_run(
            "print(list(x*2 for x in range(5)))"
        )
        assert rc == 0 and out == "[0, 2, 4, 6, 8]"

    def test_genexp_sum(self):
        out, _, rc = clython_run(
            "print(sum(x for x in range(10)))"
        )
        assert rc == 0 and out == "45"

    def test_genexp_with_condition(self):
        out, _, rc = clython_run(
            "print(list(x for x in range(10) if x % 2 == 0))"
        )
        assert rc == 0 and out == "[0, 2, 4, 6, 8]"


class TestGeneratorWithArgs:
    """Generators with function arguments."""

    def test_generator_with_args(self):
        out, _, rc = clython_run(
            "def repeat(val, n):\n    for i in range(n):\n        yield val\n"
            "print(list(repeat('x', 3)))"
        )
        assert rc == 0 and out == "['x', 'x', 'x']"

    def test_generator_with_default_args(self):
        out, _, rc = clython_run(
            "def count(start=0, step=1):\n    n = start\n    for i in range(5):\n        yield n\n        n += step\n"
            "print(list(count()))\nprint(list(count(10, 2)))"
        )
        assert rc == 0 and out == "[0, 1, 2, 3, 4]\n[10, 12, 14, 16, 18]"

    def test_generator_with_varargs(self):
        out, _, rc = clython_run(
            "def chain(*iterables):\n    for it in iterables:\n        for x in it:\n            yield x\n"
            "print(list(chain([1, 2], [3], [4, 5])))"
        )
        assert rc == 0 and out == "[1, 2, 3, 4, 5]"
