"""
Section 7.2: Assignment Statements - Clython Runtime Test Suite

Tests that Clython actually executes assignment statements correctly at runtime.
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


def test_simple_assignment():
    """Basic variable assignment"""
    out, err, rc = clython_run("x = 42\nprint(x)")
    assert rc == 0
    assert out == "42"


def test_string_assignment():
    """String assignment"""
    out, err, rc = clython_run("name = 'hello'\nprint(name)")
    assert rc == 0
    assert out == "hello"


def test_chained_assignment():
    """Chained assignment (a = b = value)"""
    out, err, rc = clython_run("a = b = c = 10\nprint(a, b, c)")
    assert rc == 0
    assert out == "10 10 10"


def test_tuple_unpacking():
    """Tuple unpacking assignment"""
    out, err, rc = clython_run("a, b = 1, 2\nprint(a, b)")
    assert rc == 0
    assert out == "1 2"


def test_three_way_unpack():
    """Three-way tuple unpack"""
    out, err, rc = clython_run("x, y, z = 10, 20, 30\nprint(x, y, z)")
    assert rc == 0
    assert out == "10 20 30"


def test_starred_unpack():
    """Starred unpacking: first, *rest"""
    out, err, rc = clython_run("first, *rest = [1, 2, 3, 4]\nprint(first, rest)")
    assert rc == 0
    assert out == "1 [2, 3, 4]"


def test_starred_unpack_tail():
    """Starred unpacking: *init, last"""
    out, err, rc = clython_run("*init, last = [1, 2, 3, 4]\nprint(init, last)")
    assert rc == 0
    assert out == "[1, 2, 3] 4"


def test_starred_unpack_middle():
    """Starred unpacking: first, *middle, last"""
    out, err, rc = clython_run("first, *middle, last = [1, 2, 3, 4, 5]\nprint(first, middle, last)")
    assert rc == 0
    assert out == "1 [2, 3, 4] 5"


def test_nested_tuple_unpack():
    """Nested tuple unpacking"""
    out, err, rc = clython_run("(a, b), c = (1, 2), 3\nprint(a, b, c)")
    assert rc == 0
    assert out == "1 2 3"


def test_list_unpack():
    """List-style unpacking"""
    out, err, rc = clython_run("[a, b, c] = [10, 20, 30]\nprint(a, b, c)")
    assert rc == 0
    assert out == "10 20 30"


def test_attribute_assignment():
    """Attribute assignment"""
    out, err, rc = clython_run(
        "class Obj: pass\n"
        "o = Obj()\n"
        "o.x = 99\n"
        "print(o.x)"
    )
    assert rc == 0
    assert out == "99"


def test_subscript_assignment():
    """Subscript assignment"""
    out, err, rc = clython_run(
        "lst = [0, 0, 0]\n"
        "lst[1] = 42\n"
        "print(lst)"
    )
    assert rc == 0
    assert out == "[0, 42, 0]"


def test_dict_subscript_assignment():
    """Dictionary subscript assignment"""
    out, err, rc = clython_run(
        "d = {}\n"
        "d['key'] = 'value'\n"
        "print(d['key'])"
    )
    assert rc == 0
    assert out == "value"


def test_augmented_add_assignment():
    """Augmented addition assignment +="""
    out, err, rc = clython_run("x = 5\nx += 3\nprint(x)")
    assert rc == 0
    assert out == "8"


def test_augmented_sub_assignment():
    """Augmented subtraction assignment -="""
    out, err, rc = clython_run("x = 10\nx -= 4\nprint(x)")
    assert rc == 0
    assert out == "6"


def test_augmented_mul_assignment():
    """Augmented multiplication assignment *="""
    out, err, rc = clython_run("x = 3\nx *= 7\nprint(x)")
    assert rc == 0
    assert out == "21"


def test_augmented_div_assignment():
    """Augmented floor division assignment //="""
    out, err, rc = clython_run("x = 17\nx //= 5\nprint(x)")
    assert rc == 0
    assert out == "3"


def test_augmented_mod_assignment():
    """Augmented modulo assignment %="""
    out, err, rc = clython_run("x = 17\nx %= 5\nprint(x)")
    assert rc == 0
    assert out == "2"


def test_augmented_pow_assignment():
    """Augmented power assignment **="""
    out, err, rc = clython_run("x = 3\nx **= 4\nprint(x)")
    assert rc == 0
    assert out == "81"


def test_multiple_unpack_from_function():
    """Unpack multiple values returned from function"""
    out, err, rc = clython_run(
        "def get_pair(): return (10, 20)\n"
        "a, b = get_pair()\n"
        "print(a, b)"
    )
    assert rc == 0
    assert out == "10 20"


def test_global_variable_assignment():
    """Global variable assignment in function"""
    out, err, rc = clython_run(
        "x = 0\n"
        "def set_x(val):\n"
        "    global x\n"
        "    x = val\n"
        "set_x(99)\n"
        "print(x)"
    )
    assert rc == 0
    assert out == "99"


def test_nonlocal_assignment():
    """Nonlocal assignment in nested function"""
    out, err, rc = clython_run(
        "def outer():\n"
        "    x = 1\n"
        "    def inner():\n"
        "        nonlocal x\n"
        "        x = 2\n"
        "    inner()\n"
        "    return x\n"
        "print(outer())"
    )
    assert rc == 0
    assert out == "2"


def test_walrus_operator():
    """Walrus operator := assigns and returns value"""
    out, err, rc = clython_run(
        "if (n := 10) > 5:\n"
        "    print('n is', n)"
    )
    assert rc == 0
    assert out == "n is 10"


def test_swap_via_unpack():
    """Swap two variables using tuple unpacking"""
    out, err, rc = clython_run(
        "a, b = 1, 2\n"
        "a, b = b, a\n"
        "print(a, b)"
    )
    assert rc == 0
    assert out == "2 1"


def test_unpack_string():
    """Unpack characters from a string"""
    out, err, rc = clython_run(
        "a, b, c = 'xyz'\n"
        "print(a, b, c)"
    )
    assert rc == 0
    assert out == "x y z"


def test_large_tuple_unpack():
    """Unpack large tuple"""
    values = ", ".join(str(i) for i in range(10))
    vars_ = ", ".join(f"v{i}" for i in range(10))
    out, err, rc = clython_run(
        f"{vars_} = {values}\n"
        "print(v0, v9)"
    )
    assert rc == 0
    assert out == "0 9"
