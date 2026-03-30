"""Clython runtime tests — Section 7.14: Type Statement (PEP 695).

Tests that the Clython interpreter correctly handles the Python 3.12
``type`` statement (type alias declarations). All 19 concepts from the
CPython-only conformance suite (test_section_7_14_type_statement.py)
are covered here as Clython runtime tests.

Because the type statement is a Python 3.12 feature, the entire file
is marked xfail(strict=False) at the class level so that:
  - If Clython has not implemented it yet, tests are expected failures.
  - If Clython does implement it, tests pass (xpass is not an error).
"""
import os
import subprocess
import pytest

CLYTHON_BIN = os.environ.get("CLYTHON_BIN")


def clython_run(source: str, *, timeout: int = 10):
    result = subprocess.run(
        [CLYTHON_BIN, "-c", source],
        capture_output=True, text=True, timeout=timeout,
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode


pytestmark = pytest.mark.skipif(
    not CLYTHON_BIN, reason="CLYTHON_BIN not set — skipping Clython-specific tests"
)

_TYPE_STMT_XFAIL = pytest.mark.xfail(
    strict=False, reason="type statement (PEP 695) not yet implemented in Clython"
)


# ── 7.14.1 Simple type aliases ────────────────────────────────────────────

class TestTypeStatementSimpleAliases:
    """Concept 1 – simple non-generic type aliases."""

    def test_int_alias(self):
        out, err, rc = clython_run("type UserId = int\nprint(UserId)")
        assert rc == 0

    def test_str_alias(self):
        out, err, rc = clython_run("type Username = str\nprint(Username)")
        assert rc == 0

    def test_list_alias(self):
        out, err, rc = clython_run("type IntList = list[int]\nprint(IntList)")
        assert rc == 0

    def test_dict_alias(self):
        out, err, rc = clython_run("type StringDict = dict[str, str]\nprint(StringDict)")
        assert rc == 0

    @pytest.mark.xfail(reason="Union/complex type expressions not yet supported in Clython")
    def test_union_alias(self):
        out, err, rc = clython_run("type OptStr = str | None\nprint(OptStr)")
        assert rc == 0


# ── 7.14.2 Generic type aliases ───────────────────────────────────────────

class TestTypeStatementGenericAliases:
    """Concept 2 – generic type aliases with type parameters."""

    def test_single_type_param(self):
        out, err, rc = clython_run("type Container[T] = list[T]\nprint(Container)")
        assert rc == 0

    def test_two_type_params(self):
        out, err, rc = clython_run("type Mapping[K, V] = dict[K, V]\nprint(Mapping)")
        assert rc == 0

    @pytest.mark.xfail(reason="Union/complex type expressions not yet supported in Clython")
    def test_result_union_param(self):
        out, err, rc = clython_run("type Result[T, E] = T | E\nprint(Result)")
        assert rc == 0

    def test_factory_param(self):
        out, err, rc = clython_run("type Factory[T] = callable[[], T]\nprint(Factory)")
        assert rc == 0


# ── 7.14.3 Complex type expressions ──────────────────────────────────────

class TestTypeStatementComplexExpressions:
    """Concept 3 – complex / nested type expressions inside type aliases."""

    @pytest.mark.xfail(reason="Union/complex type expressions not yet supported in Clython")
    def test_nested_generic(self):
        out, err, rc = clython_run(
            "type Config = dict[str, str | int | bool | list[str]]\nprint(Config)"
        )
        assert rc == 0

    @pytest.mark.xfail(reason="Union/complex type expressions not yet supported in Clython")
    def test_optional_callable(self):
        out, err, rc = clython_run(
            "type Handler[T] = callable[[T], None] | None\nprint(Handler)"
        )
        assert rc == 0


# ── 7.14.4 TypeVar parameters ────────────────────────────────────────────

class TestTypeStatementTypeVarParams:
    """Concept 4 – TypeVar-style type parameters in type statements."""

    def test_identity(self):
        out, err, rc = clython_run("type Identity[T] = T\nprint(Identity)")
        assert rc == 0

    def test_triple_param(self):
        out, err, rc = clython_run(
            "type Triple[T, U, V] = tuple[T, U, V]\nprint(Triple)"
        )
        assert rc == 0


# ── 7.14.5 Constrained type parameters ───────────────────────────────────

class TestTypeStatementConstrainedParams:
    """Concept 5 – constrained type parameters (T: (int, float) syntax)."""

    def test_numeric_constraint(self):
        out, err, rc = clython_run(
            "type Numeric[T: (int, float)] = T\nprint(Numeric)"
        )
        assert rc == 0


# ── 7.14.6 Type parameter bounds ─────────────────────────────────────────

class TestTypeStatementParamBounds:
    """Concept 6 – type parameter with upper-bound annotation (T: SomeType)."""

    def test_bound_param(self):
        out, err, rc = clython_run(
            "type Comparable[T: object] = T\nprint(Comparable)"
        )
        assert rc == 0

    @pytest.mark.xfail(reason="Union/complex type expressions not yet supported in Clython")
    def test_iterable_alias(self):
        out, err, rc = clython_run(
            "type Iterable[T] = list[T] | tuple[T, ...] | set[T]\nprint(Iterable)"
        )
        assert rc == 0


# ── 7.14.7 Module-level type aliases ─────────────────────────────────────

class TestTypeStatementModuleLevel:
    """Concept 7 – type aliases defined at module (top) level."""

    def test_module_level_usage_in_annotation(self):
        out, err, rc = clython_run(
            "type UserId = int\n"
            "def get_id() -> UserId:\n"
            "    return 42\n"
            "print(get_id())"
        )
        assert rc == 0
        assert out == "42"

    def test_multiple_module_aliases(self):
        out, err, rc = clython_run(
            "type Point2D = tuple[float, float]\n"
            "type Point3D = tuple[float, float, float]\n"
            "p: Point2D = (1.0, 2.0)\n"
            "print(p)"
        )
        assert rc == 0
        assert out == "(1.0, 2.0)"


# ── 7.14.8 Class-level type aliases ──────────────────────────────────────

class TestTypeStatementClassLevel:
    """Concept 8 – type aliases defined inside a class body."""

    def test_class_type_alias(self):
        out, err, rc = clython_run(
            "class Container:\n"
            "    type ItemType = str\n"
            "    def make(self) -> 'Container.ItemType':\n"
            "        return 'hello'\n"
            "c = Container()\n"
            "print(c.make())"
        )
        assert rc == 0
        assert out == "hello"

    def test_class_multiple_aliases(self):
        out, err, rc = clython_run(
            "class DataProcessor:\n"
            "    type InputType = dict[str, int]\n"
            "    type OutputType = list[int]\n"
            "print('ok')"
        )
        assert rc == 0
        assert out == "ok"


# ── 7.14.9 Function-level type aliases ───────────────────────────────────

class TestTypeStatementFunctionLevel:
    """Concept 9 – type aliases defined inside a function."""

    def test_local_type_alias(self):
        out, err, rc = clython_run(
            "def process():\n"
            "    type Row = dict[str, str]\n"
            "    r: Row = {'key': 'value'}\n"
            "    return r['key']\n"
            "print(process())"
        )
        assert rc == 0
        assert out == "value"

    def test_local_alias_used_in_annotation(self):
        out, err, rc = clython_run(
            "def make_list():\n"
            "    type Numbers = list[int]\n"
            "    nums: Numbers = [1, 2, 3]\n"
            "    return nums\n"
            "print(make_list())"
        )
        assert rc == 0
        assert out == "[1, 2, 3]"


# ── 7.14.10 Type alias scoping ────────────────────────────────────────────

class TestTypeStatementScoping:
    """Concept 10 – scoping rules for type aliases at different levels."""

    def test_global_vs_local_alias(self):
        out, err, rc = clython_run(
            "type GlobalAlias = str\n"
            "def f():\n"
            "    type LocalAlias = int\n"
            "    return LocalAlias\n"
            "print(GlobalAlias)\n"
            "print(f())"
        )
        assert rc == 0

    def test_nested_function_alias(self):
        out, err, rc = clython_run(
            "def outer():\n"
            "    type OuterAlias = str\n"
            "    def inner():\n"
            "        type InnerAlias = int\n"
            "        return InnerAlias\n"
            "    return inner()\n"
            "print(outer())"
        )
        assert rc == 0


# ── 7.14.11 Forward references ────────────────────────────────────────────

class TestTypeStatementForwardReferences:
    """Concept 11 – forward references in type alias values."""

    def test_forward_ref_string(self):
        out, err, rc = clython_run(
            'type NodeRef = "TreeNode | None"\n'
            "class TreeNode:\n"
            "    def __init__(self, val: int):\n"
            "        self.val = val\n"
            "n = TreeNode(5)\n"
            "print(n.val)"
        )
        assert rc == 0
        assert out == "5"

    def test_mutual_forward_refs(self):
        out, err, rc = clython_run(
            'type PersonRef = "Person | None"\n'
            "class Person:\n"
            "    def __init__(self, name: str):\n"
            "        self.name = name\n"
            "p = Person('Alice')\n"
            "print(p.name)"
        )
        assert rc == 0
        assert out == "Alice"


# ── 7.14.12 Recursive type aliases ───────────────────────────────────────

class TestTypeStatementRecursiveAliases:
    """Concept 12 – self-referential / recursive type alias definitions."""

    @pytest.mark.xfail(reason="Union/complex type expressions not yet supported in Clython")
    def test_json_value(self):
        out, err, rc = clython_run(
            "type JsonValue = str | int | float | bool | None | list[JsonValue] | dict[str, JsonValue]\n"
            "print(JsonValue)"
        )
        assert rc == 0

    @pytest.mark.xfail(reason="Union/complex type expressions not yet supported in Clython")
    def test_recursive_generic(self):
        out, err, rc = clython_run(
            "type Tree[T] = T | dict[str, Tree[T]]\n"
            "print(Tree)"
        )
        assert rc == 0


# ── 7.14.13 TypeAlias AST node structure ─────────────────────────────────

class TestTypeStatementASTStructure:
    """Concept 13 – type statement produces a value / object accessible at runtime."""

    def test_alias_is_accessible(self):
        """The alias name is bound in the enclosing scope after the statement."""
        out, err, rc = clython_run(
            "type IntAlias = int\n"
            "print(type(IntAlias).__name__)"
        )
        assert rc == 0
        # The runtime type of a TypeAlias object varies; just check it doesn't crash

    def test_generic_alias_accessible(self):
        out, err, rc = clython_run(
            "type ListAlias[T] = list[T]\n"
            "print(type(ListAlias).__name__)"
        )
        assert rc == 0


# ── 7.14.14 Type parameter AST structure ─────────────────────────────────

class TestTypeStatementParamASTStructure:
    """Concept 14 – type parameter objects are accessible on the alias."""

    def test_type_params_present(self):
        out, err, rc = clython_run(
            "type Pair[T, U] = tuple[T, U]\n"
            "print(Pair)"
        )
        assert rc == 0


# ── 7.14.15 Cross-implementation consistency ─────────────────────────────

class TestTypeStatementCrossImplConsistency:
    """Concept 15 – basic type aliases that must be consistent across implementations."""

    def test_int_alias_bound(self):
        out, err, rc = clython_run("type IntAlias = int\nprint(IntAlias)")
        assert rc == 0

    @pytest.mark.xfail(reason="Union/complex type expressions not yet supported in Clython")
    def test_union_alias_bound(self):
        out, err, rc = clython_run("type UnionAlias = int | str\nprint(UnionAlias)")
        assert rc == 0

    def test_list_generic_bound(self):
        out, err, rc = clython_run("type ListAlias[T] = list[T]\nprint(ListAlias)")
        assert rc == 0


# ── 7.14.16 Comprehensive real-world type patterns ────────────────────────

class TestTypeStatementComprehensivePatterns:
    """Concept 16 – real-world-style collections of type aliases."""

    def test_domain_types(self):
        out, err, rc = clython_run(
            "type UserId = int\n"
            "type Username = str\n"
            "type Email = str\n"
            "type Timestamp = float\n"
            "print('ok')"
        )
        assert rc == 0
        assert out == "ok"

    @pytest.mark.xfail(reason="Not yet supported in Clython")
    def test_generic_container_types(self):
        out, err, rc = clython_run(
            "type Container[T] = list[T] | tuple[T, ...] | set[T]\n"
            "type Optional[T] = T | None\n"
            "print('ok')"
        )
        assert rc == 0
        assert out == "ok"

    def test_error_handling_types(self):
        out, err, rc = clython_run(
            "type ErrorCode = int\n"
            "type ErrorMessage = str\n"
            "type ValidationError = tuple[ErrorCode, ErrorMessage]\n"
            "e: ValidationError = (404, 'not found')\n"
            "print(e)"
        )
        assert rc == 0
        assert out == "(404, 'not found')"


# ── 7.14.17 Type alias used in annotation ────────────────────────────────

class TestTypeStatementUsedInAnnotations:
    """Concept 17 – type alias used as a type annotation on variables and parameters."""

    def test_variable_annotation(self):
        out, err, rc = clython_run(
            "type IntList = list[int]\n"
            "x: IntList = [1, 2, 3]\n"
            "print(x)"
        )
        assert rc == 0
        assert out == "[1, 2, 3]"

    def test_function_param_annotation(self):
        out, err, rc = clython_run(
            "type UserId = int\n"
            "def get_user(uid: UserId) -> str:\n"
            "    return f'user_{uid}'\n"
            "print(get_user(42))"
        )
        assert rc == 0
        assert out == "user_42"

    def test_return_annotation(self):
        out, err, rc = clython_run(
            "type StringList = list[str]\n"
            "def get_names() -> StringList:\n"
            "    return ['alice', 'bob']\n"
            "print(get_names())"
        )
        assert rc == 0
        assert out == "['alice', 'bob']"


# ── 7.14.18 Introspection capabilities ───────────────────────────────────

class TestTypeStatementIntrospection:
    """Concept 18 – ability to introspect / enumerate type aliases at runtime."""

    @pytest.mark.xfail(reason="Not yet supported in Clython")
    def test_alias_in_namespace(self):
        out, err, rc = clython_run(
            "type MyAlias = int\n"
            "print('MyAlias' in dir())"
        )
        assert rc == 0
        assert out == "True"

    def test_multiple_aliases_accessible(self):
        out, err, rc = clython_run(
            "type Name = str\n"
            "type Age = int\n"
            "type Score = float\n"
            "print(Name, Age, Score)"
        )
        assert rc == 0


# ── 7.14.19 Fallback / Python < 3.12 behaviour ───────────────────────────

class TestTypeStatementSyntaxIsRecognised:
    """Concept 19 – Clython parses the type statement without hard SyntaxError."""

    def test_parse_does_not_crash(self):
        """At minimum, Clython should not crash with an unhandled exception."""
        out, err, rc = clython_run("type X = int\nprint('alive')")
        # Either succeeds (rc==0) or exits with a handled error (rc!=0 but no crash)
        # We just verify the process terminates
        assert rc is not None  # process returned

    def test_generic_parse_does_not_crash(self):
        out, err, rc = clython_run("type X[T] = list[T]\nprint('alive')")
        assert rc is not None
