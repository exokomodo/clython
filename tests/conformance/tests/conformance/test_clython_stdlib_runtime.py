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

    @pytest.mark.xfail(strict=False, reason="string.Formatter not implemented in Clython")
    def test_formatter_format(self):
        out, _, rc = clython_run(
            "import string\nprint(string.Formatter().format('Hello {name}', name='world'))"
        )
        assert rc == 0
        assert out == "Hello world"

    @pytest.mark.xfail(strict=False, reason="string.Template not implemented in Clython")
    def test_template_substitute(self):
        out, _, rc = clython_run(
            "import string\nprint(string.Template('$x').substitute(x=42))"
        )
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
            "import collections\n"
            "c = collections.Counter('aab')\n"
            "print(c['a'])"
        )
        assert rc == 0
        assert out == "2"

    def test_deque_popleft(self):
        out, _, rc = clython_run(
            "import collections\n"
            "d = collections.deque([1, 2, 3])\n"
            "print(d.popleft())"
        )
        assert rc == 0
        assert out == "1"

    @pytest.mark.xfail(reason="collections.ChainMap not implemented in Clython")
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

    def test_gcd(self):
        out, _, rc = clython_run("import math\nprint(math.gcd(12, 8))")
        assert rc == 0
        assert out == "4"

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
            "import functools\n"
            "print(functools.reduce(lambda a, b: a + b, [1, 2, 3]))"
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

    @pytest.mark.xfail(strict=False, reason="re.match returns None instead of a match object")
    def test_match_returns_not_none(self):
        out, _, rc = clython_run(
            r"import re" + "\n" + r"print(re.match(r'\d+', '123') is not None)"
        )
        assert rc == 0
        assert out == "True"

    @pytest.mark.xfail(strict=False, reason="re.sub not implemented or broken in Clython")
    def test_sub_collapses_whitespace(self):
        out, _, rc = clython_run(
            r"import re" + "\n" + r"print(re.sub(r'\s+', ' ', 'hello  world'))"
        )
        assert rc == 0
        assert out == "hello world"

    @pytest.mark.xfail(strict=False, reason="re.compile pattern type not yet implemented")
    def test_compile_returns_pattern(self):
        out, _, rc = clython_run(
            r"import re" + "\n" + r"p = re.compile(r'[a-z]+')" + "\nprint(type(p).__name__)"
        )
        assert rc == 0
        # CPython uses 're.Pattern', but any non-error type name is acceptable
        assert out in ("Pattern", "re.Pattern", "SRE_Pattern")

    @pytest.mark.xfail(strict=False, reason="re.findall not implemented or broken in Clython")
    def test_findall_digits(self):
        out, _, rc = clython_run(
            r"import re" + "\n" + r"print(re.findall(r'\d+', 'abc 12 def 34'))"
        )
        assert rc == 0
        assert out == "['12', '34']"

    @pytest.mark.xfail(strict=False, reason="re.search not implemented or broken in Clython")
    def test_search_finds_inner_match(self):
        out, _, rc = clython_run(
            r"import re" + "\n" + r"print(re.search(r'\d+', 'abc123def') is not None)"
        )
        assert rc == 0
        assert out == "True"

    @pytest.mark.xfail(strict=False, reason="re.split not implemented or broken in Clython")
    def test_split_on_whitespace(self):
        out, _, rc = clython_run(
            r"import re" + "\n" + r"print(re.split(r'\s+', 'a b  c'))"
        )
        assert rc == 0
        assert out == "['a', 'b', 'c']"


# ═══════════════════════════════════════════════════════════════════════════════
# itertools module
# ═══════════════════════════════════════════════════════════════════════════════


class TestItertoolsModule:
    """Tests for the itertools stdlib module."""

    def test_islice(self):
        out, _, rc = clython_run(
            "import itertools\n"
            "print(list(itertools.islice([1, 2, 3, 4, 5], 2, 4)))"
        )
        assert rc == 0
        assert out == "[3, 4]"

    def test_chain(self):
        out, _, rc = clython_run(
            "import itertools\n"
            "print(list(itertools.chain([1, 2], [3, 4])))"
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
