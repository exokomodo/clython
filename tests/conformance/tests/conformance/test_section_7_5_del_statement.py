"""
Section 7.5: Del Statement - Conformance Test Suite

Tests Python Language Reference Section 7.5 compliance across implementations.
Based on formal del statement syntax definitions and prose assertions for deletion behavior.

Grammar tested:
    del_stmt: 'del' target_list

Language Reference requirements tested:
    - Del statement syntax validation
    - Name deletion and unbinding semantics
    - Attribute deletion behavior (__delattr__)
    - Subscript deletion behavior (__delitem__)
    - Slice deletion patterns and behavior
    - Del statement error conditions and restrictions
    - Multiple target deletion in single statement
    - Del statement AST structure validation
    - Cross-implementation del compatibility
"""

import ast
import pytest
import sys
from typing import Any


class DelTester:
    """Helper class for testing del statement conformance.
    
    Focuses on AST structure validation for del syntax and deletion
    patterns that can be statically analyzed for cross-implementation compatibility.
    """
    
    def assert_del_syntax_parses(self, source: str):
        """Test that del statement syntax parses correctly.
        
        Args:
            source: Python source code with del statements
        """
        try:
            tree = ast.parse(source)
            return tree
        except SyntaxError as e:
            pytest.fail(f"Del syntax should be valid but failed to parse: {source}\\nError: {e}")
    
    def assert_del_syntax_error(self, source: str):
        """Test that invalid del syntax raises SyntaxError.
        
        Args:
            source: Python source code that should be invalid
        """
        with pytest.raises(SyntaxError):
            ast.parse(source)
    
    def get_del_statements(self, source: str) -> list:
        """Get Delete AST nodes from source.
        
        Args:
            source: Python source code
            
        Returns:
            List of ast.Delete nodes
        """
        tree = ast.parse(source)
        dels = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Delete):
                dels.append(node)
        
        return dels
    
    def get_del_targets(self, source: str) -> list:
        """Get deletion target nodes from del statements.
        
        Args:
            source: Python source code
            
        Returns:
            List of target nodes from Delete statements
        """
        tree = ast.parse(source)
        targets = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Delete):
                targets.extend(node.targets)
        
        return targets
    
    def has_name_targets(self, source: str) -> bool:
        """Check if del statement has name targets.
        
        Args:
            source: Python source code
            
        Returns:
            True if del targets include Name nodes
        """
        targets = self.get_del_targets(source)
        return any(isinstance(target, ast.Name) for target in targets)
    
    def has_attribute_targets(self, source: str) -> bool:
        """Check if del statement has attribute targets.
        
        Args:
            source: Python source code
            
        Returns:
            True if del targets include Attribute nodes
        """
        targets = self.get_del_targets(source)
        return any(isinstance(target, ast.Attribute) for target in targets)
    
    def has_subscript_targets(self, source: str) -> bool:
        """Check if del statement has subscript targets.
        
        Args:
            source: Python source code
            
        Returns:
            True if del targets include Subscript nodes
        """
        targets = self.get_del_targets(source)
        return any(isinstance(target, ast.Subscript) for target in targets)


@pytest.fixture
def tester():
    """Provide DelTester instance for tests."""
    return DelTester()


class TestSection75BasicDelSyntax:
    """Test basic del statement syntax."""
    
    def test_simple_name_deletion(self, tester):
        """Test simple variable name deletion"""
        # Language Reference: del_stmt: 'del' target_list
        simple_name_del_patterns = [
            """
x = 42
del x
""",
            """
var1 = "hello"
var2 = "world"
del var1
del var2
""",
            """
a, b, c = 1, 2, 3
del a
del b
del c
""",
            """
result = compute_value()
del result
"""
        ]
        
        for source in simple_name_del_patterns:
            tree = tester.assert_del_syntax_parses(source)
            del_nodes = tester.get_del_statements(source)
            assert len(del_nodes) >= 1, f"Should have del statements: {source}"
            assert tester.has_name_targets(source), f"Should have name targets: {source}"
    
    def test_multiple_name_deletion(self, tester):
        """Test multiple variable deletion in single statement"""
        # Language Reference: del can target multiple names
        multiple_del_patterns = [
            """
a = 1
b = 2
c = 3
del a, b, c
""",
            """
x = y = z = 42
del x, y, z
""",
            """
var1, var2 = "hello", "world"
del var1, var2
""",
            """
items = [1, 2, 3, 4, 5]
start = 0
end = len(items)
del items, start, end
"""
        ]
        
        for source in multiple_del_patterns:
            tree = tester.assert_del_syntax_parses(source)
            del_nodes = tester.get_del_statements(source)
            assert len(del_nodes) >= 1, f"Should have del statements: {source}"
            
            targets = tester.get_del_targets(source)
            assert len(targets) >= 2, f"Should have multiple targets: {source}"
    
    def test_attribute_deletion(self, tester):
        """Test object attribute deletion"""
        # Language Reference: del can target object attributes
        attribute_del_patterns = [
            """
class MyClass:
    def __init__(self):
        self.attr = 42

obj = MyClass()
del obj.attr
""",
            """
import sys
del sys.path  # This would be problematic but syntactically valid
""",
            """
class Container:
    value = 100

del Container.value
""",
            """
obj = type('DynamicClass', (), {'x': 1, 'y': 2})
del obj.x
del obj.y
"""
        ]
        
        for source in attribute_del_patterns:
            tree = tester.assert_del_syntax_parses(source)
            del_nodes = tester.get_del_statements(source)
            assert len(del_nodes) >= 1, f"Should have del statements: {source}"
            assert tester.has_attribute_targets(source), f"Should have attribute targets: {source}"
    
    def test_subscript_deletion(self, tester):
        """Test subscript and slice deletion"""
        # Language Reference: del can target subscripts and slices
        subscript_del_patterns = [
            """
my_list = [1, 2, 3, 4, 5]
del my_list[0]
""",
            """
my_dict = {'a': 1, 'b': 2, 'c': 3}
del my_dict['a']
del my_dict['b']
""",
            """
data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
del data[2:5]
del data[::2]
""",
            """
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
del matrix[1][1]
del matrix[0]
"""
        ]
        
        for source in subscript_del_patterns:
            tree = tester.assert_del_syntax_parses(source)
            del_nodes = tester.get_del_statements(source)
            assert len(del_nodes) >= 1, f"Should have del statements: {source}"
            assert tester.has_subscript_targets(source), f"Should have subscript targets: {source}"


class TestSection75DelTargetTypes:
    """Test different types of del targets."""
    
    def test_complex_attribute_deletion(self, tester):
        """Test complex attribute deletion patterns"""
        # Language Reference: del can target complex attribute expressions
        complex_attribute_patterns = [
            """
obj.nested.deep.attribute = "value"
del obj.nested.deep.attribute
""",
            """
class Chain:
    def __init__(self):
        self.next = None

root = Chain()
root.next = Chain()
root.next.next = Chain()
del root.next.next
""",
            """
module.submodule.function.cache = {}
del module.submodule.function.cache
""",
            """
instance.method().result.value = 42
del instance.method().result.value
"""
        ]
        
        for source in complex_attribute_patterns:
            tree = tester.assert_del_syntax_parses(source)
            del_nodes = tester.get_del_statements(source)
            assert len(del_nodes) >= 1, f"Should have del statements: {source}"
            assert tester.has_attribute_targets(source), f"Should have attribute targets: {source}"
    
    def test_complex_subscript_deletion(self, tester):
        """Test complex subscript deletion patterns"""
        # Language Reference: del can target complex subscript expressions
        complex_subscript_patterns = [
            """
data = {'users': {'admin': {'permissions': ['read', 'write']}}}
del data['users']['admin']['permissions'][0]
""",
            """
matrix = [[[1, 2], [3, 4]], [[5, 6], [7, 8]]]
del matrix[0][1][0]
""",
            """
lookup = {get_key(): {get_subkey(): get_value()}}
del lookup[get_key()][get_subkey()]
""",
            """
arrays = [list(range(10)) for _ in range(5)]
del arrays[2][1:7:2]
"""
        ]
        
        for source in complex_subscript_patterns:
            tree = tester.assert_del_syntax_parses(source)
            del_nodes = tester.get_del_statements(source)
            assert len(del_nodes) >= 1, f"Should have del statements: {source}"
            assert tester.has_subscript_targets(source), f"Should have subscript targets: {source}"
    
    def test_slice_deletion_patterns(self, tester):
        """Test various slice deletion patterns"""
        # Language Reference: del supports slice notation
        slice_deletion_patterns = [
            """
items = list(range(20))
del items[:]  # Delete all items
""",
            """
data = list(range(100))
del data[10:90]  # Delete middle section
""",
            """
sequence = list(range(50))
del sequence[::2]  # Delete every other item
""",
            """
values = list(range(30))
del values[5:25:3]  # Delete with step
del values[-5:]  # Delete last 5
del values[:5]   # Delete first 5
"""
        ]
        
        for source in slice_deletion_patterns:
            tree = tester.assert_del_syntax_parses(source)
            del_nodes = tester.get_del_statements(source)
            assert len(del_nodes) >= 1, f"Should have del statements: {source}"
            assert tester.has_subscript_targets(source), f"Should have subscript targets: {source}"
    
    def test_mixed_target_deletion(self, tester):
        """Test deletion of mixed target types"""
        # Language Reference: del can target multiple different types simultaneously
        mixed_target_patterns = [
            """
var = 42
obj.attr = "value"
items = [1, 2, 3]
del var, obj.attr, items[0]
""",
            """
a = b = c = 100
data = {'key': 'value'}
matrix = [[1, 2], [3, 4]]
del a, data['key'], matrix[0][1], b
""",
            """
x, y, z = 1, 2, 3
config.setting = True
cache = [10, 20, 30, 40, 50]
del x, config.setting, cache[1:4], y, z
""",
        ]
        
        for source in mixed_target_patterns:
            tree = tester.assert_del_syntax_parses(source)
            del_nodes = tester.get_del_statements(source)
            assert len(del_nodes) >= 1, f"Should have del statements: {source}"
            
            # Should have multiple target types
            targets = tester.get_del_targets(source)
            assert len(targets) >= 3, f"Should have multiple targets: {source}"


class TestSection75DelErrorConditions:
    """Test del statement error conditions."""
    
    def test_del_literals_error(self, tester):
        """Test del with literals (should be syntax error)"""
        # Language Reference: del cannot target literals
        literal_del_patterns = [
            "del 42",
            "del 'string'",
            "del [1, 2, 3]",
            "del {'key': 'value'}",
            "del True",
            "del None",
        ]
        
        for source in literal_del_patterns:
            tester.assert_del_syntax_error(source)
    
    def test_del_function_calls_error(self, tester):
        """Test del with function calls (should be syntax error)"""
        # Language Reference: del cannot target function calls
        function_call_del_patterns = [
            "del func()",
            "del obj.method()",
            "del get_value()",
            "del len([1, 2, 3])",
        ]
        
        for source in function_call_del_patterns:
            tester.assert_del_syntax_error(source)
    
    def test_del_expressions_error(self, tester):
        """Test del with expressions (should be syntax error)"""
        # Language Reference: del cannot target arbitrary expressions
        expression_del_patterns = [
            "del x + y",
            "del a * b",
            "del (x + y)",
            "del x if condition else y",
            "del lambda x: x",
        ]
        
        for source in expression_del_patterns:
            tester.assert_del_syntax_error(source)
    
    def test_del_assignments_error(self, tester):
        """Test del with assignment expressions (should be syntax error)"""
        # Language Reference: del cannot target assignments
        assignment_del_patterns = [
            "del (x := 5)",  # Assignment expression
            "del x = 5",     # Assignment statement
        ]
        
        for source in assignment_del_patterns:
            tester.assert_del_syntax_error(source)


class TestSection75DelInControlStructures:
    """Test del statements in various control structures."""
    
    def test_del_in_conditionals(self, tester):
        """Test del statements in conditional blocks"""
        # Language Reference: del can appear in control structures
        conditional_del_patterns = [
            """
x = 42
if x > 0:
    del x
""",
            """
temp_data = get_data()
if temp_data is not None:
    process(temp_data)
    del temp_data
else:
    del temp_data  # Clean up even if None
""",
            """
cache = {}
for key in ['a', 'b', 'c']:
    if key in cache:
        del cache[key]
""",
            """
cleanup_needed = True
while cleanup_needed:
    if temp_vars_exist():
        del temp_var1, temp_var2
        cleanup_needed = False
"""
        ]
        
        for source in conditional_del_patterns:
            tree = tester.assert_del_syntax_parses(source)
            del_nodes = tester.get_del_statements(source)
            assert len(del_nodes) >= 1, f"Should have del statements: {source}"
    
    def test_del_in_loops(self, tester):
        """Test del statements in loop contexts"""
        # Language Reference: del can appear in loops
        loop_del_patterns = [
            """
items = [1, 2, 3, 4, 5]
for i in range(len(items)):
    if items[i] % 2 == 0:
        del items[i]
        break  # Avoid index issues
""",
            """
data = {'a': 1, 'b': 2, 'c': 3}
for key in list(data.keys()):
    if data[key] % 2 == 0:
        del data[key]
""",
            """
temp_files = get_temp_files()
while temp_files:
    file_path = temp_files.pop()
    if os.path.exists(file_path):
        os.remove(file_path)
    del file_path
""",
            """
resources = acquire_resources()
try:
    for resource in resources:
        if resource.is_expired():
            del resource.cached_data
        use_resource(resource)
finally:
    for resource in resources:
        del resource
"""
        ]
        
        for source in loop_del_patterns:
            tree = tester.assert_del_syntax_parses(source)
            del_nodes = tester.get_del_statements(source)
            assert len(del_nodes) >= 1, f"Should have del statements: {source}"
    
    def test_del_in_exception_handling(self, tester):
        """Test del statements in exception handling"""
        # Language Reference: del can appear in try/except/finally
        exception_del_patterns = [
            """
resource = None
try:
    resource = acquire_resource()
    use_resource(resource)
except Exception:
    if resource:
        del resource
    raise
finally:
    del resource
""",
            """
temp_data = None
try:
    temp_data = process_data()
    result = transform(temp_data)
except ProcessingError:
    del temp_data
    raise
except Exception as e:
    del temp_data, e
    raise
""",
            """
cache = {}
try:
    expensive_computation(cache)
except MemoryError:
    del cache  # Free memory
    raise
except Exception:
    cache.clear()
else:
    optimize_cache(cache)
finally:
    del cache
"""
        ]
        
        for source in exception_del_patterns:
            tree = tester.assert_del_syntax_parses(source)
            del_nodes = tester.get_del_statements(source)
            assert len(del_nodes) >= 1, f"Should have del statements: {source}"
    
    def test_del_in_functions(self, tester):
        """Test del statements in function contexts"""
        # Language Reference: del can appear in functions
        function_del_patterns = [
            """
def cleanup_function():
    global temp_var
    if 'temp_var' in globals():
        del temp_var

def process_with_cleanup(data):
    temp_result = expensive_operation(data)
    try:
        return transform(temp_result)
    finally:
        del temp_result
""",
            """
def cache_manager():
    cache = {}
    
    def add_item(key, value):
        cache[key] = value
    
    def remove_item(key):
        if key in cache:
            del cache[key]
    
    def clear_cache():
        del cache
        cache = {}
    
    return add_item, remove_item, clear_cache
""",
            """
def generator_with_cleanup():
    resources = []
    try:
        for i in range(10):
            resource = acquire_resource(i)
            resources.append(resource)
            yield resource
    finally:
        for resource in resources:
            del resource
        del resources
"""
        ]
        
        for source in function_del_patterns:
            tree = tester.assert_del_syntax_parses(source)
            del_nodes = tester.get_del_statements(source)
            assert len(del_nodes) >= 1, f"Should have del statements: {source}"


class TestSection75DelAST:
    """Test del AST structure validation."""
    
    def test_del_ast_node_structure(self, tester):
        """Test Delete AST node structure"""
        # Language Reference: AST structure for del statements
        del_ast_cases = [
            """
x = 42
del x
""",
            """
obj.attr = "value"
del obj.attr
""",
            """
items = [1, 2, 3]
del items[0]
""",
            """
a, b, c = 1, 2, 3
del a, b, c
"""
        ]
        
        for source in del_ast_cases:
            tree = tester.assert_del_syntax_parses(source)
            del_nodes = tester.get_del_statements(source)
            assert len(del_nodes) >= 1, f"Should have del nodes: {source}"
            
            for del_node in del_nodes:
                # Delete nodes must have targets list
                assert isinstance(del_node, ast.Delete), "Should be Delete node"
                assert hasattr(del_node, 'targets'), "Delete should have targets attribute"
                assert isinstance(del_node.targets, list), "Targets should be a list"
                assert len(del_node.targets) >= 1, "Should have at least one target"
    
    def test_del_target_types_ast(self, tester):
        """Test different del target types in AST"""
        # Language Reference: del targets can be Name, Attribute, Subscript
        target_types_source = """
x = 42
obj.attr = "value"
items = [1, 2, 3]
data = {'key': 'value'}

del x  # Name target
del obj.attr  # Attribute target
del items[0]  # Subscript target
del data['key']  # Subscript target
"""
        
        tree = tester.assert_del_syntax_parses(target_types_source)
        targets = tester.get_del_targets(target_types_source)
        
        # Should have different target types
        target_types = [type(target).__name__ for target in targets]
        assert 'Name' in target_types, "Should have Name targets"
        assert 'Attribute' in target_types, "Should have Attribute targets"
        assert 'Subscript' in target_types, "Should have Subscript targets"
    
    def test_multiple_targets_ast(self, tester):
        """Test multiple targets in single del statement AST"""
        # Language Reference: del can have multiple targets
        multiple_targets_source = """
a = 1
b = 2
obj.x = 10
items = [1, 2, 3]
del a, b, obj.x, items[0]
"""
        
        tree = tester.assert_del_syntax_parses(multiple_targets_source)
        del_nodes = tester.get_del_statements(multiple_targets_source)
        assert len(del_nodes) == 1, "Should have one del statement"
        
        del_node = del_nodes[0]
        assert len(del_node.targets) == 4, "Should have four targets"
        
        # Verify target types
        target_types = [type(target).__name__ for target in del_node.targets]
        expected_types = ['Name', 'Name', 'Attribute', 'Subscript']
        assert target_types == expected_types, f"Expected {expected_types}, got {target_types}"
    
    def test_del_in_complex_context_ast(self, tester):
        """Test del in complex contexts AST structure"""
        # Language Reference: del in various contexts
        complex_context_source = """
def function():
    local_var = 42
    
    if condition:
        temp = get_temp()
        del temp
    
    try:
        resource = acquire()
        use_resource(resource)
    finally:
        del resource, local_var
    
    for item in items:
        if should_delete(item):
            del item.cache
"""
        
        tree = tester.assert_del_syntax_parses(complex_context_source)
        del_nodes = tester.get_del_statements(complex_context_source)
        assert len(del_nodes) >= 3, "Should have multiple del statements in different contexts"


class TestSection75CrossImplementationCompatibility:
    """Test cross-implementation compatibility for del statements."""
    
    def test_del_ast_consistency(self, tester):
        """Test del AST consistency across implementations"""
        # Language Reference: del AST should be consistent
        consistency_test_cases = [
            """
x = 42
del x
""",
            """
obj.attr = "value"
del obj.attr
""",
            """
items = [1, 2, 3, 4, 5]
del items[1:4]
""",
            """
a, b, c = 1, 2, 3
del a, b, c
"""
        ]
        
        for source in consistency_test_cases:
            tree = tester.assert_del_syntax_parses(source)
            
            # Should have consistent del structure
            del_nodes = tester.get_del_statements(source)
            assert len(del_nodes) >= 1, f"Should have del statements: {source}"
            
            for del_node in del_nodes:
                assert isinstance(del_node, ast.Delete), "Should be Delete node"
                assert hasattr(del_node, 'targets'), "Should have targets attribute"
                assert len(del_node.targets) >= 1, "Should have targets"
    
    def test_comprehensive_del_patterns(self, tester):
        """Test comprehensive real-world del patterns"""
        # Language Reference: complex del usage scenarios
        comprehensive_patterns = [
            """
# Resource management with del
class ResourceManager:
    def __init__(self):
        self.resources = {}
        self.temp_data = []
    
    def acquire_resource(self, name):
        resource = expensive_resource_creation(name)
        self.resources[name] = resource
        return resource
    
    def release_resource(self, name):
        if name in self.resources:
            resource = self.resources[name]
            cleanup_resource(resource)
            del self.resources[name]
            del resource
    
    def cleanup_temp_data(self):
        while self.temp_data:
            item = self.temp_data.pop()
            if hasattr(item, 'cleanup'):
                item.cleanup()
            del item
        del self.temp_data[:]

def process_large_dataset(data):
    # Create working copies
    working_data = data.copy()
    intermediate_results = []
    temp_caches = {}
    
    try:
        for chunk in working_data:
            # Process chunk
            result = expensive_computation(chunk)
            intermediate_results.append(result)
            
            # Cache if needed
            if should_cache(chunk):
                temp_caches[chunk.id] = result
            
            # Clean up chunk immediately
            del chunk
        
        # Combine results
        final_result = combine_results(intermediate_results)
        
        # Clean up intermediate data
        for result in intermediate_results:
            del result
        del intermediate_results
        
        # Clean up caches
        for cache_key in list(temp_caches.keys()):
            del temp_caches[cache_key]
        del temp_caches
        
        return final_result
        
    except MemoryError:
        # Emergency cleanup
        del working_data, intermediate_results, temp_caches
        raise
    finally:
        # Final cleanup
        if 'working_data' in locals():
            del working_data
""",
            """
# Configuration management with del
class ConfigManager:
    def __init__(self):
        self.config = {}
        self.temp_settings = {}
        self.cached_values = {}
    
    def load_config(self, source):
        # Clear existing config
        for key in list(self.config.keys()):
            del self.config[key]
        
        # Load new config
        new_config = parse_config(source)
        self.config.update(new_config)
        del new_config
    
    def set_temp_setting(self, key, value):
        # Store original if exists
        if key in self.config:
            self.temp_settings[key] = self.config[key]
        
        # Set temporary value
        self.config[key] = value
        
        # Clear any cached value
        if key in self.cached_values:
            del self.cached_values[key]
    
    def restore_temp_settings(self):
        # Restore original values
        for key, original_value in self.temp_settings.items():
            self.config[key] = original_value
            # Clear cache
            if key in self.cached_values:
                del self.cached_values[key]
        
        # Clear temp storage
        for key in list(self.temp_settings.keys()):
            del self.temp_settings[key]
    
    def get_cached_value(self, key):
        if key not in self.cached_values:
            self.cached_values[key] = expensive_compute(self.config[key])
        return self.cached_values[key]
    
    def invalidate_cache(self, pattern=None):
        if pattern is None:
            # Clear all cache
            for key in list(self.cached_values.keys()):
                del self.cached_values[key]
        else:
            # Clear matching entries
            for key in list(self.cached_values.keys()):
                if pattern_matches(key, pattern):
                    del self.cached_values[key]
"""
        ]
        
        for source in comprehensive_patterns:
            tree = tester.assert_del_syntax_parses(source)
            
            # Should have multiple del usages
            del_nodes = tester.get_del_statements(source)
            assert len(del_nodes) >= 5, f"Should have multiple del statements: {source}"
    
    def test_del_introspection(self, tester):
        """Test ability to analyze del statements programmatically"""
        # Test programmatic analysis of del structure
        introspection_source = """
def complex_cleanup():
    # Simple name deletion
    temp_var = 42
    del temp_var
    
    # Attribute deletion
    obj.cached_result = compute()
    del obj.cached_result
    
    # Subscript deletion
    data = {'key': 'value'}
    del data['key']
    
    # Slice deletion
    items = list(range(10))
    del items[2:8]
    
    # Multiple target deletion
    a, b, c = 1, 2, 3
    del a, b, c
    
    # Complex mixed deletion
    del (obj.nested.attr, 
         cache[get_key()], 
         temp_list[:5],
         local_var)
"""
        
        tree = tester.assert_del_syntax_parses(introspection_source)
        
        # Should identify all del statements
        del_nodes = tester.get_del_statements(introspection_source)
        assert len(del_nodes) >= 6, "Should have multiple del statements"
        
        # Should identify different target types
        targets = tester.get_del_targets(introspection_source)
        target_types = {type(target).__name__ for target in targets}
        expected_types = {'Name', 'Attribute', 'Subscript'}
        assert expected_types.issubset(target_types), f"Should have various target types: {target_types}"
        
        # Should have name, attribute, and subscript targets
        assert tester.has_name_targets(introspection_source), "Should have name targets"
        assert tester.has_attribute_targets(introspection_source), "Should have attribute targets"
        assert tester.has_subscript_targets(introspection_source), "Should have subscript targets"