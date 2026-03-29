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
