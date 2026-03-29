"""
Clython Runtime Tests: Section 6.15 - Expression Lists

Tests expression list / tuple formation execution via the Clython binary.
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


def test_simple_tuple_creation():
    out, err, rc = clython_run("t = 1, 2, 3; print(t)")
    assert rc == 0
    assert out == "(1, 2, 3)"


def test_tuple_without_parens():
    out, err, rc = clython_run("a, b = 1, 2; print(a, b)")
    assert rc == 0
    assert out == "1 2"


def test_single_element_tuple():
    out, err, rc = clython_run("t = (42,); print(t); print(type(t).__name__)")
    assert rc == 0
    assert out == "(42,)\ntuple"


def test_single_element_tuple_without_parens():
    out, err, rc = clython_run("t = 42,; print(t)")
    assert rc == 0
    assert out == "(42,)"


def test_empty_tuple():
    out, err, rc = clython_run("t = (); print(t); print(len(t))")
    assert rc == 0
    assert out == "()\n0"


def test_trailing_comma():
    out, err, rc = clython_run("t = 1, 2, 3,; print(t)")
    assert rc == 0
    assert out == "(1, 2, 3)"


def test_tuple_unpacking_basic():
    out, err, rc = clython_run("a, b, c = (10, 20, 30); print(a, b, c)")
    assert rc == 0
    assert out == "10 20 30"


def test_tuple_unpacking_starred_rest():
    out, err, rc = clython_run("first, *rest = [1, 2, 3, 4]; print(first); print(rest)")
    assert rc == 0
    assert out == "1\n[2, 3, 4]"


def test_tuple_unpacking_starred_beginning():
    out, err, rc = clython_run("*beginning, last = [1, 2, 3, 4]; print(beginning); print(last)")
    assert rc == 0
    assert out == "[1, 2, 3]\n4"


def test_tuple_unpacking_starred_middle():
    out, err, rc = clython_run("first, *middle, last = [1, 2, 3, 4, 5]; print(first, middle, last)")
    assert rc == 0
    assert out == "1 [2, 3, 4] 5"


def test_expression_list_in_return():
    source = """
def func():
    return 1, 2, 3
print(func())
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "(1, 2, 3)"


def test_expression_list_in_for():
    source = """
pairs = [(1, 'a'), (2, 'b'), (3, 'c')]
for n, c in pairs:
    print(n, c)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "1 a\n2 b\n3 c"


def test_starred_in_list_literal():
    out, err, rc = clython_run("a = [1, 2]; b = [3, 4]; print([*a, *b])")
    assert rc == 0
    assert out == "[1, 2, 3, 4]"


def test_starred_in_function_call():
    out, err, rc = clython_run("args = [1, 2, 3]; print(*args)")
    assert rc == 0
    assert out == "1 2 3"


@pytest.mark.xfail(reason="Clython **kwargs unpacking in function calls may not be implemented")
def test_double_starred_in_function_call():
    out, err, rc = clython_run("kw = {'end': '!', 'sep': '-'}; print('a', 'b', **kw)")
    assert rc == 0
    assert out == "a-b!"


def test_nested_tuple_unpacking():
    out, err, rc = clython_run("(a, b), c = (1, 2), 3; print(a, b, c)")
    assert rc == 0
    assert out == "1 2 3"


def test_simultaneous_assignment():
    out, err, rc = clython_run("a, b = 1, 2; a, b = b, a; print(a, b)")
    assert rc == 0
    assert out == "2 1"


def test_tuple_in_comprehension():
    source = """
result = [(x, y) for x in range(2) for y in range(2)]
print(result)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "[(0, 0), (0, 1), (1, 0), (1, 1)]"


def test_tuple_type_and_immutability():
    source = """
t = (1, 2, 3)
print(isinstance(t, tuple))
try:
    t[0] = 99
    print('mutated')
except TypeError:
    print('immutable')
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True\nimmutable"


def test_expression_list_in_dict_comprehension():
    source = """
keys = ['a', 'b', 'c']
values = [1, 2, 3]
result = {k: v for k, v in zip(keys, values)}
print(result)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "{'a': 1, 'b': 2, 'c': 3}"


@pytest.mark.xfail(reason="Clython starred set unpacking may not be implemented")
def test_starred_merge_sets():
    out, err, rc = clython_run("s1 = {1, 2}; s2 = {3, 4}; print(sorted({*s1, *s2}))")
    assert rc == 0
    assert out == "[1, 2, 3, 4]"


def test_starred_in_tuple_literal():
    out, err, rc = clython_run("a = (1, 2); b = (3, 4); print((*a, *b))")
    assert rc == 0
    assert out == "(1, 2, 3, 4)"


def test_expression_list_precedence():
    """Comma has lowest precedence — all sub-expressions evaluated first."""
    out, err, rc = clython_run("t = 1 + 2, 3 * 4; print(t)")
    assert rc == 0
    assert out == "(3, 12)"


def test_zip_and_unpack():
    source = """
keys = [1, 2, 3]
vals = ['a', 'b', 'c']
pairs = list(zip(keys, vals))
print(pairs)
k2, v2 = zip(*pairs)
print(list(k2))
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "[(1, 'a'), (2, 'b'), (3, 'c')]\n[1, 2, 3]"
