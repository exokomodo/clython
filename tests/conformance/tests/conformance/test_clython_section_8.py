"""Clython conformance tests — Section 8: Compound Statements.

Tests that the Clython interpreter correctly implements Python 3.12 compound
statements: if, while, for, try/except/finally, with, function defs, class
defs, decorators.
"""
import os
import subprocess
import pytest

CLYTHON_BIN = os.environ.get("CLYTHON_BIN")

def clython_run(source: str, *, timeout: int = 10):
    """Run source through Clython, return (stdout, stderr, returncode)."""
    result = subprocess.run(
        [CLYTHON_BIN, "-c", source],
        capture_output=True, text=True, timeout=timeout
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode

pytestmark = pytest.mark.skipif(
    not CLYTHON_BIN, reason="CLYTHON_BIN not set — skipping Clython-specific tests"
)


# ── 8.1 If Statements ─────────────────────────────────────────────────────

class TestSection81IfStatements:
    def test_if_true(self):
        out, _, rc = clython_run("if True:\n    print('yes')")
        assert rc == 0 and out == "yes"

    def test_if_false(self):
        out, _, rc = clython_run("if False:\n    print('yes')\nprint('done')")
        assert rc == 0 and out == "done"

    def test_if_else(self):
        out, _, rc = clython_run("if False:\n    print('yes')\nelse:\n    print('no')")
        assert rc == 0 and out == "no"

    def test_if_elif_else(self):
        out, _, rc = clython_run(
            "x = 5\nif x > 10:\n    print('big')\nelif x > 3:\n    print('medium')\nelse:\n    print('small')"
        )
        assert rc == 0 and out == "medium"

    def test_multiple_elif(self):
        out, _, rc = clython_run(
            "x = 3\nif x == 1:\n    print('one')\nelif x == 2:\n    print('two')\nelif x == 3:\n    print('three')\nelse:\n    print('other')"
        )
        assert rc == 0 and out == "three"

    def test_nested_if(self):
        out, _, rc = clython_run(
            "x = 5\nif x > 0:\n    if x > 3:\n        print('big positive')\n    else:\n        print('small positive')"
        )
        assert rc == 0 and out == "big positive"

    def test_truthiness_empty_list(self):
        out, _, rc = clython_run("if []:\n    print('truthy')\nelse:\n    print('falsy')")
        assert rc == 0 and out == "falsy"

    def test_truthiness_nonempty_list(self):
        out, _, rc = clython_run("if [1]:\n    print('truthy')\nelse:\n    print('falsy')")
        assert rc == 0 and out == "truthy"

    def test_truthiness_zero(self):
        out, _, rc = clython_run("if 0:\n    print('truthy')\nelse:\n    print('falsy')")
        assert rc == 0 and out == "falsy"

    def test_truthiness_empty_string(self):
        out, _, rc = clython_run("if '':\n    print('truthy')\nelse:\n    print('falsy')")
        assert rc == 0 and out == "falsy"


# ── 8.2 While Statements ──────────────────────────────────────────────────

class TestSection82WhileStatements:
    def test_basic_while(self):
        out, _, rc = clython_run("i = 0\nwhile i < 3:\n    print(i)\n    i += 1")
        assert rc == 0 and out == "0\n1\n2"

    def test_while_else(self):
        out, _, rc = clython_run("i = 0\nwhile i < 3:\n    i += 1\nelse:\n    print('done', i)")
        assert rc == 0 and out == "done 3"

    def test_while_break_no_else(self):
        out, _, rc = clython_run(
            "i = 0\nwhile i < 10:\n    if i == 3:\n        break\n    i += 1\nelse:\n    print('no break')\nprint(i)"
        )
        assert rc == 0 and out == "3"

    def test_while_false(self):
        out, _, rc = clython_run("while False:\n    print('never')\nprint('done')")
        assert rc == 0 and out == "done"

    def test_while_condition_expression(self):
        out, _, rc = clython_run(
            "items = [3, 2, 1]\nwhile len(items) > 0:\n    items.pop()\nprint('empty:', len(items))"
        )
        assert rc == 0 and out == "empty: 0"


# ── 8.3 For Statements ────────────────────────────────────────────────────

class TestSection83ForStatements:
    def test_for_range(self):
        out, _, rc = clython_run(
            "result = []\nfor i in range(5):\n    result.append(i)\nprint(result)"
        )
        assert rc == 0 and out == "[0, 1, 2, 3, 4]"

    def test_for_list(self):
        out, _, rc = clython_run(
            "total = 0\nfor x in [10, 20, 30]:\n    total += x\nprint(total)"
        )
        assert rc == 0 and out == "60"

    def test_for_string(self):
        out, _, rc = clython_run(
            "result = []\nfor c in 'abc':\n    result.append(c)\nprint(result)"
        )
        assert rc == 0 and out == "['a', 'b', 'c']"

    def test_for_dict(self):
        out, _, rc = clython_run(
            "d = {'a': 1, 'b': 2}\nfor k in d:\n    print(k, d[k])"
        )
        assert rc == 0 and "a 1" in out and "b 2" in out

    def test_for_else(self):
        out, _, rc = clython_run(
            "for i in range(3):\n    pass\nelse:\n    print('completed')"
        )
        assert rc == 0 and out == "completed"

    def test_for_break_skips_else(self):
        out, _, rc = clython_run(
            "for i in range(5):\n    if i == 2:\n        break\nelse:\n    print('no break')\nprint(i)"
        )
        assert rc == 0 and out == "2"

    def test_for_tuple_unpacking(self):
        out, _, rc = clython_run(
            "pairs = [(1, 'a'), (2, 'b')]\nfor num, letter in pairs:\n    print(num, letter)"
        )
        assert rc == 0 and out == "1 a\n2 b"

    def test_nested_for(self):
        out, _, rc = clython_run(
            "result = []\nfor i in range(3):\n    for j in range(3):\n        if i == j:\n            result.append(i)\nprint(result)"
        )
        assert rc == 0 and out == "[0, 1, 2]"

    def test_for_enumerate(self):
        out, _, rc = clython_run(
            "for i, v in enumerate(['a', 'b', 'c']):\n    print(i, v)"
        )
        assert rc == 0 and out == "0 a\n1 b\n2 c"


# ── 8.4 Try Statements ────────────────────────────────────────────────────

class TestSection84TryStatements:
    def test_try_except(self):
        out, _, rc = clython_run(
            "try:\n    1/0\nexcept ZeroDivisionError:\n    print('caught')"
        )
        assert rc == 0 and out == "caught"

    def test_try_except_as(self):
        out, _, rc = clython_run(
            "try:\n    raise ValueError('oops')\nexcept ValueError as e:\n    print(e)"
        )
        assert rc == 0 and out == "oops"

    def test_try_multiple_except(self):
        out, _, rc = clython_run(
            "try:\n    d = {}\n    d['x']\nexcept KeyError:\n    print('key')\nexcept Exception:\n    print('other')"
        )
        assert rc == 0 and out == "key"

    def test_try_else(self):
        out, _, rc = clython_run(
            "try:\n    x = 1\nexcept:\n    print('error')\nelse:\n    print('ok')"
        )
        assert rc == 0 and out == "ok"

    def test_try_finally(self):
        out, _, rc = clython_run(
            "try:\n    print('body')\nfinally:\n    print('finally')"
        )
        assert rc == 0 and out == "body\nfinally"

    def test_try_except_finally(self):
        out, _, rc = clython_run(
            "try:\n    1/0\nexcept ZeroDivisionError:\n    print('caught')\nfinally:\n    print('finally')"
        )
        assert rc == 0 and out == "caught\nfinally"

    def test_nested_try(self):
        out, _, rc = clython_run(
            "try:\n    try:\n        raise ValueError('inner')\n    except ValueError:\n        print('inner caught')\n        raise KeyError('outer')\nexcept KeyError:\n    print('outer caught')"
        )
        assert rc == 0 and out == "inner caught\nouter caught"

    def test_exception_hierarchy_catch(self):
        out, _, rc = clython_run(
            "try:\n    raise ValueError('v')\nexcept Exception as e:\n    print('caught by parent')"
        )
        assert rc == 0 and out == "caught by parent"


# ── 8.6 Function Definitions ──────────────────────────────────────────────

class TestSection86FunctionDefinitions:
    def test_basic_function(self):
        out, _, rc = clython_run("def add(a, b):\n    return a + b\nprint(add(2, 3))")
        assert rc == 0 and out == "5"

    def test_default_args(self):
        out, _, rc = clython_run("def f(x, y=10):\n    return x + y\nprint(f(5))")
        assert rc == 0 and out == "15"

    def test_kwargs(self):
        out, _, rc = clython_run("def f(a, b):\n    return a - b\nprint(f(b=3, a=10))")
        assert rc == 0 and out == "7"

    def test_varargs(self):
        out, _, rc = clython_run("def f(*args):\n    return len(args)\nprint(f(1, 2, 3))")
        assert rc == 0 and out == "3"

    def test_kwargs_dict(self):
        out, _, rc = clython_run("def f(**kwargs):\n    return len(kwargs)\nprint(f(a=1, b=2))")
        assert rc == 0 and out == "2"

    def test_recursive_function(self):
        out, _, rc = clython_run(
            "def fib(n):\n    if n <= 1:\n        return n\n    return fib(n-1) + fib(n-2)\nprint(fib(10))"
        )
        assert rc == 0 and out == "55"

    def test_closure(self):
        out, _, rc = clython_run(
            "def make_adder(n):\n    def adder(x):\n        return x + n\n    return adder\nadd5 = make_adder(5)\nprint(add5(3))"
        )
        assert rc == 0 and out == "8"

    def test_nested_function(self):
        out, _, rc = clython_run(
            "def outer():\n    def inner(x):\n        return x * 2\n    return inner(5)\nprint(outer())"
        )
        assert rc == 0 and out == "10"

    def test_first_class_function(self):
        out, _, rc = clython_run(
            "def double(x):\n    return x * 2\ndef apply(f, v):\n    return f(v)\nprint(apply(double, 7))"
        )
        assert rc == 0 and out == "14"

    def test_return_multiple(self):
        out, _, rc = clython_run(
            "def f():\n    return 1, 2, 3\na, b, c = f()\nprint(a, b, c)"
        )
        assert rc == 0 and out == "1 2 3"


# ── 8.7 Class Definitions ─────────────────────────────────────────────────

class TestSection87ClassDefinitions:
    def test_empty_class(self):
        out, _, rc = clython_run("class C:\n    pass\nprint(type(C).__name__)")
        assert rc == 0

    def test_class_with_init(self):
        out, _, rc = clython_run(
            "class Dog:\n    def __init__(self, name):\n        self.name = name\nd = Dog('Rex')\nprint(d.name)"
        )
        assert rc == 0 and out == "Rex"

    def test_class_method(self):
        out, _, rc = clython_run(
            "class Counter:\n    def __init__(self):\n        self.n = 0\n    def inc(self):\n        self.n += 1\n        return self.n\nc = Counter()\nprint(c.inc(), c.inc(), c.inc())"
        )
        assert rc == 0 and out == "1 2 3"

    def test_class_attribute(self):
        out, _, rc = clython_run(
            "class C:\n    x = 42\nprint(C.x)"
        )
        assert rc == 0 and out == "42"

    def test_class_str(self):
        out, _, rc = clython_run(
            "class Point:\n    def __init__(self, x, y):\n        self.x = x\n        self.y = y\n    def __str__(self):\n        return '(' + str(self.x) + ', ' + str(self.y) + ')'\np = Point(3, 4)\nprint(p)"
        )
        assert rc == 0 and out == "(3, 4)"

    def test_class_repr(self):
        out, _, rc = clython_run(
            "class C:\n    def __repr__(self):\n        return 'C()'\nc = C()\nprint(repr(c))"
        )
        assert rc == 0 and out == "C()"


# ── 8.9 Decorators ────────────────────────────────────────────────────────

class TestSection89Decorators:
    def test_simple_decorator(self):
        out, _, rc = clython_run(
            "def deco(f):\n    def wrapper():\n        print('before')\n        f()\n        print('after')\n    return wrapper\n@deco\ndef greet():\n    print('hello')\ngreet()"
        )
        assert rc == 0 and out == "before\nhello\nafter"

    def test_decorator_with_args(self):
        out, _, rc = clython_run(
            "def repeat(n):\n    def deco(f):\n        def wrapper():\n            for i in range(n):\n                f()\n        return wrapper\n    return deco\n@repeat(3)\ndef hi():\n    print('hi')\nhi()"
        )
        assert rc == 0 and out == "hi\nhi\nhi"


# ── Comprehensions (8.x related) ──────────────────────────────────────────

class TestSection8Comprehensions:
    def test_list_comprehension(self):
        out, _, rc = clython_run("print([x*2 for x in range(5)])")
        assert rc == 0 and out == "[0, 2, 4, 6, 8]"

    def test_list_comp_with_filter(self):
        out, _, rc = clython_run("print([x for x in range(10) if x % 2 == 0])")
        assert rc == 0 and out == "[0, 2, 4, 6, 8]"

    def test_dict_comprehension(self):
        out, _, rc = clython_run("d = {k: v for k, v in [('a', 1), ('b', 2)]}\nprint(d['a'], d['b'])")
        assert rc == 0 and out == "1 2"

    def test_set_comprehension(self):
        out, _, rc = clython_run("print(len({x % 3 for x in range(10)}))")
        assert rc == 0 and out == "3"

    def test_nested_comprehension(self):
        out, _, rc = clython_run("print([i*j for i in range(1,4) for j in range(1,4)])")
        assert rc == 0 and out == "[1, 2, 3, 2, 4, 6, 3, 6, 9]"
