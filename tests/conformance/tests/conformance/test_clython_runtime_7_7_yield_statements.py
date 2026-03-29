"""
Section 7.7: Yield Statements - Clython Runtime Test Suite

Tests that Clython actually executes yield statements correctly at runtime.
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


def test_simple_generator():
    """Basic generator with yield produces values"""
    out, err, rc = clython_run(
        "def gen():\n"
        "    yield 1\n"
        "    yield 2\n"
        "    yield 3\n"
        "print(list(gen()))"
    )
    assert rc == 0
    assert out == "[1, 2, 3]"


def test_generator_in_for_loop():
    """Generator consumed by for loop"""
    out, err, rc = clython_run(
        "def countdown(n):\n"
        "    while n > 0:\n"
        "        yield n\n"
        "        n -= 1\n"
        "for x in countdown(3):\n"
        "    print(x)"
    )
    assert rc == 0
    assert out == "3\n2\n1"


def test_generator_next():
    """Generator advances with next()"""
    out, err, rc = clython_run(
        "def gen():\n"
        "    yield 'a'\n"
        "    yield 'b'\n"
        "g = gen()\n"
        "print(next(g))\n"
        "print(next(g))"
    )
    assert rc == 0
    assert out == "a\nb"


def test_generator_stopiteration():
    """Generator raises StopIteration when exhausted"""
    out, err, rc = clython_run(
        "def gen():\n"
        "    yield 1\n"
        "g = gen()\n"
        "next(g)\n"
        "try:\n"
        "    next(g)\n"
        "except StopIteration:\n"
        "    print('exhausted')"
    )
    assert rc == 0
    assert out == "exhausted"


def test_yield_none():
    """Yield without value yields None"""
    out, err, rc = clython_run(
        "def gen():\n"
        "    yield\n"
        "    yield\n"
        "print(list(gen()))"
    )
    assert rc == 0
    assert out == "[None, None]"


def test_yield_from_list():
    """yield from delegates to an iterable"""
    out, err, rc = clython_run(
        "def gen():\n"
        "    yield from [1, 2, 3]\n"
        "print(list(gen()))"
    )
    assert rc == 0
    assert out == "[1, 2, 3]"


def test_yield_from_range():
    """yield from range()"""
    out, err, rc = clython_run(
        "def gen():\n"
        "    yield from range(5)\n"
        "print(list(gen()))"
    )
    assert rc == 0
    assert out == "[0, 1, 2, 3, 4]"


def test_yield_from_generator():
    """yield from another generator"""
    out, err, rc = clython_run(
        "def inner():\n"
        "    yield 1\n"
        "    yield 2\n"
        "def outer():\n"
        "    yield from inner()\n"
        "    yield 3\n"
        "print(list(outer()))"
    )
    assert rc == 0
    assert out == "[1, 2, 3]"


def test_generator_with_return():
    """Generator with return raises StopIteration"""
    out, err, rc = clython_run(
        "def gen():\n"
        "    yield 1\n"
        "    return\n"
        "    yield 2\n"
        "print(list(gen()))"
    )
    assert rc == 0
    assert out == "[1]"


def test_generator_send():
    """Generator send() passes value to yield expression"""
    out, err, rc = clython_run(
        "def gen():\n"
        "    x = yield 1\n"
        "    yield x * 2\n"
        "g = gen()\n"
        "print(next(g))\n"
        "print(g.send(5))"
    )
    assert rc == 0
    assert out == "1\n10"


def test_generator_range_replacement():
    """Generator as lazy range replacement"""
    out, err, rc = clython_run(
        "def my_range(n):\n"
        "    i = 0\n"
        "    while i < n:\n"
        "        yield i\n"
        "        i += 1\n"
        "print(list(my_range(5)))"
    )
    assert rc == 0
    assert out == "[0, 1, 2, 3, 4]"


@pytest.mark.xfail(reason="itertools.islice not yet available in Clython")
def test_generator_fibonacci():
    """Fibonacci generator"""
    out, err, rc = clython_run(
        "def fib():\n"
        "    a, b = 0, 1\n"
        "    while True:\n"
        "        yield a\n"
        "        a, b = b, a + b\n"
        "import itertools\n"
        "print(list(itertools.islice(fib(), 8)))"
    )
    assert rc == 0
    assert out == "[0, 1, 1, 2, 3, 5, 8, 13]"


def test_generator_conditional_yield():
    """Generator with conditional yield"""
    out, err, rc = clython_run(
        "def evens(n):\n"
        "    for i in range(n):\n"
        "        if i % 2 == 0:\n"
        "            yield i\n"
        "print(list(evens(10)))"
    )
    assert rc == 0
    assert out == "[0, 2, 4, 6, 8]"


def test_generator_list_conversion():
    """list() fully consumes a generator"""
    out, err, rc = clython_run(
        "def gen():\n"
        "    for i in range(5): yield i * i\n"
        "print(list(gen()))"
    )
    assert rc == 0
    assert out == "[0, 1, 4, 9, 16]"


def test_generator_sum():
    """sum() works with generator expression"""
    out, err, rc = clython_run("print(sum(x*x for x in range(5)))")
    assert rc == 0
    assert out == "30"


def test_generator_is_iterator():
    """Generator objects support iter() and next()"""
    out, err, rc = clython_run(
        "def gen():\n"
        "    yield 1\n"
        "    yield 2\n"
        "g = gen()\n"
        "print(iter(g) is g)\n"
        "print(next(g))"
    )
    assert rc == 0
    assert out == "True\n1"


def test_yield_in_try_except():
    """Yield inside try/except"""
    out, err, rc = clython_run(
        "def gen():\n"
        "    try:\n"
        "        yield 1\n"
        "        yield 2\n"
        "    except Exception:\n"
        "        yield -1\n"
        "print(list(gen()))"
    )
    assert rc == 0
    assert out == "[1, 2]"


def test_multiple_yield_from():
    """Multiple yield from in sequence"""
    out, err, rc = clython_run(
        "def gen():\n"
        "    yield from [1, 2]\n"
        "    yield from [3, 4]\n"
        "    yield from [5]\n"
        "print(list(gen()))"
    )
    assert rc == 0
    assert out == "[1, 2, 3, 4, 5]"


def test_generator_with_default_param():
    """Generator function with default parameter"""
    out, err, rc = clython_run(
        "def repeat(val, times=3):\n"
        "    for _ in range(times): yield val\n"
        "print(list(repeat('x')))\n"
        "print(list(repeat('y', 2)))"
    )
    assert rc == 0
    assert out == "['x', 'x', 'x']\n['y', 'y']"


def test_nested_generators():
    """Nested generator composition"""
    out, err, rc = clython_run(
        "def gen1():\n"
        "    yield from range(3)\n"
        "def gen2():\n"
        "    yield from gen1()\n"
        "    yield from gen1()\n"
        "print(list(gen2()))"
    )
    assert rc == 0
    assert out == "[0, 1, 2, 0, 1, 2]"


def test_generator_close():
    """Generator close() terminates generator"""
    out, err, rc = clython_run(
        "def gen():\n"
        "    yield 1\n"
        "    yield 2\n"
        "    yield 3\n"
        "g = gen()\n"
        "print(next(g))\n"
        "g.close()\n"
        "try:\n"
        "    next(g)\n"
        "except StopIteration:\n"
        "    print('closed')"
    )
    assert rc == 0
    assert out == "1\nclosed"


def test_generator_in_class():
    """Generator method in class"""
    out, err, rc = clython_run(
        "class Counter:\n"
        "    def __init__(self, n): self.n = n\n"
        "    def generate(self):\n"
        "        for i in range(self.n): yield i\n"
        "c = Counter(4)\n"
        "print(list(c.generate()))"
    )
    assert rc == 0
    assert out == "[0, 1, 2, 3]"
