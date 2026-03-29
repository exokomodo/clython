"""
Section 7.1: Expression Statements - Clython Runtime Test Suite

Tests that Clython actually executes expression statements correctly at runtime.
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


def test_function_call_statement():
    """Function call as expression statement (side effect)"""
    out, err, rc = clython_run("print('hello')")
    assert rc == 0
    assert out == "hello"


def test_method_call_statement():
    """Method call as expression statement"""
    out, err, rc = clython_run(
        "lst = []\n"
        "lst.append(1)\n"
        "lst.append(2)\n"
        "print(lst)"
    )
    assert rc == 0
    assert out == "[1, 2]"


def test_chained_method_call():
    """Chained method calls as expression statement"""
    out, err, rc = clython_run(
        "result = 'hello world'.upper().split()\n"
        "print(result)"
    )
    assert rc == 0
    assert out == "['HELLO', 'WORLD']"


def test_literal_as_statement():
    """Literal expression as statement (no error)"""
    out, err, rc = clython_run("42\nprint('ok')")
    assert rc == 0
    assert out == "ok"


def test_binary_operation_statement():
    """Binary operation as expression statement"""
    out, err, rc = clython_run(
        "x = 5\n"
        "y = 3\n"
        "x + y\n"  # result discarded
        "print('done')"
    )
    assert rc == 0
    assert out == "done"


def test_comparison_expression_statement():
    """Comparison expression as statement"""
    out, err, rc = clython_run(
        "x = 5\n"
        "x > 3\n"  # result discarded
        "print('ok')"
    )
    assert rc == 0
    assert out == "ok"


def test_list_comprehension_statement():
    """List comprehension as expression statement"""
    out, err, rc = clython_run(
        "[x * 2 for x in range(5)]\n"
        "print('ok')"
    )
    assert rc == 0
    assert out == "ok"


def test_generator_expression_statement():
    """Generator expression as expression statement"""
    out, err, rc = clython_run(
        "(x * 2 for x in range(5))\n"
        "print('ok')"
    )
    assert rc == 0
    assert out == "ok"


def test_conditional_expression_statement():
    """Conditional (ternary) expression as statement"""
    out, err, rc = clython_run(
        "x = 5\n"
        "result = 'pos' if x > 0 else 'non-pos'\n"
        "print(result)"
    )
    assert rc == 0
    assert out == "pos"


def test_lambda_expression_statement():
    """Lambda expression used as value"""
    out, err, rc = clython_run(
        "f = lambda x: x * 3\n"
        "print(f(7))"
    )
    assert rc == 0
    assert out == "21"


def test_subscript_expression_statement():
    """Subscript expression as statement"""
    out, err, rc = clython_run(
        "lst = [10, 20, 30]\n"
        "lst[0]\n"  # result discarded
        "print(lst[1])"
    )
    assert rc == 0
    assert out == "20"


def test_attribute_access_statement():
    """Attribute access as expression statement"""
    out, err, rc = clython_run(
        "x = 'hello'\n"
        "x.upper\n"  # result discarded
        "print(x.upper())"
    )
    assert rc == 0
    assert out == "HELLO"


def test_nested_function_call():
    """Nested function calls"""
    out, err, rc = clython_run("print(str(len([1,2,3])))")
    assert rc == 0
    assert out == "3"


def test_arithmetic_expressions():
    """Arithmetic expression values"""
    out, err, rc = clython_run(
        "print(2 + 3 * 4)\n"
        "print(10 // 3)\n"
        "print(10 % 3)\n"
        "print(2 ** 8)"
    )
    assert rc == 0
    assert out == "14\n3\n1\n256"


def test_logical_expression_statement():
    """Logical operators in expression statement"""
    out, err, rc = clython_run(
        "print(True and False)\n"
        "print(True or False)\n"
        "print(not True)"
    )
    assert rc == 0
    assert out == "False\nTrue\nFalse"


def test_bitwise_expression_statement():
    """Bitwise operators"""
    out, err, rc = clython_run(
        "print(0b1010 | 0b0101)\n"
        "print(0b1010 & 0b1100)\n"
        "print(0b1010 ^ 0b1100)\n"
        "print(1 << 4)\n"
        "print(16 >> 2)"
    )
    assert rc == 0
    assert out == "15\n8\n6\n16\n4"


def test_unary_operation_statement():
    """Unary operators"""
    out, err, rc = clython_run(
        "x = 5\n"
        "print(-x)\n"
        "print(+x)\n"
        "print(~x)"
    )
    assert rc == 0
    assert out == "-5\n5\n-6"


def test_dict_comprehension_statement():
    """Dict comprehension as statement"""
    out, err, rc = clython_run(
        "result = {k: k**2 for k in range(4)}\n"
        "print(result)"
    )
    assert rc == 0
    assert out == "{0: 0, 1: 1, 2: 4, 3: 9}"


def test_set_comprehension_statement():
    """Set comprehension as statement"""
    out, err, rc = clython_run(
        "result = {x % 3 for x in range(9)}\n"
        "print(sorted(result))"
    )
    assert rc == 0
    assert out == "[0, 1, 2]"


def test_walrus_operator_expression():
    """Walrus operator := as expression"""
    out, err, rc = clython_run(
        "data = [1, 2, 3, 4, 5]\n"
        "if (n := len(data)) > 3:\n"
        "    print('long:', n)"
    )
    assert rc == 0
    assert out == "long: 5"


def test_multiple_print_statements():
    """Multiple print calls (expression statements with side effects)"""
    out, err, rc = clython_run(
        "print(1)\n"
        "print(2)\n"
        "print(3)"
    )
    assert rc == 0
    assert out == "1\n2\n3"


def test_string_expression_docstring_like():
    """String literal expression statement (docstring-like)"""
    out, err, rc = clython_run(
        "'This is a string expression'\n"
        "print('after')"
    )
    assert rc == 0
    assert out == "after"


def test_complex_expression_sum_generator():
    """sum() with generator expression"""
    out, err, rc = clython_run("print(sum(x * x for x in range(5)))")
    assert rc == 0
    assert out == "30"


def test_expression_in_loop():
    """Expression statements inside loops"""
    out, err, rc = clython_run(
        "results = []\n"
        "for i in range(5):\n"
        "    results.append(i * 2)\n"
        "print(results)"
    )
    assert rc == 0
    assert out == "[0, 2, 4, 6, 8]"
