"""
Clython runtime conformance tests for Section 2.3: Names, Identifiers, and Keywords.

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


def test_simple_ascii_identifier_assignment():
    """Basic ASCII identifier can be assigned and printed."""
    out, err, rc = clython_run("variable = 42\nprint(variable)")
    assert rc == 0
    assert out == "42"


def test_underscore_identifier():
    """Underscore-prefixed identifier works."""
    out, err, rc = clython_run("_private = 99\nprint(_private)")
    assert rc == 0
    assert out == "99"


def test_double_underscore_identifier():
    """Double-underscore identifier works."""
    out, err, rc = clython_run("__special = 'hello'\nprint(__special)")
    assert rc == 0
    assert out == "hello"


def test_identifier_with_digits():
    """Identifier with digits in continuation works."""
    out, err, rc = clython_run("var1 = 1\nvar2 = 2\nprint(var1 + var2)")
    assert rc == 0
    assert out == "3"


def test_snake_case_identifier():
    """Snake-case identifier works."""
    out, err, rc = clython_run("snake_case_var = 'snake'\nprint(snake_case_var)")
    assert rc == 0
    assert out == "snake"


def test_camel_case_identifier():
    """CamelCase identifier works."""
    out, err, rc = clython_run("CamelCaseVar = 'camel'\nprint(CamelCaseVar)")
    assert rc == 0
    assert out == "camel"


def test_case_sensitivity():
    """Identifiers are case-sensitive."""
    source = "name = 1\nName = 2\nNAME = 3\nprint(name, Name, NAME)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "1 2 3"


def test_keyword_false():
    """False literal evaluates correctly."""
    out, err, rc = clython_run("print(False)")
    assert rc == 0
    assert out == "False"


def test_keyword_true():
    """True literal evaluates correctly."""
    out, err, rc = clython_run("print(True)")
    assert rc == 0
    assert out == "True"


def test_keyword_none():
    """None literal evaluates correctly."""
    out, err, rc = clython_run("print(None)")
    assert rc == 0
    assert out == "None"


def test_keyword_cannot_be_assigned():
    """Keywords cannot be used as identifiers (assignment to 'if' should fail)."""
    _, _, rc = clython_run("if = 1")
    assert rc != 0


def test_keyword_for_cannot_be_assigned():
    """'for' keyword cannot be used as identifier."""
    _, _, rc = clython_run("for = 1")
    assert rc != 0


def test_keyword_class_cannot_be_assigned():
    """'class' keyword cannot be used as identifier."""
    _, _, rc = clython_run("class = 1")
    assert rc != 0


def test_builtin_name_as_identifier():
    """Built-in names can be overridden (though inadvisable)."""
    # 'int' is not a keyword — can be shadowed
    out, err, rc = clython_run("int = 'shadowed'\nprint(int)")
    assert rc == 0
    assert out == "shadowed"


def test_identifier_in_function_def():
    """Identifiers work as function names and parameters."""
    source = "def my_func(param_one):\n    return param_one * 2\nprint(my_func(5))"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "10"


def test_identifier_in_class_def():
    """Identifiers work as class names."""
    source = "class MyClass:\n    x = 42\nprint(MyClass.x)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "42"


def test_single_underscore_identifier():
    """Single underscore is a valid identifier."""
    out, err, rc = clython_run("_ = 'throwaway'\nprint(_)")
    assert rc == 0
    assert out == "throwaway"


@pytest.mark.xfail(reason="Name mangling (__name -> _Class__name) not yet implemented in Clython")
def test_dunder_identifier_in_class():
    """Dunder identifier is valid in class scope."""
    source = "class C:\n    __init_val = 10\nprint(C._C__init_val)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "10"


def test_long_identifier():
    """Long identifiers work."""
    name = "a_very_long_identifier_name_that_goes_on_and_on_and_on_for_testing"
    source = f"{name} = 'long'\nprint({name})"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "long"


def test_unicode_identifier():
    """Unicode letters are valid identifiers per spec."""
    out, err, rc = clython_run("café = 'coffee'\nprint(café)")
    assert rc == 0
    assert out == "coffee"


def test_digit_start_identifier_is_error():
    """Identifier starting with digit is a syntax error."""
    _, _, rc = clython_run("1invalid = 1")
    assert rc != 0


def test_soft_keyword_match_as_identifier():
    """'match' is a soft keyword and can be used as a regular identifier."""
    out, err, rc = clython_run("match = 'value'\nprint(match)")
    assert rc == 0
    assert out == "value"


def test_soft_keyword_case_as_identifier():
    """'case' is a soft keyword and can be used as a regular identifier."""
    out, err, rc = clython_run("case = 'value'\nprint(case)")
    assert rc == 0
    assert out == "value"


def test_identifier_reassignment():
    """Identifiers can be reassigned."""
    source = "x = 1\nx = 2\nx = 'three'\nprint(x)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "three"


def test_and_keyword_cannot_be_assigned():
    """'and' keyword cannot be used as identifier."""
    _, _, rc = clython_run("and = 1")
    assert rc != 0
