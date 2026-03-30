"""
Clython runtime conformance tests for Section 2.8: Operators and Delimiters.

These tests run code through the Clython binary and verify output/behavior.
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


def test_addition():
    out, err, rc = clython_run("print(1 + 2)")
    assert rc == 0
    assert out == "3"


def test_subtraction():
    out, err, rc = clython_run("print(5 - 3)")
    assert rc == 0
    assert out == "2"


def test_multiplication():
    out, err, rc = clython_run("print(4 * 3)")
    assert rc == 0
    assert out == "12"


def test_division():
    out, err, rc = clython_run("print(7 / 2)")
    assert rc == 0
    assert out == "3.5"


def test_floor_division():
    out, err, rc = clython_run("print(7 // 2)")
    assert rc == 0
    assert out == "3"


def test_modulo():
    out, err, rc = clython_run("print(7 % 3)")
    assert rc == 0
    assert out == "1"


def test_power():
    out, err, rc = clython_run("print(2 ** 10)")
    assert rc == 0
    assert out == "1024"


def test_bitwise_and():
    out, err, rc = clython_run("print(0b1100 & 0b1010)")
    assert rc == 0
    assert out == "8"


def test_bitwise_or():
    out, err, rc = clython_run("print(0b1100 | 0b1010)")
    assert rc == 0
    assert out == "14"


def test_bitwise_xor():
    out, err, rc = clython_run("print(0b1100 ^ 0b1010)")
    assert rc == 0
    assert out == "6"


def test_bitwise_not():
    out, err, rc = clython_run("print(~0)")
    assert rc == 0
    assert out == "-1"


def test_left_shift():
    out, err, rc = clython_run("print(1 << 4)")
    assert rc == 0
    assert out == "16"


def test_right_shift():
    out, err, rc = clython_run("print(16 >> 2)")
    assert rc == 0
    assert out == "4"


def test_comparison_equal():
    out, err, rc = clython_run("print(1 == 1)")
    assert rc == 0
    assert out == "True"


def test_comparison_not_equal():
    out, err, rc = clython_run("print(1 != 2)")
    assert rc == 0
    assert out == "True"


def test_comparison_less_than():
    out, err, rc = clython_run("print(1 < 2)")
    assert rc == 0
    assert out == "True"


def test_comparison_greater_than():
    out, err, rc = clython_run("print(2 > 1)")
    assert rc == 0
    assert out == "True"


def test_comparison_less_equal():
    out, err, rc = clython_run("print(2 <= 2)")
    assert rc == 0
    assert out == "True"


def test_comparison_greater_equal():
    out, err, rc = clython_run("print(3 >= 3)")
    assert rc == 0
    assert out == "True"


def test_logical_and():
    out, err, rc = clython_run("print(True and False)")
    assert rc == 0
    assert out == "False"


def test_logical_or():
    out, err, rc = clython_run("print(False or True)")
    assert rc == 0
    assert out == "True"


def test_logical_not():
    out, err, rc = clython_run("print(not True)")
    assert rc == 0
    assert out == "False"


def test_augmented_add_assign():
    out, err, rc = clython_run("x = 5\nx += 3\nprint(x)")
    assert rc == 0
    assert out == "8"


def test_augmented_sub_assign():
    out, err, rc = clython_run("x = 5\nx -= 3\nprint(x)")
    assert rc == 0
    assert out == "2"


def test_augmented_mul_assign():
    out, err, rc = clython_run("x = 5\nx *= 3\nprint(x)")
    assert rc == 0
    assert out == "15"


def test_augmented_div_assign():
    out, err, rc = clython_run("x = 10\nx /= 4\nprint(x)")
    assert rc == 0
    assert out == "2.5"


def test_augmented_floordiv_assign():
    out, err, rc = clython_run("x = 10\nx //= 3\nprint(x)")
    assert rc == 0
    assert out == "3"


def test_augmented_mod_assign():
    out, err, rc = clython_run("x = 10\nx %= 3\nprint(x)")
    assert rc == 0
    assert out == "1"


def test_augmented_pow_assign():
    out, err, rc = clython_run("x = 2\nx **= 8\nprint(x)")
    assert rc == 0
    assert out == "256"


def test_identity_operator_is():
    out, err, rc = clython_run("x = None\nprint(x is None)")
    assert rc == 0
    assert out == "True"


def test_identity_operator_is_not():
    out, err, rc = clython_run("print(1 is not None)")
    assert rc == 0
    assert out == "True"


def test_membership_operator_in():
    out, err, rc = clython_run("print(2 in [1, 2, 3])")
    assert rc == 0
    assert out == "True"


def test_membership_operator_not_in():
    out, err, rc = clython_run("print(5 not in [1, 2, 3])")
    assert rc == 0
    assert out == "True"


def test_operator_precedence_mul_before_add():
    """Multiplication has higher precedence than addition."""
    out, err, rc = clython_run("print(2 + 3 * 4)")
    assert rc == 0
    assert out == "14"


def test_operator_precedence_pow_before_mul():
    """Power has higher precedence than multiplication."""
    out, err, rc = clython_run("print(2 * 3 ** 2)")
    assert rc == 0
    assert out == "18"


def test_parentheses_override_precedence():
    out, err, rc = clython_run("print((2 + 3) * 4)")
    assert rc == 0
    assert out == "20"


def test_chained_comparison():
    out, err, rc = clython_run("print(1 < 2 < 3)")
    assert rc == 0
    assert out == "True"


def test_list_delimiter():
    out, err, rc = clython_run("x = [1, 2, 3]\nprint(len(x))")
    assert rc == 0
    assert out == "3"


def test_dict_delimiter():
    out, err, rc = clython_run("x = {'a': 1, 'b': 2}\nprint(len(x))")
    assert rc == 0
    assert out == "2"


def test_tuple_delimiter():
    out, err, rc = clython_run("x = (1, 2, 3)\nprint(len(x))")
    assert rc == 0
    assert out == "3"


def test_attribute_access_dot():
    out, err, rc = clython_run("x = 'hello'\nprint(x.upper())")
    assert rc == 0
    assert out == "HELLO"


def test_subscript_delimiter():
    out, err, rc = clython_run("x = [10, 20, 30]\nprint(x[1])")
    assert rc == 0
    assert out == "20"


def test_walrus_operator():
    out, err, rc = clython_run("x = [y := 10]\nprint(y)")
    assert rc == 0
    assert out == "10"


def test_incomplete_operator_is_error():
    """Incomplete operator expression is a syntax error."""
    _, _, rc = clython_run("print(1 +)")
    assert rc != 0


def test_mismatched_brackets_is_error():
    _, _, rc = clython_run("print([1, 2, 3)")
    assert rc != 0


# --- Additional tests to cover all source test cases ---

def test_basic_arithmetic_operators():
    """Test basic arithmetic operators."""
    source = "print(1 + 2)\nprint(5 - 3)\nprint(2 * 4)\nprint(10 / 4)\nprint(10 // 3)\nprint(10 % 3)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "3\n2\n8\n2.5\n3\n1"


def test_unary_arithmetic_operators():
    """Test unary arithmetic operators."""
    source = "x = 5\nprint(-x)\nprint(+x)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "-5\n5"


def test_comparison_operators():
    """Test comparison operators."""
    source = "print(1 < 2)\nprint(2 > 1)\nprint(1 == 1)\nprint(1 != 2)\nprint(2 >= 2)\nprint(1 <= 2)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True\nTrue\nTrue\nTrue\nTrue\nTrue"


def test_logical_binary_operators():
    """Test logical binary operators."""
    source = "print(True and False)\nprint(True or False)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "False\nTrue"


def test_logical_unary_operator():
    """Test logical unary operator."""
    source = "print(not True)\nprint(not False)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "False\nTrue"


def test_bitwise_binary_operators():
    """Test bitwise binary operators."""
    source = "print(0b1010 | 0b0101)\nprint(0b1010 & 0b1100)\nprint(0b1010 ^ 0b1100)\nprint(1 << 4)\nprint(16 >> 2)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "15\n8\n6\n16\n4"


def test_bitwise_unary_operators():
    """Test bitwise unary operator."""
    source = "print(~0)\nprint(~1)\nprint(~(-1))"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "-1\n-2\n0"


def test_augmented_assignment_operators():
    """Test augmented assignment operators."""
    source = "x = 10\nx += 5\nprint(x)\nx -= 3\nprint(x)\nx *= 2\nprint(x)\nx //= 4\nprint(x)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "15\n12\n24\n6"


def test_simple_assignment_operator():
    """Test simple assignment operator."""
    source = "x = 42\nprint(x)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "42"


def test_annotated_assignment_operator():
    """Test annotated assignment operator."""
    source = "x: int = 42\nprint(x)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "42"


def test_assignment_operator_contexts():
    """Test assignment operator in various contexts."""
    source = "a = b = c = 1\nprint(a, b, c)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "1 1 1"


def test_identity_operators():
    """Test identity operators."""
    source = "x = [1, 2]\ny = x\nz = [1, 2]\nprint(x is y)\nprint(x is not z)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True\nTrue"


def test_membership_operators():
    """Test membership operators."""
    source = "lst = [1, 2, 3]\nprint(1 in lst)\nprint(4 not in lst)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True\nTrue"


def test_matrix_multiplication_operator():
    """Test matrix multiplication operator."""
    source = "class M:\n    def __matmul__(self, o): return 'matmul'\na = M()\nprint(a @ a)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "matmul"


def test_grouping_delimiters():
    """Test grouping delimiters."""
    source = "result = (1 + 2) * 3\nprint(result)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "9"


def test_function_delimiters():
    """Test function call delimiters."""
    source = "def f(a, b): return a + b\nprint(f(3, 4))"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "7"


def test_separator_delimiters():
    """Test separator delimiters."""
    source = "a, b, c = 1, 2, 3\nprint(a)\nprint(b)\nprint(c)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "1\n2\n3"


def test_decorator_delimiter():
    """Test decorator delimiter."""
    source = "def deco(f):\n    def wrapper():\n        return f() * 2\n    return wrapper\n@deco\ndef f():\n    return 5\nprint(f())"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "10"


def test_nested_delimiter_structures():
    """Test nested delimiter structures."""
    source = "result = {'key': [1, (2, 3)]}\nprint(result['key'][1][0])"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "2"


def test_arithmetic_operator_precedence():
    """Test arithmetic operator precedence."""
    source = "print(2 + 3 * 4)\nprint((2 + 3) * 4)\nprint(2 ** 3 ** 2)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "14\n20\n512"


def test_bitwise_operator_precedence():
    """Test bitwise operator precedence."""
    source = "print(1 | 2 & 3)\nprint((1 | 2) & 3)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "3\n3"


def test_logical_operator_precedence():
    """Test logical operator precedence."""
    source = "print(True or False and False)\nprint(not True or True)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True\nTrue"


def test_arithmetic_operator_associativity():
    """Test arithmetic operator associativity."""
    source = "print(10 - 3 - 2)\nprint(2 ** 3 ** 2)"  # Left and right assoc
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "5\n512"


def test_chained_comparisons():
    """Test chained comparison operators."""
    source = "print(1 < 2 < 3)\nprint(1 < 2 > 0)\nprint(1 == 1 != 2)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True\nTrue\nTrue"


def test_operator_precedence_validation():
    """Test operator precedence validation."""
    source = "print(2 + 3 * 4 - 1)\nprint(4 * 2 / 8)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "13\n1.0"


def test_operator_with_different_types():
    """Test operators with different types."""
    source = "print(1 + 1.5)\nprint('hi' * 3)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "2.5\nhihihi"


def test_operator_ast_structure_validation():
    """Test operator AST structure validation."""
    source = "x = 1 + 2\nprint(x)\ny = x * 3\nprint(y)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "3\n9"


def test_incomplete_operators():
    """Test incomplete operator expressions are errors."""
    _, _, rc = clython_run("print(1 +)")
    assert rc != 0


def test_invalid_operator_combinations():
    """Test invalid operator combinations."""
    _, _, rc = clython_run("print(1 + * 2)")
    assert rc != 0


def test_invalid_delimiter_usage():
    """Test invalid delimiter usage."""
    _, _, rc = clython_run("print([1, 2, 3)")
    assert rc != 0


def test_comprehensive_operator_expression():
    """Test comprehensive operator expression."""
    # (2+3)*4 - 6//2 + 1 = 5*4 - 3 + 1 = 20 - 3 + 1 = 18
    source = "result = (2 + 3) * 4 - 6 // 2 + 1\nprint(result)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "18"
