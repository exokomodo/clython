"""Clython runtime tests — Section 7.13: Nonlocal Statement.

Tests that the Clython interpreter correctly implements the nonlocal
statement for binding to enclosing function scope variables.
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


class TestNonlocalStatementRuntime:
    def test_nonlocal_modify_enclosing(self):
        """nonlocal allows inner function to modify outer variable"""
        out, err, rc = clython_run(
            "def outer():\n"
            "    x = 10\n"
            "    def inner():\n"
            "        nonlocal x\n"
            "        x = 20\n"
            "    inner()\n"
            "    return x\n"
            "print(outer())"
        )
        assert rc == 0
        assert out == "20"

    def test_nonlocal_does_not_affect_module(self):
        """nonlocal changes enclosing local, NOT module variable"""
        out, err, rc = clython_run(
            "x = 'module'\n"
            "def outer():\n"
            "    x = 'outer'\n"
            "    def inner():\n"
            "        nonlocal x\n"
            "        x = 'inner'\n"
            "    inner()\n"
            "    return x\n"
            "result = outer()\n"
            "print(result)\n"
            "print(x)"
        )
        assert rc == 0
        assert out == "inner\nmodule"

    def test_nonlocal_counter(self):
        """classic counter pattern using nonlocal"""
        out, err, rc = clython_run(
            "def make_counter():\n"
            "    count = 0\n"
            "    def inc():\n"
            "        nonlocal count\n"
            "        count += 1\n"
            "        return count\n"
            "    return inc\n"
            "counter = make_counter()\n"
            "print(counter(), counter(), counter())"
        )
        assert rc == 0
        assert out == "1 2 3"

    def test_nonlocal_multiple_variables(self):
        """nonlocal with multiple variable names"""
        out, err, rc = clython_run(
            "def outer():\n"
            "    a, b = 1, 2\n"
            "    def inner():\n"
            "        nonlocal a, b\n"
            "        a, b = b, a\n"
            "    inner()\n"
            "    return a, b\n"
            "print(outer())"
        )
        assert rc == 0
        assert out == "(2, 1)"

    def test_nonlocal_separate_statements(self):
        """separate nonlocal statements for different variables"""
        out, err, rc = clython_run(
            "def outer():\n"
            "    x = 0\n"
            "    y = 0\n"
            "    def inner():\n"
            "        nonlocal x\n"
            "        nonlocal y\n"
            "        x = 5\n"
            "        y = 10\n"
            "    inner()\n"
            "    return x, y\n"
            "print(outer())"
        )
        assert rc == 0
        assert out == "(5, 10)"

    def test_nonlocal_three_levels(self):
        """nonlocal skips intermediate scope to reach enclosing"""
        out, err, rc = clython_run(
            "def level1():\n"
            "    val = 'level1'\n"
            "    def level2():\n"
            "        def level3():\n"
            "            nonlocal val\n"
            "            val = 'modified'\n"
            "        level3()\n"
            "    level2()\n"
            "    return val\n"
            "print(level1())"
        )
        assert rc == 0
        assert out == "modified"

    def test_nonlocal_accumulator(self):
        """accumulator pattern using nonlocal"""
        out, err, rc = clython_run(
            "def make_adder():\n"
            "    total = 0\n"
            "    def add(n):\n"
            "        nonlocal total\n"
            "        total += n\n"
            "        return total\n"
            "    return add\n"
            "add = make_adder()\n"
            "print(add(1), add(2), add(3))"
        )
        assert rc == 0
        assert out == "1 3 6"

    def test_nonlocal_closure_multiple_closures(self):
        """each closure has its own copy of the enclosing variable"""
        out, err, rc = clython_run(
            "def make_counter():\n"
            "    count = 0\n"
            "    def inc():\n"
            "        nonlocal count\n"
            "        count += 1\n"
            "        return count\n"
            "    return inc\n"
            "c1 = make_counter()\n"
            "c2 = make_counter()\n"
            "c1()\nc1()\nc2()\n"
            "print(c1(), c2())"
        )
        assert rc == 0
        assert out == "3 2"

    def test_nonlocal_list_append(self):
        """nonlocal allows appending to a list in outer scope"""
        out, err, rc = clython_run(
            "def outer():\n"
            "    items = []\n"
            "    def add(x):\n"
            "        nonlocal items\n"
            "        items.append(x)\n"
            "    add(1)\n"
            "    add(2)\n"
            "    return items\n"
            "print(outer())"
        )
        assert rc == 0
        assert out == "[1, 2]"

    def test_nonlocal_flag_pattern(self):
        """nonlocal flag set by inner function"""
        out, err, rc = clython_run(
            "def search(items, target):\n"
            "    found = False\n"
            "    def check(item):\n"
            "        nonlocal found\n"
            "        if item == target:\n"
            "            found = True\n"
            "    for item in items:\n"
            "        check(item)\n"
            "    return found\n"
            "print(search([1, 2, 3, 4], 3))\n"
            "print(search([1, 2, 3, 4], 9))"
        )
        assert rc == 0
        assert out == "True\nFalse"

    def test_nonlocal_with_default_arg_outer(self):
        """nonlocal works when outer function has default arguments"""
        out, err, rc = clython_run(
            "def outer(start=0):\n"
            "    val = start\n"
            "    def bump(n=1):\n"
            "        nonlocal val\n"
            "        val += n\n"
            "        return val\n"
            "    return bump\n"
            "b = outer(10)\n"
            "print(b(), b(5))"
        )
        assert rc == 0
        assert out == "11 16"

    def test_nonlocal_in_loop(self):
        """nonlocal variable modified in a loop"""
        out, err, rc = clython_run(
            "def outer():\n"
            "    total = 0\n"
            "    def add_all(vals):\n"
            "        nonlocal total\n"
            "        for v in vals:\n"
            "            total += v\n"
            "    add_all([1, 2, 3, 4, 5])\n"
            "    return total\n"
            "print(outer())"
        )
        assert rc == 0
        assert out == "15"

    def test_nonlocal_and_global_coexist(self):
        """nonlocal and global can coexist in nested functions"""
        out, err, rc = clython_run(
            "module_var = 'module'\n"
            "def outer():\n"
            "    enc_var = 'enclosing'\n"
            "    def inner():\n"
            "        global module_var\n"
            "        nonlocal enc_var\n"
            "        module_var = 'changed_module'\n"
            "        enc_var = 'changed_enc'\n"
            "    inner()\n"
            "    return enc_var\n"
            "enc_result = outer()\n"
            "print(enc_result)\n"
            "print(module_var)"
        )
        assert rc == 0
        assert out == "changed_enc\nchanged_module"

    @pytest.mark.xfail(reason="Clython validates nonlocal at runtime, not compile-time")
    def test_nonlocal_undefined_enclosing_raises(self):
        """nonlocal referencing undefined enclosing variable is a SyntaxError"""
        out, err, rc = clython_run(
            "def outer():\n"
            "    def inner():\n"
            "        nonlocal no_such_var\n"
            "        no_such_var = 1\n"
            "    inner()"
        )
        assert rc != 0

    def test_nonlocal_bank_account_pattern(self):
        """bank account pattern with nonlocal balance"""
        out, err, rc = clython_run(
            "def make_account(initial):\n"
            "    balance = initial\n"
            "    def deposit(n):\n"
            "        nonlocal balance\n"
            "        balance += n\n"
            "    def withdraw(n):\n"
            "        nonlocal balance\n"
            "        balance -= n\n"
            "    def get():\n"
            "        return balance\n"
            "    return deposit, withdraw, get\n"
            "dep, wdraw, bal = make_account(100)\n"
            "dep(50)\nwdraw(30)\nprint(bal())"
        )
        assert rc == 0
        assert out == "120"

    def test_nonlocal_reassign_enclosing(self):
        """nonlocal allows full reassignment of enclosing variable"""
        out, err, rc = clython_run(
            "def outer():\n"
            "    state = 'initial'\n"
            "    def change():\n"
            "        nonlocal state\n"
            "        state = 'final'\n"
            "    change()\n"
            "    return state\n"
            "print(outer())"
        )
        assert rc == 0
        assert out == "final"
