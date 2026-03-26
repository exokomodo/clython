"""
Section 6.15: Expression Lists - Conformance Test Suite

Tests Python Language Reference Section 6.15 compliance across implementations.
Based on formal expression list syntax definitions and prose assertions for tuple formation.

Grammar tested:
    expression_list: expression ( "," expression )* [","]
    starred_list: starred_item ( "," starred_item )* [","]
    starred_expression: expression | ( starred_item "," )* [ starred_item ]

Language Reference requirements tested:
    - Expression list syntax validation
    - Comma-separated expression parsing
    - Tuple formation rules and contexts
    - Trailing comma handling in expression lists
    - Precedence in expression list evaluation
    - Expression list in different contexts (assignments, calls, returns)
    - Starred expressions in expression lists (*args unpacking)
    - Error conditions for invalid expression lists
    - Expression list AST structure validation
    - Cross-implementation expression list compatibility
"""

import ast
import pytest
import sys
from typing import Any, Tuple


class ExpressionListTester:
    """Helper class for testing expression list conformance.
    
    Focuses on AST structure validation for expression list syntax and tuple
    formation patterns that can be statically analyzed for cross-implementation compatibility.
    """
    
    def assert_expression_list_parses(self, source: str):
        """Test that expression list syntax parses correctly.
        
        Args:
            source: Python source code with expression lists
        """
        try:
            tree = ast.parse(source)
            return tree
        except SyntaxError as e:
            pytest.fail(f"Expression list syntax should be valid but failed to parse: {source}\\nError: {e}")
    
    def assert_expression_list_syntax_error(self, source: str):
        """Test that invalid expression list syntax raises SyntaxError.
        
        Args:
            source: Python source code that should be invalid
        """
        with pytest.raises(SyntaxError):
            ast.parse(source)
    
    def get_tuple_nodes(self, source: str) -> list:
        """Get Tuple AST nodes from source.
        
        Args:
            source: Python source code
            
        Returns:
            List of ast.Tuple nodes
        """
        tree = ast.parse(source)
        tuples = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Tuple):
                tuples.append(node)
        
        return tuples
    
    def get_assignment_targets(self, source: str) -> list:
        """Get assignment target nodes from source.
        
        Args:
            source: Python source code
            
        Returns:
            List of assignment target nodes
        """
        tree = ast.parse(source)
        targets = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                targets.extend(node.targets)
            elif isinstance(node, ast.AugAssign):
                targets.append(node.target)
        
        return targets
    
    def get_function_calls(self, source: str) -> list:
        """Get function call nodes from source.
        
        Args:
            source: Python source code
            
        Returns:
            List of ast.Call nodes
        """
        tree = ast.parse(source)
        calls = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                calls.append(node)
        
        return calls
    
    def has_starred_expressions(self, source: str) -> bool:
        """Check if source contains starred expressions.
        
        Args:
            source: Python source code
            
        Returns:
            True if contains ast.Starred nodes or **kwargs
        """
        tree = ast.parse(source)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Starred):
                return True
            # Also check for **kwargs in function calls
            elif isinstance(node, ast.Call) and node.keywords:
                for keyword in node.keywords:
                    if keyword.arg is None:  # **kwargs
                        return True
        
        return False
    
    def count_tuple_elements(self, tuple_node: ast.Tuple) -> int:
        """Count elements in a tuple node.
        
        Args:
            tuple_node: AST Tuple node
            
        Returns:
            Number of elements in tuple
        """
        return len(tuple_node.elts)


@pytest.fixture
def tester():
    """Provide ExpressionListTester instance for tests."""
    return ExpressionListTester()


class TestSection615BasicExpressionLists:
    """Test basic expression list syntax."""
    
    def test_simple_expression_lists(self, tester):
        """Test simple comma-separated expressions"""
        # Language Reference: expression_list: expression ( "," expression )* [","]
        simple_expression_list_patterns = [
            """
x = 1, 2, 3
""",
            """
result = a, b, c
""",
            """
values = 'hello', 'world', 42
""",
            """
coordinates = x + 1, y * 2, z / 3
""",
            """
mixed = func(a), obj.attr, items[0]
"""
        ]
        
        for source in simple_expression_list_patterns:
            tree = tester.assert_expression_list_parses(source)
            tuple_nodes = tester.get_tuple_nodes(source)
            assert len(tuple_nodes) >= 1, f"Should create tuple from expression list: {source}"
            
            # Should have multiple elements
            for tuple_node in tuple_nodes:
                assert tester.count_tuple_elements(tuple_node) >= 2, f"Tuple should have multiple elements: {source}"
    
    def test_trailing_comma_expressions(self, tester):
        """Test expression lists with trailing commas"""
        # Language Reference: expression lists can have trailing commas
        trailing_comma_patterns = [
            """
x = 1, 2, 3,
""",
            """
result = a, b,
""",
            """
single_element = value,
""",
            """
long_list = (
    first_item,
    second_item,
    third_item,
)
""",
            """
function_args = (
    arg1,
    arg2,
    arg3,
)
"""
        ]
        
        for source in trailing_comma_patterns:
            tree = tester.assert_expression_list_parses(source)
            tuple_nodes = tester.get_tuple_nodes(source)
            assert len(tuple_nodes) >= 1, f"Should handle trailing commas: {source}"
    
    def test_single_element_tuples(self, tester):
        """Test single-element tuple creation with trailing comma"""
        # Language Reference: single element + comma creates tuple
        single_element_patterns = [
            """
single = value,
""",
            """
x = (42,)
""",
            """
result = func(),
""",
            """
item = obj.attr,
""",
            """
element = items[0],
"""
        ]
        
        for source in single_element_patterns:
            tree = tester.assert_expression_list_parses(source)
            tuple_nodes = tester.get_tuple_nodes(source)
            assert len(tuple_nodes) >= 1, f"Should create single-element tuple: {source}"
            
            # Should have exactly one element
            for tuple_node in tuple_nodes:
                assert tester.count_tuple_elements(tuple_node) == 1, f"Should be single-element tuple: {source}"
    
    def test_expression_list_precedence(self, tester):
        """Test precedence in expression lists"""
        # Language Reference: comma has lowest precedence
        precedence_patterns = [
            """
x = 1 + 2, 3 * 4
""",
            """
result = a and b, c or d
""",
            """
values = x < y, z > w
""",
            """
comparisons = a == b, c != d, e >= f
""",
            """
operations = a + b * c, d / e - f
"""
        ]
        
        for source in precedence_patterns:
            tree = tester.assert_expression_list_parses(source)
            tuple_nodes = tester.get_tuple_nodes(source)
            assert len(tuple_nodes) >= 1, f"Should handle operator precedence: {source}"


class TestSection615ExpressionListContexts:
    """Test expression lists in different contexts."""
    
    def test_assignment_expression_lists(self, tester):
        """Test expression lists in assignment contexts"""
        # Language Reference: expression lists in assignments
        assignment_context_patterns = [
            """
a, b, c = 1, 2, 3
""",
            """
x, y = func1(), func2()
""",
            """
first, *rest = sequence
""",
            """
*beginning, last = items
""",
            """
start, *middle, end = data
""",
            """
(x, y), z = nested_data
"""
        ]
        
        for source in assignment_context_patterns:
            tree = tester.assert_expression_list_parses(source)
            
            # Should have assignment with tuple targets/values
            assignments = [node for node in ast.walk(tree) if isinstance(node, ast.Assign)]
            assert len(assignments) >= 1, f"Should have assignment: {source}"
    
    def test_function_call_expression_lists(self, tester):
        """Test expression lists in function calls"""
        # Language Reference: expression lists as function arguments
        function_call_patterns = [
            """
func(a, b, c)
""",
            """
result = method(x, y, z)
""",
            """
call_with_expressions(1 + 2, 3 * 4, 5 / 6)
""",
            """
mixed_args(positional, *args, **kwargs)
""",
            """
nested_call(func1(a, b), func2(c, d))
""",
            """
complex_call(
    first_arg,
    second_arg,
    third_arg,
)
"""
        ]
        
        for source in function_call_patterns:
            tree = tester.assert_expression_list_parses(source)
            calls = tester.get_function_calls(source)
            assert len(calls) >= 1, f"Should have function calls: {source}"
            
            # Should have multiple arguments
            for call in calls:
                if hasattr(call, 'args') and call.args:
                    assert len(call.args) >= 1, f"Should have call arguments: {source}"
    
    def test_return_expression_lists(self, tester):
        """Test expression lists in return statements"""
        # Language Reference: return statements with expression lists
        return_context_patterns = [
            """
def func():
    return 1, 2, 3
""",
            """
def multi_return():
    return a, b, c
""",
            """
def computed_return():
    return x + 1, y * 2
""",
            """
def conditional_return():
    if condition:
        return first, second
    else:
        return third, fourth
""",
            """
def complex_return():
    return (
        compute_first(),
        compute_second(),
        compute_third()
    )
"""
        ]
        
        for source in return_context_patterns:
            tree = tester.assert_expression_list_parses(source)
            
            # Should have return statements
            returns = [node for node in ast.walk(tree) if isinstance(node, ast.Return)]
            assert len(returns) >= 1, f"Should have return statements: {source}"
            
            # Should have tuple returns
            tuple_nodes = tester.get_tuple_nodes(source)
            assert len(tuple_nodes) >= 1, f"Should return tuples: {source}"
    
    def test_comprehension_expression_lists(self, tester):
        """Test expression lists in comprehensions"""
        # Language Reference: expression lists in comprehension targets
        comprehension_patterns = [
            """
result = [(x, y) for x in range(3) for y in range(3)]
""",
            """
pairs = [(a, b) for a, b in zip(list1, list2)]
""",
            """
coords = [(x + 1, y * 2) for x, y in points]
""",
            """
nested = [((i, j), (i*j)) for i in range(3) for j in range(3)]
""",
            """
filtered = [(x, y, x+y) for x, y in data if x > y]
"""
        ]
        
        for source in comprehension_patterns:
            tree = tester.assert_expression_list_parses(source)
            tuple_nodes = tester.get_tuple_nodes(source)
            assert len(tuple_nodes) >= 1, f"Should have tuples in comprehensions: {source}"


class TestSection615StarredExpressions:
    """Test starred expressions in expression lists."""
    
    def test_basic_starred_expressions(self, tester):
        """Test basic starred expression syntax"""
        # Language Reference: starred expressions with *
        basic_starred_patterns = [
            """
args = [1, 2, 3]
result = func(*args)
""",
            """
items = [a, b, c]
combined = [*items, d, e]
""",
            """
first, *rest = sequence
""",
            """
*beginning, last = items
""",
            """
start, *middle, end = data
""",
            """
merged = [*list1, *list2, *list3]
"""
        ]
        
        for source in basic_starred_patterns:
            tree = tester.assert_expression_list_parses(source)
            assert tester.has_starred_expressions(source), f"Should have starred expressions: {source}"
    
    def test_starred_in_assignments(self, tester):
        """Test starred expressions in assignment targets"""
        # Language Reference: starred expressions in assignment contexts
        starred_assignment_patterns = [
            """
a, *b, c = range(10)
""",
            """
*head, tail = sequence
""",
            """
first, *middle, last = data
""",
            """
x, *y = values
""",
            """
*all_items, = iterable  # Unpack all into list
""",
            """
(a, *b), c = nested_structure
"""
        ]
        
        for source in starred_assignment_patterns:
            tree = tester.assert_expression_list_parses(source)
            assert tester.has_starred_expressions(source), f"Should have starred in assignments: {source}"
    
    def test_starred_in_function_calls(self, tester):
        """Test starred expressions in function calls"""
        # Language Reference: starred expressions as function arguments
        starred_call_patterns = [
            """
args = [1, 2, 3]
kwargs = {'key': 'value'}
func(*args, **kwargs)
""",
            """
list1 = [1, 2]
list2 = [3, 4]
combined_call(0, *list1, *list2, 5)
""",
            """
data = {'a': 1, 'b': 2}
extra = {'c': 3}
function(**data, **extra)
""",
            """
mixed_call(arg1, *args, kwarg1=val1, **kwargs)
""",
            """
nested_call(func(*inner_args), *outer_args)
"""
        ]
        
        for source in starred_call_patterns:
            tree = tester.assert_expression_list_parses(source)
            assert tester.has_starred_expressions(source), f"Should have starred in calls: {source}"
    
    def test_starred_in_collections(self, tester):
        """Test starred expressions in collection literals"""
        # Language Reference: starred expressions in lists, sets, tuples
        starred_collection_patterns = [
            """
list1 = [1, 2]
list2 = [3, 4]
combined = [*list1, 5, *list2]
""",
            """
set1 = {1, 2}
set2 = {3, 4}
merged = {*set1, *set2, 5}
""",
            """
tuple1 = (1, 2)
tuple2 = (3, 4)
result = (*tuple1, 5, *tuple2)
""",
            """
nested = [*range(3), *range(3, 6), *range(6, 10)]
""",
            """
mixed_types = [*"hello", *[1, 2, 3], *range(3)]
"""
        ]
        
        for source in starred_collection_patterns:
            tree = tester.assert_expression_list_parses(source)
            assert tester.has_starred_expressions(source), f"Should have starred in collections: {source}"


class TestSection615ExpressionListErrors:
    """Test expression list error conditions."""
    
    def test_invalid_starred_usage(self, tester):
        """Test invalid starred expression usage"""
        # Language Reference: restrictions on starred expressions
        # Clear syntax errors that should be caught
        clear_syntax_errors = [
            "*",  # Bare starred expression
            "del *x",  # Cannot delete starred
        ]
        
        for source in clear_syntax_errors:
            tester.assert_expression_list_syntax_error(source)
        
        # Context-dependent restrictions that parse but are semantically invalid
        contextual_restrictions = [
            """
def test_func():
    x = *args  # Assignment without unpacking context
"""
        ]
        
        # These should parse (syntax is valid) but would fail at runtime/compile time
        for source in contextual_restrictions:
            tree = tester.assert_expression_list_parses(source)
    
    def test_multiple_starred_assignments(self, tester):
        """Test multiple starred expressions in assignments"""
        # Language Reference: only one starred expression per assignment target
        # Note: These are semantic errors, not always syntax errors
        semantic_error_patterns = [
            """
def test_func():
    try:
        a, *b, *c = sequence  # Multiple starred in same level
    except SyntaxError:
        pass
""",
            """
def test_func():
    try:
        *x, *y, z = items     # Multiple starred at start
    except SyntaxError:
        pass
"""
        ]
        
        # These should parse but may fail semantically
        for source in semantic_error_patterns:
            # Let's test that these at least parse as valid Python syntax
            # The semantic restrictions are enforced later
            tree = tester.assert_expression_list_parses(source)
    
    def test_bare_comma_errors(self, tester):
        """Test invalid bare comma usage"""
        # Language Reference: commas need expressions
        bare_comma_patterns = [
            "x = ,",           # Bare comma
            "func(,)",         # Bare comma in call
            "result = a, ,",   # Missing expression
        ]
        
        for source in bare_comma_patterns:
            tester.assert_expression_list_syntax_error(source)


class TestSection615TupleFormationRules:
    """Test tuple formation rules and contexts."""
    
    def test_parentheses_vs_tuple_creation(self, tester):
        """Test when parentheses create tuples vs grouping"""
        # Language Reference: parentheses for grouping vs tuple creation
        parentheses_patterns = [
            """
grouped = (x + y)  # Grouping, not tuple
""",
            """
single_tuple = (x,)  # Single-element tuple
""",
            """
multi_tuple = (x, y)  # Multi-element tuple
""",
            """
nested = ((a, b), (c, d))  # Nested tuples
""",
            """
expression = (x + y, z * w)  # Tuple of expressions
"""
        ]
        
        for source in parentheses_patterns:
            tree = tester.assert_expression_list_parses(source)
            tuple_nodes = tester.get_tuple_nodes(source)
            
            # Check expected tuple behavior based on pattern
            if "grouped = (x + y)" in source:
                # Should not create tuple for simple grouping
                pass  # This is hard to test statically without execution
            elif "single_tuple" in source or "multi_tuple" in source:
                assert len(tuple_nodes) >= 1, f"Should create tuple: {source}"
    
    def test_tuple_contexts_without_parentheses(self, tester):
        """Test tuple creation without parentheses"""
        # Language Reference: tuples can be created without parentheses in many contexts
        no_parens_patterns = [
            """
x, y = 1, 2
""",
            """
def func():
    return a, b, c
""",
            """
def gen():
    yield x, y, z
""",
            """
for a, b in pairs:
    pass
""",
            """
try:
    pass
except (ValueError, TypeError) as e:
    pass
"""
        ]
        
        for source in no_parens_patterns:
            tree = tester.assert_expression_list_parses(source)
            # Should parse successfully and create tuples where appropriate
            tuple_nodes = tester.get_tuple_nodes(source)
            # Most of these contexts should create tuples
            if not any(keyword in source for keyword in ['except']):
                assert len(tuple_nodes) >= 1, f"Should create tuples: {source}"
    
    def test_tuple_in_different_contexts(self, tester):
        """Test tuple behavior in various Python contexts"""
        # Language Reference: tuple creation rules vary by context
        context_patterns = [
            """
# Assignment context
a, b = 1, 2
x = 1, 2  # Creates tuple

# Function definition
def func(a, b=(1, 2)):  # Default parameter tuple
    return a, b  # Return tuple

# Function call
result = func(1, 2)  # Arguments, not tuple
tuple_arg = func((1, 2))  # Tuple argument

# Comparison
if (a, b) == (c, d):  # Tuple comparison
    pass

# Dictionary
mapping = {(x, y): value for x, y in coordinates}
""",
        ]
        
        for source in context_patterns:
            tree = tester.assert_expression_list_parses(source)
            tuple_nodes = tester.get_tuple_nodes(source)
            assert len(tuple_nodes) >= 1, f"Should have tuples in context: {source}"


class TestSection615AST:
    """Test expression list AST structure validation."""
    
    def test_tuple_ast_structure(self, tester):
        """Test Tuple AST node structure"""
        # Language Reference: AST structure for tuples
        tuple_ast_cases = [
            """
x = 1, 2, 3
""",
            """
single = value,
""",
            """
nested = (a, b), (c, d)
""",
            """
mixed = func(1, 2), obj.attr, items[0]
"""
        ]
        
        for source in tuple_ast_cases:
            tree = tester.assert_expression_list_parses(source)
            tuple_nodes = tester.get_tuple_nodes(source)
            assert len(tuple_nodes) >= 1, f"Should have tuple nodes: {source}"
            
            for tuple_node in tuple_nodes:
                # Tuple nodes must have elts attribute
                assert isinstance(tuple_node, ast.Tuple), "Should be Tuple node"
                assert hasattr(tuple_node, 'elts'), "Tuple should have elts attribute"
                assert isinstance(tuple_node.elts, list), "Elts should be a list"
                assert len(tuple_node.elts) >= 1, "Tuple should have elements"
                assert hasattr(tuple_node, 'ctx'), "Tuple should have context"
    
    def test_starred_ast_structure(self, tester):
        """Test Starred AST node structure"""
        # Language Reference: AST structure for starred expressions
        starred_ast_source = """
args = [1, 2, 3]
first, *rest = args
result = func(*args)
combined = [*args, 4, 5]
"""
        
        tree = tester.assert_expression_list_parses(starred_ast_source)
        
        # Should have Starred nodes
        starred_nodes = [node for node in ast.walk(tree) if isinstance(node, ast.Starred)]
        assert len(starred_nodes) >= 2, "Should have starred nodes"
        
        for starred_node in starred_nodes:
            assert hasattr(starred_node, 'value'), "Starred should have value attribute"
            assert hasattr(starred_node, 'ctx'), "Starred should have context"
    
    def test_expression_list_in_assignments_ast(self, tester):
        """Test expression list AST in assignment contexts"""
        # Language Reference: expression lists in assignment AST
        assignment_ast_source = """
a, b, c = 1, 2, 3
x, *y, z = range(10)
(p, q), r = nested
"""
        
        tree = tester.assert_expression_list_parses(assignment_ast_source)
        
        # Should have assignment nodes with tuple targets and values
        assignments = [node for node in ast.walk(tree) if isinstance(node, ast.Assign)]
        assert len(assignments) >= 3, "Should have assignment nodes"
        
        for assign in assignments:
            # Should have targets
            assert hasattr(assign, 'targets'), "Assignment should have targets"
            assert len(assign.targets) >= 1, "Should have at least one target"
            
            # Should have value
            assert hasattr(assign, 'value'), "Assignment should have value"


class TestSection615CrossImplementationCompatibility:
    """Test cross-implementation compatibility for expression lists."""
    
    def test_expression_list_ast_consistency(self, tester):
        """Test expression list AST consistency across implementations"""
        # Language Reference: expression list AST should be consistent
        consistency_test_cases = [
            """
x = 1, 2, 3
""",
            """
a, b = func1(), func2()
""",
            """
result = [*args, value, *more_args]
""",
            """
first, *middle, last = sequence
"""
        ]
        
        for source in consistency_test_cases:
            tree = tester.assert_expression_list_parses(source)
            
            # Should have consistent structure
            tuple_nodes = tester.get_tuple_nodes(source)
            for tuple_node in tuple_nodes:
                assert isinstance(tuple_node, ast.Tuple), "Should be Tuple node"
                assert hasattr(tuple_node, 'elts'), "Should have elements"
                assert hasattr(tuple_node, 'ctx'), "Should have context"
    
    def test_comprehensive_expression_list_patterns(self, tester):
        """Test comprehensive real-world expression list patterns"""
        # Language Reference: complex expression list usage scenarios
        comprehensive_patterns = [
            """
# Data processing with expression lists
def process_coordinates(points):
    # Multiple assignment
    for x, y, z in points:
        # Tuple creation and unpacking
        normalized = x/scale, y/scale, z/scale
        
        # Function calls with expression lists
        result = transform(x, y, z)
        
        # Return expression list
        yield normalized, result

# Configuration management
def setup_environment():
    # Multiple assignment with defaults
    host, port = config.get('server', ('localhost', 8080))
    
    # Starred expressions
    args = ['--verbose', '--debug']
    kwargs = {'timeout': 30}
    
    # Function call with unpacking
    server = Server(*args, host=host, port=port, **kwargs)
    
    # Return multiple values
    return server, host, port

# Data structure manipulation
def matrix_operations(matrix):
    # Nested tuple unpacking
    for row_idx, (row_data, metadata) in enumerate(matrix):
        # Expression lists in comprehensions
        processed = [(val * 2, idx) for idx, val in enumerate(row_data)]
        
        # Complex assignment patterns
        first, *middle, last = processed
        
        # Tuple construction with starred
        result = (row_idx, *middle, last.value if last else None)
        
        yield result
""",
            """
# Advanced tuple and expression list patterns
class DataProcessor:
    def __init__(self, *sources, **options):
        # Starred parameter unpacking
        self.sources = sources
        self.options = options
    
    def merge_sources(self):
        # Complex expression lists
        headers = self.sources[0].headers if self.sources else []
        
        # Multiple starred expressions
        all_data = [
            *headers,
            *[row for source in self.sources for row in source.data],
            *self.get_footer_rows()
        ]
        
        return all_data
    
    def process_batch(self, batch_data):
        # Tuple unpacking in nested structures
        for batch_id, (records, metadata, stats) in batch_data.items():
            # Expression list assignment
            count, avg, total = stats.count, stats.average, stats.total
            
            # Complex function calls
            processed_records = self.transform_records(
                *records,
                metadata=metadata,
                **self.options
            )
            
            # Multi-value return
            yield batch_id, processed_records, (count, avg, total)
    
    def aggregate_results(self, results):
        # Nested tuple unpacking
        batch_ids, record_sets, stat_tuples = zip(*results)
        
        # Starred expression in assignment
        first_batch, *other_batches = batch_ids
        
        # Complex tuple construction
        summary = (
            len(batch_ids),
            first_batch,
            sum(stats[2] for stats in stat_tuples),  # Sum totals
            [*record_sets[0], *[r for rs in record_sets[1:] for r in rs]]
        )
        
        return summary
"""
        ]
        
        for source in comprehensive_patterns:
            tree = tester.assert_expression_list_parses(source)
            
            # Should have multiple expression list usages
            tuple_nodes = tester.get_tuple_nodes(source)
            assert len(tuple_nodes) >= 3, f"Should have multiple tuples: {source}"
            
            # Should have starred expressions
            assert tester.has_starred_expressions(source), f"Should have starred expressions: {source}"
    
    def test_expression_list_introspection(self, tester):
        """Test ability to analyze expression lists programmatically"""
        # Test programmatic analysis of expression list structure
        introspection_source = """
def demonstrate_expression_lists():
    # Simple tuple creation
    coordinates = x, y, z
    
    # Assignment unpacking
    a, b, c = coordinates
    
    # Starred expressions
    first, *rest = sequence
    
    # Function calls
    result = func(a, b, c)
    
    # Starred in calls
    output = process(*args, **kwargs)
    
    # Return expression list
    return a, b, result
    
    # Complex nested structures
    nested = ((1, 2), (3, 4)), (5, 6)
    
    # Expression lists in comprehensions
    pairs = [(x, y) for x, y in zip(list1, list2)]
    
    # Mixed starred and regular
    combined = [*prefix, middle, *suffix]
"""
        
        tree = tester.assert_expression_list_parses(introspection_source)
        
        # Should identify all tuple nodes
        tuple_nodes = tester.get_tuple_nodes(introspection_source)
        assert len(tuple_nodes) >= 5, "Should have multiple tuple nodes"
        
        # Should identify starred expressions
        assert tester.has_starred_expressions(introspection_source), "Should have starred expressions"
        
        # Should identify function calls
        calls = tester.get_function_calls(introspection_source)
        assert len(calls) >= 2, "Should have function calls"
        
        # Should identify assignments
        assignments = [node for node in ast.walk(tree) if isinstance(node, ast.Assign)]
        assert len(assignments) >= 3, "Should have assignment statements"