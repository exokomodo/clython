"""
Section 8.9: Decorators - Clython Runtime Test Suite

Tests that Clython actually executes decorator syntax and semantics correctly at runtime.
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


def test_simple_function_decorator():
    """Simple decorator wraps function"""
    out, err, rc = clython_run(
        "def log(fn):\n"
        "    def wrapper(*a, **k):\n"
        "        result = fn(*a, **k)\n"
        "        return result\n"
        "    return wrapper\n"
        "@log\n"
        "def add(x, y): return x + y\n"
        "print(add(2, 3))"
    )
    assert rc == 0
    assert out == "5"


def test_decorator_modifies_return():
    """Decorator can modify return value"""
    out, err, rc = clython_run(
        "def double_return(fn):\n"
        "    def wrapper(*a, **k): return fn(*a, **k) * 2\n"
        "    return wrapper\n"
        "@double_return\n"
        "def get_five(): return 5\n"
        "print(get_five())"
    )
    assert rc == 0
    assert out == "10"


def test_decorator_with_arguments():
    """Decorator factory with arguments"""
    out, err, rc = clython_run(
        "def multiply(n):\n"
        "    def decorator(fn):\n"
        "        def wrapper(*a, **k): return fn(*a, **k) * n\n"
        "        return wrapper\n"
        "    return decorator\n"
        "@multiply(3)\n"
        "def get_four(): return 4\n"
        "print(get_four())"
    )
    assert rc == 0
    assert out == "12"


def test_multiple_decorators_order():
    """Multiple decorators applied bottom-up"""
    out, err, rc = clython_run(
        "def d1(fn):\n"
        "    def w(*a,**k): return 'd1(' + fn(*a,**k) + ')'\n"
        "    return w\n"
        "def d2(fn):\n"
        "    def w(*a,**k): return 'd2(' + fn(*a,**k) + ')'\n"
        "    return w\n"
        "def d3(fn):\n"
        "    def w(*a,**k): return 'd3(' + fn(*a,**k) + ')'\n"
        "    return w\n"
        "@d1\n@d2\n@d3\n"
        "def fn(): return 'x'\n"
        "print(fn())"
    )
    assert rc == 0
    # d3 first (closest to def), then d2, then d1 (outermost)
    assert out == "d1(d2(d3(x)))"


def test_staticmethod_decorator():
    """@staticmethod decorator works"""
    out, err, rc = clython_run(
        "class Math:\n"
        "    @staticmethod\n"
        "    def square(x): return x * x\n"
        "print(Math.square(7))"
    )
    assert rc == 0
    assert out == "49"


def test_classmethod_decorator():
    """@classmethod decorator works"""
    out, err, rc = clython_run(
        "class Counter:\n"
        "    count = 0\n"
        "    @classmethod\n"
        "    def increment(cls): cls.count += 1\n"
        "    @classmethod\n"
        "    def get_count(cls): return cls.count\n"
        "Counter.increment()\n"
        "Counter.increment()\n"
        "print(Counter.get_count())"
    )
    assert rc == 0
    assert out == "2"


def test_property_decorator():
    """@property decorator works"""
    out, err, rc = clython_run(
        "class Circle:\n"
        "    def __init__(self, r): self._r = r\n"
        "    @property\n"
        "    def area(self): return 3.14 * self._r ** 2\n"
        "c = Circle(10)\n"
        "print(c.area)"
    )
    assert rc == 0
    assert out == "314.0"


def test_property_setter_decorator():
    """@x.setter decorator works"""
    out, err, rc = clython_run(
        "class Temperature:\n"
        "    def __init__(self): self._c = 0\n"
        "    @property\n"
        "    def celsius(self): return self._c\n"
        "    @celsius.setter\n"
        "    def celsius(self, val): self._c = val\n"
        "t = Temperature()\n"
        "t.celsius = 100\n"
        "print(t.celsius)"
    )
    assert rc == 0
    assert out == "100"


def test_class_decorator():
    """Decorator on class definition"""
    out, err, rc = clython_run(
        "def add_repr(cls):\n"
        "    cls.__repr__ = lambda self: f'{cls.__name__}()'\n"
        "    return cls\n"
        "@add_repr\n"
        "class Foo: pass\n"
        "print(repr(Foo()))"
    )
    assert rc == 0
    assert out == "Foo()"


def test_class_multiple_decorators():
    """Multiple decorators on class"""
    out, err, rc = clython_run(
        "def tag_a(cls):\n"
        "    cls.tag_a = True\n"
        "    return cls\n"
        "def tag_b(cls):\n"
        "    cls.tag_b = True\n"
        "    return cls\n"
        "@tag_a\n@tag_b\n"
        "class Tagged: pass\n"
        "print(Tagged.tag_a, Tagged.tag_b)"
    )
    assert rc == 0
    assert out == "True True"


def test_decorator_dotted_name():
    """Decorator with dotted name (module.attr)"""
    out, err, rc = clython_run(
        "class decorators:\n"
        "    @staticmethod\n"
        "    def noop(fn): return fn\n"
        "@decorators.noop\n"
        "def my_func(): return 'ok'\n"
        "print(my_func())"
    )
    assert rc == 0
    assert out == "ok"


def test_decorator_preserves_callable():
    """Decorated function is still callable"""
    out, err, rc = clython_run(
        "def identity(fn): return fn\n"
        "@identity\n"
        "def greet(): return 'hi'\n"
        "print(callable(greet))\n"
        "print(greet())"
    )
    assert rc == 0
    assert out == "True\nhi"


@pytest.mark.xfail(reason="**kwargs not passed through *args/**kwargs spread in Clython")
def test_decorator_with_args_and_kwargs():
    """Decorator that passes args and kwargs through"""
    out, err, rc = clython_run(
        "def passthrough(fn):\n"
        "    def wrapper(*args, **kwargs): return fn(*args, **kwargs)\n"
        "    return wrapper\n"
        "@passthrough\n"
        "def add(a, b=0): return a + b\n"
        "print(add(3))\n"
        "print(add(3, b=7))"
    )
    assert rc == 0
    assert out == "3\n10"


def test_decorator_stacking_four():
    """Four decorators stacked"""
    out, err, rc = clython_run(
        "def add1(fn):\n"
        "    def w(*a,**k): return fn(*a,**k) + 1\n"
        "    return w\n"
        "@add1\n@add1\n@add1\n@add1\n"
        "def zero(): return 0\n"
        "print(zero())"
    )
    assert rc == 0
    assert out == "4"


def test_decorator_on_async_function():
    """Decorator works on async function"""
    out, err, rc = clython_run(
        "import asyncio\n"
        "def deco(fn):\n"
        "    async def wrapper(*a, **k): return await fn(*a, **k)\n"
        "    return wrapper\n"
        "@deco\n"
        "async def main(): return 77\n"
        "print(asyncio.run(main()))"
    )
    assert rc == 0
    assert out == "77"


def test_class_decorator_with_args():
    """Class decorator with arguments"""
    out, err, rc = clython_run(
        "def version(v):\n"
        "    def deco(cls):\n"
        "        cls._version = v\n"
        "        return cls\n"
        "    return deco\n"
        "@version(2)\n"
        "class MyApi: pass\n"
        "print(MyApi._version)"
    )
    assert rc == 0
    assert out == "2"


def test_decorator_in_class():
    """Decorated methods in class"""
    out, err, rc = clython_run(
        "class MyClass:\n"
        "    @staticmethod\n"
        "    def static_add(a, b): return a + b\n"
        "    @classmethod\n"
        "    def class_name(cls): return cls.__name__\n"
        "    @property\n"
        "    def value(self): return 42\n"
        "obj = MyClass()\n"
        "print(MyClass.static_add(2, 3))\n"
        "print(MyClass.class_name())\n"
        "print(obj.value)"
    )
    assert rc == 0
    assert out == "5\nMyClass\n42"


def test_decorator_evaluation_is_call():
    """Decorator with () is called at definition time"""
    out, err, rc = clython_run(
        "call_log = []\n"
        "def make_deco():\n"
        "    call_log.append('made')\n"
        "    def deco(fn): return fn\n"
        "    return deco\n"
        "@make_deco()\n"
        "def my_func(): pass\n"
        "print(call_log)"
    )
    assert rc == 0
    assert out == "['made']"


def test_decorator_replaces_function():
    """Decorator completely replaces function"""
    out, err, rc = clython_run(
        "def replace(fn):\n"
        "    return lambda: 'replaced'\n"
        "@replace\n"
        "def original(): return 'original'\n"
        "print(original())"
    )
    assert rc == 0
    assert out == "replaced"


def test_multiple_decorators_with_args():
    """Multiple parametrized decorators"""
    out, err, rc = clython_run(
        "def prepend(s):\n"
        "    def deco(fn):\n"
        "        def w(*a,**k): return s + fn(*a,**k)\n"
        "        return w\n"
        "    return deco\n"
        "@prepend('C:')\n"
        "@prepend('B:')\n"
        "@prepend('A:')\n"
        "def base(): return 'X'\n"
        "print(base())"
    )
    assert rc == 0
    # A: applied first (inner), then B:, then C: (outer)
    assert out == "C:B:A:X"
