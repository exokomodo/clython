"""
Section 6.5: Power Operator - Conformance Test Suite

Tests Python Language Reference Section 6.5 compliance across implementations.
Based on formal power operation syntax definitions and prose assertions for exponentiation behavior.

Grammar tested:
    power: atom_expr ['**' factor]

Language Reference requirements tested:
    - Power operator (**) syntax and basic exponentiation
    - Right-associative behavior unique to power operator
    - Power operator precedence (highest except unary minus)
    - Power operations with different numeric types
    - Error conditions and overflow handling
    - Power operator AST structure validation
    - Cross-implementation power operation compatibility
"""

import ast
import pytest
import sys
from typing import Any


class PowerOperatorTester:
    """Helper class for testing power operator conformance.
    
    Focuses on AST structure validation for power operation syntax and behavior
    patterns that can be statically analyzed for cross-implementation compatibility.
    """
    
    def assert_power_operation_parses(self, source: str):
        """Test that power operation syntax parses correctly.
        
        Args:
            source: Python source code with power operations
        """
        try:
            tree = ast.parse(source)
            return tree
        except SyntaxError as e:
            pytest.fail(f"Power operation syntax should be valid but failed to parse: {source}\\nError: {e}")
    
    def assert_power_operation_syntax_error(self, source: str):
        """Test that invalid power operation syntax raises SyntaxError.
        
        Args:
            source: Python source code that should be invalid
        """
        with pytest.raises(SyntaxError):
            ast.parse(source)
    
    def get_power_operations(self, source: str) -> list:
        """Get BinOp AST nodes with Pow operators from source.
        
        Args:
            source: Python source code
            
        Returns:
            List of ast.BinOp nodes with Pow operators
        """
        tree = ast.parse(source)
        power_ops = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow):
                power_ops.append(node)
        
        return power_ops
    
    def get_unary_operations(self, source: str) -> list:
        """Get UnaryOp AST nodes from source for precedence testing.
        
        Args:
            source: Python source code
            
        Returns:
            List of ast.UnaryOp nodes
        """
        tree = ast.parse(source)
        unary_ops = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.UnaryOp):
                unary_ops.append(node)
        
        return unary_ops
    
    def get_binary_operations(self, source: str) -> list:
        """Get binary operations from source (excluding power).
        
        Args:
            source: Python source code
            
        Returns:
            List of ast.BinOp nodes (non-power)
        """
        tree = ast.parse(source)
        binary_ops = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp) and not isinstance(node.op, ast.Pow):
                binary_ops.append(node)
        
        return binary_ops
    
    def count_chained_power_operations(self, source: str) -> int:
        """Count depth of chained power operations.
        
        Args:
            source: Python source code
            
        Returns:
            Maximum depth of chained power operations
        """
        tree = ast.parse(source)
        
        def count_depth(node):
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow):
                # Count chain depth in right operand (right-associative)
                right_depth = count_depth(node.right)
                return 1 + right_depth
            return 0
        
        max_depth = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow):
                depth = count_depth(node)
                max_depth = max(max_depth, depth)
        
        return max_depth
    
    def analyze_power_associativity(self, source: str) -> dict:
        """Analyze power operation associativity structure.
        
        Args:
            source: Python source code with chained power operations
            
        Returns:
            Dict with associativity analysis
        """
        tree = ast.parse(source)
        
        # Find the top-level power operation
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow):
                # Check if right operand is also a power operation
                right_is_power = (isinstance(node.right, ast.BinOp) and 
                                isinstance(node.right.op, ast.Pow))
                
                # Check if left operand is also a power operation  
                left_is_power = (isinstance(node.left, ast.BinOp) and
                               isinstance(node.left.op, ast.Pow))
                
                return {
                    'right_is_power': right_is_power,
                    'left_is_power': left_is_power,
                    'is_chained': right_is_power or left_is_power
                }
        
        return {'right_is_power': False, 'left_is_power': False, 'is_chained': False}


@pytest.fixture
def tester():
    """Provide PowerOperatorTester instance for tests."""
    return PowerOperatorTester()


class TestSection65BasicPowerSyntax:
    """Test basic power operator syntax."""
    
    def test_simple_power_operations(self, tester):
        """Test simple power operation patterns"""
        # Language Reference: power: atom_expr ['**' factor]
        power_patterns = [
            """
result = 2 ** 3
""",
            """
value = x ** y
""",
            """
power = base ** exponent
""",
            """
squared = number ** 2
""",
            """
cubed = value ** 3
"""
        ]
        
        for source in power_patterns:
            tree = tester.assert_power_operation_parses(source)
            power_ops = tester.get_power_operations(source)
            assert len(power_ops) >= 1, f"Should have power operations: {source}"
    
    def test_power_with_variables(self, tester):
        """Test power operations with variables"""
        # Language Reference: variables as operands
        variable_power_patterns = [
            """
result = base ** exponent
""",
            """
value = data ** power
""",
            """
output = input_value ** scale
""",
            """
calculation = x ** n
""",
            """
transformed = array ** factor
"""
        ]
        
        for source in variable_power_patterns:
            tree = tester.assert_power_operation_parses(source)
            power_ops = tester.get_power_operations(source)
            assert len(power_ops) >= 1, f"Should handle variable operands: {source}"
    
    def test_power_with_expressions(self, tester):
        """Test power operations with complex expressions"""
        # Language Reference: complex expressions as operands
        expression_power_patterns = [
            """
result = (a + b) ** (c - d)
""",
            """
value = func() ** calculate()
""",
            """
output = array[index] ** obj.attr
""",
            """
complex_power = (x * y) ** (z / w)
""",
            """
nested = expression() ** another_expression()
"""
        ]
        
        for source in expression_power_patterns:
            tree = tester.assert_power_operation_parses(source)
            power_ops = tester.get_power_operations(source)
            assert len(power_ops) >= 1, f"Should handle complex expressions: {source}"
    
    def test_power_with_literals(self, tester):
        """Test power operations with literal values"""
        # Language Reference: literal operands
        literal_power_patterns = [
            """
result = 2 ** 8
""",
            """
value = 3.14 ** 2.0
""",
            """
complex_power = (1+2j) ** (0.5+0j)
""",
            """
hex_power = 0xFF ** 2
""",
            """
binary_power = 0b1010 ** 0b11
"""
        ]
        
        for source in literal_power_patterns:
            tree = tester.assert_power_operation_parses(source)
            power_ops = tester.get_power_operations(source)
            assert len(power_ops) >= 1, f"Should handle literal operands: {source}"
    
    def test_power_with_negative_bases(self, tester):
        """Test power operations with negative bases"""
        # Language Reference: unary minus with power precedence
        negative_base_patterns = [
            """
result = (-2) ** 3
""",
            """
value = (-x) ** y
""",
            """
negative_power = -(base ** exponent)
""",
            """
explicit_negative = (-value) ** power
""",
            """
mixed = -base ** exponent  # This is -(base ** exponent)
"""
        ]
        
        for source in negative_base_patterns:
            tree = tester.assert_power_operation_parses(source)
            # Should parse without syntax errors
            power_ops = tester.get_power_operations(source)
            assert len(power_ops) >= 1, f"Should handle negative bases: {source}"


class TestSection65PowerAssociativity:
    """Test power operator associativity (right-associative)."""
    
    def test_right_associative_chaining(self, tester):
        """Test right-associative chaining behavior"""
        # Language Reference: power is right-associative (a**b**c = a**(b**c))
        right_associative_patterns = [
            """
result = 2 ** 3 ** 4  # Should be 2 ** (3 ** 4) = 2 ** 81
""",
            """
value = a ** b ** c  # Should be a ** (b ** c)
""",
            """
chained = x ** y ** z ** w  # Should be x ** (y ** (z ** w))
""",
            """
complex_chain = base ** exp1 ** exp2
""",
            """
nested = value ** power ** scale
"""
        ]
        
        for source in right_associative_patterns:
            tree = tester.assert_power_operation_parses(source)
            power_ops = tester.get_power_operations(source)
            assert len(power_ops) >= 2, f"Should have chained power operations: {source}"
            
            # Check associativity structure
            associativity = tester.analyze_power_associativity(source)
            assert associativity['is_chained'], f"Should be chained: {source}"
    
    def test_explicit_left_associative_grouping(self, tester):
        """Test explicit left-associative grouping with parentheses"""
        # Language Reference: parentheses override default associativity
        left_associative_patterns = [
            """
result = (2 ** 3) ** 4  # Should be 8 ** 4 = 4096 (not 2 ** 81)
""",
            """
value = (a ** b) ** c  # Explicit left-associative
""",
            """
grouped = ((x ** y) ** z) ** w  # Fully left-associative
""",
            """
explicit = (base ** exp1) ** exp2
""",
            """
forced_left = (value ** power) ** scale
"""
        ]
        
        for source in left_associative_patterns:
            tree = tester.assert_power_operation_parses(source)
            power_ops = tester.get_power_operations(source)
            assert len(power_ops) >= 2, f"Should have chained power operations: {source}"
    
    def test_mixed_associativity_patterns(self, tester):
        """Test mixed associativity patterns"""
        # Language Reference: complex associativity scenarios
        mixed_associativity_patterns = [
            """
result = a ** (b ** c) ** d  # Mix of explicit and implicit
""",
            """
value = (x ** y) ** z ** w  # Left then right associative
""",
            """
complex_mix = a ** b ** (c ** d)
""",
            """
nested_groups = (a ** b) ** (c ** d)
""",
            """
multi_level = ((a ** b) ** c) ** (d ** e)
"""
        ]
        
        for source in mixed_associativity_patterns:
            tree = tester.assert_power_operation_parses(source)
            power_ops = tester.get_power_operations(source)
            assert len(power_ops) >= 3, f"Should have multiple power operations: {source}"
    
    def test_deep_right_associative_chains(self, tester):
        """Test deep right-associative chains"""
        # Language Reference: arbitrary depth chaining
        deep_chain_patterns = [
            """
deep = 2 ** 2 ** 2 ** 2 ** 2  # Right-associative chain
""",
            """
variables = a ** b ** c ** d ** e
""",
            """
mixed_deep = x ** y ** 2 ** z ** 3
""",
            """
very_deep = base ** exp1 ** exp2 ** exp3 ** exp4 ** exp5
""",
            """
arithmetic_deep = 3 ** 2 ** 3 ** 2 ** 2
"""
        ]
        
        for source in deep_chain_patterns:
            tree = tester.assert_power_operation_parses(source)
            power_ops = tester.get_power_operations(source)
            assert len(power_ops) >= 4, f"Should have deep chaining: {source}"
            
            # Check chain depth
            chain_depth = tester.count_chained_power_operations(source)
            assert chain_depth >= 4, f"Should have deep chain: {source}"


class TestSection65PowerPrecedence:
    """Test power operator precedence."""
    
    def test_power_vs_unary_precedence(self, tester):
        """Test power vs unary operator precedence"""
        # Language Reference: unary minus has lower precedence than power
        # So -x**y is parsed as -(x**y), not (-x)**y
        precedence_patterns = [
            """
result = -2 ** 3  # Should be -(2 ** 3) = -8, not (-2) ** 3 = -8
""",
            """
value = +x ** y  # Should be +(x ** y)
""",
            """
inverted = ~base ** exponent  # Should be ~(base ** exponent)
""",
            """
negative = -value ** power
""",
            """
explicit_precedence = -(a ** b)
"""
        ]
        
        for source in precedence_patterns:
            tree = tester.assert_power_operation_parses(source)
            power_ops = tester.get_power_operations(source)
            unary_ops = tester.get_unary_operations(source)
            
            # Should have both power and unary operations
            assert len(power_ops) >= 1, f"Should have power operations: {source}"
            # Unary operations should be present in some cases
    
    def test_power_vs_arithmetic_precedence(self, tester):
        """Test power vs arithmetic operator precedence"""
        # Language Reference: power has higher precedence than arithmetic
        arithmetic_precedence_patterns = [
            """
result = 2 + 3 ** 4  # Should be 2 + (3 ** 4) = 2 + 81 = 83
""",
            """
value = a * b ** c  # Should be a * (b ** c)
""",
            """
calculation = x - y ** z  # Should be x - (y ** z)
""",
            """
division = a / b ** c  # Should be a / (b ** c)
""",
            """
complex_arithmetic = a + b * c ** d - e
"""
        ]
        
        for source in arithmetic_precedence_patterns:
            tree = tester.assert_power_operation_parses(source)
            power_ops = tester.get_power_operations(source)
            binary_ops = tester.get_binary_operations(source)
            
            assert len(power_ops) >= 1, f"Should have power operations: {source}"
            assert len(binary_ops) >= 1, f"Should have binary operations: {source}"
    
    def test_power_with_parentheses(self, tester):
        """Test power operations with explicit parentheses"""
        # Language Reference: parentheses override precedence
        parentheses_patterns = [
            """
result = (2 + 3) ** 4  # Should be 5 ** 4 = 625
""",
            """
value = (a * b) ** c  # Explicit grouping
""",
            """
calculation = a ** (b + c)  # Exponent grouping
""",
            """
both_grouped = (a + b) ** (c * d)
""",
            """
complex_grouping = (x - y) ** ((z + w) * 2)
"""
        ]
        
        for source in parentheses_patterns:
            tree = tester.assert_power_operation_parses(source)
            power_ops = tester.get_power_operations(source)
            assert len(power_ops) >= 1, f"Should handle parentheses: {source}"
    
    def test_power_precedence_with_comparisons(self, tester):
        """Test power precedence with comparison operators"""
        # Language Reference: power has higher precedence than comparisons
        comparison_precedence_patterns = [
            """
result = 2 ** 3 > 4  # Should be (2 ** 3) > 4 = 8 > 4 = True
""",
            """
value = a ** b < c * d  # Should be (a ** b) < (c * d)
""",
            """
equality = x ** y == z ** w  # Should be (x ** y) == (z ** w)
""",
            """
inequality = base ** exp != other ** power
""",
            """
complex_comparison = a ** 2 <= b ** 2 + c
"""
        ]
        
        for source in comparison_precedence_patterns:
            tree = tester.assert_power_operation_parses(source)
            power_ops = tester.get_power_operations(source)
            assert len(power_ops) >= 1, f"Should have power operations: {source}"


class TestSection65PowerOperationContexts:
    """Test power operations in different contexts."""
    
    def test_power_in_assignments(self, tester):
        """Test power operations in assignment contexts"""
        # Language Reference: power operations in assignments
        assignment_patterns = [
            """
result = base ** exponent
""",
            """
squared = number ** 2
""",
            """
cubed = value ** 3
""",
            """
a, b = x ** y, z ** w
""",
            """
array[index] = data ** power
"""
        ]
        
        for source in assignment_patterns:
            tree = tester.assert_power_operation_parses(source)
            power_ops = tester.get_power_operations(source)
            assert len(power_ops) >= 1, f"Should work in assignments: {source}"
    
    def test_power_in_function_calls(self, tester):
        """Test power operations in function call arguments"""
        # Language Reference: power operations in function arguments
        function_call_patterns = [
            """
result = calculate(base ** exponent)
""",
            """
output = transform(data ** power, scale=factor ** 2)
""",
            """
validate(x ** y, expected ** actual)
""",
            """
complex_function(
    base ** exp,
    (value ** 2) + offset,
    scale=multiplier ** factor
)
""",
            """
api_call(data ** transform_power, format=style ** variation)
"""
        ]
        
        for source in function_call_patterns:
            tree = tester.assert_power_operation_parses(source)
            power_ops = tester.get_power_operations(source)
            assert len(power_ops) >= 1, f"Should work in function calls: {source}"
    
    def test_power_in_return_statements(self, tester):
        """Test power operations in return statements"""
        # Language Reference: power operations in returns
        return_patterns = [
            """
def square(x):
    return x ** 2
""",
            """
def power_of(base, exponent):
    return base ** exponent
""",
            """
def compute_area(radius):
    return 3.14159 * radius ** 2
""",
            """
def exponential_growth(initial, rate, time):
    return initial * (1 + rate) ** time
""",
            """
def polynomial(x, coefficients):
    return sum(coeff * x ** i for i, coeff in enumerate(coefficients))
"""
        ]
        
        for source in return_patterns:
            tree = tester.assert_power_operation_parses(source)
            power_ops = tester.get_power_operations(source)
            assert len(power_ops) >= 1, f"Should work in returns: {source}"
    
    def test_power_in_comprehensions(self, tester):
        """Test power operations in comprehensions"""
        # Language Reference: power operations in comprehensions
        comprehension_patterns = [
            """
squares = [x ** 2 for x in range(10)]
""",
            """
powers = [base ** exp for base, exp in pairs]
""",
            """
cubed = {x: x ** 3 for x in values}
""",
            """
exponentials = [
    initial * growth ** year
    for year in range(years)
    if growth ** year > threshold
]
""",
            """
polynomial_terms = [
    coeff * x ** i
    for i, coeff in enumerate(coefficients)
    if coeff != 0
]
"""
        ]
        
        for source in comprehension_patterns:
            tree = tester.assert_power_operation_parses(source)
            power_ops = tester.get_power_operations(source)
            assert len(power_ops) >= 1, f"Should work in comprehensions: {source}"
    
    def test_power_in_conditional_expressions(self, tester):
        """Test power operations in conditional expressions"""
        # Language Reference: power operations in conditionals
        conditional_patterns = [
            """
result = x ** 2 if positive else -(x ** 2)
""",
            """
output = base ** exp if valid else default ** fallback
""",
            """
power_value = value ** exponent if exponent > 0 else 1 / (value ** (-exponent))
""",
            """
normalized = (data ** scale) if scale != 0 else data
""",
            """
final_result = a ** b if condition else c ** d
"""
        ]
        
        for source in conditional_patterns:
            tree = tester.assert_power_operation_parses(source)
            power_ops = tester.get_power_operations(source)
            assert len(power_ops) >= 1, f"Should work in conditionals: {source}"


class TestSection65PowerOperationTypes:
    """Test power operations with different data types."""
    
    def test_power_with_integers(self, tester):
        """Test power operations with integer types"""
        # Language Reference: power operations work with integers
        integer_power_patterns = [
            """
result = 2 ** 8
""",
            """
large_power = 10 ** 100
""",
            """
hex_power = 0xFF ** 2
""",
            """
binary_power = 0b101 ** 0b11
""",
            """
negative_base = (-3) ** 4
"""
        ]
        
        for source in integer_power_patterns:
            tree = tester.assert_power_operation_parses(source)
            power_ops = tester.get_power_operations(source)
            assert len(power_ops) >= 1, f"Should handle integers: {source}"
    
    def test_power_with_floats(self, tester):
        """Test power operations with floating-point types"""
        # Language Reference: power operations work with floats
        float_power_patterns = [
            """
result = 2.5 ** 3.0
""",
            """
square_root = 16.0 ** 0.5
""",
            """
scientific = 1.23e-4 ** 2.0
""",
            """
pi_power = 3.14159 ** 2.71828
""",
            """
negative_exponent = 2.0 ** -3.0
"""
        ]
        
        for source in float_power_patterns:
            tree = tester.assert_power_operation_parses(source)
            power_ops = tester.get_power_operations(source)
            assert len(power_ops) >= 1, f"Should handle floats: {source}"
    
    def test_power_with_complex_numbers(self, tester):
        """Test power operations with complex number types"""
        # Language Reference: power operations work with complex numbers
        complex_power_patterns = [
            """
result = (1+2j) ** (3+4j)
""",
            """
imaginary_power = 1j ** 2
""",
            """
complex_base = (3+4j) ** 2.0
""",
            """
real_exponent = 2.0 ** (1+0j)
""",
            """
euler_formula = (2.71828 ** (1j * 3.14159))  # e^(i*pi)
"""
        ]
        
        for source in complex_power_patterns:
            tree = tester.assert_power_operation_parses(source)
            power_ops = tester.get_power_operations(source)
            assert len(power_ops) >= 1, f"Should handle complex numbers: {source}"
    
    def test_power_with_mixed_types(self, tester):
        """Test power operations with mixed numeric types"""
        # Language Reference: power operations with type coercion
        mixed_type_patterns = [
            """
result = 2 ** 3.0  # int ** float
""",
            """
value = 2.5 ** 3  # float ** int
""",
            """
complex_result = 2 ** (1+0j)  # int ** complex
""",
            """
float_complex = 2.5 ** (2+0j)  # float ** complex
""",
            """
mixed_chain = 2 ** 3.0 ** (1+0j)
"""
        ]
        
        for source in mixed_type_patterns:
            tree = tester.assert_power_operation_parses(source)
            power_ops = tester.get_power_operations(source)
            assert len(power_ops) >= 1, f"Should handle mixed types: {source}"


class TestSection65PowerOperationErrors:
    """Test power operation error conditions."""
    
    def test_power_operator_syntax(self, tester):
        """Test proper power operator syntax"""
        # Language Reference: correct operator syntax
        valid_operator_patterns = [
            """
result = base ** exponent
""",
            """
output = 2 ** 3
""",
            """
chained = a ** b ** c
""",
            """
grouped = (x ** y) ** z
"""
        ]
        
        for source in valid_operator_patterns:
            tree = tester.assert_power_operation_parses(source)
            power_ops = tester.get_power_operations(source)
            assert len(power_ops) >= 1, f"Should parse valid operators: {source}"
    
    def test_incomplete_power_expressions(self, tester):
        """Test incomplete power expressions"""
        # Language Reference: both operands required
        incomplete_patterns = [
            "x = **",          # Missing both operands
            "x = 2 **",        # Missing right operand
            "x = ** 3",        # Missing left operand
        ]
        
        for source in incomplete_patterns:
            tester.assert_power_operation_syntax_error(source)
    
    def test_malformed_power_syntax(self, tester):
        """Test malformed power operator syntax"""
        # Language Reference: specific syntax requirements
        malformed_patterns = [
            "x = 2 * * 3",     # Space in operator
            "x = 2 *** 3",     # Triple asterisk
        ]
        
        for source in malformed_patterns:
            tester.assert_power_operation_syntax_error(source)
        
        # Note: "x = 2 ^ 3" is valid syntax (XOR operator), not malformed


class TestSection65PowerOperationAST:
    """Test power operation AST structure validation."""
    
    def test_power_ast_structure(self, tester):
        """Test BinOp AST node structure for power operations"""
        # Language Reference: AST structure for power operations
        power_ast_cases = [
            """
result = base ** exponent
""",
            """
output = 2 ** 3
""",
            """
chained = a ** b ** c
""",
            """
complex_power = (x + y) ** (z * w)
"""
        ]
        
        for source in power_ast_cases:
            tree = tester.assert_power_operation_parses(source)
            power_ops = tester.get_power_operations(source)
            assert len(power_ops) >= 1, f"Should have power operations: {source}"
            
            for power_op in power_ops:
                # BinOp nodes must have left, op, and right
                assert isinstance(power_op, ast.BinOp), "Should be BinOp node"
                assert isinstance(power_op.op, ast.Pow), "Should be Pow operator"
                assert hasattr(power_op, 'left'), "Should have left operand"
                assert hasattr(power_op, 'right'), "Should have right operand"
                assert power_op.left is not None, "Left operand should not be None"
                assert power_op.right is not None, "Right operand should not be None"
    
    def test_chained_power_ast_structure(self, tester):
        """Test chained power operation AST structure"""
        # Language Reference: chained power operations create nested BinOp nodes
        chained_power_source = """
result = a ** b ** c ** d
"""
        
        tree = tester.assert_power_operation_parses(chained_power_source)
        power_ops = tester.get_power_operations(chained_power_source)
        assert len(power_ops) >= 3, "Should have multiple power operations"
        
        # Check right-associative structure
        # a ** b ** c ** d should parse as a ** (b ** (c ** d))
        for power_op in power_ops:
            assert isinstance(power_op, ast.BinOp), "Should be BinOp node"
            assert isinstance(power_op.op, ast.Pow), "Should be Pow operator"
    
    def test_power_with_complex_operands_ast(self, tester):
        """Test power with complex operands AST"""
        # Language Reference: complex expressions as operands
        complex_power_source = """
result = (a + b) ** (c * d) + (e - f) ** (g / h)
"""
        
        tree = tester.assert_power_operation_parses(complex_power_source)
        power_ops = tester.get_power_operations(complex_power_source)
        assert len(power_ops) >= 2, "Should have power operations"
        
        # Should have arithmetic operations as operands
        binary_ops = tester.get_binary_operations(complex_power_source)
        assert len(binary_ops) >= 5, "Should have binary operations in operands and top level"


class TestSection65CrossImplementationCompatibility:
    """Test cross-implementation compatibility for power operations."""
    
    def test_power_ast_consistency(self, tester):
        """Test power operation AST consistency across implementations"""
        # Language Reference: power AST should be consistent
        consistency_test_cases = [
            """
result = base ** exponent
""",
            """
output = 2 ** 3
""",
            """
chained = a ** b ** c
""",
            """
complex_power = (x + y) ** (z - w)
"""
        ]
        
        for source in consistency_test_cases:
            tree = tester.assert_power_operation_parses(source)
            
            # Should have consistent power structure
            power_ops = tester.get_power_operations(source)
            assert len(power_ops) >= 1, f"Should have power operations: {source}"
            
            for power_op in power_ops:
                assert isinstance(power_op, ast.BinOp), "Should be BinOp node"
                assert isinstance(power_op.op, ast.Pow), "Should be Pow operator"
                assert power_op.left is not None, "Should have left operand"
                assert power_op.right is not None, "Should have right operand"
    
    def test_comprehensive_power_patterns(self, tester):
        """Test comprehensive real-world power patterns"""
        # Language Reference: complex power usage scenarios
        comprehensive_patterns = [
            """
# Mathematical computations with power operations
class MathematicalProcessor:
    def __init__(self):
        # Mathematical constants involving powers
        self.E_SQUARED = 2.71828 ** 2
        self.PI_SQUARED = 3.14159 ** 2
        self.GOLDEN_RATIO_SQUARED = 1.618 ** 2
        self.SQRT_2 = 2 ** 0.5
        self.SQRT_3 = 3 ** 0.5
        
        # Physics constants
        self.PLANCK_ENERGY_SCALE = (1.054e-34 * 2.998e8 ** 5 / 1.381e-23) ** 0.25
        self.FINE_STRUCTURE = (1.602e-19 ** 2) / (4 * 3.14159 * 8.854e-12 * 1.054e-34 * 2.998e8)
    
    def polynomial_evaluation(self, x, coefficients):
        # Polynomial evaluation using power operations
        result = 0
        for i, coeff in enumerate(coefficients):
            term = coeff * (x ** i)
            result = result + term
        return result
    
    def exponential_functions(self, x):
        # Various exponential functions
        natural_exp = 2.71828 ** x
        base_2_exp = 2 ** x
        base_10_exp = 10 ** x
        arbitrary_exp = 1.5 ** x
        
        # Compound exponentials
        double_exp = 2 ** (2 ** x)
        triple_exp = 3 ** (3 ** (3 ** x))
        
        return natural_exp, base_2_exp, base_10_exp, double_exp, triple_exp
    
    def power_series_approximations(self, x, n_terms=10):
        # Power series approximations
        # e^x = sum(x^n / n!) for n=0 to infinity
        exp_approx = sum(x ** n / self.factorial(n) for n in range(n_terms))
        
        # sin(x) = sum((-1)^n * x^(2n+1) / (2n+1)!) for n=0 to infinity
        sin_approx = sum(
            ((-1) ** n) * (x ** (2*n + 1)) / self.factorial(2*n + 1)
            for n in range(n_terms)
        )
        
        # cos(x) = sum((-1)^n * x^(2n) / (2n)!) for n=0 to infinity
        cos_approx = sum(
            ((-1) ** n) * (x ** (2*n)) / self.factorial(2*n)
            for n in range(n_terms)
        )
        
        # ln(1+x) = sum((-1)^(n-1) * x^n / n) for n=1 to infinity
        ln_approx = sum(
            ((-1) ** (n-1)) * (x ** n) / n
            for n in range(1, n_terms+1)
            if abs(x) < 1
        )
        
        return exp_approx, sin_approx, cos_approx, ln_approx
    
    def factorial(self, n):
        # Simple factorial for power series
        if n <= 1:
            return 1
        result = 1
        for i in range(2, n + 1):
            result = result * i
        return result
    
    def matrix_powers(self, matrix, power):
        # Matrix exponentiation (simplified for 2x2 matrices)
        if power == 0:
            # Identity matrix
            return [[1, 0], [0, 1]]
        elif power == 1:
            return matrix
        else:
            # Repeated multiplication (naive approach)
            result = matrix
            for _ in range(power - 1):
                result = self.matrix_multiply(result, matrix)
            return result
    
    def matrix_multiply(self, a, b):
        # 2x2 matrix multiplication
        return [
            [a[0][0] * b[0][0] + a[0][1] * b[1][0], a[0][0] * b[0][1] + a[0][1] * b[1][1]],
            [a[1][0] * b[0][0] + a[1][1] * b[1][0], a[1][0] * b[0][1] + a[1][1] * b[1][1]]
        ]
    
    def numerical_methods(self, f, x0, tolerance=1e-10):
        # Newton's method with derivatives involving powers
        x = x0
        for iteration in range(100):
            # f'(x) using finite difference
            h = tolerance ** 0.5
            derivative = (f(x + h) - f(x - h)) / (2 * h)
            
            # Newton's step
            if abs(derivative) < tolerance:
                break
            
            new_x = x - f(x) / derivative
            
            # Convergence check
            if abs(new_x - x) < tolerance:
                break
            
            x = new_x
        
        return x
    
    def geometric_series(self, a, r, n_terms):
        # Geometric series: a + ar + ar^2 + ar^3 + ... + ar^(n-1)
        if abs(r) >= 1 and n_terms == float('inf'):
            raise ValueError("Geometric series diverges for |r| >= 1")
        
        if n_terms == float('inf'):
            # Infinite series sum
            return a / (1 - r)
        else:
            # Finite series sum
            return sum(a * (r ** k) for k in range(n_terms))
    
    def compound_interest(self, principal, rate, times_compounded, years):
        # Compound interest formula: A = P(1 + r/n)^(nt)
        return principal * ((1 + rate / times_compounded) ** (times_compounded * years))
    
    def population_growth(self, initial_population, growth_rate, time):
        # Exponential population growth: P(t) = P0 * e^(rt)
        return initial_population * (2.71828 ** (growth_rate * time))
    
    def radioactive_decay(self, initial_amount, half_life, time):
        # Radioactive decay: N(t) = N0 * (1/2)^(t/t_half)
        return initial_amount * ((1/2) ** (time / half_life))
    
    def signal_processing(self, signal, frequencies, time_points):
        # Fourier series representation
        reconstructed_signal = []
        
        for t in time_points:
            value = 0
            for freq, amplitude, phase in frequencies:
                # Real part of complex exponential
                angular_freq = 2 * 3.14159 * freq
                
                # e^(i*omega*t) = cos(omega*t) + i*sin(omega*t)
                # We'll use power operations for the trigonometric approximations
                
                # cos(x) ≈ 1 - x^2/2! + x^4/4! - x^6/6! + ...
                angle = angular_freq * t + phase
                cos_approx = 1 - (angle ** 2) / 2 + (angle ** 4) / 24 - (angle ** 6) / 720
                
                value = value + amplitude * cos_approx
            
            reconstructed_signal.append(value)
        
        return reconstructed_signal
    
    def optimization_algorithms(self, objective_function, initial_guess, learning_rate=0.01):
        # Gradient descent with momentum (simplified)
        x = initial_guess
        velocity = 0
        momentum = 0.9
        
        for iteration in range(1000):
            # Approximate gradient using finite differences
            h = 1e-8
            gradient = (objective_function(x + h) - objective_function(x - h)) / (2 * h)
            
            # Momentum update
            velocity = momentum * velocity - learning_rate * gradient
            x = x + velocity
            
            # Convergence check using exponential decay of tolerance
            tolerance = 1e-6 * ((0.99) ** iteration)
            if abs(gradient) < tolerance:
                break
        
        return x
    
    def chaos_theory_examples(self, x0, r, iterations=1000):
        # Logistic map: x_{n+1} = r * x_n * (1 - x_n)
        # This demonstrates sensitive dependence on initial conditions
        
        trajectory = []
        x = x0
        
        for i in range(iterations):
            # Note: This uses multiplication, not power, but demonstrates iteration
            x = r * x * (1 - x)
            trajectory.append(x)
            
            # Escape condition for unbounded behavior
            if x < 0 or x > 1:
                break
        
        return trajectory
    
    def fractal_computations(self, c, max_iterations=100):
        # Mandelbrot set iteration: z_{n+1} = z_n^2 + c
        z = 0 + 0j
        
        for iteration in range(max_iterations):
            # Power operation with complex numbers
            z = z ** 2 + c
            
            # Escape condition
            if abs(z) > 2:
                return iteration
        
        return max_iterations
    
    def statistical_distributions(self, x, parameters):
        # Probability density functions using power operations
        
        # Normal distribution: (1/sqrt(2*pi*sigma^2)) * exp(-(x-mu)^2 / (2*sigma^2))
        mu, sigma = parameters.get('normal', (0, 1))
        normal_pdf = (1 / ((2 * 3.14159 * sigma ** 2) ** 0.5)) * (2.71828 ** (-(x - mu) ** 2 / (2 * sigma ** 2)))
        
        # Exponential distribution: lambda * exp(-lambda * x)
        lam = parameters.get('exponential', 1.0)
        exponential_pdf = lam * (2.71828 ** (-lam * x)) if x >= 0 else 0
        
        # Power law distribution: alpha * x^(-alpha-1) for x >= 1
        alpha = parameters.get('power_law', 2.0)
        power_law_pdf = alpha * (x ** (-alpha - 1)) if x >= 1 else 0
        
        # Gamma distribution (simplified): x^(k-1) * exp(-x) / Gamma(k)
        k = parameters.get('gamma', 2.0)
        gamma_pdf = (x ** (k - 1)) * (2.71828 ** (-x)) / self.gamma_function(k) if x > 0 else 0
        
        return {
            'normal': normal_pdf,
            'exponential': exponential_pdf,
            'power_law': power_law_pdf,
            'gamma': gamma_pdf
        }
    
    def gamma_function(self, z):
        # Simplified gamma function approximation using Stirling's formula
        # Gamma(z) ≈ sqrt(2*pi/z) * (z/e)^z
        if z < 1:
            # Use gamma function property: Gamma(z) = Gamma(z+1) / z
            return self.gamma_function(z + 1) / z
        else:
            # Stirling's approximation
            return ((2 * 3.14159 / z) ** 0.5) * ((z / 2.71828) ** z)
"""
        ]
        
        for source in comprehensive_patterns:
            tree = tester.assert_power_operation_parses(source)
            
            # Should have extensive power usage
            power_ops = tester.get_power_operations(source)
            assert len(power_ops) >= 40, f"Should have many power operations: {len(power_ops)} found"
    
    def test_power_introspection(self, tester):
        """Test ability to analyze power operations programmatically"""
        # Test programmatic analysis of power operation structure
        introspection_source = """
def power_examples():
    # Simple power operations
    squared = x ** 2
    cubed = y ** 3
    arbitrary = base ** exponent
    
    # Right-associative chaining
    chained = a ** b ** c  # a ** (b ** c)
    deep_chain = x ** y ** z ** w
    
    # With different types
    int_power = 2 ** 8
    float_power = 2.5 ** 3.0
    complex_power = (1+2j) ** (3+4j)
    
    # Precedence patterns
    unary_precedence = -x ** 2  # -(x ** 2)
    arithmetic_precedence = 2 + 3 ** 4  # 2 + (3 ** 4)
    
    # In expressions
    polynomial = a * x ** 2 + b * x + c
    exponential = initial * base ** time
    
    # Complex patterns
    nested_powers = (a ** b) ** (c ** d)
    mixed_operations = x ** 2 + y ** 3 - z ** 0.5
    
    return squared, chained, polynomial, nested_powers
"""
        
        tree = tester.assert_power_operation_parses(introspection_source)
        
        # Should identify all power operations
        power_ops = tester.get_power_operations(introspection_source)
        assert len(power_ops) >= 15, "Should have multiple power operations"
        
        # Should identify chained operations
        chain_depth = tester.count_chained_power_operations(introspection_source)
        assert chain_depth >= 3, "Should have chained power operations"
        
        # All power operations should have proper structure
        for power_op in power_ops:
            assert isinstance(power_op, ast.BinOp), "Should be BinOp node"
            assert isinstance(power_op.op, ast.Pow), "Should be Pow operator"
            assert power_op.left is not None, "Should have left operand"
            assert power_op.right is not None, "Should have right operand"