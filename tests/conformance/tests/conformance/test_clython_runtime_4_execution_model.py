"""
Clython Runtime Tests: Section 4 - Execution Model

Tests scope resolution and name binding semantics via the Clython binary.
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


def test_local_variable_binding():
    source = """
def func():
    x = 42
    return x
print(func())
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "42"


def test_local_variable_not_visible_outside():
    source = """
def func():
    local = 99
func()
try:
    print(local)
except NameError:
    print('NameError')
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "NameError"


def test_enclosing_scope_closure():
    source = """
def outer():
    x = 'from outer'
    def inner():
        return x
    return inner()
print(outer())
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "from outer"


def test_global_variable_read():
    source = """
module_var = 'global'
def func():
    return module_var
print(func())
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "global"


def test_global_statement():
    source = """
counter = 0
def increment():
    global counter
    counter += 1
increment()
increment()
print(counter)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "2"


def test_nonlocal_statement():
    source = """
def outer():
    x = 0
    def inner():
        nonlocal x
        x += 1
    inner()
    inner()
    return x
print(outer())
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "2"


def test_global_and_nonlocal_coexist():
    source = """
g = 'global'
def outer():
    enc = 'enclosing'
    def inner():
        global g
        nonlocal enc
        g = 'modified'
        enc = 'modified_enc'
    inner()
    return enc
print(outer())
print(g)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "modified_enc\nmodified"


def test_legb_resolution_order():
    source = """
x = 'builtin_not_shadowed'
x = 'global'
def outer():
    x = 'enclosing'
    def inner():
        x = 'local'
        return x
    return inner()
print(outer())
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "local"


def test_legb_enclosing_used_when_no_local():
    source = """
def outer():
    x = 'enclosing'
    def inner():
        return x
    return inner()
print(outer())
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "enclosing"


def test_builtin_access():
    out, err, rc = clython_run("print(len([1, 2, 3]))")
    assert rc == 0
    assert out == "3"


def test_multiple_assignment_targets():
    source = """
a = b = c = 0
a += 1
b += 2
print(a, b, c)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "1 2 0"


def test_augmented_assignment():
    source = """
x = 10
x += 5
x *= 2
print(x)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "30"


def test_class_scope_class_var():
    source = """
class MyClass:
    value = 42
    def get(self): return self.value
obj = MyClass()
print(obj.get())
print(MyClass.value)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "42\n42"


def test_class_instance_var_shadows_class_var():
    source = """
class Foo:
    x = 'class'
    def set_instance(self): self.x = 'instance'
f = Foo()
print(f.x)
f.set_instance()
print(f.x)
print(Foo.x)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "class\ninstance\nclass"


def test_comprehension_scope_isolation():
    source = """
x = 'outer'
result = [x for x in [1, 2, 3]]
print(x)
print(result)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    # In Python 3, comprehension x should not leak
    assert out == "outer\n[1, 2, 3]"


def test_exception_variable_cleaned_up():
    source = """
try:
    raise ValueError('test')
except ValueError as e:
    msg = str(e)
print(msg)
try:
    print(e)
except NameError:
    print('e cleaned up')
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "test\ne cleaned up"


def test_nested_functions_multiple_closures():
    source = """
def make_adder(n):
    return lambda x: x + n
add3 = make_adder(3)
add10 = make_adder(10)
print(add3(7))
print(add10(7))
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "10\n17"


def test_eval_with_namespace():
    source = """
ns = {'x': 10, 'y': 20}
result = eval('x + y', ns)
print(result)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "30"


def test_exec_creates_variable():
    source = """
ns = {}
exec('z = 99', ns)
print(ns['z'])
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "99"


def test_for_loop_binding():
    source = """
for i in range(3):
    pass
print(i)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "2"


def test_try_except_binding():
    source = """
try:
    result = 1 / 0
except ZeroDivisionError as e:
    caught = True
print(caught)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True"


def test_generator_expression_scope():
    source = """
x = 'outer'
gen = (x * 2 for x in [1, 2, 3])
print(x)
print(list(gen))
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "outer\n[2, 4, 6]"


# --- Additional tests to cover all source test cases ---

def test_basic_name_binding():
    """Test basic name binding patterns."""
    source = "x = 42\nprint(x)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "42"


def test_multiple_assignment_binding():
    """Test multiple assignment and tuple unpacking."""
    source = "a, b, c = 1, 2, 3\nprint(a, b, c)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "1 2 3"


def test_augmented_assignment_binding():
    """Test augmented assignment binding behavior."""
    source = "x = 5\nx += 3\nprint(x)\nx *= 2\nprint(x)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "8\n16"


def test_binding_vs_reference_patterns():
    """Test binding vs reference in name usage."""
    source = "x = [1, 2, 3]\ny = x\ny.append(4)\nprint(x)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "[1, 2, 3, 4]"


def test_local_scope_patterns():
    """Test local scope resolution."""
    source = "def f():\n    x = 'local'\n    return x\nprint(f())"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "local"


def test_enclosing_scope_patterns():
    """Test enclosing scope resolution."""
    source = """
def outer():
    x = 'outer'
    def inner():
        return x
    return inner()
print(outer())
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "outer"


def test_global_scope_patterns():
    """Test global scope resolution."""
    source = "g = 'global'\ndef f():\n    global g\n    g = 'modified'\nf()\nprint(g)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "modified"


def test_builtin_scope_patterns():
    """Test built-in scope resolution."""
    source = "print(len([1, 2, 3]))\nprint(type(42).__name__)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "3\nint"


def test_global_statement_patterns():
    """Test global statement usage."""
    source = "x = 1\ndef f():\n    global x\n    x = 99\nf()\nprint(x)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "99"


def test_nonlocal_statement_patterns():
    """Test nonlocal statement usage."""
    source = """
def outer():
    x = 0
    def inner():
        nonlocal x
        x += 1
    inner()
    inner()
    return x
print(outer())
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "2"


def test_global_nonlocal_interaction():
    """Test interaction between global and nonlocal."""
    source = """
count = 0
def outer():
    total = 0
    def inner():
        global count
        nonlocal total
        count += 1
        total += 1
    inner()
    inner()
    return total
print(outer())
print(count)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "2\n2"


def test_class_scope_patterns():
    """Test class scope behavior."""
    source = """
class C:
    class_var = 'class'
    def get(self):
        return self.class_var
c = C()
print(c.get())
print(C.class_var)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "class\nclass"


def test_class_variable_vs_instance_variable():
    """Test class vs instance variable patterns."""
    source = """
class C:
    shared = 0
    def __init__(self):
        self.instance = 1
c1 = C()
c2 = C()
c1.instance = 99
print(c1.instance)
print(c2.instance)
print(C.shared)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "99\n1\n0"


def test_method_scope_patterns():
    """Test method scope behavior."""
    source = """
class C:
    def __init__(self, v):
        self.v = v
    def double(self):
        return self.v * 2
c = C(5)
print(c.double())
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "10"


def test_code_block_nesting():
    """Test nested code block structure."""
    source = """
def outer():
    def middle():
        def inner():
            return 'deep'
        return inner()
    return middle()
print(outer())
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "deep"


def test_module_level_structure():
    """Test module-level program structure."""
    source = "x = 1\ny = 2\nz = x + y\nprint(z)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "3"


def test_globals_locals_patterns():
    """Test globals() and locals() function usage."""
    source = """
x = 42
def f():
    local_var = 99
    return 'local_var' in locals()
print('x' in globals())
print(f())
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True\nTrue"


@pytest.mark.xfail(strict=False, reason="vars() on instances may not be implemented in Clython")
def test_vars_dir_patterns():
    """Test vars() and dir() introspection patterns."""
    source = """
class C:
    def __init__(self):
        self.x = 1
        self.y = 2
c = C()
v = vars(c)
print('x' in v)
print('y' in v)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "True\nTrue"


def test_eval_exec_patterns():
    """Test eval() and exec() usage patterns."""
    source = "result = eval('1 + 2 + 3')\nprint(result)"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "6"


def test_exception_scope_patterns():
    """Test exception variable scope."""
    source = """
try:
    raise ValueError('test')
except ValueError as e:
    msg = str(e)
print(msg)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "test"


def test_exception_propagation_patterns():
    """Test exception propagation through scopes."""
    source = """
def inner():
    raise ValueError('from inner')
def outer():
    try:
        inner()
    except ValueError as e:
        return str(e)
print(outer())
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "from inner"


def test_statement_vs_expression_structure():
    """Test distinction between statements and expressions."""
    source = "x = 1 + 2\nprint(x)\n3 + 4\nprint('ok')"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "3\nok"


def test_scope_ast_structure_consistency():
    """Test scope-related AST structure consistency."""
    source = "x = 1\ndef f():\n    y = 2\n    return y\nprint(x)\nprint(f())"
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "1\n2"


@pytest.mark.xfail(strict=False, reason="sys.modules['__main__'] may not be available in Clython")
def test_execution_model_introspection():
    """Test ability to analyze execution model programmatically."""
    source = """
import sys
print(type(sys.modules['__main__']).__name__)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "module"


def test_comprehensive_execution_patterns():
    """Test comprehensive real-world execution patterns."""
    source = """
def fibonacci(n):
    if n <= 1: return n
    a, b = 0, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b
result = [fibonacci(i) for i in range(8)]
print(result)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "[0, 1, 1, 2, 3, 5, 8, 13]"
