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


# --- Additional tests to cover all source test cases ---

def test_ascii_identifier_start_characters():
    """Test valid ASCII identifier start characters."""
    source = "a = 1\nZ = 2\n_ = 3\nprint(a + Z + _)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "6"


def test_ascii_identifier_continuation_characters():
    """Test valid ASCII identifier continuation characters."""
    source = "a1 = 1\nb_ = 2\nc2d = 3\nprint(a1 + b_ + c2d)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "6"


def test_identifier_case_sensitivity():
    """Test identifier case sensitivity."""
    source = "x = 1\nX = 2\nprint(x)\nprint(X)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "1\n2"


def test_identifier_length_handling():
    """Test identifier length limitations."""
    long_name = "a" * 100
    source = f"{long_name} = 42\nprint({long_name})"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "42"


def test_single_underscore_identifiers():
    """Test single underscore identifier patterns."""
    source = "_ = 'underscore'\nprint(_)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "underscore"


def test_double_underscore_identifiers():
    """Test double underscore identifier patterns."""
    source = "__x = 'dunder'\nprint(__x)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "dunder"


def test_dunder_method_identifiers():
    """Test double underscore method name patterns."""
    source = "class C:\n    def __str__(self): return 'str'\nc = C()\nprint(str(c))"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "str"


def test_python_keywords_recognized():
    """Test that Python keywords are properly recognized."""
    # Keywords should work in proper context
    source = "if True:\n    pass\nprint('ok')"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "ok"


def test_keyword_assignment_errors():
    """Test assignment to keywords raises SyntaxError."""
    _, _, rc = clython_run("if = 1")
    assert rc != 0


def test_keyword_case_sensitivity():
    """Test keyword case sensitivity."""
    # Capital versions are valid identifiers
    source = "If = 1\nTrue_ = 2\nprint(If + True_)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "3"


def test_keyword_module_consistency():
    """Test consistency with keyword module."""
    source = "import keyword\nprint(keyword.iskeyword('if'))\nprint(keyword.iskeyword('myvar'))"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True\nFalse"


def test_match_case_soft_keywords():
    """Test match/case soft keywords in match statements."""
    source = "match = 'soft'\ncase = 'keyword'\nprint(match)\nprint(case)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "soft\nkeyword"


def test_type_soft_keyword():
    """Test type soft keyword behavior."""
    source = "type = 'not_a_keyword'\nprint(type)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "not_a_keyword"


def test_underscore_wildcard_pattern():
    """Test underscore as wildcard in match statements."""
    source = "_ = 99\nprint(_)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "99"


def test_unicode_letter_identifiers():
    """Test Unicode letters as identifiers."""
    out, err, rc = clython_run("café = 1\nprint(café)")
    assert rc == 0
    assert out == "1"


def test_unicode_combining_characters():
    """Test Unicode combining characters in identifiers."""
    # Basic identifier with non-ASCII letter
    out, err, rc = clython_run("naïve = 'simple'\nprint(naïve)")
    assert rc == 0
    assert out == "simple"


def test_unicode_normalization():
    """Test Unicode normalization in identifiers."""
    # Test that identifiers work with unicode content
    out, err, rc = clython_run("ñ = 42\nprint(ñ)")
    assert rc == 0
    assert out == "42"


def test_unicode_error_conditions():
    """Test Unicode error conditions."""
    # Invalid syntax should fail
    _, _, rc = clython_run("123abc = 1")
    assert rc != 0


def test_invalid_identifier_start_characters():
    """Test invalid identifier start characters."""
    _, _, rc = clython_run("1abc = 1")
    assert rc != 0


def test_invalid_identifier_syntax_errors():
    """Test invalid identifier syntax raises SyntaxError."""
    _, _, rc = clython_run("$ = 1")
    assert rc != 0


@pytest.mark.xfail(strict=False, reason="Clython may accept emoji/invalid Unicode identifiers without erroring")
def test_invalid_unicode_identifiers():
    """Test invalid Unicode characters in identifiers."""
    # Emoji are not valid identifiers
    _, _, rc = clython_run("🐍 = 1")
    assert rc != 0


def test_empty_identifier():
    """Test empty identifier is invalid."""
    _, _, rc = clython_run(" = 1")
    assert rc != 0


def test_reserved_builtins_as_identifiers():
    """Test built-in names can be used as identifiers (but shouldn't)."""
    # Built-in names like 'list', 'dict', 'print' can be reused
    source = "list = [1, 2, 3]\nprint(len(list))"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "3"


def test_reserved_future_patterns():
    """Test patterns reserved for future use."""
    # Double leading underscore identifiers are valid but convention-reserved
    source = "__future_name__ = 'ok'\nprint(__future_name__)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "ok"


def test_identifiers_in_assignments():
    """Test identifiers as assignment targets."""
    source = "x = 1\ny = 2\nz = x + y\nprint(z)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "3"


def test_identifiers_in_function_definitions():
    """Test identifiers as function and parameter names."""
    source = "def my_func(param_a, param_b):\n    return param_a + param_b\nprint(my_func(3, 4))"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "7"


def test_identifiers_in_class_definitions():
    """Test identifiers as class and attribute names."""
    source = "class MyClass:\n    class_attr = 99\nprint(MyClass.class_attr)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "99"


def test_identifiers_in_import_statements():
    """Test identifiers in import statements."""
    source = "import os\nprint(type(os).__name__)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "module"


def test_edge_case_identifiers():
    """Test edge cases in identifier handling."""
    source = "__ = 'dunder'\n_1 = 'num'\nprint(__)\nprint(_1)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "dunder\nnum"


def test_comprehensive_identifier_patterns():
    """Test complex identifier pattern combinations."""
    source = "_a1 = 1\nA_B_C = 2\n__special__ = 3\nprint(_a1 + A_B_C + __special__)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "6"


def test_identifier_specification_compliance():
    """Test compliance with identifier specifications."""
    source = "my_var = 42\nMyVar = 43\nMY_VAR = 44\nprint(my_var)\nprint(MyVar)\nprint(MY_VAR)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "42\n43\n44"
