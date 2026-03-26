"""
Section 7.13: Nonlocal Statement - Conformance Test Suite

Tests Python Language Reference Section 7.13 compliance across implementations.
Based on formal nonlocal statement syntax definitions and prose assertions for enclosing scope binding.

Grammar tested:
    nonlocal_stmt: 'nonlocal' NAME (',' NAME)* 

Language Reference requirements tested:
    - Nonlocal statement syntax validation
    - Enclosing scope variable binding modification
    - Nonlocal statement placement and scope requirements
    - Multiple variable nonlocal declarations
    - Interaction with nested function closures
    - Error conditions for invalid nonlocal usage
    - Nonlocal statement AST structure validation
    - Cross-implementation nonlocal compatibility
"""

import ast
import pytest
import sys
from typing import Any


class NonlocalTester:
    """Helper class for testing nonlocal statement conformance.
    
    Focuses on AST structure validation for nonlocal syntax and scope
    binding patterns that can be statically analyzed for cross-implementation compatibility.
    """
    
    def assert_nonlocal_syntax_parses(self, source: str):
        """Test that nonlocal statement syntax parses correctly.
        
        Args:
            source: Python source code with nonlocal statements
        """
        try:
            tree = ast.parse(source)
            return tree
        except SyntaxError as e:
            pytest.fail(f"Nonlocal syntax should be valid but failed to parse: {source}\\nError: {e}")
    
    def assert_nonlocal_syntax_error(self, source: str):
        """Test that invalid nonlocal syntax raises SyntaxError.
        
        Args:
            source: Python source code that should be invalid
        """
        with pytest.raises(SyntaxError):
            ast.parse(source)
    
    def get_nonlocal_statements(self, source: str) -> list:
        """Get Nonlocal AST nodes from source.
        
        Args:
            source: Python source code
            
        Returns:
            List of ast.Nonlocal nodes
        """
        tree = ast.parse(source)
        nonlocals = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Nonlocal):
                nonlocals.append(node)
        
        return nonlocals
    
    def get_nonlocal_names(self, source: str) -> list:
        """Get names declared as nonlocal.
        
        Args:
            source: Python source code
            
        Returns:
            List of nonlocal variable name strings
        """
        nonlocal_nodes = self.get_nonlocal_statements(source)
        names = []
        
        for nonlocal_node in nonlocal_nodes:
            names.extend(nonlocal_node.names)
        
        return names
    
    def has_nested_functions(self, source: str) -> bool:
        """Check if source contains nested function definitions.
        
        Args:
            source: Python source code
            
        Returns:
            True if contains nested functions
        """
        tree = ast.parse(source)
        function_depth = 0
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Simple heuristic: if we find functions at different levels
                # in the AST, there are likely nested functions
                function_depth += 1
        
        return function_depth >= 2
    
    def get_function_nesting_depth(self, source: str) -> int:
        """Get maximum function nesting depth.
        
        Args:
            source: Python source code
            
        Returns:
            Maximum depth of nested functions
        """
        tree = ast.parse(source)
        
        def count_depth(node, current_depth=0):
            max_depth = current_depth
            
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                current_depth += 1
                max_depth = current_depth
            
            for child in ast.iter_child_nodes(node):
                child_depth = count_depth(child, current_depth)
                max_depth = max(max_depth, child_depth)
            
            return max_depth
        
        return count_depth(tree)


@pytest.fixture
def tester():
    """Provide NonlocalTester instance for tests."""
    return NonlocalTester()


class TestSection713BasicNonlocalSyntax:
    """Test basic nonlocal statement syntax."""
    
    def test_simple_nonlocal_statements(self, tester):
        """Test simple nonlocal statement syntax"""
        # Language Reference: nonlocal_stmt: 'nonlocal' NAME (',' NAME)*
        simple_nonlocal_patterns = [
            """
def outer():
    x = 10
    def inner():
        nonlocal x
        x = 20
    return inner
""",
            """
def outer():
    value = 42
    def inner():
        nonlocal value
        value += 1
        return value
    return inner()
""",
            """
def factory():
    count = 0
    def counter():
        nonlocal count
        count += 1
        return count
    return counter
""",
            """
def outer():
    result = None
    def inner():
        nonlocal result
        result = "modified"
    inner()
    return result
"""
        ]
        
        for source in simple_nonlocal_patterns:
            tree = tester.assert_nonlocal_syntax_parses(source)
            nonlocal_nodes = tester.get_nonlocal_statements(source)
            assert len(nonlocal_nodes) == 1, f"Should have one nonlocal statement: {source}"
            
            nonlocal_names = tester.get_nonlocal_names(source)
            assert len(nonlocal_names) == 1, f"Should have one nonlocal variable: {source}"
    
    def test_multiple_nonlocal_variables(self, tester):
        """Test nonlocal statements with multiple variables"""
        # Language Reference: multiple NAME in nonlocal statement
        multiple_nonlocal_patterns = [
            """
def outer():
    x, y = 1, 2
    def inner():
        nonlocal x, y
        x, y = y, x
    return inner
""",
            """
def outer():
    a, b, c = 1, 2, 3
    def inner():
        nonlocal a, b, c
        a = b = c = 0
    return inner
""",
            """
def factory():
    count, total = 0, 0
    def update():
        nonlocal count, total
        count += 1
        total += count
        return count, total
    return update
""",
            """
def outer():
    flag, message, value = False, "", 0
    def inner():
        nonlocal flag, message, value
        flag = True
        message = "updated"
        value = 42
    return inner
"""
        ]
        
        for source in multiple_nonlocal_patterns:
            tree = tester.assert_nonlocal_syntax_parses(source)
            nonlocal_names = tester.get_nonlocal_names(source)
            assert len(nonlocal_names) >= 2, f"Should have multiple nonlocal variables: {source}"
    
    def test_nonlocal_in_nested_functions(self, tester):
        """Test nonlocal in nested function contexts"""
        # Language Reference: nonlocal applies to enclosing function scope
        nested_function_patterns = [
            """
def level0():
    x = "level0"
    def level1():
        def level2():
            nonlocal x
            x = "modified"
        return level2
    return level1
""",
            """
def outer():
    shared = []
    def middle():
        def inner():
            nonlocal shared
            shared.append("item")
        return inner
    return middle
""",
            """
def factory():
    state = {"count": 0}
    def outer():
        def inner():
            nonlocal state
            state = {"count": 1}
        return inner
    return outer
""",
            """
def create_closures():
    x, y = 10, 20
    def first():
        def nested():
            nonlocal x
            x += 1
        return nested
    def second():
        def nested():
            nonlocal y  
            y += 1
        return nested
    return first, second
"""
        ]
        
        for source in nested_function_patterns:
            tree = tester.assert_nonlocal_syntax_parses(source)
            assert tester.has_nested_functions(source), f"Should have nested functions: {source}"
            
            nonlocal_nodes = tester.get_nonlocal_statements(source)
            assert len(nonlocal_nodes) >= 1, f"Should have nonlocal statements: {source}"
    
    def test_separate_nonlocal_statements(self, tester):
        """Test multiple separate nonlocal statements"""
        # Language Reference: multiple nonlocal statements allowed
        separate_nonlocal_patterns = [
            """
def outer():
    x, y = 1, 2
    def inner():
        nonlocal x
        nonlocal y
        x = 10
        y = 20
    return inner
""",
            """
def factory():
    a, b, c = 1, 2, 3
    def worker():
        nonlocal a
        a += 1
        nonlocal b
        b += 2
        nonlocal c
        c += 3
        return a + b + c
    return worker
""",
            """
def outer():
    flag = False
    message = "initial"
    def inner():
        nonlocal flag
        flag = True
        nonlocal message
        message = "updated"
    return inner
"""
        ]
        
        for source in separate_nonlocal_patterns:
            tree = tester.assert_nonlocal_syntax_parses(source)
            nonlocal_nodes = tester.get_nonlocal_statements(source)
            assert len(nonlocal_nodes) >= 2, f"Should have multiple nonlocal statements: {source}"


class TestSection713NonlocalScopeBinding:
    """Test nonlocal scope binding behavior."""
    
    def test_enclosing_scope_binding(self, tester):
        """Test nonlocal binding to enclosing scope variables"""
        # Language Reference: nonlocal binds to enclosing function scope
        enclosing_scope_patterns = [
            """
def outer():
    enclosing_var = "outer"
    def inner():
        nonlocal enclosing_var
        enclosing_var = "modified by inner"
        return enclosing_var
    return inner()
""",
            """
def closure_factory():
    closure_state = 0
    def closure():
        nonlocal closure_state
        closure_state += 1
        return closure_state
    return closure
""",
            """
def accumulator(initial=0):
    total = initial
    def add(value):
        nonlocal total
        total += value
        return total
    return add
""",
            """
def stateful_processor():
    processed_count = 0
    results = []
    
    def process_item(item):
        nonlocal processed_count
        nonlocal results
        processed_count += 1
        results.append(f"Item {processed_count}: {item}")
        return results[-1]
    
    return process_item
"""
        ]
        
        for source in enclosing_scope_patterns:
            tree = tester.assert_nonlocal_syntax_parses(source)
            nonlocal_names = tester.get_nonlocal_names(source)
            assert len(nonlocal_names) >= 1, f"Should have nonlocal variables: {source}"
            
            # Should have nested function structure
            depth = tester.get_function_nesting_depth(source)
            assert depth >= 2, f"Should have function nesting: {source}"
    
    def test_multi_level_nonlocal_binding(self, tester):
        """Test nonlocal binding across multiple scope levels"""
        # Language Reference: nonlocal binds to nearest enclosing scope
        multi_level_patterns = [
            """
def level1():
    var1 = "level1"
    def level2():
        var2 = "level2"
        def level3():
            nonlocal var1  # Binds to level1
            nonlocal var2  # Binds to level2
            var1 = "modified at level3"
            var2 = "modified at level3"
        return level3
    return level2
""",
            """
def outer():
    x = 1
    def middle():
        y = 2
        def inner():
            nonlocal x  # Skip middle scope, bind to outer
            nonlocal y  # Bind to middle scope
            x = 10
            y = 20
        return inner
    return middle
""",
            """
def factory():
    shared_state = {"count": 0}
    def create_counter():
        local_multiplier = 1
        def counter():
            nonlocal shared_state  # Outer scope
            nonlocal local_multiplier  # Middle scope
            shared_state["count"] += local_multiplier
            local_multiplier += 1
            return shared_state["count"]
        return counter
    return create_counter
""",
            """
def nested_example():
    a = 1
    def level2():
        b = 2
        def level3():
            c = 3
            def level4():
                nonlocal a  # Skip level3, level2, bind to nested_example
                nonlocal b  # Skip level3, bind to level2
                nonlocal c  # Bind to level3
                a, b, c = 10, 20, 30
            return level4
        return level3
    return level2
"""
        ]
        
        for source in multi_level_patterns:
            tree = tester.assert_nonlocal_syntax_parses(source)
            nonlocal_names = tester.get_nonlocal_names(source)
            assert len(nonlocal_names) >= 2, f"Should have multiple nonlocal variables: {source}"
            
            # Should have deep nesting
            depth = tester.get_function_nesting_depth(source)
            assert depth >= 3, f"Should have deep function nesting: {source}"
    
    def test_nonlocal_with_closures(self, tester):
        """Test nonlocal behavior with closure creation"""
        # Language Reference: nonlocal creates closures over enclosing variables
        closure_patterns = [
            """
def make_counter():
    count = 0
    def increment():
        nonlocal count
        count += 1
        return count
    def decrement():
        nonlocal count
        count -= 1
        return count
    def get_count():
        return count
    return increment, decrement, get_count
""",
            """
def create_bank_account(initial_balance):
    balance = initial_balance
    
    def deposit(amount):
        nonlocal balance
        balance += amount
        return balance
    
    def withdraw(amount):
        nonlocal balance
        if amount <= balance:
            balance -= amount
        return balance
    
    def get_balance():
        return balance
    
    return {"deposit": deposit, "withdraw": withdraw, "balance": get_balance}
""",
            """
def event_tracker():
    events = []
    event_count = 0
    
    def log_event(event):
        nonlocal events, event_count
        events.append(event)
        event_count += 1
    
    def get_events():
        return events.copy()
    
    def get_count():
        return event_count
    
    return log_event, get_events, get_count
"""
        ]
        
        for source in closure_patterns:
            tree = tester.assert_nonlocal_syntax_parses(source)
            nonlocal_names = tester.get_nonlocal_names(source)
            assert len(nonlocal_names) >= 1, f"Should have nonlocal variables: {source}"
            
            # Should have multiple functions accessing nonlocal variables
            nonlocal_nodes = tester.get_nonlocal_statements(source)
            assert len(nonlocal_nodes) >= 1, f"Should have nonlocal statements: {source}"


class TestSection713NonlocalErrorConditions:
    """Test nonlocal statement error conditions."""
    
    def test_invalid_nonlocal_syntax(self, tester):
        """Test invalid nonlocal statement syntax"""
        # Language Reference: syntactic restrictions on nonlocal
        invalid_nonlocal_syntax = [
            "nonlocal",                     # Missing variable name
            "nonlocal 123",                 # Invalid variable name
            "nonlocal def",                 # Keyword as variable name
            "nonlocal x.y",                 # Dotted name not allowed
            "nonlocal x[0]",                # Subscript not allowed
        ]
        
        for source in invalid_nonlocal_syntax:
            tester.assert_nonlocal_syntax_error(source)
    
    def test_nonlocal_scope_restrictions(self, tester):
        """Test nonlocal scope placement restrictions"""
        # Language Reference: nonlocal only valid in nested functions
        # Note: Some scope restrictions are runtime errors, not syntax errors
        syntax_error_cases = [
            """
def function():
    # Function level without enclosing scope - runtime error, not syntax
    nonlocal x
    x = 10
""",
        ]
        
        # These should cause syntax errors
        definite_syntax_errors = [
            "nonlocal",                # Missing variable name
        ]
        
        for source in definite_syntax_errors:
            tester.assert_nonlocal_syntax_error(source)
        
        # These parse but would fail at runtime
        for source in syntax_error_cases:
            tree = tester.assert_nonlocal_syntax_parses(source)
            # Should parse successfully but would fail at runtime
    
    def test_nonlocal_undefined_variable_restrictions(self, tester):
        """Test nonlocal with undefined enclosing variables"""
        # Language Reference: nonlocal variables must exist in enclosing scope
        # Note: This is a runtime error, not syntax error, so syntax should parse
        undefined_variable_patterns = [
            """
def outer():
    def inner():
        nonlocal undefined_var  # Runtime error but syntax valid
        undefined_var = 10
    return inner
""",
            """
def outer():
    def inner():
        nonlocal missing_var  # Runtime error but syntax valid
        missing_var = "value"
    return inner
"""
        ]
        
        for source in undefined_variable_patterns:
            # Should parse (syntax is valid), but would fail at runtime
            tree = tester.assert_nonlocal_syntax_parses(source)
            nonlocal_names = tester.get_nonlocal_names(source)
            assert len(nonlocal_names) >= 1, f"Should parse nonlocal syntax: {source}"
    
    def test_nonlocal_global_variable_restrictions(self, tester):
        """Test nonlocal with global variables"""
        # Language Reference: nonlocal cannot refer to global variables
        # Note: This is a runtime error, not syntax error
        global_variable_patterns = [
            """
global_var = "global"

def function():
    def inner():
        nonlocal global_var  # Runtime error but syntax valid
        global_var = "modified"
    return inner
""",
            """
MODULE_CONSTANT = 42

def outer():
    def inner():
        nonlocal MODULE_CONSTANT  # Runtime error but syntax valid
        MODULE_CONSTANT = 100
    return inner
"""
        ]
        
        for source in global_variable_patterns:
            # Should parse (syntax is valid), but would fail at runtime
            tree = tester.assert_nonlocal_syntax_parses(source)
            nonlocal_names = tester.get_nonlocal_names(source)
            assert len(nonlocal_names) >= 1, f"Should parse nonlocal syntax: {source}"


class TestSection713NonlocalInteractionPatterns:
    """Test nonlocal interaction with other language features."""
    
    def test_nonlocal_with_global_statements(self, tester):
        """Test nonlocal and global statement interaction"""
        # Language Reference: nonlocal and global can coexist
        nonlocal_global_patterns = [
            """
global_var = "global"

def outer():
    enclosing_var = "enclosing"
    
    def inner():
        global global_var
        nonlocal enclosing_var
        global_var = "modified global"
        enclosing_var = "modified enclosing"
    
    return inner
""",
            """
MODULE_STATE = {"count": 0}

def factory():
    local_state = {"value": 42}
    
    def worker():
        global MODULE_STATE
        nonlocal local_state
        MODULE_STATE["count"] += 1
        local_state["value"] *= 2
        return MODULE_STATE, local_state
    
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
        
        for source in nonlocal_global_patterns:
            tree = tester.assert_nonlocal_syntax_parses(source)
            nonlocal_names = tester.get_nonlocal_names(source)
            assert len(nonlocal_names) >= 1, f"Should have nonlocal variables: {source}"
            
            # Should also have global statements
            global_nodes = [node for node in ast.walk(tree) if isinstance(node, ast.Global)]
            assert len(global_nodes) >= 1, f"Should have global statements: {source}"
    
    def test_nonlocal_with_default_arguments(self, tester):
        """Test nonlocal in functions with default arguments"""
        # Language Reference: nonlocal works with various function features
        default_argument_patterns = [
            """
def factory(initial_value=0):
    state = initial_value
    
    def updater(increment=1):
        nonlocal state
        state += increment
        return state
    
    return updater
""",
            """
def create_formatter(prefix="Result"):
    format_string = f"{prefix}: %s"
    
    def format_value(value, suffix=""):
        nonlocal format_string
        if suffix:
            format_string = f"{prefix}: %s {suffix}"
        return format_string % value
    
    return format_value
""",
            """
def range_checker(min_val=0, max_val=100):
    valid_count = 0
    
    def check(value, update_count=True):
        nonlocal valid_count
        is_valid = min_val <= value <= max_val
        if update_count and is_valid:
            valid_count += 1
        return is_valid, valid_count
    
    return check
"""
        ]
        
        for source in default_argument_patterns:
            tree = tester.assert_nonlocal_syntax_parses(source)
            nonlocal_names = tester.get_nonlocal_names(source)
            assert len(nonlocal_names) >= 1, f"Should have nonlocal variables: {source}"
    
    def test_nonlocal_with_exception_handling(self, tester):
        """Test nonlocal in exception handling contexts"""
        # Language Reference: nonlocal works in try/except/finally blocks
        exception_handling_patterns = [
            """
def error_tracker():
    error_count = 0
    last_error = None
    
    def risky_operation():
        nonlocal error_count, last_error
        try:
            # Simulate risky operation
            result = 1 / 0
        except ZeroDivisionError as e:
            error_count += 1
            last_error = str(e)
            return None
        finally:
            # Cleanup could also use nonlocal
            pass
        return result
    
    return risky_operation
""",
            """
def retry_mechanism(max_attempts=3):
    attempt_count = 0
    success_count = 0
    
    def attempt_operation(operation):
        nonlocal attempt_count, success_count
        for i in range(max_attempts):
            try:
                attempt_count += 1
                result = operation()
                success_count += 1
                return result
            except Exception:
                if i == max_attempts - 1:
                    raise
        return None
    
    return attempt_operation
""",
            """
def resource_manager():
    resource_count = 0
    active_resources = []
    
    def with_resource(resource_id):
        nonlocal resource_count, active_resources
        try:
            resource_count += 1
            active_resources.append(resource_id)
            yield resource_id
        finally:
            active_resources.remove(resource_id)
            resource_count -= 1
    
    return with_resource
"""
        ]
        
        for source in exception_handling_patterns:
            tree = tester.assert_nonlocal_syntax_parses(source)
            nonlocal_names = tester.get_nonlocal_names(source)
            assert len(nonlocal_names) >= 1, f"Should have nonlocal variables: {source}"


class TestSection713NonlocalASTStructure:
    """Test nonlocal AST structure validation."""
    
    def test_nonlocal_ast_node_structure(self, tester):
        """Test Nonlocal AST node structure"""
        # Language Reference: AST structure for nonlocal statements
        nonlocal_ast_cases = [
            """
def outer():
    x = 10
    def inner():
        nonlocal x
        x = 20
    return inner
""",
            """
def outer():
    a, b, c = 1, 2, 3
    def inner():
        nonlocal a, b, c
        a = b = c = 0
    return inner
"""
        ]
        
        for source in nonlocal_ast_cases:
            tree = tester.assert_nonlocal_syntax_parses(source)
            nonlocal_nodes = tester.get_nonlocal_statements(source)
            assert len(nonlocal_nodes) >= 1, f"Should have nonlocal nodes: {source}"
            
            for nonlocal_node in nonlocal_nodes:
                # Should have names attribute
                assert hasattr(nonlocal_node, 'names'), "Nonlocal should have 'names' attribute"
                assert isinstance(nonlocal_node.names, list), "names should be list"
                assert len(nonlocal_node.names) >= 1, "Should have at least one name"
                
                # Each name should be a string
                for name in nonlocal_node.names:
                    assert isinstance(name, str), "Nonlocal name should be string"
    
    def test_nonlocal_statement_positioning(self, tester):
        """Test nonlocal statement positioning in AST"""
        # Language Reference: nonlocal statements can appear anywhere in function
        positioning_cases = [
            """
def outer():
    x = 10
    def inner():
        nonlocal x  # At beginning
        x = 20
        return x
    return inner
""",
            """
def outer():
    x = 10
    def inner():
        y = 5
        nonlocal x  # In middle
        x = y + 10
        return x
    return inner
""",
            """
def outer():
    x = 10
    def inner():
        y = 5
        z = y * 2
        nonlocal x  # Towards end
        x = z
    return inner
"""
        ]
        
        for source in positioning_cases:
            tree = tester.assert_nonlocal_syntax_parses(source)
            nonlocal_nodes = tester.get_nonlocal_statements(source)
            assert len(nonlocal_nodes) == 1, f"Should have one nonlocal statement: {source}"
    
    def test_multiple_nonlocal_statements_ast(self, tester):
        """Test multiple nonlocal statements in AST"""
        # Language Reference: multiple nonlocal statements create multiple AST nodes
        multiple_statement_source = """
def outer():
    a, b, c = 1, 2, 3
    def inner():
        nonlocal a
        nonlocal b, c
        a = 10
        b = 20
        c = 30
    return inner
"""
        
        tree = tester.assert_nonlocal_syntax_parses(multiple_statement_source)
        nonlocal_nodes = tester.get_nonlocal_statements(multiple_statement_source)
        assert len(nonlocal_nodes) == 2, "Should have two nonlocal statements"
        
        # First statement should have one name
        assert len(nonlocal_nodes[0].names) == 1, "First statement should have one name"
        assert nonlocal_nodes[0].names[0] == "a", "First statement should declare 'a'"
        
        # Second statement should have two names  
        assert len(nonlocal_nodes[1].names) == 2, "Second statement should have two names"
        assert "b" in nonlocal_nodes[1].names, "Second statement should declare 'b'"
        assert "c" in nonlocal_nodes[1].names, "Second statement should declare 'c'"


class TestSection713CrossImplementationCompatibility:
    """Test cross-implementation compatibility for nonlocal statements."""
    
    def test_nonlocal_ast_consistency(self, tester):
        """Test nonlocal AST consistency across implementations"""
        # Language Reference: nonlocal AST should be consistent
        consistency_test_cases = [
            """
def counter():
    count = 0
    def increment():
        nonlocal count
        count += 1
        return count
    return increment
""",
            """
def state_machine():
    state = "initial"
    def transition(new_state):
        nonlocal state
        old_state = state
        state = new_state
        return old_state, new_state
    return transition
""",
            """
def accumulator():
    total = 0
    count = 0
    def add(value):
        nonlocal total, count
        total += value
        count += 1
        return total / count if count > 0 else 0
    return add
"""
        ]
        
        for source in consistency_test_cases:
            tree = tester.assert_nonlocal_syntax_parses(source)
            
            # Should have consistent nonlocal structure
            nonlocal_nodes = tester.get_nonlocal_statements(source)
            assert len(nonlocal_nodes) >= 1, f"Should have nonlocal statements: {source}"
            
            for nonlocal_node in nonlocal_nodes:
                assert hasattr(nonlocal_node, 'names'), "Should have names attribute"
                assert len(nonlocal_node.names) >= 1, "Should have variable names"
    
    def test_comprehensive_nonlocal_patterns(self, tester):
        """Test comprehensive real-world nonlocal patterns"""
        # Language Reference: complex nonlocal usage scenarios
        comprehensive_patterns = [
            """
# Event system with nonlocal state
def create_event_system():
    listeners = {}
    event_count = 0
    
    def add_listener(event_type, callback):
        nonlocal listeners
        if event_type not in listeners:
            listeners[event_type] = []
        listeners[event_type].append(callback)
    
    def emit_event(event_type, data=None):
        nonlocal event_count
        event_count += 1
        if event_type in listeners:
            for callback in listeners[event_type]:
                callback(data)
    
    def get_stats():
        return {"listeners": len(listeners), "events_emitted": event_count}
    
    return add_listener, emit_event, get_stats
""",
            """
# Cache with nonlocal state management
def create_cache(max_size=100):
    cache = {}
    access_count = {}
    total_requests = 0
    cache_hits = 0
    
    def get(key):
        nonlocal total_requests, cache_hits, access_count
        total_requests += 1
        access_count[key] = access_count.get(key, 0) + 1
        
        if key in cache:
            cache_hits += 1
            return cache[key]
        return None
    
    def put(key, value):
        nonlocal cache
        if len(cache) >= max_size:
            # Simple LRU: remove least accessed
            least_key = min(access_count.keys(), key=lambda k: access_count[k])
            del cache[least_key]
            del access_count[least_key]
        cache[key] = value
    
    def stats():
        hit_rate = cache_hits / total_requests if total_requests > 0 else 0
        return {"hit_rate": hit_rate, "size": len(cache), "requests": total_requests}
    
    return get, put, stats
"""
        ]
        
        for source in comprehensive_patterns:
            tree = tester.assert_nonlocal_syntax_parses(source)
            
            # Should have multiple nonlocal usages
            nonlocal_names = tester.get_nonlocal_names(source)
            assert len(nonlocal_names) >= 2, f"Should have nonlocal variables: {source}"
    
    def test_nonlocal_introspection(self, tester):
        """Test ability to analyze nonlocal statements programmatically"""
        # Test programmatic analysis of nonlocal structure
        introspection_source = """
def complex_closure():
    state_a = "initial_a"
    state_b = 42
    counters = {"x": 0, "y": 0}
    
    def inner_function():
        nonlocal state_a, state_b
        nonlocal counters
        
        state_a = "modified"
        state_b += 1
        counters["x"] += 1
        
        def deeper_function():
            nonlocal state_a
            state_a = "deeply modified"
        
        return deeper_function
    
    return inner_function
"""
        
        tree = tester.assert_nonlocal_syntax_parses(introspection_source)
        
        # Should identify all nonlocal statements
        nonlocal_nodes = tester.get_nonlocal_statements(introspection_source)
        assert len(nonlocal_nodes) >= 2, "Should have multiple nonlocal statements"
        
        # Should identify all nonlocal variable names
        nonlocal_names = tester.get_nonlocal_names(introspection_source)
        assert len(nonlocal_names) >= 4, "Should have multiple nonlocal variables"
        
        # Should detect nested function structure
        depth = tester.get_function_nesting_depth(introspection_source)
        assert depth >= 3, "Should have deep function nesting"
        
        # Should identify specific variable names
        assert "state_a" in nonlocal_names, "Should identify state_a as nonlocal"
        assert "state_b" in nonlocal_names, "Should identify state_b as nonlocal"
        assert "counters" in nonlocal_names, "Should identify counters as nonlocal"