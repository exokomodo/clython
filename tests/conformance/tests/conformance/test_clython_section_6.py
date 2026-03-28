"""
Clython Section 6 conformance tests — methods, kwargs, defaults, tuples.

Tests specific interpreter features that require Clython execution:
string/list method dispatch, keyword argument passing, lambda defaults,
and tuple packing/unpacking.
"""

import os
import subprocess
import pytest

CLYTHON_BIN = os.environ.get("CLYTHON_BIN")

pytestmark = pytest.mark.skipif(
    not CLYTHON_BIN, reason="CLYTHON_BIN not set — skipping Clython-specific tests"
)


def clython_run(source: str, timeout: float = 30.0):
    """Run source through Clython, return (stdout, stderr, returncode)."""
    result = subprocess.run(
        [CLYTHON_BIN, "-c", source],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode


# ── String methods ───────────────────────────────────────────────────────────


class TestClythonStringMethods:
    """Test str method dispatch via attribute access."""

    def test_string_method_upper(self):
        """'hello'.upper() → HELLO"""
        stdout, stderr, rc = clython_run("print('hello'.upper())")
        assert rc == 0 and stdout == "HELLO", f"rc={rc}, stdout={stdout!r}, stderr={stderr!r}"

    def test_string_method_lower(self):
        stdout, stderr, rc = clython_run("print('HELLO'.lower())")
        assert rc == 0 and stdout == "hello"

    def test_string_method_strip(self):
        stdout, stderr, rc = clython_run("print('  hi  '.strip())")
        assert rc == 0 and stdout == "hi"

    def test_string_method_split(self):
        stdout, stderr, rc = clython_run("print('a,b,c'.split(','))")
        assert rc == 0 and stdout == "['a', 'b', 'c']"

    def test_string_method_join(self):
        stdout, stderr, rc = clython_run("print('-'.join(['a', 'b', 'c']))")
        assert rc == 0 and stdout == "a-b-c"

    def test_string_method_replace(self):
        stdout, stderr, rc = clython_run("print('hello world'.replace('world', 'python'))")
        assert rc == 0 and stdout == "hello python"

    def test_string_method_startswith(self):
        stdout, stderr, rc = clython_run("print('hello'.startswith('hel'))")
        assert rc == 0 and stdout == "True"

    def test_string_method_endswith(self):
        stdout, stderr, rc = clython_run("print('hello'.endswith('llo'))")
        assert rc == 0 and stdout == "True"

    def test_string_method_find(self):
        stdout, stderr, rc = clython_run("print('hello'.find('ll'))")
        assert rc == 0 and stdout == "2"

    def test_string_method_count(self):
        stdout, stderr, rc = clython_run("print('banana'.count('an'))")
        assert rc == 0 and stdout == "2"

    def test_string_method_format(self):
        stdout, stderr, rc = clython_run("print('Hello, {}!'.format('world'))")
        assert rc == 0 and stdout == "Hello, world!"


# ── List methods ─────────────────────────────────────────────────────────────


class TestClythonListMethods:
    """Test list method dispatch via attribute access."""

    def test_list_method_append(self):
        """x = [1,2]; x.append(3); print(x) → [1, 2, 3]"""
        stdout, stderr, rc = clython_run("x = [1, 2]\nx.append(3)\nprint(x)")
        assert rc == 0 and stdout == "[1, 2, 3]", f"rc={rc}, stdout={stdout!r}, stderr={stderr!r}"

    def test_list_method_pop(self):
        stdout, stderr, rc = clython_run("x = [1, 2, 3]\nprint(x.pop())")
        assert rc == 0 and stdout == "3"

    def test_list_method_reverse(self):
        stdout, stderr, rc = clython_run("x = [1, 2, 3]\nx.reverse()\nprint(x)")
        assert rc == 0 and stdout == "[3, 2, 1]"

    def test_list_method_sort(self):
        stdout, stderr, rc = clython_run("x = [3, 1, 2]\nx.sort()\nprint(x)")
        assert rc == 0 and stdout == "[1, 2, 3]"

    def test_list_method_copy(self):
        stdout, stderr, rc = clython_run("x = [1, 2]\ny = x.copy()\ny.append(3)\nprint(x)\nprint(y)")
        assert rc == 0 and stdout == "[1, 2]\n[1, 2, 3]"

    def test_list_method_count(self):
        stdout, stderr, rc = clython_run("print([1, 2, 1, 3, 1].count(1))")
        assert rc == 0 and stdout == "3"


# ── Keyword arguments ────────────────────────────────────────────────────────


class TestClythonKeywordArguments:
    """Test keyword argument passing to functions."""

    def test_keyword_argument_print_sep(self):
        """print('a', 'b', sep='-') → a-b"""
        stdout, stderr, rc = clython_run("print('a', 'b', sep='-')")
        assert rc == 0 and stdout == "a-b", f"rc={rc}, stdout={stdout!r}, stderr={stderr!r}"

    def test_keyword_argument_print_end(self):
        stdout, stderr, rc = clython_run("print('hello', end='!')\nprint('world')")
        assert rc == 0 and stdout == "hello!world"

    def test_keyword_argument_print_sep_and_end(self):
        stdout, stderr, rc = clython_run("print('a', 'b', 'c', sep=', ', end='.')")
        assert rc == 0 and stdout == "a, b, c."


# ── Lambda defaults ──────────────────────────────────────────────────────────


class TestClythonLambdaDefaults:
    """Test lambda expressions with default parameter values."""

    def test_lambda_default_args(self):
        """f = lambda x, y=10: x + y; f(5) → 15"""
        stdout, stderr, rc = clython_run("f = lambda x, y=10: x + y\nprint(f(5))")
        assert rc == 0 and stdout == "15", f"rc={rc}, stdout={stdout!r}, stderr={stderr!r}"

    def test_lambda_default_override(self):
        stdout, stderr, rc = clython_run("f = lambda x, y=10: x + y\nprint(f(5, 3))")
        assert rc == 0 and stdout == "8"

    def test_lambda_multiple_defaults(self):
        stdout, stderr, rc = clython_run("f = lambda a=1, b=2, c=3: a + b + c\nprint(f())")
        assert rc == 0 and stdout == "6"


# ── Tuple packing / unpacking / swap ─────────────────────────────────────────


class TestClythonTuplePacking:
    """Test tuple packing via comma-separated expressions."""

    def test_tuple_packing(self):
        """x = 1, 2, 3 should produce a tuple"""
        stdout, stderr, rc = clython_run("x = 1, 2, 3\nprint(x)")
        assert rc == 0 and stdout == "(1, 2, 3)", f"rc={rc}, stdout={stdout!r}, stderr={stderr!r}"

    def test_tuple_packing_two(self):
        stdout, stderr, rc = clython_run("x = 1, 2\nprint(x)")
        assert rc == 0 and stdout == "(1, 2)"


class TestClythonTupleUnpacking:
    """Test tuple unpacking in assignments."""

    def test_tuple_unpacking(self):
        """a, b, c = 1, 2, 3"""
        stdout, stderr, rc = clython_run("a, b, c = 1, 2, 3\nprint(a)\nprint(b)\nprint(c)")
        assert rc == 0 and stdout == "1\n2\n3", f"rc={rc}, stdout={stdout!r}, stderr={stderr!r}"

    def test_tuple_unpacking_list(self):
        stdout, stderr, rc = clython_run("a, b = [10, 20]\nprint(a)\nprint(b)")
        assert rc == 0 and stdout == "10\n20"


class TestClythonSwap:
    """Test variable swap via tuple unpacking."""

    def test_swap(self):
        """a, b = b, a should swap values"""
        stdout, stderr, rc = clython_run("a = 1\nb = 2\na, b = b, a\nprint(a)\nprint(b)")
        assert rc == 0 and stdout == "2\n1", f"rc={rc}, stdout={stdout!r}, stderr={stderr!r}"

    def test_swap_strings(self):
        stdout, stderr, rc = clython_run("x = 'hello'\ny = 'world'\nx, y = y, x\nprint(x)\nprint(y)")
        assert rc == 0 and stdout == "world\nhello"
