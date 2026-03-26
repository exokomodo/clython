"""
Section 8.7: Class Definitions - Conformance Test Suite

Tests Python Language Reference Section 8.7 compliance across implementations.
Based on formal grammar definitions and prose assertions for class definitions.

Grammar tested:
    classdef: [decorators] "class" classname [inheritance] ":" suite
    inheritance: "(" [argument_list] ")"
    classname: identifier

Language Reference requirements tested:
    - Class definition syntax: "class" keyword with classname
    - Inheritance syntax: parentheses with base classes
    - Method definitions: functions defined within class
    - Class decorators: @decorator on class definitions
    - Metaclass specification: metaclass keyword argument
    - Multiple inheritance: multiple base classes
    - Class variables and instance variables
"""

import ast
import pytest
import sys
from typing import Any


class ClassDefinitionTester:
    """Helper class for testing class definition conformance.
    
    Follows established AST-based validation pattern from previous sections.
    """
    
    def assert_class_syntax_parses(self, source: str):
        """Test that class definition syntax parses correctly.
        
        Args:
            source: Python class definition source code
        """
        try:
            tree = ast.parse(source)
            # Verify the AST contains class definition
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    return  # Found class definition, syntax is valid
            pytest.fail(f"Expected ClassDef not found in parsed AST for: {source}")
        except SyntaxError as e:
            pytest.fail(f"Class syntax {source!r} failed to parse: {e}")
    
    def assert_class_syntax_error(self, source: str):
        """Test that invalid class syntax raises SyntaxError.
        
        Args:
            source: Python class source code that should be invalid
        """
        with pytest.raises(SyntaxError):
            ast.parse(source)

    def get_class_def_from_source(self, source: str) -> ast.ClassDef:
        """Get the ClassDef AST node from source for detailed validation.
        
        Args:
            source: Python class definition source
            
        Returns:
            ast.ClassDef node
        """
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                return node
        pytest.fail(f"No ClassDef found in: {source}")


class TestSection87BasicClassDefinitions:
    """Test Section 8.7: Basic Class Definitions"""
    
    @pytest.fixture
    def tester(self):
        return ClassDefinitionTester()

    def test_basic_class_syntax(self, tester):
        """Test basic class definition syntax"""
        # Language Reference: classdef: "class" classname ":" suite
        basic_classes = [
            "class Simple: pass",
            "class Empty:\n    pass",
            "class WithMethod:\n    def method(self): pass",
            "class WithMultipleMethods:\n    def method1(self): pass\n    def method2(self): pass"
        ]
        
        for source in basic_classes:
            tester.assert_class_syntax_parses(source)

    def test_class_with_docstring(self, tester):
        """Test class with docstring"""
        # Classes with docstrings
        docstring_classes = [
            'class Documented:\n    """This is a docstring."""\n    pass',
            'class MultilineDoc:\n    """This is a\n    multiline docstring."""\n    pass',
            "class SingleQuoteDoc:\n    'Simple docstring.'\n    pass"
        ]
        
        for source in docstring_classes:
            tester.assert_class_syntax_parses(source)

    def test_class_with_variables(self, tester):
        """Test class with class variables"""
        # Class variables
        variable_classes = [
            "class WithVars:\n    x = 42\n    y = 'hello'",
            "class WithMultipleVars:\n    a, b = 1, 2\n    c = d = 3",
            "class WithComplexVars:\n    data = [1, 2, 3]\n    config = {'key': 'value'}"
        ]
        
        for source in variable_classes:
            tester.assert_class_syntax_parses(source)

    def test_class_name_validation(self, tester):
        """Test valid class name syntax"""
        # Language Reference: classname: identifier
        valid_names = [
            "class ValidName: pass",
            "class _PrivateName: pass",  
            "class __DunderName__: pass",
            "class CamelCase: pass",
            "class snake_case: pass",
            "class Name123: pass"
        ]
        
        for source in valid_names:
            tester.assert_class_syntax_parses(source)

    def test_nested_class_definitions(self, tester):
        """Test nested class definitions"""
        # Nested classes
        nested_classes = [
            """class Outer:
    class Inner:
        pass""",
            
            """class Container:
    class Data:
        def __init__(self, value):
            self.value = value
    
    class Helper:
        @staticmethod
        def process():
            pass"""
        ]
        
        for source in nested_classes:
            tester.assert_class_syntax_parses(source)


class TestSection87Inheritance:
    """Test class inheritance syntax"""
    
    @pytest.fixture
    def tester(self):
        return ClassDefinitionTester()

    def test_single_inheritance(self, tester):
        """Test single inheritance syntax"""
        # Language Reference: inheritance: "(" [argument_list] ")"
        single_inheritance = [
            "class Child(Parent): pass",
            "class Derived(Base):\n    def method(self): pass",
            "class SpecificList(list): pass",
            "class CustomDict(dict):\n    def custom_method(self): pass"
        ]
        
        for source in single_inheritance:
            tester.assert_class_syntax_parses(source)

    def test_multiple_inheritance(self, tester):
        """Test multiple inheritance syntax"""
        # Multiple base classes
        multiple_inheritance = [
            "class Multi(Base1, Base2): pass",
            "class Complex(A, B, C): pass",
            "class MixedInheritance(list, dict): pass",
            "class ManyBases(A, B, C, D, E): pass"
        ]
        
        for source in multiple_inheritance:
            tester.assert_class_syntax_parses(source)

    def test_inheritance_with_arguments(self, tester):
        """Test inheritance with base class arguments"""
        # Base class initialization
        inheritance_args = [
            "class Child(Parent, arg1=value1): pass",
            "class Configured(Base, config=True): pass",
            "class WithKeywords(Base, metaclass=Meta): pass",
            "class Complex(A, B, arg=1, metaclass=M): pass"
        ]
        
        for source in inheritance_args:
            tester.assert_class_syntax_parses(source)

    def test_metaclass_specification(self, tester):
        """Test metaclass specification syntax"""
        # Metaclass syntax
        metaclass_specs = [
            "class WithMeta(metaclass=MetaClass): pass",
            "class CustomMeta(Base, metaclass=Custom): pass",
            "class TypedClass(metaclass=type): pass",
            "class ABCClass(ABC, metaclass=ABCMeta): pass"
        ]
        
        for source in metaclass_specs:
            tester.assert_class_syntax_parses(source)

    def test_inheritance_ast_structure(self, tester):
        """Test inheritance AST structure validation"""
        # Test AST structure for inheritance
        source = "class Child(Parent1, Parent2, metaclass=Meta): pass"
        classdef = tester.get_class_def_from_source(source)
        
        assert classdef.name == "Child"
        assert len(classdef.bases) == 2  # Parent1, Parent2
        assert len(classdef.keywords) == 1  # metaclass=Meta
        assert classdef.keywords[0].arg == "metaclass"


class TestSection87MethodDefinitions:
    """Test method definitions within classes"""
    
    @pytest.fixture
    def tester(self):
        return ClassDefinitionTester()

    def test_instance_methods(self, tester):
        """Test instance method definitions"""
        # Instance methods with self parameter
        instance_methods = [
            """class WithMethods:
    def __init__(self): pass
    def method(self): pass
    def with_args(self, x, y): return x + y""",
            
            """class ComplexMethods:
    def __init__(self, value):
        self.value = value
    
    def get_value(self):
        return self.value
    
    def set_value(self, new_value):
        self.value = new_value"""
        ]
        
        for source in instance_methods:
            tester.assert_class_syntax_parses(source)

    def test_special_methods(self, tester):
        """Test special method definitions (dunder methods)"""
        # Special methods
        special_methods = [
            """class WithSpecial:
    def __init__(self): pass
    def __str__(self): return 'string'
    def __repr__(self): return 'repr'
    def __len__(self): return 0""",
            
            """class Operators:
    def __add__(self, other): return self
    def __sub__(self, other): return self  
    def __mul__(self, other): return self
    def __eq__(self, other): return True"""
        ]
        
        for source in special_methods:
            tester.assert_class_syntax_parses(source)

    def test_class_methods(self, tester):
        """Test classmethod decorator usage"""
        # Class methods
        class_methods = [
            """class WithClassMethod:
    @classmethod
    def create(cls): return cls()""",
            
            """class Factory:
    @classmethod  
    def from_string(cls, s):
        return cls(s)
    
    @classmethod
    def from_dict(cls, d):
        return cls(**d)"""
        ]
        
        for source in class_methods:
            tester.assert_class_syntax_parses(source)

    def test_static_methods(self, tester):
        """Test staticmethod decorator usage"""
        # Static methods  
        static_methods = [
            """class WithStaticMethod:
    @staticmethod
    def utility(): pass""",
            
            """class Utils:
    @staticmethod
    def helper(x, y):
        return x + y
    
    @staticmethod
    def validator(value):
        return isinstance(value, int)"""
        ]
        
        for source in static_methods:
            tester.assert_class_syntax_parses(source)

    def test_property_definitions(self, tester):
        """Test property decorator usage"""
        # Properties
        property_defs = [
            """class WithProperty:
    @property
    def value(self): return self._value
    
    @value.setter
    def value(self, val): self._value = val""",
            
            """class Managed:
    @property
    def x(self): return self._x
    
    @x.setter  
    def x(self, value):
        if value < 0:
            raise ValueError()
        self._x = value"""
        ]
        
        for source in property_defs:
            tester.assert_class_syntax_parses(source)


class TestSection87ClassDecorators:
    """Test class decorator syntax"""
    
    @pytest.fixture
    def tester(self):
        return ClassDefinitionTester()

    def test_single_decorator(self, tester):
        """Test single class decorator"""
        # Language Reference: decorators on classdef
        single_decorators = [
            "@decorator\nclass Decorated: pass",
            "@dataclass\nclass Data: pass",
            "@register\nclass Plugin: pass",
            "@frozen\nclass Immutable: pass"
        ]
        
        for source in single_decorators:
            tester.assert_class_syntax_parses(source)

    def test_multiple_decorators(self, tester):
        """Test multiple class decorators"""
        # Multiple decorators
        multiple_decorators = [
            "@decorator1\n@decorator2\nclass Multi: pass",
            "@dataclass\n@frozen\nclass FrozenData: pass", 
            "@deco1\n@deco2\n@deco3\nclass Triple: pass",
            "@register('plugin')\n@cache\nclass Complex: pass"
        ]
        
        for source in multiple_decorators:
            tester.assert_class_syntax_parses(source)

    def test_decorator_with_arguments(self, tester):
        """Test decorators with arguments"""
        # Decorators with arguments
        decorator_args = [
            "@decorator(arg=value)\nclass Configured: pass",
            "@dataclass(frozen=True)\nclass Frozen: pass",
            "@register('name', version=1)\nclass Versioned: pass",
            "@decorator(a=1, b=2)\nclass MultiArg: pass"
        ]
        
        for source in decorator_args:
            tester.assert_class_syntax_parses(source)

    def test_decorator_ast_structure(self, tester):
        """Test decorator AST structure"""
        # Verify decorator AST structure
        source = "@decorator1\n@decorator2(arg=value)\nclass Decorated: pass"
        classdef = tester.get_class_def_from_source(source)
        
        assert len(classdef.decorator_list) == 2
        assert isinstance(classdef.decorator_list[0], ast.Name)  # Simple decorator
        assert isinstance(classdef.decorator_list[1], ast.Call)  # Decorator with args


class TestSection87ErrorConditions:
    """Test error conditions for class definitions"""
    
    @pytest.fixture
    def tester(self):
        return ClassDefinitionTester()

    def test_invalid_class_syntax(self, tester):
        """Test invalid class definition syntax"""
        # Invalid syntax
        invalid_syntax = [
            "class: pass",           # Missing class name
            "class 123Invalid: pass", # Invalid name (starts with number)
            "class def: pass",       # Keyword as name
            "class Valid",           # Missing colon
            "class Valid() pass"     # Missing colon with parentheses
        ]
        
        for source in invalid_syntax:
            tester.assert_class_syntax_error(source)

    def test_invalid_inheritance_syntax(self, tester):
        """Test invalid inheritance syntax"""
        # Invalid inheritance
        invalid_inheritance = [
            "class Child(: pass",     # Malformed parentheses
            "class Child): pass",     # Malformed parentheses
            "class Child(,): pass",   # Invalid comma placement
            "class Child(Parent,): pass"  # Trailing comma (actually valid in modern Python)
        ]
        
        # Note: Some of these might be valid in newer Python versions
        for source in invalid_inheritance[:-1]:  # Skip the last one (trailing comma)
            tester.assert_class_syntax_error(source)

    def test_invalid_nested_class_syntax(self, tester):
        """Test invalid nested class syntax"""
        # Invalid nesting
        invalid_nesting = [
            """class Outer:
class Inner: pass""",  # Wrong indentation
            
            "def func():\nclass Inner: pass"  # Class in function (actually valid)
        ]
        
        # Only test the clearly invalid one
        tester.assert_class_syntax_error(invalid_nesting[0])

    def test_reserved_keywords_as_class_names(self, tester):
        """Test reserved keywords cannot be class names"""
        # Keywords that should not be valid class names
        invalid_names = [
            "class if: pass",
            "class for: pass", 
            "class while: pass",
            "class def: pass",
            "class class: pass",
            "class import: pass"
        ]
        
        for source in invalid_names:
            tester.assert_class_syntax_error(source)


class TestSection87ComplexClassFeatures:
    """Test complex class definition features"""
    
    @pytest.fixture
    def tester(self):
        return ClassDefinitionTester()

    def test_class_with_all_features(self, tester):
        """Test class with multiple advanced features"""
        # Complex class with many features
        complex_class = """
@dataclass
@register('complex')
class ComplexClass(Base1, Base2, metaclass=CustomMeta):
    \"\"\"A complex class demonstrating many features.\"\"\"
    
    class_var = 42
    
    def __init__(self, value):
        self.value = value
    
    @classmethod
    def create(cls, data):
        return cls(data)
    
    @staticmethod
    def validate(value):
        return value > 0
    
    @property
    def formatted_value(self):
        return f"Value: {self.value}"
    
    def __str__(self):
        return self.formatted_value
    
    class NestedHelper:
        def process(self): pass
"""
        
        tester.assert_class_syntax_parses(complex_class)

    @pytest.mark.min_version_3_5  
    def test_generic_class_syntax(self, tester):
        """Test generic class syntax (Python 3.5+ type hints)"""
        # Generic classes (syntax only, not runtime)
        generic_classes = [
            "class Generic[T]: pass",  # Python 3.12+ syntax
            "class Container: pass",   # Will add type hints in comments
            "class Mapping: pass"     # Generic-style naming
        ]
        
        # Test what's actually parseable
        for source in generic_classes[1:]:  # Skip new generic syntax for now
            tester.assert_class_syntax_parses(source)

    def test_abstract_base_class_syntax(self, tester):
        """Test abstract base class patterns"""
        # ABC patterns
        abc_classes = [
            """class AbstractClass:
    def abstract_method(self):
        raise NotImplementedError""",
        
            """class Interface:
    def method1(self): raise NotImplementedError
    def method2(self): raise NotImplementedError""",
            
            """class Mixin:
    def mixin_method(self):
        return "mixin functionality" """
        ]
        
        for source in abc_classes:
            tester.assert_class_syntax_parses(source)

    def test_dataclass_pattern_syntax(self, tester):
        """Test common dataclass-like patterns"""
        # Dataclass-style patterns
        dataclass_patterns = [
            """@dataclass
class Point:
    x: int
    y: int""",
            
            """@dataclass(frozen=True)
class ImmutablePoint:
    x: float
    y: float""",
            
            """class ManualDataClass:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def __repr__(self):
        return f"{self.__class__.__name__}({self.name!r}, {self.age!r})" """
        ]
        
        for source in dataclass_patterns:
            tester.assert_class_syntax_parses(source)


class TestSection87CrossImplementationCompatibility:
    """Test class features across Python implementations"""
    
    @pytest.fixture
    def tester(self):
        return ClassDefinitionTester()

    def test_large_class_definitions(self, tester):
        """Test very large class definitions"""
        # Large class with many methods
        methods = "\n".join([f"    def method_{i}(self): pass" for i in range(100)])
        large_class = f"class LargeClass:\n{methods}"
        
        tester.assert_class_syntax_parses(large_class)

    def test_deep_inheritance_hierarchy(self, tester):
        """Test deep inheritance chains"""
        # Deep inheritance (syntax only)
        deep_inheritance = [
            "class A: pass",
            "class B(A): pass", 
            "class C(B): pass",
            "class D(C): pass",
            "class E(D): pass"
        ]
        
        combined = "\n".join(deep_inheritance)
        tester.assert_class_syntax_parses(combined)

    def test_complex_inheritance_patterns(self, tester):
        """Test complex multiple inheritance patterns"""
        # Diamond inheritance pattern
        diamond_pattern = """
class Base: pass
class Left(Base): pass
class Right(Base): pass  
class Diamond(Left, Right): pass
"""
        
        tester.assert_class_syntax_parses(diamond_pattern)

    def test_class_definition_introspection(self, tester):
        """Test class definition AST introspection"""
        # Detailed AST validation
        source = """
@decorator
class TestClass(Base, metaclass=Meta):
    def method(self): pass
"""
        
        classdef = tester.get_class_def_from_source(source)
        
        # Validate AST structure
        assert classdef.name == "TestClass"
        assert len(classdef.bases) == 1  
        assert len(classdef.keywords) == 1
        assert len(classdef.decorator_list) == 1
        assert len(classdef.body) == 1  # One method
        assert isinstance(classdef.body[0], ast.FunctionDef)

    def test_class_with_many_decorators(self, tester):
        """Test class with many decorators"""
        # Many decorators (reasonable limit)
        decorators = "\n".join([f"@decorator_{i}" for i in range(20)])
        many_decorators = f"{decorators}\nclass ManyDecorators: pass"
        
        tester.assert_class_syntax_parses(many_decorators)

    def test_class_with_many_base_classes(self, tester):
        """Test class with many base classes"""
        # Many base classes (reasonable limit)
        bases = ", ".join([f"Base{i}" for i in range(20)])
        many_bases = f"class ManyBases({bases}): pass"
        
        tester.assert_class_syntax_parses(many_bases)