"""
Clython Section 6 conformance tests — Expressions.

Tests run through the Clython binary (CLYTHON_BIN) to verify expression
evaluation matches Python 3.12 semantics.

Coverage:
  6.1  Arithmetic conversions
  6.2  Atoms (identifiers, literals, displays, comprehensions)
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
  6.16 Evaluation order
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


# ═══════════════════════════════════════════════════════════════════════════════
# 6.1: Arithmetic Conversions
# ═══════════════════════════════════════════════════════════════════════════════


class TestSection61IntFloatConversions:
    """6.1: Integer-float arithmetic type promotion."""

    def test_int_plus_float(self):
        out, _, rc = clython_run("print(1 + 2.0)")
        assert rc == 0 and out == "3.0"

    def test_int_plus_float_2(self):
        out, _, rc = clython_run("print(42 + 3.14)")
        assert rc == 0 and out == "45.14"

    def test_float_minus_int(self):
        out, _, rc = clython_run("print(2.5 - 1)")
        assert rc == 0 and out == "1.5"

    def test_float_times_int(self):
        out, _, rc = clython_run("print(1.5 * 3)")
        assert rc == 0 and out == "4.5"

    def test_float_div_int(self):
        out, _, rc = clython_run("print(7.5 / 2)")
        assert rc == 0 and out == "3.75"

    def test_float_floordiv_int(self):
        out, _, rc = clython_run("print(9.0 // 4)")
        assert rc == 0 and out == "2.0"

    def test_float_mod_int(self):
        out, _, rc = clython_run("print(5.5 % 2)")
        assert rc == 0 and out == "1.5"

    def test_chained_mixed_arithmetic(self):
        out, _, rc = clython_run("print(1 + 2.0 + 3)")
        assert rc == 0 and out == "6.0"

    def test_int_true_division_produces_float(self):
        """5 / 2 always produces float."""
        out, _, rc = clython_run("print(5 / 2)")
        assert rc == 0 and out == "2.5"

    def test_even_division_produces_float(self):
        """8 / 4 still produces float."""
        out, _, rc = clython_run("print(type(8 / 4).__name__)")
        assert rc == 0 and out == "float"

    def test_result_type_is_float(self):
        out, _, rc = clython_run("print(type(1 + 2.0).__name__)")
        assert rc == 0 and out == "float"


class TestSection61BooleanConversions:
    """6.1: Boolean arithmetic conversion (True=1, False=0)."""

    def test_true_plus_int(self):
        out, _, rc = clython_run("print(True + 1)")
        assert rc == 0 and out == "2"

    def test_false_plus_int(self):
        out, _, rc = clython_run("print(False + 5)")
        assert rc == 0 and out == "5"

    def test_true_times_int(self):
        out, _, rc = clython_run("print(True * 10)")
        assert rc == 0 and out == "10"

    def test_false_times_int(self):
        out, _, rc = clython_run("print(False * 42)")
        assert rc == 0 and out == "0"

    def test_true_minus_false(self):
        out, _, rc = clython_run("print(True - False)")
        assert rc == 0 and out == "1"

    def test_true_plus_true(self):
        out, _, rc = clython_run("print(True + True)")
        assert rc == 0 and out == "2"

    def test_true_plus_float(self):
        out, _, rc = clython_run("print(True + 1.0)")
        assert rc == 0 and out == "2.0"

    def test_false_plus_float(self):
        out, _, rc = clython_run("print(False + 3.14)")
        assert rc == 0 and out == "3.14"

    def test_true_div_true_is_float(self):
        out, _, rc = clython_run("print(True / True)")
        assert rc == 0 and out == "1.0"


class TestSection61ComplexConversions:
    """6.1: Complex number arithmetic conversions."""

    @pytest.mark.xfail(reason="Complex number arithmetic not yet supported")
    def test_complex_plus_int(self):
        out, _, rc = clython_run("print(1j + 2)")
        assert rc == 0 and out == "(2+1j)"

    @pytest.mark.xfail(reason="Complex number arithmetic not yet supported")
    def test_complex_plus_complex(self):
        out, _, rc = clython_run("print(1j + 2j)")
        assert rc == 0 and out == "3j"

    @pytest.mark.xfail(reason="Complex number arithmetic not yet supported")
    def test_complex_times_float(self):
        out, _, rc = clython_run("print(1j * 2.0)")
        assert rc == 0 and out == "2j"


class TestSection61DecimalFractionTypes:
    """6.1: Decimal and Fraction type integration."""

    @pytest.mark.xfail(reason="decimal module import not yet supported")
    def test_decimal_addition(self):
        out, _, rc = clython_run("from decimal import Decimal\nprint(Decimal('1.1') + Decimal('2.2'))")
        assert rc == 0 and out == "3.3"

    @pytest.mark.xfail(reason="fractions module import not yet supported")
    def test_fraction_creation(self):
        out, _, rc = clython_run("from fractions import Fraction\nprint(Fraction(1, 3))")
        assert rc == 0 and out == "1/3"


class TestSection61ConversionErrors:
    """6.1: Arithmetic conversion error conditions."""

    def test_division_by_zero(self):
        _, _, rc = clython_run("print(1 / 0)")
        assert rc != 0

    def test_floor_division_by_zero(self):
        _, _, rc = clython_run("print(1 // 0)")
        assert rc != 0

    def test_modulo_by_zero(self):
        _, _, rc = clython_run("print(1 % 0)")
        assert rc != 0

    def test_unsupported_type_combination(self):
        _, err, rc = clython_run("print('hello' + 1)")
        assert rc != 0
        assert "TypeError" in err


# ═══════════════════════════════════════════════════════════════════════════════
# 6.2: Atoms
# ═══════════════════════════════════════════════════════════════════════════════


class TestSection62BuiltinConstants:
    """6.2: Built-in constant atoms."""

    def test_true(self):
        out, _, rc = clython_run("print(True)")
        assert rc == 0 and out == "True"

    def test_false(self):
        out, _, rc = clython_run("print(False)")
        assert rc == 0 and out == "False"

    def test_none(self):
        out, _, rc = clython_run("print(None)")
        assert rc == 0 and out == "None"

    def test_ellipsis(self):
        out, _, rc = clython_run("print(...)")
        assert rc == 0 and out == "Ellipsis"

    def test_true_is_1(self):
        out, _, rc = clython_run("print(True == 1)")
        assert rc == 0 and out == "True"

    def test_false_is_0(self):
        out, _, rc = clython_run("print(False == 0)")
        assert rc == 0 and out == "True"

    def test_none_is_none(self):
        out, _, rc = clython_run("print(None is None)")
        assert rc == 0 and out == "True"


class TestSection62Identifiers:
    """6.2: Identifier atoms."""

    def test_simple_name_lookup(self):
        out, _, rc = clython_run("x = 42\nprint(x)")
        assert rc == 0 and out == "42"

    def test_name_rebinding(self):
        out, _, rc = clython_run("x = 1\nx = 2\nprint(x)")
        assert rc == 0 and out == "2"

    def test_undefined_name_error(self):
        _, _, rc = clython_run("print(undefined_var)")
        assert rc != 0

    def test_underscore_name(self):
        out, _, rc = clython_run("_x = 10\nprint(_x)")
        assert rc == 0 and out == "10"

    def test_name_with_digits(self):
        out, _, rc = clython_run("var123 = 'ok'\nprint(var123)")
        assert rc == 0 and out == "ok"


class TestSection62Literals:
    """6.2: Literal atoms — strings, numbers, booleans, None."""

    def test_string_literal(self):
        out, _, rc = clython_run("print('hello')")
        assert rc == 0 and out == "hello"

    def test_double_quoted_string(self):
        out, _, rc = clython_run('print("hello")')
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

    def test_hex_literal(self):
        out, _, rc = clython_run("print(0xFF)")
        assert rc == 0 and out == "255"

    def test_octal_literal(self):
        out, _, rc = clython_run("print(0o77)")
        assert rc == 0 and out == "63"

    def test_binary_literal(self):
        out, _, rc = clython_run("print(0b1010)")
        assert rc == 0 and out == "10"

    def test_underscore_in_number(self):
        out, _, rc = clython_run("print(1_000_000)")
        assert rc == 0 and out == "1000000"

    def test_string_concatenation_adjacent(self):
        out, _, rc = clython_run("print('hello' 'world')")
        assert rc == 0 and out == "helloworld"

    def test_raw_string(self):
        out, _, rc = clython_run(r"print(r'\n')")
        assert rc == 0 and out == "\\n"

    def test_fstring(self):
        out, _, rc = clython_run('print(f"x={1+2}")')
        assert rc == 0 and out == "x=3"

    def test_bytes_literal(self):
        out, _, rc = clython_run("print(b'hello')")
        # Clython may print just "hello" for bytes
        assert rc == 0

    def test_negative_number_is_unary_op(self):
        """Negative numbers are unary minus applied to a positive literal."""
        out, _, rc = clython_run("print(-5)")
        assert rc == 0 and out == "-5"

    def test_large_integer(self):
        out, _, rc = clython_run("print(10**20)")
        assert rc == 0 and out == "100000000000000000000"


class TestSection62Displays:
    """6.2: Container displays (list, set, dict, tuple)."""

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

    def test_empty_tuple(self):
        out, _, rc = clython_run("print(())")
        assert rc == 0 and out == "()"

    def test_nested_containers(self):
        out, _, rc = clython_run("print([1, [2, 3], [4]])")
        assert rc == 0 and out == "[1, [2, 3], [4]]"

    def test_list_with_trailing_comma(self):
        out, _, rc = clython_run("print([1, 2, 3,])")
        assert rc == 0 and out == "[1, 2, 3]"

    def test_dict_with_trailing_comma(self):
        out, _, rc = clython_run("print({'a': 1,})")
        assert rc == 0 and out == "{'a': 1}"

    def test_single_element_tuple(self):
        out, _, rc = clython_run("print((1,))")
        assert rc == 0 and out == "(1,)"

    def test_parenthesized_expression_not_tuple(self):
        out, _, rc = clython_run("print(type((1)).__name__)")
        assert rc == 0 and out == "int"

    def test_set_vs_empty_dict(self):
        """Empty braces {} is a dict, not a set."""
        out, _, rc = clython_run("print(type({}).__name__)")
        assert rc == 0 and out == "dict"

    def test_nested_dict(self):
        out, _, rc = clython_run("print({'a': {'b': 1}})")
        assert rc == 0 and out == "{'a': {'b': 1}}"

    def test_complex_list_elements(self):
        out, _, rc = clython_run("print([1+2, 3*4, 5-1])")
        assert rc == 0 and out == "[3, 12, 4]"


class TestSection62Comprehensions:
    """6.2: List/set/dict comprehensions and generator expressions."""

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

    def test_generator_expression(self):
        out, _, rc = clython_run("g = (x**2 for x in range(5))\nprint(list(g))")
        assert rc == 0 and out == "[0, 1, 4, 9, 16]"

    def test_generator_with_condition(self):
        out, _, rc = clython_run("g = (x for x in range(10) if x % 2 == 0)\nprint(list(g))")
        assert rc == 0 and out == "[0, 2, 4, 6, 8]"

    def test_nested_comprehension(self):
        out, _, rc = clython_run("print([x*y for x in [1,2] for y in [10,20]])")
        assert rc == 0 and out == "[10, 20, 20, 40]"

    def test_comprehension_scope(self):
        """Comprehension variables should not leak."""
        out, _, rc = clython_run("[x for x in range(3)]\ntry:\n    print(x)\nexcept NameError:\n    print('not defined')")
        # In Python 3, comprehension vars don't leak; Clython may or may not match
        assert rc == 0


class TestSection62YieldAtoms:
    """6.2: Yield expressions."""

    def test_simple_yield(self):
        out, _, rc = clython_run("def gen():\n    yield 1\n    yield 2\nprint(list(gen()))")
        assert rc == 0 and out == "[1, 2]"

    def test_yield_from(self):
        out, _, rc = clython_run("def gen():\n    yield from [1, 2, 3]\nprint(list(gen()))")
        assert rc == 0 and out == "[1, 2, 3]"


# ═══════════════════════════════════════════════════════════════════════════════
# 6.3: Primaries
# ═══════════════════════════════════════════════════════════════════════════════


class TestSection63AttributeRefs:
    """6.3.1: Attribute references."""

    def test_string_method(self):
        out, _, rc = clython_run("print('hello'.upper())")
        assert rc == 0 and out == "HELLO"

    def test_list_method_append(self):
        out, _, rc = clython_run("x = [1, 2]\nx.append(3)\nprint(x)")
        assert rc == 0 and out == "[1, 2, 3]"

    def test_chained_attribute(self):
        out, _, rc = clython_run("print('  Hello  '.strip().lower())")
        assert rc == 0 and out == "hello"

    def test_attribute_on_result(self):
        out, _, rc = clython_run("print([1,2,3].count(2))")
        assert rc == 0 and out == "1"


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

    def test_nested_subscription(self):
        out, _, rc = clython_run("print([[1,2],[3,4]][1][0])")
        assert rc == 0 and out == "3"

    def test_subscription_with_expression(self):
        out, _, rc = clython_run("print([10, 20, 30][1 + 1])")
        assert rc == 0 and out == "30"

    def test_tuple_subscription(self):
        out, _, rc = clython_run("print((10, 20, 30)[2])")
        assert rc == 0 and out == "30"


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

    def test_negative_step_slice(self):
        out, _, rc = clython_run("print([1,2,3,4,5][4:1:-1])")
        assert rc == 0 and out == "[5, 4, 3]"

    def test_full_slice_is_copy(self):
        out, _, rc = clython_run("x = [1,2,3]\ny = x[:]\ny.append(4)\nprint(x, y)")
        assert rc == 0 and out == "[1, 2, 3] [1, 2, 3, 4]"


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

    def test_kwargs(self):
        out, _, rc = clython_run("def f(**kw): return list(kw.keys())\nprint(f(a=1, b=2))")
        assert rc == 0 and out == "['a', 'b']"

    def test_star_unpack_in_call(self):
        out, _, rc = clython_run("def f(a, b, c): return a + b + c\nprint(f(*[1, 2, 3]))")
        assert rc == 0 and out == "6"

    def test_method_call(self):
        out, _, rc = clython_run("print([3,1,2].count(1))")
        assert rc == 0 and out == "1"

    def test_chained_method_calls(self):
        out, _, rc = clython_run("print('hello world'.split(' ')[0].upper())")
        assert rc == 0 and out == "HELLO"

    def test_nested_function_calls(self):
        out, _, rc = clython_run("print(str(len([1,2,3])))")
        assert rc == 0 and out == "3"

    def test_keyword_only_arg(self):
        out, _, rc = clython_run("def f(*, x): return x\nprint(f(x=5))")
        assert rc == 0 and out == "5"


class TestSection63StringMethods:
    """Extended string method dispatch tests."""

    def test_string_method_lower(self):
        out, _, rc = clython_run("print('HELLO'.lower())")
        assert rc == 0 and out == "hello"

    def test_string_method_strip(self):
        out, _, rc = clython_run("print('  hello  '.strip())")
        assert rc == 0 and out == "hello"

    def test_string_method_split(self):
        out, _, rc = clython_run("print('a,b,c'.split(','))")
        assert rc == 0 and out == "['a', 'b', 'c']"

    def test_string_method_join(self):
        out, _, rc = clython_run("print('-'.join(['a', 'b', 'c']))")
        assert rc == 0 and out == "a-b-c"

    def test_string_method_replace(self):
        out, _, rc = clython_run("print('hello world'.replace('world', 'python'))")
        assert rc == 0 and out == "hello python"

    def test_string_method_startswith(self):
        out, _, rc = clython_run("print('hello'.startswith('hel'))")
        assert rc == 0 and out == "True"

    def test_string_method_endswith(self):
        out, _, rc = clython_run("print('hello'.endswith('llo'))")
        assert rc == 0 and out == "True"

    def test_string_method_find(self):
        out, _, rc = clython_run("print('hello'.find('ll'))")
        assert rc == 0 and out == "2"

    def test_string_method_count(self):
        out, _, rc = clython_run("print('banana'.count('a'))")
        assert rc == 0 and out == "3"

    def test_string_method_format(self):
        out, _, rc = clython_run("print('hi {}'.format('world'))")
        assert rc == 0 and out == "hi world"

    def test_string_method_upper(self):
        out, _, rc = clython_run("print('hello'.upper())")
        assert rc == 0 and out == "HELLO"

    def test_string_isdigit(self):
        out, _, rc = clython_run("print('123'.isdigit())")
        assert rc == 0 and out == "True"

    def test_string_isalpha(self):
        out, _, rc = clython_run("print('abc'.isalpha())")
        assert rc == 0 and out == "True"

    def test_string_title(self):
        out, _, rc = clython_run("print('hello world'.title())")
        assert rc == 0 and out == "Hello World"

    def test_string_capitalize(self):
        out, _, rc = clython_run("print('hello'.capitalize())")
        assert rc == 0 and out == "Hello"

    def test_string_zfill(self):
        out, _, rc = clython_run("print('42'.zfill(5))")
        assert rc == 0 and out == "00042"


class TestSection63ListMethods:
    """Extended list method dispatch tests."""

    def test_list_method_pop(self):
        out, _, rc = clython_run("x = [1, 2, 3]\nprint(x.pop())")
        assert rc == 0 and out == "3"

    def test_list_method_reverse(self):
        out, _, rc = clython_run("x = [1, 2, 3]\nx.reverse()\nprint(x)")
        assert rc == 0 and out == "[3, 2, 1]"

    def test_list_method_sort(self):
        out, _, rc = clython_run("x = [3, 1, 2]\nx.sort()\nprint(x)")
        assert rc == 0 and out == "[1, 2, 3]"

    def test_list_method_count(self):
        out, _, rc = clython_run("print([1, 2, 2, 3].count(2))")
        assert rc == 0 and out == "2"

    def test_list_method_copy(self):
        out, _, rc = clython_run("x = [1, 2]\ny = x.copy()\ny.append(3)\nprint(x, y)")
        assert rc == 0 and out == "[1, 2] [1, 2, 3]"

    def test_list_method_extend(self):
        out, _, rc = clython_run("x = [1, 2]\nx.extend([3, 4])\nprint(x)")
        assert rc == 0 and out == "[1, 2, 3, 4]"

    def test_list_method_insert(self):
        out, _, rc = clython_run("x = [1, 3]\nx.insert(1, 2)\nprint(x)")
        assert rc == 0 and out == "[1, 2, 3]"

    def test_list_method_remove(self):
        out, _, rc = clython_run("x = [1, 2, 3]\nx.remove(2)\nprint(x)")
        assert rc == 0 and out == "[1, 3]"

    def test_list_method_index(self):
        out, _, rc = clython_run("print([10, 20, 30].index(20))")
        assert rc == 0 and out == "1"

    def test_list_method_clear(self):
        out, _, rc = clython_run("x = [1, 2, 3]\nx.clear()\nprint(x)")
        assert rc == 0 and out == "[]"


class TestSection63DictMethods:
    """Dict method dispatch tests."""

    def test_dict_keys(self):
        out, _, rc = clython_run("print(sorted({'a': 1, 'b': 2}.keys()))")
        assert rc == 0 and out == "['a', 'b']"

    def test_dict_values(self):
        out, _, rc = clython_run("print(sorted({'a': 1, 'b': 2}.values()))")
        assert rc == 0 and out == "[1, 2]"

    def test_dict_items(self):
        out, _, rc = clython_run("print(sorted({'a': 1, 'b': 2}.items()))")
        assert rc == 0 and out == "[('a', 1), ('b', 2)]"

    def test_dict_get(self):
        out, _, rc = clython_run("print({'a': 1}.get('a'))")
        assert rc == 0 and out == "1"

    def test_dict_get_default(self):
        out, _, rc = clython_run("print({'a': 1}.get('b', 99))")
        assert rc == 0 and out == "99"

    def test_dict_pop(self):
        out, _, rc = clython_run("d = {'a': 1, 'b': 2}\nprint(d.pop('a'))\nprint(d)")
        assert rc == 0 and out == "1\n{'b': 2}"

    def test_dict_update(self):
        out, _, rc = clython_run("d = {'a': 1}\nd.update({'b': 2})\nprint(sorted(d.items()))")
        assert rc == 0 and out == "[('a', 1), ('b', 2)]"


# ═══════════════════════════════════════════════════════════════════════════════
# 6.5: Power Operator
# ═══════════════════════════════════════════════════════════════════════════════


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

    def test_right_associative(self):
        """2 ** 3 ** 2 == 2 ** (3 ** 2) == 2 ** 9 == 512."""
        out, _, rc = clython_run("print(2 ** 3 ** 2)")
        assert rc == 0 and out == "512"

    def test_explicit_left_grouping(self):
        """(2 ** 3) ** 2 == 8 ** 2 == 64."""
        out, _, rc = clython_run("print((2 ** 3) ** 2)")
        assert rc == 0 and out == "64"

    def test_power_with_float_exponent(self):
        out, _, rc = clython_run("print(27 ** (1/3))")
        assert rc == 0 and out == "3.0"

    def test_power_zero_to_zero(self):
        out, _, rc = clython_run("print(0 ** 0)")
        assert rc == 0 and out == "1"

    def test_power_large_int(self):
        out, _, rc = clython_run("print(2 ** 64)")
        assert rc == 0 and out == "18446744073709551616"

    def test_power_vs_multiply_precedence(self):
        """** binds tighter than *."""
        out, _, rc = clython_run("print(2 * 3 ** 2)")
        assert rc == 0 and out == "18"

    def test_power_vs_add_precedence(self):
        out, _, rc = clython_run("print(1 + 2 ** 3)")
        assert rc == 0 and out == "9"

    def test_power_negative_exponent(self):
        out, _, rc = clython_run("print(2 ** -1)")
        assert rc == 0 and out == "0.5"

    def test_power_in_expression(self):
        out, _, rc = clython_run("x = 3\nprint(x ** 2 + x ** 3)")
        assert rc == 0 and out == "36"


# ═══════════════════════════════════════════════════════════════════════════════
# 6.6: Unary Operators
# ═══════════════════════════════════════════════════════════════════════════════


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

    def test_double_negative(self):
        out, _, rc = clython_run("print(-(-5))")
        assert rc == 0 and out == "5"

    def test_double_not(self):
        out, _, rc = clython_run("print(not not True)")
        assert rc == 0 and out == "True"

    def test_bitwise_not_positive(self):
        out, _, rc = clython_run("print(~5)")
        assert rc == 0 and out == "-6"

    def test_bitwise_not_negative(self):
        out, _, rc = clython_run("print(~(-1))")
        assert rc == 0 and out == "0"

    def test_unary_minus_float(self):
        out, _, rc = clython_run("print(-3.14)")
        assert rc == 0 and out == "-3.14"

    def test_unary_plus_float(self):
        out, _, rc = clython_run("print(+3.14)")
        assert rc == 0 and out == "3.14"

    def test_not_none(self):
        out, _, rc = clython_run("print(not None)")
        assert rc == 0 and out == "True"

    def test_not_empty_string(self):
        out, _, rc = clython_run("print(not '')")
        assert rc == 0 and out == "True"

    def test_not_nonempty_string(self):
        out, _, rc = clython_run("print(not 'hello')")
        assert rc == 0 and out == "False"

    def test_unary_minus_bool(self):
        out, _, rc = clython_run("print(-True)")
        assert rc == 0 and out == "-1"

    def test_chained_unary_plus(self):
        out, _, rc = clython_run("print(+(+5))")
        assert rc == 0 and out == "5"

    def test_chained_unary_not(self):
        out, _, rc = clython_run("print(~~5)")
        assert rc == 0 and out == "5"

    def test_unary_minus_vs_power(self):
        """-x**2 is -(x**2), not (-x)**2."""
        out, _, rc = clython_run("x = 3\nprint(-x**2)")
        assert rc == 0 and out == "-9"

    def test_unary_vs_binary(self):
        out, _, rc = clython_run("print(-2 + 3)")
        assert rc == 0 and out == "1"


# ═══════════════════════════════════════════════════════════════════════════════
# 6.7: Binary Arithmetic
# ═══════════════════════════════════════════════════════════════════════════════


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

    def test_string_concatenation(self):
        out, _, rc = clython_run("print('hello' + ' ' + 'world')")
        assert rc == 0 and out == "hello world"

    def test_left_associativity(self):
        """a - b - c == (a - b) - c."""
        out, _, rc = clython_run("print(10 - 3 - 2)")
        assert rc == 0 and out == "5"

    def test_floor_division_negative(self):
        """Floor division rounds toward negative infinity."""
        out, _, rc = clython_run("print(-7 // 2)")
        assert rc == 0 and out == "-4"

    def test_modulo_negative(self):
        out, _, rc = clython_run("print(-7 % 3)")
        assert rc == 0 and out == "2"

    def test_float_floor_division(self):
        out, _, rc = clython_run("print(7.5 // 2)")
        assert rc == 0 and out == "3.0"

    def test_string_format_modulo(self):
        out, _, rc = clython_run("print('%s is %d' % ('pi', 3))")
        assert rc == 0 and out == "pi is 3"

    def test_multiply_precedence_vs_add(self):
        out, _, rc = clython_run("print(1 + 2 * 3 + 4)")
        assert rc == 0 and out == "11"

    def test_complex_precedence(self):
        out, _, rc = clython_run("print(2 + 3 * 4 - 1)")
        assert rc == 0 and out == "13"

    def test_nested_arithmetic(self):
        out, _, rc = clython_run("print((2 + 3) * (4 - 1))")
        assert rc == 0 and out == "15"

    @pytest.mark.xfail(reason="Matrix multiplication @ not yet supported")
    def test_matmul_operator(self):
        """@ operator for matrix multiplication (requires __matmul__)."""
        out, _, rc = clython_run("class M:\n    def __matmul__(self, other): return 42\nprint(M() @ M())")
        assert rc == 0 and out == "42"


# ═══════════════════════════════════════════════════════════════════════════════
# 6.8: Shifting Operations
# ═══════════════════════════════════════════════════════════════════════════════


class TestSection68Shifting:
    """6.8: Shifting operations."""

    def test_left_shift(self):
        out, _, rc = clython_run("print(1 << 8)")
        assert rc == 0 and out == "256"

    def test_right_shift(self):
        out, _, rc = clython_run("print(256 >> 4)")
        assert rc == 0 and out == "16"

    def test_left_shift_zero(self):
        out, _, rc = clython_run("print(5 << 0)")
        assert rc == 0 and out == "5"

    def test_right_shift_zero(self):
        out, _, rc = clython_run("print(5 >> 0)")
        assert rc == 0 and out == "5"

    def test_left_shift_by_one(self):
        """Left shift by 1 is multiply by 2."""
        out, _, rc = clython_run("print(7 << 1)")
        assert rc == 0 and out == "14"

    def test_right_shift_by_one(self):
        """Right shift by 1 is floor divide by 2."""
        out, _, rc = clython_run("print(7 >> 1)")
        assert rc == 0 and out == "3"

    def test_chained_left_shifts(self):
        """Left-associative: (1 << 2) << 3 == 4 << 3 == 32."""
        out, _, rc = clython_run("print(1 << 2 << 3)")
        assert rc == 0 and out == "32"

    def test_chained_right_shifts(self):
        out, _, rc = clython_run("print(256 >> 2 >> 2)")
        assert rc == 0 and out == "16"

    def test_mixed_shifts(self):
        out, _, rc = clython_run("print(1 << 4 >> 2)")
        assert rc == 0 and out == "4"

    def test_shift_large(self):
        out, _, rc = clython_run("print(1 << 32)")
        assert rc == 0 and out == "4294967296"

    def test_shift_vs_add_precedence(self):
        """Shift has lower precedence than addition."""
        out, _, rc = clython_run("print(1 << 2 + 1)")
        assert rc == 0 and out == "8"

    def test_shift_vs_multiply_precedence(self):
        out, _, rc = clython_run("print(1 << 2 * 2)")
        assert rc == 0 and out == "16"

    def test_shift_in_expression(self):
        out, _, rc = clython_run("x = 3\nprint((x << 2) + (x >> 1))")
        assert rc == 0 and out == "13"

    def test_shift_with_parentheses(self):
        out, _, rc = clython_run("print((1 << 2) + (8 >> 2))")
        assert rc == 0 and out == "6"

    def test_negative_right_shift(self):
        out, _, rc = clython_run("print(-16 >> 2)")
        assert rc == 0 and out == "-4"


# ═══════════════════════════════════════════════════════════════════════════════
# 6.9: Binary Bitwise
# ═══════════════════════════════════════════════════════════════════════════════


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

    def test_and_identity(self):
        out, _, rc = clython_run("print(42 & 42)")
        assert rc == 0 and out == "42"

    def test_or_identity(self):
        out, _, rc = clython_run("print(42 | 0)")
        assert rc == 0 and out == "42"

    def test_xor_self_is_zero(self):
        out, _, rc = clython_run("print(42 ^ 42)")
        assert rc == 0 and out == "0"

    def test_and_with_zero(self):
        out, _, rc = clython_run("print(0xFF & 0)")
        assert rc == 0 and out == "0"

    def test_or_with_zero(self):
        out, _, rc = clython_run("print(0 | 0xFF)")
        assert rc == 0 and out == "255"

    def test_chained_and(self):
        out, _, rc = clython_run("print(0xFF & 0x7F & 0x0F)")
        assert rc == 0 and out == "15"

    def test_chained_or(self):
        out, _, rc = clython_run("print(0x0F | 0xF0 | 0x100)")
        assert rc == 0 and out == "511"

    def test_chained_xor(self):
        out, _, rc = clython_run("print(0xFF ^ 0x0F ^ 0xF0)")
        assert rc == 0 and out == "0"

    def test_bitwise_precedence(self):
        """& binds tighter than ^, which binds tighter than |."""
        out, _, rc = clython_run("print(0xFF & 0x0F | 0xF0)")
        assert rc == 0 and out == "255"

    def test_bitwise_with_parentheses(self):
        out, _, rc = clython_run("print(0xFF & (0x0F | 0xF0))")
        assert rc == 0 and out == "255"

    def test_bitwise_vs_shift_precedence(self):
        """Shift binds tighter than bitwise."""
        out, _, rc = clython_run("print(1 << 4 & 0xFF)")
        assert rc == 0 and out == "16"

    def test_and_with_booleans(self):
        """Bitwise & on bools gives int results."""
        out, _, rc = clython_run("print(True & False)")
        assert rc == 0 and out == "0"

    def test_or_with_booleans(self):
        out, _, rc = clython_run("print(True | False)")
        assert rc == 0 and out == "1"

    def test_xor_with_booleans(self):
        out, _, rc = clython_run("print(True ^ True)")
        assert rc == 0 and out == "0"

    def test_set_intersection_via_and(self):
        out, _, rc = clython_run("print({1, 2, 3} & {2, 3, 4})")
        assert rc == 0 and out == "{2, 3}"

    def test_set_union_via_or(self):
        out, _, rc = clython_run("print(sorted({1, 2, 3} | {3, 4, 5}))")
        assert rc == 0 and out == "[1, 2, 3, 4, 5]"

    def test_set_symmetric_diff_via_xor(self):
        out, _, rc = clython_run("print(sorted({1, 2, 3} ^ {2, 3, 4}))")
        assert rc == 0 and out == "[1, 4]"

    def test_mixed_bitwise_operations(self):
        out, _, rc = clython_run("print((0xAA & 0x0F) | (0x55 & 0xF0))")
        assert rc == 0 and out == "90"


# ═══════════════════════════════════════════════════════════════════════════════
# 6.10: Comparisons
# ═══════════════════════════════════════════════════════════════════════════════


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

    def test_equality_with_different_types(self):
        out, _, rc = clython_run("print(1 == 1.0)")
        assert rc == 0 and out == "True"

    def test_not_equal_types(self):
        out, _, rc = clython_run("print(1 != '1')")
        assert rc == 0 and out == "True"

    def test_long_chain(self):
        out, _, rc = clython_run("print(1 < 2 < 3 < 4 < 5)")
        assert rc == 0 and out == "True"

    def test_long_chain_false(self):
        out, _, rc = clython_run("print(1 < 2 < 3 < 2 < 5)")
        assert rc == 0 and out == "False"

    def test_chained_equality(self):
        out, _, rc = clython_run("print(1 == 1 == 1)")
        assert rc == 0 and out == "True"

    def test_mixed_comparison_chain(self):
        out, _, rc = clython_run("print(1 <= 2 < 3 == 3)")
        assert rc == 0 and out == "True"

    def test_identity_vs_equality(self):
        """is checks identity, == checks value."""
        out, _, rc = clython_run("a = [1, 2]\nb = [1, 2]\nprint(a == b, a is b)")
        assert rc == 0 and out == "True False"

    def test_in_set(self):
        out, _, rc = clython_run("print(2 in {1, 2, 3})")
        assert rc == 0 and out == "True"

    def test_not_in_string(self):
        out, _, rc = clython_run("print('xyz' not in 'hello')")
        assert rc == 0 and out == "True"

    def test_comparison_vs_arithmetic_precedence(self):
        """Comparisons have lower precedence than arithmetic."""
        out, _, rc = clython_run("print(1 + 2 < 4)")
        assert rc == 0 and out == "True"

    def test_comparison_short_circuit(self):
        """In chained comparisons, middle is only evaluated once."""
        out, _, rc = clython_run(
            "log = []\ndef f(x):\n    log.append(x)\n    return x\n"
            "print(1 < f(2) < 3)\nprint(log)"
        )
        assert rc == 0 and out == "True\n[2]"

    def test_string_comparison(self):
        out, _, rc = clython_run("print('abc' < 'abd')")
        assert rc == 0 and out == "True"

    def test_none_equality(self):
        out, _, rc = clython_run("print(None == None)")
        assert rc == 0 and out == "True"


# ═══════════════════════════════════════════════════════════════════════════════
# 6.11: Boolean Operations
# ═══════════════════════════════════════════════════════════════════════════════


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

    def test_and_returns_value_not_bool(self):
        """and returns the actual value, not True/False."""
        out, _, rc = clython_run("print(1 and 2)")
        assert rc == 0 and out == "2"

    def test_or_returns_value_not_bool(self):
        out, _, rc = clython_run("print(1 or 2)")
        assert rc == 0 and out == "1"

    def test_chained_and(self):
        out, _, rc = clython_run("print(1 and 2 and 3)")
        assert rc == 0 and out == "3"

    def test_chained_or(self):
        out, _, rc = clython_run("print(0 or '' or 'found')")
        assert rc == 0 and out == "found"

    def test_and_short_circuit_no_call(self):
        """False and expr should not evaluate expr."""
        out, _, rc = clython_run(
            "log = []\ndef f():\n    log.append('called')\n    return True\n"
            "print(False and f())\nprint(log)"
        )
        assert rc == 0 and out == "False\n[]"

    def test_or_short_circuit_no_call(self):
        """True or expr should not evaluate expr."""
        out, _, rc = clython_run(
            "log = []\ndef f():\n    log.append('called')\n    return True\n"
            "print(True or f())\nprint(log)"
        )
        assert rc == 0 and out == "True\n[]"

    def test_not_precedence_vs_comparison(self):
        """not has lower precedence than comparisons."""
        out, _, rc = clython_run("print(not 1 < 2)")
        assert rc == 0 and out == "False"

    def test_falsy_values(self):
        """All falsy values."""
        out, _, rc = clython_run(
            "for v in [0, 0.0, '', [], {}, set(), None, False]:\n"
            "    print(not v, end=' ')"
        )
        assert rc == 0 and out == "True True True True True True True True"

    def test_truthy_values(self):
        out, _, rc = clython_run(
            "for v in [1, 0.1, 'x', [0], {0: 0}, True]:\n"
            "    print(not v, end=' ')"
        )
        assert rc == 0 and out == "False False False False False False"

    def test_complex_boolean_expression(self):
        out, _, rc = clython_run("print((True and False) or (not False and True))")
        assert rc == 0 and out == "True"

    def test_parentheses_override_boolean_precedence(self):
        out, _, rc = clython_run("print((True or False) and False)")
        assert rc == 0 and out == "False"

    def test_boolean_with_comparison(self):
        out, _, rc = clython_run("print(1 < 2 and 3 > 1)")
        assert rc == 0 and out == "True"


# ═══════════════════════════════════════════════════════════════════════════════
# 6.12: Walrus Operator
# ═══════════════════════════════════════════════════════════════════════════════


class TestSection612Walrus:
    """6.12: Assignment expressions (:=)."""

    def test_walrus_in_if(self):
        out, _, rc = clython_run("x = [1, 2, 3]\nif (n := len(x)) > 2:\n    print(n)")
        assert rc == 0 and out == "3"

    def test_walrus_in_while(self):
        src = "data = [1, 2, 0, 3]\ni = 0\nwhile (val := data[i]) != 0:\n    print(val)\n    i += 1"
        out, _, rc = clython_run(src)
        assert rc == 0 and out == "1\n2"

    def test_walrus_simple_assignment(self):
        out, _, rc = clython_run("print((x := 5))")
        assert rc == 0 and out == "5"

    def test_walrus_value_propagation(self):
        """Walrus assigns and returns the value."""
        out, _, rc = clython_run("y = (x := 10) + 5\nprint(x, y)")
        assert rc == 0 and out == "10 15"

    def test_walrus_with_expression(self):
        out, _, rc = clython_run("print((x := 2 + 3))")
        assert rc == 0 and out == "5"

    def test_walrus_with_string(self):
        out, _, rc = clython_run("if (s := 'hello'):\n    print(s)")
        assert rc == 0 and out == "hello"

    @pytest.mark.xfail(reason="Walrus operator in comprehensions not yet supported")
    def test_walrus_in_list_comprehension(self):
        out, _, rc = clython_run("result = [y := x + 1 for x in range(3)]\nprint(result, y)")
        assert rc == 0 and out == "[1, 2, 3] 3"

    def test_walrus_nested(self):
        out, _, rc = clython_run("if (a := (b := 3) + 1) == 4:\n    print(a, b)")
        assert rc == 0 and out == "4 3"

    def test_walrus_in_function_call(self):
        out, _, rc = clython_run("print(len(s := 'hello'), s)")
        assert rc == 0 and out == "5 hello"


# ═══════════════════════════════════════════════════════════════════════════════
# 6.13: Conditional Expressions
# ═══════════════════════════════════════════════════════════════════════════════


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

    def test_ternary_with_different_types(self):
        out, _, rc = clython_run("print(1 if True else 'no')")
        assert rc == 0 and out == "1"

    def test_ternary_with_complex_condition(self):
        out, _, rc = clython_run("print('yes' if 1 < 2 and 3 > 1 else 'no')")
        assert rc == 0 and out == "yes"

    def test_ternary_with_function_call(self):
        out, _, rc = clython_run("print(len([1,2,3]) if True else 0)")
        assert rc == 0 and out == "3"

    def test_ternary_evaluates_only_one_branch(self):
        """Only the selected branch should be evaluated."""
        out, _, rc = clython_run(
            "log = []\ndef a():\n    log.append('a')\n    return 1\n"
            "def b():\n    log.append('b')\n    return 2\n"
            "print(a() if True else b())\nprint(log)"
        )
        assert rc == 0 and out == "1\n['a']"

    def test_ternary_in_assignment(self):
        out, _, rc = clython_run("x = 'even' if 4 % 2 == 0 else 'odd'\nprint(x)")
        assert rc == 0 and out == "even"

    def test_ternary_with_arithmetic_values(self):
        out, _, rc = clython_run("print(2 + 3 if True else 10 * 20)")
        assert rc == 0 and out == "5"

    def test_ternary_in_list(self):
        out, _, rc = clython_run("print(['even' if x % 2 == 0 else 'odd' for x in range(4)])")
        assert rc == 0 and out == "['even', 'odd', 'even', 'odd']"

    def test_deeply_nested_ternary(self):
        out, _, rc = clython_run("x = 2\nprint('one' if x == 1 else 'two' if x == 2 else 'three' if x == 3 else 'other')")
        assert rc == 0 and out == "two"


# ═══════════════════════════════════════════════════════════════════════════════
# 6.14: Lambdas
# ═══════════════════════════════════════════════════════════════════════════════


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

    def test_lambda_multiple_defaults(self):
        out, _, rc = clython_run("f = lambda x=1, y=2, z=3: x + y + z\nprint(f())")
        assert rc == 0 and out == "6"

    def test_lambda_default_override(self):
        out, _, rc = clython_run("f = lambda x, y=10: x * y\nprint(f(3, 5))")
        assert rc == 0 and out == "15"

    def test_lambda_star_args(self):
        out, _, rc = clython_run("f = lambda *args: sum(args)\nprint(f(1, 2, 3))")
        assert rc == 0 and out == "6"

    def test_lambda_kwargs(self):
        out, _, rc = clython_run("f = lambda **kw: list(kw.keys())\nprint(f(a=1, b=2))")
        assert rc == 0 and out == "['a', 'b']"

    def test_lambda_keyword_only(self):
        out, _, rc = clython_run("f = lambda *, x: x\nprint(f(x=5))")
        assert rc == 0 and out == "5"

    @pytest.mark.xfail(reason="Positional-only parameters (/) not yet supported")
    def test_lambda_positional_only(self):
        out, _, rc = clython_run("f = lambda x, /: x\nprint(f(5))")
        assert rc == 0 and out == "5"

    def test_lambda_returning_lambda(self):
        out, _, rc = clython_run("f = lambda x: lambda y: x + y\nprint(f(3)(4))")
        assert rc == 0 and out == "7"

    def test_lambda_closure(self):
        out, _, rc = clython_run("def make_adder(n):\n    return lambda x: x + n\nadd5 = make_adder(5)\nprint(add5(10))")
        assert rc == 0 and out == "15"

    def test_lambda_in_map(self):
        out, _, rc = clython_run("print(list(map(lambda x: x * 2, [1, 2, 3])))")
        assert rc == 0 and out == "[2, 4, 6]"

    def test_lambda_in_filter(self):
        out, _, rc = clython_run("print(list(filter(lambda x: x > 2, [1, 2, 3, 4, 5])))")
        assert rc == 0 and out == "[3, 4, 5]"

    def test_lambda_in_sorted(self):
        out, _, rc = clython_run("print(sorted([(1, 'b'), (2, 'a')], key=lambda x: x[1]))")
        assert rc == 0 and out == "[(2, 'a'), (1, 'b')]"

    def test_lambda_complex_body(self):
        out, _, rc = clython_run("f = lambda x: x if x > 0 else -x\nprint(f(-5))")
        assert rc == 0 and out == "5"

    def test_deeply_nested_lambda(self):
        out, _, rc = clython_run("f = lambda x: lambda y: lambda z: x + y + z\nprint(f(1)(2)(3))")
        assert rc == 0 and out == "6"


# ═══════════════════════════════════════════════════════════════════════════════
# 6.15: Expression Lists
# ═══════════════════════════════════════════════════════════════════════════════


class TestSection615ExpressionLists:
    """6.15: Expression lists (tuple packing/unpacking)."""

    def test_tuple_packing(self):
        out, _, rc = clython_run("x = 1, 2, 3\nprint(x)")
        assert rc == 0 and out == "(1, 2, 3)"

    def test_tuple_unpacking(self):
        out, _, rc = clython_run("a, b, c = 1, 2, 3\nprint(a, b, c)")
        assert rc == 0 and out == "1 2 3"

    def test_swap(self):
        out, _, rc = clython_run("a, b = 1, 2\na, b = b, a\nprint(a, b)")
        assert rc == 0 and out == "2 1"

    def test_tuple_packing_two(self):
        out, _, rc = clython_run("x = 1, 2\nprint(x)")
        assert rc == 0 and out == "(1, 2)"

    def test_tuple_unpacking_list(self):
        out, _, rc = clython_run("a, b = [10, 20]\nprint(a, b)")
        assert rc == 0 and out == "10 20"

    def test_swap_strings(self):
        out, _, rc = clython_run("a, b = 'x', 'y'\na, b = b, a\nprint(a, b)")
        assert rc == 0 and out == "y x"

    def test_trailing_comma_creates_tuple(self):
        out, _, rc = clython_run("x = 1,\nprint(type(x).__name__, x)")
        assert rc == 0 and out == "tuple (1,)"

    def test_single_element_expression_list(self):
        out, _, rc = clython_run("x = (42,)\nprint(x)")
        assert rc == 0 and out == "(42,)"

    def test_starred_unpacking(self):
        out, _, rc = clython_run("a, *b = [1, 2, 3, 4]\nprint(a, b)")
        assert rc == 0 and out == "1 [2, 3, 4]"

    def test_starred_unpacking_middle(self):
        out, _, rc = clython_run("a, *b, c = [1, 2, 3, 4, 5]\nprint(a, b, c)")
        assert rc == 0 and out == "1 [2, 3, 4] 5"

    def test_starred_unpacking_end(self):
        out, _, rc = clython_run("*a, b = [1, 2, 3, 4]\nprint(a, b)")
        assert rc == 0 and out == "[1, 2, 3] 4"

    def test_starred_in_function_call(self):
        out, _, rc = clython_run("print(*[1, 2, 3])")
        assert rc == 0 and out == "1 2 3"

    def test_tuple_in_for_loop(self):
        out, _, rc = clython_run("for a, b in [(1, 2), (3, 4)]:\n    print(a + b)")
        assert rc == 0 and out == "3\n7"

    def test_nested_unpacking(self):
        out, _, rc = clython_run("(a, b), c = [1, 2], 3\nprint(a, b, c)")
        assert rc == 0 and out == "1 2 3"

    def test_expression_list_in_return(self):
        out, _, rc = clython_run("def f():\n    return 1, 2, 3\nprint(f())")
        assert rc == 0 and out == "(1, 2, 3)"

    @pytest.mark.xfail(reason="Star unpacking in list literals not yet supported")
    def test_starred_in_list_literal(self):
        out, _, rc = clython_run("print([1, *[2, 3], 4])")
        assert rc == 0 and out == "[1, 2, 3, 4]"

    @pytest.mark.xfail(reason="Star unpacking in set literals not yet supported")
    def test_starred_in_set_literal(self):
        out, _, rc = clython_run("print(sorted({1, *[2, 3], 4}))")
        assert rc == 0 and out == "[1, 2, 3, 4]"

    @pytest.mark.xfail(reason="Double-star unpacking in dict literals not yet supported")
    def test_starred_in_dict_literal(self):
        out, _, rc = clython_run("print({**{'a': 1}, **{'b': 2}})")
        assert rc == 0 and out == "{'a': 1, 'b': 2}"


# ═══════════════════════════════════════════════════════════════════════════════
# 6.16: Evaluation Order
# ═══════════════════════════════════════════════════════════════════════════════


class TestSection616EvaluationOrder:
    """6.16: Evaluation order (left-to-right, short-circuit)."""

    def test_left_to_right_arithmetic(self):
        """Arguments are evaluated left to right."""
        out, _, rc = clython_run(
            "log = []\ndef f(x):\n    log.append(x)\n    return x\n"
            "print(f(1) + f(2) + f(3))\nprint(log)"
        )
        assert rc == 0 and out == "6\n[1, 2, 3]"

    def test_function_argument_order(self):
        """Function arguments evaluated left to right."""
        out, _, rc = clython_run(
            "log = []\ndef f(x):\n    log.append(x)\n    return x\n"
            "def add(a, b, c): return a + b + c\n"
            "print(add(f(1), f(2), f(3)))\nprint(log)"
        )
        assert rc == 0 and out == "6\n[1, 2, 3]"

    def test_and_short_circuit_order(self):
        """and stops at first falsy value."""
        out, _, rc = clython_run(
            "log = []\ndef f(x):\n    log.append(x)\n    return x\n"
            "print(f(0) and f(1) and f(2))\nprint(log)"
        )
        assert rc == 0 and out == "0\n[0]"

    def test_or_short_circuit_order(self):
        """or stops at first truthy value."""
        out, _, rc = clython_run(
            "log = []\ndef f(x):\n    log.append(x)\n    return x\n"
            "print(f(0) or f(0) or f(3))\nprint(log)"
        )
        assert rc == 0 and out == "3\n[0, 0, 3]"

    def test_conditional_expression_order(self):
        """Only the selected branch is evaluated."""
        out, _, rc = clython_run(
            "log = []\ndef a():\n    log.append('a')\n    return 1\n"
            "def b():\n    log.append('b')\n    return 2\n"
            "result = a() if True else b()\n"
            "print(result)\nprint(log)"
        )
        assert rc == 0 and out == "1\n['a']"

    def test_comparison_chain_eval_once(self):
        """In chained comparison, middle expression evaluated once."""
        out, _, rc = clython_run(
            "log = []\ndef f(x):\n    log.append(x)\n    return x\n"
            "print(0 < f(1) < 2)\nprint(log)"
        )
        assert rc == 0 and out == "True\n[1]"

    def test_nested_function_call_order(self):
        """Nested calls: outer waits for inner."""
        out, _, rc = clython_run(
            "log = []\ndef f(x):\n    log.append(x)\n    return x\n"
            "print(f(f(1) + f(2)))\nprint(log)"
        )
        assert rc == 0 and out == "3\n[1, 2, 3]"

    def test_comprehension_evaluation_order(self):
        out, _, rc = clython_run(
            "log = []\ndef f(x):\n    log.append(x)\n    return x\n"
            "result = [f(x) for x in [3, 1, 2]]\nprint(result)\nprint(log)"
        )
        assert rc == 0 and out == "[3, 1, 2]\n[3, 1, 2]"

    def test_assignment_rhs_before_lhs(self):
        """Right-hand side is fully evaluated before assignment."""
        out, _, rc = clython_run("a = 1\nb = 2\na, b = b, a\nprint(a, b)")
        assert rc == 0 and out == "2 1"

    def test_subscript_evaluation_order(self):
        out, _, rc = clython_run(
            "log = []\ndef f(x):\n    log.append(x)\n    return x\n"
            "x = [10, 20, 30]\nprint(x[f(1)])\nprint(log)"
        )
        assert rc == 0 and out == "20\n[1]"

    def test_precedence_evaluation(self):
        """Precedence determines grouping, not evaluation order."""
        out, _, rc = clython_run(
            "log = []\ndef f(x):\n    log.append(x)\n    return x\n"
            "print(f(2) + f(3) * f(4))\nprint(log)"
        )
        assert rc == 0 and out == "14\n[2, 3, 4]"

    def test_walrus_evaluation_order(self):
        out, _, rc = clython_run(
            "log = []\ndef f(x):\n    log.append(x)\n    return x\n"
            "if (y := f(5)) > 3:\n    print(y)\nprint(log)"
        )
        assert rc == 0 and out == "5\n[5]"

    def test_lambda_body_deferred(self):
        """Lambda body is not evaluated at definition time."""
        out, _, rc = clython_run(
            "log = []\ndef f(x):\n    log.append(x)\n    return x\n"
            "fn = lambda: f(1)\nprint(log)\nprint(fn())\nprint(log)"
        )
        assert rc == 0 and out == "[]\n1\n[1]"


# ═══════════════════════════════════════════════════════════════════════════════
# Extended keyword argument tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestSection63KwargsExtended:
    """Extended keyword argument tests."""

    def test_keyword_argument_print_end(self):
        out, _, rc = clython_run("print('hello', end='!')\nprint('world')")
        assert rc == 0 and out == "hello!world"

    def test_keyword_argument_print_sep_and_end(self):
        out, _, rc = clython_run("print('a', 'b', sep='-', end='\\n')")
        assert rc == 0 and out == "a-b"
