"""
Section 3.3: Special Method Names - Conformance Test Suite

Tests Python Language Reference Section 3.3 compliance across implementations.
Based on formal specifications and prose assertions for special method definitions.

Language Reference requirements tested:
    - Object initialization: __new__, __init__, __del__
    - String representation: __str__, __repr__, __format__, __bytes__
    - Numeric operations: __add__, __sub__, __mul__, __truediv__, __floordiv__, etc.
    - Comparison operations: __eq__, __ne__, __lt__, __le__, __gt__, __ge__
    - Container operations: __len__, __getitem__, __setitem__, __delitem__
    - Attribute access: __getattr__, __setattr__, __delattr__, __getattribute__
    - Callable objects: __call__
    - Context managers: __enter__, __exit__
    - Iterator protocol: __iter__, __next__
    - Descriptor protocol: __get__, __set__, __delete__
    - Method signatures and return value expectations
"""

import ast
import pytest
import sys
from typing import Any


class SpecialMethodTester:
    """Helper class for testing special method conformance.
    
    Follows established AST-based validation pattern from previous sections.
    """
    
    def assert_method_syntax_parses(self, source: str):
        """Test that special method definition syntax parses correctly.
        
        Args:
            source: Python class with special method source code
        """
        try:
            tree = ast.parse(source)
            # Verify the AST contains class definition
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    return tree
            pytest.fail(f"Expected ClassDef not found in parsed AST for: {source}")
        except SyntaxError as e:
            pytest.fail(f"Special method syntax {source!r} failed to parse: {e}")
    
    def assert_method_syntax_error(self, source: str):
        """Test that invalid special method syntax raises SyntaxError.
        
        Args:
            source: Python special method source code that should be invalid
        """
        with pytest.raises(SyntaxError):
            ast.parse(source)

    def get_class_methods(self, source: str) -> list:
        """Get list of method names from a class definition.
        
        Args:
            source: Python class definition source
            
        Returns:
            List of method names defined in the class
        """
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = []
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        methods.append(item.name)
                return methods
        return []


class TestSection33ObjectLifecycleMethods:
    """Test Section 3.3: Object Lifecycle Special Methods"""
    
    @pytest.fixture
    def tester(self):
        return SpecialMethodTester()

    def test_object_creation_methods(self, tester):
        """Test object creation and initialization methods"""
        # Language Reference: __new__, __init__ methods
        creation_methods = [
            """class TestClass:
    def __new__(cls):
        return super().__new__(cls)""",
            
            """class TestClass:
    def __init__(self):
        pass""",
            
            """class TestClass:
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)
        
    def __init__(self, value):
        self.value = value"""
        ]
        
        for source in creation_methods:
            tree = tester.assert_method_syntax_parses(source)
            methods = tester.get_class_methods(source)
            assert any(method in ['__new__', '__init__'] for method in methods)

    def test_object_deletion_methods(self, tester):
        """Test object deletion and cleanup methods"""
        # Language Reference: __del__ method
        deletion_methods = [
            """class TestClass:
    def __del__(self):
        pass""",
            
            """class ResourceClass:
    def __del__(self):
        self.cleanup()
        super().__del__()"""
        ]
        
        for source in deletion_methods:
            tree = tester.assert_method_syntax_parses(source)
            methods = tester.get_class_methods(source)
            assert '__del__' in methods

    def test_object_representation_methods(self, tester):
        """Test object string representation methods"""
        # Language Reference: __str__, __repr__, __format__, __bytes__
        representation_methods = [
            """class TestClass:
    def __str__(self):
        return 'string representation'""",
            
            """class TestClass:
    def __repr__(self):
        return 'TestClass()'""",
            
            """class TestClass:
    def __format__(self, format_spec):
        return f'formatted: {format_spec}'""",
            
            """class TestClass:
    def __bytes__(self):
        return b'byte representation'"""
        ]
        
        for source in representation_methods:
            tree = tester.assert_method_syntax_parses(source)
            methods = tester.get_class_methods(source)
            assert any(method in ['__str__', '__repr__', '__format__', '__bytes__'] for method in methods)

    def test_hash_and_bool_methods(self, tester):
        """Test hash and boolean conversion methods"""
        # Language Reference: __hash__, __bool__
        conversion_methods = [
            """class TestClass:
    def __hash__(self):
        return hash(self.value)""",
            
            """class TestClass:
    def __bool__(self):
        return True""",
            
            """class TestClass:
    def __hash__(self):
        return 42
        
    def __bool__(self):
        return bool(self.data)"""
        ]
        
        for source in conversion_methods:
            tree = tester.assert_method_syntax_parses(source)
            methods = tester.get_class_methods(source)
            assert any(method in ['__hash__', '__bool__'] for method in methods)


class TestSection33ArithmeticMethods:
    """Test arithmetic operation special methods"""
    
    @pytest.fixture
    def tester(self):
        return SpecialMethodTester()

    def test_basic_arithmetic_methods(self, tester):
        """Test basic arithmetic operation methods"""
        # Language Reference: __add__, __sub__, __mul__, __truediv__, __floordiv__
        arithmetic_methods = [
            """class Number:
    def __add__(self, other):
        return Number(self.value + other.value)""",
            
            """class Number:
    def __sub__(self, other):
        return Number(self.value - other.value)""",
            
            """class Number:
    def __mul__(self, other):
        return Number(self.value * other.value)""",
            
            """class Number:
    def __truediv__(self, other):
        return Number(self.value / other.value)""",
            
            """class Number:
    def __floordiv__(self, other):
        return Number(self.value // other.value)"""
        ]
        
        for source in arithmetic_methods:
            tree = tester.assert_method_syntax_parses(source)
            methods = tester.get_class_methods(source)
            expected = ['__add__', '__sub__', '__mul__', '__truediv__', '__floordiv__']
            assert any(method in expected for method in methods)

    def test_reflected_arithmetic_methods(self, tester):
        """Test reflected (right-hand) arithmetic methods"""
        # Language Reference: __radd__, __rsub__, __rmul__, etc.
        reflected_methods = [
            """class Number:
    def __radd__(self, other):
        return Number(other + self.value)""",
            
            """class Number:
    def __rsub__(self, other):
        return Number(other - self.value)""",
            
            """class Number:
    def __rmul__(self, other):
        return Number(other * self.value)""",
            
            """class Number:
    def __rtruediv__(self, other):
        return Number(other / self.value)"""
        ]
        
        for source in reflected_methods:
            tree = tester.assert_method_syntax_parses(source)
            methods = tester.get_class_methods(source)
            expected = ['__radd__', '__rsub__', '__rmul__', '__rtruediv__']
            assert any(method in expected for method in methods)

    def test_augmented_assignment_methods(self, tester):
        """Test augmented assignment operation methods"""
        # Language Reference: __iadd__, __isub__, __imul__, etc.
        augmented_methods = [
            """class Number:
    def __iadd__(self, other):
        self.value += other.value
        return self""",
            
            """class Number:
    def __isub__(self, other):
        self.value -= other.value
        return self""",
            
            """class Number:
    def __imul__(self, other):
        self.value *= other.value
        return self""",
            
            """class Number:
    def __itruediv__(self, other):
        self.value /= other.value
        return self"""
        ]
        
        for source in augmented_methods:
            tree = tester.assert_method_syntax_parses(source)
            methods = tester.get_class_methods(source)
            expected = ['__iadd__', '__isub__', '__imul__', '__itruediv__']
            assert any(method in expected for method in methods)

    def test_unary_operation_methods(self, tester):
        """Test unary operation methods"""
        # Language Reference: __neg__, __pos__, __abs__, __invert__
        unary_methods = [
            """class Number:
    def __neg__(self):
        return Number(-self.value)""",
            
            """class Number:
    def __pos__(self):
        return Number(+self.value)""",
            
            """class Number:
    def __abs__(self):
        return Number(abs(self.value))""",
            
            """class Number:
    def __invert__(self):
        return Number(~self.value)"""
        ]
        
        for source in unary_methods:
            tree = tester.assert_method_syntax_parses(source)
            methods = tester.get_class_methods(source)
            expected = ['__neg__', '__pos__', '__abs__', '__invert__']
            assert any(method in expected for method in methods)

    def test_complex_arithmetic_methods(self, tester):
        """Test complex arithmetic methods"""
        # Additional arithmetic methods
        complex_methods = [
            """class Number:
    def __mod__(self, other):
        return Number(self.value % other.value)""",
            
            """class Number:
    def __divmod__(self, other):
        q, r = divmod(self.value, other.value)
        return Number(q), Number(r)""",
            
            """class Number:
    def __pow__(self, other, modulo=None):
        if modulo is None:
            return Number(pow(self.value, other.value))
        return Number(pow(self.value, other.value, modulo))""",
            
            """class Integer:
    def __lshift__(self, other):
        return Integer(self.value << other)
        
    def __rshift__(self, other):
        return Integer(self.value >> other)""",
            
            """class Integer:
    def __and__(self, other):
        return Integer(self.value & other.value)
        
    def __or__(self, other):
        return Integer(self.value | other.value)
        
    def __xor__(self, other):
        return Integer(self.value ^ other.value)"""
        ]
        
        for source in complex_methods:
            tree = tester.assert_method_syntax_parses(source)
            # Just verify they parse correctly


class TestSection33ComparisonMethods:
    """Test comparison operation special methods"""
    
    @pytest.fixture
    def tester(self):
        return SpecialMethodTester()

    def test_rich_comparison_methods(self, tester):
        """Test rich comparison methods"""
        # Language Reference: __eq__, __ne__, __lt__, __le__, __gt__, __ge__
        comparison_methods = [
            """class Comparable:
    def __eq__(self, other):
        return self.value == other.value""",
            
            """class Comparable:
    def __ne__(self, other):
        return not self.__eq__(other)""",
            
            """class Comparable:
    def __lt__(self, other):
        return self.value < other.value""",
            
            """class Comparable:
    def __le__(self, other):
        return self.value <= other.value""",
            
            """class Comparable:
    def __gt__(self, other):
        return self.value > other.value""",
            
            """class Comparable:
    def __ge__(self, other):
        return self.value >= other.value"""
        ]
        
        for source in comparison_methods:
            tree = tester.assert_method_syntax_parses(source)
            methods = tester.get_class_methods(source)
            expected = ['__eq__', '__ne__', '__lt__', '__le__', '__gt__', '__ge__']
            assert any(method in expected for method in methods)

    def test_complete_comparison_implementation(self, tester):
        """Test complete comparison method implementation"""
        # Complete comparison class
        complete_comparison = """class FullComparable:
    def __init__(self, value):
        self.value = value
        
    def __eq__(self, other):
        return isinstance(other, FullComparable) and self.value == other.value
        
    def __ne__(self, other):
        return not self.__eq__(other)
        
    def __lt__(self, other):
        if not isinstance(other, FullComparable):
            return NotImplemented
        return self.value < other.value
        
    def __le__(self, other):
        return self.__lt__(other) or self.__eq__(other)
        
    def __gt__(self, other):
        if not isinstance(other, FullComparable):
            return NotImplemented
        return self.value > other.value
        
    def __ge__(self, other):
        return self.__gt__(other) or self.__eq__(other)"""
        
        tree = tester.assert_method_syntax_parses(complete_comparison)
        methods = tester.get_class_methods(complete_comparison)
        expected = ['__init__', '__eq__', '__ne__', '__lt__', '__le__', '__gt__', '__ge__']
        assert all(method in methods for method in expected)


class TestSection33ContainerMethods:
    """Test container operation special methods"""
    
    @pytest.fixture
    def tester(self):
        return SpecialMethodTester()

    def test_container_access_methods(self, tester):
        """Test container access methods"""
        # Language Reference: __len__, __getitem__, __setitem__, __delitem__
        container_methods = [
            """class Container:
    def __len__(self):
        return len(self.data)""",
            
            """class Container:
    def __getitem__(self, key):
        return self.data[key]""",
            
            """class Container:
    def __setitem__(self, key, value):
        self.data[key] = value""",
            
            """class Container:
    def __delitem__(self, key):
        del self.data[key]"""
        ]
        
        for source in container_methods:
            tree = tester.assert_method_syntax_parses(source)
            methods = tester.get_class_methods(source)
            expected = ['__len__', '__getitem__', '__setitem__', '__delitem__']
            assert any(method in expected for method in methods)

    def test_container_membership_methods(self, tester):
        """Test container membership methods"""
        # Language Reference: __contains__, __missing__
        membership_methods = [
            """class Container:
    def __contains__(self, item):
        return item in self.data""",
            
            """class Container:
    def __missing__(self, key):
        return self.default_value"""
        ]
        
        for source in membership_methods:
            tree = tester.assert_method_syntax_parses(source)
            methods = tester.get_class_methods(source)
            expected = ['__contains__', '__missing__']
            assert any(method in expected for method in methods)

    def test_iterator_methods(self, tester):
        """Test iterator protocol methods"""
        # Language Reference: __iter__, __next__
        iterator_methods = [
            """class Iterator:
    def __iter__(self):
        return self""",
            
            """class Iterator:
    def __next__(self):
        if self.index >= len(self.data):
            raise StopIteration
        value = self.data[self.index]
        self.index += 1
        return value""",
            
            """class Iterable:
    def __iter__(self):
        return iter(self.data)"""
        ]
        
        for source in iterator_methods:
            tree = tester.assert_method_syntax_parses(source)
            methods = tester.get_class_methods(source)
            expected = ['__iter__', '__next__']
            assert any(method in expected for method in methods)

    def test_complete_container_implementation(self, tester):
        """Test complete container implementation"""
        # Full container class
        complete_container = """class FullContainer:
    def __init__(self):
        self.data = []
        
    def __len__(self):
        return len(self.data)
        
    def __getitem__(self, index):
        return self.data[index]
        
    def __setitem__(self, index, value):
        self.data[index] = value
        
    def __delitem__(self, index):
        del self.data[index]
        
    def __contains__(self, item):
        return item in self.data
        
    def __iter__(self):
        return iter(self.data)"""
        
        tree = tester.assert_method_syntax_parses(complete_container)
        methods = tester.get_class_methods(complete_container)
        expected = ['__init__', '__len__', '__getitem__', '__setitem__', 
                   '__delitem__', '__contains__', '__iter__']
        assert all(method in methods for method in expected)


class TestSection33AttributeMethods:
    """Test attribute access special methods"""
    
    @pytest.fixture
    def tester(self):
        return SpecialMethodTester()

    def test_attribute_access_methods(self, tester):
        """Test attribute access methods"""
        # Language Reference: __getattr__, __setattr__, __delattr__, __getattribute__
        attribute_methods = [
            """class AttributeHandler:
    def __getattr__(self, name):
        return f'default value for {name}'""",
            
            """class AttributeHandler:
    def __setattr__(self, name, value):
        super().__setattr__(name, value)""",
            
            """class AttributeHandler:
    def __delattr__(self, name):
        super().__delattr__(name)""",
            
            """class AttributeHandler:
    def __getattribute__(self, name):
        return super().__getattribute__(name)"""
        ]
        
        for source in attribute_methods:
            tree = tester.assert_method_syntax_parses(source)
            methods = tester.get_class_methods(source)
            expected = ['__getattr__', '__setattr__', '__delattr__', '__getattribute__']
            assert any(method in expected for method in methods)

    def test_descriptor_methods(self, tester):
        """Test descriptor protocol methods"""
        # Language Reference: __get__, __set__, __delete__, __set_name__
        descriptor_methods = [
            """class Descriptor:
    def __get__(self, instance, owner):
        return self.value""",
            
            """class Descriptor:
    def __set__(self, instance, value):
        self.value = value""",
            
            """class Descriptor:
    def __delete__(self, instance):
        del self.value""",
            
            """class Descriptor:
    def __set_name__(self, owner, name):
        self.name = name"""
        ]
        
        for source in descriptor_methods:
            tree = tester.assert_method_syntax_parses(source)
            methods = tester.get_class_methods(source)
            expected = ['__get__', '__set__', '__delete__', '__set_name__']
            assert any(method in expected for method in methods)

    def test_attribute_dir_method(self, tester):
        """Test directory listing method"""
        # Language Reference: __dir__ method
        dir_method = """class CustomDir:
    def __dir__(self):
        return ['custom_attr1', 'custom_attr2']"""
        
        tree = tester.assert_method_syntax_parses(dir_method)
        methods = tester.get_class_methods(dir_method)
        assert '__dir__' in methods


class TestSection33CallableMethods:
    """Test callable object special methods"""
    
    @pytest.fixture
    def tester(self):
        return SpecialMethodTester()

    def test_callable_method(self, tester):
        """Test callable object method"""
        # Language Reference: __call__ method
        callable_methods = [
            """class Callable:
    def __call__(self):
        return 'called with no args'""",
            
            """class Callable:
    def __call__(self, *args, **kwargs):
        return f'called with {args} and {kwargs}'""",
            
            """class FunctionLike:
    def __call__(self, x, y=None):
        if y is None:
            return x * 2
        return x + y"""
        ]
        
        for source in callable_methods:
            tree = tester.assert_method_syntax_parses(source)
            methods = tester.get_class_methods(source)
            assert '__call__' in methods


class TestSection33ContextManagerMethods:
    """Test context manager special methods"""
    
    @pytest.fixture
    def tester(self):
        return SpecialMethodTester()

    def test_context_manager_methods(self, tester):
        """Test context manager protocol methods"""
        # Language Reference: __enter__, __exit__ methods
        context_manager_methods = [
            """class ContextManager:
    def __enter__(self):
        return self""",
            
            """class ContextManager:
    def __exit__(self, exc_type, exc_value, traceback):
        return False""",
            
            """class ResourceManager:
    def __enter__(self):
        self.acquire_resource()
        return self.resource
        
    def __exit__(self, exc_type, exc_value, traceback):
        self.release_resource()
        return exc_type is None"""
        ]
        
        for source in context_manager_methods:
            tree = tester.assert_method_syntax_parses(source)
            methods = tester.get_class_methods(source)
            expected = ['__enter__', '__exit__']
            assert any(method in expected for method in methods)


class TestSection33CopyMethods:
    """Test copy and deepcopy special methods"""
    
    @pytest.fixture
    def tester(self):
        return SpecialMethodTester()

    def test_copy_methods(self, tester):
        """Test copy protocol methods"""
        # Language Reference: __copy__, __deepcopy__ methods
        copy_methods = [
            """class Copyable:
    def __copy__(self):
        return Copyable(self.value)""",
            
            """class Copyable:
    def __deepcopy__(self, memo):
        import copy
        return Copyable(copy.deepcopy(self.value, memo))"""
        ]
        
        for source in copy_methods:
            tree = tester.assert_method_syntax_parses(source)
            methods = tester.get_class_methods(source)
            expected = ['__copy__', '__deepcopy__']
            assert any(method in expected for method in methods)


class TestSection33PickleMethods:
    """Test pickle/unpickle special methods"""
    
    @pytest.fixture
    def tester(self):
        return SpecialMethodTester()

    def test_pickle_methods(self, tester):
        """Test pickle protocol methods"""
        # Language Reference: __getstate__, __setstate__, __getnewargs__, __reduce__
        pickle_methods = [
            """class Pickleable:
    def __getstate__(self):
        return self.__dict__.copy()""",
            
            """class Pickleable:
    def __setstate__(self, state):
        self.__dict__.update(state)""",
            
            """class Pickleable:
    def __getnewargs__(self):
        return (self.arg1, self.arg2)""",
            
            """class Pickleable:
    def __reduce__(self):
        return (self.__class__, (self.value,))""",
            
            """class Pickleable:
    def __reduce_ex__(self, protocol):
        return self.__reduce__()"""
        ]
        
        for source in pickle_methods:
            tree = tester.assert_method_syntax_parses(source)
            methods = tester.get_class_methods(source)
            expected = ['__getstate__', '__setstate__', '__getnewargs__', '__reduce__', '__reduce_ex__']
            assert any(method in expected for method in methods)


class TestSection33ErrorConditions:
    """Test error conditions for special methods"""
    
    @pytest.fixture
    def tester(self):
        return SpecialMethodTester()

    def test_invalid_special_method_names(self, tester):
        """Test that invalid special method names parse but are not special"""
        # These parse as regular methods, not special methods
        invalid_special = [
            """class Test:
    def _single_underscore(self):
        pass""",
            
            """class Test:
    def __partial_special(self):
        pass""",
            
            """class Test:
    def not_special__(self):
        pass""",
            
            """class Test:
    def ___triple_underscore___(self):
        pass"""
        ]
        
        for source in invalid_special:
            tree = tester.assert_method_syntax_parses(source)
            # These should parse successfully as regular methods

    def test_special_method_signature_variations(self, tester):
        """Test various special method signatures"""
        # Different signature patterns
        signature_variations = [
            """class Test:
    def __init__(self, *args, **kwargs):
        pass""",
            
            """class Test:
    def __getitem__(self, key):
        pass""",
            
            """class Test:
    def __setitem__(self, key, value):
        pass""",
            
            """class Test:
    def __call__(self, *args, **kwargs):
        pass""",
            
            """class Test:
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        return False"""
        ]
        
        for source in signature_variations:
            tree = tester.assert_method_syntax_parses(source)
            # Should all parse correctly


class TestSection33CrossImplementationCompatibility:
    """Test special method features across Python implementations"""
    
    @pytest.fixture
    def tester(self):
        return SpecialMethodTester()

    def test_comprehensive_special_methods_class(self, tester):
        """Test class with many special methods"""
        # Comprehensive class with multiple special methods
        comprehensive_class = """class ComprehensiveClass:
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return f'ComprehensiveClass({self.value})'
        
    def __repr__(self):
        return f'ComprehensiveClass({self.value!r})'
        
    def __eq__(self, other):
        return isinstance(other, ComprehensiveClass) and self.value == other.value
        
    def __hash__(self):
        return hash(self.value)
        
    def __add__(self, other):
        if isinstance(other, ComprehensiveClass):
            return ComprehensiveClass(self.value + other.value)
        return ComprehensiveClass(self.value + other)
        
    def __len__(self):
        return len(str(self.value))
        
    def __getitem__(self, index):
        return str(self.value)[index]
        
    def __call__(self, *args):
        return f'{self.value} called with {args}'
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        return False
        
    def __iter__(self):
        return iter(str(self.value))"""
        
        tree = tester.assert_method_syntax_parses(comprehensive_class)
        methods = tester.get_class_methods(comprehensive_class)
        expected = ['__init__', '__str__', '__repr__', '__eq__', '__hash__', 
                   '__add__', '__len__', '__getitem__', '__call__', 
                   '__enter__', '__exit__', '__iter__']
        assert all(method in methods for method in expected)

    def test_special_method_inheritance(self, tester):
        """Test special method inheritance patterns"""
        # Inheritance with special methods
        inheritance_patterns = [
            """class Base:
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return f'Base({self.value})'

class Derived(Base):
    def __init__(self, value, extra):
        super().__init__(value)
        self.extra = extra
        
    def __str__(self):
        return f'Derived({self.value}, {self.extra})'""",
            
            """class Mixin:
    def __eq__(self, other):
        return hasattr(other, 'value') and self.value == other.value

class MyClass(Mixin):
    def __init__(self, value):
        self.value = value"""
        ]
        
        for source in inheritance_patterns:
            tree = tester.assert_method_syntax_parses(source)
            # Should parse successfully

    def test_special_method_with_decorators(self, tester):
        """Test special methods with decorators"""
        # Decorated special methods
        decorated_methods = [
            """class Test:
    @property
    def __len__(self):
        return len(self.data)""",
            
            """class Test:
    @classmethod
    def __new__(cls, *args):
        return super().__new__(cls)""",
            
            """class Test:
    @staticmethod
    def __format__(value, format_spec):
        return format(value, format_spec)"""
        ]
        
        for source in decorated_methods:
            tree = tester.assert_method_syntax_parses(source)
            # Should parse successfully

    def test_multiple_special_method_definitions(self, tester):
        """Test multiple definitions of same special method"""
        # Multiple method definitions (last one wins)
        multiple_definitions = """class Test:
    def __str__(self):
        return 'first definition'
        
    def __str__(self):
        return 'second definition'"""
        
        tree = tester.assert_method_syntax_parses(multiple_definitions)
        methods = tester.get_class_methods(multiple_definitions)
        # Should have __str__ method (last definition wins)
        assert '__str__' in methods

    def test_special_method_ast_structure(self, tester):
        """Test special method AST structure validation"""
        # Validate AST structure for special methods
        source = """class TestClass:
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return str(self.value)"""
        
        tree = tester.assert_method_syntax_parses(source)
        
        # Find the class definition
        class_def = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_def = node
                break
        
        assert class_def is not None
        assert class_def.name == 'TestClass'
        
        # Check method definitions
        methods = {}
        for item in class_def.body:
            if isinstance(item, ast.FunctionDef):
                methods[item.name] = item
        
        assert '__init__' in methods
        assert '__str__' in methods
        
        # Check __init__ method structure
        init_method = methods['__init__']
        assert len(init_method.args.args) == 2  # self + value
        assert init_method.args.args[0].arg == 'self'
        assert init_method.args.args[1].arg == 'value'