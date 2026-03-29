"""
Clython Runtime Tests: Section 6.14 - Lambdas

Tests lambda expression execution via the Clython binary.
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


def test_simple_lambda_no_args():
    out, err, rc = clython_run("f = lambda: 42; print(f())")
    assert rc == 0
    assert out == "42"


def test_simple_lambda_single_arg():
    out, err, rc = clython_run("square = lambda x: x * x; print(square(5))")
    assert rc == 0
    assert out == "25"


def test_simple_lambda_two_args():
    out, err, rc = clython_run("add = lambda x, y: x + y; print(add(3, 4))")
    assert rc == 0
    assert out == "7"


def test_lambda_default_param():
    out, err, rc = clython_run("f = lambda x, y=10: x + y; print(f(5)); print(f(5, 2))")
    assert rc == 0
    assert out == "15\n7"


def test_lambda_with_multiple_defaults():
    out, err, rc = clython_run("f = lambda a=1, b=2, c=3: a + b + c; print(f()); print(f(10))")
    assert rc == 0
    assert out == "6\n15"


def test_lambda_varargs():
    out, err, rc = clython_run("f = lambda *args: sum(args); print(f(1, 2, 3, 4))")
    assert rc == 0
    assert out == "10"


def test_lambda_kwargs():
    out, err, rc = clython_run("f = lambda **kw: kw.get('x', 0); print(f(x=99))")
    assert rc == 0
    assert out == "99"


def test_lambda_in_map():
    out, err, rc = clython_run("print(list(map(lambda x: x * 2, [1, 2, 3])))")
    assert rc == 0
    assert out == "[2, 4, 6]"


def test_lambda_in_filter():
    out, err, rc = clython_run("print(list(filter(lambda x: x > 2, [1, 2, 3, 4])))")
    assert rc == 0
    assert out == "[3, 4]"


def test_lambda_in_sorted():
    out, err, rc = clython_run("data = [(2,'b'),(1,'a'),(3,'c')]; print(sorted(data, key=lambda t: t[0]))")
    assert rc == 0
    assert out == "[(1, 'a'), (2, 'b'), (3, 'c')]"


def test_lambda_returning_lambda():
    out, err, rc = clython_run("adder = lambda x: lambda y: x + y; add5 = adder(5); print(add5(3))")
    assert rc == 0
    assert out == "8"


def test_lambda_closure_over_enclosing():
    source = """
def make_multiplier(n):
    return lambda x: x * n
double = make_multiplier(2)
triple = make_multiplier(3)
print(double(4))
print(triple(4))
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "8\n12"


def test_lambda_in_list():
    source = """
ops = [lambda x: x + 1, lambda x: x * 2, lambda x: x ** 2]
print([f(3) for f in ops])
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "[4, 6, 9]"


def test_lambda_in_dict():
    source = """
ops = {'inc': lambda x: x + 1, 'double': lambda x: x * 2}
print(ops['inc'](5))
print(ops['double'](5))
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "6\n10"


def test_lambda_conditional_expression():
    out, err, rc = clython_run("f = lambda x: 'pos' if x > 0 else 'neg' if x < 0 else 'zero'; print(f(1)); print(f(-1)); print(f(0))")
    assert rc == 0
    assert out == "pos\nneg\nzero"


def test_lambda_with_arithmetic():
    out, err, rc = clython_run("f = lambda a, b, c: (a + b) * c; print(f(2, 3, 4))")
    assert rc == 0
    assert out == "20"


def test_lambda_keyword_only_param():
    out, err, rc = clython_run("f = lambda *, x: x * 2; print(f(x=7))")
    assert rc == 0
    assert out == "14"


def test_lambda_immediately_invoked():
    out, err, rc = clython_run("print((lambda x, y: x + y)(10, 20))")
    assert rc == 0
    assert out == "30"


def test_nested_lambda_three_deep():
    source = """
f = lambda a: lambda b: lambda c: a + b + c
print(f(1)(2)(3))
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "6"


def test_lambda_string_operation():
    out, err, rc = clython_run("f = lambda s: s.upper(); print(f('hello'))")
    assert rc == 0
    assert out == "HELLO"


def test_lambda_with_boolean_ops():
    out, err, rc = clython_run("f = lambda x, y: x > 0 and y > 0; print(f(1, 2)); print(f(-1, 2))")
    assert rc == 0
    assert out == "True\nFalse"


def test_lambda_in_reduce():
    source = """
from functools import reduce
total = reduce(lambda acc, x: acc + x, [1, 2, 3, 4, 5], 0)
print(total)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "15"


def test_lambda_capture_loop_variable():
    """Each lambda should capture final loop value unless default is used."""
    source = """
fns = [lambda x, i=i: x + i for i in range(3)]
print([f(0) for f in fns])
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "[0, 1, 2]"


def test_lambda_positional_only_param():
    out, err, rc = clython_run("f = lambda x, y, /: x + y; print(f(3, 4))")
    assert rc == 0
    assert out == "7"
