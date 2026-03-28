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


# ── 8.9 Decorators ────────────────────────────────────────────────────────

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


# ── 8.1 If Statements (extended) ──────────────────────────────────────────

class TestSection81IfStatementsExtended:
    """Additional if statement tests from AST conformance suite."""

    def test_chained_comparison_in_if(self):
        out, _, rc = clython_run("x = 5\nif 0 < x < 10:\n    print('in range')\nelse:\n    print('out')")
        assert rc == 0 and out == "in range"

    def test_chained_comparison_fail(self):
        out, _, rc = clython_run("x = 15\nif 0 < x < 10:\n    print('in range')\nelse:\n    print('out')")
        assert rc == 0 and out == "out"

    def test_is_none_check(self):
        out, _, rc = clython_run("x = None\nif x is None:\n    print('none')\nelse:\n    print('not none')")
        assert rc == 0 and out == "none"

    def test_is_not_none_check(self):
        out, _, rc = clython_run("x = 42\nif x is not None:\n    print('has value')\nelse:\n    print('none')")
        assert rc == 0 and out == "has value"

    def test_in_membership(self):
        out, _, rc = clython_run("if 3 in [1, 2, 3, 4]:\n    print('found')\nelse:\n    print('missing')")
        assert rc == 0 and out == "found"

    def test_not_in_membership(self):
        out, _, rc = clython_run("if 5 not in [1, 2, 3]:\n    print('missing')\nelse:\n    print('found')")
        assert rc == 0 and out == "missing"

    def test_complex_boolean_and(self):
        out, _, rc = clython_run("x, y = 5, 10\nif x > 0 and y > 0:\n    print('both positive')")
        assert rc == 0 and out == "both positive"

    def test_complex_boolean_or(self):
        out, _, rc = clython_run("x, y = -1, 10\nif x > 0 or y > 0:\n    print('at least one positive')")
        assert rc == 0 and out == "at least one positive"

    def test_not_condition(self):
        out, _, rc = clython_run("if not False:\n    print('yes')")
        assert rc == 0 and out == "yes"

    def test_double_negation(self):
        out, _, rc = clython_run("if not not True:\n    print('yes')")
        assert rc == 0 and out == "yes"

    def test_truthiness_none(self):
        out, _, rc = clython_run("if None:\n    print('truthy')\nelse:\n    print('falsy')")
        assert rc == 0 and out == "falsy"

    def test_truthiness_empty_dict(self):
        out, _, rc = clython_run("if {}:\n    print('truthy')\nelse:\n    print('falsy')")
        assert rc == 0 and out == "falsy"

    def test_truthiness_nonempty_string(self):
        out, _, rc = clython_run("if 'hello':\n    print('truthy')\nelse:\n    print('falsy')")
        assert rc == 0 and out == "truthy"

    def test_walrus_operator_in_if(self):
        out, _, rc = clython_run("data = [1, 2, 3]\nif (n := len(data)) > 2:\n    print(n)")
        assert rc == 0 and out == "3"

    def test_multiline_condition(self):
        out, _, rc = clython_run(
            "x = 5\ny = 10\nif (\n    x > 0 and\n    y > 0\n):\n    print('yes')"
        )
        assert rc == 0 and out == "yes"


# ── 8.2 While Statements (extended) ───────────────────────────────────────

class TestSection82WhileStatementsExtended:
    """Additional while statement tests from AST conformance suite."""

    def test_while_with_continue(self):
        out, _, rc = clython_run(
            "result = []\ni = 0\nwhile i < 5:\n    i += 1\n    if i % 2 == 0:\n        continue\n    result.append(i)\nprint(result)"
        )
        assert rc == 0 and out == "[1, 3, 5]"

    def test_while_else_with_continue(self):
        """continue does not skip the else clause"""
        out, _, rc = clython_run(
            "i = 0\nwhile i < 3:\n    i += 1\n    continue\nelse:\n    print('done')"
        )
        assert rc == 0 and out == "done"

    def test_while_nested_break(self):
        """break in inner loop does not affect outer"""
        out, _, rc = clython_run(
            "outer = 0\nwhile outer < 3:\n    inner = 0\n    while inner < 5:\n        if inner == 2:\n            break\n        inner += 1\n    outer += 1\nprint(outer, inner)"
        )
        assert rc == 0 and out == "3 2"

    def test_while_with_function_call_condition(self):
        out, _, rc = clython_run(
            "items = [3, 2, 1]\nwhile len(items) > 1:\n    items.pop()\nprint(items)"
        )
        assert rc == 0 and out == "[3]"

    def test_while_accumulator(self):
        out, _, rc = clython_run(
            "total = 0\ni = 1\nwhile i <= 100:\n    total += i\n    i += 1\nprint(total)"
        )
        assert rc == 0 and out == "5050"


# ── 8.3 For Statements (extended) ─────────────────────────────────────────

class TestSection83ForStatementsExtended:
    """Additional for statement tests from AST conformance suite."""

    def test_for_dict_items(self):
        out, _, rc = clython_run(
            "d = {'x': 1, 'y': 2}\nfor k, v in d.items():\n    print(k, v)"
        )
        assert rc == 0 and "x 1" in out and "y 2" in out

    def test_for_dict_values(self):
        out, _, rc = clython_run(
            "d = {'a': 10, 'b': 20}\ntotal = 0\nfor v in d.values():\n    total += v\nprint(total)"
        )
        assert rc == 0 and out == "30"

    def test_for_with_continue(self):
        out, _, rc = clython_run(
            "result = []\nfor i in range(5):\n    if i == 2:\n        continue\n    result.append(i)\nprint(result)"
        )
        assert rc == 0 and out == "[0, 1, 3, 4]"

    def test_for_continue_does_not_skip_else(self):
        out, _, rc = clython_run(
            "for i in range(3):\n    continue\nelse:\n    print('done')"
        )
        assert rc == 0 and out == "done"

    def test_for_starred_unpacking(self):
        out, _, rc = clython_run(
            "for first, *rest in [(1, 2, 3), (4, 5, 6)]:\n    print(first, rest)"
        )
        assert rc == 0 and out == "1 [2, 3]\n4 [5, 6]"

    def test_for_zip(self):
        out, _, rc = clython_run(
            "for a, b in zip([1, 2, 3], ['a', 'b', 'c']):\n    print(a, b)"
        )
        assert rc == 0 and out == "1 a\n2 b\n3 c"

    def test_for_reversed(self):
        out, _, rc = clython_run(
            "result = []\nfor i in reversed([1, 2, 3]):\n    result.append(i)\nprint(result)"
        )
        assert rc == 0 and out == "[3, 2, 1]"

    def test_for_nested_unpacking(self):
        out, _, rc = clython_run(
            "data = [(1, (2, 3)), (4, (5, 6))]\nfor a, (b, c) in data:\n    print(a, b, c)"
        )
        assert rc == 0 and out == "1 2 3\n4 5 6"

    def test_for_empty_iterable(self):
        out, _, rc = clython_run(
            "count = 0\nfor x in []:\n    count += 1\nprint(count)"
        )
        assert rc == 0 and out == "0"

    def test_for_empty_iterable_else(self):
        out, _, rc = clython_run(
            "for x in []:\n    pass\nelse:\n    print('else ran')"
        )
        assert rc == 0 and out == "else ran"

    def test_for_set_iteration(self):
        out, _, rc = clython_run(
            "result = sorted([x for x in {3, 1, 2}])\nprint(result)"
        )
        assert rc == 0 and out == "[1, 2, 3]"


# ── 8.4 Try Statements (extended) ─────────────────────────────────────────

class TestSection84TryStatementsExtended:
    """Additional try statement tests from AST conformance suite."""

    def test_bare_except(self):
        out, _, rc = clython_run(
            "try:\n    1/0\nexcept:\n    print('caught')"
        )
        assert rc == 0 and out == "caught"

    def test_tuple_exception_types(self):
        out, _, rc = clython_run(
            "try:\n    raise TypeError('t')\nexcept (ValueError, TypeError) as e:\n    print('caught', e)"
        )
        assert rc == 0 and out == "caught t"

    def test_try_else_not_run_on_exception(self):
        out, _, rc = clython_run(
            "try:\n    raise ValueError('v')\nexcept ValueError:\n    print('except')\nelse:\n    print('else')"
        )
        assert rc == 0 and out == "except"

    def test_finally_runs_on_exception(self):
        out, _, rc = clython_run(
            "try:\n    raise ValueError('v')\nexcept ValueError:\n    print('except')\nfinally:\n    print('finally')"
        )
        assert rc == 0 and out == "except\nfinally"

    def test_finally_runs_on_unhandled_exception(self):
        out, _, rc = clython_run(
            "try:\n    try:\n        raise ValueError('v')\n    finally:\n        print('inner finally')\nexcept ValueError:\n    print('outer caught')"
        )
        assert rc == 0 and out == "inner finally\nouter caught"

    def test_reraise(self):
        out, _, rc = clython_run(
            "try:\n    try:\n        raise ValueError('v')\n    except ValueError:\n        print('inner')\n        raise\nexcept ValueError:\n    print('outer')"
        )
        assert rc == 0 and out == "inner\nouter"

    @pytest.mark.xfail(reason="exception chaining (from) may not be implemented")
    def test_exception_chaining_from(self):
        out, _, rc = clython_run(
            "try:\n    try:\n        raise ValueError('original')\n    except ValueError as e:\n        raise TypeError('new') from e\nexcept TypeError as e:\n    print(type(e).__name__)\n    print(type(e.__cause__).__name__)"
        )
        assert rc == 0 and out == "TypeError\nValueError"

    def test_try_except_else_finally_all(self):
        out, _, rc = clython_run(
            "try:\n    x = 1\nexcept:\n    print('except')\nelse:\n    print('else')\nfinally:\n    print('finally')"
        )
        assert rc == 0 and out == "else\nfinally"

    def test_multiple_except_first_match_wins(self):
        out, _, rc = clython_run(
            "try:\n    raise ValueError('v')\nexcept ValueError:\n    print('first')\nexcept Exception:\n    print('second')"
        )
        assert rc == 0 and out == "first"

    def test_exception_in_except_handler(self):
        out, _, rc = clython_run(
            "try:\n    try:\n        raise ValueError('v')\n    except ValueError:\n        raise TypeError('t')\nexcept TypeError:\n    print('caught type error')"
        )
        assert rc == 0 and out == "caught type error"


# ── 8.5 With Statements ───────────────────────────────────────────────────

class TestSection85WithStatements:
    """With statement tests based on AST conformance suite."""

    def test_basic_context_manager(self):
        out, _, rc = clython_run(
            "class CM:\n"
            "    def __enter__(self):\n"
            "        print('enter')\n"
            "        return self\n"
            "    def __exit__(self, *args):\n"
            "        print('exit')\n"
            "with CM():\n"
            "    print('body')"
        )
        assert rc == 0 and out == "enter\nbody\nexit"

    def test_with_as_binding(self):
        out, _, rc = clython_run(
            "class CM:\n"
            "    def __enter__(self):\n"
            "        return 42\n"
            "    def __exit__(self, *args):\n"
            "        pass\n"
            "with CM() as val:\n"
            "    print(val)"
        )
        assert rc == 0 and out == "42"

    def test_with_exit_on_exception(self):
        out, _, rc = clython_run(
            "class CM:\n"
            "    def __enter__(self):\n"
            "        return self\n"
            "    def __exit__(self, exc_type, exc_val, exc_tb):\n"
            "        print('exit', exc_type is not None)\n"
            "        return True\n"
            "with CM():\n"
            "    raise ValueError('oops')\n"
            "print('after')"
        )
        assert rc == 0 and out == "exit True\nafter"

    def test_with_exit_does_not_suppress(self):
        out, _, rc = clython_run(
            "class CM:\n"
            "    def __enter__(self):\n"
            "        return self\n"
            "    def __exit__(self, *args):\n"
            "        print('exit')\n"
            "        return False\n"
            "try:\n"
            "    with CM():\n"
            "        raise ValueError('v')\n"
            "except ValueError:\n"
            "    print('caught')"
        )
        assert rc == 0 and out == "exit\ncaught"

    def test_multiple_context_managers(self):
        out, _, rc = clython_run(
            "class CM:\n"
            "    def __init__(self, name):\n"
            "        self.name = name\n"
            "    def __enter__(self):\n"
            "        print('enter', self.name)\n"
            "        return self\n"
            "    def __exit__(self, *args):\n"
            "        print('exit', self.name)\n"
            "with CM('a'), CM('b'):\n"
            "    print('body')"
        )
        assert rc == 0 and out == "enter a\nenter b\nbody\nexit b\nexit a"

    def test_nested_with_statements(self):
        out, _, rc = clython_run(
            "class CM:\n"
            "    def __init__(self, name):\n"
            "        self.name = name\n"
            "    def __enter__(self):\n"
            "        print('enter', self.name)\n"
            "        return self\n"
            "    def __exit__(self, *args):\n"
            "        print('exit', self.name)\n"
            "with CM('outer'):\n"
            "    with CM('inner'):\n"
            "        print('body')"
        )
        assert rc == 0 and out == "enter outer\nenter inner\nbody\nexit inner\nexit outer"

    def test_with_exit_always_called(self):
        """__exit__ is called even on normal completion"""
        out, _, rc = clython_run(
            "class CM:\n"
            "    def __enter__(self):\n"
            "        return 'value'\n"
            "    def __exit__(self, *args):\n"
            "        print('cleaned up')\n"
            "with CM() as v:\n"
            "    print(v)\n"
            "print('after')"
        )
        assert rc == 0 and out == "value\ncleaned up\nafter"


# ── 8.6 Function Definitions (extended) ───────────────────────────────────

class TestSection86FunctionDefinitionsExtended:
    """Additional function definition tests from AST conformance suite."""

    def test_keyword_only_params(self):
        out, _, rc = clython_run(
            "def f(a, *, key):\n    return a + key\nprint(f(1, key=2))"
        )
        assert rc == 0 and out == "3"

    def test_positional_only_params(self):
        out, _, rc = clython_run(
            "def f(a, b, /):\n    return a + b\nprint(f(1, 2))"
        )
        assert rc == 0 and out == "3"

    def test_mixed_args_and_kwargs(self):
        out, _, rc = clython_run(
            "def f(*args, **kwargs):\n    return len(args) + len(kwargs)\nprint(f(1, 2, a=3, b=4))"
        )
        assert rc == 0 and out == "4"

    @pytest.mark.xfail(reason="function __doc__ attribute not implemented")
    def test_function_docstring(self):
        out, _, rc = clython_run(
            "def f():\n    '''my docstring'''\n    return 42\nprint(f.__doc__)"
        )
        assert rc == 0 and out == "my docstring"

    @pytest.mark.xfail(reason="type annotations on functions may not be fully implemented")
    def test_type_annotations(self):
        out, _, rc = clython_run(
            "def add(a: int, b: int) -> int:\n    return a + b\nprint(add(2, 3))\nprint(add.__annotations__)"
        )
        assert rc == 0 and "5" in out

    def test_lambda_basic(self):
        out, _, rc = clython_run("f = lambda x: x * 2\nprint(f(5))")
        assert rc == 0 and out == "10"

    def test_lambda_multiple_args(self):
        out, _, rc = clython_run("f = lambda x, y: x + y\nprint(f(3, 4))")
        assert rc == 0 and out == "7"

    def test_lambda_default_arg(self):
        out, _, rc = clython_run("f = lambda x, y=10: x + y\nprint(f(5))")
        assert rc == 0 and out == "15"

    def test_generator_function(self):
        out, _, rc = clython_run(
            "def gen(n):\n    for i in range(n):\n        yield i\nprint(list(gen(4)))"
        )
        assert rc == 0 and out == "[0, 1, 2, 3]"

    def test_global_keyword(self):
        out, _, rc = clython_run(
            "x = 0\ndef inc():\n    global x\n    x += 1\ninc()\ninc()\nprint(x)"
        )
        assert rc == 0 and out == "2"

    def test_nonlocal_keyword(self):
        out, _, rc = clython_run(
            "def outer():\n    x = 0\n    def inner():\n        nonlocal x\n        x += 1\n    inner()\n    inner()\n    return x\nprint(outer())"
        )
        assert rc == 0 and out == "2"

    def test_function_as_default_arg_evaluated_once(self):
        out, _, rc = clython_run(
            "def f(x, lst=[]):\n    lst.append(x)\n    return lst\nprint(f(1))\nprint(f(2))"
        )
        assert rc == 0 and out == "[1]\n[1, 2]"


# ── 8.7 Class Definitions (extended) ──────────────────────────────────────

class TestSection87ClassDefinitionsExtended:
    """Additional class definition tests from AST conformance suite."""

    def test_single_inheritance(self):
        out, _, rc = clython_run(
            "class Base:\n"
            "    def greet(self):\n"
            "        return 'hello'\n"
            "class Child(Base):\n"
            "    pass\n"
            "print(Child().greet())"
        )
        assert rc == 0 and out == "hello"

    def test_method_override(self):
        out, _, rc = clython_run(
            "class Base:\n"
            "    def greet(self):\n"
            "        return 'base'\n"
            "class Child(Base):\n"
            "    def greet(self):\n"
            "        return 'child'\n"
            "print(Child().greet())"
        )
        assert rc == 0 and out == "child"

    def test_super_call(self):
        out, _, rc = clython_run(
            "class Base:\n"
            "    def __init__(self, x):\n"
            "        self.x = x\n"
            "class Child(Base):\n"
            "    def __init__(self, x, y):\n"
            "        super().__init__(x)\n"
            "        self.y = y\n"
            "c = Child(1, 2)\nprint(c.x, c.y)"
        )
        assert rc == 0 and out == "1 2"

    def test_multiple_inheritance(self):
        out, _, rc = clython_run(
            "class A:\n"
            "    def who(self):\n"
            "        return 'A'\n"
            "class B:\n"
            "    def what(self):\n"
            "        return 'B'\n"
            "class C(A, B):\n"
            "    pass\n"
            "c = C()\nprint(c.who(), c.what())"
        )
        assert rc == 0 and out == "A B"

    def test_isinstance_check(self):
        out, _, rc = clython_run(
            "class Animal:\n    pass\n"
            "class Dog(Animal):\n    pass\n"
            "d = Dog()\n"
            "print(isinstance(d, Dog), isinstance(d, Animal))"
        )
        assert rc == 0 and out == "True True"

    def test_issubclass_not_correctly_implemented_for_user(self):
        out, _, rc = clython_run(
            "class Base:\n    pass\n"
            "class Child(Base):\n    pass\n"
            "print(issubclass(Child, Base))"
        )
        assert rc == 0 and out == "True"

    def test_static_method(self):
        out, _, rc = clython_run(
            "class C:\n"
            "    @staticmethod\n"
            "    def add(a, b):\n"
            "        return a + b\n"
            "print(C.add(2, 3))"
        )
        assert rc == 0 and out == "5"
    def test_class_method(self):
        out, _, rc = clython_run(
            "class C:\n"
            "    count = 0\n"
            "    @classmethod\n"
            "    def inc(cls):\n"
            "        cls.count += 1\n"
            "        return cls.count\n"
            "print(C.inc(), C.inc())"
        )
        assert rc == 0 and out == "1 2"

    @pytest.mark.xfail(reason="@property may not be implemented")
    def test_property_decorator(self):
        out, _, rc = clython_run(
            "class Circle:\n"
            "    def __init__(self, r):\n"
            "        self._r = r\n"
            "    @property\n"
            "    def area(self):\n"
            "        return 3.14159 * self._r ** 2\n"
            "c = Circle(1)\nprint(round(c.area, 2))"
        )
        assert rc == 0 and out == "3.14"

    def test_dunder_len(self):
        out, _, rc = clython_run(
            "class Bag:\n"
            "    def __init__(self, items):\n"
            "        self.items = items\n"
            "    def __len__(self):\n"
            "        return len(self.items)\n"
            "print(len(Bag([1, 2, 3])))"
        )
        assert rc == 0 and out == "3"

    def test_dunder_getitem(self):
        out, _, rc = clython_run(
            "class MyList:\n"
            "    def __init__(self, data):\n"
            "        self.data = data\n"
            "    def __getitem__(self, idx):\n"
            "        return self.data[idx]\n"
            "m = MyList([10, 20, 30])\nprint(m[1])"
        )
        assert rc == 0 and out == "20"

    @pytest.mark.xfail(reason="class __doc__ attribute not implemented")
    def test_class_docstring(self):
        out, _, rc = clython_run(
            "class C:\n    '''my class doc'''\n    pass\nprint(C.__doc__)"
        )
        assert rc == 0 and out == "my class doc"

    def test_nested_classes(self):
        out, _, rc = clython_run(
            "class Outer:\n"
            "    class Inner:\n"
            "        value = 99\n"
            "print(Outer.Inner.value)"
        )
        assert rc == 0 and out == "99"


# ── 8.9 Decorators (extended) ─────────────────────────────────────────────

class TestSection89DecoratorsExtended:
    """Additional decorator tests from AST conformance suite."""

    def test_stacked_decorators(self):
        """Multiple decorators are applied bottom-up"""
        out, _, rc = clython_run(
            "def d1(f):\n"
            "    def w(*a):\n"
            "        return 'd1(' + f(*a) + ')'\n"
            "    return w\n"
            "def d2(f):\n"
            "    def w(*a):\n"
            "        return 'd2(' + f(*a) + ')'\n"
            "    return w\n"
            "@d1\n@d2\ndef greet():\n    return 'hi'\n"
            "print(greet())"
        )
        assert rc == 0 and out == "d1(d2(hi))"

    def test_class_decorator(self):
        out, _, rc = clython_run(
            "def add_greet(cls):\n"
            "    cls.greet = lambda self: 'hello'\n"
            "    return cls\n"
            "@add_greet\n"
            "class C:\n    pass\n"
            "print(C().greet())"
        )
        assert rc == 0 and out == "hello"

    def test_decorator_preserves_return(self):
        out, _, rc = clython_run(
            "def log(f):\n"
            "    def wrapper(*args):\n"
            "        result = f(*args)\n"
            "        print('called')\n"
            "        return result\n"
            "    return wrapper\n"
            "@log\ndef add(a, b):\n    return a + b\n"
            "print(add(2, 3))"
        )
        assert rc == 0 and out == "called\n5"

    def test_decorator_factory_with_kwargs(self):
        out, _, rc = clython_run(
            "def tag(name):\n"
            "    def deco(f):\n"
            "        def wrapper():\n"
            "            return '<' + name + '>' + f() + '</' + name + '>'\n"
            "        return wrapper\n"
            "    return deco\n"
            "@tag('b')\ndef text():\n    return 'bold'\n"
            "print(text())"
        )
        assert rc == 0 and out == "<b>bold</b>"
