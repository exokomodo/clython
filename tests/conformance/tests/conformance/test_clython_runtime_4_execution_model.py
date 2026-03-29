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


@pytest.mark.xfail(reason="Clython does not clean up exception variable after except block")
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


@pytest.mark.xfail(reason="Clython eval() may not be implemented")
def test_eval_with_namespace():
    source = """
ns = {'x': 10, 'y': 20}
result = eval('x + y', ns)
print(result)
"""
    out, err, rc = clython_run(source)
    assert rc == 0
    assert out == "30"


@pytest.mark.xfail(reason="Clython exec() may not be fully implemented")
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
