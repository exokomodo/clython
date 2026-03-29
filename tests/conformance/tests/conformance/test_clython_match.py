"""
Clython match statement conformance tests (PEP 634).

Tests structural pattern matching: literal, wildcard, capture,
sequence, OR, guard clauses, nested patterns, and edge cases.

Requires CLYTHON_BIN to be set.
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


# ── Literal matching ─────────────────────────────────────────────────────────


class TestMatchLiteral:
    """Test matching against literal values."""

    def test_match_int(self):
        out, _, rc = clython_run("""
match 1:
    case 1:
        print("one")
    case 2:
        print("two")
""")
        assert rc == 0
        assert out == "one"

    def test_match_str(self):
        out, _, rc = clython_run("""
command = "hello"
match command:
    case "quit":
        print("quitting")
    case "hello":
        print("hello!")
    case _:
        print("unknown")
""")
        assert rc == 0
        assert out == "hello!"

    def test_match_bool_true(self):
        out, _, rc = clython_run("""
match True:
    case True:
        print("yes")
    case False:
        print("no")
""")
        assert rc == 0
        assert out == "yes"

    def test_match_bool_false(self):
        out, _, rc = clython_run("""
match False:
    case True:
        print("yes")
    case False:
        print("no")
""")
        assert rc == 0
        assert out == "no"

    def test_match_none(self):
        out, _, rc = clython_run("""
match None:
    case None:
        print("none")
    case _:
        print("other")
""")
        assert rc == 0
        assert out == "none"

    def test_match_negative_int(self):
        out, _, rc = clython_run("""
match -1:
    case -1:
        print("neg one")
    case 1:
        print("pos one")
""")
        assert rc == 0
        assert out == "neg one"


# ── Wildcard ─────────────────────────────────────────────────────────────────


class TestMatchWildcard:
    """Test wildcard _ pattern."""

    def test_wildcard_matches_anything(self):
        out, _, rc = clython_run("""
match 42:
    case _:
        print("matched")
""")
        assert rc == 0
        assert out == "matched"

    def test_wildcard_does_not_bind(self):
        out, _, rc = clython_run("""
match 42:
    case _:
        pass
try:
    print(_)
except:
    print("not bound")
""")
        assert rc == 0
        assert out == "not bound"

    def test_wildcard_as_default(self):
        out, _, rc = clython_run("""
match "xyz":
    case "a":
        print("a")
    case "b":
        print("b")
    case _:
        print("default")
""")
        assert rc == 0
        assert out == "default"


# ── Capture patterns ─────────────────────────────────────────────────────────


class TestMatchCapture:
    """Test capture (name) patterns."""

    def test_capture_binds_value(self):
        out, _, rc = clython_run("""
match 42:
    case x:
        print(x)
""")
        assert rc == 0
        assert out == "42"

    def test_capture_in_sequence(self):
        out, _, rc = clython_run("""
point = (3, 4)
match point:
    case (x, y):
        print(f"{x} {y}")
""")
        assert rc == 0
        assert out == "3 4"

    def test_capture_with_literal(self):
        out, _, rc = clython_run("""
point = (0, 5)
match point:
    case (0, y):
        print(f"y={y}")
    case (x, y):
        print(f"x={x} y={y}")
""")
        assert rc == 0
        assert out == "y=5"


# ── Sequence patterns ────────────────────────────────────────────────────────


class TestMatchSequence:
    """Test sequence (tuple/list) patterns."""

    def test_tuple_origin(self):
        out, _, rc = clython_run("""
match (0, 0):
    case (0, 0):
        print("origin")
    case (x, y):
        print(f"{x},{y}")
""")
        assert rc == 0
        assert out == "origin"

    def test_tuple_x_axis(self):
        out, _, rc = clython_run("""
match (5, 0):
    case (0, 0):
        print("origin")
    case (x, 0):
        print(f"x-axis at {x}")
    case (x, y):
        print(f"{x},{y}")
""")
        assert rc == 0
        assert out == "x-axis at 5"

    def test_tuple_y_axis(self):
        out, _, rc = clython_run("""
match (0, 7):
    case (0, 0):
        print("origin")
    case (x, 0):
        print(f"x-axis")
    case (0, y):
        print(f"y-axis at {y}")
    case (x, y):
        print(f"{x},{y}")
""")
        assert rc == 0
        assert out == "y-axis at 7"

    def test_tuple_general(self):
        out, _, rc = clython_run("""
match (3, 4):
    case (0, 0):
        print("origin")
    case (x, y):
        print(f"point at {x}, {y}")
""")
        assert rc == 0
        assert out == "point at 3, 4"

    def test_list_sequence(self):
        out, _, rc = clython_run("""
match [1, 2, 3]:
    case [a, b, c]:
        print(f"{a} {b} {c}")
""")
        assert rc == 0
        assert out == "1 2 3"

    def test_sequence_length_mismatch(self):
        out, _, rc = clython_run("""
match (1, 2, 3):
    case (x, y):
        print("two")
    case (x, y, z):
        print("three")
""")
        assert rc == 0
        assert out == "three"


# ── OR patterns ──────────────────────────────────────────────────────────────


class TestMatchOr:
    """Test OR (|) patterns."""

    def test_or_pattern_match_first(self):
        out, _, rc = clython_run("""
match 1:
    case 1 | 2 | 3:
        print("small")
    case _:
        print("other")
""")
        assert rc == 0
        assert out == "small"

    def test_or_pattern_match_middle(self):
        out, _, rc = clython_run("""
match 2:
    case 1 | 2 | 3:
        print("small")
    case _:
        print("other")
""")
        assert rc == 0
        assert out == "small"

    def test_or_pattern_match_last(self):
        out, _, rc = clython_run("""
match 3:
    case 1 | 2 | 3:
        print("small")
    case _:
        print("other")
""")
        assert rc == 0
        assert out == "small"

    def test_or_pattern_no_match(self):
        out, _, rc = clython_run("""
match 99:
    case 1 | 2 | 3:
        print("small")
    case _:
        print("other")
""")
        assert rc == 0
        assert out == "other"

    def test_or_with_strings(self):
        out, _, rc = clython_run("""
match "yes":
    case "yes" | "y" | "Y":
        print("affirmative")
    case _:
        print("negative")
""")
        assert rc == 0
        assert out == "affirmative"


# ── Guard clauses ────────────────────────────────────────────────────────────


class TestMatchGuard:
    """Test guard (if) clauses."""

    def test_guard_passes(self):
        out, _, rc = clython_run("""
match 200:
    case x if x > 100:
        print("big")
    case _:
        print("other")
""")
        assert rc == 0
        assert out == "big"

    def test_guard_fails(self):
        out, _, rc = clython_run("""
match 50:
    case x if x > 100:
        print("big")
    case _:
        print("other")
""")
        assert rc == 0
        assert out == "other"

    def test_guard_with_literal(self):
        out, _, rc = clython_run("""
match 5:
    case 1 | 2 | 3:
        print("small")
    case x if x > 100:
        print("big")
    case _:
        print("other")
""")
        assert rc == 0
        assert out == "other"

    def test_guard_combined(self):
        out, _, rc = clython_run("""
match 2:
    case 1 | 2 | 3:
        print("small")
    case x if x > 100:
        print("big")
    case _:
        print("other")
""")
        assert rc == 0
        assert out == "small"


# ── Nested patterns ──────────────────────────────────────────────────────────


class TestMatchNested:
    """Test nested sequence patterns."""

    def test_nested_tuple(self):
        out, _, rc = clython_run("""
match (1, (2, 3)):
    case (x, (a, b)):
        print(f"{x} {a} {b}")
""")
        assert rc == 0
        assert out == "1 2 3"

    def test_nested_with_literal(self):
        out, _, rc = clython_run("""
match (0, (1, 2)):
    case (0, (a, b)):
        print(f"zero {a} {b}")
    case (x, (a, b)):
        print(f"{x} {a} {b}")
""")
        assert rc == 0
        assert out == "zero 1 2"


# ── No match (fall through) ─────────────────────────────────────────────────


class TestMatchNoMatch:
    """Test behavior when no case matches."""

    def test_no_match_no_error(self):
        out, _, rc = clython_run("""
match 99:
    case 1:
        print("one")
    case 2:
        print("two")
print("done")
""")
        assert rc == 0
        assert out == "done"

    def test_no_match_returns_none(self):
        out, _, rc = clython_run("""
result = None
match 99:
    case 1:
        result = "one"
print(result)
""")
        assert rc == 0
        assert out == "None"


# ── Side effects ─────────────────────────────────────────────────────────────


class TestMatchSideEffects:
    """Test that matched case bodies execute properly with side effects."""

    def test_side_effects_in_body(self):
        out, _, rc = clython_run("""
results = []
for val in [1, 2, 3, 99]:
    match val:
        case 1:
            results.append("one")
        case 2:
            results.append("two")
        case 3:
            results.append("three")
        case _:
            results.append("other")
print(results)
""")
        assert rc == 0
        assert out == "['one', 'two', 'three', 'other']"

    def test_match_in_function(self):
        out, _, rc = clython_run("""
def classify(x):
    match x:
        case 1 | 2 | 3:
            return "small"
        case x if x > 100:
            return "big"
        case _:
            return "medium"
print(classify(2))
print(classify(200))
print(classify(50))
""")
        assert rc == 0
        assert out == "small\nbig\nmedium"

    def test_first_match_wins(self):
        out, _, rc = clython_run("""
match 1:
    case 1:
        print("first")
    case 1:
        print("second")
""")
        assert rc == 0
        assert out == "first"


# ── Mapping patterns ─────────────────────────────────────────────────────────


class TestMatchMapping:
    """Test mapping (dict) patterns from Section 8.10."""

    def test_dict_pattern_basic(self):
        out, _, rc = clython_run("""
match {"action": "move", "x": 5}:
    case {"action": "move", "x": x}:
        print(f"move to {x}")
    case _:
        print("other")
""")
        assert rc == 0
        assert out == "move to 5"

    def test_dict_pattern_subset(self):
        """Dict patterns match if keys are present (extra keys allowed)."""
        out, _, rc = clython_run("""
match {"a": 1, "b": 2, "c": 3}:
    case {"a": a, "b": b}:
        print(f"{a} {b}")
""")
        assert rc == 0
        assert out == "1 2"

    def test_dict_pattern_rest(self):
        out, _, rc = clython_run("""
match {"x": 1, "y": 2, "z": 3}:
    case {"x": x, **rest}:
        print(x, sorted(rest.keys()))
""")
        assert rc == 0
        assert out == "1 ['y', 'z']"


# ── Class patterns ───────────────────────────────────────────────────────────


class TestMatchClass:
    """Test class patterns from Section 8.10."""

    def test_class_pattern_basic(self):
        out, _, rc = clython_run("""
class Point:
    __match_args__ = ("x", "y")
    def __init__(self, x, y):
        self.x = x
        self.y = y

match Point(1, 2):
    case Point(x, y):
        print(f"{x} {y}")
""")
        assert rc == 0
        assert out == "1 2"

    def test_class_pattern_keyword(self):
        out, _, rc = clython_run("""
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

match Point(3, 4):
    case Point(x=3, y=y):
        print(f"x=3, y={y}")
    case _:
        print("other")
""")
        assert rc == 0
        assert out == "x=3, y=4"


# ── As patterns ──────────────────────────────────────────────────────────────


class TestMatchAs:
    """Test as patterns from Section 8.10."""

    def test_as_pattern_basic(self):
        out, _, rc = clython_run("""
match (1, 2):
    case (1, y) as point:
        print(f"y={y} point={point}")
""")
        assert rc == 0
        assert out == "y=2 point=(1, 2)"

    def test_as_pattern_with_or(self):
        out, _, rc = clython_run("""
match 2:
    case (1 | 2 | 3) as x:
        print(f"small: {x}")
    case _:
        print("other")
""")
        assert rc == 0
        assert out == "small: 2"


# ── Star patterns in sequences ───────────────────────────────────────────────


class TestMatchStarPattern:
    """Test star (*) patterns in sequences from Section 8.10."""

    def test_star_pattern_rest(self):
        out, _, rc = clython_run("""
match [1, 2, 3, 4]:
    case [first, *rest]:
        print(f"{first} {rest}")
""")
        assert rc == 0
        assert out == "1 [2, 3, 4]"

    def test_star_pattern_middle(self):
        out, _, rc = clython_run("""
match [1, 2, 3, 4, 5]:
    case [first, *middle, last]:
        print(f"{first} {middle} {last}")
""")
        assert rc == 0
        assert out == "1 [2, 3, 4] 5"

    def test_star_pattern_empty(self):
        out, _, rc = clython_run("""
match [1]:
    case [x, *rest]:
        print(f"{x} {rest}")
""")
        assert rc == 0
        assert out == "1 []"


# ── Complex match patterns ───────────────────────────────────────────────────


class TestMatchComplex:
    """Test complex/combined match patterns from Section 8.10."""

    def test_match_with_computation_in_body(self):
        out, _, rc = clython_run("""
match (3, 4):
    case (x, y):
        import math
        dist = math.sqrt(x**2 + y**2)
        print(dist)
""")
        assert rc == 0
        assert out == "5.0"

    def test_match_string_patterns(self):
        out, _, rc = clython_run("""
commands = ["quit", "hello", "unknown"]
results = []
for cmd in commands:
    match cmd:
        case "quit":
            results.append("q")
        case "hello":
            results.append("h")
        case _:
            results.append("?")
print(results)
""")
        assert rc == 0
        assert out == "['q', 'h', '?']"

    def test_match_nested_in_if(self):
        out, _, rc = clython_run("""
x = 5
if x > 0:
    match x:
        case 5:
            print("five")
        case _:
            print("other positive")
""")
        assert rc == 0
        assert out == "five"

    def test_match_float_literal(self):
        out, _, rc = clython_run("""
match 3.14:
    case 3.14:
        print("pi-ish")
    case _:
        print("other")
""")
        assert rc == 0
        assert out == "pi-ish"
