"""Clython runtime tests — Section 7.5: Del Statement.

Tests that the Clython interpreter correctly executes del statements
for name unbinding, attribute deletion, and subscript deletion.
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


class TestDelStatementRuntime:
    def test_del_simple_name(self):
        """del unbinds a variable name"""
        out, err, rc = clython_run(
            "x = 42\ndel x\n"
            "try:\n    print(x)\nexcept NameError:\n    print('gone')"
        )
        assert rc == 0
        assert out == "gone"

    def test_del_multiple_names(self):
        """del a, b unbinds both names"""
        out, err, rc = clython_run(
            "a = 1\nb = 2\ndel a, b\n"
            "try:\n    print(a)\nexcept NameError:\n    print('a gone')\n"
            "try:\n    print(b)\nexcept NameError:\n    print('b gone')"
        )
        assert rc == 0
        assert out == "a gone\nb gone"

    def test_del_list_item(self):
        """del removes an item from a list by index"""
        out, err, rc = clython_run(
            "lst = [1, 2, 3, 4]\ndel lst[1]\nprint(lst)"
        )
        assert rc == 0
        assert out == "[1, 3, 4]"

    def test_del_dict_key(self):
        """del removes a key from a dict"""
        out, err, rc = clython_run(
            "d = {'a': 1, 'b': 2}\ndel d['a']\nprint(d)"
        )
        assert rc == 0
        assert out == "{'b': 2}"

    def test_del_slice(self):
        """del removes a slice from a list"""
        out, err, rc = clython_run(
            "lst = [0, 1, 2, 3, 4, 5]\ndel lst[2:4]\nprint(lst)"
        )
        assert rc == 0
        assert out == "[0, 1, 4, 5]"

    def test_del_attribute(self):
        """del removes an instance attribute"""
        out, err, rc = clython_run(
            "class C:\n    pass\n"
            "obj = C()\nobj.x = 10\ndel obj.x\n"
            "try:\n    print(obj.x)\nexcept AttributeError:\n    print('gone')"
        )
        assert rc == 0
        assert out == "gone"

    def test_del_unbound_name_raises(self):
        """del of unbound name raises NameError"""
        out, err, rc = clython_run(
            "try:\n    del nonexistent\nexcept NameError:\n    print('NameError')"
        )
        assert rc == 0
        assert out == "NameError"

    def test_del_nonexistent_key_raises(self):
        """del of missing dict key raises KeyError"""
        out, err, rc = clython_run(
            "d = {}\n"
            "try:\n    del d['missing']\nexcept KeyError:\n    print('KeyError')"
        )
        assert rc == 0
        assert out == "KeyError"

    def test_del_out_of_range_index_raises(self):
        """del of out-of-range list index raises IndexError"""
        out, err, rc = clython_run(
            "lst = [1, 2, 3]\n"
            "try:\n    del lst[99]\nexcept IndexError:\n    print('IndexError')"
        )
        assert rc == 0
        assert out == "IndexError"

    def test_del_name_in_loop(self):
        """del inside a loop body"""
        out, err, rc = clython_run(
            "results = []\n"
            "for i in range(3):\n"
            "    tmp = i * 2\n"
            "    results.append(tmp)\n"
            "    del tmp\n"
            "print(results)"
        )
        assert rc == 0
        assert out == "[0, 2, 4]"

    def test_del_in_function_scope(self):
        """del removes a local variable in function scope"""
        out, err, rc = clython_run(
            "def f():\n"
            "    x = 99\n"
            "    del x\n"
            "    try:\n"
            "        return x\n"
            "    except UnboundLocalError:\n"
            "        return 'gone'\n"
            "print(f())"
        )
        assert rc == 0
        assert out == "gone"

    def test_del_all_slice(self):
        """del lst[:] clears list in place"""
        out, err, rc = clython_run(
            "lst = [1, 2, 3]\ndel lst[:]\nprint(lst)"
        )
        assert rc == 0
        assert out == "[]"

    def test_del_nested_subscript(self):
        """del nested subscript"""
        out, err, rc = clython_run(
            "d = {'a': [1, 2, 3]}\ndel d['a'][1]\nprint(d)"
        )
        assert rc == 0
        assert out == "{'a': [1, 3]}"

    def test_del_does_not_affect_other_names(self):
        """del one name does not affect a different name"""
        out, err, rc = clython_run(
            "a = 1\nb = 2\ndel a\nprint(b)"
        )
        assert rc == 0
        assert out == "2"

    def test_del_separate_statements(self):
        """multiple separate del statements each remove one name"""
        out, err, rc = clython_run(
            "a = 1\nb = 2\ndel a\ndel b\n"
            "try:\n    print(a)\nexcept NameError:\n    pass\n"
            "try:\n    print(b)\nexcept NameError:\n    print('both gone')"
        )
        assert rc == 0
        assert out == "both gone"

    def test_del_step_slice(self):
        """del with step slice removes every other element"""
        out, err, rc = clython_run(
            "lst = [0, 1, 2, 3, 4, 5]\ndel lst[::2]\nprint(lst)"
        )
        assert rc == 0
        assert out == "[1, 3, 5]"

    def test_del_in_except_handler(self):
        """del inside except block"""
        out, err, rc = clython_run(
            "d = {'key': 'value'}\n"
            "try:\n"
            "    raise ValueError()\n"
            "except ValueError:\n"
            "    del d['key']\n"
            "print(d)"
        )
        assert rc == 0
        assert out == "{}"
