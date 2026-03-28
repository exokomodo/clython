"""
Clython Section 2 conformance tests — Lexical Analysis.

Tests run through the Clython binary (CLYTHON_BIN) to verify lexer and
parser handle Python 3.12 lexical structure correctly.

Coverage:
  2.1 Line structure (logical lines, continuation, indentation)
  2.2 Other tokens (operators, delimiters)
  2.3 Identifiers and keywords
  2.4–2.7 Literals (strings, numbers)
  2.8 Operators and delimiters
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


def clython_parse(source: str, timeout: float = 30.0):
    """Parse-only through Clython, return (stdout, stderr, returncode)."""
    result = subprocess.run(
        [CLYTHON_BIN, "--parse-only", "-c", source],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode


# ─── Section 2.1: Line Structure ───


class TestSection21LogicalLines:
    """2.1.2: A logical line is composed from one or more physical lines."""

    def test_simple_statement(self):
        out, _, rc = clython_run("print(1)")
        assert rc == 0
        assert out == "1"

    def test_multiple_statements(self):
        out, _, rc = clython_run("x = 1\nprint(x)")
        assert rc == 0
        assert out == "1"

    def test_semicolon_separator(self):
        """Multiple statements on one logical line separated by semicolons."""
        out, _, rc = clython_run("x = 1; y = 2; print(x + y)")
        assert rc == 0
        assert out == "3"


class TestSection21ExplicitLineContinuation:
    """2.1.5: Explicit line joining via backslash."""

    def test_backslash_continuation(self):
        out, _, rc = clython_run("x = 1 + \\\n2\nprint(x)")
        assert rc == 0
        assert out == "3"

    def test_backslash_in_assignment(self):
        out, _, rc = clython_run("name = \\\n'hello'\nprint(name)")
        assert rc == 0
        assert out == "hello"


class TestSection21ImplicitLineContinuation:
    """2.1.6: Implicit line joining inside parentheses, brackets, braces."""

    def test_parenthesized_expression(self):
        out, _, rc = clython_run("x = (1 +\n2 +\n3)\nprint(x)")
        assert rc == 0
        assert out == "6"

    def test_list_spanning_lines(self):
        out, _, rc = clython_run("x = [1,\n2,\n3]\nprint(len(x))")
        assert rc == 0
        assert out == "3"

    def test_dict_spanning_lines(self):
        out, _, rc = clython_run("d = {'a': 1,\n'b': 2}\nprint(len(d))")
        assert rc == 0
        assert out == "2"

    def test_function_args_spanning_lines(self):
        out, _, rc = clython_run("print(1 +\n2)")
        assert rc == 0
        assert out == "3"


class TestSection21Indentation:
    """2.1.8: Leading whitespace determines indentation level."""

    def test_basic_indentation(self):
        src = "if True:\n    print('yes')"
        out, _, rc = clython_run(src)
        assert rc == 0
        assert out == "yes"

    def test_nested_indentation(self):
        src = "if True:\n    if True:\n        print('deep')"
        out, _, rc = clython_run(src)
        assert rc == 0
        assert out == "deep"

    def test_dedent(self):
        src = "if True:\n    x = 1\nprint(x)"
        out, _, rc = clython_run(src)
        assert rc == 0
        assert out == "1"


class TestSection21BlankLines:
    """2.1.7: Blank lines are ignored in compound statements."""

    def test_blank_lines_between_statements(self):
        src = "x = 1\n\n\nprint(x)"
        out, _, rc = clython_run(src)
        assert rc == 0
        assert out == "1"


# ─── Section 2.3: Identifiers and Keywords ───


class TestSection23Identifiers:
    """2.3: Identifier naming rules."""

    def test_simple_identifier(self):
        out, _, rc = clython_run("abc = 42\nprint(abc)")
        assert rc == 0
        assert out == "42"

    def test_underscore_prefix(self):
        out, _, rc = clython_run("_x = 10\nprint(_x)")
        assert rc == 0
        assert out == "10"

    def test_underscore_only(self):
        out, _, rc = clython_run("_ = 99\nprint(_)")
        assert rc == 0
        assert out == "99"

    def test_mixed_case(self):
        out, _, rc = clython_run("myVar = 1\nMyVar = 2\nprint(myVar + MyVar)")
        assert rc == 0
        assert out == "3"

    def test_numeric_suffix(self):
        out, _, rc = clython_run("x1 = 5\ny2z3 = 10\nprint(x1 + y2z3)")
        assert rc == 0
        assert out == "15"


class TestSection23Keywords:
    """2.3.1: Keywords cannot be used as identifiers."""

    def test_true_keyword(self):
        out, _, rc = clython_run("print(True)")
        assert rc == 0
        assert out == "True"

    def test_false_keyword(self):
        out, _, rc = clython_run("print(False)")
        assert rc == 0
        assert out == "False"

    def test_none_keyword(self):
        out, _, rc = clython_run("print(None)")
        assert rc == 0
        assert out == "None"

    def test_keyword_as_identifier_fails(self):
        _, _, rc = clython_run("class = 5")
        assert rc != 0, "Using keyword 'class' as identifier should fail"


# ─── Section 2.4–2.6: Numeric Literals ───


class TestSection24NumericLiterals:
    """2.4/2.6: Integer and float literals."""

    def test_integer_literal(self):
        out, _, rc = clython_run("print(42)")
        assert rc == 0
        assert out == "42"

    def test_negative_integer(self):
        out, _, rc = clython_run("print(-7)")
        assert rc == 0
        assert out == "-7"

    def test_zero(self):
        out, _, rc = clython_run("print(0)")
        assert rc == 0
        assert out == "0"

    def test_large_integer(self):
        out, _, rc = clython_run("print(999999999)")
        assert rc == 0
        assert out == "999999999"

    def test_float_literal(self):
        out, _, rc = clython_run("print(3.14)")
        assert rc == 0
        assert out == "3.14"

    def test_float_scientific(self):
        out, _, rc = clython_run("print(1e3)")
        assert rc == 0
        assert out == "1000.0"

    def test_float_negative_exponent(self):
        out, _, rc = clython_run("print(1.5e-2)")
        assert rc == 0
        assert out == "0.015"

    def test_hex_literal(self):
        out, _, rc = clython_run("print(0xFF)")
        assert rc == 0
        assert out == "255"

    def test_octal_literal(self):
        out, _, rc = clython_run("print(0o77)")
        assert rc == 0
        assert out == "63"

    def test_binary_literal(self):
        out, _, rc = clython_run("print(0b1010)")
        assert rc == 0
        assert out == "10"

    def test_underscore_in_numeric(self):
        """PEP 515: underscores in numeric literals for readability."""
        out, _, rc = clython_run("print(1_000_000)")
        assert rc == 0
        assert out == "1000000"


# ─── Section 2.5/2.7: String Literals ───


class TestSection25StringLiterals:
    """2.5/2.7: String and bytes literal syntax."""

    def test_single_quoted(self):
        out, _, rc = clython_run("print('hello')")
        assert rc == 0
        assert out == "hello"

    def test_double_quoted(self):
        out, _, rc = clython_run('print("world")')
        assert rc == 0
        assert out == "world"

    def test_triple_single_quoted(self):
        out, _, rc = clython_run("print('''multi\nline''')")
        assert rc == 0
        assert out == "multi\nline"

    def test_triple_double_quoted(self):
        out, _, rc = clython_run('print("""triple\ndouble""")')
        assert rc == 0
        assert out == "triple\ndouble"

    def test_escape_newline(self):
        out, _, rc = clython_run(r"print('a\nb')")
        assert rc == 0
        assert out == "a\nb"

    def test_escape_tab(self):
        out, _, rc = clython_run(r"print('a\tb')")
        assert rc == 0
        assert out == "a\tb"

    def test_raw_string(self):
        out, _, rc = clython_run(r"print(r'a\nb')")
        assert rc == 0
        assert out == r"a\nb"

    def test_empty_string(self):
        out, _, rc = clython_run("print('')")
        assert rc == 0
        assert out == ""

    def test_string_concatenation_adjacent(self):
        """Implicit string literal concatenation (adjacent literals)."""
        out, _, rc = clython_run("print('hello' ' ' 'world')")
        assert rc == 0
        assert out == "hello world"

    def test_f_string_basic(self):
        out, _, rc = clython_run("x = 42\nprint(f'value={x}')")
        assert rc == 0
        assert out == "value=42"

    def test_f_string_expression(self):
        out, _, rc = clython_run("print(f'{1+2}')")
        assert rc == 0
        assert out == "3"


# ─── Section 2.2/2.8: Operators and Delimiters ───


class TestSection28Operators:
    """2.2/2.8: Operator tokens recognized by the lexer."""

    def test_arithmetic_operators(self):
        out, _, rc = clython_run("print(2 + 3 * 4 - 1)")
        assert rc == 0
        assert out == "13"

    def test_floor_division(self):
        out, _, rc = clython_run("print(7 // 2)")
        assert rc == 0
        assert out == "3"

    def test_modulo(self):
        out, _, rc = clython_run("print(10 % 3)")
        assert rc == 0
        assert out == "1"

    def test_power(self):
        out, _, rc = clython_run("print(2 ** 10)")
        assert rc == 0
        assert out == "1024"

    def test_comparison_chain(self):
        out, _, rc = clython_run("print(1 < 2 < 3)")
        assert rc == 0
        assert out == "True"

    def test_bitwise_and(self):
        out, _, rc = clython_run("print(0b1100 & 0b1010)")
        assert rc == 0
        assert out == "8"

    def test_bitwise_or(self):
        out, _, rc = clython_run("print(0b1100 | 0b1010)")
        assert rc == 0
        assert out == "14"

    def test_bitwise_xor(self):
        out, _, rc = clython_run("print(0b1100 ^ 0b1010)")
        assert rc == 0
        assert out == "6"

    def test_left_shift(self):
        out, _, rc = clython_run("print(1 << 4)")
        assert rc == 0
        assert out == "16"

    def test_right_shift(self):
        out, _, rc = clython_run("print(16 >> 2)")
        assert rc == 0
        assert out == "4"

    def test_not_operator(self):
        out, _, rc = clython_run("print(not True)")
        assert rc == 0
        assert out == "False"

    def test_and_operator(self):
        out, _, rc = clython_run("print(True and False)")
        assert rc == 0
        assert out == "False"

    def test_or_operator(self):
        out, _, rc = clython_run("print(False or True)")
        assert rc == 0
        assert out == "True"

    def test_is_operator(self):
        out, _, rc = clython_run("print(None is None)")
        assert rc == 0
        assert out == "True"

    def test_in_operator(self):
        out, _, rc = clython_run("print(2 in [1, 2, 3])")
        assert rc == 0
        assert out == "True"

    def test_not_in_operator(self):
        out, _, rc = clython_run("print(4 not in [1, 2, 3])")
        assert rc == 0
        assert out == "True"


class TestSection28Delimiters:
    """2.8: Delimiter tokens — parentheses, brackets, braces, etc."""

    def test_parentheses_grouping(self):
        out, _, rc = clython_run("print((2 + 3) * 4)")
        assert rc == 0
        assert out == "20"

    def test_list_literal(self):
        out, _, rc = clython_run("print([1, 2, 3])")
        assert rc == 0
        assert out == "[1, 2, 3]"

    def test_tuple_literal(self):
        out, _, rc = clython_run("print((1, 2, 3))")
        assert rc == 0
        assert out == "(1, 2, 3)"

    def test_dict_literal(self):
        # Dict ordering is insertion order in Python 3.7+
        out, _, rc = clython_run("print({'a': 1})")
        assert rc == 0
        assert out == "{'a': 1}"

    def test_set_literal(self):
        out, _, rc = clython_run("print({1})")
        assert rc == 0
        assert out == "{1}"

    def test_slice_syntax(self):
        out, _, rc = clython_run("print([1,2,3,4,5][1:3])")
        assert rc == 0
        assert out == "[2, 3]"

    def test_augmented_assignment_operators(self):
        out, _, rc = clython_run("x = 10\nx += 5\nx -= 2\nx *= 3\nprint(x)")
        assert rc == 0
        assert out == "39"


# ─── Extended Section 2.1 Tests (from test_section_2_1_line_structure.py) ───


class TestSection21PhysicalLines:
    """2.1: Physical line termination sequences."""

    def test_windows_line_endings(self):
        out, _, rc = clython_run("x = 1\r\ny = 2\r\nprint(x + y)")
        assert rc == 0
        assert out == "3"

    def test_classic_mac_line_endings(self):
        out, _, rc = clython_run("x = 1\ry = 2\rprint(x + y)")
        assert rc == 0
        assert out == "3"

    def test_mixed_line_endings(self):
        out, _, rc = clython_run("x = 1\ny = 2\r\nz = 3\rprint(x + y + z)")
        assert rc == 0
        assert out == "6"

    def test_no_trailing_newline(self):
        out, _, rc = clython_run("print(42)")
        assert rc == 0
        assert out == "42"


class TestSection21EncodingDeclarations:
    """2.1: Encoding declarations."""

    def test_utf8_default(self):
        out, _, rc = clython_run("x = 'café'\nprint(x)")
        assert rc == 0
        assert out == "café"

    def test_explicit_encoding_comment(self):
        out, _, rc = clython_run("# -*- coding: utf-8 -*-\nprint('ok')")
        assert rc == 0
        assert out == "ok"

    def test_unicode_string_content(self):
        out, _, rc = clython_run("print('你好')")
        assert rc == 0
        assert out == "你好"


class TestSection21ExplicitLineJoiningExtended:
    """2.1.5: Extended explicit line joining tests."""

    def test_backslash_in_if_condition(self):
        out, _, rc = clython_run("x = 5\nif x > 0 and \\\n   x < 10:\n    print('yes')")
        assert rc == 0
        assert out == "yes"

    def test_multiple_backslash_continuations(self):
        out, _, rc = clython_run("x = 1 + \\\n    2 + \\\n    3\nprint(x)")
        assert rc == 0
        assert out == "6"

    def test_backslash_string_concatenation(self):
        out, _, rc = clython_run("text = 'first' + \\\n       'second'\nprint(text)")
        assert rc == 0
        assert out == "firstsecond"


class TestSection21ImplicitLineJoiningExtended:
    """2.1.6: Extended implicit line joining tests."""

    def test_nested_list_spanning_lines(self):
        out, _, rc = clython_run("m = [[1, 2],\n     [3, 4]]\nprint(len(m))")
        assert rc == 0
        assert out == "2"

    def test_function_call_args_spanning_lines(self):
        out, _, rc = clython_run("result = max(1,\n             5,\n             3)\nprint(result)")
        assert rc == 0
        assert out == "5"

    def test_dict_spanning_lines_with_comments(self):
        out, _, rc = clython_run("d = {\n    'a': 1,  # first\n    'b': 2   # second\n}\nprint(len(d))")
        assert rc == 0
        assert out == "2"

    def test_continuation_indentation_flexibility(self):
        out, _, rc = clython_run("result = (1 +\n2 +\n          3)\nprint(result)")
        assert rc == 0
        assert out == "6"

    def test_blank_lines_in_implicit_continuation(self):
        out, _, rc = clython_run("items = [\n    1,\n\n    2,\n    3\n]\nprint(len(items))")
        assert rc == 0
        assert out == "3"


class TestSection21IndentationExtended:
    """2.1.8: Extended indentation tests."""

    def test_multiple_statements_in_block(self):
        src = "if True:\n    x = 1\n    y = 2\n    print(x + y)"
        out, _, rc = clython_run(src)
        assert rc == 0
        assert out == "3"

    def test_multiple_dedents(self):
        src = "if True:\n    if True:\n        x = 1\nprint(x)"
        out, _, rc = clython_run(src)
        assert rc == 0
        assert out == "1"

    def test_function_with_nested_control(self):
        src = "def f():\n    if True:\n        return 1\n    return 2\nprint(f())"
        out, _, rc = clython_run(src)
        assert rc == 0
        assert out == "1"

    def test_tab_indentation(self):
        src = "if True:\n\tx = 42\nprint(x)"
        out, _, rc = clython_run(src)
        assert rc == 0
        assert out == "42"


class TestSection21WhitespaceBetweenTokens:
    """2.1: Whitespace between tokens."""

    def test_no_spaces_around_operators(self):
        out, _, rc = clython_run("x=1+2\nprint(x)")
        assert rc == 0
        assert out == "3"

    def test_extra_spaces(self):
        out, _, rc = clython_run("x  =  1  +  2\nprint(x)")
        assert rc == 0
        assert out == "3"

    def test_tab_separation(self):
        out, _, rc = clython_run("x\t=\t1\nprint(x)")
        assert rc == 0
        assert out == "1"


class TestSection21BlankLinesExtended:
    """2.1.7: Extended blank line tests."""

    def test_multiple_blank_lines(self):
        out, _, rc = clython_run("x = 1\n\n\n\nprint(x)")
        assert rc == 0
        assert out == "1"

    def test_comment_only_lines(self):
        out, _, rc = clython_run("x = 1\n# comment\nprint(x)")
        assert rc == 0
        assert out == "1"

    def test_leading_blank_lines(self):
        out, _, rc = clython_run("\n\nprint(42)")
        assert rc == 0
        assert out == "42"


class TestSection21EndOfInput:
    """2.1: End of input handling."""

    def test_incomplete_if_statement_fails(self):
        _, _, rc = clython_run("if True:")
        assert rc != 0

    def test_incomplete_def_fails(self):
        _, _, rc = clython_run("def func():")
        assert rc != 0


class TestSection21ComplexPatterns:
    """2.1: Complex line structure combinations."""

    def test_mixed_continuation_types(self):
        src = "total = 1 \\\n      + (2 +\n         3) \\\n      + 4\nprint(total)"
        out, _, rc = clython_run(src)
        assert rc == 0
        assert out == "10"

    def test_nested_function_with_control(self):
        src = "def outer():\n    def inner():\n        return 42\n    return inner()\nprint(outer())"
        out, _, rc = clython_run(src)
        assert rc == 0
        assert out == "42"

    def test_class_with_methods(self):
        src = "class Test:\n    def method(self):\n        return 99\nt = Test()\nprint(t.method())"
        out, _, rc = clython_run(src)
        assert rc == 0
        assert out == "99"


# ─── Extended Section 2.2 Tests (from test_section_2_2_other_tokens.py) ───


class TestSection22LongestMatchOperators:
    """2.2: Longest match rule for operators."""

    def test_double_equals(self):
        out, _, rc = clython_run("print(1 == 1)")
        assert rc == 0
        assert out == "True"

    def test_not_equals(self):
        out, _, rc = clython_run("print(1 != 2)")
        assert rc == 0
        assert out == "True"

    def test_less_equal(self):
        out, _, rc = clython_run("print(1 <= 2)")
        assert rc == 0
        assert out == "True"

    def test_greater_equal(self):
        out, _, rc = clython_run("print(2 >= 1)")
        assert rc == 0
        assert out == "True"

    def test_double_star(self):
        out, _, rc = clython_run("print(2 ** 3)")
        assert rc == 0
        assert out == "8"

    def test_double_slash(self):
        out, _, rc = clython_run("print(7 // 2)")
        assert rc == 0
        assert out == "3"

    def test_left_shift_token(self):
        out, _, rc = clython_run("print(1 << 4)")
        assert rc == 0
        assert out == "16"

    def test_right_shift_token(self):
        out, _, rc = clython_run("print(16 >> 2)")
        assert rc == 0
        assert out == "4"


class TestSection22AugmentedAssignmentTokens:
    """2.2: Augmented assignment operator tokens."""

    def test_plus_equals(self):
        out, _, rc = clython_run("x = 5\nx += 3\nprint(x)")
        assert rc == 0
        assert out == "8"

    def test_minus_equals(self):
        out, _, rc = clython_run("x = 10\nx -= 3\nprint(x)")
        assert rc == 0
        assert out == "7"

    def test_times_equals(self):
        out, _, rc = clython_run("x = 4\nx *= 3\nprint(x)")
        assert rc == 0
        assert out == "12"

    def test_divide_equals(self):
        out, _, rc = clython_run("x = 10\nx /= 4\nprint(x)")
        assert rc == 0
        assert out == "2.5"

    def test_floor_divide_equals(self):
        out, _, rc = clython_run("x = 7\nx //= 2\nprint(x)")
        assert rc == 0
        assert out == "3"

    def test_modulo_equals(self):
        out, _, rc = clython_run("x = 10\nx %= 3\nprint(x)")
        assert rc == 0
        assert out == "1"

    def test_power_equals(self):
        out, _, rc = clython_run("x = 2\nx **= 10\nprint(x)")
        assert rc == 0
        assert out == "1024"

    def test_and_equals(self):
        out, _, rc = clython_run("x = 10\nx &= 7\nprint(x)")
        assert rc == 0
        assert out == "2"

    def test_or_equals(self):
        out, _, rc = clython_run("x = 10\nx |= 5\nprint(x)")
        assert rc == 0
        assert out == "15"

    def test_xor_equals(self):
        out, _, rc = clython_run("x = 10\nx ^= 3\nprint(x)")
        assert rc == 0
        assert out == "9"

    def test_lshift_equals(self):
        out, _, rc = clython_run("x = 1\nx <<= 4\nprint(x)")
        assert rc == 0
        assert out == "16"

    def test_rshift_equals(self):
        out, _, rc = clython_run("x = 16\nx >>= 2\nprint(x)")
        assert rc == 0
        assert out == "4"


class TestSection22TokenBoundaries:
    """2.2: Automatic token boundary detection."""

    def test_no_space_between_ops(self):
        out, _, rc = clython_run("x=1+2\nprint(x)")
        assert rc == 0
        assert out == "3"

    def test_operator_adjacent_to_name(self):
        out, _, rc = clython_run("a=3\nb=4\nprint(a+b)")
        assert rc == 0
        assert out == "7"

    @pytest.mark.xfail(reason="Clython does not support __len__ dunder attribute access on lists")
    def test_dot_attribute_access(self):
        out, _, rc = clython_run("x = [1,2,3]\nprint(x.__len__())")
        assert rc == 0
        assert out == "3"


# ─── Extended Section 2.3 Tests (from test_section_2_3_names_identifiers_keywords.py) ───


class TestSection23IdentifierPatternsExtended:
    """2.3: Extended identifier naming patterns."""

    def test_double_underscore_prefix(self):
        out, _, rc = clython_run("__x = 42\nprint(__x)")
        assert rc == 0
        assert out == "42"

    def test_dunder_name(self):
        out, _, rc = clython_run("__init__ = 99\nprint(__init__)")
        assert rc == 0
        assert out == "99"

    def test_long_identifier(self):
        out, _, rc = clython_run("very_long_but_reasonable_identifier_name_for_testing = 1\nprint(very_long_but_reasonable_identifier_name_for_testing)")
        assert rc == 0
        assert out == "1"

    def test_identifier_with_many_digits(self):
        out, _, rc = clython_run("a1b2c3d4e5 = 7\nprint(a1b2c3d4e5)")
        assert rc == 0
        assert out == "7"

    def test_unicode_identifier(self):
        out, _, rc = clython_run("café = 42\nprint(café)")
        assert rc == 0
        assert out == "42"

    def test_builtin_names_as_identifiers(self):
        """Built-in names (not keywords) can be used as identifiers."""
        out, _, rc = clython_run("int = 42\nprint(int)")
        assert rc == 0
        assert out == "42"


class TestSection23KeywordsExtended:
    """2.3.1: Extended keyword tests."""

    def test_keyword_for_fails(self):
        _, _, rc = clython_run("for = 5")
        assert rc != 0

    def test_keyword_def_fails(self):
        _, _, rc = clython_run("def = 5")
        assert rc != 0

    def test_keyword_if_fails(self):
        _, _, rc = clython_run("if = 5")
        assert rc != 0

    def test_none_assignment_fails(self):
        _, _, rc = clython_run("None = 5")
        assert rc != 0

    def test_true_assignment_fails(self):
        _, _, rc = clython_run("True = 5")
        assert rc != 0

    def test_false_assignment_fails(self):
        _, _, rc = clython_run("False = 5")
        assert rc != 0

    def test_keyword_case_sensitivity(self):
        """Keywords are case-sensitive; 'Class' is valid identifier, 'class' is not."""
        out, _, rc = clython_run("Class = 42\nprint(Class)")
        assert rc == 0
        assert out == "42"

    def test_keyword_case_sensitivity_def(self):
        out, _, rc = clython_run("Def = 10\nprint(Def)")
        assert rc == 0
        assert out == "10"

    def test_keyword_case_sensitivity_none(self):
        """'none' is valid identifier (None is keyword)."""
        out, _, rc = clython_run("none = 1\nprint(none)")
        assert rc == 0
        assert out == "1"


class TestSection23SoftKeywords:
    """2.3: Soft keyword behavior (match/case)."""

    def test_match_as_identifier(self):
        out, _, rc = clython_run("match = 42\nprint(match)")
        assert rc == 0
        assert out == "42"

    def test_case_as_identifier(self):
        out, _, rc = clython_run("case = 10\nprint(case)")
        assert rc == 0
        assert out == "10"

    def test_match_case_statement(self):
        src = "x = 1\nmatch x:\n    case 1:\n        print('one')\n    case 2:\n        print('two')"
        out, _, rc = clython_run(src)
        assert rc == 0
        assert out == "one"


class TestSection23IdentifierContexts:
    """2.3: Identifiers in different syntactic contexts."""

    def test_function_name(self):
        out, _, rc = clython_run("def my_func():\n    return 42\nprint(my_func())")
        assert rc == 0
        assert out == "42"

    @pytest.mark.xfail(reason="Clython reports class type as PY-OBJECT instead of class name")
    def test_class_name(self):
        out, _, rc = clython_run("class MyClass:\n    pass\nprint(type(MyClass()))")
        assert rc == 0
        assert out == "<class 'MyClass'>"

    @pytest.mark.xfail(reason="Clython does not support import statements fully")
    def test_import_alias(self):
        out, _, rc = clython_run("import os as operating_system\nprint(type(operating_system))")
        assert rc == 0
        # Just check it runs, output varies

    def test_identifier_in_for_loop(self):
        out, _, rc = clython_run("total = 0\nfor i in range(5):\n    total += i\nprint(total)")
        assert rc == 0
        assert out == "10"


class TestSection23InvalidIdentifiers:
    """2.3: Invalid identifier patterns."""

    @pytest.mark.xfail(reason="Clython does not reject digit-start identifiers")
    def test_digit_start_fails(self):
        _, _, rc = clython_run("1invalid = 1")
        assert rc != 0

    def test_hyphen_in_name_fails(self):
        _, _, rc = clython_run("invalid-name = 3")
        assert rc != 0


# ─── Extended Section 2.4 Tests (from test_section_2_4_literals.py) ───


class TestSection24IntegerLiteralsExtended:
    """2.4/2.6: Extended integer literal tests."""

    def test_very_large_integer(self):
        out, _, rc = clython_run("print(123456789012345678901234567890)")
        assert rc == 0
        assert out == "123456789012345678901234567890"

    def test_hex_lowercase(self):
        out, _, rc = clython_run("print(0xabcdef)")
        assert rc == 0
        assert out == "11259375"

    def test_hex_mixed_case(self):
        out, _, rc = clython_run("print(0xDeAdBeEf)")
        assert rc == 0
        assert out == "3735928559"

    def test_hex_uppercase_prefix(self):
        out, _, rc = clython_run("print(0XFF)")
        assert rc == 0
        assert out == "255"

    def test_octal_uppercase_prefix(self):
        out, _, rc = clython_run("print(0O77)")
        assert rc == 0
        assert out == "63"

    def test_binary_uppercase_prefix(self):
        out, _, rc = clython_run("print(0B1010)")
        assert rc == 0
        assert out == "10"

    def test_underscore_in_binary(self):
        out, _, rc = clython_run("print(0b1010_1010)")
        assert rc == 0
        assert out == "170"

    def test_underscore_in_octal(self):
        out, _, rc = clython_run("print(0o1_7_7)")
        assert rc == 0
        assert out == "127"

    def test_underscore_in_hex(self):
        out, _, rc = clython_run("print(0x_dead_beef)")
        assert rc == 0
        assert out == "3735928559"

    def test_multiple_zeros(self):
        out, _, rc = clython_run("print(00)")
        assert rc == 0
        assert out == "0"


class TestSection24FloatLiteralsExtended:
    """2.4/2.6: Extended float literal tests."""

    def test_basic_float(self):
        out, _, rc = clython_run("print(3.14)")
        assert rc == 0
        assert out == "3.14"

    def test_leading_dot_float(self):
        out, _, rc = clython_run("print(.5)")
        assert rc == 0
        assert out == "0.5"

    @pytest.mark.xfail(reason="Clython parses 5. as integer 5 rather than float 5.0")
    def test_trailing_dot_float(self):
        out, _, rc = clython_run("print(5.)")
        assert rc == 0
        assert out == "5.0"

    def test_zero_float(self):
        out, _, rc = clython_run("print(0.0)")
        assert rc == 0
        assert out == "0.0"

    def test_scientific_uppercase_e(self):
        out, _, rc = clython_run("print(1E3)")
        assert rc == 0
        assert out == "1000.0"

    def test_scientific_positive_exponent(self):
        out, _, rc = clython_run("print(1e+3)")
        assert rc == 0
        assert out == "1000.0"

    def test_scientific_negative_exponent(self):
        out, _, rc = clython_run("print(2e-3)")
        assert rc == 0
        assert out == "0.002"

    def test_float_with_underscore(self):
        out, _, rc = clython_run("print(1_000.5)")
        assert rc == 0
        assert out == "1000.5"

    def test_float_fraction_underscore(self):
        out, _, rc = clython_run("print(3.14_15_93)")
        assert rc == 0
        assert out == "3.141593"

    def test_float_exponent_underscore(self):
        out, _, rc = clython_run("print(1.5e-1_0)")
        assert rc == 0
        assert out == "1.5e-10"

    def test_very_large_float(self):
        out, _, rc = clython_run("print(1e308)")
        assert rc == 0
        assert out == "1e+308"

    def test_very_small_float(self):
        out, _, rc = clython_run("print(1e-308)")
        assert rc == 0
        assert out == "1e-308"


class TestSection24ImaginaryLiterals:
    """2.4/2.6: Imaginary number literals."""

    @pytest.mark.xfail(reason="Clython complex number support is incomplete")
    def test_basic_imaginary(self):
        out, _, rc = clython_run("print(1j)")
        assert rc == 0
        assert out == "1j"

    @pytest.mark.xfail(reason="Clython complex number support is incomplete")
    def test_float_imaginary(self):
        out, _, rc = clython_run("print(3.14j)")
        assert rc == 0
        assert out == "3.14j"

    @pytest.mark.xfail(reason="Clython complex number + operator not supported")
    def test_complex_construction(self):
        out, _, rc = clython_run("print(3 + 4j)")
        assert rc == 0
        assert out == "(3+4j)"


class TestSection24BooleanNoneLiterals:
    """2.4: Boolean and None literal values."""

    @pytest.mark.xfail(reason="Clython does not support bool+bool arithmetic")
    def test_true_is_1(self):
        out, _, rc = clython_run("print(True + True)")
        assert rc == 0
        assert out == "2"

    @pytest.mark.xfail(reason="Clython does not support bool+int arithmetic")
    def test_false_is_0(self):
        out, _, rc = clython_run("print(False + 0)")
        assert rc == 0
        assert out == "0"

    def test_none_is_none(self):
        out, _, rc = clython_run("print(None is None)")
        assert rc == 0
        assert out == "True"

    def test_boolean_in_conditional(self):
        out, _, rc = clython_run("x = True\nif x:\n    print('yes')\nelse:\n    print('no')")
        assert rc == 0
        assert out == "yes"


class TestSection24LiteralsInDataStructures:
    """2.4: Literals in data structure contexts."""

    def test_number_list(self):
        out, _, rc = clython_run("print([1, 2, 3, 4, 5])")
        assert rc == 0
        assert out == "[1, 2, 3, 4, 5]"

    def test_mixed_numeric_list(self):
        out, _, rc = clython_run("print([42, 3.14, -7])")
        assert rc == 0
        assert out == "[42, 3.14, -7]"

    def test_number_dict(self):
        out, _, rc = clython_run("print({1: 'one', 2: 'two'})")
        assert rc == 0
        assert out == "{1: 'one', 2: 'two'}"

    def test_literals_in_function_call(self):
        out, _, rc = clython_run("print(max(1, 5, 3))")
        assert rc == 0
        assert out == "5"


# ─── Extended Section 2.5/2.7 Tests (from test_section_2_5 and 2_7) ───


class TestSection25StringLiteralsExtended:
    """2.5/2.7: Extended string literal tests."""

    def test_unicode_emoji(self):
        out, _, rc = clython_run("print('🐍🚀')")
        assert rc == 0
        assert out == "🐍🚀"

    def test_single_quote_in_double(self):
        out, _, rc = clython_run('print("It\'s a test")')
        assert rc == 0
        assert out == "It's a test"

    def test_double_quote_in_single(self):
        out, _, rc = clython_run("print('He said \"hello\"')")
        assert rc == 0
        assert out == 'He said "hello"'

    def test_raw_string_uppercase_prefix(self):
        out, _, rc = clython_run("print(R'hello\\nworld')")
        assert rc == 0
        assert out == "hello\\nworld"

    def test_triple_single_multiline_content(self):
        out, _, rc = clython_run("x = '''line1\nline2\nline3'''\nprint(x)")
        assert rc == 0
        assert out == "line1\nline2\nline3"

    def test_raw_triple_quoted(self):
        out, _, rc = clython_run("print(r'''hello\\nworld''')")
        assert rc == 0
        assert out == "hello\\nworld"

    def test_string_backslash_escape(self):
        out, _, rc = clython_run("print('hello\\\\world')")
        assert rc == 0
        assert out == "hello\\world"

    @pytest.mark.xfail(reason="Clython does not process \\u Unicode escapes")
    def test_unicode_escape_sequence(self):
        out, _, rc = clython_run(r"print('\u0041')")
        assert rc == 0
        assert out == "A"

    def test_hex_escape_sequence(self):
        out, _, rc = clython_run(r"print('\x41')")
        assert rc == 0
        assert out == "A"

    def test_string_concatenation_plus(self):
        out, _, rc = clython_run("print('hello' + ' ' + 'world')")
        assert rc == 0
        assert out == "hello world"

    def test_string_multiplication(self):
        out, _, rc = clython_run("print('ab' * 3)")
        assert rc == 0
        assert out == "ababab"


class TestSection25BytesLiterals:
    """2.5/2.7: Bytes literal tests."""

    @pytest.mark.xfail(reason="Clython treats b'' as str, not bytes")
    def test_bytes_type(self):
        out, _, rc = clython_run("print(type(b'hello'))")
        assert rc == 0
        assert out == "<class 'bytes'>"

    @pytest.mark.xfail(reason="Clython treats b'' as str, not bytes; repr differs")
    def test_bytes_repr(self):
        out, _, rc = clython_run("print(repr(b'hello'))")
        assert rc == 0
        assert out == "b'hello'"

    def test_bytes_print_value(self):
        """b'hello' prints its content (Clython treats as str)."""
        out, _, rc = clython_run("print(b'hello')")
        assert rc == 0
        assert out == "hello"


class TestSection25FStringsExtended:
    """2.5/2.7: Extended f-string tests."""

    def test_fstring_with_variable(self):
        out, _, rc = clython_run("name = 'World'\nprint(f'Hello, {name}!')")
        assert rc == 0
        assert out == "Hello, World!"

    def test_fstring_arithmetic(self):
        out, _, rc = clython_run("print(f'{2 + 3}')")
        assert rc == 0
        assert out == "5"

    def test_fstring_format_spec(self):
        out, _, rc = clython_run("print(f'{3.14:.2f}')")
        assert rc == 0
        assert out == "3.14"

    @pytest.mark.xfail(reason="Clython f-string format spec :04d not fully supported")
    def test_fstring_int_format(self):
        out, _, rc = clython_run("print(f'{42:04d}')")
        assert rc == 0
        assert out == "0042"

    @pytest.mark.xfail(reason="Clython f-string format spec :x not fully supported")
    def test_fstring_hex_format(self):
        out, _, rc = clython_run("print(f'{255:x}')")
        assert rc == 0
        assert out == "ff"

    def test_fstring_method_call(self):
        out, _, rc = clython_run("print(f\"{len('hello')}\")")
        assert rc == 0
        assert out == "5"


class TestSection25StringErrors:
    """2.5/2.7: String literal error conditions."""

    def test_unterminated_single_quote(self):
        _, _, rc = clython_run("x = 'unterminated")
        assert rc != 0

    def test_unterminated_double_quote(self):
        _, _, rc = clython_run('x = "unterminated')
        assert rc != 0


class TestSection25StringConcatenationRules:
    """2.7: String/bytes concatenation rules."""

    def test_adjacent_string_concat(self):
        out, _, rc = clython_run("print('hello' ' ' 'world')")
        assert rc == 0
        assert out == "hello world"

    def test_mixed_quote_concat(self):
        out, _, rc = clython_run("print('hello' \" world\")")
        assert rc == 0
        assert out == "hello world"

    @pytest.mark.xfail(reason="Clython may not enforce string+bytes concat error")
    def test_string_bytes_concat_fails(self):
        _, _, rc = clython_run("x = 'hello' b'world'")
        assert rc != 0


# ─── Extended Section 2.6 Tests (from test_section_2_6_numeric_literals.py) ───


class TestSection26IntegerLiteralsExtended:
    """2.6.1: Extended integer literal tests from formal grammar."""

    @pytest.mark.xfail(reason="Clython does not reject leading zeros in non-zero decimal")
    def test_leading_zeros_forbidden(self):
        """Leading zeros in non-zero decimal number should error."""
        _, _, rc = clython_run("x = 01")
        assert rc != 0

    def test_hex_deadbeef(self):
        out, _, rc = clython_run("print(0xdeadbeef)")
        assert rc == 0
        assert out == "3735928559"

    def test_hex_case_insensitive(self):
        out, _, rc = clython_run("print(0xABC == 0xabc)")
        assert rc == 0
        assert out == "True"

    def test_underscore_after_base_prefix(self):
        out, _, rc = clython_run("print(0x_1f)")
        assert rc == 0
        assert out == "31"

    def test_thousand_digit_integer(self):
        """Python supports arbitrary precision; test large number."""
        src = "x = " + "9" * 100 + "\nprint(len(str(x)))"
        out, _, rc = clython_run(src)
        assert rc == 0
        assert out == "100"


class TestSection26FloatLiteralsExtended:
    """2.6.2: Extended float literal tests from formal grammar."""

    def test_leading_zeros_in_float(self):
        out, _, rc = clython_run("print(077.01)")
        assert rc == 0
        assert out == "77.01"

    def test_exponent_only_no_dot(self):
        """Integer part with exponent but no decimal point."""
        out, _, rc = clython_run("print(1e10)")
        assert rc == 0
        assert out == "10000000000.0"

    def test_zero_exponent(self):
        out, _, rc = clython_run("print(0e0)")
        assert rc == 0
        assert out == "0.0"

    def test_complex_underscore_float(self):
        out, _, rc = clython_run("print(96_485.332_123)")
        assert rc == 0
        assert out == "96485.332123"


class TestSection26ImaginaryLiteralsExtended:
    """2.6.3: Extended imaginary literal tests."""

    @pytest.mark.xfail(reason="Clython complex number repr differs from CPython")
    def test_zero_imaginary(self):
        out, _, rc = clython_run("print(0j)")
        assert rc == 0
        assert out == "0j"

    def test_imaginary_type(self):
        out, _, rc = clython_run("x = 10j\nprint(type(x))")
        assert rc == 0
        assert out == "<class 'complex'>"

    @pytest.mark.xfail(reason="Clython complex number repr differs from CPython")
    def test_uppercase_j_suffix(self):
        out, _, rc = clython_run("print(5J)")
        assert rc == 0
        assert out == "5j"


# ─── Extended Section 2.8 Tests (from test_section_2_8_operators_delimiters.py) ───


class TestSection28ArithmeticExtended:
    """2.8: Extended arithmetic operator tests."""

    def test_unary_plus(self):
        out, _, rc = clython_run("print(+5)")
        assert rc == 0
        assert out == "5"

    def test_unary_minus(self):
        out, _, rc = clython_run("print(-5)")
        assert rc == 0
        assert out == "-5"

    def test_bitwise_not(self):
        out, _, rc = clython_run("print(~0)")
        assert rc == 0
        assert out == "-1"

    def test_operator_precedence_power_over_multiply(self):
        out, _, rc = clython_run("print(2 ** 3 * 2)")
        assert rc == 0
        assert out == "16"

    def test_operator_precedence_multiply_over_add(self):
        out, _, rc = clython_run("print(2 + 3 * 4)")
        assert rc == 0
        assert out == "14"

    def test_power_right_associative(self):
        out, _, rc = clython_run("print(2 ** 3 ** 2)")
        assert rc == 0
        assert out == "512"

    def test_left_associative_subtraction(self):
        out, _, rc = clython_run("print(10 - 3 - 2)")
        assert rc == 0
        assert out == "5"

    def test_left_associative_division(self):
        out, _, rc = clython_run("print(100 / 10 / 2)")
        assert rc == 0
        assert out == "5.0"

    def test_negative_power(self):
        """Unary minus has lower precedence than **."""
        out, _, rc = clython_run("print(-2 ** 2)")
        assert rc == 0
        assert out == "-4"


class TestSection28ComparisonExtended:
    """2.8: Extended comparison operator tests."""

    def test_equality(self):
        out, _, rc = clython_run("print(1 == 1)")
        assert rc == 0
        assert out == "True"

    def test_inequality(self):
        out, _, rc = clython_run("print(1 != 2)")
        assert rc == 0
        assert out == "True"

    def test_less_than(self):
        out, _, rc = clython_run("print(1 < 2)")
        assert rc == 0
        assert out == "True"

    def test_greater_than(self):
        out, _, rc = clython_run("print(2 > 1)")
        assert rc == 0
        assert out == "True"

    def test_less_equal(self):
        out, _, rc = clython_run("print(2 <= 2)")
        assert rc == 0
        assert out == "True"

    def test_greater_equal(self):
        out, _, rc = clython_run("print(2 >= 2)")
        assert rc == 0
        assert out == "True"

    def test_chained_less_less_equal(self):
        out, _, rc = clython_run("print(1 < 2 <= 3)")
        assert rc == 0
        assert out == "True"

    def test_chained_equals(self):
        out, _, rc = clython_run("print(1 == 1 == 1)")
        assert rc == 0
        assert out == "True"

    def test_is_not_operator(self):
        out, _, rc = clython_run("print(1 is not None)")
        assert rc == 0
        assert out == "True"


class TestSection28LogicalExtended:
    """2.8: Extended logical operator tests."""

    def test_and_short_circuit(self):
        out, _, rc = clython_run("print(False and 1/0)")
        assert rc == 0
        assert out == "False"

    def test_or_short_circuit(self):
        out, _, rc = clython_run("print(True or 1/0)")
        assert rc == 0
        assert out == "True"

    def test_not_false(self):
        out, _, rc = clython_run("print(not False)")
        assert rc == 0
        assert out == "True"

    def test_logical_precedence_not_over_and(self):
        out, _, rc = clython_run("print(not True and False)")
        assert rc == 0
        assert out == "False"

    def test_logical_precedence_and_over_or(self):
        out, _, rc = clython_run("print(True or False and False)")
        assert rc == 0
        assert out == "True"


class TestSection28BitwiseExtended:
    """2.8: Extended bitwise operator tests."""

    def test_bitwise_not_value(self):
        out, _, rc = clython_run("print(~0b1100)")
        assert rc == 0
        assert out == "-13"

    def test_bitwise_precedence_and_over_xor(self):
        """& binds tighter than ^."""
        out, _, rc = clython_run("print(0b1111 ^ 0b1100 & 0b1010)")
        assert rc == 0
        assert out == "7"

    def test_bitwise_precedence_xor_over_or(self):
        """^ binds tighter than |."""
        out, _, rc = clython_run("print(0b1000 | 0b0100 ^ 0b0010)")
        assert rc == 0
        assert out == "14"

    def test_shift_precedence_over_bitwise(self):
        """<< binds tighter than &."""
        out, _, rc = clython_run("print(0xFF & 1 << 4)")
        assert rc == 0
        assert out == "16"


class TestSection28DelimitersExtended:
    """2.8: Extended delimiter tests."""

    def test_nested_parentheses(self):
        out, _, rc = clython_run("print(((1 + 2) * 3))")
        assert rc == 0
        assert out == "9"

    def test_nested_lists(self):
        out, _, rc = clython_run("print([[1, 2], [3, 4]])")
        assert rc == 0
        assert out == "[[1, 2], [3, 4]]"

    def test_empty_list(self):
        out, _, rc = clython_run("print([])")
        assert rc == 0
        assert out == "[]"

    def test_empty_dict(self):
        out, _, rc = clython_run("print({})")
        assert rc == 0
        assert out == "{}"

    def test_empty_tuple(self):
        out, _, rc = clython_run("print(())")
        assert rc == 0
        assert out == "()"

    def test_slice_with_step(self):
        out, _, rc = clython_run("print([0,1,2,3,4,5][::2])")
        assert rc == 0
        assert out == "[0, 2, 4]"

    def test_negative_index(self):
        out, _, rc = clython_run("print([1,2,3][-1])")
        assert rc == 0
        assert out == "3"

    def test_tuple_unpacking(self):
        out, _, rc = clython_run("a, b = 1, 2\nprint(a, b)")
        assert rc == 0
        assert out == "1 2"

    def test_chained_assignment(self):
        out, _, rc = clython_run("a = b = c = 1\nprint(a, b, c)")
        assert rc == 0
        assert out == "1 1 1"

    def test_list_comprehension(self):
        out, _, rc = clython_run("print([x*2 for x in range(5)])")
        assert rc == 0
        assert out == "[0, 2, 4, 6, 8]"

    def test_dict_comprehension(self):
        out, _, rc = clython_run("print({k: k*2 for k in range(3)})")
        assert rc == 0
        assert out == "{0: 0, 1: 2, 2: 4}"

    def test_lambda_expression(self):
        out, _, rc = clython_run("f = lambda x: x + 1\nprint(f(5))")
        assert rc == 0
        assert out == "6"

    def test_decorator_syntax(self):
        src = "def deco(f):\n    return f\n@deco\ndef foo():\n    return 42\nprint(foo())"
        out, _, rc = clython_run(src)
        assert rc == 0
        assert out == "42"

    def test_annotated_assignment(self):
        out, _, rc = clython_run("x: int = 42\nprint(x)")
        assert rc == 0
        assert out == "42"


class TestSection28OperatorErrors:
    """2.8: Error conditions for operators."""

    @pytest.mark.xfail(reason="Clython does not reject incomplete expression 'x = 1 +'")
    def test_incomplete_expression_plus(self):
        _, _, rc = clython_run("x = 1 +")
        assert rc != 0

    def test_mismatched_brackets(self):
        _, _, rc = clython_run("x = [1, 2, 3)")
        assert rc != 0

    def test_mismatched_parens(self):
        _, _, rc = clython_run("x = (1, 2, 3]")
        assert rc != 0


class TestSection28OperatorWithTypes:
    """2.8: Operators with various operand types."""

    def test_string_addition(self):
        out, _, rc = clython_run("print('hello' + ' ' + 'world')")
        assert rc == 0
        assert out == "hello world"

    def test_list_addition(self):
        out, _, rc = clython_run("print([1] + [2])")
        assert rc == 0
        assert out == "[1, 2]"

    def test_string_multiply(self):
        out, _, rc = clython_run("print('ab' * 3)")
        assert rc == 0
        assert out == "ababab"

    def test_int_float_comparison(self):
        out, _, rc = clython_run("print(1 < 2.0)")
        assert rc == 0
        assert out == "True"

    def test_none_identity(self):
        out, _, rc = clython_run("print(None is None)")
        assert rc == 0
        assert out == "True"
