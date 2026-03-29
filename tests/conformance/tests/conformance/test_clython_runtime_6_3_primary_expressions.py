"""
Clython runtime tests for Section 6.3: Primary Expressions.

Executes expressions through the Clython binary and validates stdout/stderr/returncode.
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


# ---------------------------------------------------------------------------
# Attribute references
# ---------------------------------------------------------------------------

def test_attribute_access_builtin():
    """Attribute access on a built-in object."""
    out, err, rc = clython_run("print(type(42).__name__)")
    assert rc == 0
    assert out == "int"


def test_attribute_access_string():
    """Attribute access: str.upper method call."""
    out, err, rc = clython_run("print('hello'.upper())")
    assert rc == 0
    assert out == "HELLO"


def test_attribute_access_list():
    """Attribute access: list.append then print."""
    out, err, rc = clython_run("x = [1, 2]; x.append(3); print(x)")
    assert rc == 0
    assert out == "[1, 2, 3]"


def test_chained_attribute_access():
    """Chained attribute access."""
    out, err, rc = clython_run("print('hello world'.strip().upper())")
    assert rc == 0
    assert out == "HELLO WORLD"


# ---------------------------------------------------------------------------
# Subscriptions (indexing)
# ---------------------------------------------------------------------------

def test_list_subscript_positive():
    """Positive index on list."""
    out, err, rc = clython_run("x = [10, 20, 30]; print(x[1])")
    assert rc == 0
    assert out == "20"


def test_list_subscript_negative():
    """Negative index on list."""
    out, err, rc = clython_run("x = [10, 20, 30]; print(x[-1])")
    assert rc == 0
    assert out == "30"


def test_dict_subscript():
    """Dictionary subscript with string key."""
    out, err, rc = clython_run("d = {'a': 1, 'b': 2}; print(d['a'])")
    assert rc == 0
    assert out == "1"


def test_string_subscript():
    """String indexing."""
    out, err, rc = clython_run("s = 'hello'; print(s[0])")
    assert rc == 0
    assert out == "h"


def test_nested_list_subscript():
    """Nested list subscript."""
    out, err, rc = clython_run("m = [[1, 2], [3, 4]]; print(m[1][0])")
    assert rc == 0
    assert out == "3"


# ---------------------------------------------------------------------------
# Slicing
# ---------------------------------------------------------------------------

def test_slice_start_stop():
    """Basic start:stop slice."""
    out, err, rc = clython_run("x = [0, 1, 2, 3, 4]; print(x[1:3])")
    assert rc == 0
    assert out == "[1, 2]"


def test_slice_from_start():
    """Slice from beginning."""
    out, err, rc = clython_run("x = [0, 1, 2, 3]; print(x[:2])")
    assert rc == 0
    assert out == "[0, 1]"


def test_slice_to_end():
    """Slice to end."""
    out, err, rc = clython_run("x = [0, 1, 2, 3]; print(x[2:])")
    assert rc == 0
    assert out == "[2, 3]"


def test_slice_with_step():
    """Slice with step."""
    out, err, rc = clython_run("x = [0, 1, 2, 3, 4, 5]; print(x[::2])")
    assert rc == 0
    assert out == "[0, 2, 4]"


def test_slice_reverse():
    """Reverse a list with slice."""
    out, err, rc = clython_run("x = [1, 2, 3]; print(x[::-1])")
    assert rc == 0
    assert out == "[3, 2, 1]"


def test_string_slice():
    """String slicing."""
    out, err, rc = clython_run("s = 'hello'; print(s[1:4])")
    assert rc == 0
    assert out == "ell"


# ---------------------------------------------------------------------------
# Function calls
# ---------------------------------------------------------------------------

def test_simple_function_call():
    """Simple built-in function call."""
    out, err, rc = clython_run("print(len([1, 2, 3]))")
    assert rc == 0
    assert out == "3"


def test_function_call_with_keyword():
    """Function call with keyword argument."""
    out, err, rc = clython_run("print('hello', end='!')")
    assert rc == 0
    assert out == "hello!"


def test_nested_function_calls():
    """Nested function calls."""
    out, err, rc = clython_run("print(str(len([1, 2, 3])))")
    assert rc == 0
    assert out == "3"


def test_method_call_chained():
    """Chained method call."""
    out, err, rc = clython_run("print('  hello  '.strip().replace('h', 'H'))")
    assert rc == 0
    assert out == "Hello"


def test_user_defined_function_call():
    """Call a user-defined function."""
    source = "def add(a, b): return a + b\nprint(add(2, 3))"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "5"


# ---------------------------------------------------------------------------
# Complex primary expression combinations
# ---------------------------------------------------------------------------

def test_subscript_then_method():
    """Subscript then method call."""
    out, err, rc = clython_run("x = ['hello', 'world']; print(x[0].upper())")
    assert rc == 0
    assert out == "HELLO"


def test_call_result_subscript():
    """Subscript on function call result."""
    out, err, rc = clython_run("print(list(range(5))[2])")
    assert rc == 0
    assert out == "2"


def test_attribute_subscript_call():
    """Attribute then subscript then call."""
    out, err, rc = clython_run("d = {'k': 'hello'}; print(d['k'].upper())")
    assert rc == 0
    assert out == "HELLO"


def test_varargs_call():
    """Function call with *args unpacking."""
    source = "args = [1, 2, 3]; print(sum(args))"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "6"


def test_kwargs_call():
    """Function call with **kwargs unpacking."""
    source = "def f(a, b): return a + b\nkw = {'a': 3, 'b': 4}\nprint(f(**kw))"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "7"


def test_generator_as_argument():
    """Generator expression passed to sum()."""
    out, err, rc = clython_run("print(sum(x*x for x in range(4)))")
    assert rc == 0
    assert out == "14"
