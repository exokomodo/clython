"""
Section 6.14: Lambdas - Conformance Test Suite

Tests Python Language Reference Section 6.14 compliance across implementations.
Based on formal lambda expression syntax definitions and prose assertions for anonymous function behavior.

Grammar tested:
    lambda_expr: 'lambda' [parameter_list] ':' expression

Language Reference requirements tested:
    - Lambda expression syntax validation (lambda parameters: expression)
    - Parameter patterns and default value handling
    - Scope resolution and closure behavior in lambda expressions
    - Restrictions on lambda expressions (statement limitations)
    - Nested lambda patterns and composition
    - Lambda expressions in different contexts
    - Error conditions for malformed lambda expressions
    - Lambda expression AST structure validation
    - Cross-implementation lambda expression compatibility
"""

import ast
import pytest
import sys
from typing import Any


class LambdaExpressionTester:
    """Helper class for testing lambda expression conformance.
    
    Focuses on AST structure validation for lambda expression syntax and closure
    patterns that can be statically analyzed for cross-implementation compatibility.
    """
    
    def assert_lambda_expression_parses(self, source: str):
        """Test that lambda expression syntax parses correctly.
        
        Args:
            source: Python source code with lambda expressions
        """
        try:
            tree = ast.parse(source)
            return tree
        except SyntaxError as e:
            pytest.fail(f"Lambda expression syntax should be valid but failed to parse: {source}\\nError: {e}")
    
    def assert_lambda_expression_syntax_error(self, source: str):
        """Test that invalid lambda expression syntax raises SyntaxError.
        
        Args:
            source: Python source code that should be invalid
        """
        with pytest.raises(SyntaxError):
            ast.parse(source)
    
    def get_lambda_expressions(self, source: str) -> list:
        """Get Lambda AST nodes from source.
        
        Args:
            source: Python source code
            
        Returns:
            List of ast.Lambda nodes
        """
        tree = ast.parse(source)
        lambdas = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Lambda):
                lambdas.append(node)
        
        return lambdas
    
    def get_function_definitions(self, source: str) -> list:
        """Get FunctionDef AST nodes from source.
        
        Args:
            source: Python source code
            
        Returns:
            List of ast.FunctionDef nodes
        """
        tree = ast.parse(source)
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node)
        
        return functions
    
    def count_lambda_parameters(self, source: str) -> dict:
        """Count parameter types in lambda expressions.
        
        Args:
            source: Python source code
            
        Returns:
            Dict with counts of different parameter types
        """
        tree = ast.parse(source)
        param_counts = {
            'positional': 0,
            'defaults': 0,
            'varargs': 0,
            'kwonly': 0,
            'kwdefaults': 0,
            'kwargs': 0
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Lambda):
                args = node.args
                param_counts['positional'] += len(args.args)
                param_counts['defaults'] += len(args.defaults)
                param_counts['varargs'] += 1 if args.vararg else 0
                param_counts['kwonly'] += len(args.kwonlyargs)
                param_counts['kwdefaults'] += len([d for d in args.kw_defaults if d is not None])
                param_counts['kwargs'] += 1 if args.kwarg else 0
        
        return param_counts
    
    def count_nested_lambdas(self, source: str) -> int:
        """Count depth of nested lambda expressions.
        
        Args:
            source: Python source code
            
        Returns:
            Maximum nesting depth of lambda expressions
        """
        tree = ast.parse(source)
        
        def count_depth(node):
            max_depth = 0
            if isinstance(node, ast.Lambda):
                # Count nesting in lambda body
                body_depth = count_depth(node.body)
                max_depth = 1 + body_depth
            else:
                # Recurse into child nodes
                for child in ast.iter_child_nodes(node):
                    child_depth = count_depth(child)
                    max_depth = max(max_depth, child_depth)
            return max_depth
        
        return count_depth(tree)


@pytest.fixture
def tester():
    """Provide LambdaExpressionTester instance for tests."""
    return LambdaExpressionTester()


class TestSection614BasicLambdaSyntax:
    """Test basic lambda expression syntax."""
    
    def test_simple_lambda_expressions(self, tester):
        """Test simple lambda expression patterns"""
        # Language Reference: lambda_expr: 'lambda' [parameter_list] ':' expression
        simple_lambda_patterns = [
            """
square = lambda x: x * x
""",
            """
add = lambda x, y: x + y
""",
            """
constant = lambda: 42
""",
            """
identity = lambda x: x
""",
            """
greeting = lambda name: f"Hello, {name}!"
"""
        ]
        
        for source in simple_lambda_patterns:
            tree = tester.assert_lambda_expression_parses(source)
            lambdas = tester.get_lambda_expressions(source)
            assert len(lambdas) >= 1, f"Should have lambda expressions: {source}"
    
    def test_lambda_with_default_parameters(self, tester):
        """Test lambda expressions with default parameter values"""
        # Language Reference: lambda parameter defaults
        default_param_patterns = [
            """
multiply = lambda x, y=2: x * y
""",
            """
greet = lambda name, greeting="Hello": f"{greeting}, {name}!"
""",
            """
power = lambda base, exponent=2: base ** exponent
""",
            """
format_number = lambda value, precision=2: round(value, precision)
""",
            """
create_range = lambda start=0, stop=10, step=1: range(start, stop, step)
"""
        ]
        
        for source in default_param_patterns:
            tree = tester.assert_lambda_expression_parses(source)
            lambdas = tester.get_lambda_expressions(source)
            assert len(lambdas) >= 1, f"Should handle default parameters: {source}"
            
            param_counts = tester.count_lambda_parameters(source)
            assert param_counts['defaults'] >= 1, f"Should have default parameters: {source}"
    
    def test_lambda_with_variable_arguments(self, tester):
        """Test lambda expressions with *args and **kwargs"""
        # Language Reference: lambda variable arguments
        varargs_patterns = [
            """
sum_all = lambda *args: sum(args)
""",
            """
create_dict = lambda **kwargs: kwargs
""",
            """
combine = lambda *args, **kwargs: (args, kwargs)
""",
            """
flexible = lambda x, *args, y=10, **kwargs: (x, args, y, kwargs)
""",
            """
accumulate = lambda first, *rest: first + sum(rest)
"""
        ]
        
        for source in varargs_patterns:
            tree = tester.assert_lambda_expression_parses(source)
            lambdas = tester.get_lambda_expressions(source)
            assert len(lambdas) >= 1, f"Should handle variable arguments: {source}"
    
    @pytest.mark.min_version_3_8  # Positional-only parameters
    def test_lambda_with_positional_only_parameters(self, tester):
        """Test lambda expressions with positional-only parameters"""
        # Language Reference: positional-only parameters in lambda
        posonly_patterns = [
            """
divide = lambda x, y, /: x / y
""",
            """
complex_func = lambda a, b, /, c=10, *args, d, **kwargs: (a, b, c, args, d, kwargs)
""",
            """
restricted = lambda x, y, /, z: x + y + z
"""
        ]
        
        # Skip if Python version doesn't support positional-only parameters
        if sys.version_info < (3, 8):
            pytest.skip("Positional-only parameters require Python 3.8+")
        
        for source in posonly_patterns:
            tree = tester.assert_lambda_expression_parses(source)
            lambdas = tester.get_lambda_expressions(source)
            assert len(lambdas) >= 1, f"Should handle positional-only parameters: {source}"
    
    def test_lambda_with_keyword_only_parameters(self, tester):
        """Test lambda expressions with keyword-only parameters"""
        # Language Reference: keyword-only parameters in lambda
        kwonly_patterns = [
            """
func = lambda *, x: x * 2
""",
            """
config = lambda *, debug=False, verbose=True: {'debug': debug, 'verbose': verbose}
""",
            """
compute = lambda a, *, scale=1, offset=0: a * scale + offset
""",
            """
process = lambda data, *args, mode='fast', **kwargs: (data, args, mode, kwargs)
""",
            """
transform = lambda x, y, *, method='linear', **options: (x, y, method, options)
"""
        ]
        
        for source in kwonly_patterns:
            tree = tester.assert_lambda_expression_parses(source)
            lambdas = tester.get_lambda_expressions(source)
            assert len(lambdas) >= 1, f"Should handle keyword-only parameters: {source}"


class TestSection614LambdaContexts:
    """Test lambda expressions in different contexts."""
    
    def test_lambdas_in_assignments(self, tester):
        """Test lambda expressions in assignment contexts"""
        # Language Reference: lambda expressions assigned to variables
        assignment_patterns = [
            """
square = lambda x: x * x
""",
            """
operations = {
    'add': lambda x, y: x + y,
    'multiply': lambda x, y: x * y,
    'power': lambda x, y: x ** y
}
""",
            """
handlers = [
    lambda x: x.upper(),
    lambda x: x.lower(),
    lambda x: x.strip()
]
""",
            """
transform_func = lambda data: [item.process() for item in data] if data else []
""",
            """
validator = lambda value: value is not None and value > 0
"""
        ]
        
        for source in assignment_patterns:
            tree = tester.assert_lambda_expression_parses(source)
            lambdas = tester.get_lambda_expressions(source)
            assert len(lambdas) >= 1, f"Should work in assignments: {source}"
    
    def test_lambdas_in_function_calls(self, tester):
        """Test lambda expressions as function arguments"""
        # Language Reference: lambda expressions as arguments
        function_call_patterns = [
            """
result = map(lambda x: x * 2, numbers)
""",
            """
filtered = filter(lambda x: x > 0, values)
""",
            """
sorted_data = sorted(items, key=lambda x: x.priority)
""",
            """
reduced = reduce(lambda acc, x: acc + x, sequence, 0)
""",
            """
transformed = transform(data, processor=lambda x: x.clean().normalize())
"""
        ]
        
        for source in function_call_patterns:
            tree = tester.assert_lambda_expression_parses(source)
            lambdas = tester.get_lambda_expressions(source)
            assert len(lambdas) >= 1, f"Should work in function calls: {source}"
    
    def test_lambdas_in_comprehensions(self, tester):
        """Test lambda expressions in comprehensions"""
        # Language Reference: lambda expressions in comprehensions
        comprehension_patterns = [
            """
processors = [lambda x: x * i for i in range(5)]
""",
            """
validators = {name: lambda value: check_value(value, name) for name in fields}
""",
            """
transforms = (lambda data: process(data, mode) for mode in modes)
""",
            """
handlers = [lambda item: item if predicate(item) else default for predicate in predicates]
""",
            """
mappers = {
    key: lambda value: transform_value(value, config[key])
    for key in config
}
"""
        ]
        
        for source in comprehension_patterns:
            tree = tester.assert_lambda_expression_parses(source)
            lambdas = tester.get_lambda_expressions(source)
            assert len(lambdas) >= 1, f"Should work in comprehensions: {source}"
    
    def test_lambdas_in_return_statements(self, tester):
        """Test lambda expressions in return statements"""
        # Language Reference: lambda expressions in returns
        return_patterns = [
            """
def get_multiplier(factor):
    return lambda x: x * factor
""",
            """
def create_validator(min_value, max_value):
    return lambda value: min_value <= value <= max_value
""",
            """
def build_processor(config):
    return lambda data: process_data(data, config) if data else None
""",
            """
def get_comparator(ascending=True):
    return lambda x, y: (x > y) - (x < y) if ascending else (x < y) - (x > y)
""",
            """
def make_transformer(operations):
    return lambda input_data: [op(item) for op in operations for item in input_data]
"""
        ]
        
        for source in return_patterns:
            tree = tester.assert_lambda_expression_parses(source)
            lambdas = tester.get_lambda_expressions(source)
            assert len(lambdas) >= 1, f"Should work in returns: {source}"
    
    def test_lambdas_in_conditional_expressions(self, tester):
        """Test lambda expressions in conditional expressions"""
        # Language Reference: lambda expressions in conditionals
        conditional_patterns = [
            """
processor = lambda x: x.upper() if isinstance(x, str) else str(x)
""",
            """
handler = (lambda data: data.process()) if use_processing else (lambda data: data)
""",
            """
transform = lambda value: (
    value * 2 if value > 0 else
    value / 2 if value < 0 else
    0
)
""",
            """
selector = lambda items: (
    lambda item: item.priority
    if sort_by_priority else
    lambda item: item.name
)
""",
            """
validator = lambda input_value: (
    lambda x: x > 0 and x < 100
    if strict_mode else
    lambda x: True
)
"""
        ]
        
        for source in conditional_patterns:
            tree = tester.assert_lambda_expression_parses(source)
            lambdas = tester.get_lambda_expressions(source)
            assert len(lambdas) >= 1, f"Should work in conditionals: {source}"


class TestSection614NestedLambdas:
    """Test nested lambda expressions."""
    
    def test_lambdas_returning_lambdas(self, tester):
        """Test lambda expressions that return other lambda expressions"""
        # Language Reference: lambda expressions can return lambda expressions
        nested_lambda_patterns = [
            """
adder = lambda x: lambda y: x + y
""",
            """
multiplier = lambda factor: lambda value: value * factor
""",
            """
comparator = lambda op: lambda x, y: op(x, y)
""",
            """
curried = lambda f: lambda x: lambda y: f(x, y)
""",
            """
partial = lambda func, arg1: lambda arg2: func(arg1, arg2)
"""
        ]
        
        for source in nested_lambda_patterns:
            tree = tester.assert_lambda_expression_parses(source)
            lambdas = tester.get_lambda_expressions(source)
            assert len(lambdas) >= 2, f"Should have nested lambdas: {source}"
            
            nesting_depth = tester.count_nested_lambdas(source)
            assert nesting_depth >= 2, f"Should have lambda nesting: {source}"
    
    def test_lambdas_with_lambda_parameters(self, tester):
        """Test lambda expressions that take lambda parameters"""
        # Language Reference: lambda expressions as parameters to other lambdas
        lambda_param_patterns = [
            """
apply_twice = lambda f, x: f(f(x))
result = apply_twice(lambda y: y * 2, 5)
""",
            """
combine = lambda f, g: lambda x: f(g(x))
composed = combine(lambda x: x * 2, lambda x: x + 1)
""",
            """
conditional = lambda predicate, true_func, false_func: lambda x: true_func(x) if predicate(x) else false_func(x)
processor = conditional(lambda x: x > 0, lambda x: x * 2, lambda x: 0)
""",
            """
mapper = lambda transform: lambda collection: [transform(item) for item in collection]
string_mapper = mapper(lambda s: s.upper())
""",
            """
reducer = lambda combiner, initial: lambda sequence: reduce(combiner, sequence, initial)
summer = reducer(lambda acc, x: acc + x, 0)
"""
        ]
        
        for source in lambda_param_patterns:
            tree = tester.assert_lambda_expression_parses(source)
            lambdas = tester.get_lambda_expressions(source)
            assert len(lambdas) >= 2, f"Should have multiple lambdas: {source}"
    
    def test_deeply_nested_lambdas(self, tester):
        """Test deeply nested lambda expressions"""
        # Language Reference: lambda expressions can be arbitrarily nested
        deeply_nested_patterns = [
            """
triple_nested = lambda x: lambda y: lambda z: x + y + z
""",
            """
curried_func = lambda a: lambda b: lambda c: lambda d: a * b + c * d
""",
            """
builder = lambda config: lambda transform: lambda validator: lambda data: (
    transform(data) if validator(data) else None
)
""",
            """
compose_three = lambda f: lambda g: lambda h: lambda x: f(g(h(x)))
""",
            """
pipeline = (
    lambda stage1: lambda stage2: lambda stage3: lambda input_data:
    stage3(stage2(stage1(input_data)))
)
"""
        ]
        
        for source in deeply_nested_patterns:
            tree = tester.assert_lambda_expression_parses(source)
            nesting_depth = tester.count_nested_lambdas(source)
            assert nesting_depth >= 3, f"Should have deep nesting: {source}"
    
    def test_lambda_closures(self, tester):
        """Test lambda expressions creating closures"""
        # Language Reference: lambda expressions capture enclosing scope
        closure_patterns = [
            """
def create_multiplier(factor):
    return lambda x: x * factor

double = create_multiplier(2)
triple = create_multiplier(3)
""",
            """
def make_counter(start=0):
    count = start
    return lambda: count

counter = make_counter(10)
""",
            """
def build_validator(min_val, max_val):
    return lambda value: min_val <= value <= max_val

validator = build_validator(0, 100)
""",
            """
def create_formatter(prefix, suffix):
    return lambda text: f"{prefix}{text}{suffix}"

formatter = create_formatter("[", "]")
""",
            """
def make_accumulator():
    total = 0
    return lambda x: total + x  # Note: this captures total but doesn't modify

accumulator = make_accumulator()
"""
        ]
        
        for source in closure_patterns:
            tree = tester.assert_lambda_expression_parses(source)
            lambdas = tester.get_lambda_expressions(source)
            assert len(lambdas) >= 1, f"Should have lambda closures: {source}"


class TestSection614LambdaRestrictions:
    """Test lambda expression restrictions and limitations."""
    
    def test_lambda_statement_restrictions(self, tester):
        """Test restrictions on statements in lambda expressions"""
        # Language Reference: lambda body must be expression, not statement
        invalid_statement_patterns = [
            "lambda x: print(x)",  # Function call is valid
            "lambda x: x if True else None",  # Conditional expression is valid
        ]
        
        # These should actually parse fine - they're expressions, not statements
        for source in invalid_statement_patterns:
            tree = tester.assert_lambda_expression_parses(source)
            lambdas = tester.get_lambda_expressions(source)
            assert len(lambdas) >= 1, f"Should parse valid expressions: {source}"
        
        # These are actual statement errors
        statement_error_patterns = [
            "lambda x: x = 5",  # Assignment is statement
            "lambda: import os",  # Import is statement
            "lambda x: for i in x: pass",  # For loop is statement
            "lambda x: if x: pass",  # If statement (not expression) is statement
        ]
        
        for source in statement_error_patterns:
            tester.assert_lambda_expression_syntax_error(source)
    
    def test_lambda_complex_expression_allowed(self, tester):
        """Test complex expressions allowed in lambda bodies"""
        # Language Reference: lambda bodies can be complex expressions
        complex_expression_patterns = [
            """
complex_lambda = lambda x, y: (x + y) * (x - y) if x != y else 0
""",
            """
data_processor = lambda items: [
    item.transform().validate()
    for item in items
    if item is not None and item.is_valid()
]
""",
            """
dict_builder = lambda keys, values: {
    k: v for k, v in zip(keys, values)
    if k is not None
}
""",
            """
conditional_compute = lambda x: (
    expensive_function(x) if x > threshold else
    cheap_function(x) if x > 0 else
    0
)
""",
            """
nested_access = lambda data: (
    data.get('level1', {}).get('level2', {}).get('value', default_value)
    if isinstance(data, dict) else None
)
"""
        ]
        
        for source in complex_expression_patterns:
            tree = tester.assert_lambda_expression_parses(source)
            lambdas = tester.get_lambda_expressions(source)
            assert len(lambdas) >= 1, f"Should allow complex expressions: {source}"
    
    def test_lambda_annotation_restrictions(self, tester):
        """Test lambda parameter and return annotation restrictions"""
        # Language Reference: lambda expressions don't support annotations
        
        # These should be syntax errors in lambda context
        if sys.version_info >= (3, 5):  # Type annotations
            annotation_error_patterns = [
                "lambda x: int -> x * 2",  # Return annotation syntax error
                "lambda x: int: x * 2",   # Malformed syntax
            ]
            
            for source in annotation_error_patterns:
                tester.assert_lambda_expression_syntax_error(source)
    
    def test_lambda_name_restrictions(self, tester):
        """Test lambda expression name restrictions"""
        # Language Reference: lambda expressions are anonymous
        
        # Lambda expressions don't have names in the same way as def statements
        name_test_patterns = [
            """
# Lambda assigned to variable
func = lambda x: x * 2

# Lambda in data structure  
operations = {'double': lambda x: x * 2}

# Lambda as argument
result = map(lambda x: x + 1, range(10))
"""
        ]
        
        for source in name_test_patterns:
            tree = tester.assert_lambda_expression_parses(source)
            lambdas = tester.get_lambda_expressions(source)
            assert len(lambdas) >= 1, f"Should handle lambda naming: {source}"


class TestSection614LambdaAST:
    """Test lambda expression AST structure validation."""
    
    def test_lambda_ast_structure(self, tester):
        """Test Lambda AST node structure"""
        # Language Reference: AST structure for lambda expressions
        lambda_ast_cases = [
            """
simple = lambda x: x * 2
""",
            """
with_defaults = lambda x, y=5: x + y
""",
            """
with_varargs = lambda *args, **kwargs: (args, kwargs)
"""
        ]
        
        for source in lambda_ast_cases:
            tree = tester.assert_lambda_expression_parses(source)
            lambdas = tester.get_lambda_expressions(source)
            assert len(lambdas) >= 1, f"Should have lambda expressions: {source}"
            
            for lambda_node in lambdas:
                # Lambda nodes must have args and body
                assert isinstance(lambda_node, ast.Lambda), "Should be Lambda node"
                assert hasattr(lambda_node, 'args'), "Should have args"
                assert hasattr(lambda_node, 'body'), "Should have body"
                
                # Args should be arguments object
                assert isinstance(lambda_node.args, ast.arguments), "Should have arguments object"
                
                # Body should be an expression
                assert lambda_node.body is not None, "Body should not be None"
    
    def test_lambda_parameter_ast_structure(self, tester):
        """Test lambda parameter AST structure"""
        # Language Reference: lambda parameter structure in AST
        parameter_lambda_source = """
complex_lambda = lambda a, b=10, *args, c, d=20, **kwargs: (a, b, args, c, d, kwargs)
"""
        
        tree = tester.assert_lambda_expression_parses(parameter_lambda_source)
        lambdas = tester.get_lambda_expressions(parameter_lambda_source)
        assert len(lambdas) >= 1, "Should have lambda expression"
        
        lambda_node = lambdas[0]
        args = lambda_node.args
        
        # Should have correct argument structure
        assert len(args.args) >= 1, "Should have positional args"
        assert len(args.defaults) >= 1, "Should have defaults"
        if sys.version_info >= (3, 0):
            assert len(args.kwonlyargs) >= 1, "Should have keyword-only args"
        assert args.vararg is not None, "Should have varargs"
        assert args.kwarg is not None, "Should have kwargs"
    
    def test_nested_lambda_ast_structure(self, tester):
        """Test nested lambda AST structure"""
        # Language Reference: nested lambda structure in AST
        nested_lambda_source = """
curried = lambda x: lambda y: lambda z: x + y + z
"""
        
        tree = tester.assert_lambda_expression_parses(nested_lambda_source)
        lambdas = tester.get_lambda_expressions(nested_lambda_source)
        assert len(lambdas) >= 3, "Should have nested lambdas"
        
        # Check nesting structure
        nesting_depth = tester.count_nested_lambdas(nested_lambda_source)
        assert nesting_depth >= 3, "Should have proper nesting depth"


class TestSection614CrossImplementationCompatibility:
    """Test cross-implementation compatibility for lambda expressions."""
    
    def test_lambda_ast_consistency(self, tester):
        """Test lambda expression AST consistency across implementations"""
        # Language Reference: lambda AST should be consistent
        consistency_test_cases = [
            """
simple = lambda x: x * 2
""",
            """
default_params = lambda x, y=5: x + y
""",
            """
varargs = lambda *args, **kwargs: (args, kwargs)
""",
            """
nested = lambda x: lambda y: x + y
"""
        ]
        
        for source in consistency_test_cases:
            tree = tester.assert_lambda_expression_parses(source)
            
            # Should have consistent lambda structure
            lambdas = tester.get_lambda_expressions(source)
            assert len(lambdas) >= 1, f"Should have lambda expressions: {source}"
            
            for lambda_node in lambdas:
                assert isinstance(lambda_node, ast.Lambda), "Should be Lambda node"
                assert hasattr(lambda_node, 'args'), "Should have args"
                assert hasattr(lambda_node, 'body'), "Should have body"
                assert isinstance(lambda_node.args, ast.arguments), "Should have arguments object"
    
    def test_comprehensive_lambda_patterns(self, tester):
        """Test comprehensive real-world lambda patterns"""
        # Language Reference: complex lambda usage scenarios
        comprehensive_patterns = [
            """
# Functional programming with lambdas
class FunctionalProcessor:
    def __init__(self):
        # Basic transformations
        self.transforms = {
            'double': lambda x: x * 2,
            'square': lambda x: x ** 2,
            'negate': lambda x: -x,
            'abs': lambda x: abs(x),
            'increment': lambda x: x + 1
        }
        
        # Conditional processors
        self.conditional_transforms = {
            'positive_double': lambda x: x * 2 if x > 0 else x,
            'safe_divide': lambda x, y: x / y if y != 0 else 0,
            'clamp': lambda x, min_val=0, max_val=100: max(min_val, min(max_val, x))
        }
        
        # Composition functions
        self.compose = lambda f, g: lambda x: f(g(x))
        self.pipe = lambda *funcs: lambda x: self._apply_pipeline(x, funcs)
        
        # Higher-order functions
        self.map_filter = lambda pred, transform: lambda items: [
            transform(item) for item in items if pred(item)
        ]
        
        # Curried functions
        self.add = lambda x: lambda y: x + y
        self.multiply = lambda x: lambda y: x * y
        self.power = lambda base: lambda exponent: base ** exponent
        
        # Validation functions
        self.validators = {
            'positive': lambda x: x > 0,
            'in_range': lambda min_val, max_val: lambda x: min_val <= x <= max_val,
            'is_even': lambda x: x % 2 == 0,
            'not_empty': lambda collection: len(collection) > 0,
            'has_attribute': lambda attr: lambda obj: hasattr(obj, attr)
        }
    
    def _apply_pipeline(self, value, funcs):
        result = value
        for func in funcs:
            result = func(result)
        return result
    
    def create_processor_chain(self, operations):
        # Create a processing chain from operation names
        chain_funcs = [self.transforms[op] for op in operations if op in self.transforms]
        return lambda data: [
            self._apply_pipeline(item, chain_funcs)
            for item in data
            if isinstance(item, (int, float))
        ]
    
    def create_conditional_processor(self, conditions_and_transforms):
        # Create processor with multiple conditional branches
        def processor(value):
            for condition, transform in conditions_and_transforms:
                if condition(value):
                    return transform(value)
            return value  # No condition matched
        return processor
    
    def create_aggregator(self, group_by, aggregate_func):
        # Create aggregation function using lambdas
        return lambda data: {
            key: aggregate_func([item for item in data if group_by(item) == key])
            for key in set(group_by(item) for item in data)
        }

# Event handling with lambdas
class EventProcessor:
    def __init__(self):
        self.handlers = {}
        self.middleware = []
        
        # Default handlers using lambdas
        self.default_handlers = {
            'log': lambda event: print(f"[LOG] {event['message']}"),
            'error': lambda event: print(f"[ERROR] {event['error']} at {event['timestamp']}"),
            'debug': lambda event: print(f"[DEBUG] {event}") if event.get('debug_mode') else None,
            'metric': lambda event: self._record_metric(event['metric'], event['value'])
        }
        
        # Middleware functions
        self.timestamp_middleware = lambda event, next_handler: next_handler({
            **event, 'timestamp': self._get_current_timestamp()
        })
        
        self.validation_middleware = lambda required_fields: lambda event, next_handler: (
            next_handler(event) if all(field in event for field in required_fields)
            else self._handle_validation_error(event, required_fields)
        )
        
        self.rate_limit_middleware = lambda max_per_second: lambda event, next_handler: (
            next_handler(event) if self._check_rate_limit(event, max_per_second)
            else self._handle_rate_limit(event)
        )
        
        # Event transformers
        self.transformers = {
            'normalize': lambda event: {k.lower(): v for k, v in event.items()},
            'sanitize': lambda event: {
                k: v for k, v in event.items() 
                if not k.startswith('_') and v is not None
            },
            'enrich': lambda external_data: lambda event: {
                **event, 
                **self._get_enrichment_data(event, external_data)
            }
        }
        
        # Complex event processors
        self.batch_processor = lambda batch_size: lambda events: [
            self._process_batch(events[i:i+batch_size])
            for i in range(0, len(events), batch_size)
        ]
        
        self.priority_processor = lambda priority_func: lambda events: sorted(
            events, key=priority_func, reverse=True
        )
    
    def register_handler(self, event_type, handler_func):
        self.handlers[event_type] = handler_func
    
    def add_middleware(self, middleware_func):
        self.middleware.append(middleware_func)
    
    def process_event(self, event):
        # Apply middleware chain
        current_handler = self.handlers.get(
            event.get('type'), 
            self.default_handlers.get('log', lambda e: None)
        )
        
        # Apply middleware in reverse order
        for middleware in reversed(self.middleware):
            current_handler = lambda e, h=current_handler, m=middleware: m(e, h)
        
        return current_handler(event)
    
    def create_event_filter(self, filter_conditions):
        # Create complex event filter using lambda composition
        return lambda events: [
            event for event in events
            if all(condition(event) for condition in filter_conditions)
        ]
    
    def _get_current_timestamp(self):
        import time
        return time.time()
    
    def _record_metric(self, name, value):
        pass  # Placeholder for metric recording
    
    def _handle_validation_error(self, event, required_fields):
        pass  # Placeholder for validation error handling
    
    def _check_rate_limit(self, event, max_per_second):
        return True  # Placeholder for rate limiting
    
    def _handle_rate_limit(self, event):
        pass  # Placeholder for rate limit handling
    
    def _get_enrichment_data(self, event, external_data):
        return {}  # Placeholder for data enrichment
    
    def _process_batch(self, batch):
        return batch  # Placeholder for batch processing

# Data analysis with lambda expressions
class DataAnalyzer:
    def __init__(self):
        # Statistical functions
        self.stats = {
            'mean': lambda data: sum(data) / len(data) if data else 0,
            'median': lambda data: sorted(data)[len(data) // 2] if data else 0,
            'mode': lambda data: max(set(data), key=data.count) if data else None,
            'range': lambda data: max(data) - min(data) if data else 0,
            'variance': lambda data: sum((x - self.stats['mean'](data)) ** 2 for x in data) / len(data) if data else 0
        }
        
        # Data transformation functions
        self.transformers = {
            'normalize': lambda data: [(x - min(data)) / (max(data) - min(data)) for x in data] if data and max(data) != min(data) else data,
            'standardize': lambda data: [(x - self.stats['mean'](data)) / (self.stats['variance'](data) ** 0.5) for x in data] if data else [],
            'smooth': lambda window_size: lambda data: [
                sum(data[max(0, i-window_size//2):i+window_size//2+1]) / min(window_size, len(data[max(0, i-window_size//2):i+window_size//2+1]))
                for i in range(len(data))
            ],
            'outlier_removal': lambda threshold: lambda data: [
                x for x in data 
                if abs(x - self.stats['mean'](data)) <= threshold * (self.stats['variance'](data) ** 0.5)
            ]
        }
        
        # Grouping and aggregation
        self.group_by = lambda key_func: lambda data: {
            key: [item for item in data if key_func(item) == key]
            for key in set(key_func(item) for item in data)
        }
        
        self.aggregate = lambda agg_func: lambda grouped_data: {
            key: agg_func(values) for key, values in grouped_data.items()
        }
        
        # Complex analysis pipelines
        self.create_pipeline = lambda *operations: lambda data: self._apply_operations(data, operations)
        
        # Filtering and selection
        self.filters = {
            'above_threshold': lambda threshold: lambda data: [x for x in data if x > threshold],
            'below_threshold': lambda threshold: lambda data: [x for x in data if x < threshold],
            'in_percentile': lambda low, high: lambda data: self._percentile_filter(data, low, high),
            'not_null': lambda data: [x for x in data if x is not None],
            'unique': lambda data: list(set(data))
        }
    
    def _apply_operations(self, data, operations):
        result = data
        for operation in operations:
            result = operation(result)
        return result
    
    def _percentile_filter(self, data, low_percentile, high_percentile):
        sorted_data = sorted(data)
        low_index = int(len(sorted_data) * low_percentile / 100)
        high_index = int(len(sorted_data) * high_percentile / 100)
        low_threshold = sorted_data[low_index] if sorted_data else float('-inf')
        high_threshold = sorted_data[high_index] if sorted_data else float('inf')
        return [x for x in data if low_threshold <= x <= high_threshold]
""",
            """
# Configuration management with lambdas
class ConfigManager:
    def __init__(self):
        # Configuration validators
        self.validators = {
            'string': lambda value: isinstance(value, str),
            'non_empty_string': lambda value: isinstance(value, str) and len(value) > 0,
            'positive_int': lambda value: isinstance(value, int) and value > 0,
            'percentage': lambda value: isinstance(value, (int, float)) and 0 <= value <= 100,
            'url': lambda value: isinstance(value, str) and value.startswith(('http://', 'https://')),
            'email': lambda value: isinstance(value, str) and '@' in value and '.' in value.split('@')[-1]
        }
        
        # Configuration transformers
        self.transformers = {
            'to_int': lambda value: int(value) if str(value).isdigit() else value,
            'to_float': lambda value: float(value) if isinstance(value, (str, int, float)) else value,
            'to_bool': lambda value: value.lower() in ('true', '1', 'yes', 'on') if isinstance(value, str) else bool(value),
            'strip_whitespace': lambda value: value.strip() if isinstance(value, str) else value,
            'to_lowercase': lambda value: value.lower() if isinstance(value, str) else value,
            'expand_path': lambda value: os.path.expanduser(value) if isinstance(value, str) and value.startswith('~') else value
        }
        
        # Default value providers
        self.defaults = {
            'environment': lambda key: os.environ.get(key),
            'computed': lambda func: func(),
            'conditional': lambda condition, true_value, false_value: true_value if condition() else false_value,
            'fallback_chain': lambda *providers: next((p() for p in providers if p() is not None), None)
        }
        
        # Configuration rules
        self.rules = {
            'required': lambda config, key: key in config and config[key] is not None,
            'one_of': lambda choices: lambda config, key: config.get(key) in choices,
            'depends_on': lambda dependency: lambda config, key: dependency not in config or config[key] is not None,
            'mutually_exclusive': lambda other_key: lambda config, key: not (key in config and other_key in config)
        }
    
    def create_validator(self, schema):
        # Create validator from schema using lambdas
        return lambda config: all(
            self._validate_field(config, field, rules)
            for field, rules in schema.items()
        )
    
    def create_transformer(self, transformation_map):
        # Create transformer pipeline
        return lambda config: {
            key: self._apply_transformations(value, transformation_map.get(key, []))
            for key, value in config.items()
        }
    
    def create_config_merger(self, merge_strategies):
        # Create configuration merger with custom strategies
        return lambda *configs: self._merge_configs(configs, merge_strategies)
    
    def _validate_field(self, config, field, rules):
        for rule in rules:
            if not rule(config, field):
                return False
        return True
    
    def _apply_transformations(self, value, transformations):
        result = value
        for transform in transformations:
            result = self.transformers[transform](result)
        return result
    
    def _merge_configs(self, configs, strategies):
        result = {}
        for config in configs:
            for key, value in config.items():
                if key not in result:
                    result[key] = value
                else:
                    strategy = strategies.get(key, 'override')
                    if strategy == 'override':
                        result[key] = value
                    elif strategy == 'merge_list':
                        if isinstance(result[key], list) and isinstance(value, list):
                            result[key].extend(value)
                    elif strategy == 'merge_dict':
                        if isinstance(result[key], dict) and isinstance(value, dict):
                            result[key].update(value)
        return result
"""
        ]
        
        for source in comprehensive_patterns:
            tree = tester.assert_lambda_expression_parses(source)
            
            # Should have extensive lambda usage
            lambdas = tester.get_lambda_expressions(source)
            assert len(lambdas) >= 10, f"Should have many lambda expressions: {source}"
            
            # Should have various complexity levels
            max_depth = tester.count_nested_lambdas(source)
            assert max_depth >= 1, f"Should have lambda expressions: {source}"
    
    def test_lambda_introspection(self, tester):
        """Test ability to analyze lambda expressions programmatically"""
        # Test programmatic analysis of lambda structure
        introspection_source = """
def lambda_examples():
    # Simple lambdas
    identity = lambda x: x
    square = lambda x: x ** 2
    
    # Lambdas with defaults
    multiply = lambda x, factor=2: x * factor
    greet = lambda name, greeting="Hello": f"{greeting}, {name}"
    
    # Lambdas with variable arguments
    sum_all = lambda *args: sum(args)
    create_dict = lambda **kwargs: kwargs
    flexible = lambda x, *args, **kwargs: (x, args, kwargs)
    
    # Nested lambdas
    curried_add = lambda x: lambda y: x + y
    compose = lambda f: lambda g: lambda x: f(g(x))
    
    # Lambdas in data structures
    processors = [
        lambda x: x * 2,
        lambda x: x + 1,
        lambda x: x ** 0.5
    ]
    
    operations = {
        'double': lambda x: x * 2,
        'halve': lambda x: x / 2,
        'negate': lambda x: -x
    }
    
    return identity, square, multiply, greet, sum_all, create_dict, flexible, curried_add, compose, processors, operations
"""
        
        tree = tester.assert_lambda_expression_parses(introspection_source)
        
        # Should identify all lambda expressions
        lambdas = tester.get_lambda_expressions(introspection_source)
        assert len(lambdas) >= 10, "Should have multiple lambda expressions"
        
        # Should identify parameter patterns
        param_counts = tester.count_lambda_parameters(introspection_source)
        assert param_counts['positional'] >= 5, "Should have positional parameters"
        assert param_counts['defaults'] >= 2, "Should have default parameters"
        assert param_counts['varargs'] >= 1, "Should have varargs"
        assert param_counts['kwargs'] >= 1, "Should have kwargs"
        
        # Should identify nesting
        nesting_depth = tester.count_nested_lambdas(introspection_source)
        assert nesting_depth >= 2, "Should have nested lambdas"
        
        # All lambdas should have proper structure
        for lambda_node in lambdas:
            assert isinstance(lambda_node, ast.Lambda), "Should be Lambda node"
            assert lambda_node.args is not None, "Should have arguments"
            assert lambda_node.body is not None, "Should have body expression"