"""
Section 8.8: Async Function Definitions - Clython Runtime Test Suite

Tests that Clython actually executes async function definitions correctly at runtime.
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


def test_basic_async_def():
    """Basic async def can be defined and run via asyncio.run"""
    out, err, rc = clython_run(
        "import asyncio\n"
        "async def main(): return 42\n"
        "print(asyncio.run(main()))"
    )
    assert rc == 0
    assert out == "42"


def test_async_def_with_await():
    """async def with await expression"""
    out, err, rc = clython_run(
        "import asyncio\n"
        "async def get_val():\n"
        "    await asyncio.sleep(0)\n"
        "    return 'done'\n"
        "print(asyncio.run(get_val()))"
    )
    assert rc == 0
    assert out == "done"


@pytest.mark.xfail(reason="asyncio.iscoroutine not yet available in Clython's asyncio stub")
def test_async_def_returns_coroutine():
    """async def produces a coroutine object"""
    out, err, rc = clython_run(
        "import asyncio\n"
        "async def coro(): return 1\n"
        "c = coro()\n"
        "print(asyncio.iscoroutine(c))\n"
        "asyncio.run(c)"
    )
    assert rc == 0
    assert out == "True"


def test_async_def_with_parameters():
    """async def with parameters"""
    out, err, rc = clython_run(
        "import asyncio\n"
        "async def add(a, b): return a + b\n"
        "print(asyncio.run(add(3, 4)))"
    )
    assert rc == 0
    assert out == "7"


def test_async_def_with_default_params():
    """async def with default parameter values"""
    out, err, rc = clython_run(
        "import asyncio\n"
        "async def greet(name='World'): return 'Hello ' + name\n"
        "print(asyncio.run(greet()))\n"
        "print(asyncio.run(greet('Clython')))"
    )
    assert rc == 0
    assert out == "Hello World\nHello Clython"


def test_async_def_with_annotation():
    """async def with type annotations"""
    out, err, rc = clython_run(
        "import asyncio\n"
        "async def double(x: int) -> int: return x * 2\n"
        "print(asyncio.run(double(21)))"
    )
    assert rc == 0
    assert out == "42"


def test_async_await_chain():
    """Chained await calls"""
    out, err, rc = clython_run(
        "import asyncio\n"
        "async def step1(): return 10\n"
        "async def step2(x): return x + 5\n"
        "async def main():\n"
        "    a = await step1()\n"
        "    b = await step2(a)\n"
        "    return b\n"
        "print(asyncio.run(main()))"
    )
    assert rc == 0
    assert out == "15"


def test_async_def_with_kwonly_params():
    """async def with keyword-only parameters"""
    out, err, rc = clython_run(
        "import asyncio\n"
        "async def f(a, *, b): return a + b\n"
        "print(asyncio.run(f(1, b=2)))"
    )
    assert rc == 0
    assert out == "3"


def test_async_def_with_args_kwargs():
    """async def with *args and **kwargs"""
    out, err, rc = clython_run(
        "import asyncio\n"
        "async def f(*args, **kwargs): return sum(args), len(kwargs)\n"
        "print(asyncio.run(f(1, 2, 3, x=4)))"
    )
    assert rc == 0
    assert out == "(6, 1)"


def test_async_nested_functions():
    """Nested async functions"""
    out, err, rc = clython_run(
        "import asyncio\n"
        "async def outer():\n"
        "    async def inner(): return 42\n"
        "    return await inner()\n"
        "print(asyncio.run(outer()))"
    )
    assert rc == 0
    assert out == "42"


def test_async_with_decorator():
    """Decorator on async function"""
    out, err, rc = clython_run(
        "import asyncio\n"
        "def deco(f):\n"
        "    async def wrapper(*a, **k):\n"
        "        return await f(*a, **k)\n"
        "    return wrapper\n"
        "@deco\n"
        "async def main(): return 99\n"
        "print(asyncio.run(main()))"
    )
    assert rc == 0
    assert out == "99"


def test_async_with_statement():
    """async with context manager"""
    out, err, rc = clython_run(
        "import asyncio\n"
        "class AsyncCtx:\n"
        "    async def __aenter__(self): return self\n"
        "    async def __aexit__(self, *a): pass\n"
        "    def value(self): return 42\n"
        "async def main():\n"
        "    async with AsyncCtx() as ctx:\n"
        "        print(ctx.value())\n"
        "asyncio.run(main())"
    )
    assert rc == 0
    assert out == "42"


@pytest.mark.xfail(reason="async for with async generators not yet supported in Clython")
def test_async_for_statement():
    """async for over async generator"""
    out, err, rc = clython_run(
        "import asyncio\n"
        "async def agen():\n"
        "    for i in range(3): yield i\n"
        "async def main():\n"
        "    result = []\n"
        "    async for item in agen(): result.append(item)\n"
        "    print(result)\n"
        "asyncio.run(main())"
    )
    assert rc == 0
    assert out == "[0, 1, 2]"


def test_async_exception_handling():
    """async def with try/except"""
    out, err, rc = clython_run(
        "import asyncio\n"
        "async def safe():\n"
        "    try:\n"
        "        raise ValueError('test')\n"
        "    except ValueError as e:\n"
        "        return str(e)\n"
        "print(asyncio.run(safe()))"
    )
    assert rc == 0
    assert out == "test"


def test_async_gather():
    """asyncio.gather runs multiple coroutines"""
    out, err, rc = clython_run(
        "import asyncio\n"
        "async def double(x): return x * 2\n"
        "async def main():\n"
        "    results = await asyncio.gather(double(1), double(2), double(3))\n"
        "    print(results)\n"
        "asyncio.run(main())"
    )
    assert rc == 0
    assert out == "[2, 4, 6]"


def test_async_def_name_attribute():
    """async def function has __name__"""
    out, err, rc = clython_run(
        "async def my_async_func(): pass\n"
        "print(my_async_func.__name__)"
    )
    assert rc == 0
    assert out == "my_async_func"


def test_async_conditional_return():
    """async def with conditional return"""
    out, err, rc = clython_run(
        "import asyncio\n"
        "async def classify(x):\n"
        "    if x > 0: return 'positive'\n"
        "    elif x < 0: return 'negative'\n"
        "    else: return 'zero'\n"
        "print(asyncio.run(classify(5)))\n"
        "print(asyncio.run(classify(-3)))\n"
        "print(asyncio.run(classify(0)))"
    )
    assert rc == 0
    assert out == "positive\nnegative\nzero"


def test_async_def_with_positional_only():
    """async def with positional-only parameter"""
    out, err, rc = clython_run(
        "import asyncio\n"
        "async def f(x, /, y): return x + y\n"
        "print(asyncio.run(f(1, 2)))"
    )
    assert rc == 0
    assert out == "3"


def test_async_sleep_and_continue():
    """async def with multiple awaits"""
    out, err, rc = clython_run(
        "import asyncio\n"
        "async def pipeline(x):\n"
        "    await asyncio.sleep(0)\n"
        "    x = x + 1\n"
        "    await asyncio.sleep(0)\n"
        "    return x * 2\n"
        "print(asyncio.run(pipeline(4)))"
    )
    assert rc == 0
    assert out == "10"


def test_async_multiple_decorators():
    """Multiple decorators on async function"""
    out, err, rc = clython_run(
        "import asyncio\n"
        "def d1(f):\n"
        "    async def w(*a, **k): return (await f(*a,**k)) + 1\n"
        "    return w\n"
        "def d2(f):\n"
        "    async def w(*a, **k): return (await f(*a,**k)) * 2\n"
        "    return w\n"
        "@d1\n@d2\n"
        "async def get_val(): return 5\n"
        "print(asyncio.run(get_val()))"
    )
    assert rc == 0
    # d2 applied first (inner): 5*2=10, then d1 (outer): 10+1=11
    assert out == "11"
