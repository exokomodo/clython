"""Clython runtime tests — Section 6.2: Atoms.

Tests that the Clython interpreter correctly evaluates atom expressions:
built-in constants, identifiers, numeric/string literals, parenthesized
forms, list/dict/set displays, and generator expressions.
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


class TestBuiltinConstants:
    def test_true_is_bool(self):
        out, err, rc = clython_run("print(type(True).__name__)")
        assert rc == 0
        assert out == "bool"

    def test_false_is_bool(self):
        out, err, rc = clython_run("print(type(False).__name__)")
        assert rc == 0
        assert out == "bool"

    def test_none_is_none_type(self):
        out, err, rc = clython_run("print(type(None).__name__)")
        assert rc == 0
        assert out == "NoneType"

    @pytest.mark.xfail(reason="Clython reports ellipsis type as 'PY-ELLIPSIS' instead of 'ellipsis'")
    def test_ellipsis_is_ellipsis(self):
        out, err, rc = clython_run("print(type(...).__name__)")
        assert rc == 0
        assert out == "ellipsis"

    def test_true_equals_one(self):
        out, err, rc = clython_run("print(True == 1)")
        assert rc == 0
        assert out == "True"

    def test_false_equals_zero(self):
        out, err, rc = clython_run("print(False == 0)")
        assert rc == 0
        assert out == "True"

    def test_none_is_singleton(self):
        out, err, rc = clython_run("print(None is None)")
        assert rc == 0
        assert out == "True"

    def test_true_assignment_forbidden(self):
        """assigning to True is a SyntaxError"""
        out, err, rc = clython_run("True = 1")
        assert rc != 0

    def test_none_assignment_forbidden(self):
        """assigning to None is a SyntaxError"""
        out, err, rc = clython_run("None = 'x'")
        assert rc != 0


class TestIdentifiers:
    def test_simple_name_lookup(self):
        out, err, rc = clython_run("x = 42\nprint(x)")
        assert rc == 0
        assert out == "42"

    def test_unbound_name_raises_name_error(self):
        out, err, rc = clython_run(
            "try:\n    print(undefined_xyz)\nexcept NameError:\n    print('NameError')"
        )
        assert rc == 0
        assert out == "NameError"

    def test_underscore_name(self):
        out, err, rc = clython_run("_ = 99\nprint(_)")
        assert rc == 0
        assert out == "99"

    def test_dunder_name(self):
        out, err, rc = clython_run("print(__name__)")
        assert rc == 0
        assert out == "__main__"


class TestNumericLiterals:
    def test_integer_literal(self):
        out, err, rc = clython_run("print(42)")
        assert rc == 0
        assert out == "42"

    def test_float_literal(self):
        out, err, rc = clython_run("print(3.14)")
        assert rc == 0
        assert out == "3.14"

    def test_complex_literal(self):
        out, err, rc = clython_run("print(type(1j).__name__)")
        assert rc == 0
        assert out == "complex"

    def test_hex_literal(self):
        out, err, rc = clython_run("print(0xFF)")
        assert rc == 0
        assert out == "255"

    def test_octal_literal(self):
        out, err, rc = clython_run("print(0o10)")
        assert rc == 0
        assert out == "8"

    def test_binary_literal(self):
        out, err, rc = clython_run("print(0b1010)")
        assert rc == 0
        assert out == "10"

    def test_scientific_notation(self):
        out, err, rc = clython_run("print(1e3)")
        assert rc == 0
        assert out == "1000.0"


class TestStringLiterals:
    def test_single_quoted_string(self):
        out, err, rc = clython_run("print('hello')")
        assert rc == 0
        assert out == "hello"

    def test_double_quoted_string(self):
        out, err, rc = clython_run('print("world")')
        assert rc == 0
        assert out == "world"

    def test_triple_quoted_string(self):
        out, err, rc = clython_run('print("""triple""")')
        assert rc == 0
        assert out == "triple"

    def test_raw_string(self):
        out, err, rc = clython_run(r"print(r'\n')")
        assert rc == 0
        assert out == r"\n"

    def test_fstring_basic(self):
        out, err, rc = clython_run("x = 7\nprint(f'value={x}')")
        assert rc == 0
        assert out == "value=7"

    def test_bytes_literal(self):
        out, err, rc = clython_run("print(type(b'hello').__name__)")
        assert rc == 0
        assert out == "bytes"


class TestParenthesizedForms:
    def test_empty_parens_creates_empty_tuple(self):
        out, err, rc = clython_run("print(type(())).__name__")
        # fallback form
        out, err, rc = clython_run("t = ()\nprint(type(t).__name__, len(t))")
        assert rc == 0
        assert out == "tuple 0"

    def test_parenthesized_expression(self):
        out, err, rc = clython_run("print((2 + 3) * 4)")
        assert rc == 0
        assert out == "20"

    def test_single_element_tuple(self):
        out, err, rc = clython_run("t = (42,)\nprint(type(t).__name__, t[0])")
        assert rc == 0
        assert out == "tuple 42"

    def test_multi_element_tuple(self):
        out, err, rc = clython_run("t = (1, 2, 3)\nprint(t)")
        assert rc == 0
        assert out == "(1, 2, 3)"


class TestListDisplays:
    def test_empty_list(self):
        out, err, rc = clython_run("print([])")
        assert rc == 0
        assert out == "[]"

    def test_list_with_elements(self):
        out, err, rc = clython_run("print([1, 2, 3])")
        assert rc == 0
        assert out == "[1, 2, 3]"

    def test_list_type(self):
        out, err, rc = clython_run("print(type([1, 2]).__name__)")
        assert rc == 0
        assert out == "list"

    def test_list_comprehension(self):
        out, err, rc = clython_run("print([x * 2 for x in range(4)])")
        assert rc == 0
        assert out == "[0, 2, 4, 6]"


class TestDictDisplays:
    def test_empty_dict(self):
        out, err, rc = clython_run("print({})")
        assert rc == 0
        assert out == "{}"

    def test_dict_with_entries(self):
        out, err, rc = clython_run("d = {'a': 1, 'b': 2}\nprint(d['a'])")
        assert rc == 0
        assert out == "1"

    def test_dict_type(self):
        out, err, rc = clython_run("print(type({'k': 'v'}).__name__)")
        assert rc == 0
        assert out == "dict"

    def test_dict_comprehension(self):
        out, err, rc = clython_run("print({x: x**2 for x in range(3)})")
        assert rc == 0
        assert out == "{0: 0, 1: 1, 2: 4}"


class TestSetDisplays:
    def test_set_with_elements(self):
        out, err, rc = clython_run("s = {1, 2, 3}\nprint(type(s).__name__)")
        assert rc == 0
        assert out == "set"

    def test_set_deduplication(self):
        out, err, rc = clython_run("s = {1, 2, 2, 3, 1}\nprint(sorted(s))")
        assert rc == 0
        assert out == "[1, 2, 3]"

    def test_set_comprehension(self):
        out, err, rc = clython_run("s = {x % 3 for x in range(9)}\nprint(sorted(s))")
        assert rc == 0
        assert out == "[0, 1, 2]"

    def test_empty_braces_is_dict_not_set(self):
        out, err, rc = clython_run("print(type({}).__name__)")
        assert rc == 0
        assert out == "dict"


class TestGeneratorExpressions:
    @pytest.mark.xfail(reason="Clython reports generator type as 'PY-GENERATOR' instead of 'generator'")
    def test_generator_type(self):
        out, err, rc = clython_run("g = (x for x in range(3))\nprint(type(g).__name__)")
        assert rc == 0
        assert out == "generator"

    def test_generator_sum(self):
        out, err, rc = clython_run("print(sum(x * x for x in range(4)))")
        assert rc == 0
        assert out == "14"

    def test_generator_with_condition(self):
        out, err, rc = clython_run("print(list(x for x in range(6) if x % 2 == 0))")
        assert rc == 0
        assert out == "[0, 2, 4]"

    def test_generator_lazy(self):
        """generator does not consume elements until iterated"""
        out, err, rc = clython_run(
            "g = (x for x in range(1000000))\n"
            "print(next(g), next(g))"
        )
        assert rc == 0
        assert out == "0 1"
