"""
Clython runtime tests for Section 6.11: Boolean Operations.

Tests and, or, not operators through the Clython binary.
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


# ---------------------------------------------------------------------------
# 'not' operator
# ---------------------------------------------------------------------------

def test_not_true():
    """not True == False."""
    out, err, rc = clython_run("print(not True)")
    assert rc == 0
    assert out == "False"


def test_not_false():
    """not False == True."""
    out, err, rc = clython_run("print(not False)")
    assert rc == 0
    assert out == "True"


def test_not_zero():
    """not 0 == True (0 is falsy)."""
    out, err, rc = clython_run("print(not 0)")
    assert rc == 0
    assert out == "True"


def test_not_nonzero():
    """not 1 == False (nonzero is truthy)."""
    out, err, rc = clython_run("print(not 1)")
    assert rc == 0
    assert out == "False"


def test_not_empty_list():
    """not [] == True (empty list is falsy)."""
    out, err, rc = clython_run("print(not [])")
    assert rc == 0
    assert out == "True"


def test_not_nonempty_list():
    """not [1] == False."""
    out, err, rc = clython_run("print(not [1])")
    assert rc == 0
    assert out == "False"


def test_not_none():
    """not None == True."""
    out, err, rc = clython_run("print(not None)")
    assert rc == 0
    assert out == "True"


def test_double_not():
    """not not True == True."""
    out, err, rc = clython_run("print(not not True)")
    assert rc == 0
    assert out == "True"


# ---------------------------------------------------------------------------
# 'and' operator — return value semantics
# ---------------------------------------------------------------------------

def test_and_both_true():
    """True and True returns second (truthy) value."""
    out, err, rc = clython_run("print(True and True)")
    assert rc == 0
    assert out == "True"


def test_and_first_false():
    """False and True short-circuits and returns False."""
    out, err, rc = clython_run("print(False and True)")
    assert rc == 0
    assert out == "False"


def test_and_returns_first_falsy():
    """x and y returns x if x is falsy."""
    out, err, rc = clython_run("print(0 and 99)")
    assert rc == 0
    assert out == "0"


def test_and_returns_last_truthy():
    """x and y returns y if x is truthy."""
    out, err, rc = clython_run("print(1 and 2)")
    assert rc == 0
    assert out == "2"


def test_and_short_circuit():
    """and short-circuits: side effect in second operand not reached."""
    source = (
        "side = []\n"
        "def effect(): side.append(1); return True\n"
        "result = False and effect()\n"
        "print(side)\n"
    )
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "[]"


def test_and_chained():
    """Chained and returns False if any operand is falsy."""
    out, err, rc = clython_run("print(1 and 2 and 0 and 4)")
    assert rc == 0
    assert out == "0"


# ---------------------------------------------------------------------------
# 'or' operator — return value semantics
# ---------------------------------------------------------------------------

def test_or_both_true():
    """True or True returns first truthy value."""
    out, err, rc = clython_run("print(True or False)")
    assert rc == 0
    assert out == "True"


def test_or_first_truthy():
    """x or y returns x if x is truthy (short-circuit)."""
    out, err, rc = clython_run("print(1 or 99)")
    assert rc == 0
    assert out == "1"


def test_or_first_falsy():
    """x or y returns y if x is falsy."""
    out, err, rc = clython_run("print(0 or 42)")
    assert rc == 0
    assert out == "42"


def test_or_both_false():
    """x or y returns y if both falsy."""
    out, err, rc = clython_run("print(0 or False)")
    assert rc == 0
    assert out == "False"


def test_or_short_circuit():
    """or short-circuits when first operand is truthy."""
    source = (
        "side = []\n"
        "def effect(): side.append(1); return True\n"
        "result = True or effect()\n"
        "print(side)\n"
    )
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "[]"


def test_or_chained():
    """Chained or returns first truthy value."""
    out, err, rc = clython_run("print(0 or False or 3 or 4)")
    assert rc == 0
    assert out == "3"


# ---------------------------------------------------------------------------
# Precedence: not > and > or
# ---------------------------------------------------------------------------

def test_not_before_and():
    """not applies before and: not False and True == True."""
    out, err, rc = clython_run("print(not False and True)")
    assert rc == 0
    assert out == "True"


def test_and_before_or():
    """and binds tighter than or: False and True or True == True."""
    out, err, rc = clython_run("print(False and True or True)")
    assert rc == 0
    assert out == "True"


def test_parentheses_override():
    """Parentheses override boolean precedence."""
    out, err, rc = clython_run("print(not (True and False))")
    assert rc == 0
    assert out == "True"


# ---------------------------------------------------------------------------
# Boolean with comparison operators
# ---------------------------------------------------------------------------

def test_and_with_comparison():
    """and combined with comparisons."""
    out, err, rc = clython_run("x = 5; print(x > 0 and x < 10)")
    assert rc == 0
    assert out == "True"


def test_or_with_comparison():
    """or combined with comparisons."""
    out, err, rc = clython_run("x = 15; print(x < 0 or x > 10)")
    assert rc == 0
    assert out == "True"


def test_boolean_in_list_comprehension():
    """Boolean expression used as filter in comprehension."""
    out, err, rc = clython_run("print([x for x in range(10) if x > 3 and x < 7])")
    assert rc == 0
    assert out == "[4, 5, 6]"
