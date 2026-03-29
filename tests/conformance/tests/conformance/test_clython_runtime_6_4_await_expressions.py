"""
Clython runtime conformance tests for Section 6.4: Await Expressions.

These tests run code through the Clython binary and verify output/behavior.
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


def test_simple_async_function_runs():
    """Basic async function with asyncio.run executes."""
    source = """\
import asyncio

async def main():
    return 42

print(asyncio.run(main()))
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "42"


def test_await_coroutine_result():
    """Await returns value from coroutine."""
    source = """\
import asyncio

async def get_value():
    return 99

async def main():
    result = await get_value()
    print(result)

asyncio.run(main())
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "99"


def test_await_multiple_sequential():
    """Multiple sequential awaits work correctly."""
    source = """\
import asyncio

async def get_a():
    return 1

async def get_b():
    return 2

async def main():
    a = await get_a()
    b = await get_b()
    print(a + b)

asyncio.run(main())
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "3"


def test_await_in_if_condition():
    """Await expression works in if condition."""
    source = """\
import asyncio

async def check():
    return True

async def main():
    if await check():
        print("yes")
    else:
        print("no")

asyncio.run(main())
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "yes"


def test_await_in_return():
    """Await expression works in return statement."""
    source = """\
import asyncio

async def compute():
    return 7

async def double():
    return await compute() * 2

async def main():
    print(await double())

asyncio.run(main())
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "14"


def test_await_in_while_loop():
    """Await works inside a while loop."""
    source = """\
import asyncio

counter = 0

async def check_limit():
    global counter
    counter += 1
    return counter < 4

async def main():
    while await check_limit():
        pass
    print(counter)

asyncio.run(main())
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "4"


def test_await_in_function_call_arg():
    """Await expression used as function argument."""
    source = """\
import asyncio

async def get_val():
    return 5

async def main():
    print(str(await get_val()))

asyncio.run(main())
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "5"


def test_await_asyncio_sleep():
    """await asyncio.sleep(0) works (yields control)."""
    source = """\
import asyncio

async def main():
    await asyncio.sleep(0)
    print("after sleep")

asyncio.run(main())
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "after sleep"


def test_await_gather_multiple():
    """asyncio.gather with multiple coroutines."""
    source = """\
import asyncio

async def get_n(n):
    return n

async def main():
    a, b, c = await asyncio.gather(get_n(1), get_n(2), get_n(3))
    print(a, b, c)

asyncio.run(main())
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "1 2 3"


def test_await_nested_coroutines():
    """Nested awaits work correctly."""
    source = """\
import asyncio

async def inner():
    return 10

async def outer():
    return await inner() + 5

async def main():
    print(await outer())

asyncio.run(main())
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "15"


def test_await_with_exception_handling():
    """Await works inside try/except."""
    source = """\
import asyncio

async def might_fail(should_fail):
    if should_fail:
        raise ValueError("oops")
    return "ok"

async def main():
    try:
        result = await might_fail(False)
        print(result)
    except ValueError:
        print("caught")

asyncio.run(main())
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "ok"


def test_await_catches_exception():
    """Exceptions from awaited coroutines are catchable."""
    source = """\
import asyncio

async def fail():
    raise RuntimeError("boom")

async def main():
    try:
        await fail()
    except RuntimeError as e:
        print(str(e))

asyncio.run(main())
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "boom"


def test_await_conditional_expression():
    """Await in conditional (ternary) expression."""
    source = """\
import asyncio

async def get_a():
    return "a"

async def get_b():
    return "b"

async def main():
    flag = True
    result = await get_a() if flag else await get_b()
    print(result)

asyncio.run(main())
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "a"


def test_await_result_used_in_arithmetic():
    """Await result can be used in arithmetic."""
    source = """\
import asyncio

async def get_num():
    return 6

async def main():
    x = await get_num()
    print(x * x)

asyncio.run(main())
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "36"


@pytest.mark.xfail(reason="inspect.iscoroutinefunction not fully supported in Clython")
def test_async_function_type():
    """Async function object is a coroutine function."""
    source = """\
import asyncio
import inspect

async def my_coro():
    return 1

print(inspect.iscoroutinefunction(my_coro))
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True"


@pytest.mark.xfail(reason="asyncio.create_task not yet supported in Clython")
def test_await_asyncio_create_task():
    """asyncio.create_task with await works."""
    source = """\
import asyncio

async def worker():
    return "done"

async def main():
    task = asyncio.create_task(worker())
    result = await task
    print(result)

asyncio.run(main())
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "done"


def test_await_outside_async_is_error():
    """Await outside async function is a syntax/runtime error."""
    source = """\
def regular():
    return await something()

regular()
"""
    _, _, rc = clython_run(source)
    assert rc != 0


def test_async_for_loop():
    """async for loop works with async iterator."""
    source = """\
import asyncio

class AsyncRange:
    def __init__(self, n):
        self.n = n
        self.i = 0
    def __aiter__(self):
        return self
    async def __anext__(self):
        if self.i >= self.n:
            raise StopAsyncIteration
        val = self.i
        self.i += 1
        return val

async def main():
    total = 0
    async for x in AsyncRange(5):
        total += x
    print(total)

asyncio.run(main())
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "10"


def test_async_with_context_manager():
    """async with works with async context manager."""
    source = """\
import asyncio

class AsyncCtx:
    async def __aenter__(self):
        return self
    async def __aexit__(self, *args):
        pass

async def main():
    async with AsyncCtx() as ctx:
        print("inside")

asyncio.run(main())
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "inside"


def test_await_assignment_augmented():
    """Await result used in augmented assignment."""
    source = """\
import asyncio

async def get_delta():
    return 5

async def main():
    total = 10
    total += await get_delta()
    print(total)

asyncio.run(main())
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "15"
