"""
Section 8.10: Match Statements - Clython Runtime Test Suite

Tests that Clython actually executes match statements correctly at runtime.
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


def test_basic_literal_match():
    """Match against integer literals"""
    out, err, rc = clython_run(
        "x = 2\n"
        "match x:\n"
        "    case 1: print('one')\n"
        "    case 2: print('two')\n"
        "    case 3: print('three')"
    )
    assert rc == 0
    assert out == "two"


def test_match_wildcard():
    """Match with wildcard _ catches anything"""
    out, err, rc = clython_run(
        "x = 99\n"
        "match x:\n"
        "    case 1: print('one')\n"
        "    case _: print('other')"
    )
    assert rc == 0
    assert out == "other"


def test_match_string_literal():
    """Match against string literals"""
    out, err, rc = clython_run(
        "status = 'error'\n"
        "match status:\n"
        "    case 'ok': print('success')\n"
        "    case 'error': print('failure')\n"
        "    case _: print('unknown')"
    )
    assert rc == 0
    assert out == "failure"


def test_match_capture_pattern():
    """Match with capture pattern binds variable"""
    out, err, rc = clython_run(
        "val = 42\n"
        "match val:\n"
        "    case x: print(x)"
    )
    assert rc == 0
    assert out == "42"


def test_match_tuple_pattern():
    """Match against tuple/sequence pattern"""
    out, err, rc = clython_run(
        "point = (1, 2)\n"
        "match point:\n"
        "    case (0, 0): print('origin')\n"
        "    case (x, 0): print('x-axis', x)\n"
        "    case (0, y): print('y-axis', y)\n"
        "    case (x, y): print('point', x, y)"
    )
    assert rc == 0
    assert out == "point 1 2"


def test_match_list_pattern():
    """Match against list pattern"""
    out, err, rc = clython_run(
        "items = [1, 2, 3]\n"
        "match items:\n"
        "    case []: print('empty')\n"
        "    case [x]: print('one:', x)\n"
        "    case [x, y]: print('two:', x, y)\n"
        "    case [x, y, z]: print('three:', x, y, z)"
    )
    assert rc == 0
    assert out == "three: 1 2 3"


def test_match_list_star_pattern():
    """Match list with starred rest"""
    out, err, rc = clython_run(
        "items = [1, 2, 3, 4]\n"
        "match items:\n"
        "    case [first, *rest]: print(first, rest)"
    )
    assert rc == 0
    assert out == "1 [2, 3, 4]"


def test_match_dict_pattern():
    """Match against mapping pattern"""
    out, err, rc = clython_run(
        "d = {'type': 'user', 'name': 'Alice'}\n"
        "match d:\n"
        "    case {'type': 'user', 'name': name}: print('User:', name)\n"
        "    case {'type': 'admin'}: print('Admin')"
    )
    assert rc == 0
    assert out == "User: Alice"


def test_match_dict_rest_pattern():
    """Match with ** rest in mapping"""
    out, err, rc = clython_run(
        "d = {'kind': 'circle', 'r': 5, 'color': 'red'}\n"
        "match d:\n"
        "    case {'kind': 'circle', **rest}: print(sorted(rest.keys()))"
    )
    assert rc == 0
    assert out == "['color', 'r']"


def test_match_guard():
    """Match case with guard condition"""
    out, err, rc = clython_run(
        "val = 10\n"
        "match val:\n"
        "    case x if x > 5: print('big:', x)\n"
        "    case x: print('small:', x)"
    )
    assert rc == 0
    assert out == "big: 10"


def test_match_or_pattern():
    """Match with or pattern using |"""
    out, err, rc = clython_run(
        "for val in [1, 2, 3, 5]:\n"
        "    match val:\n"
        "        case 1 | 2: print(val, 'low')\n"
        "        case 3 | 5: print(val, 'mid')"
    )
    assert rc == 0
    assert out == "1 low\n2 low\n3 mid\n5 mid"


def test_match_none_literal():
    """Match against None"""
    out, err, rc = clython_run(
        "val = None\n"
        "match val:\n"
        "    case None: print('none')\n"
        "    case _: print('something')"
    )
    assert rc == 0
    assert out == "none"


def test_match_bool_literals():
    """Match against True/False"""
    out, err, rc = clython_run(
        "for b in [True, False]:\n"
        "    match b:\n"
        "        case True: print('yes')\n"
        "        case False: print('no')"
    )
    assert rc == 0
    assert out == "yes\nno"


def test_match_no_case_matches():
    """No case matched — control falls through"""
    out, err, rc = clython_run(
        "x = 99\n"
        "result = 'no match'\n"
        "match x:\n"
        "    case 1: result = 'one'\n"
        "    case 2: result = 'two'\n"
        "print(result)"
    )
    assert rc == 0
    assert out == "no match"


def test_match_class_pattern():
    """Match against class pattern with __match_args__"""
    out, err, rc = clython_run(
        "class Point:\n"
        "    __match_args__ = ('x', 'y')\n"
        "    def __init__(self, x, y):\n"
        "        self.x = x\n"
        "        self.y = y\n"
        "p = Point(0, 5)\n"
        "match p:\n"
        "    case Point(x=0, y=y): print('y-axis', y)\n"
        "    case Point(x=x, y=y): print('point', x, y)"
    )
    assert rc == 0
    assert out == "y-axis 5"


def test_match_multiple_cases_with_wildcard():
    """Multiple cases with wildcard at end"""
    out, err, rc = clython_run(
        "for code in [200, 404, 500, 999]:\n"
        "    match code:\n"
        "        case 200: print('ok')\n"
        "        case 404: print('not found')\n"
        "        case 500: print('server error')\n"
        "        case _: print('unknown')"
    )
    assert rc == 0
    assert out == "ok\nnot found\nserver error\nunknown"


def test_match_in_function():
    """Match statement inside a function"""
    out, err, rc = clython_run(
        "def describe(val):\n"
        "    match val:\n"
        "        case 0: return 'zero'\n"
        "        case x if x > 0: return 'positive'\n"
        "        case _: return 'negative'\n"
        "print(describe(0))\n"
        "print(describe(5))\n"
        "print(describe(-3))"
    )
    assert rc == 0
    assert out == "zero\npositive\nnegative"


def test_match_sequence_two_elements():
    """Match sequence of exactly two elements"""
    out, err, rc = clython_run(
        "pairs = [(1, 2), (0, 0), (3, 0)]\n"
        "for p in pairs:\n"
        "    match p:\n"
        "        case (0, 0): print('origin')\n"
        "        case (x, 0): print('x-axis', x)\n"
        "        case (x, y): print('pair', x, y)"
    )
    assert rc == 0
    assert out == "pair 1 2\norigin\nx-axis 3"


def test_match_nested_dict():
    """Match nested dictionary pattern"""
    out, err, rc = clython_run(
        "event = {'type': 'click', 'x': 10, 'y': 20}\n"
        "match event:\n"
        "    case {'type': 'click', 'x': x, 'y': y}: print('click at', x, y)\n"
        "    case _: print('other event')"
    )
    assert rc == 0
    assert out == "click at 10 20"


def test_match_large_case_set():
    """Match with many cases"""
    cases = "\n".join(f"        case {i}: print({i})" for i in range(10))
    out, err, rc = clython_run(
        f"for x in [0, 5, 9]:\n"
        f"    match x:\n"
        f"{cases}"
    )
    assert rc == 0
    assert out == "0\n5\n9"


def test_match_guard_complex():
    """Match with complex guard expression"""
    out, err, rc = clython_run(
        "point = (3, 4)\n"
        "match point:\n"
        "    case (x, y) if x**2 + y**2 == 25: print('on unit circle of r=5')\n"
        "    case (x, y): print('elsewhere', x, y)"
    )
    assert rc == 0
    assert out == "on unit circle of r=5"
