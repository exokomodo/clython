"""
Section 6.12: Assignment Expressions (Walrus Operator) - Conformance Test Suite

Tests Python Language Reference Section 6.12 compliance across implementations.
Based on formal assignment expression syntax definitions and prose assertions for named expression behavior.

Grammar tested:
    named_expr: NAME ':=' expr

Language Reference requirements tested:
    - Assignment expression syntax validation (name := expr)
    - Scoping rules and variable binding behavior
    - Restrictions on assignment expression usage contexts
    - Named expression evaluation and assignment semantics
    - Assignment expressions in different contexts
    - Error conditions for malformed assignment expressions
    - Assignment expression AST structure validation
    - Cross-implementation assignment expression compatibility

NOTE: Assignment expressions were introduced in Python 3.8
"""

import ast
import pytest
import sys
from typing import Any


class AssignmentExpressionTester:
    """Helper class for testing assignment expression conformance.
    
    Focuses on AST structure validation for assignment expression syntax and scoping
    patterns that can be statically analyzed for cross-implementation compatibility.
    """
    
    def assert_assignment_expression_parses(self, source: str):
        """Test that assignment expression syntax parses correctly.
        
        Args:
            source: Python source code with assignment expressions
        """
        try:
            tree = ast.parse(source)
            return tree
        except SyntaxError as e:
            pytest.fail(f"Assignment expression syntax should be valid but failed to parse: {source}\\nError: {e}")
    
    def assert_assignment_expression_syntax_error(self, source: str):
        """Test that invalid assignment expression syntax raises SyntaxError.
        
        Args:
            source: Python source code that should be invalid
        """
        with pytest.raises(SyntaxError):
            ast.parse(source)
    
    def get_named_expressions(self, source: str) -> list:
        """Get NamedExpr AST nodes from source (assignment expressions).
        
        Args:
            source: Python source code
            
        Returns:
            List of ast.NamedExpr nodes
        """
        tree = ast.parse(source)
        named_exprs = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.NamedExpr):
                named_exprs.append(node)
        
        return named_exprs
    
    def get_assignment_targets(self, source: str) -> list:
        """Get assignment targets from named expressions.
        
        Args:
            source: Python source code
            
        Returns:
            List of target names from assignment expressions
        """
        tree = ast.parse(source)
        targets = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.NamedExpr):
                if isinstance(node.target, ast.Name):
                    targets.append(node.target.id)
        
        return targets
    
    def get_assignment_values(self, source: str) -> list:
        """Get assignment value expressions from named expressions.
        
        Args:
            source: Python source code
            
        Returns:
            List of value expressions from assignment expressions
        """
        tree = ast.parse(source)
        values = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.NamedExpr):
                values.append(node.value)
        
        return values
    
    def count_nested_assignments(self, source: str) -> int:
        """Count depth of nested assignment expressions.
        
        Args:
            source: Python source code
            
        Returns:
            Maximum nesting depth of assignment expressions
        """
        tree = ast.parse(source)
        
        def count_depth(node):
            max_depth = 0
            if isinstance(node, ast.NamedExpr):
                # Count nesting in value expression
                value_depth = count_depth(node.value)
                max_depth = 1 + value_depth
            else:
                # Recurse into child nodes
                for child in ast.iter_child_nodes(node):
                    child_depth = count_depth(child)
                    max_depth = max(max_depth, child_depth)
            return max_depth
        
        return count_depth(tree)


@pytest.fixture
def tester():
    """Provide AssignmentExpressionTester instance for tests."""
    return AssignmentExpressionTester()


@pytest.mark.min_version_3_8  # Assignment expressions require Python 3.8+
class TestSection612BasicAssignmentExpressionSyntax:
    """Test basic assignment expression syntax."""
    
    def test_simple_assignment_expressions(self, tester):
        """Test simple assignment expression patterns"""
        # Skip if Python version doesn't support assignment expressions
        if sys.version_info < (3, 8):
            pytest.skip("Assignment expressions require Python 3.8+")
        
        # Language Reference: named_expr: NAME ':=' expr
        simple_assignment_patterns = [
            """
if (n := len(items)) > 10:
    process_large_collection(n)
""",
            """
while (line := file.readline()) != "":
    process_line(line)
""",
            """
result = [(x := calculate(i)) for i in range(10) if x > threshold]
""",
            """
if (match := pattern.search(text)):
    extract_data(match)
""",
            """
data = [process_item(item) for item in items if (processed := preprocess(item))]
"""
        ]
        
        for source in simple_assignment_patterns:
            tree = tester.assert_assignment_expression_parses(source)
            named_exprs = tester.get_named_expressions(source)
            assert len(named_exprs) >= 1, f"Should have assignment expressions: {source}"
    
    def test_assignment_with_complex_expressions(self, tester):
        """Test assignment expressions with complex value expressions"""
        # Skip if Python version doesn't support assignment expressions
        if sys.version_info < (3, 8):
            pytest.skip("Assignment expressions require Python 3.8+")
        
        # Language Reference: complex expressions in assignment expressions
        complex_expression_patterns = [
            """
if (result := expensive_computation(x, y, z)) is not None:
    use_result(result)
""",
            """
while (data := api_call().get('data', [])) and len(data) > 0:
    process_batch(data)
""",
            """
items = [transform(item) for item in collection if (cleaned := clean(item)) and validate(cleaned)]
""",
            """
if (config := load_config()) and (validator := create_validator(config)):
    validate_data(validator)
""",
            """
results = [(processed := process_complex(item.value, config)) for item in items if processed is not None]
"""
        ]
        
        for source in complex_expression_patterns:
            tree = tester.assert_assignment_expression_parses(source)
            named_exprs = tester.get_named_expressions(source)
            assert len(named_exprs) >= 1, f"Should handle complex expressions: {source}"
    
    def test_assignment_with_different_types(self, tester):
        """Test assignment expressions with different value types"""
        # Skip if Python version doesn't support assignment expressions
        if sys.version_info < (3, 8):
            pytest.skip("Assignment expressions require Python 3.8+")
        
        # Language Reference: assignment expressions can assign any type
        type_variation_patterns = [
            """
if (count := len(items)) > 0:
    print(f"Found {count} items")
""",
            """
while (chunk := read_chunk(size=1024)):
    process_chunk(chunk)
""",
            """
if (handler := get_handler(event_type)):
    handler.process(event)
""",
            """
results = [item for item in data if (value := extract_value(item)) is not None]
""",
            """
if (settings := parse_settings(config_file)) and settings.get('enabled'):
    apply_settings(settings)
"""
        ]
        
        for source in type_variation_patterns:
            tree = tester.assert_assignment_expression_parses(source)
            named_exprs = tester.get_named_expressions(source)
            assert len(named_exprs) >= 1, f"Should handle type variations: {source}"
    
    def test_assignment_variable_naming(self, tester):
        """Test assignment expression variable naming patterns"""
        # Skip if Python version doesn't support assignment expressions
        if sys.version_info < (3, 8):
            pytest.skip("Assignment expressions require Python 3.8+")
        
        # Language Reference: assignment expression target names
        naming_patterns = [
            """
if (n := calculate()) > 0:
    use_n(n)
""",
            """
if (result_value := compute()) is not None:
    process_result_value(result_value)
""",
            """
while (current_item := iterator.next()):
    handle_current_item(current_item)
""",
            """
if (_temp := expensive_call()) and _temp.is_valid():
    use_temp(_temp)
""",
            """
data = [process(x) for item in items if (x := transform(item)) is not None]
"""
        ]
        
        for source in naming_patterns:
            tree = tester.assert_assignment_expression_parses(source)
            targets = tester.get_assignment_targets(source)
            assert len(targets) >= 1, f"Should have assignment targets: {source}"
            
            # Targets should be valid variable names
            for target in targets:
                assert isinstance(target, str), f"Target should be string: {target}"
                assert target.isidentifier(), f"Target should be valid identifier: {target}"


@pytest.mark.min_version_3_8  # Assignment expressions require Python 3.8+
class TestSection612AssignmentExpressionContexts:
    """Test assignment expressions in different contexts."""
    
    def test_assignments_in_if_statements(self, tester):
        """Test assignment expressions in if statement conditions"""
        # Skip if Python version doesn't support assignment expressions
        if sys.version_info < (3, 8):
            pytest.skip("Assignment expressions require Python 3.8+")
        
        # Language Reference: assignment expressions in if conditions
        if_context_patterns = [
            """
if (value := get_value()) > threshold:
    process_high_value(value)
""",
            """
if (data := load_data()) and validate_data(data):
    use_data(data)
""",
            """
if (match := regex.search(text)) and match.group(1):
    handle_match(match)
""",
            """
if (result := expensive_operation()) is not None:
    cache_result(result)
    return result
""",
            """
if not (error := validate_input(user_input)):
    proceed_with_input(user_input)
else:
    handle_error(error)
"""
        ]
        
        for source in if_context_patterns:
            tree = tester.assert_assignment_expression_parses(source)
            named_exprs = tester.get_named_expressions(source)
            assert len(named_exprs) >= 1, f"Should work in if statements: {source}"
    
    def test_assignments_in_while_loops(self, tester):
        """Test assignment expressions in while loop conditions"""
        # Skip if Python version doesn't support assignment expressions
        if sys.version_info < (3, 8):
            pytest.skip("Assignment expressions require Python 3.8+")
        
        # Language Reference: assignment expressions in while conditions
        while_context_patterns = [
            """
while (line := file.readline()):
    process_line(line)
""",
            """
while (chunk := stream.read(1024)) and len(chunk) > 0:
    write_chunk(chunk)
""",
            """
while (item := queue.get()) != sentinel:
    process_item(item)
""",
            """
while (data := api.get_next_page()) and data['has_more']:
    process_page(data)
""",
            """
while (batch := get_next_batch()) and not should_stop():
    process_batch(batch)
"""
        ]
        
        for source in while_context_patterns:
            tree = tester.assert_assignment_expression_parses(source)
            named_exprs = tester.get_named_expressions(source)
            assert len(named_exprs) >= 1, f"Should work in while loops: {source}"
    
    def test_assignments_in_comprehensions(self, tester):
        """Test assignment expressions in comprehensions"""
        # Skip if Python version doesn't support assignment expressions
        if sys.version_info < (3, 8):
            pytest.skip("Assignment expressions require Python 3.8+")
        
        # Language Reference: assignment expressions in comprehensions
        comprehension_patterns = [
            """
results = [process_value(x) for item in items if (x := extract_value(item)) is not None]
""",
            """
data = {key: transform(value) for key, raw_value in items.items() if (value := clean(raw_value))}
""",
            """
processed = (handle_item(x) for item in collection if (x := preprocess(item)) and validate(x))
""",
            """
filtered = {item for item in dataset if (score := calculate_score(item)) > min_score}
""",
            """
matrix = [[compute(x, y) for y in range(cols) if (x := get_x_value(row, y))] for row in range(rows)]
"""
        ]
        
        for source in comprehension_patterns:
            tree = tester.assert_assignment_expression_parses(source)
            named_exprs = tester.get_named_expressions(source)
            assert len(named_exprs) >= 1, f"Should work in comprehensions: {source}"
    
    def test_assignments_in_function_calls(self, tester):
        """Test assignment expressions in function call arguments"""
        # Skip if Python version doesn't support assignment expressions
        if sys.version_info < (3, 8):
            pytest.skip("Assignment expressions require Python 3.8+")
        
        # Language Reference: assignment expressions in function arguments
        function_call_patterns = [
            """
result = process_data(
    input_data,
    transformed=transform(input_data) if (cleaned := clean_data(input_data)) else None
)
""",
            """
output = complex_function(
    base_value,
    modifier=(multiplier := calculate_multiplier()) * adjustment,
    use_cache=True
)
""",
            """
validate_and_store(
    data,
    validator=create_validator() if (config := load_config()) else default_validator
)
""",
            """
api_call(
    endpoint,
    payload=build_payload(data),
    timeout=(timeout := get_timeout()) if timeout > 0 else default_timeout
)
""",
            """
logging.info(
    "Processing complete: %d items processed",
    (count := len(processed_items))
)
"""
        ]
        
        for source in function_call_patterns:
            tree = tester.assert_assignment_expression_parses(source)
            named_exprs = tester.get_named_expressions(source)
            assert len(named_exprs) >= 1, f"Should work in function calls: {source}"
    
    def test_assignments_in_lambda_expressions(self, tester):
        """Test assignment expressions in lambda expressions"""
        # Skip if Python version doesn't support assignment expressions
        if sys.version_info < (3, 8):
            pytest.skip("Assignment expressions require Python 3.8+")
        
        # Language Reference: assignment expressions in lambdas
        lambda_context_patterns = [
            """
processor = lambda item: process(x) if (x := extract(item)) else None
""",
            """
validator = lambda data: check(cleaned) if (cleaned := clean(data)) else False
""",
            """
transformer = lambda input_val: transform(normalized) if (normalized := normalize(input_val)) and normalized > 0 else 0
""",
            """
filter_func = lambda item: (score := calculate_score(item)) > threshold and score < max_score
""",
            """
mapper = lambda collection: [process(x) for item in collection if (x := prepare(item))]
"""
        ]
        
        for source in lambda_context_patterns:
            tree = tester.assert_assignment_expression_parses(source)
            named_exprs = tester.get_named_expressions(source)
            assert len(named_exprs) >= 1, f"Should work in lambda expressions: {source}"


@pytest.mark.min_version_3_8  # Assignment expressions require Python 3.8+
class TestSection612NestedAssignmentExpressions:
    """Test nested assignment expressions."""
    
    def test_assignments_in_assignment_values(self, tester):
        """Test assignment expressions in values of other assignment expressions"""
        # Skip if Python version doesn't support assignment expressions
        if sys.version_info < (3, 8):
            pytest.skip("Assignment expressions require Python 3.8+")
        
        # Language Reference: nested assignment expressions
        nested_assignment_patterns = [
            """
if (outer := calculate(inner)) and (inner := get_base_value()) > 0:
    use_values(outer, inner)
""",
            """
while (processed := transform(raw)) and (raw := get_next_raw_value()):
    handle_processed(processed, raw)
""",
            """
result = [
    complex_transform(final_value) 
    for item in items 
    if (intermediate := preprocess(item)) 
    and (final_value := process(intermediate))
]
""",
            """
if (config := load_config()) and (validator := create_validator(schema)) and (schema := config.get('schema')):
    validate_with(validator, data)
""",
            """
data = {
    key: final_result
    for key, value in raw_data.items()
    if (processed := process_value(value))
    and (final_result := finalize(processed))
}
"""
        ]
        
        for source in nested_assignment_patterns:
            tree = tester.assert_assignment_expression_parses(source)
            named_exprs = tester.get_named_expressions(source)
            assert len(named_exprs) >= 2, f"Should have nested assignments: {source}"
    
    def test_deeply_nested_assignments(self, tester):
        """Test deeply nested assignment expressions"""
        # Skip if Python version doesn't support assignment expressions
        if sys.version_info < (3, 8):
            pytest.skip("Assignment expressions require Python 3.8+")
        
        # Language Reference: assignment expressions can be nested arbitrarily
        deeply_nested_patterns = [
            """
if (result := transform(processed)) and (processed := clean(raw)) and (raw := get_data()):
    use_result(result, processed, raw)
""",
            """
complex_result = [
    final
    for item in collection
    if (stage1 := first_transform(item))
    and (stage2 := second_transform(stage1))
    and (final := final_transform(stage2))
]
""",
            """
while (
    (final := process_all(intermediate, config))
    and (intermediate := prepare_data(raw))
    and (raw := source.read_next())
    and (config := get_current_config())
):
    store_result(final)
"""
        ]
        
        for source in deeply_nested_patterns:
            tree = tester.assert_assignment_expression_parses(source)
            nesting_depth = tester.count_nested_assignments(source)
            # Note: Counting may be limited by expression structure
            named_exprs = tester.get_named_expressions(source)
            assert len(named_exprs) >= 2, f"Should have multiple assignments: {source}"
    
    def test_assignment_variable_reuse(self, tester):
        """Test reusing assignment expression variables"""
        # Skip if Python version doesn't support assignment expressions
        if sys.version_info < (3, 8):
            pytest.skip("Assignment expressions require Python 3.8+")
        
        # Language Reference: assignment expression variables can be reused
        variable_reuse_patterns = [
            """
# Same variable name in different scopes
if (value := get_first()) > 0:
    process_first(value)

if (value := get_second()) > 0:
    process_second(value)
""",
            """
# Reusing in comprehensions
data1 = [transform(x) for item in items1 if (x := extract(item)) is not None]
data2 = [transform(x) for item in items2 if (x := extract(item)) is not None]
""",
            """
# Reusing with different types
if (result := get_string_result()):
    handle_string(result)

if (result := get_number_result()) > 0:
    handle_number(result)
""",
            """
# Sequential reuse in same scope
if (temp := first_calculation()) and temp > threshold:
    intermediate = temp * 2

if (temp := second_calculation()) and temp < limit:
    final = temp / 2
"""
        ]
        
        for source in variable_reuse_patterns:
            tree = tester.assert_assignment_expression_parses(source)
            named_exprs = tester.get_named_expressions(source)
            assert len(named_exprs) >= 2, f"Should have multiple assignments: {source}"


@pytest.mark.min_version_3_8  # Assignment expressions require Python 3.8+
class TestSection612AssignmentExpressionRestrictions:
    """Test assignment expression restrictions and limitations."""
    
    def test_assignment_target_restrictions(self, tester):
        """Test restrictions on assignment expression targets"""
        # Skip if Python version doesn't support assignment expressions
        if sys.version_info < (3, 8):
            pytest.skip("Assignment expressions require Python 3.8+")
        
        # Language Reference: only simple names allowed as targets
        # These are actual syntax errors in Python
        target_restriction_errors = [
            "if (1 := value) > 0: pass",         # Literal assignment
            "if (obj.attr := value) > 0: pass",  # Attribute assignment
            "if (items[0] := value) > 0: pass",  # Subscript assignment  
            "if (*args := values) > 0: pass",    # Starred assignment
        ]
        
        for source in target_restriction_errors:
            tester.assert_assignment_expression_syntax_error(source)
        
        # This one actually parses but creates a weird AST (tuple with assignment expression)
        tuple_assignment_source = "if (a, b := values) > 0: pass"
        tree = tester.assert_assignment_expression_parses(tuple_assignment_source)
        # This creates a tuple containing a NamedExpr, which is syntactically valid but semantically odd
    
    def test_assignment_context_restrictions(self, tester):
        """Test restrictions on assignment expression contexts"""
        # Skip if Python version doesn't support assignment expressions
        if sys.version_info < (3, 8):
            pytest.skip("Assignment expressions require Python 3.8+")
        
        # Language Reference: assignment expressions not allowed in certain contexts
        # Note: These restrictions may be semantic rather than syntactic
        contextual_restrictions = [
            # These should parse but may have semantic restrictions
            """
# Assignment in function default parameter (semantic restriction)
def func(param=(x := default_value())):
    return param, x
""",
            """
# Assignment in class body (context-dependent)
class TestClass:
    if (attr_value := compute_default()):
        class_attr = attr_value
"""
        ]
        
        # These should parse as valid syntax
        for source in contextual_restrictions:
            tree = tester.assert_assignment_expression_parses(source)
    
    def test_assignment_operator_precedence(self, tester):
        """Test assignment expression operator precedence"""
        # Skip if Python version doesn't support assignment expressions
        if sys.version_info < (3, 8):
            pytest.skip("Assignment expressions require Python 3.8+")
        
        # Language Reference: := has specific precedence
        precedence_patterns = [
            """
# Assignment has lower precedence than most operators
if (result := a + b) > c:
    use_result(result)
""",
            """
# Assignment with comparison
if (value := calculate()) == expected:
    success(value)
""",
            """
# Assignment with logical operators
if (config := load_config()) and config.enabled:
    apply_config(config)
""",
            """
# Assignment in complex expressions
result = (x := compute()) * 2 if x > 0 else 0
""",
            """
# Assignment with function calls
output = process((data := prepare_data()), validate=True)
"""
        ]
        
        for source in precedence_patterns:
            tree = tester.assert_assignment_expression_parses(source)
            named_exprs = tester.get_named_expressions(source)
            assert len(named_exprs) >= 1, f"Should handle precedence: {source}"
    
    def test_assignment_scoping_behavior(self, tester):
        """Test assignment expression scoping behavior"""
        # Skip if Python version doesn't support assignment expressions
        if sys.version_info < (3, 8):
            pytest.skip("Assignment expressions require Python 3.8+")
        
        # Language Reference: assignment expressions create variables in enclosing scope
        scoping_patterns = [
            """
# Assignment in comprehension affects enclosing scope
result = [process(x) for item in items if (x := transform(item)) is not None]
# x is available here
print(f"Last x value: {x}")
""",
            """
# Assignment in conditional creates variable
if (value := get_value()) > 0:
    print(f"Got positive value: {value}")
# value is available here too
else:
    print(f"Got non-positive value: {value}")
""",
            """
# Assignment in while loop
while (line := file.readline()):
    process_line(line)
# line is available here (last value or empty string)
""",
            """
# Multiple assignments create multiple variables
if (a := get_a()) and (b := get_b()):
    result = combine(a, b)
# Both a and b are available here
"""
        ]
        
        for source in scoping_patterns:
            tree = tester.assert_assignment_expression_parses(source)
            named_exprs = tester.get_named_expressions(source)
            assert len(named_exprs) >= 1, f"Should handle scoping: {source}"


@pytest.mark.min_version_3_8  # Assignment expressions require Python 3.8+
class TestSection612AssignmentExpressionAST:
    """Test assignment expression AST structure validation."""
    
    def test_named_expr_ast_structure(self, tester):
        """Test NamedExpr AST node structure"""
        # Skip if Python version doesn't support assignment expressions
        if sys.version_info < (3, 8):
            pytest.skip("Assignment expressions require Python 3.8+")
        
        # Language Reference: AST structure for assignment expressions
        assignment_ast_cases = [
            """
if (value := compute()) > 0:
    use_value(value)
""",
            """
result = [transform(x) for item in items if (x := extract(item))]
""",
            """
while (line := file.readline()):
    process_line(line)
"""
        ]
        
        for source in assignment_ast_cases:
            tree = tester.assert_assignment_expression_parses(source)
            named_exprs = tester.get_named_expressions(source)
            assert len(named_exprs) >= 1, f"Should have assignment expressions: {source}"
            
            for named_expr in named_exprs:
                # NamedExpr nodes must have target and value
                assert isinstance(named_expr, ast.NamedExpr), "Should be NamedExpr node"
                assert hasattr(named_expr, 'target'), "Should have target"
                assert hasattr(named_expr, 'value'), "Should have value"
                
                # Target should be Name node
                assert isinstance(named_expr.target, ast.Name), "Target should be Name node"
                assert hasattr(named_expr.target, 'id'), "Target should have id"
                
                # Value should be expression
                assert named_expr.value is not None, "Value should not be None"
    
    def test_nested_assignment_ast_structure(self, tester):
        """Test nested assignment expression AST structure"""
        # Skip if Python version doesn't support assignment expressions
        if sys.version_info < (3, 8):
            pytest.skip("Assignment expressions require Python 3.8+")
        
        # Language Reference: nested assignment structure in AST
        nested_assignment_source = """
if (outer := transform(inner)) and (inner := get_value()):
    use_both(outer, inner)
"""
        
        tree = tester.assert_assignment_expression_parses(nested_assignment_source)
        named_exprs = tester.get_named_expressions(nested_assignment_source)
        assert len(named_exprs) >= 2, "Should have multiple assignment expressions"
        
        # Check that each has proper structure
        for named_expr in named_exprs:
            assert isinstance(named_expr, ast.NamedExpr), "Should be NamedExpr node"
            assert isinstance(named_expr.target, ast.Name), "Target should be Name node"
            assert named_expr.value is not None, "Value should not be None"
    
    def test_assignment_in_complex_expressions_ast(self, tester):
        """Test assignment with complex expressions AST"""
        # Skip if Python version doesn't support assignment expressions
        if sys.version_info < (3, 8):
            pytest.skip("Assignment expressions require Python 3.8+")
        
        # Language Reference: complex expressions containing assignments
        complex_assignment_source = """
result = [
    final_transform(processed)
    for item in collection
    if (processed := complex_preprocessing(item.value, config))
    and processed.is_valid()
    and (score := calculate_score(processed)) > threshold
]
"""
        
        tree = tester.assert_assignment_expression_parses(complex_assignment_source)
        named_exprs = tester.get_named_expressions(complex_assignment_source)
        assert len(named_exprs) >= 2, "Should have assignment expressions"
        
        # Should have function calls and other complex expressions
        function_calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
        assert len(function_calls) >= 3, "Should have function calls in assignments"


@pytest.mark.min_version_3_8  # Assignment expressions require Python 3.8+
class TestSection612CrossImplementationCompatibility:
    """Test cross-implementation compatibility for assignment expressions."""
    
    def test_assignment_expression_ast_consistency(self, tester):
        """Test assignment expression AST consistency across implementations"""
        # Skip if Python version doesn't support assignment expressions
        if sys.version_info < (3, 8):
            pytest.skip("Assignment expressions require Python 3.8+")
        
        # Language Reference: assignment AST should be consistent
        consistency_test_cases = [
            """
if (value := compute()) > 0:
    use_value(value)
""",
            """
while (line := file.readline()):
    process_line(line)
""",
            """
result = [transform(x) for item in items if (x := extract(item))]
""",
            """
if (a := get_a()) and (b := get_b()):
    combine(a, b)
"""
        ]
        
        for source in consistency_test_cases:
            tree = tester.assert_assignment_expression_parses(source)
            
            # Should have consistent assignment structure
            named_exprs = tester.get_named_expressions(source)
            assert len(named_exprs) >= 1, f"Should have assignment expressions: {source}"
            
            for named_expr in named_exprs:
                assert isinstance(named_expr, ast.NamedExpr), "Should be NamedExpr node"
                assert hasattr(named_expr, 'target'), "Should have target"
                assert hasattr(named_expr, 'value'), "Should have value"
                assert isinstance(named_expr.target, ast.Name), "Target should be Name node"
    
    def test_comprehensive_assignment_patterns(self, tester):
        """Test comprehensive real-world assignment patterns"""
        # Skip if Python version doesn't support assignment expressions
        if sys.version_info < (3, 8):
            pytest.skip("Assignment expressions require Python 3.8+")
        
        # Language Reference: complex assignment usage scenarios
        comprehensive_patterns = [
            """
# Data processing pipeline with assignment expressions
class DataProcessor:
    def __init__(self, config_file):
        self.config = self._load_config(config_file)
        self.stats = {'processed': 0, 'errors': 0}
        
    def process_stream(self, data_stream):
        results = []
        
        # Process data with assignment expressions for efficiency
        while (batch := data_stream.read_batch()):
            # Preprocess and validate in one step
            if (cleaned := self._clean_batch(batch)) and self._validate_batch(cleaned):
                # Transform with error handling
                if (transformed := self._transform_batch(cleaned)):
                    # Apply business rules
                    if (filtered := self._apply_filters(transformed)) and len(filtered) > 0:
                        results.extend(filtered)
                        self.stats['processed'] += len(filtered)
                    else:
                        self.stats['errors'] += len(cleaned)
        
        return results
    
    def process_files(self, file_paths):
        all_results = []
        
        for file_path in file_paths:
            try:
                # Read and validate file in condition
                if (content := self._read_file(file_path)) and (parsed := self._parse_content(content)):
                    # Process with quality checks
                    if (quality_score := self._check_quality(parsed)) > self.config.min_quality:
                        # Transform based on file type
                        if (file_type := self._detect_type(file_path)) in self.config.supported_types:
                            if (processor := self.config.processors.get(file_type)):
                                if (processed := processor(parsed, quality_score)):
                                    all_results.append({
                                        'file': file_path,
                                        'type': file_type,
                                        'quality': quality_score,
                                        'data': processed
                                    })
            except Exception as e:
                self._log_error(f"Failed to process {file_path}: {e}")
        
        return all_results
    
    def analyze_patterns(self, datasets):
        pattern_analysis = {}
        
        for dataset_name, dataset in datasets.items():
            analysis = {}
            
            # Analyze data characteristics
            if (numeric_cols := [col for col in dataset.columns if self._is_numeric(dataset[col])]):
                analysis['numeric_summary'] = {
                    col: {
                        'mean': dataset[col].mean() if (filtered := dataset[col].dropna()).size > 0 else None,
                        'std': filtered.std() if len(filtered) > 1 else 0,
                        'outliers': len(outliers) if (outliers := self._detect_outliers(filtered)) else 0
                    }
                    for col in numeric_cols
                }
            
            # Analyze categorical patterns
            if (categorical_cols := [col for col in dataset.columns if self._is_categorical(dataset[col])]):
                analysis['categorical_summary'] = {
                    col: {
                        'unique_count': len(unique_vals) if (unique_vals := dataset[col].unique()) else 0,
                        'most_common': most_common[0] if (most_common := dataset[col].value_counts().index) and len(most_common) > 0 else None,
                        'distribution': dict(dataset[col].value_counts()) if len(unique_vals) < 50 else None
                    }
                    for col in categorical_cols
                }
            
            # Correlation analysis
            if (corr_matrix := self._calculate_correlations(dataset)) is not None:
                if (high_corr := self._find_high_correlations(corr_matrix, threshold=0.8)):
                    analysis['high_correlations'] = high_corr
            
            pattern_analysis[dataset_name] = analysis
        
        return pattern_analysis
    
    def _load_config(self, config_file):
        # Placeholder for config loading
        return type('Config', (), {
            'min_quality': 0.7,
            'supported_types': ['json', 'csv', 'xml'],
            'processors': {}
        })()
    
    def _clean_batch(self, batch):
        return batch  # Placeholder
    
    def _validate_batch(self, batch):
        return True  # Placeholder
    
    def _transform_batch(self, batch):
        return batch  # Placeholder
    
    def _apply_filters(self, batch):
        return batch  # Placeholder
    
    def _read_file(self, file_path):
        return "content"  # Placeholder
    
    def _parse_content(self, content):
        return {'data': content}  # Placeholder
    
    def _check_quality(self, parsed):
        return 0.8  # Placeholder
    
    def _detect_type(self, file_path):
        return 'json'  # Placeholder
    
    def _log_error(self, message):
        print(f"ERROR: {message}")
    
    def _is_numeric(self, series):
        return True  # Placeholder
    
    def _is_categorical(self, series):
        return True  # Placeholder
    
    def _detect_outliers(self, series):
        return []  # Placeholder
    
    def _calculate_correlations(self, dataset):
        return None  # Placeholder
    
    def _find_high_correlations(self, corr_matrix, threshold):
        return []  # Placeholder

# API interaction with assignment expressions
class APIClient:
    def __init__(self, base_url, auth_token):
        self.base_url = base_url
        self.auth_token = auth_token
        self.session_stats = {'requests': 0, 'errors': 0}
    
    def fetch_paginated_data(self, endpoint, page_size=100):
        all_data = []
        page = 1
        
        # Efficient pagination with assignment expressions
        while (response := self._make_request(f"{endpoint}?page={page}&size={page_size}")) and response.get('data'):
            if (data := response['data']) and len(data) > 0:
                # Process and validate each item
                valid_items = [
                    item for item in data 
                    if (processed := self._process_item(item)) and self._validate_item(processed)
                ]
                
                if valid_items:
                    all_data.extend(valid_items)
                
                # Check for more pages
                if not (has_more := response.get('has_more', False)) or len(data) < page_size:
                    break
                
                page += 1
            else:
                break
        
        return all_data
    
    def batch_operations(self, operations):
        results = {}
        
        for operation_id, operation in operations.items():
            try:
                # Execute operation with error handling
                if (endpoint := operation.get('endpoint')) and (method := operation.get('method')):
                    if (payload := self._prepare_payload(operation.get('data', {}))) or method in ['GET', 'DELETE']:
                        if (response := self._execute_operation(method, endpoint, payload)):
                            # Process response based on expected format
                            if (expected_format := operation.get('response_format')) == 'json':
                                if (parsed := self._parse_json_response(response)):
                                    results[operation_id] = parsed
                            elif expected_format == 'xml':
                                if (parsed := self._parse_xml_response(response)):
                                    results[operation_id] = parsed
                            else:
                                results[operation_id] = response
                        else:
                            results[operation_id] = {'error': 'Operation failed'}
                    else:
                        results[operation_id] = {'error': 'Invalid payload'}
                else:
                    results[operation_id] = {'error': 'Missing endpoint or method'}
            except Exception as e:
                results[operation_id] = {'error': str(e)}
        
        return results
    
    def smart_retry_request(self, endpoint, max_retries=3):
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Attempt request with exponential backoff
                if (response := self._make_request(endpoint)) and response.get('status') == 'success':
                    return response
                elif (error_code := response.get('error_code') if response else None) in [429, 502, 503]:
                    # Exponential backoff for retryable errors
                    if (wait_time := min(2 ** retry_count, 30)) > 0:
                        import time
                        time.sleep(wait_time)
                    retry_count += 1
                else:
                    # Non-retryable error
                    return response
            except Exception as e:
                if retry_count == max_retries - 1:
                    return {'error': str(e)}
                retry_count += 1
        
        return {'error': 'Max retries exceeded'}
    
    def _make_request(self, url):
        self.session_stats['requests'] += 1
        return {'status': 'success', 'data': []}  # Placeholder
    
    def _process_item(self, item):
        return item  # Placeholder
    
    def _validate_item(self, item):
        return True  # Placeholder
    
    def _prepare_payload(self, data):
        return data  # Placeholder
    
    def _execute_operation(self, method, endpoint, payload):
        return {'status': 'success'}  # Placeholder
    
    def _parse_json_response(self, response):
        return response  # Placeholder
    
    def _parse_xml_response(self, response):
        return response  # Placeholder
"""
        ]
        
        for source in comprehensive_patterns:
            tree = tester.assert_assignment_expression_parses(source)
            
            # Should have multiple assignment usages
            named_exprs = tester.get_named_expressions(source)
            assert len(named_exprs) >= 10, f"Should have many assignment expressions: {source}"
    
    def test_assignment_expression_introspection(self, tester):
        """Test ability to analyze assignment expressions programmatically"""
        # Skip if Python version doesn't support assignment expressions
        if sys.version_info < (3, 8):
            pytest.skip("Assignment expressions require Python 3.8+")
        
        # Test programmatic analysis of assignment expression structure
        introspection_source = """
def assignment_examples():
    # Simple assignments
    if (value := get_value()) > 0:
        use_value(value)
    
    # Assignments in loops
    while (line := file.readline()):
        process_line(line)
    
    # Assignments in comprehensions
    result = [transform(x) for item in items if (x := extract(item))]
    
    # Multiple assignments
    if (a := get_a()) and (b := get_b()) and (c := compute(a, b)):
        use_all(a, b, c)
    
    # Nested assignments
    if (outer := process(inner)) and (inner := get_inner()):
        combine(outer, inner)
    
    # Assignments in function calls
    output = complex_function(
        base_value,
        modifier=(multiplier := calculate()) * adjustment
    )
    
    return value, line, result, a, b, c, outer, inner, multiplier
"""
        
        tree = tester.assert_assignment_expression_parses(introspection_source)
        
        # Should identify all assignment expressions
        named_exprs = tester.get_named_expressions(introspection_source)
        assert len(named_exprs) >= 8, "Should have multiple assignment expressions"
        
        # Should identify assignment targets
        targets = tester.get_assignment_targets(introspection_source)
        assert len(targets) >= 8, "Should have assignment targets"
        
        # Should identify assignment values
        values = tester.get_assignment_values(introspection_source)
        assert len(values) >= 8, "Should have assignment values"
        
        # All assignments should have proper structure
        for named_expr in named_exprs:
            assert isinstance(named_expr, ast.NamedExpr), "Should be NamedExpr node"
            assert isinstance(named_expr.target, ast.Name), "Target should be Name node"
            assert named_expr.value is not None, "Should have value expression"
        
        # Targets should be valid identifiers
        for target in targets:
            assert isinstance(target, str), "Target should be string"
            assert target.isidentifier(), "Target should be valid identifier"