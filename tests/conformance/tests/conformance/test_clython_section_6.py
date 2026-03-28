"""
Clython Section 6 conformance tests — Expressions.

Tests run through the Clython binary (CLYTHON_BIN) to verify expression
evaluation matches Python 3.12 semantics.

Coverage:
  6.1  Atoms (identifiers, literals, displays, comprehensions)
  6.2  Arithmetic conversions
  6.3  Primaries (attribute refs, subscriptions, slicings, calls)
  6.5  Power operator
  6.6  Unary arithmetic and bitwise operators
  6.7  Binary arithmetic operators
  6.8  Shifting operations
  6.9  Binary bitwise operations
  6.10 Comparisons
  6.11 Boolean operations
  6.12 Walrus operator
  6.13 Conditional expressions
  6.14 Lambdas
  6.15 Expression lists
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


# ─── 6.1: Atoms ───


class TestSection61Identifiers:
    """6.1.1: Identifier atoms."""

    def test_simple_name_lookup(self):
        out, _, rc = clython_run("x = 42\nprint(x)")
        assert rc == 0 and out == "42"

    def test_name_rebinding(self):
        out, _, rc = clython_run("x = 1\nx = 2\nprint(x)")
        assert rc == 0 and out == "2"

    def test_undefined_name_error(self):
        _, _, rc = clython_run("print(undefined_var)")
        assert rc != 0


class TestSection61Literals:
    """6.1.2: Literal atoms — strings, numbers, booleans, None."""

    def test_string_literal(self):
        out, _, rc = clython_run("print('hello')")
        assert rc == 0 and out == "hello"

    def test_integer_literal(self):
        out, _, rc = clython_run("print(42)")
        assert rc == 0 and out == "42"

    def test_float_literal(self):
        out, _, rc = clython_run("print(3.14)")
        assert rc == 0 and out == "3.14"

    def test_boolean_literals(self):
        out, _, rc = clython_run("print(True, False)")
        assert rc == 0 and out == "True False"

    def test_none_literal(self):
        out, _, rc = clython_run("print(None)")
        assert rc == 0 and out == "None"


class TestSection61Displays:
    """6.1.3–6.1.5: Container displays (list, set, dict)."""

    def test_list_display_empty(self):
        out, _, rc = clython_run("print([])")
        assert rc == 0 and out == "[]"

    def test_list_display(self):
        out, _, rc = clython_run("print([1, 2, 3])")
        assert rc == 0 and out == "[1, 2, 3]"

    def test_set_display(self):
        out, _, rc = clython_run("print({1})")
        assert rc == 0 and out == "{1}"

    def test_dict_display_empty(self):
        out, _, rc = clython_run("print({})")
        assert rc == 0 and out == "{}"

    def test_dict_display(self):
        out, _, rc = clython_run("print({'a': 1, 'b': 2})")
        assert rc == 0 and out == "{'a': 1, 'b': 2}"

    def test_tuple_display(self):
        out, _, rc = clython_run("print((1, 2, 3))")
        assert rc == 0 and out == "(1, 2, 3)"

    def test_nested_containers(self):
        out, _, rc = clython_run("print([1, [2, 3], [4]])")
        assert rc == 0 and out == "[1, [2, 3], [4]]"


class TestSection61Comprehensions:
    """6.1.3: List/set/dict comprehensions."""

    def test_list_comprehension(self):
        out, _, rc = clython_run("print([x * 2 for x in [1, 2, 3]])")
        assert rc == 0 and out == "[2, 4, 6]"

    def test_list_comprehension_with_filter(self):
        out, _, rc = clython_run("print([x for x in [1, 2, 3, 4, 5] if x > 2])")
        assert rc == 0 and out == "[3, 4, 5]"

    def test_set_comprehension(self):
        out, _, rc = clython_run("print(len({x % 3 for x in range(10)}))")
        assert rc == 0 and out == "3"

    def test_dict_comprehension(self):
        out, _, rc = clython_run("d = {k: v for k, v in [('a', 1), ('b', 2)]}\nprint(d['a'], d['b'])")
        assert rc == 0 and out == "1 2"


# ─── 6.3: Primaries ───


class TestSection63AttributeRefs:
    """6.3.1: Attribute references."""

    def test_string_method(self):
        out, _, rc = clython_run("print('hello'.upper())")
        assert rc == 0 and out == "HELLO"

    def test_list_method_append(self):
        out, _, rc = clython_run("x = [1, 2]\nx.append(3)\nprint(x)")
        assert rc == 0 and out == "[1, 2, 3]"


class TestSection63Subscriptions:
    """6.3.2: Subscriptions."""

    def test_list_index(self):
        out, _, rc = clython_run("print([10, 20, 30][1])")
        assert rc == 0 and out == "20"

    def test_list_negative_index(self):
        out, _, rc = clython_run("print([10, 20, 30][-1])")
        assert rc == 0 and out == "30"

    def test_dict_subscription(self):
        out, _, rc = clython_run("d = {'a': 1}\nprint(d['a'])")
        assert rc == 0 and out == "1"

    def test_string_index(self):
        out, _, rc = clython_run("print('hello'[0])")
        assert rc == 0 and out == "h"

    def test_index_out_of_range(self):
        _, _, rc = clython_run("print([1, 2][5])")
        assert rc != 0


class TestSection63Slicings:
    """6.3.3: Slicings."""

    def test_basic_slice(self):
        out, _, rc = clython_run("print([1, 2, 3, 4, 5][1:3])")
        assert rc == 0 and out == "[2, 3]"

    def test_slice_from_start(self):
        out, _, rc = clython_run("print([1, 2, 3, 4, 5][:3])")
        assert rc == 0 and out == "[1, 2, 3]"

    def test_slice_to_end(self):
        out, _, rc = clython_run("print([1, 2, 3, 4, 5][2:])")
        assert rc == 0 and out == "[3, 4, 5]"

    def test_slice_with_step(self):
        out, _, rc = clython_run("print([1, 2, 3, 4, 5][::2])")
        assert rc == 0 and out == "[1, 3, 5]"

    def test_slice_negative(self):
        out, _, rc = clython_run("print([1, 2, 3, 4, 5][-2:])")
        assert rc == 0 and out == "[4, 5]"

    def test_slice_reverse(self):
        out, _, rc = clython_run("print([1, 2, 3][::-1])")
        assert rc == 0 and out == "[3, 2, 1]"

    def test_string_slice(self):
        out, _, rc = clython_run("print('hello'[1:4])")
        assert rc == 0 and out == "ell"


class TestSection63Calls:
    """6.3.4: Calls."""

    def test_builtin_call(self):
        out, _, rc = clython_run("print(len([1, 2, 3]))")
        assert rc == 0 and out == "3"

    def test_function_call(self):
        out, _, rc = clython_run("def f(x): return x + 1\nprint(f(5))")
        assert rc == 0 and out == "6"

    def test_keyword_argument(self):
        out, _, rc = clython_run("print('a', 'b', sep='-')")
        assert rc == 0 and out == "a-b"

    def test_multiple_args(self):
        out, _, rc = clython_run("def add(a, b): return a + b\nprint(add(3, 4))")
        assert rc == 0 and out == "7"

    def test_default_argument(self):
        out, _, rc = clython_run("def greet(name='world'): return 'hello ' + name\nprint(greet())")
        assert rc == 0 and out == "hello world"

    def test_star_args(self):
        out, _, rc = clython_run("def f(*args): return len(args)\nprint(f(1, 2, 3))")
        assert rc == 0 and out == "3"


# ─── 6.5: Power Operator ───


class TestSection65Power:
    """6.5: The power operator **."""

    def test_integer_power(self):
        out, _, rc = clython_run("print(2 ** 10)")
        assert rc == 0 and out == "1024"

    def test_float_power(self):
        out, _, rc = clython_run("print(4.0 ** 0.5)")
        assert rc == 0 and out == "2.0"

    def test_negative_base(self):
        out, _, rc = clython_run("print((-2) ** 3)")
        assert rc == 0 and out == "-8"

    def test_zero_exponent(self):
        out, _, rc = clython_run("print(999 ** 0)")
        assert rc == 0 and out == "1"

    def test_power_precedence(self):
        """** is right-associative and binds tighter than unary -."""
        out, _, rc = clython_run("print(-2 ** 2)")
        assert rc == 0 and out == "-4"


# ─── 6.6: Unary Operators ───


class TestSection66Unary:
    """6.6: Unary arithmetic and bitwise operators."""

    def test_unary_minus(self):
        out, _, rc = clython_run("print(-42)")
        assert rc == 0 and out == "-42"

    def test_unary_plus(self):
        out, _, rc = clython_run("print(+42)")
        assert rc == 0 and out == "42"

    def test_bitwise_not(self):
        out, _, rc = clython_run("print(~0)")
        assert rc == 0 and out == "-1"

    def test_not_operator(self):
        out, _, rc = clython_run("print(not True)")
        assert rc == 0 and out == "False"

    def test_not_falsy(self):
        out, _, rc = clython_run("print(not 0)")
        assert rc == 0 and out == "True"


# ─── 6.7: Binary Arithmetic ───


class TestSection67Arithmetic:
    """6.7: Binary arithmetic operations."""

    def test_addition(self):
        out, _, rc = clython_run("print(1 + 2)")
        assert rc == 0 and out == "3"

    def test_subtraction(self):
        out, _, rc = clython_run("print(10 - 7)")
        assert rc == 0 and out == "3"

    def test_multiplication(self):
        out, _, rc = clython_run("print(6 * 7)")
        assert rc == 0 and out == "42"

    def test_true_division(self):
        out, _, rc = clython_run("print(7 / 2)")
        assert rc == 0 and out == "3.5"

    def test_floor_division(self):
        out, _, rc = clython_run("print(7 // 2)")
        assert rc == 0 and out == "3"

    def test_modulo(self):
        out, _, rc = clython_run("print(10 % 3)")
        assert rc == 0 and out == "1"

    def test_string_multiplication(self):
        out, _, rc = clython_run("print('ab' * 3)")
        assert rc == 0 and out == "ababab"

    def test_list_concatenation(self):
        out, _, rc = clython_run("print([1] + [2, 3])")
        assert rc == 0 and out == "[1, 2, 3]"

    def test_list_repetition(self):
        out, _, rc = clython_run("print([0] * 3)")
        assert rc == 0 and out == "[0, 0, 0]"

    def test_division_by_zero(self):
        _, _, rc = clython_run("print(1 / 0)")
        assert rc != 0

    def test_precedence(self):
        out, _, rc = clython_run("print(2 + 3 * 4)")
        assert rc == 0 and out == "14"

    def test_parentheses_override_precedence(self):
        out, _, rc = clython_run("print((2 + 3) * 4)")
        assert rc == 0 and out == "20"


# ─── 6.8: Shifting Operations ───


class TestSection68Shifting:
    """6.8: Shifting operations."""

    def test_left_shift(self):
        out, _, rc = clython_run("print(1 << 8)")
        assert rc == 0 and out == "256"

    def test_right_shift(self):
        out, _, rc = clython_run("print(256 >> 4)")
        assert rc == 0 and out == "16"


# ─── 6.9: Binary Bitwise ───


class TestSection69Bitwise:
    """6.9: Binary bitwise operations."""

    def test_and(self):
        out, _, rc = clython_run("print(0xFF & 0x0F)")
        assert rc == 0 and out == "15"

    def test_or(self):
        out, _, rc = clython_run("print(0xF0 | 0x0F)")
        assert rc == 0 and out == "255"

    def test_xor(self):
        out, _, rc = clython_run("print(0xFF ^ 0x0F)")
        assert rc == 0 and out == "240"


# ─── 6.10: Comparisons ───


class TestSection610Comparisons:
    """6.10: Comparison operations."""

    def test_less_than(self):
        out, _, rc = clython_run("print(1 < 2)")
        assert rc == 0 and out == "True"

    def test_greater_than(self):
        out, _, rc = clython_run("print(2 > 1)")
        assert rc == 0 and out == "True"

    def test_equal(self):
        out, _, rc = clython_run("print(1 == 1)")
        assert rc == 0 and out == "True"

    def test_not_equal(self):
        out, _, rc = clython_run("print(1 != 2)")
        assert rc == 0 and out == "True"

    def test_less_equal(self):
        out, _, rc = clython_run("print(2 <= 2)")
        assert rc == 0 and out == "True"

    def test_greater_equal(self):
        out, _, rc = clython_run("print(3 >= 2)")
        assert rc == 0 and out == "True"

    def test_chained_comparison(self):
        out, _, rc = clython_run("print(1 < 2 < 3)")
        assert rc == 0 and out == "True"

    def test_chained_comparison_false(self):
        out, _, rc = clython_run("print(1 < 2 > 3)")
        assert rc == 0 and out == "False"

    def test_is_none(self):
        out, _, rc = clython_run("print(None is None)")
        assert rc == 0 and out == "True"

    def test_is_not(self):
        out, _, rc = clython_run("print(1 is not None)")
        assert rc == 0 and out == "True"

    def test_in_list(self):
        out, _, rc = clython_run("print(2 in [1, 2, 3])")
        assert rc == 0 and out == "True"

    def test_not_in_list(self):
        out, _, rc = clython_run("print(4 not in [1, 2, 3])")
        assert rc == 0 and out == "True"

    def test_in_string(self):
        out, _, rc = clython_run("print('ell' in 'hello')")
        assert rc == 0 and out == "True"

    def test_in_dict(self):
        out, _, rc = clython_run("print('a' in {'a': 1, 'b': 2})")
        assert rc == 0 and out == "True"


# ─── 6.11: Boolean Operations ───


class TestSection611Boolean:
    """6.11: Boolean operations (and, or, not)."""

    def test_and_true(self):
        out, _, rc = clython_run("print(True and True)")
        assert rc == 0 and out == "True"

    def test_and_false(self):
        out, _, rc = clython_run("print(True and False)")
        assert rc == 0 and out == "False"

    def test_or_true(self):
        out, _, rc = clython_run("print(False or True)")
        assert rc == 0 and out == "True"

    def test_or_false(self):
        out, _, rc = clython_run("print(False or False)")
        assert rc == 0 and out == "False"

    def test_and_short_circuit(self):
        """and returns first falsy value or last value."""
        out, _, rc = clython_run("print(0 and 5)")
        assert rc == 0 and out == "0"

    def test_or_short_circuit(self):
        """or returns first truthy value or last value."""
        out, _, rc = clython_run("print(0 or 5)")
        assert rc == 0 and out == "5"

    def test_not_true(self):
        out, _, rc = clython_run("print(not True)")
        assert rc == 0 and out == "False"

    def test_not_false(self):
        out, _, rc = clython_run("print(not False)")
        assert rc == 0 and out == "True"

    def test_not_zero(self):
        out, _, rc = clython_run("print(not 0)")
        assert rc == 0 and out == "True"

    def test_not_empty_list(self):
        out, _, rc = clython_run("print(not [])")
        assert rc == 0 and out == "True"

    def test_boolean_precedence(self):
        """not > and > or."""
        out, _, rc = clython_run("print(True or False and False)")
        assert rc == 0 and out == "True"


# ─── 6.12: Walrus Operator ───


class TestSection612Walrus:
    """6.12: Assignment expressions (:=)."""

    def test_walrus_in_if(self):
        out, _, rc = clython_run("x = [1, 2, 3]\nif (n := len(x)) > 2:\n    print(n)")
        assert rc == 0 and out == "3"

    def test_walrus_in_while(self):
        src = "data = [1, 2, 0, 3]\ni = 0\nwhile (val := data[i]) != 0:\n    print(val)\n    i += 1"
        out, _, rc = clython_run(src)
        assert rc == 0 and out == "1\n2"


# ─── 6.13: Conditional Expressions ───


class TestSection613Conditional:
    """6.13: Conditional expressions (ternary)."""

    def test_ternary_true(self):
        out, _, rc = clython_run("print('yes' if True else 'no')")
        assert rc == 0 and out == "yes"

    def test_ternary_false(self):
        out, _, rc = clython_run("print('yes' if False else 'no')")
        assert rc == 0 and out == "no"

    def test_ternary_with_expression(self):
        out, _, rc = clython_run("x = 5\nprint('big' if x > 3 else 'small')")
        assert rc == 0 and out == "big"

    def test_nested_ternary(self):
        out, _, rc = clython_run("x = 0\nprint('pos' if x > 0 else 'neg' if x < 0 else 'zero')")
        assert rc == 0 and out == "zero"


# ─── 6.14: Lambdas ───


class TestSection614Lambdas:
    """6.14: Lambda expressions."""

    def test_simple_lambda(self):
        out, _, rc = clython_run("f = lambda x: x + 1\nprint(f(5))")
        assert rc == 0 and out == "6"

    def test_lambda_multiple_args(self):
        out, _, rc = clython_run("f = lambda x, y: x * y\nprint(f(3, 4))")
        assert rc == 0 and out == "12"

    def test_lambda_no_args(self):
        out, _, rc = clython_run("f = lambda: 42\nprint(f())")
        assert rc == 0 and out == "42"

    def test_lambda_default_arg(self):
        out, _, rc = clython_run("f = lambda x, y=10: x + y\nprint(f(5))")
        assert rc == 0 and out == "15"

    def test_lambda_in_expression(self):
        out, _, rc = clython_run("print((lambda x: x ** 2)(7))")
        assert rc == 0 and out == "49"


# ─── 6.15: Expression Lists ───


class TestSection615ExpressionLists:
    """6.15: Expression lists (tuple packing)."""

    def test_tuple_packing(self):
        out, _, rc = clython_run("x = 1, 2, 3\nprint(x)")
        assert rc == 0 and out == "(1, 2, 3)"

    def test_tuple_unpacking(self):
        out, _, rc = clython_run("a, b, c = 1, 2, 3\nprint(a, b, c)")
        assert rc == 0 and out == "1 2 3"

    def test_swap(self):
        out, _, rc = clython_run("a, b = 1, 2\na, b = b, a\nprint(a, b)")
        assert rc == 0 and out == "2 1"
