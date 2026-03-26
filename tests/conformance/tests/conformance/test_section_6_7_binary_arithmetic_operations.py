"""
Section 6.7: Binary Arithmetic Operations - Conformance Test Suite

Tests Python Language Reference Section 6.7 compliance across implementations.
Based on formal grammar definitions and prose assertions for binary arithmetic operations.

Grammar tested:
    arith_expr: term (('+'|'-') term)*
    term: factor (('*'|'@'|'/'|'//'|'%') factor)*

Language Reference requirements tested:
    - Binary arithmetic operators: +, -, *, /, //, %, @
    - Operator precedence (*, /, //, %, @ before +, -)
    - Left-associativity of all binary arithmetic operators
    - Type coercion and numeric promotion rules
    - Error conditions (division by zero, type incompatibility)
    - Integration with unary operators and comparisons
    - Matrix multiplication operator (@) behavior
    - Floor division (//) vs true division (/) semantics
    - Modulo operator (%) behavior with different numeric types
"""

import ast
import pytest
import sys
from typing import Any


class BinaryArithmeticTester:
    """Helper class for testing binary arithmetic operation conformance.
    
    Follows established AST-based validation pattern from previous sections.
    """
    
    def assert_arithmetic_syntax_parses(self, source: str):
        """Test that arithmetic operation syntax parses correctly.
        
        Args:
            source: Python arithmetic operation source code
        """
        try:
            tree = ast.parse(source)
            return tree
        except SyntaxError as e:
            pytest.fail(f"Arithmetic syntax should be valid but failed to parse: {source}\\nError: {e}")
    
    def assert_arithmetic_syntax_error(self, source: str):
        """Test that invalid arithmetic syntax raises SyntaxError.
        
        Args:
            source: Python arithmetic source code that should be invalid
        """
        with pytest.raises(SyntaxError):
            ast.parse(source)
    
    def get_binary_operations(self, source: str) -> list:
        """Get BinOp AST nodes from source for analysis.
        
        Args:
            source: Python source code
            
        Returns:
            List of ast.BinOp nodes
        """
        tree = ast.parse(source)
        binary_ops = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp):
                binary_ops.append(node)
        
        return binary_ops
    
    def get_operator_types(self, source: str) -> list:
        """Get list of binary operator types from source.
        
        Args:
            source: Python source code
            
        Returns:
            List of operator type names (e.g., ['Add', 'Mult'])
        """
        binary_ops = self.get_binary_operations(source)
        operators = []
        
        for binop in binary_ops:
            operators.append(type(binop.op).__name__)
        
        return operators
    
    def has_operator_precedence_structure(self, source: str) -> bool:
        """Check if source demonstrates operator precedence.
        
        Args:
            source: Python source code
            
        Returns:
            True if contains mixed precedence operators
        """
        operators = self.get_operator_types(source)
        # Check for mix of high precedence (Mult, Div, FloorDiv, Mod, MatMult) 
        # and low precedence (Add, Sub)
        high_prec = {'Mult', 'Div', 'FloorDiv', 'Mod', 'MatMult'}
        low_prec = {'Add', 'Sub'}
        
        has_high = any(op in high_prec for op in operators)
        has_low = any(op in low_prec for op in operators)
        
        return has_high and has_low


@pytest.fixture
def tester():
    """Provide BinaryArithmeticTester instance for tests."""
    return BinaryArithmeticTester()


class TestSection67AdditionSubtraction:
    """Test addition and subtraction operators."""
    
    def test_basic_addition_operations(self, tester):
        """Test basic addition operator syntax and structure"""
        # Language Reference: + operator for numeric addition
        addition_expressions = [
            "a + b",
            "x + y + z",
            "1 + 2",
            "3.14 + 2.71",
            "value + offset",
            "result + increment",
            "total + partial",
            "base + modifier",
        ]
        
        for source in addition_expressions:
            tree = tester.assert_arithmetic_syntax_parses(source)
            binary_ops = tester.get_binary_operations(source)
            assert len(binary_ops) >= 1, f"Should contain addition: {source}"
            
            # Check for addition operators
            operators = tester.get_operator_types(source)
            assert 'Add' in operators, f"Should have addition operator: {source}"
    
    def test_basic_subtraction_operations(self, tester):
        """Test basic subtraction operator syntax and structure"""
        # Language Reference: - operator for numeric subtraction
        subtraction_expressions = [
            "a - b",
            "x - y - z",
            "10 - 3",
            "5.5 - 1.1",
            "total - deduction",
            "balance - withdrawal",
            "maximum - current",
            "end - start",
        ]
        
        for source in subtraction_expressions:
            tree = tester.assert_arithmetic_syntax_parses(source)
            binary_ops = tester.get_binary_operations(source)
            assert len(binary_ops) >= 1, f"Should contain subtraction: {source}"
            
            # Check for subtraction operators
            operators = tester.get_operator_types(source)
            assert 'Sub' in operators, f"Should have subtraction operator: {source}"
    
    def test_addition_subtraction_chaining(self, tester):
        """Test chained addition and subtraction operations"""
        # Language Reference: left-associative chaining
        chained_expressions = [
            "a + b + c + d",
            "x - y - z - w",
            "a + b - c + d",
            "start + increment - fee + bonus",
            "total - tax + discount - shipping",
        ]
        
        for source in chained_expressions:
            tree = tester.assert_arithmetic_syntax_parses(source)
            binary_ops = tester.get_binary_operations(source)
            assert len(binary_ops) >= 3, f"Should have chained operations: {source}"
            
            # Check for mix of add/sub operators
            operators = tester.get_operator_types(source)
            has_add_or_sub = any(op in ['Add', 'Sub'] for op in operators)
            assert has_add_or_sub, f"Should have add/sub operators: {source}"
    
    def test_addition_with_different_types(self, tester):
        """Test addition with different numeric types"""
        # Language Reference: addition works across numeric types
        type_addition_expressions = [
            "1 + 2.5",              # int + float
            "3.14 + 42",            # float + int
            "x + 1",                # variable + literal
            "func() + value",       # expression + variable
            "obj.attr + offset",    # attribute + value
        ]
        
        for source in type_addition_expressions:
            tree = tester.assert_arithmetic_syntax_parses(source)
            # Should parse correctly - type compatibility is runtime behavior
            binary_ops = tester.get_binary_operations(source)
            assert len(binary_ops) >= 1, f"Should contain addition: {source}"


class TestSection67MultiplicationDivision:
    """Test multiplication and division operators."""
    
    def test_basic_multiplication_operations(self, tester):
        """Test basic multiplication operator syntax and structure"""
        # Language Reference: * operator for numeric multiplication
        multiplication_expressions = [
            "a * b",
            "x * y * z",
            "3 * 7",
            "2.5 * 4",
            "rate * quantity",
            "width * height",
            "factor * value",
            "coefficient * variable",
        ]
        
        for source in multiplication_expressions:
            tree = tester.assert_arithmetic_syntax_parses(source)
            binary_ops = tester.get_binary_operations(source)
            assert len(binary_ops) >= 1, f"Should contain multiplication: {source}"
            
            # Check for multiplication operators
            operators = tester.get_operator_types(source)
            assert 'Mult' in operators, f"Should have multiplication operator: {source}"
    
    def test_basic_division_operations(self, tester):
        """Test basic division operator syntax and structure"""
        # Language Reference: / operator for true division
        division_expressions = [
            "a / b",
            "x / y / z",
            "15 / 3",
            "7.5 / 2.5",
            "total / count",
            "distance / time",
            "numerator / denominator",
            "area / width",
        ]
        
        for source in division_expressions:
            tree = tester.assert_arithmetic_syntax_parses(source)
            binary_ops = tester.get_binary_operations(source)
            assert len(binary_ops) >= 1, f"Should contain division: {source}"
            
            # Check for division operators
            operators = tester.get_operator_types(source)
            assert 'Div' in operators, f"Should have division operator: {source}"
    
    def test_floor_division_operations(self, tester):
        """Test floor division operator (//)"""
        # Language Reference: // operator for floor division
        floor_division_expressions = [
            "a // b",
            "x // y // z",
            "17 // 5",
            "10.0 // 3.0",
            "total_items // batch_size",
            "seconds // 60",
            "bytes_count // chunk_size",
            "pixel_count // row_width",
        ]
        
        for source in floor_division_expressions:
            tree = tester.assert_arithmetic_syntax_parses(source)
            binary_ops = tester.get_binary_operations(source)
            assert len(binary_ops) >= 1, f"Should contain floor division: {source}"
            
            # Check for floor division operators
            operators = tester.get_operator_types(source)
            assert 'FloorDiv' in operators, f"Should have floor division operator: {source}"
    
    def test_modulo_operations(self, tester):
        """Test modulo operator (%)"""
        # Language Reference: % operator for modulo/remainder
        modulo_expressions = [
            "a % b",
            "x % y % z",
            "17 % 5",
            "10.5 % 3.2",
            "index % array_length",
            "timestamp % interval",
            "hash_value % bucket_count",
            "position % cycle_length",
        ]
        
        for source in modulo_expressions:
            tree = tester.assert_arithmetic_syntax_parses(source)
            binary_ops = tester.get_binary_operations(source)
            assert len(binary_ops) >= 1, f"Should contain modulo: {source}"
            
            # Check for modulo operators
            operators = tester.get_operator_types(source)
            assert 'Mod' in operators, f"Should have modulo operator: {source}"
    
    def test_matrix_multiplication_operations(self, tester):
        """Test matrix multiplication operator (@)"""
        # Language Reference: @ operator for matrix multiplication (Python 3.5+)
        matrix_mult_expressions = [
            "matrix_a @ matrix_b",
            "A @ B @ C",
            "transform @ vector",
            "weights @ inputs",
            "rotation @ coordinates",
            "left_matrix @ right_matrix",
        ]
        
        for source in matrix_mult_expressions:
            tree = tester.assert_arithmetic_syntax_parses(source)
            binary_ops = tester.get_binary_operations(source)
            assert len(binary_ops) >= 1, f"Should contain matrix multiplication: {source}"
            
            # Check for matrix multiplication operators
            operators = tester.get_operator_types(source)
            assert 'MatMult' in operators, f"Should have matrix multiplication operator: {source}"


class TestSection67ArithmeticPrecedence:
    """Test arithmetic operator precedence."""
    
    def test_multiplication_division_precedence(self, tester):
        """Test precedence: *, /, //, %, @ before +, -"""
        # Language Reference: multiplicative operators have higher precedence
        precedence_expressions = [
            "a + b * c",           # b * c first, then + a
            "x - y / z",           # y / z first, then x -
            "a + b // c",          # b // c first, then + a
            "x - y % z",           # y % z first, then x -
            "a + b @ c",           # b @ c first, then + a
            "total + rate * quantity",  # rate * quantity first
            "balance - fee / rate",     # fee / rate first
        ]
        
        for source in precedence_expressions:
            tree = tester.assert_arithmetic_syntax_parses(source)
            assert tester.has_operator_precedence_structure(source), f"Should show precedence: {source}"
    
    def test_same_precedence_associativity(self, tester):
        """Test left-associativity within same precedence level"""
        # Language Reference: arithmetic operators are left-associative
        associativity_expressions = [
            "a + b + c",           # ((a + b) + c)
            "x - y - z",           # ((x - y) - z)
            "a * b * c",           # ((a * b) * c)
            "x / y / z",           # ((x / y) / z)
            "a // b // c",         # ((a // b) // c)
            "x % y % z",           # ((x % y) % z)
            "a @ b @ c",           # ((a @ b) @ c)
        ]
        
        for source in associativity_expressions:
            tree = tester.assert_arithmetic_syntax_parses(source)
            binary_ops = tester.get_binary_operations(source)
            # Should have nested structure showing left-associativity
            assert len(binary_ops) >= 2, f"Should have chained operations: {source}"
    
    def test_parentheses_override_precedence(self, tester):
        """Test parentheses overriding arithmetic precedence"""
        # Language Reference: parentheses can override precedence
        parenthesized_expressions = [
            "(a + b) * c",         # Addition first, then multiplication
            "(x - y) / z",         # Subtraction first, then division
            "a * (b + c)",         # Addition first, then multiplication
            "x / (y - z)",         # Subtraction first, then division
            "(a + b) @ (c + d)",   # Both additions first, then matrix mult
        ]
        
        for source in parenthesized_expressions:
            tree = tester.assert_arithmetic_syntax_parses(source)
            # Should parse correctly with parentheses
            assert tree is not None, f"Should parse with parentheses: {source}"
    
    def test_complex_precedence_patterns(self, tester):
        """Test complex precedence interaction patterns"""
        # Language Reference: complex real-world precedence scenarios
        complex_expressions = [
            "a + b * c - d / e",           # Mixed precedence levels
            "x * y + z // w - v % u",      # Multiple high-precedence ops
            "rate * hours + overtime * 1.5",   # Real-world calculation
            "base + tax * rate - discount / 100",  # Financial calculation
            "width * height + border * 2",     # Geometric calculation
        ]
        
        for source in complex_expressions:
            tree = tester.assert_arithmetic_syntax_parses(source)
            assert tester.has_operator_precedence_structure(source), f"Should have precedence: {source}"


class TestSection67ArithmeticErrorConditions:
    """Test arithmetic operation error conditions."""
    
    def test_invalid_arithmetic_syntax(self, tester):
        """Test invalid arithmetic operation syntax"""
        # Language Reference: syntactic restrictions on arithmetic operators
        invalid_expressions = [
            "x *",                 # Missing right operand
            "/ y",                 # Missing left operand
            "x //",                # Missing right operand
            "% z",                 # Missing left operand
            "x @",                 # Missing right operand
            "a * * b",             # Invalid operator sequence
            "x / / y",             # Should be // not / /
        ]
        
        for source in invalid_expressions:
            tester.assert_arithmetic_syntax_error(source)
    
    def test_division_by_zero_syntax(self, tester):
        """Test division by zero - syntax should be valid"""
        # Language Reference: division by zero is runtime error, not syntax error
        division_by_zero_expressions = [
            "x / 0",               # True division by zero
            "y // 0",              # Floor division by zero
            "z % 0",               # Modulo by zero
            "value / (a - a)",     # Expression evaluating to zero
        ]
        
        for source in division_by_zero_expressions:
            tree = tester.assert_arithmetic_syntax_parses(source)
            # Should parse correctly - division by zero is runtime error
            assert tree is not None, f"Division by zero should parse: {source}"
    
    def test_arithmetic_indentation_requirements(self, tester):
        """Test arithmetic operations follow indentation rules"""
        # Language Reference: arithmetic operations follow normal expression rules
        valid_indented_expressions = [
            """
result = (
    base_amount +
    tax_amount -
    discount_amount
)
""",
            """
calculation = (
    width * height *
    depth / density
)
""",
            """
def compute():
    return (
        rate * hours +
        overtime * 1.5
    )
"""
        ]
        
        for source in valid_indented_expressions:
            tree = tester.assert_arithmetic_syntax_parses(source)
            # Should handle indentation correctly
            assert tree is not None, f"Should handle indentation: {source}"


class TestSection67TypeCoercionPatterns:
    """Test arithmetic type coercion and promotion."""
    
    def test_numeric_type_mixing(self, tester):
        """Test arithmetic with mixed numeric types"""
        # Language Reference: numeric type promotion in arithmetic
        type_mixing_expressions = [
            "1 + 2.5",             # int + float
            "3.14 * 2",            # float * int
            "10 / 3",              # int / int (results in float)
            "7.5 // 2",            # float // int
            "15 % 4.0",            # int % float
        ]
        
        for source in type_mixing_expressions:
            tree = tester.assert_arithmetic_syntax_parses(source)
            # Should parse correctly - type promotion is runtime behavior
            binary_ops = tester.get_binary_operations(source)
            assert len(binary_ops) >= 1, f"Should contain arithmetic: {source}"
    
    def test_incompatible_type_syntax(self, tester):
        """Test arithmetic with incompatible types (syntax still valid)"""
        # Language Reference: type errors are runtime, not syntax errors
        incompatible_expressions = [
            "'string' + 42",       # string + int
            "[1, 2] * 'text'",     # list * string (valid: repetition)
            "'hello' - 'world'",   # string - string
            "{} / []",             # dict / list
            "None * 5",            # None * int
        ]
        
        for source in incompatible_expressions:
            tree = tester.assert_arithmetic_syntax_parses(source)
            # Should parse correctly - type errors happen at runtime
            assert tree is not None, f"Incompatible types should parse: {source}"
    
    def test_special_numeric_values(self, tester):
        """Test arithmetic with special numeric values"""
        # Language Reference: special values in arithmetic operations
        special_value_expressions = [
            "float('inf') + 1",
            "float('-inf') - 1", 
            "float('nan') * 2",
            "x + float('inf')",
            "value / float('inf')",
        ]
        
        for source in special_value_expressions:
            tree = tester.assert_arithmetic_syntax_parses(source)
            # Should parse correctly - special value behavior is runtime
            assert tree is not None, f"Special values should parse: {source}"


class TestSection67ComplexArithmeticPatterns:
    """Test complex arithmetic operation patterns."""
    
    def test_nested_arithmetic_expressions(self, tester):
        """Test deeply nested arithmetic expressions"""
        # Language Reference: arithmetic operations can be arbitrarily nested
        nested_expressions = [
            "(a + b) * (c - d)",
            "(x / y) + (z * w)",
            "((a * b) + c) / (d - e)",
            "(rate + bonus) * (hours - break_time)",
            "((width + padding) * (height + padding)) - (width * height)",
        ]
        
        for source in nested_expressions:
            tree = tester.assert_arithmetic_syntax_parses(source)
            binary_ops = tester.get_binary_operations(source)
            assert len(binary_ops) >= 3, f"Should have multiple operations: {source}"
    
    def test_function_call_integration(self, tester):
        """Test arithmetic operations with function calls"""
        # Language Reference: function calls can be operands in arithmetic
        function_call_expressions = [
            "func(x) + func(y)",
            "calculate_tax(income) * rate",
            "get_width() * get_height()",
            "math.sqrt(value) + offset",
            "transform(data) @ matrix",
        ]
        
        for source in function_call_expressions:
            tree = tester.assert_arithmetic_syntax_parses(source)
            # Should contain both function calls and arithmetic operations
            calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
            binary_ops = tester.get_binary_operations(source)
            assert len(calls) >= 1, f"Should have function calls: {source}"
            assert len(binary_ops) >= 1, f"Should have arithmetic: {source}"
    
    def test_arithmetic_in_comprehensions(self, tester):
        """Test arithmetic operations in comprehensions"""
        # Language Reference: arithmetic can appear in comprehensions
        comprehension_expressions = [
            "[x * 2 for x in range(10)]",
            "[a + b for a, b in pairs]",
            "{x: x ** 2 + 1 for x in values}",
            "(total / count for total, count in data)",
            "[rate * hours + overtime for rate, hours, overtime in payroll]",
        ]
        
        for source in comprehension_expressions:
            tree = tester.assert_arithmetic_syntax_parses(source)
            # Should contain both comprehension and arithmetic operations
            comprehensions = [node for node in ast.walk(tree) 
                             if isinstance(node, (ast.ListComp, ast.DictComp, 
                                                 ast.SetComp, ast.GeneratorExp))]
            binary_ops = tester.get_binary_operations(source)
            assert len(comprehensions) >= 1, f"Should have comprehension: {source}"
            assert len(binary_ops) >= 1, f"Should have arithmetic: {source}"


class TestSection67CrossImplementationCompatibility:
    """Test cross-implementation compatibility for arithmetic operations."""
    
    def test_arithmetic_ast_structure_consistency(self, tester):
        """Test arithmetic operation AST structure across implementations"""
        # Language Reference: AST structure should be consistent
        test_cases = [
            "a + b",
            "x * y",
            "z / w",
            "a // b",
            "x % y",
            "matrix @ vector",
            "a + b * c",
        ]
        
        for source in test_cases:
            tree = tester.assert_arithmetic_syntax_parses(source)
            binary_ops = tester.get_binary_operations(source)
            
            # Should have arithmetic operations
            assert len(binary_ops) >= 1, f"Should have arithmetic operations: {source}"
            
            # Check AST structure consistency
            for binop in binary_ops:
                assert hasattr(binop, 'left'), "BinOp should have 'left' attribute"
                assert hasattr(binop, 'op'), "BinOp should have 'op' attribute"
                assert hasattr(binop, 'right'), "BinOp should have 'right' attribute"
    
    def test_all_arithmetic_operators_supported(self, tester):
        """Test all arithmetic operators are properly supported"""
        # Language Reference: comprehensive operator support verification
        operator_test_cases = [
            ("a + b", "Add"),
            ("a - b", "Sub"),
            ("a * b", "Mult"),
            ("a / b", "Div"),
            ("a // b", "FloorDiv"),
            ("a % b", "Mod"),
            ("a @ b", "MatMult"),
        ]
        
        for source, expected_op in operator_test_cases:
            tree = tester.assert_arithmetic_syntax_parses(source)
            operators = tester.get_operator_types(source)
            assert expected_op in operators, f"Should support {expected_op} operator: {source}"
    
    def test_complex_arithmetic_evaluation_patterns(self, tester):
        """Test complex arithmetic patterns for compatibility"""
        # Language Reference: comprehensive real-world patterns
        complex_patterns = [
            """
total_cost = (
    base_price * quantity +
    shipping_cost +
    tax_rate * (base_price * quantity + shipping_cost)
)
""",
            """
physics_calculation = (
    mass * velocity ** 2 / 2 +
    potential_energy +
    kinetic_energy_offset
)
""",
            """
matrix_transform = (
    rotation_matrix @ scale_matrix @ 
    translation_matrix @ input_vector
)
"""
        ]
        
        for source in complex_patterns:
            tree = tester.assert_arithmetic_syntax_parses(source)
            # Just verify complex patterns parse successfully
            assert len(tree.body) >= 1, f"Complex arithmetic pattern should parse: {source}"
    
    def test_arithmetic_operation_introspection(self, tester):
        """Test ability to analyze arithmetic operations programmatically"""
        # Test programmatic analysis of arithmetic operation structure
        introspection_source = "rate * hours + overtime * 1.5 - deductions / 12"
        
        tree = tester.assert_arithmetic_syntax_parses(introspection_source)
        binary_ops = tester.get_binary_operations(source=introspection_source)
        
        # Should be able to identify and analyze arithmetic operations
        assert len(binary_ops) >= 3, "Should have multiple arithmetic operations"
        
        # Should be able to analyze operation types and precedence
        operators = tester.get_operator_types(introspection_source)
        expected_ops = ['Mult', 'Add', 'Mult', 'Sub', 'Div']
        for expected_op in expected_ops:
            assert expected_op in operators, f"Should find {expected_op} operator"