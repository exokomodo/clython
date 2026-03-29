"""
Clython Runtime Tests: Section 6.16 - Evaluation Order

Tests evaluation order semantics via the Clython binary.
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


def test_left_to_right_addition():
    """Verify left-to-right evaluation for addition chain."""
    source = """
log = []
def v(n):
    log.append(n)
    return n
result = v(1) + v(2) + v(3)
print(log)
print(result)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "[1, 2, 3]\n6"


def test_left_to_right_subtraction():
    source = """
log = []
def v(n):
    log.append(n)
    return n
result = v(10) - v(3) - v(2)
print(log)
print(result)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "[10, 3, 2]\n5"


def test_function_args_left_to_right():
    source = """
log = []
def capture(n):
    log.append(n)
    return n
def func(a, b, c):
    return a + b + c
func(capture(1), capture(2), capture(3))
print(log)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "[1, 2, 3]"


def test_boolean_and_short_circuit():
    source = """
called = []
def f1():
    called.append('f1')
    return False
def f2():
    called.append('f2')
    return True
result = f1() and f2()
print(called)
print(result)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "['f1']\nFalse"


def test_boolean_or_short_circuit():
    source = """
called = []
def f1():
    called.append('f1')
    return True
def f2():
    called.append('f2')
    return False
result = f1() or f2()
print(called)
print(result)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "['f1']\nTrue"


def test_boolean_and_evaluates_second_when_first_true():
    source = """
called = []
def f1():
    called.append('f1')
    return True
def f2():
    called.append('f2')
    return True
result = f1() and f2()
print(called)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "['f1', 'f2']"


def test_boolean_or_evaluates_second_when_first_false():
    source = """
called = []
def f1():
    called.append('f1')
    return False
def f2():
    called.append('f2')
    return True
result = f1() or f2()
print(called)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "['f1', 'f2']"


def test_conditional_expression_evaluates_condition_first():
    source = """
log = []
def cond():
    log.append('cond')
    return True
def t():
    log.append('true')
    return 1
def f():
    log.append('false')
    return 2
result = t() if cond() else f()
print(log)
print(result)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "['cond', 'true']\n1"


def test_conditional_false_branch_not_evaluated():
    source = """
log = []
def cond():
    log.append('cond')
    return False
def t():
    log.append('true')
    return 1
def f():
    log.append('false')
    return 2
result = t() if cond() else f()
print(log)
print(result)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "['cond', 'false']\n2"


def test_arithmetic_precedence_mul_before_add():
    out, err, rc = clython_run("print(2 + 3 * 4)")
    assert rc == 0
    assert out == "14"


def test_parentheses_override_precedence():
    out, err, rc = clython_run("print((2 + 3) * 4)")
    assert rc == 0
    assert out == "20"


def test_comparison_chaining():
    out, err, rc = clython_run("print(1 < 2 < 3)")
    assert rc == 0
    assert out == "True"


def test_comparison_chaining_short_circuits():
    source = """
log = []
def v(n):
    log.append(n)
    return n
# 1 < 2 is True, so 2 == 3 is checked, which is False
result = v(1) < v(2) == v(3)
print(result)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "False"


def test_nested_function_calls_inside_out():
    source = """
log = []
def inner(x):
    log.append(('inner', x))
    return x * 2
def outer(x):
    log.append(('outer', x))
    return x + 1
result = outer(inner(5))
print(result)
print(log)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "11\n[('inner', 5), ('outer', 10)]"


def test_attribute_access_left_to_right():
    source = """
class Obj:
    def method(self):
        return self
    
    def get_val(self):
        return 42
o = Obj()
print(o.method().get_val())
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "42"


def test_subscript_evaluates_container_then_index():
    source = """
log = []
def make_list():
    log.append('list')
    return [10, 20, 30]
def get_index():
    log.append('index')
    return 1
result = make_list()[get_index()]
print(result)
print(log)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "20\n['list', 'index']"


def test_listcomp_evaluates_iterable_first():
    source = """
log = []
def source():
    log.append('source')
    return [1, 2, 3]
def transform(x):
    log.append(x)
    return x * 2
result = [transform(x) for x in source()]
print(result)
# source should appear first in log
print(log[0])
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "[2, 4, 6]\nsource"


def test_not_has_higher_precedence_than_and():
    out, err, rc = clython_run("print(not True and True)")
    assert rc == 0
    assert out == "False"


def test_not_has_higher_precedence_than_or():
    out, err, rc = clython_run("print(not False or False)")
    assert rc == 0
    assert out == "True"


def test_unary_minus_precedence():
    out, err, rc = clython_run("print(-2 ** 2)")
    # In Python, -2**2 == -(2**2) == -4, not (-2)**2 == 4
    assert rc == 0
    assert out == "-4"


def test_multiple_assignments_evaluate_rhs_first():
    """All RHS expressions are evaluated before any assignments."""
    source = """
a = 1
b = 2
a, b = b, a
print(a, b)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "2 1"


def test_walrus_operator_evaluation_order():
    source = """
data = [1, 2, 3, 4, 5]
if n := len(data):
    print(n)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "5"
