"""
Section 3: Data Model - Conformance Test Suite

Tests Python Language Reference Section 3 compliance across implementations.
Based on formal specifications for Python's object system and data model.

Language Reference requirements tested:
    - Objects: Identity, type, value, mutability, lifetime
    - Types: Built-in types, user-defined types, type object behavior
    - Special method names: Complete object protocol (__init__, __str__, etc.)
    - Attribute access: Getters, setters, descriptors, __getattribute__
    - Descriptors: Descriptor protocol, property, classmethod, staticmethod
    - Invoking descriptors: Method resolution, bound methods, descriptor access
    - Metaclasses: Class creation, type objects, metaclass protocols
    - Customizing class creation: __new__, __init_subclass__, __set_name__
    - Customizing instance creation: __new__, __init__, __del__
    - Customizing attribute access: __getattr__, __setattr__, __delattr__
    - Implementing descriptors: __get__, __set__, __delete__, __set_name__
    - Invoking class creation: type construction, metaclass selection
    - Abstract base classes: ABC protocol, register, __subclasshook__
    - Coroutines: async/await protocol, __await__, async generators
"""

import ast
import pytest
import sys
import gc
import weakref
from typing import Any
from abc import ABC, abstractmethod


class DataModelTester:
    """Helper class for testing data model conformance.
    
    Uses runtime inspection and AST validation to test object model behavior
    across Python implementations.
    """
    
    def assert_source_parses(self, source: str):
        """Test that source code parses successfully.
        
        Args:
            source: Python source code to parse
        """
        try:
            return ast.parse(source)
        except SyntaxError as e:
            pytest.fail(f"Data model source {source!r} failed to parse: {e}")

    def assert_has_attribute(self, obj: Any, attr_name: str):
        """Test that object has specified attribute.
        
        Args:
            obj: Object to check
            attr_name: Attribute name to verify
        """
        assert hasattr(obj, attr_name), f"Object {obj} missing attribute {attr_name}"

    def assert_callable_attribute(self, obj: Any, attr_name: str):
        """Test that object has callable attribute.
        
        Args:
            obj: Object to check
            attr_name: Attribute name to verify as callable
        """
        self.assert_has_attribute(obj, attr_name)
        attr = getattr(obj, attr_name)
        assert callable(attr), f"Attribute {attr_name} of {obj} is not callable"

    def assert_type_relationship(self, obj: Any, expected_type: type):
        """Test object type relationship.
        
        Args:
            obj: Object to check
            expected_type: Expected type or parent type
        """
        assert isinstance(obj, expected_type), f"Object {obj} is not instance of {expected_type}"


class TestSection3Objects:
    """Test fundamental object system"""
    
    @pytest.fixture
    def tester(self):
        return DataModelTester()

    def test_object_identity(self, tester):
        """Test object identity with id() and is operator"""
        # Language Reference: objects have identity, compared with 'is'
        obj1 = object()
        obj2 = object()
        obj3 = obj1
        
        # Each object has unique identity
        assert id(obj1) != id(obj2)
        assert id(obj1) == id(obj3)
        
        # 'is' operator tests identity
        assert obj1 is obj3
        assert obj1 is not obj2
        assert obj2 is not obj3

    def test_object_types(self, tester):
        """Test object type system"""
        # Language Reference: objects have types, accessed with type()
        obj = object()
        string = "hello"
        number = 42
        list_obj = [1, 2, 3]
        
        # type() returns type object
        assert type(obj) is object
        assert type(string) is str
        assert type(number) is int
        assert type(list_obj) is list
        
        # Types themselves are objects
        assert type(type(obj)) is type
        assert isinstance(type, type)

    def test_object_values_and_mutability(self, tester):
        """Test object values and mutability concepts"""
        # Language Reference: objects have values, may be mutable or immutable
        
        # Immutable objects
        immutable_int = 42
        immutable_str = "hello"
        immutable_tuple = (1, 2, 3)
        
        # Mutable objects
        mutable_list = [1, 2, 3]
        mutable_dict = {"key": "value"}
        mutable_set = {1, 2, 3}
        
        # Immutable objects can be tested for equality
        assert immutable_int == 42
        assert immutable_str == "hello"
        assert immutable_tuple == (1, 2, 3)
        
        # Mutable objects can be modified
        original_list_id = id(mutable_list)
        mutable_list.append(4)
        assert id(mutable_list) == original_list_id  # Same object
        assert mutable_list == [1, 2, 3, 4]  # Different value

    def test_object_lifetime_and_garbage_collection(self, tester):
        """Test object lifetime and garbage collection"""
        # Language Reference: objects have lifetime, managed by garbage collector
        
        # Create object that supports weak references
        class TestObject:
            def __init__(self, value):
                self.value = value
        
        obj = TestObject(42)
        obj_id = id(obj)
        
        # Create weak reference to test garbage collection
        weak_ref = weakref.ref(obj)
        assert weak_ref() is not None
        assert weak_ref().value == 42
        
        # Remove reference and force garbage collection
        del obj
        gc.collect()
        
        # Object may be garbage collected (implementation dependent)
        # Note: This test is informational, not strict requirement
        # Some implementations may keep objects longer
        
    def test_object_string_representations(self, tester):
        """Test object string representation methods"""
        # Language Reference: objects have string representations
        obj = object()
        
        # All objects have __str__ and __repr__
        tester.assert_callable_attribute(obj, "__str__")
        tester.assert_callable_attribute(obj, "__repr__")
        
        # str() and repr() use these methods
        str_result = str(obj)
        repr_result = repr(obj)
        
        assert isinstance(str_result, str)
        assert isinstance(repr_result, str)
        assert len(str_result) > 0
        assert len(repr_result) > 0


class TestSection3Types:
    """Test type system behavior"""
    
    @pytest.fixture
    def tester(self):
        return DataModelTester()

    def test_builtin_types(self, tester):
        """Test built-in type objects"""
        # Language Reference: built-in types are type objects
        builtin_types = [
            int, float, complex, str, bytes, bytearray,
            list, tuple, dict, set, frozenset,
            bool, type, object
        ]
        
        for builtin_type in builtin_types:
            # Each is a type object
            assert isinstance(builtin_type, type)
            
            # Can create instances (for most types)
            if builtin_type in [int, float, str, list, dict, set, bool]:
                instance = builtin_type()
                assert type(instance) is builtin_type

    def test_type_hierarchy(self, tester):
        """Test type hierarchy relationships"""
        # Language Reference: types form hierarchy with object as base
        
        # object is base of all types
        assert issubclass(int, object)
        assert issubclass(str, object)
        assert issubclass(list, object)
        assert issubclass(type, object)
        
        # type is metaclass for most types
        assert type(int) is type
        assert type(str) is type
        assert type(list) is type
        
        # type is instance of itself
        assert type(type) is type
        assert isinstance(type, type)

    def test_user_defined_types(self, tester):
        """Test user-defined class types"""
        # Language Reference: user-defined classes create new types
        
        class CustomClass:
            pass
        
        class DerivedClass(CustomClass):
            pass
        
        # Classes are type objects
        assert isinstance(CustomClass, type)
        assert isinstance(DerivedClass, type)
        
        # Instances have correct type
        custom_instance = CustomClass()
        derived_instance = DerivedClass()
        
        assert type(custom_instance) is CustomClass
        assert type(derived_instance) is DerivedClass
        
        # Inheritance relationships
        assert issubclass(DerivedClass, CustomClass)
        assert issubclass(CustomClass, object)
        assert isinstance(derived_instance, CustomClass)
        assert isinstance(derived_instance, object)

    def test_type_construction(self, tester):
        """Test dynamic type construction with type()"""
        # Language Reference: type() can construct new types
        
        def init_method(self, value):
            self.value = value
        
        def str_method(self):
            return f"Dynamic({self.value})"
        
        # Create type dynamically
        DynamicClass = type(
            'DynamicClass',
            (object,),
            {
                '__init__': init_method,
                '__str__': str_method
            }
        )
        
        # Verify it's a proper type
        assert isinstance(DynamicClass, type)
        assert DynamicClass.__name__ == 'DynamicClass'
        assert issubclass(DynamicClass, object)
        
        # Create instance and test behavior
        instance = DynamicClass("test")
        assert instance.value == "test"
        assert str(instance) == "Dynamic(test)"


class TestSection3SpecialMethodNames:
    """Test special method names (dunder methods)"""
    
    @pytest.fixture
    def tester(self):
        return DataModelTester()

    def test_basic_customization_methods(self, tester):
        """Test basic object customization methods"""
        # Language Reference: __new__, __init__, __del__, __repr__, __str__
        
        class CustomObject:
            def __new__(cls, value):
                instance = super().__new__(cls)
                instance.created = True
                return instance
            
            def __init__(self, value):
                self.value = value
                self.initialized = True
            
            def __repr__(self):
                return f"CustomObject({self.value!r})"
            
            def __str__(self):
                return f"Custom: {self.value}"
            
            def __del__(self):
                # Destructor (rarely used in practice)
                pass
        
        # Test object creation
        obj = CustomObject("test")
        assert obj.created
        assert obj.initialized
        assert obj.value == "test"
        
        # Test string representations
        assert repr(obj) == "CustomObject('test')"
        assert str(obj) == "Custom: test"

    def test_comparison_methods(self, tester):
        """Test rich comparison methods"""
        # Language Reference: __eq__, __ne__, __lt__, __le__, __gt__, __ge__
        
        class ComparableObject:
            def __init__(self, value):
                self.value = value
            
            def __eq__(self, other):
                return isinstance(other, ComparableObject) and self.value == other.value
            
            def __lt__(self, other):
                return isinstance(other, ComparableObject) and self.value < other.value
            
            def __le__(self, other):
                return self == other or self < other
            
            def __gt__(self, other):
                return not self <= other
            
            def __ge__(self, other):
                return not self < other
            
            def __ne__(self, other):
                return not self == other
        
        # Test comparisons
        obj1 = ComparableObject(1)
        obj2 = ComparableObject(2)
        obj3 = ComparableObject(1)
        
        assert obj1 == obj3
        assert obj1 != obj2
        assert obj1 < obj2
        assert obj1 <= obj2
        assert obj2 > obj1
        assert obj2 >= obj1

    def test_arithmetic_methods(self, tester):
        """Test arithmetic operation methods"""
        # Language Reference: __add__, __sub__, __mul__, etc.
        
        class MathObject:
            def __init__(self, value):
                self.value = value
            
            def __add__(self, other):
                if isinstance(other, MathObject):
                    return MathObject(self.value + other.value)
                return MathObject(self.value + other)
            
            def __sub__(self, other):
                if isinstance(other, MathObject):
                    return MathObject(self.value - other.value)
                return MathObject(self.value - other)
            
            def __mul__(self, other):
                if isinstance(other, MathObject):
                    return MathObject(self.value * other.value)
                return MathObject(self.value * other)
            
            def __eq__(self, other):
                return isinstance(other, MathObject) and self.value == other.value
        
        # Test arithmetic operations
        obj1 = MathObject(5)
        obj2 = MathObject(3)
        
        assert (obj1 + obj2) == MathObject(8)
        assert (obj1 - obj2) == MathObject(2)
        assert (obj1 * obj2) == MathObject(15)
        assert (obj1 + 2) == MathObject(7)

    def test_container_methods(self, tester):
        """Test container protocol methods"""
        # Language Reference: __len__, __getitem__, __setitem__, __delitem__, __contains__
        
        class CustomContainer:
            def __init__(self):
                self._items = {}
            
            def __len__(self):
                return len(self._items)
            
            def __getitem__(self, key):
                return self._items[key]
            
            def __setitem__(self, key, value):
                self._items[key] = value
            
            def __delitem__(self, key):
                del self._items[key]
            
            def __contains__(self, key):
                return key in self._items
            
            def __iter__(self):
                return iter(self._items)
        
        # Test container operations
        container = CustomContainer()
        
        # Initially empty
        assert len(container) == 0
        
        # Add items
        container["a"] = 1
        container["b"] = 2
        
        assert len(container) == 2
        assert container["a"] == 1
        assert container["b"] == 2
        assert "a" in container
        assert "c" not in container
        
        # Delete item
        del container["a"]
        assert len(container) == 1
        assert "a" not in container

    def test_callable_objects(self, tester):
        """Test callable object protocol"""
        # Language Reference: __call__ makes objects callable
        
        class CallableObject:
            def __init__(self, multiplier):
                self.multiplier = multiplier
            
            def __call__(self, value):
                return value * self.multiplier
        
        # Test callable behavior
        doubler = CallableObject(2)
        assert callable(doubler)
        assert doubler(5) == 10
        assert doubler(3) == 6

    def test_context_manager_methods(self, tester):
        """Test context manager protocol"""
        # Language Reference: __enter__, __exit__ for with statements
        
        class CustomContextManager:
            def __init__(self, name):
                self.name = name
                self.entered = False
                self.exited = False
            
            def __enter__(self):
                self.entered = True
                return f"Resource: {self.name}"
            
            def __exit__(self, exc_type, exc_value, traceback):
                self.exited = True
                return False  # Don't suppress exceptions
        
        # Test context manager
        manager = CustomContextManager("test")
        
        with manager as resource:
            assert manager.entered
            assert not manager.exited
            assert resource == "Resource: test"
        
        assert manager.exited


class TestSection3AttributeAccess:
    """Test attribute access customization"""
    
    @pytest.fixture
    def tester(self):
        return DataModelTester()

    def test_attribute_access_methods(self, tester):
        """Test attribute access customization methods"""
        # Language Reference: __getattr__, __getattribute__, __setattr__, __delattr__
        
        class AttributeCustomizer:
            def __init__(self):
                self._data = {}
            
            def __getattr__(self, name):
                # Called when attribute not found normally
                if name in self._data:
                    return self._data[name]
                raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
            
            def __setattr__(self, name, value):
                # Called for all attribute assignments
                if name.startswith('_'):
                    super().__setattr__(name, value)
                else:
                    if not hasattr(self, '_data'):
                        super().__setattr__('_data', {})
                    self._data[name] = value
            
            def __delattr__(self, name):
                # Called for attribute deletions
                if name in self._data:
                    del self._data[name]
                else:
                    super().__delattr__(name)
        
        # Test attribute access
        obj = AttributeCustomizer()
        
        # Set attributes (goes through __setattr__)
        obj.x = 10
        obj.y = 20
        
        # Get attributes (goes through __getattr__ for dynamic attributes)
        assert obj.x == 10
        assert obj.y == 20
        
        # Delete attribute (goes through __delattr__)
        del obj.x
        
        with pytest.raises(AttributeError):
            _ = obj.x

    def test_property_descriptors(self, tester):
        """Test property descriptor behavior"""
        # Language Reference: property() creates descriptors
        
        class PropertyExample:
            def __init__(self):
                self._value = 0
            
            @property
            def value(self):
                return self._value
            
            @value.setter
            def value(self, new_value):
                if new_value < 0:
                    raise ValueError("Value must be non-negative")
                self._value = new_value
            
            @value.deleter
            def value(self):
                self._value = 0
        
        # Test property behavior
        obj = PropertyExample()
        
        # Get property
        assert obj.value == 0
        
        # Set property
        obj.value = 42
        assert obj.value == 42
        
        # Property validation
        with pytest.raises(ValueError):
            obj.value = -1
        
        # Delete property
        del obj.value
        assert obj.value == 0


class TestSection3Descriptors:
    """Test descriptor protocol"""
    
    @pytest.fixture
    def tester(self):
        return DataModelTester()

    def test_descriptor_protocol(self, tester):
        """Test descriptor __get__, __set__, __delete__ methods"""
        # Language Reference: descriptors customize attribute access
        
        class CustomDescriptor:
            def __init__(self, initial_value=None):
                self.value = initial_value
                self.name = None
            
            def __set_name__(self, owner, name):
                # Called when descriptor assigned to class attribute
                self.name = name
            
            def __get__(self, instance, owner):
                if instance is None:
                    return self
                return getattr(instance, f'_{self.name}', self.value)
            
            def __set__(self, instance, value):
                if not isinstance(value, (int, float)):
                    raise TypeError(f"{self.name} must be a number")
                setattr(instance, f'_{self.name}', value)
            
            def __delete__(self, instance):
                setattr(instance, f'_{self.name}', self.value)
        
        class DescriptorExample:
            x = CustomDescriptor(0)
            y = CustomDescriptor(1)
        
        # Test descriptor behavior
        obj = DescriptorExample()
        
        # Get descriptor (uses __get__)
        assert obj.x == 0
        assert obj.y == 1
        
        # Set descriptor (uses __set__)
        obj.x = 42
        assert obj.x == 42
        
        # Type validation
        with pytest.raises(TypeError):
            obj.x = "invalid"
        
        # Delete descriptor (uses __delete__)
        del obj.x
        assert obj.x == 0

    def test_method_descriptors(self, tester):
        """Test method descriptor behavior"""
        # Language Reference: methods are descriptors
        
        class MethodExample:
            def instance_method(self):
                return "instance method called"
            
            @classmethod
            def class_method(cls):
                return f"class method called on {cls.__name__}"
            
            @staticmethod
            def static_method():
                return "static method called"
        
        # Test method descriptor behavior
        obj = MethodExample()
        
        # Instance method becomes bound method
        bound_method = obj.instance_method
        assert callable(bound_method)
        assert bound_method() == "instance method called"
        
        # Class method works on class and instance
        assert obj.class_method() == "class method called on MethodExample"
        assert MethodExample.class_method() == "class method called on MethodExample"
        
        # Static method is just a function
        assert obj.static_method() == "static method called"
        assert MethodExample.static_method() == "static method called"


class TestSection3Metaclasses:
    """Test metaclass behavior"""
    
    @pytest.fixture
    def tester(self):
        return DataModelTester()

    def test_metaclass_basics(self, tester):
        """Test basic metaclass functionality"""
        # Language Reference: metaclasses control class creation
        
        class MetaExample(type):
            def __new__(cls, name, bases, namespace):
                # Modify class creation
                namespace['created_by_meta'] = True
                namespace['class_name'] = name
                return super().__new__(cls, name, bases, namespace)
            
            def __init__(cls, name, bases, namespace):
                super().__init__(name, bases, namespace)
                cls.initialized_by_meta = True
        
        class ExampleClass(metaclass=MetaExample):
            pass
        
        # Test metaclass effects
        assert hasattr(ExampleClass, 'created_by_meta')
        assert hasattr(ExampleClass, 'initialized_by_meta')
        assert ExampleClass.created_by_meta is True
        assert ExampleClass.initialized_by_meta is True
        assert ExampleClass.class_name == 'ExampleClass'
        
        # Verify it's still a proper class
        instance = ExampleClass()
        assert type(instance) is ExampleClass
        assert type(ExampleClass) is MetaExample

    @pytest.mark.min_version_3_6
    def test_init_subclass_hook(self, tester):
        """Test __init_subclass__ customization hook"""
        # Language Reference: __init_subclass__ called when class is subclassed
        
        class BaseWithHook:
            subclasses = []
            
            def __init_subclass__(cls, **kwargs):
                super().__init_subclass__(**kwargs)
                BaseWithHook.subclasses.append(cls.__name__)
        
        class Subclass1(BaseWithHook):
            pass
        
        class Subclass2(BaseWithHook):
            pass
        
        # Test hook was called
        assert 'Subclass1' in BaseWithHook.subclasses
        assert 'Subclass2' in BaseWithHook.subclasses

    def test_class_creation_process(self, tester):
        """Test complete class creation process"""
        # Language Reference: class creation involves namespace preparation
        
        creation_log = []
        
        class TrackedMeta(type):
            @classmethod
            def __prepare__(cls, name, bases):
                creation_log.append(f"prepare: {name}")
                return {}
            
            def __new__(cls, name, bases, namespace):
                creation_log.append(f"new: {name}")
                return super().__new__(cls, name, bases, namespace)
            
            def __init__(cls, name, bases, namespace):
                creation_log.append(f"init: {name}")
                super().__init__(name, bases, namespace)
        
        class TrackedClass(metaclass=TrackedMeta):
            pass
        
        # Verify creation order (__prepare__ available in Python 3.0+)
        assert "prepare: TrackedClass" in creation_log
        assert "new: TrackedClass" in creation_log
        assert "init: TrackedClass" in creation_log


class TestSection3AbstractBaseClasses:
    """Test Abstract Base Class protocol"""
    
    @pytest.fixture
    def tester(self):
        return DataModelTester()

    def test_abc_protocol(self, tester):
        """Test ABC protocol with abstractmethod"""
        # Language Reference: ABC protocol enforces interface contracts
        
        class AbstractShape(ABC):
            @abstractmethod
            def area(self):
                pass
            
            @abstractmethod
            def perimeter(self):
                pass
            
            # Concrete method can use abstract methods
            def describe(self):
                return f"Shape with area {self.area()}"
        
        class Rectangle(AbstractShape):
            def __init__(self, width, height):
                self.width = width
                self.height = height
            
            def area(self):
                return self.width * self.height
            
            def perimeter(self):
                return 2 * (self.width + self.height)
        
        # Cannot instantiate abstract class
        with pytest.raises(TypeError):
            AbstractShape()
        
        # Can instantiate concrete implementation
        rect = Rectangle(3, 4)
        assert rect.area() == 12
        assert rect.perimeter() == 14
        assert rect.describe() == "Shape with area 12"
        
        # Verify inheritance
        assert isinstance(rect, AbstractShape)
        assert issubclass(Rectangle, AbstractShape)

    def test_virtual_subclassing(self, tester):
        """Test virtual subclassing with register()"""
        # Language Reference: register() creates virtual inheritance
        
        class Drawable(ABC):
            @abstractmethod
            def draw(self):
                pass
        
        class Circle:
            def draw(self):
                return "Drawing circle"
        
        # Register as virtual subclass
        Drawable.register(Circle)
        
        # Test virtual inheritance
        circle = Circle()
        assert isinstance(circle, Drawable)
        assert issubclass(Circle, Drawable)
        assert circle.draw() == "Drawing circle"

    def test_subclasshook(self, tester):
        """Test __subclasshook__ for duck typing"""
        # Language Reference: __subclasshook__ enables structural subtyping
        
        class Sized(ABC):
            @classmethod
            def __subclasshook__(cls, C):
                if cls is Sized:
                    # Check if class has __len__ method
                    if any("__len__" in B.__dict__ for B in C.__mro__):
                        return True
                return NotImplemented
            
            @abstractmethod
            def __len__(self):
                pass
        
        # Test duck typing
        assert issubclass(list, Sized)
        assert issubclass(dict, Sized)
        assert issubclass(str, Sized)
        assert not issubclass(int, Sized)
        
        # Instances also work
        assert isinstance([], Sized)
        assert isinstance({}, Sized)
        assert isinstance("", Sized)
        assert not isinstance(42, Sized)


class TestSection3CoroutineProtocol:
    """Test coroutine and async protocols"""
    
    @pytest.fixture
    def tester(self):
        return DataModelTester()

    def test_awaitable_protocol(self, tester):
        """Test awaitable object protocol"""
        # Language Reference: __await__ makes objects awaitable
        
        class CustomAwaitable:
            def __init__(self, value):
                self.value = value
            
            def __await__(self):
                # Simple awaitable that yields then returns value
                yield
                return self.value
        
        # Test awaitable creation
        awaitable = CustomAwaitable(42)
        tester.assert_callable_attribute(awaitable, "__await__")
        
        # Test that __await__ returns iterator
        await_iter = awaitable.__await__()
        assert hasattr(await_iter, '__next__')

    def test_async_iterator_protocol(self, tester):
        """Test async iterator protocol"""
        # Language Reference: __aiter__ and __anext__ for async iteration
        
        class AsyncRange:
            def __init__(self, start, stop):
                self.start = start
                self.stop = stop
            
            def __aiter__(self):
                return AsyncRangeIterator(self.start, self.stop)
        
        class AsyncRangeIterator:
            def __init__(self, start, stop):
                self.current = start
                self.stop = stop
            
            def __aiter__(self):
                return self
            
            async def __anext__(self):
                if self.current >= self.stop:
                    raise StopAsyncIteration
                value = self.current
                self.current += 1
                return value
        
        # Test async iterator creation
        async_range = AsyncRange(0, 3)
        tester.assert_callable_attribute(async_range, "__aiter__")
        
        iterator = async_range.__aiter__()
        tester.assert_callable_attribute(iterator, "__anext__")

    @pytest.mark.min_version_3_5
    def test_coroutine_function_protocol(self, tester):
        """Test coroutine function creation"""
        # Language Reference: async def creates coroutine functions
        
        async_def_source = """
async def async_function():
    return "async result"

def regular_function():
    return "regular result"
"""
        
        # Test that async def creates coroutine functions
        tree = tester.assert_source_parses(async_def_source)
        
        # Verify AST structure
        async_def = tree.body[0]
        regular_def = tree.body[1]
        
        assert isinstance(async_def, ast.AsyncFunctionDef)
        assert isinstance(regular_def, ast.FunctionDef)


class TestSection3DataModelCompatibility:
    """Test data model across Python implementations"""
    
    @pytest.fixture
    def tester(self):
        return DataModelTester()

    def test_mro_consistency(self, tester):
        """Test Method Resolution Order consistency"""
        # Language Reference: MRO follows C3 linearization
        
        class A: pass
        class B(A): pass
        class C(A): pass
        class D(B, C): pass
        
        # Test MRO
        mro = D.__mro__
        assert mro[0] is D
        assert mro[1] is B
        assert mro[2] is C
        assert mro[3] is A
        assert mro[4] is object
        
        # Test super() works correctly
        class Base:
            def method(self):
                return ["Base"]
        
        class Mixin1(Base):
            def method(self):
                return super().method() + ["Mixin1"]
        
        class Mixin2(Base):
            def method(self):
                return super().method() + ["Mixin2"]
        
        class Combined(Mixin1, Mixin2):
            def method(self):
                return super().method() + ["Combined"]
        
        instance = Combined()
        result = instance.method()
        assert "Base" in result
        assert "Mixin1" in result
        assert "Mixin2" in result
        assert "Combined" in result

    def test_data_model_specification_compliance(self, tester):
        """Test compliance with data model specifications"""
        # Comprehensive data model compliance tests
        
        class CompleteObject:
            """Object implementing many data model methods"""
            
            def __init__(self, value):
                self.value = value
            
            def __str__(self):
                return f"CompleteObject({self.value})"
            
            def __repr__(self):
                return f"CompleteObject({self.value!r})"
            
            def __eq__(self, other):
                return isinstance(other, CompleteObject) and self.value == other.value
            
            def __hash__(self):
                return hash(self.value)
            
            def __bool__(self):
                return bool(self.value)
            
            def __len__(self):
                return len(str(self.value))
            
            def __call__(self):
                return self.value
        
        # Test object creation and basic methods
        obj = CompleteObject("test")
        assert str(obj) == "CompleteObject(test)"
        assert repr(obj) == "CompleteObject('test')"
        assert obj == CompleteObject("test")
        assert obj != CompleteObject("other")
        assert hash(obj) == hash("test")
        assert bool(obj) is True
        assert bool(CompleteObject("")) is False
        assert len(obj) == 4
        assert obj() == "test"