"""Clython conformance tests — Section 4: Execution Model.

Tests that the Clython interpreter correctly implements Python 3.12 execution model:
code blocks, naming and binding (LEGB), global/nonlocal, and exception context.
"""
import os
import subprocess
import pytest

CLYTHON_BIN = os.environ.get("CLYTHON_BIN")

def clython_run(source: str, *, timeout: int = 10):
    """Run source through Clython, return (stdout, stderr, returncode)."""
    result = subprocess.run(
        [CLYTHON_BIN, "-c", source],
        capture_output=True, text=True, timeout=timeout
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode

pytestmark = pytest.mark.skipif(
    not CLYTHON_BIN, reason="CLYTHON_BIN not set — skipping Clython-specific tests"
)


# ── 4.1 Structure of a program ────────────────────────────────────────────

class TestSection41CodeBlocks:
    def test_module_is_code_block(self):
        """Module-level code is a code block."""
        out, _, rc = clython_run("x = 1\ny = 2\nprint(x + y)")
        assert rc == 0 and out == "3"

    def test_function_body_is_code_block(self):
        out, _, rc = clython_run("def f():\n    x = 10\n    return x\nprint(f())")
        assert rc == 0 and out == "10"

    def test_class_body_is_code_block(self):
        out, _, rc = clython_run("class C:\n    x = 42\nprint(C.x)")
        assert rc == 0 and out == "42"


# ── 4.2 Naming and binding ────────────────────────────────────────────────

class TestSection42LEGB:
    def test_local_scope(self):
        out, _, rc = clython_run("def f():\n    x = 1\n    return x\nprint(f())")
        assert rc == 0 and out == "1"

    def test_enclosing_scope(self):
        out, _, rc = clython_run("def outer():\n    x = 10\n    def inner():\n        return x\n    return inner()\nprint(outer())")
        assert rc == 0 and out == "10"

    def test_global_scope(self):
        out, _, rc = clython_run("x = 42\ndef f():\n    return x\nprint(f())")
        assert rc == 0 and out == "42"

    def test_builtin_scope(self):
        out, _, rc = clython_run("def f():\n    return len([1, 2, 3])\nprint(f())")
        assert rc == 0 and out == "3"

    def test_local_shadows_global(self):
        out, _, rc = clython_run("x = 'global'\ndef f():\n    x = 'local'\n    return x\nprint(f())\nprint(x)")
        assert rc == 0 and out == "local\nglobal"

    def test_enclosing_shadows_global(self):
        out, _, rc = clython_run("x = 'global'\ndef outer():\n    x = 'enclosing'\n    def inner():\n        return x\n    return inner()\nprint(outer())")
        assert rc == 0 and out == "enclosing"

    def test_nested_closures(self):
        out, _, rc = clython_run("def a():\n    x = 1\n    def b():\n        def c():\n            return x\n        return c()\n    return b()\nprint(a())")
        assert rc == 0 and out == "1"


class TestSection42GlobalStatement:
    def test_global_write(self):
        out, _, rc = clython_run("x = 0\ndef f():\n    global x\n    x = 42\nf()\nprint(x)")
        assert rc == 0 and out == "42"

    def test_global_read_and_write(self):
        out, _, rc = clython_run("count = 0\ndef inc():\n    global count\n    count += 1\ninc()\ninc()\nprint(count)")
        assert rc == 0 and out == "2"


class TestSection42NonlocalStatement:
    def test_nonlocal_write(self):
        out, _, rc = clython_run("def outer():\n    x = 0\n    def inner():\n        nonlocal x\n        x = 42\n    inner()\n    return x\nprint(outer())")
        assert rc == 0 and out == "42"

    def test_nonlocal_increment(self):
        out, _, rc = clython_run("def counter():\n    n = 0\n    def inc():\n        nonlocal n\n        n += 1\n        return n\n    return inc\nc = counter()\nprint(c())\nprint(c())\nprint(c())")
        assert rc == 0 and out == "1\n2\n3"


class TestSection42NameResolutionErrors:
    def test_undefined_name(self):
        _, err, rc = clython_run("print(undefined_var)")
        assert rc != 0 and "NameError" in err

    def test_undefined_in_function(self):
        _, err, rc = clython_run("def f():\n    return undefined_var\nf()")
        assert rc != 0 and "NameError" in err


# ── 4.3 Exceptions ────────────────────────────────────────────────────────

class TestSection43Exceptions:
    def test_try_except(self):
        out, _, rc = clython_run("try:\n    x = 1 / 0\nexcept ZeroDivisionError:\n    print('caught')")
        assert rc == 0 and out == "caught"

    def test_try_except_as(self):
        out, _, rc = clython_run("try:\n    raise ValueError('oops')\nexcept ValueError as e:\n    print(e)")
        assert rc == 0 and out == "oops"

    def test_try_finally(self):
        out, _, rc = clython_run("try:\n    print('try')\nfinally:\n    print('finally')")
        assert rc == 0 and out == "try\nfinally"

    def test_try_except_finally(self):
        out, _, rc = clython_run("try:\n    x = 1 / 0\nexcept ZeroDivisionError:\n    print('caught')\nfinally:\n    print('done')")
        assert rc == 0 and out == "caught\ndone"

    def test_try_else(self):
        out, _, rc = clython_run("try:\n    x = 1\nexcept:\n    print('error')\nelse:\n    print('ok')")
        assert rc == 0 and out == "ok"

    def test_raise_runtime_error(self):
        _, err, rc = clython_run("raise RuntimeError('boom')")
        assert rc != 0 and "RuntimeError" in err

    def test_exception_in_function(self):
        out, _, rc = clython_run("def f():\n    try:\n        return 1 / 0\n    except ZeroDivisionError:\n        return 'caught'\nprint(f())")
        assert rc == 0 and out == "caught"

    def test_nested_try_except(self):
        out, _, rc = clython_run("try:\n    try:\n        raise ValueError('inner')\n    except ValueError:\n        print('inner caught')\n        raise TypeError('outer')\nexcept TypeError:\n    print('outer caught')")
        assert rc == 0 and out == "inner caught\nouter caught"

    def test_reraise(self):
        out, _, rc = clython_run("try:\n    try:\n        raise ValueError('x')\n    except ValueError:\n        raise\nexcept ValueError as e:\n    print(e)")
        assert rc == 0 and out == "x"


# ── 4.1 Additional code block tests (from test_section_4_execution_model) ─

class TestSection41NestedCodeBlocks:
    """Nested code block structure."""

    def test_nested_functions(self):
        out, _, rc = clython_run(
            "def outer():\n"
            "    def inner():\n"
            "        def nested():\n"
            "            return 'deep'\n"
            "        return nested()\n"
            "    return inner()\n"
            "print(outer())"
        )
        assert rc == 0 and out == "deep"

    def test_class_with_methods(self):
        out, _, rc = clython_run(
            "class C:\n"
            "    x = 10\n"
            "    def get_x(self):\n"
            "        return self.x\n"
            "print(C().get_x())"
        )
        assert rc == 0 and out == "10"

    def test_function_with_class(self):
        out, _, rc = clython_run(
            "def factory():\n"
            "    class C:\n"
            "        val = 99\n"
            "    return C.val\n"
            "print(factory())"
        )
        assert rc == 0 and out == "99"


# ── 4.2 Additional binding tests ─────────────────────────────────────────

class TestSection42BindingPatterns:
    """Additional name binding and assignment patterns."""

    def test_tuple_unpacking(self):
        out, _, rc = clython_run("a, b = 1, 2\nprint(a, b)")
        assert rc == 0 and out == "1 2"

    def test_triple_unpacking(self):
        out, _, rc = clython_run("a, b, c = 'x', 'y', 'z'\nprint(a, b, c)")
        assert rc == 0 and out == "x y z"

    def test_starred_unpacking(self):
        out, _, rc = clython_run(
            "first, *rest = [1, 2, 3, 4, 5]\nprint(first)\nprint(rest)"
        )
        assert rc == 0 and out == "1\n[2, 3, 4, 5]"

    def test_augmented_assignment_int(self):
        out, _, rc = clython_run("x = 10\nx += 5\nx *= 2\nprint(x)")
        assert rc == 0 and out == "30"

    def test_augmented_assignment_list(self):
        out, _, rc = clython_run("items = [1]\nitems += [2, 3]\nprint(items)")
        assert rc == 0 and out == "[1, 2, 3]"

    def test_for_loop_binding(self):
        """For loop target variable is bound in enclosing scope."""
        out, _, rc = clython_run(
            "for i in range(5):\n    pass\nprint(i)"
        )
        assert rc == 0 and out == "4"


class TestSection42ClosureCapture:
    """Closure variable capture semantics."""

    def test_closure_captures_variable(self):
        out, _, rc = clython_run(
            "def make_adder(n):\n"
            "    def adder(x):\n"
            "        return x + n\n"
            "    return adder\n"
            "add5 = make_adder(5)\nprint(add5(3))"
        )
        assert rc == 0 and out == "8"

    def test_closure_captures_late_binding(self):
        """Closures capture the variable, not the value."""
        out, _, rc = clython_run(
            "def make_funcs():\n"
            "    funcs = []\n"
            "    for i in range(3):\n"
            "        def f(x=i):\n"
            "            return x\n"
            "        funcs.append(f)\n"
            "    return funcs\n"
            "fs = make_funcs()\nprint(fs[0](), fs[1](), fs[2]())"
        )
        assert rc == 0 and out == "0 1 2"

    def test_multiple_closures_shared_scope(self):
        out, _, rc = clython_run(
            "def pair():\n"
            "    x = 0\n"
            "    def get():\n"
            "        return x\n"
            "    def inc():\n"
            "        nonlocal x\n"
            "        x += 1\n"
            "    return get, inc\n"
            "g, i = pair()\ni()\ni()\nprint(g())"
        )
        assert rc == 0 and out == "2"


class TestSection42GlobalNonlocalInteraction:
    """Global and nonlocal coexistence."""

    def test_global_and_nonlocal_coexist(self):
        out, _, rc = clython_run(
            "g = 'global'\n"
            "def outer():\n"
            "    e = 'enclosing'\n"
            "    def inner():\n"
            "        global g\n"
            "        nonlocal e\n"
            "        g = 'modified_g'\n"
            "        e = 'modified_e'\n"
            "    inner()\n"
            "    return e\n"
            "result = outer()\nprint(g)\nprint(result)"
        )
        assert rc == 0 and out == "modified_g\nmodified_e"

    def test_global_creates_new_name(self):
        out, _, rc = clython_run(
            "def f():\n"
            "    global new_var\n"
            "    new_var = 'created'\n"
            "f()\nprint(new_var)"
        )
        assert rc == 0 and out == "created"


# ── 4.2 Comprehension scope ──────────────────────────────────────────────

class TestSection42ComprehensionScopes:
    """Comprehension scope isolation."""

    def test_listcomp_scope_isolation(self):
        """List comprehension variable doesn't leak."""
        out, _, rc = clython_run(
            "x = 'outer'\nresult = [x for x in range(3)]\nprint(x)"
        )
        assert rc == 0 and out == "outer"

    def test_listcomp_accesses_enclosing(self):
        out, _, rc = clython_run(
            "n = 10\nresult = [n + x for x in range(3)]\nprint(result)"
        )
        assert rc == 0 and out == "[10, 11, 12]"

    def test_nested_listcomp(self):
        out, _, rc = clython_run(
            "result = [(i, j) for i in range(2) for j in range(2)]\nprint(result)"
        )
        assert rc == 0 and out == "[(0, 0), (0, 1), (1, 0), (1, 1)]"

    def test_dictcomp(self):
        out, _, rc = clython_run(
            "d = {k: k*2 for k in range(3)}\nprint(d)"
        )
        assert rc == 0 and out == "{0: 0, 1: 2, 2: 4}"

    @pytest.mark.xfail(reason="set comprehension may not be implemented")
    def test_setcomp(self):
        out, _, rc = clython_run(
            "s = {x % 3 for x in range(6)}\nprint(sorted(s))"
        )
        assert rc == 0 and out == "[0, 1, 2]"

    def test_generator_expression(self):
        out, _, rc = clython_run(
            "g = (x * 2 for x in range(4))\nprint(list(g))"
        )
        assert rc == 0 and out == "[0, 2, 4, 6]"


# ── 4.3 Additional exception tests ───────────────────────────────────────

class TestSection43ExceptionPropagation:
    """Exception propagation through call stack."""

    def test_exception_propagates_through_calls(self):
        out, _, rc = clython_run(
            "def inner():\n"
            "    raise ValueError('deep')\n"
            "def middle():\n"
            "    return inner()\n"
            "def outer():\n"
            "    try:\n"
            "        return middle()\n"
            "    except ValueError as e:\n"
            "        return str(e)\n"
            "print(outer())"
        )
        assert rc == 0 and out == "deep"

    @pytest.mark.xfail(reason="custom exception classes not yet fully supported")
    def test_custom_exception_class(self):
        out, _, rc = clython_run(
            "class MyError(Exception): pass\n"
            "try:\n"
            "    raise MyError('custom')\n"
            "except MyError as e:\n"
            "    print(e)"
        )
        assert rc == 0 and out == "custom"

    @pytest.mark.xfail(reason="exception hierarchy catching not yet supported")
    def test_exception_hierarchy_catch(self):
        """Catching parent exception type catches child."""
        out, _, rc = clython_run(
            "class Base(Exception): pass\n"
            "class Child(Base): pass\n"
            "try:\n"
            "    raise Child('child')\n"
            "except Base as e:\n"
            "    print(e)"
        )
        assert rc == 0 and out == "child"

    def test_multiple_except_clauses(self):
        out, _, rc = clython_run(
            "def f(n):\n"
            "    try:\n"
            "        if n == 0:\n"
            "            raise ValueError('val')\n"
            "        else:\n"
            "            raise TypeError('typ')\n"
            "    except ValueError:\n"
            "        return 'V'\n"
            "    except TypeError:\n"
            "        return 'T'\n"
            "print(f(0), f(1))"
        )
        assert rc == 0 and out == "V T"

    @pytest.mark.xfail(reason="tuple except may not be implemented")
    def test_except_tuple(self):
        """Catch multiple exception types with a tuple."""
        out, _, rc = clython_run(
            "try:\n"
            "    raise TypeError('t')\n"
            "except (ValueError, TypeError) as e:\n"
            "    print('caught', e)"
        )
        assert rc == 0 and out == "caught t"

    def test_finally_always_runs_on_exception(self):
        out, _, rc = clython_run(
            "def f():\n"
            "    try:\n"
            "        raise ValueError('x')\n"
            "    except ValueError:\n"
            "        print('caught')\n"
            "    finally:\n"
            "        print('finally')\n"
            "f()"
        )
        assert rc == 0 and out == "caught\nfinally"

    @pytest.mark.xfail(reason="finally block not executed on early return")
    def test_finally_runs_on_return(self):
        out, _, rc = clython_run(
            "def f():\n"
            "    try:\n"
            "        return 'ret'\n"
            "    finally:\n"
            "        print('finally')\n"
            "result = f()\nprint(result)"
        )
        assert rc == 0 and out == "finally\nret"


# ── 4.2 Class scope interactions ──────────────────────────────────────────

class TestSection42ClassScopeInteraction:
    """Class scope variable access patterns."""

    def test_class_var_access_via_self(self):
        out, _, rc = clython_run(
            "class C:\n"
            "    x = 42\n"
            "    def get(self):\n"
            "        return self.x\n"
            "print(C().get())"
        )
        assert rc == 0 and out == "42"

    def test_class_var_vs_instance_var(self):
        out, _, rc = clython_run(
            "class C:\n"
            "    shared = []\n"
            "    def __init__(self, v):\n"
            "        self.own = v\n"
            "a = C(1)\nb = C(2)\nprint(a.own, b.own)\nprint(a.shared is b.shared)"
        )
        assert rc == 0 and out == "1 2\nTrue"

    def test_method_scope_nested_function(self):
        out, _, rc = clython_run(
            "class C:\n"
            "    def method(self):\n"
            "        def helper():\n"
            "            return 'helped'\n"
            "        return helper()\n"
            "print(C().method())"
        )
        assert rc == 0 and out == "helped"


# ── 4.2 Dynamic features ─────────────────────────────────────────────────

class TestSection42DynamicFeatures:
    """Dynamic execution: eval, exec."""

    @pytest.mark.xfail(reason="eval() may not be implemented")
    def test_eval_basic(self):
        out, _, rc = clython_run("print(eval('2 + 3'))")
        assert rc == 0 and out == "5"

    @pytest.mark.xfail(reason="exec() may not be implemented")
    def test_exec_basic(self):
        out, _, rc = clython_run("exec('x = 42')\nprint(x)")
        assert rc == 0 and out == "42"

    @pytest.mark.xfail(reason="globals() may not be implemented")
    def test_globals_contains_module_var(self):
        out, _, rc = clython_run(
            "x = 42\nprint('x' in globals())"
        )
        assert rc == 0 and out == "True"

    @pytest.mark.xfail(reason="locals() may not be implemented")
    def test_locals_in_function(self):
        out, _, rc = clython_run(
            "def f():\n"
            "    x = 10\n"
            "    return 'x' in locals()\n"
            "print(f())"
        )
        assert rc == 0 and out == "True"
