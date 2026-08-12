"""
Clython stdlib runtime tests — verify CL-backed stdlib module implementations
produce correct output when executed through Clython.

Modules covered:
  - string
  - collections
  - json
  - math
  - re
  - functools
  - itertools
  - keyword
  - re
"""

import os
import subprocess
import pytest

CLYTHON_BIN = os.environ.get("CLYTHON_BIN")


def clython_run(source: str, *, timeout: int = 10):
    result = subprocess.run(
        [CLYTHON_BIN, "-c", source],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode


pytestmark = pytest.mark.skipif(
    not CLYTHON_BIN, reason="CLYTHON_BIN not set — skipping Clython-specific tests"
)


# ═══════════════════════════════════════════════════════════════════════════════
# string module
# ═══════════════════════════════════════════════════════════════════════════════


class TestStringModule:
    """Tests for the string stdlib module."""

    def test_ascii_lowercase(self):
        out, _, rc = clython_run("import string\nprint(string.ascii_lowercase)")
        assert rc == 0
        assert out == "abcdefghijklmnopqrstuvwxyz"

    def test_ascii_uppercase(self):
        out, _, rc = clython_run("import string\nprint(string.ascii_uppercase)")
        assert rc == 0
        assert out == "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    def test_digits(self):
        out, _, rc = clython_run("import string\nprint(string.digits)")
        assert rc == 0
        assert out == "0123456789"

    def test_whitespace_contains_space(self):
        out, _, rc = clython_run("import string\nprint(' ' in string.whitespace)")
        assert rc == 0
        assert out == "True"

    def test_whitespace_contains_newline(self):
        out, _, rc = clython_run(r"import string" + "\nprint('\\n' in string.whitespace)")
        assert rc == 0
        assert out == "True"

    def test_ascii_letters_is_lower_plus_upper(self):
        out, _, rc = clython_run(
            "import string\n"
            "print(string.ascii_letters == string.ascii_lowercase + string.ascii_uppercase)"
        )
        assert rc == 0
        assert out == "True"

    def test_hexdigits_contains_0(self):
        out, _, rc = clython_run("import string\nprint('0' in string.hexdigits)")
        assert rc == 0
        assert out == "True"

    def test_hexdigits_contains_a(self):
        out, _, rc = clython_run("import string\nprint('a' in string.hexdigits)")
        assert rc == 0
        assert out == "True"

    def test_hexdigits_contains_F(self):
        out, _, rc = clython_run("import string\nprint('F' in string.hexdigits)")
        assert rc == 0
        assert out == "True"

    def test_punctuation_contains_bang(self):
        out, _, rc = clython_run("import string\nprint('!' in string.punctuation)")
        assert rc == 0
        assert out == "True"

    def test_formatter_format(self):
        out, _, rc = clython_run(
            "import string\nprint(string.Formatter().format('Hello {name}', name='world'))"
        )
        assert rc == 0
        assert out == "Hello world"

    def test_template_substitute(self):
        out, _, rc = clython_run("import string\nprint(string.Template('$x').substitute(x=42))")
        assert rc == 0
        assert out == "42"


# ═══════════════════════════════════════════════════════════════════════════════
# collections module
# ═══════════════════════════════════════════════════════════════════════════════


class TestCollectionsModule:
    """Tests for the collections stdlib module."""

    def test_ordereddict_create_and_iterate(self):
        out, _, rc = clython_run(
            "import collections\n"
            "od = collections.OrderedDict()\n"
            "od['x'] = 1\n"
            "od['y'] = 2\n"
            "print(list(od.keys()))"
        )
        assert rc == 0
        assert out == "['x', 'y']"

    def test_namedtuple_creates_class(self):
        out, _, rc = clython_run(
            "import collections\n"
            "Point = collections.namedtuple('Point', ['x', 'y'])\n"
            "print(type(Point).__name__)"
        )
        assert rc == 0
        # namedtuple returns a class (type)
        assert out in ("type", "function")

    def test_namedtuple_instance_attribute(self):
        out, _, rc = clython_run(
            "import collections\n"
            "Point = collections.namedtuple('Point', ['x', 'y'])\n"
            "p = Point(3, 4)\n"
            "print(p.x)"
        )
        assert rc == 0
        assert out == "3"

    def test_counter_counts_chars(self):
        out, _, rc = clython_run(
            "import collections\n" "c = collections.Counter('aab')\n" "print(c['a'])"
        )
        assert rc == 0
        assert out == "2"

    def test_deque_popleft(self):
        out, _, rc = clython_run(
            "import collections\n" "d = collections.deque([1, 2, 3])\n" "print(d.popleft())"
        )
        assert rc == 0
        assert out == "1"

    def test_chainmap_lookup(self):
        out, _, rc = clython_run(
            "import collections\n"
            "cm = collections.ChainMap({'a': 1}, {'b': 2})\n"
            "print(cm['a'])"
        )
        assert rc == 0
        assert out == "1"


# ═══════════════════════════════════════════════════════════════════════════════
# json module
# ═══════════════════════════════════════════════════════════════════════════════


class TestJsonModule:
    """Tests for the json stdlib module."""

    def test_dumps_dict(self):
        out, _, rc = clython_run("import json\nprint(json.dumps({'a': 1}))")
        assert rc == 0
        assert out == '{"a": 1}'

    def test_dumps_list(self):
        out, _, rc = clython_run("import json\nprint(json.dumps([1, 2, 3]))")
        assert rc == 0
        assert out == "[1, 2, 3]"

    def test_dumps_none(self):
        out, _, rc = clython_run("import json\nprint(json.dumps(None))")
        assert rc == 0
        assert out == "null"

    def test_dumps_true(self):
        out, _, rc = clython_run("import json\nprint(json.dumps(True))")
        assert rc == 0
        assert out == "true"

    def test_dumps_string(self):
        out, _, rc = clython_run("import json\nprint(json.dumps('hello'))")
        assert rc == 0
        assert out == '"hello"'


# ═══════════════════════════════════════════════════════════════════════════════
# math module
# ═══════════════════════════════════════════════════════════════════════════════


class TestMathModule:
    """Tests for the math stdlib module."""

    def test_floor(self):
        out, _, rc = clython_run("import math\nprint(math.floor(3.7))")
        assert rc == 0
        assert out == "3"

    def test_ceil(self):
        out, _, rc = clython_run("import math\nprint(math.ceil(3.2))")
        assert rc == 0
        assert out == "4"

    def test_factorial(self):
        out, _, rc = clython_run("import math\nprint(math.factorial(5))")
        assert rc == 0
        assert out == "120"

    def test_factorial_zero(self):
        out, _, rc = clython_run("import math\nprint(math.factorial(0))")
        assert rc == 0
        assert out == "1"

    def test_factorial_large(self):
        out, _, rc = clython_run("import math\nprint(math.factorial(10))")
        assert rc == 0
        assert out == "3628800"

    def test_gcd(self):
        out, _, rc = clython_run("import math\nprint(math.gcd(12, 8))")
        assert rc == 0
        assert out == "4"

    def test_gcd_coprime(self):
        out, _, rc = clython_run("import math\nprint(math.gcd(7, 13))")
        assert rc == 0
        assert out == "1"

    def test_gcd_zero(self):
        out, _, rc = clython_run("import math\nprint(math.gcd(0, 5))")
        assert rc == 0
        assert out == "5"

    def test_sqrt(self):
        out, _, rc = clython_run("import math\nprint(math.sqrt(4))")
        assert rc == 0
        assert out == "2.0"

    def test_pi_approx(self):
        out, _, rc = clython_run("import math\nprint(abs(math.pi - 3.14159) < 0.001)")
        assert rc == 0
        assert out == "True"


# ═══════════════════════════════════════════════════════════════════════════════
# functools module
# ═══════════════════════════════════════════════════════════════════════════════


class TestFunctoolsModule:
    """Tests for the functools stdlib module."""

    def test_reduce(self):
        out, _, rc = clython_run(
            "import functools\n" "print(functools.reduce(lambda a, b: a + b, [1, 2, 3]))"
        )
        assert rc == 0
        assert out == "6"

    def test_partial(self):
        out, _, rc = clython_run(
            "import functools\n"
            "add = lambda a, b: a + b\n"
            "add5 = functools.partial(add, 5)\n"
            "print(add5(3))"
        )
        assert rc == 0
        assert out == "8"

    def test_lru_cache_decorator(self):
        out, _, rc = clython_run(
            "import functools\n"
            "@functools.lru_cache\n"
            "def double(x):\n"
            "    return x * 2\n"
            "print(double(4))"
        )
        assert rc == 0
        assert out == "8"


# ═══════════════════════════════════════════════════════════════════════════════
# re module
# ═══════════════════════════════════════════════════════════════════════════════


class TestReModule:
    """Tests for the re stdlib module."""

    def test_match_returns_not_none(self):
        out, _, rc = clython_run(
            r"import re" + "\n" + r"print(re.match(r'\d+', '123') is not None)"
        )
        assert rc == 0
        assert out == "True"

    def test_sub_collapses_whitespace(self):
        out, _, rc = clython_run(
            r"import re" + "\n" + r"print(re.sub(r'\s+', ' ', 'hello  world'))"
        )
        assert rc == 0
        assert out == "hello world"

    def test_compile_returns_pattern(self):
        out, _, rc = clython_run(
            r"import re" + "\n" + r"p = re.compile(r'[a-z]+')" + "\nprint(type(p).__name__)"
        )
        assert rc == 0
        # CPython uses 're.Pattern', but any non-error type name is acceptable
        assert out in ("Pattern", "re.Pattern", "SRE_Pattern")

    def test_findall_digits(self):
        out, _, rc = clython_run(
            r"import re" + "\n" + r"print(re.findall(r'\d+', 'abc 12 def 34'))"
        )
        assert rc == 0
        assert out == "['12', '34']"

    def test_search_finds_inner_match(self):
        out, _, rc = clython_run(
            r"import re" + "\n" + r"print(re.search(r'\d+', 'abc123def') is not None)"
        )
        assert rc == 0
        assert out == "True"

    def test_split_on_whitespace(self):
        out, _, rc = clython_run(r"import re" + "\n" + r"print(re.split(r'\s+', 'a b  c'))")
        assert rc == 0
        assert out == "['a', 'b', 'c']"


# ═══════════════════════════════════════════════════════════════════════════════
# itertools module
# ═══════════════════════════════════════════════════════════════════════════════


class TestItertoolsModule:
    """Tests for the itertools stdlib module."""

    def test_islice(self):
        out, _, rc = clython_run(
            "import itertools\n" "print(list(itertools.islice([1, 2, 3, 4, 5], 2, 4)))"
        )
        assert rc == 0
        assert out == "[3, 4]"

    def test_chain(self):
        out, _, rc = clython_run(
            "import itertools\n" "print(list(itertools.chain([1, 2], [3, 4])))"
        )
        assert rc == 0
        assert out == "[1, 2, 3, 4]"


# ═══════════════════════════════════════════════════════════════════════════════
# keyword module
# ═══════════════════════════════════════════════════════════════════════════════


class TestKeywordModule:
    """Tests for the keyword stdlib module."""

    def test_iskeyword_for_is_true(self):
        out, _, rc = clython_run("import keyword\nprint(keyword.iskeyword('for'))")
        assert rc == 0
        assert out == "True"

    def test_iskeyword_hello_is_false(self):
        out, _, rc = clython_run("import keyword\nprint(keyword.iskeyword('hello'))")
        assert rc == 0
        assert out == "False"

    def test_kwlist_contains_for(self):
        out, _, rc = clython_run("import keyword\nprint('for' in keyword.kwlist)")
        assert rc == 0
        assert out == "True"


# ═══════════════════════════════════════════════════════════════════════════════
# str methods: padding, tabs, search, partition, predicates, splitlines
# ═══════════════════════════════════════════════════════════════════════════════


class TestStrPaddingMethods:
    def test_center_even_padding(self):
        out, _, rc = clython_run("print(repr('abc'.center(7, '-')))")
        assert rc == 0
        assert out == "'--abc--'"

    def test_center_odd_padding_favours_left(self):
        """CPython: left = marg//2 + (marg & width & 1)."""
        out, _, rc = clython_run("print(repr('ab'.center(5, '-')), repr('a'.center(4, '*')))")
        assert rc == 0
        assert out == "'--ab-' '*a**'"

    def test_center_width_not_greater_than_len(self):
        out, _, rc = clython_run("print(repr('ab'.center(2)))")
        assert rc == 0
        assert out == "'ab'"

    def test_ljust_rjust(self):
        out, _, rc = clython_run("print(repr('ab'.ljust(4, '.')), repr('ab'.rjust(4, '.')))")
        assert rc == 0
        assert out == "'ab..' '..ab'"


class TestStrExpandtabs:
    def test_expandtabs_advances_to_next_stop(self):
        out, _, rc = clython_run(r"print(repr('a\tb'.expandtabs(4)), repr('ab\tc'.expandtabs(4)))")
        assert rc == 0
        assert out == "'a   b' 'ab  c'"

    def test_expandtabs_resets_column_on_newline(self):
        """Column restarts after a newline, so the tab expands to 3 spaces.

        Compared via == rather than repr(): repr() does not yet escape
        control characters (see issue #220), which is a separate bug.
        """
        out, _, rc = clython_run(
            r"print('a\nb\tc'.expandtabs(4) == 'a' + chr(10) + 'b   c')"
        )
        assert rc == 0
        assert out == "True"


class TestStrSearchMethods:
    def test_rfind_returns_last_match(self):
        out, _, rc = clython_run("print('abcabc'.rfind('a'), 'abc'.rfind('z'))")
        assert rc == 0
        assert out == "3 -1"

    def test_partition_splits_on_first(self):
        out, _, rc = clython_run("print('a-b-c'.partition('-'))")
        assert rc == 0
        assert out == "('a', '-', 'b-c')"

    def test_rpartition_splits_on_last(self):
        out, _, rc = clython_run("print('a-b-c'.rpartition('-'))")
        assert rc == 0
        assert out == "('a-b', '-', 'c')"

    def test_partition_no_match_puts_string_first(self):
        out, _, rc = clython_run("print('xy'.partition('-'))")
        assert rc == 0
        assert out == "('xy', '', '')"

    def test_rpartition_no_match_puts_string_last(self):
        """rpartition differs from partition here — the string goes last."""
        out, _, rc = clython_run("print('xy'.rpartition('-'))")
        assert rc == 0
        assert out == "('', '', 'xy')"


class TestStrPredicates:
    def test_swapcase(self):
        out, _, rc = clython_run("print(repr('aB'.swapcase()))")
        assert rc == 0
        assert out == "'Ab'"

    def test_isalnum_isspace(self):
        out, _, rc = clython_run("print('a1'.isalnum(), ' '.isspace())")
        assert rc == 0
        assert out == "True True"

    def test_isupper_islower_need_a_cased_char(self):
        """'123'.isupper() is False — digits are not cased."""
        out, _, rc = clython_run("print('ABC'.isupper(), '123'.isupper(), 'abc'.islower())")
        assert rc == 0
        assert out == "True False True"


class TestStrSplitlines:
    def test_splitlines_basic(self):
        out, _, rc = clython_run(r"print('a\nb'.splitlines())")
        assert rc == 0
        assert out == "['a', 'b']"

    def test_splitlines_trailing_break_adds_no_empty(self):
        out, _, rc = clython_run(r"print('a\n'.splitlines(), ''.splitlines())")
        assert rc == 0
        assert out == "['a'] []"

    def test_splitlines_treats_crlf_as_one_break(self):
        out, _, rc = clython_run(r"print('a\r\nb'.splitlines())")
        assert rc == 0
        assert out == "['a', 'b']"
