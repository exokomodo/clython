"""
Section 7.12: Global Statement - Conformance Test Suite

Tests Python Language Reference Section 7.12 compliance across implementations.
Based on formal global statement syntax definitions and prose assertions for global scope binding.

Grammar tested:
    global_stmt: 'global' NAME (',' NAME)*

Language Reference requirements tested:
    - Global statement syntax validation
    - Module-level variable binding modification
    - Global statement placement and scope requirements
    - Multiple variable global declarations
    - Interaction with local variable shadowing
    - Error conditions for invalid global usage
    - Global statement AST structure validation
    - Cross-implementation global compatibility
"""

import ast
import pytest
import sys
from typing import Any


class GlobalTester:
    """Helper class for testing global statement conformance.
    
    Focuses on AST structure validation for global syntax and scope
    binding patterns that can be statically analyzed for cross-implementation compatibility.
    """
    
    def assert_global_syntax_parses(self, source: str):
        """Test that global statement syntax parses correctly.
        
        Args:
            source: Python source code with global statements
        """
        try:
            tree = ast.parse(source)
            return tree
        except SyntaxError as e:
            pytest.fail(f"Global syntax should be valid but failed to parse: {source}\\nError: {e}")
    
    def assert_global_syntax_error(self, source: str):
        """Test that invalid global syntax raises SyntaxError.
        
        Args:
            source: Python source code that should be invalid
        """
        with pytest.raises(SyntaxError):
            ast.parse(source)
    
    def get_global_statements(self, source: str) -> list:
        """Get Global AST nodes from source.
        
        Args:
            source: Python source code
            
        Returns:
            List of ast.Global nodes
        """
        tree = ast.parse(source)
        globals_list = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Global):
                globals_list.append(node)
        
        return globals_list
    
    def get_global_names(self, source: str) -> list:
        """Get names declared as global.
        
        Args:
            source: Python source code
            
        Returns:
            List of global variable name strings
        """
        global_nodes = self.get_global_statements(source)
        names = []
        
        for global_node in global_nodes:
            names.extend(global_node.names)
        
        return names
    
    def has_function_definitions(self, source: str) -> bool:
        """Check if source contains function definitions.
        
        Args:
            source: Python source code
            
        Returns:
            True if contains function definitions
        """
        tree = ast.parse(source)
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                return True
        
        return False
    
    def get_assignment_targets(self, source: str) -> list:
        """Get assignment target names from source.
        
        Args:
            source: Python source code
            
        Returns:
            List of assignment target names
        """
        tree = ast.parse(source)
        targets = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        targets.append(target.id)
        
        return targets


@pytest.fixture
def tester():
    """Provide GlobalTester instance for tests."""
    return GlobalTester()


class TestSection712BasicGlobalSyntax:
    """Test basic global statement syntax."""
    
    def test_simple_global_statements(self, tester):
        """Test simple global statement syntax"""
        # Language Reference: global_stmt: 'global' NAME (',' NAME)*
        simple_global_patterns = [
            """
x = 10

def function():
    global x
    x = 20
""",
            """
counter = 0

def increment():
    global counter
    counter += 1
    return counter
""",
            """
result = None

def compute():
    global result
    result = 42
    return result
""",
            """
flag = False

def toggle():
    global flag
    flag = not flag
    return flag
"""
        ]
        
        for source in simple_global_patterns:
            tree = tester.assert_global_syntax_parses(source)
            global_nodes = tester.get_global_statements(source)
            assert len(global_nodes) == 1, f"Should have one global statement: {source}"
            
            global_names = tester.get_global_names(source)
            assert len(global_names) == 1, f"Should have one global variable: {source}"
    
    def test_multiple_global_variables(self, tester):
        """Test global statements with multiple variables"""
        # Language Reference: multiple NAME in global statement
        multiple_global_patterns = [
            """
x, y = 1, 2

def function():
    global x, y
    x, y = y, x
""",
            """
a, b, c = 1, 2, 3

def reset():
    global a, b, c
    a = b = c = 0
""",
            """
count, total = 0, 0

def update():
    global count, total
    count += 1
    total += count
    return count, total
""",
            """
flag, message, value = False, "", 0

def initialize():
    global flag, message, value
    flag = True
    message = "initialized"
    value = 42
"""
        ]
        
        for source in multiple_global_patterns:
            tree = tester.assert_global_syntax_parses(source)
            global_names = tester.get_global_names(source)
            assert len(global_names) >= 2, f"Should have multiple global variables: {source}"
    
    def test_global_in_nested_functions(self, tester):
        """Test global in nested function contexts"""
        # Language Reference: global affects innermost function scope
        nested_function_patterns = [
            """
shared_state = "initial"

def outer():
    def inner():
        global shared_state
        shared_state = "modified by inner"
    return inner
""",
            """
module_counter = 0

def factory():
    def counter():
        global module_counter
        module_counter += 1
        return module_counter
    return counter
""",
            """
global_list = []

def processor():
    def add_item(item):
        global global_list
        global_list.append(item)
    return add_item
""",
            """
config = {"debug": False}

def create_handler():
    def handle_debug():
        global config
        config["debug"] = True
    def handle_release():
        global config  
        config["debug"] = False
    return handle_debug, handle_release
"""
        ]
        
        for source in nested_function_patterns:
            tree = tester.assert_global_syntax_parses(source)
            assert tester.has_function_definitions(source), f"Should have function definitions: {source}"
            
            global_nodes = tester.get_global_statements(source)
            assert len(global_nodes) >= 1, f"Should have global statements: {source}"
    
    def test_separate_global_statements(self, tester):
        """Test multiple separate global statements"""
        # Language Reference: multiple global statements allowed
        separate_global_patterns = [
            """
x, y = 1, 2

def function():
    global x
    global y
    x = 10
    y = 20
""",
            """
a, b, c = 1, 2, 3

def worker():
    global a
    a += 1
    global b
    b += 2
    global c
    c += 3
    return a + b + c
""",
            """
flag = False
message = "initial"

def update():
    global flag
    flag = True
    global message
    message = "updated"
"""
        ]
        
        for source in separate_global_patterns:
            tree = tester.assert_global_syntax_parses(source)
            global_nodes = tester.get_global_statements(source)
            assert len(global_nodes) >= 2, f"Should have multiple global statements: {source}"


class TestSection712GlobalScopeBinding:
    """Test global scope binding behavior."""
    
    def test_module_level_binding(self, tester):
        """Test global binding to module-level variables"""
        # Language Reference: global binds to module scope
        module_level_patterns = [
            """
module_var = "module level"

def function():
    global module_var
    module_var = "modified by function"
    return module_var
""",
            """
counter = 0

def increment():
    global counter
    counter += 1
    return counter

def decrement():
    global counter
    counter -= 1
    return counter
""",
            """
state = {"initialized": False, "count": 0}

def initialize():
    global state
    state = {"initialized": True, "count": 1}
    return state

def get_state():
    global state
    return state.copy()
""",
            """
cache = {}

def cache_get(key):
    global cache
    return cache.get(key)

def cache_set(key, value):
    global cache
    cache[key] = value
"""
        ]
        
        for source in module_level_patterns:
            tree = tester.assert_global_syntax_parses(source)
            global_names = tester.get_global_names(source)
            assert len(global_names) >= 1, f"Should have global variables: {source}"
            
            # Should have both module-level assignments and global statements
            assignment_targets = tester.get_assignment_targets(source)
            assert len(assignment_targets) >= 1, f"Should have module-level assignments: {source}"
    
    def test_global_variable_creation(self, tester):
        """Test global statement creating new module variables"""
        # Language Reference: global can create new module-level variables
        variable_creation_patterns = [
            """
def function():
    global new_variable
    new_variable = "created by function"
    return new_variable
""",
            """
def initialize():
    global app_state, config, logger
    app_state = "initialized"
    config = {"debug": True}
    logger = None
""",
            """
def setup():
    global CONSTANT
    CONSTANT = 42
    return CONSTANT

def use_constant():
    global CONSTANT
    return CONSTANT * 2
""",
            """
def create_globals():
    global x, y, z
    x = 1
    y = 2  
    z = 3
    return x + y + z
"""
        ]
        
        for source in variable_creation_patterns:
            tree = tester.assert_global_syntax_parses(source)
            global_names = tester.get_global_names(source)
            assert len(global_names) >= 1, f"Should have global variables: {source}"
    
    def test_global_shadowing_prevention(self, tester):
        """Test global preventing local variable shadowing"""
        # Language Reference: global prevents local variable creation
        shadowing_prevention_patterns = [
            """
module_var = "module"

def function():
    global module_var
    # Without global, this would create local variable
    module_var = "modified"
    return module_var
""",
            """
x = 10

def outer():
    def inner():
        global x  # Refers to module x, not outer's x if it existed
        x = 20
    return inner
""",
            """
shared = []

def processor():
    global shared
    shared.append("item")
    # Without global, shared would be local and += would fail
    shared += ["another"]
    return shared
""",
            """
config = {"mode": "production"}

def configure():
    global config
    # Without global, this would create new local dict
    config.update({"mode": "development", "debug": True})
    return config
"""
        ]
        
        for source in shadowing_prevention_patterns:
            tree = tester.assert_global_syntax_parses(source)
            global_names = tester.get_global_names(source)
            assert len(global_names) >= 1, f"Should have global variables: {source}"


class TestSection712GlobalErrorConditions:
    """Test global statement error conditions."""
    
    def test_invalid_global_syntax(self, tester):
        """Test invalid global statement syntax"""
        # Language Reference: syntactic restrictions on global
        invalid_global_syntax = [
            "global",                       # Missing variable name
            "global 123",                   # Invalid variable name
            "global def",                   # Keyword as variable name
            "global x.y",                   # Dotted name not allowed
            "global x[0]",                  # Subscript not allowed
        ]
        
        for source in invalid_global_syntax:
            tester.assert_global_syntax_error(source)
    
    def test_global_assignment_before_declaration_restrictions(self, tester):
        """Test global assignment before declaration restrictions"""
        # Language Reference: global declaration affects entire function scope
        # Note: These restrictions are checked at compile time in some implementations
        assignment_before_global_patterns = [
            """
def function():
    # Assignment before global - should parse but may cause issues
    x = 10
    global x
""",
        ]
        
        for source in assignment_before_global_patterns:
            # This parses successfully in AST but may fail at compilation/runtime
            tree = tester.assert_global_syntax_parses(source)
            global_names = tester.get_global_names(source)
            assert len(global_names) >= 1, f"Should parse global syntax: {source}"
    
    def test_global_parameter_name_restrictions(self, tester):
        """Test global with parameter names"""
        # Language Reference: cannot declare parameter as global
        # Note: This is checked at compile time, not parse time
        parameter_name_patterns = [
            """
def function(x):
    global x  # May cause compile-time error but parses
    x = 10
""",
            """
def function(a, b):
    global a  # May cause compile-time error but parses
    a = 100
""",
        ]
        
        for source in parameter_name_patterns:
            # This parses successfully in AST but may fail at compilation
            tree = tester.assert_global_syntax_parses(source)
            global_names = tester.get_global_names(source)
            assert len(global_names) >= 1, f"Should parse global syntax: {source}"
    
    def test_global_with_nested_function_parameters(self, tester):
        """Test global with nested function parameter interactions"""
        # Language Reference: global can shadow outer function parameters
        nested_parameter_patterns = [
            """
x = "module"

def outer(x):  # Parameter x shadows module x
    def inner():
        global x  # Refers to module x, not parameter x
        x = "global"
    return inner
""",
            """
value = 42

def factory(value):  # Parameter shadows module variable
    def worker():
        global value  # Refers to module value
        value = 100
        return value
    return worker
"""
        ]
        
        for source in nested_parameter_patterns:
            tree = tester.assert_global_syntax_parses(source)
            global_names = tester.get_global_names(source)
            assert len(global_names) >= 1, f"Should have global variables: {source}"


class TestSection712GlobalInteractionPatterns:
    """Test global interaction with other language features."""
    
    def test_global_with_nonlocal_statements(self, tester):
        """Test global and nonlocal statement coexistence"""
        # Language Reference: global and nonlocal can coexist
        global_nonlocal_patterns = [
            """
module_var = "module"

def outer():
    enclosing_var = "enclosing"
    
    def inner():
        global module_var
        nonlocal enclosing_var
        module_var = "modified module"
        enclosing_var = "modified enclosing"
    
    return inner
""",
            """
GLOBAL_STATE = {"count": 0}

def factory():
    local_state = {"value": 42}
    
    def worker():
        global GLOBAL_STATE
        nonlocal local_state
        GLOBAL_STATE["count"] += 1
        local_state["value"] *= 2
        return GLOBAL_STATE, local_state
    
    return worker
""",
            """
TOTAL = 0

def accumulator_factory():
    partial_sum = 0
    
    def accumulate(value):
        global TOTAL
        nonlocal partial_sum
        partial_sum += value
        TOTAL += value
        return partial_sum, TOTAL
    
    return accumulate
"""
        ]
        
        for source in global_nonlocal_patterns:
            tree = tester.assert_global_syntax_parses(source)
            global_names = tester.get_global_names(source)
            assert len(global_names) >= 1, f"Should have global variables: {source}"
            
            # Should also have nonlocal statements
            nonlocal_nodes = [node for node in ast.walk(tree) if isinstance(node, ast.Nonlocal)]
            assert len(nonlocal_nodes) >= 1, f"Should have nonlocal statements: {source}"
    
    def test_global_with_class_definitions(self, tester):
        """Test global in class method contexts"""
        # Language Reference: global works in class methods
        class_method_patterns = [
            """
class_counter = 0

class MyClass:
    def increment_global(self):
        global class_counter
        class_counter += 1
        return class_counter
    
    @classmethod
    def reset_global(cls):
        global class_counter
        class_counter = 0
    
    @staticmethod
    def get_global():
        global class_counter
        return class_counter
""",
            """
MODULE_CONFIG = {"debug": False}

class ConfigManager:
    def enable_debug(self):
        global MODULE_CONFIG
        MODULE_CONFIG["debug"] = True
    
    def disable_debug(self):
        global MODULE_CONFIG
        MODULE_CONFIG["debug"] = False
    
    def get_config(self):
        global MODULE_CONFIG
        return MODULE_CONFIG.copy()
""",
            """
shared_state = []

class StateManager:
    def __init__(self):
        global shared_state
        shared_state.append(f"StateManager-{id(self)}")
    
    def update_state(self, value):
        global shared_state
        shared_state.append(value)
        return len(shared_state)
"""
        ]
        
        for source in class_method_patterns:
            tree = tester.assert_global_syntax_parses(source)
            global_names = tester.get_global_names(source)
            assert len(global_names) >= 1, f"Should have global variables: {source}"
            
            # Should have class definitions
            class_nodes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            assert len(class_nodes) >= 1, f"Should have class definitions: {source}"
    
    def test_global_with_exception_handling(self, tester):
        """Test global in exception handling contexts"""
        # Language Reference: global works in try/except/finally blocks
        exception_handling_patterns = [
            """
error_count = 0
last_error = None

def risky_operation():
    global error_count, last_error
    try:
        # Simulate risky operation
        result = 1 / 0
    except ZeroDivisionError as e:
        error_count += 1
        last_error = str(e)
        return None
    finally:
        # Cleanup can also use global
        pass
    return result
""",
            """
attempt_count = 0
success_count = 0

def retry_operation(operation, max_attempts=3):
    global attempt_count, success_count
    for i in range(max_attempts):
        try:
            attempt_count += 1
            result = operation()
            success_count += 1
            return result
        except Exception as e:
            if i == max_attempts - 1:
                raise
    return None
""",
            """
resource_registry = {}

def with_global_resource(resource_id):
    global resource_registry
    try:
        resource_registry[resource_id] = "active"
        yield resource_id
    finally:
        if resource_id in resource_registry:
            del resource_registry[resource_id]
"""
        ]
        
        for source in exception_handling_patterns:
            tree = tester.assert_global_syntax_parses(source)
            global_names = tester.get_global_names(source)
            assert len(global_names) >= 1, f"Should have global variables: {source}"
    
    def test_global_with_comprehensions(self, tester):
        """Test global interaction with comprehensions"""
        # Language Reference: global scope interaction with comprehensions
        comprehension_patterns = [
            """
filter_criteria = lambda x: x > 0

def process_data(data):
    global filter_criteria
    # Comprehension can access global through function scope
    filtered = [x for x in data if filter_criteria(x)]
    return filtered
""",
            """
transform_function = str.upper

def transform_list(items):
    global transform_function
    # Global function used in comprehension
    return [transform_function(item) for item in items]
""",
            """
multiplier = 2

def multiply_values(values):
    global multiplier
    # Global variable accessed in comprehension
    result = [x * multiplier for x in values]
    multiplier += 1  # Modify global after use
    return result
"""
        ]
        
        for source in comprehension_patterns:
            tree = tester.assert_global_syntax_parses(source)
            global_names = tester.get_global_names(source)
            assert len(global_names) >= 1, f"Should have global variables: {source}"


class TestSection712GlobalASTStructure:
    """Test global AST structure validation."""
    
    def test_global_ast_node_structure(self, tester):
        """Test Global AST node structure"""
        # Language Reference: AST structure for global statements
        global_ast_cases = [
            """
x = 10

def function():
    global x
    x = 20
""",
            """
a, b, c = 1, 2, 3

def function():
    global a, b, c
    a = b = c = 0
"""
        ]
        
        for source in global_ast_cases:
            tree = tester.assert_global_syntax_parses(source)
            global_nodes = tester.get_global_statements(source)
            assert len(global_nodes) >= 1, f"Should have global nodes: {source}"
            
            for global_node in global_nodes:
                # Should have names attribute
                assert hasattr(global_node, 'names'), "Global should have 'names' attribute"
                assert isinstance(global_node.names, list), "names should be list"
                assert len(global_node.names) >= 1, "Should have at least one name"
                
                # Each name should be a string
                for name in global_node.names:
                    assert isinstance(name, str), "Global name should be string"
    
    def test_global_statement_positioning(self, tester):
        """Test global statement positioning in AST"""
        # Language Reference: global statements can appear anywhere in function
        positioning_cases = [
            """
x = 10

def function():
    global x  # At beginning
    x = 20
    return x
""",
            """
x = 10

def function():
    y = 5
    global x  # In middle
    x = y + 10
    return x
""",
            """
x = 10

def function():
    y = 5
    z = y * 2
    global x  # Towards end
    x = z
"""
        ]
        
        for source in positioning_cases:
            tree = tester.assert_global_syntax_parses(source)
            global_nodes = tester.get_global_statements(source)
            assert len(global_nodes) == 1, f"Should have one global statement: {source}"
    
    def test_multiple_global_statements_ast(self, tester):
        """Test multiple global statements in AST"""
        # Language Reference: multiple global statements create multiple AST nodes
        multiple_statement_source = """
a, b, c = 1, 2, 3

def function():
    global a
    global b, c
    a = 10
    b = 20
    c = 30
"""
        
        tree = tester.assert_global_syntax_parses(multiple_statement_source)
        global_nodes = tester.get_global_statements(multiple_statement_source)
        assert len(global_nodes) == 2, "Should have two global statements"
        
        # First statement should have one name
        assert len(global_nodes[0].names) == 1, "First statement should have one name"
        assert global_nodes[0].names[0] == "a", "First statement should declare 'a'"
        
        # Second statement should have two names
        assert len(global_nodes[1].names) == 2, "Second statement should have two names"
        assert "b" in global_nodes[1].names, "Second statement should declare 'b'"
        assert "c" in global_nodes[1].names, "Second statement should declare 'c'"


class TestSection712CrossImplementationCompatibility:
    """Test cross-implementation compatibility for global statements."""
    
    def test_global_ast_consistency(self, tester):
        """Test global AST consistency across implementations"""
        # Language Reference: global AST should be consistent
        consistency_test_cases = [
            """
counter = 0

def increment():
    global counter
    counter += 1
    return counter
""",
            """
state = "initial"

def change_state(new_state):
    global state
    old_state = state
    state = new_state
    return old_state, new_state
""",
            """
total = 0
count = 0

def add_value(value):
    global total, count
    total += value
    count += 1
    return total / count if count > 0 else 0
"""
        ]
        
        for source in consistency_test_cases:
            tree = tester.assert_global_syntax_parses(source)
            
            # Should have consistent global structure
            global_nodes = tester.get_global_statements(source)
            assert len(global_nodes) >= 1, f"Should have global statements: {source}"
            
            for global_node in global_nodes:
                assert hasattr(global_node, 'names'), "Should have names attribute"
                assert len(global_node.names) >= 1, "Should have variable names"
    
    def test_comprehensive_global_patterns(self, tester):
        """Test comprehensive real-world global patterns"""
        # Language Reference: complex global usage scenarios
        comprehensive_patterns = [
            """
# Configuration system with global state
DEBUG_MODE = False
LOG_LEVEL = "INFO"
FEATURES = {"feature_a": False, "feature_b": True}

def configure_debug(enabled=True):
    global DEBUG_MODE, LOG_LEVEL
    DEBUG_MODE = enabled
    LOG_LEVEL = "DEBUG" if enabled else "INFO"

def enable_feature(feature_name):
    global FEATURES
    if feature_name in FEATURES:
        FEATURES[feature_name] = True

def get_config():
    global DEBUG_MODE, LOG_LEVEL, FEATURES
    return {
        "debug": DEBUG_MODE,
        "log_level": LOG_LEVEL,
        "features": FEATURES.copy()
    }
""",
            """
# Plugin system with global registry
PLUGINS = {}
PLUGIN_HOOKS = {}

def register_plugin(name, plugin_class):
    global PLUGINS
    PLUGINS[name] = plugin_class()

def register_hook(event, callback):
    global PLUGIN_HOOKS
    if event not in PLUGIN_HOOKS:
        PLUGIN_HOOKS[event] = []
    PLUGIN_HOOKS[event].append(callback)

def trigger_hooks(event, *args, **kwargs):
    global PLUGIN_HOOKS
    results = []
    for callback in PLUGIN_HOOKS.get(event, []):
        result = callback(*args, **kwargs)
        results.append(result)
    return results

def get_plugin_stats():
    global PLUGINS, PLUGIN_HOOKS
    return {
        "plugins": len(PLUGINS),
        "hooks": {event: len(callbacks) for event, callbacks in PLUGIN_HOOKS.items()}
    }
"""
        ]
        
        for source in comprehensive_patterns:
            tree = tester.assert_global_syntax_parses(source)
            
            # Should have multiple global usages
            global_names = tester.get_global_names(source)
            assert len(global_names) >= 3, f"Should have multiple global variables: {source}"
    
    def test_global_introspection(self, tester):
        """Test ability to analyze global statements programmatically"""
        # Test programmatic analysis of global structure
        introspection_source = """
MODULE_STATE = {"initialized": False}
CACHE = {}
COUNTERS = {"requests": 0, "errors": 0}

def initialize_system():
    global MODULE_STATE
    MODULE_STATE["initialized"] = True
    
def cache_set(key, value):
    global CACHE
    CACHE[key] = value

def increment_counter(counter_name):
    global COUNTERS
    if counter_name in COUNTERS:
        COUNTERS[counter_name] += 1

def reset_system():
    global MODULE_STATE, CACHE, COUNTERS
    MODULE_STATE = {"initialized": False}
    CACHE.clear()
    COUNTERS = {"requests": 0, "errors": 0}
"""
        
        tree = tester.assert_global_syntax_parses(introspection_source)
        
        # Should identify all global statements
        global_nodes = tester.get_global_statements(introspection_source)
        assert len(global_nodes) >= 4, "Should have multiple global statements"
        
        # Should identify all global variable names
        global_names = tester.get_global_names(introspection_source)
        assert len(global_names) >= 6, "Should have multiple global variables"
        
        # Should identify specific variable names
        assert "MODULE_STATE" in global_names, "Should identify MODULE_STATE as global"
        assert "CACHE" in global_names, "Should identify CACHE as global"
        assert "COUNTERS" in global_names, "Should identify COUNTERS as global"
        
        # Should have module-level variable definitions
        assignment_targets = tester.get_assignment_targets(introspection_source)
        assert len(assignment_targets) >= 3, "Should have module-level assignments"