"""
Section 8.6: Function Definitions - Clython Runtime Test Suite

Tests that Clython actually executes function definitions correctly at runtime.
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


def test_basic_function_definition():
    """Basic def runs and returns value"""
    out, err, rc = clython_run("def f(): return 42\nprint(f())")
    assert rc == 0
    assert out == "42"


def test_function_with_positional_args():
    """Function with positional parameters"""
    out, err, rc = clython_run("def add(x, y): return x + y\nprint(add(3, 4))")
    assert rc == 0
    assert out == "7"


def test_function_with_default_parameter():
    """Function with default parameter value"""
    out, err, rc = clython_run("def greet(name='World'): return 'Hello ' + name\nprint(greet())\nprint(greet('Clython'))")
    assert rc == 0
    assert out == "Hello World\nHello Clython"


def test_function_with_multiple_defaults():
    """Function with multiple default parameters"""
    out, err, rc = clython_run(
        "def func(x=1, y=2, z=3): return x + y + z\n"
        "print(func())\nprint(func(10))\nprint(func(10, 20, 30))"
    )
    assert rc == 0
    assert out == "6\n15\n60"


def test_function_varargs():
    """Function with *args"""
    out, err, rc = clython_run("def f(*args): return sum(args)\nprint(f(1, 2, 3, 4))")
    assert rc == 0
    assert out == "10"


def test_function_kwargs():
    """Function with **kwargs"""
    out, err, rc = clython_run(
        "def f(**kwargs): return sorted(kwargs.keys())\n"
        "print(f(a=1, b=2, c=3))"
    )
    assert rc == 0
    assert out == "['a', 'b', 'c']"


def test_function_args_and_kwargs():
    """Function with *args and **kwargs"""
    out, err, rc = clython_run(
        "def f(*args, **kwargs): return len(args), len(kwargs)\n"
        "print(f(1, 2, 3, a=4, b=5))"
    )
    assert rc == 0
    assert out == "(3, 2)"


def test_keyword_only_parameter():
    """Function with keyword-only parameter after *"""
    out, err, rc = clython_run(
        "def f(a, *, b): return a + b\n"
        "print(f(1, b=2))"
    )
    assert rc == 0
    assert out == "3"


def test_positional_only_parameter():
    """Function with positional-only parameter (/)"""
    out, err, rc = clython_run(
        "def f(x, /, y): return x + y\n"
        "print(f(1, 2))\nprint(f(1, y=2))"
    )
    assert rc == 0
    assert out == "3\n3"


def test_function_type_annotations():
    """Function with type annotations executes correctly"""
    out, err, rc = clython_run(
        "def add(x: int, y: int) -> int: return x + y\n"
        "print(add(5, 6))"
    )
    assert rc == 0
    assert out == "11"


def test_nested_function():
    """Nested function definition (closure)"""
    out, err, rc = clython_run(
        "def make_adder(n):\n"
        "    def add(x): return x + n\n"
        "    return add\n"
        "add5 = make_adder(5)\n"
        "print(add5(10))"
    )
    assert rc == 0
    assert out == "15"


def test_recursive_function():
    """Recursive function (factorial)"""
    out, err, rc = clython_run(
        "def factorial(n):\n"
        "    if n <= 1: return 1\n"
        "    return n * factorial(n - 1)\n"
        "print(factorial(5))"
    )
    assert rc == 0
    assert out == "120"


def test_function_returns_none():
    """Function without return returns None"""
    out, err, rc = clython_run(
        "def f(): pass\n"
        "result = f()\n"
        "print(result is None)"
    )
    assert rc == 0
    assert out == "True"


def test_function_bare_return():
    """Function with bare return returns None"""
    out, err, rc = clython_run(
        "def f():\n"
        "    return\n"
        "print(f() is None)"
    )
    assert rc == 0
    assert out == "True"


def test_function_docstring():
    """Function with docstring has __doc__ attribute"""
    out, err, rc = clython_run(
        'def f():\n'
        '    """My docstring"""\n'
        '    pass\n'
        'print(f.__doc__)'
    )
    assert rc == 0
    assert "My docstring" in out


def test_function_with_decorator():
    """Function with decorator"""
    out, err, rc = clython_run(
        "def deco(fn):\n"
        "    def wrapper(*a, **k): return fn(*a, **k) * 2\n"
        "    return wrapper\n"
        "@deco\n"
        "def get_val(): return 21\n"
        "print(get_val())"
    )
    assert rc == 0
    assert out == "42"


def test_function_multiple_decorators():
    """Function with multiple decorators applied bottom-up"""
    out, err, rc = clython_run(
        "def d1(f):\n"
        "    def w(*a,**k): return 'd1(' + f(*a,**k) + ')'\n"
        "    return w\n"
        "def d2(f):\n"
        "    def w(*a,**k): return 'd2(' + f(*a,**k) + ')'\n"
        "    return w\n"
        "@d1\n@d2\n"
        "def hello(): return 'hello'\n"
        "print(hello())"
    )
    assert rc == 0
    assert out == "d1(d2(hello))"


def test_function_mixed_params():
    """Function with mix of all parameter kinds"""
    out, err, rc = clython_run(
        "def f(a, b=2, *args, c, d=10, **kwargs):\n"
        "    return a + b + sum(args) + c + d + sum(kwargs.values())\n"
        "print(f(1, c=3))"
    )
    assert rc == 0
    assert out == "16"


def test_function_large_param_count():
    """Function with many parameters"""
    params = ", ".join(f"p{i}=0" for i in range(20))
    out, err, rc = clython_run(
        f"def f({params}): return p0 + p1\n"
        "print(f(10, 20))"
    )
    assert rc == 0
    assert out == "30"


def test_function_as_first_class_object():
    """Functions are first-class objects"""
    out, err, rc = clython_run(
        "def add(a, b): return a + b\n"
        "op = add\n"
        "print(op(3, 7))"
    )
    assert rc == 0
    assert out == "10"


def test_function_in_list():
    """Functions can be stored in lists and called"""
    out, err, rc = clython_run(
        "def double(x): return x * 2\n"
        "def triple(x): return x * 3\n"
        "ops = [double, triple]\n"
        "print([f(5) for f in ops])"
    )
    assert rc == 0
    assert out == "[10, 15]"


def test_function_name_attribute():
    """Function has __name__ attribute"""
    out, err, rc = clython_run(
        "def my_function(): pass\n"
        "print(my_function.__name__)"
    )
    assert rc == 0
    assert out == "my_function"


def test_function_deep_nesting():
    """Deeply nested functions"""
    out, err, rc = clython_run(
        "def a():\n"
        "    def b():\n"
        "        def c():\n"
        "            return 99\n"
        "        return c()\n"
        "    return b()\n"
        "print(a())"
    )
    assert rc == 0
    assert out == "99"


def test_function_nonlocal():
    """Nonlocal variable in nested function"""
    out, err, rc = clython_run(
        "def make_counter():\n"
        "    count = 0\n"
        "    def inc():\n"
        "        nonlocal count\n"
        "        count += 1\n"
        "        return count\n"
        "    return inc\n"
        "c = make_counter()\n"
        "print(c(), c(), c())"
    )
    assert rc == 0
    assert out == "1 2 3"
