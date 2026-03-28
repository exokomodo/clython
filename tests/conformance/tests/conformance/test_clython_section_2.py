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
