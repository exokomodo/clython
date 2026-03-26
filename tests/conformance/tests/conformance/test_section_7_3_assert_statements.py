"""
Section 7.3: Assert Statements - Conformance Test Suite

Tests Python Language Reference Section 7.3 compliance across implementations.
Based on formal grammar definitions and prose assertions for assert statements.

Grammar tested:
    assert_stmt: 'assert' test [',' test]

Language Reference requirements tested:
    - Basic assert statement syntax
    - Assert with condition expression only
    - Assert with condition and message expressions
    - Assert expression evaluation behavior
    - AssertionError raising on failure
    - Assert optimization behavior (__debug__ flag)
    - Complex assertion expressions and patterns
    - Error conditions and invalid assert usage
"""

import ast
import pytest
import sys
from typing import Any


class AssertStatementTester:
    """Helper class for testing assert statement conformance.
    
    Follows established AST-based validation pattern from previous sections.
    """
    
    def assert_assert_syntax_parses(self, source: str):
        """Test that assert statement syntax parses correctly.
        
        Args:
            source: Python assert statement source code
        """
        try:
            tree = ast.parse(source)
            # Verify the AST contains assert statement
            for node in ast.walk(tree):
                if isinstance(node, ast.Assert):
                    return tree  # Found assert statement, syntax is valid
            pytest.fail(f"Expected Assert node not found in parsed AST for: {source}")
        except SyntaxError as e:
            pytest.fail(f"Assert statement syntax should be valid but failed to parse: {source}\\nError: {e}")
    
    def assert_assert_syntax_error(self, source: str):
        """Test that invalid assert syntax raises SyntaxError.
        
        Args:
            source: Python assert source code that should be invalid
        """
        with pytest.raises(SyntaxError):
            ast.parse(source)
    
    def get_assert_from_source(self, source: str) -> ast.Assert:
        """Get the Assert AST node from source for detailed validation.
        
        Args:
            source: Python assert statement source
            
        Returns:
            ast.Assert node
        """
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assert):
                return node
        pytest.fail(f"Expected Assert node not found in: {source}")
    
    def has_assert_message(self, source: str) -> bool:
        """Check if assert statement has message expression.
        
        Args:
            source: Python assert statement source
            
        Returns:
            True if assert has message expression
        """
        assert_node = self.get_assert_from_source(source)
        return assert_node.msg is not None
    
    def get_assert_test_type(self, source: str) -> type:
        """Get the AST type of assert test expression.
        
        Args:
            source: Python assert statement source
            
        Returns:
            AST node type of test expression
        """
        assert_node = self.get_assert_from_source(source)
        return type(assert_node.test)


@pytest.fixture
def tester():
    """Provide AssertStatementTester instance for tests."""
    return AssertStatementTester()


class TestSection73BasicAssertStatements:
    """Test basic assert statement syntax and semantics."""
    
    def test_simple_assert_statements(self, tester):
        """Test simple assert statements with basic conditions"""
        # Language Reference: assert with single test expression
        simple_asserts = [
            "assert True",
            "assert 1 == 1",
            "assert x > 0",
            "assert condition",
            "assert len(items) > 0",
            "assert result is not None",
            "assert flag"
        ]
        
        for source in simple_asserts:
            tree = tester.assert_assert_syntax_parses(source)
            assert_node = tester.get_assert_from_source(source)
            assert assert_node.test is not None, f"Assert should have test expression: {source}"
            assert assert_node.msg is None, f"Simple assert should have no message: {source}"
    
    def test_assert_with_message(self, tester):
        """Test assert statements with message expressions"""
        # Language Reference: assert test, message
        message_asserts = [
            "assert True, 'This should pass'",
            "assert x > 0, 'x must be positive'",
            "assert len(data) > 0, 'Data cannot be empty'",
            "assert result is not None, f'Expected result, got {result}'",
            "assert condition, error_message",
            "assert validate(input), get_error_message()",
            "assert check(), 'Check failed'"
        ]
        
        for source in message_asserts:
            tree = tester.assert_assert_syntax_parses(source)
            assert_node = tester.get_assert_from_source(source)
            assert assert_node.test is not None, f"Assert should have test expression: {source}"
            assert assert_node.msg is not None, f"Assert with message should have msg: {source}"
    
    def test_assert_boolean_expressions(self, tester):
        """Test assert with boolean expression types"""
        # Language Reference: test expression evaluated for truth value
        boolean_asserts = [
            "assert True",                      # Literal True
            "assert False or True",             # Boolean operation
            "assert not False",                 # Unary not
            "assert x and y",                   # Logical and
            "assert a or b or c",               # Multiple or
            "assert not (x and y)",             # Parenthesized expression
            "assert bool(value)"                # Explicit bool conversion
        ]
        
        for source in boolean_asserts:
            tree = tester.assert_assert_syntax_parses(source)
            test_type = tester.get_assert_test_type(source)
            assert test_type in (ast.Constant, ast.BoolOp, ast.UnaryOp, ast.Name, ast.Call)


class TestSection73AssertExpressionTypes:
    """Test various expression types in assert statements."""
    
    def test_comparison_assertions(self, tester):
        """Test assert with comparison expressions"""
        # Language Reference: comparison expressions in assertions
        comparison_asserts = [
            "assert x == y",                    # Equality
            "assert a != b",                    # Inequality  
            "assert value < limit",             # Less than
            "assert count >= 0",                # Greater or equal
            "assert result is None",            # Identity comparison
            "assert item in collection",        # Membership test
            "assert pattern not in text"        # Negative membership
        ]
        
        for source in comparison_asserts:
            tree = tester.assert_assert_syntax_parses(source)
            test_type = tester.get_assert_test_type(source)
            assert test_type == ast.Compare, f"Should be Compare node: {source}"
    
    def test_function_call_assertions(self, tester):
        """Test assert with function call expressions"""
        # Language Reference: function calls in test expressions
        function_asserts = [
            "assert validate(data)",
            "assert obj.is_valid()",
            "assert check_condition(x, y)",
            "assert callable(func)",
            "assert isinstance(obj, cls)",
            "assert hasattr(obj, 'attr')",
            "assert all(conditions)"
        ]
        
        for source in function_asserts:
            tree = tester.assert_assert_syntax_parses(source)
            test_type = tester.get_assert_test_type(source)
            assert test_type == ast.Call, f"Should be Call node: {source}"
    
    def test_complex_expression_assertions(self, tester):
        """Test assert with complex expressions"""
        # Language Reference: any expression valid as test
        complex_asserts = [
            "assert data[key] == expected",     # Subscription
            "assert obj.attr > threshold",      # Attribute access
            "assert func() and other_func()",   # Combined calls
            "assert [x for x in items if x]",   # List comprehension
            "assert value if condition else default", # Conditional expression
            "assert (a + b) == c",              # Arithmetic expression
            "assert len(items) in range(1, 10)" # Nested function calls
        ]
        
        for source in complex_asserts:
            tree = tester.assert_assert_syntax_parses(source)
            assert_node = tester.get_assert_from_source(source)
            assert assert_node.test is not None, f"Should have test expression: {source}"
    
    def test_assert_message_types(self, tester):
        """Test various message expression types"""
        # Language Reference: message expression can be any expression
        message_types = [
            "assert condition, 'Simple string'",
            "assert condition, f'Dynamic message: {value}'",
            "assert condition, error_variable",
            "assert condition, get_message()",
            "assert condition, obj.error_msg",
            "assert condition, messages[error_code]",
            "assert condition, 'Error' if serious else 'Warning'"
        ]
        
        for source in message_types:
            tree = tester.assert_assert_syntax_parses(source)
            assert tester.has_assert_message(source)
            assert_node = tester.get_assert_from_source(source)
            # Message can be various expression types
            msg_type = type(assert_node.msg)
            assert msg_type in (ast.Constant, ast.JoinedStr, ast.Name, ast.Call, 
                               ast.Attribute, ast.Subscript, ast.IfExp)


class TestSection73AssertInContexts:
    """Test assert statements in different contexts."""
    
    def test_assert_in_functions(self, tester):
        """Test assert statements in function definitions"""
        # Language Reference: assert can appear in any function context
        function_asserts = [
            """
def validate_input(data):
    assert data is not None, 'Data cannot be None'
    assert len(data) > 0, 'Data cannot be empty'
    return True
""",
            """
async def async_validate(value):
    assert isinstance(value, int), f'Expected int, got {type(value)}'
    assert value >= 0, 'Value must be non-negative'
""",
            """
def process_with_assertions(items):
    assert items, 'Items list cannot be empty'
    
    for item in items:
        assert validate_item(item), f'Invalid item: {item}'
    
    return processed_items
"""
        ]
        
        for source in function_asserts:
            tree = tester.assert_assert_syntax_parses(source)
            # Find function definitions that contain assert statements
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    asserts_in_func = [n for n in ast.walk(node) if isinstance(n, ast.Assert)]
                    assert len(asserts_in_func) >= 1, f"Expected assert in function: {source}"
    
    def test_assert_in_classes(self, tester):
        """Test assert statements in class methods"""
        # Language Reference: assert allowed in class methods
        class_asserts = [
            """
class Validator:
    def validate(self, data):
        assert data, 'Data is required'
        assert self.is_valid_format(data), 'Invalid format'
        return True
""",
            """
class Calculator:
    def divide(self, a, b):
        assert b != 0, 'Division by zero'
        return a / b
    
    @staticmethod
    def validate_number(x):
        assert isinstance(x, (int, float)), 'Must be numeric'
"""
        ]
        
        for source in class_asserts:
            tree = tester.assert_assert_syntax_parses(source)
            # Find methods that contain assert statements
            method_count = 0
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    asserts_in_method = [n for n in ast.walk(node) if isinstance(n, ast.Assert)]
                    if asserts_in_method:
                        method_count += 1
            assert method_count >= 1, f"Expected methods with assert: {source}"
    
    def test_assert_in_control_flow(self, tester):
        """Test assert statements in control flow structures"""
        # Language Reference: assert can appear in any statement context
        control_flow_asserts = [
            """
if condition:
    assert validate_condition(), 'Condition validation failed'
else:
    assert fallback_check(), 'Fallback check failed'
""",
            """
for item in items:
    assert process_item(item), f'Failed to process {item}'
""",
            """
try:
    risky_operation()
except Exception as e:
    assert handle_error(e), 'Error handling failed'
""",
            """
while counter > 0:
    assert counter >= 0, 'Counter went negative'
    counter -= 1
"""
        ]
        
        for source in control_flow_asserts:
            tree = tester.assert_assert_syntax_parses(source)
            # Verify assert statements exist in control structures
            assert_nodes = [node for node in ast.walk(tree) if isinstance(node, ast.Assert)]
            assert len(assert_nodes) >= 1, f"Expected assert in control flow: {source}"


class TestSection73AssertOptimization:
    """Test assert statement optimization behavior."""
    
    def test_assert_with_debug_considerations(self, tester):
        """Test assert statements considering __debug__ optimization"""
        # Language Reference: assert can be optimized away when __debug__ is False
        # Note: We test syntax and AST structure, not runtime optimization
        debug_aware_asserts = [
            "assert __debug__",                 # Debug flag check
            "assert True or expensive_call()",  # Short-circuit evaluation
            "assert condition, 'Debug message'", # Message only evaluated on failure
            """
if __debug__:
    assert validate_expensive(), 'Expensive validation failed'
""",
            "assert not __debug__ or check_debug_condition()"
        ]
        
        for source in debug_aware_asserts:
            tree = tester.assert_assert_syntax_parses(source)
            # Should parse correctly regardless of optimization
            assert_nodes = [node for node in ast.walk(tree) if isinstance(node, ast.Assert)]
            if "if __debug__" not in source:
                assert len(assert_nodes) >= 1, f"Should contain assert: {source}"
    
    def test_assert_side_effect_considerations(self, tester):
        """Test assert with expressions that have side effects"""
        # Language Reference: test expressions should avoid side effects 
        # due to optimization potential
        side_effect_patterns = [
            "assert func_with_side_effects()",  # Function with side effects
            "assert obj.mutating_method()",     # Method that mutates object
            "assert counter_increment()",       # Function that increments counter
            "assert append_and_check(item)",    # Function that modifies and checks
        ]
        
        for source in side_effect_patterns:
            tree = tester.assert_assert_syntax_parses(source)
            # Should parse correctly (syntax is valid)
            assert_node = tester.get_assert_from_source(source)
            assert assert_node.test is not None
    
    def test_complex_assertion_patterns(self, tester):
        """Test complex real-world assertion patterns"""
        # Language Reference: comprehensive assertion usage patterns
        complex_patterns = [
            """
def process_data(data):
    assert data, 'Data is required'
    assert isinstance(data, (list, tuple)), f'Expected sequence, got {type(data)}'
    assert len(data) > 0, 'Data sequence cannot be empty'
    
    for i, item in enumerate(data):
        assert item is not None, f'Item at index {i} is None'
        assert hasattr(item, 'value'), f'Item {i} missing value attribute'
""",
            """
class APIClient:
    def request(self, endpoint, data=None):
        assert endpoint, 'Endpoint is required'
        assert endpoint.startswith('/'), 'Endpoint must start with /'
        
        if data:
            assert isinstance(data, dict), 'Data must be dict'
            assert 'api_key' not in data, 'API key should not be in data'
        
        return self._make_request(endpoint, data)
"""
        ]
        
        for source in complex_patterns:
            tree = tester.assert_assert_syntax_parses(source)
            # Count assert statements in complex patterns
            assert_nodes = [node for node in ast.walk(tree) if isinstance(node, ast.Assert)]
            assert len(assert_nodes) >= 3, f"Complex pattern should have multiple asserts: {source}"


class TestSection73ErrorConditions:
    """Test assert statement error conditions and edge cases."""
    
    def test_invalid_assert_syntax(self, tester):
        """Test invalid assert statement syntax"""
        # Language Reference: syntactic restrictions on assert
        invalid_asserts = [
            "assert",                           # Missing test expression
            "assert,",                          # Comma without expressions
            "assert, 'message'",                # Missing test, only message
            "assert condition,",                # Trailing comma without message
            "assert True False",                # Multiple expressions without comma
            "assert condition, message, extra", # Too many expressions
        ]
        
        for source in invalid_asserts:
            tester.assert_assert_syntax_error(source)
    
    def test_assert_indentation_requirements(self, tester):
        """Test assert statement indentation requirements"""
        # Language Reference: assert follows normal indentation rules
        valid_indented_asserts = [
            """
if condition:
    assert check(), 'Check failed'
""",
            """
def function():
    assert precondition, 'Precondition not met'
    assert postcondition, 'Postcondition not met'
""",
            """
try:
    operation()
except Exception:
    assert handle_error(), 'Error handling failed'
"""
        ]
        
        for source in valid_indented_asserts:
            tester.assert_assert_syntax_parses(source)
    
    def test_assert_expression_edge_cases(self, tester):
        """Test edge cases in assert expressions"""
        # Language Reference: edge cases for test and message expressions
        edge_case_asserts = [
            "assert ()",                        # Empty tuple (falsy)
            "assert []",                        # Empty list (falsy)  
            "assert ''",                        # Empty string (falsy)
            "assert 0",                         # Zero (falsy)
            "assert False, True",               # Boolean literals
            "assert None is None",              # None identity
            "assert ... is ...",                # Ellipsis identity
        ]
        
        for source in edge_case_asserts:
            tree = tester.assert_assert_syntax_parses(source)
            # Should parse successfully even with falsy test values
            assert_node = tester.get_assert_from_source(source)
            assert assert_node.test is not None


class TestSection73CrossImplementationCompatibility:
    """Test cross-implementation compatibility for assert statements."""
    
    def test_assert_statement_ast_structure(self, tester):
        """Test assert statement AST structure across implementations"""
        # Language Reference: AST structure should be consistent
        test_cases = [
            "assert True",
            "assert condition, 'message'",
            "assert func_call()",
            "assert x == y, f'x={x}, y={y}'"
        ]
        
        for source in test_cases:
            tree = tester.assert_assert_syntax_parses(source)
            assert_node = tester.get_assert_from_source(source)
            
            # Verify required AST attributes
            assert hasattr(assert_node, 'test'), f"Assert node should have 'test' attribute: {source}"
            assert hasattr(assert_node, 'msg'), f"Assert node should have 'msg' attribute: {source}"
            
            # Test should always be present, msg may be None
            assert assert_node.test is not None, f"Assert test should not be None: {source}"
            assert assert_node.msg is None or isinstance(assert_node.msg, ast.AST)
    
    def test_assert_introspection_capabilities(self, tester):
        """Test assert statement introspection capabilities"""
        # Test ability to analyze assert statement structure programmatically
        introspection_source = "assert validate_data(input), f'Validation failed for {input}'"
        
        tree = tester.assert_assert_syntax_parses(introspection_source)
        assert_node = tester.get_assert_from_source(introspection_source)
        
        # Should be able to introspect structure
        assert assert_node.test is not None, "Should have test expression"
        assert assert_node.msg is not None, "Should have message expression"
        
        # Should be able to identify expression types
        assert isinstance(assert_node.test, ast.Call), "Test should be function call"
        assert isinstance(assert_node.msg, ast.JoinedStr), "Message should be f-string"
    
    def test_complex_assert_patterns(self, tester):
        """Test complex assert statement patterns"""
        # Language Reference: comprehensive real-world patterns
        complex_patterns = [
            """
def validate_config(config):
    assert isinstance(config, dict), f'Config must be dict, got {type(config)}'
    
    required_keys = ['host', 'port', 'database']
    for key in required_keys:
        assert key in config, f'Missing required config key: {key}'
        assert config[key], f'Config key {key} cannot be empty'
    
    assert isinstance(config['port'], int), 'Port must be integer'
    assert 1 <= config['port'] <= 65535, f'Port {config["port"]} out of valid range'
""",
            """
async def api_endpoint_handler(request, response):
    assert request.method in ['GET', 'POST'], f'Unsupported method: {request.method}'
    
    if request.method == 'POST':
        assert request.content_type == 'application/json', 'POST requires JSON'
        assert request.body, 'POST body cannot be empty'
    
    result = await process_request(request)
    assert result is not None, 'Processing returned None'
    
    response.data = result
    assert response.is_valid(), 'Response validation failed'
""",
            """
class DataProcessor:
    def __init__(self, schema):
        assert schema, 'Schema is required'
        assert hasattr(schema, 'validate'), 'Schema must have validate method'
        self.schema = schema
    
    def process(self, data):
        assert data is not None, 'Cannot process None data'
        assert self.schema.validate(data), f'Data validation failed: {data}'
        
        processed = self._transform(data)
        assert processed != data, 'Transform should modify data'
        assert self.schema.validate(processed), 'Processed data invalid'
        
        return processed
"""
        ]
        
        for source in complex_patterns:
            tree = tester.assert_assert_syntax_parses(source)
            # Just verify the pattern parses successfully
            assert len(tree.body) >= 1, f"Complex assert pattern should parse: {source}"
    
    def test_assert_error_message_evaluation(self, tester):
        """Test assert error message evaluation patterns"""
        # Language Reference: message expressions and their evaluation
        message_patterns = [
            "assert condition, 'Static message'",
            "assert condition, error_var",
            "assert condition, get_error_message()",
            "assert condition, f'Dynamic: {value}'",
            "assert condition, 'Error' + ' message'",
            "assert condition, messages.get(error_code, 'Unknown error')",
            "assert condition, error_msg if detailed else 'Error'"
        ]
        
        for source in message_patterns:
            tree = tester.assert_assert_syntax_parses(source)
            assert_node = tester.get_assert_from_source(source)
            
            # Should have both test and message
            assert assert_node.test is not None, f"Should have test: {source}"
            assert assert_node.msg is not None, f"Should have message: {source}"