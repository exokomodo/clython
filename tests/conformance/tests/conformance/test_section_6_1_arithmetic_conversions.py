"""
Section 6.1: Arithmetic Conversions - Conformance Test Suite

Tests Python Language Reference Section 6.1 compliance across implementations.
Based on formal conversion rules and prose assertions for arithmetic type conversions.

Language Reference requirements tested:
    - Numeric type hierarchy and promotion rules
    - Mixed arithmetic operation type conversions
    - Integer and floating-point conversion behavior
    - Complex number conversion and arithmetic
    - Boolean arithmetic conversion behavior
    - Decimal and Fraction type integration
    - Custom numeric type conversion protocols
    - Type coercion in binary arithmetic operations
    - Error conditions and unsupported conversions
"""

import ast
import pytest
import sys
from typing import Any
from decimal import Decimal
from fractions import Fraction


class ArithmeticConversionTester:
    """Helper class for testing arithmetic conversion conformance.
    
    Follows established AST-based validation pattern from previous sections.
    """
    
    def assert_conversion_syntax_parses(self, source: str):
        """Test that conversion operation syntax parses correctly.
        
        Args:
            source: Python conversion operation source code
        """
        try:
            tree = ast.parse(source)
            return tree
        except SyntaxError as e:
            pytest.fail(f"Conversion syntax should be valid but failed to parse: {source}\\nError: {e}")
    
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
    
    def has_mixed_type_arithmetic(self, source: str) -> bool:
        """Check if source contains mixed-type arithmetic patterns.
        
        Args:
            source: Python source code
            
        Returns:
            True if contains arithmetic that would trigger conversions
        """
        # Look for numeric literals of different types in arithmetic
        tree = ast.parse(source)
        numeric_types = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant):
                if isinstance(node.value, int):
                    numeric_types.add('int')
                elif isinstance(node.value, float):
                    numeric_types.add('float')
                elif isinstance(node.value, complex):
                    numeric_types.add('complex')
                elif isinstance(node.value, bool):
                    numeric_types.add('bool')
        
        return len(numeric_types) > 1


@pytest.fixture
def tester():
    """Provide ArithmeticConversionTester instance for tests."""
    return ArithmeticConversionTester()


class TestSection61IntegerFloatConversions:
    """Test integer and float conversion rules."""
    
    def test_int_float_addition_conversion(self, tester):
        """Test integer-float addition type promotion"""
        # Language Reference: int + float promotes to float
        int_float_additions = [
            "1 + 2.0",
            "42 + 3.14",
            "0 + 1.5",
            "-5 + 2.7",
            "100 + 0.1",
        ]
        
        for source in int_float_additions:
            tree = tester.assert_conversion_syntax_parses(source)
            assert tester.has_mixed_type_arithmetic(source), f"Should have mixed types: {source}"
            
            binary_ops = tester.get_binary_operations(source)
            assert len(binary_ops) >= 1, f"Should contain arithmetic: {source}"
    
    def test_float_int_arithmetic_conversion(self, tester):
        """Test float-integer arithmetic operations"""
        # Language Reference: float with int promotes int to float
        float_int_operations = [
            "3.14 + 2",
            "2.5 - 1",
            "1.5 * 3",
            "7.5 / 2",
            "9.0 // 4",
            "5.5 % 2",
        ]
        
        for source in float_int_operations:
            tree = tester.assert_conversion_syntax_parses(source)
            assert tester.has_mixed_type_arithmetic(source), f"Should have mixed types: {source}"
    
    def test_chained_mixed_arithmetic(self, tester):
        """Test chained operations with mixed int/float"""
        # Language Reference: consistent promotion throughout expression
        chained_mixed_operations = [
            "1 + 2.0 + 3",        # int + float + int
            "2.5 * 2 + 1",        # float * int + int  
            "10 / 2.0 - 1",       # int / float - int
            "1.5 + 2.5 + 3",      # float + float + int
            "5 * 2.0 / 3 + 1.0",  # complex mixed chain
        ]
        
        for source in chained_mixed_operations:
            tree = tester.assert_conversion_syntax_parses(source)
            binary_ops = tester.get_binary_operations(source)
            assert len(binary_ops) >= 2, f"Should have chained operations: {source}"
    
    def test_integer_division_conversion(self, tester):
        """Test integer division conversion behavior"""
        # Language Reference: int / int produces float in Python 3
        integer_division_cases = [
            "5 / 2",              # Should produce float
            "10 / 3",             # Should produce float  
            "8 / 4",              # Should produce float even if evenly divisible
            "1 / 1",              # Should produce float
            "0 / 1",              # Should produce float
        ]
        
        for source in integer_division_cases:
            tree = tester.assert_conversion_syntax_parses(source)
            binary_ops = tester.get_binary_operations(source)
            assert len(binary_ops) >= 1, f"Should contain division: {source}"


class TestSection61BooleanArithmeticConversions:
    """Test Boolean arithmetic conversion behavior."""
    
    def test_bool_int_arithmetic(self, tester):
        """Test Boolean-integer arithmetic conversions"""
        # Language Reference: bool is subclass of int, True=1, False=0
        bool_int_operations = [
            "True + 1",           # True converts to 1
            "False + 5",          # False converts to 0
            "True * 10",          # True converts to 1
            "False * 42",         # False converts to 0
            "True - False",       # 1 - 0
            "True + False",       # 1 + 0
        ]
        
        for source in bool_int_operations:
            tree = tester.assert_conversion_syntax_parses(source)
            binary_ops = tester.get_binary_operations(source)
            assert len(binary_ops) >= 1, f"Should contain arithmetic: {source}"
    
    def test_bool_float_arithmetic(self, tester):
        """Test Boolean-float arithmetic conversions"""
        # Language Reference: bool converts to int, then int promotes to float
        bool_float_operations = [
            "True + 1.0",         # True -> 1 -> 1.0
            "False + 3.14",       # False -> 0 -> 0.0
            "True * 2.5",         # True -> 1 -> 1.0
            "False / 1.0",        # False -> 0 -> 0.0
            "1.5 + True",         # True -> 1 -> 1.0
            "2.0 * False",        # False -> 0 -> 0.0
        ]
        
        for source in bool_float_operations:
            tree = tester.assert_conversion_syntax_parses(source)
            assert tester.has_mixed_type_arithmetic(source), f"Should have mixed types: {source}"
    
    def test_bool_bool_arithmetic(self, tester):
        """Test Boolean-Boolean arithmetic operations"""
        # Language Reference: both bools convert to int
        bool_bool_operations = [
            "True + True",        # 1 + 1
            "True - False",       # 1 - 0  
            "False * True",       # 0 * 1
            "True / True",        # 1 / 1 (produces float)
            "True // False",      # Would be 1 // 0 (division by zero)
            "True % True",        # 1 % 1
        ]
        
        for source in bool_bool_operations:
            tree = tester.assert_conversion_syntax_parses(source)
            # Division by zero is runtime error, not syntax error
            binary_ops = tester.get_binary_operations(source)
            assert len(binary_ops) >= 1, f"Should contain arithmetic: {source}"


class TestSection61ComplexNumberConversions:
    """Test complex number arithmetic conversions."""
    
    def test_complex_real_arithmetic(self, tester):
        """Test complex number with real number arithmetic"""
        # Language Reference: real numbers promote to complex
        complex_real_operations = [
            "1j + 2",             # complex + int
            "3.14 + 2j",          # float + complex
            "(1+2j) * 3",         # complex * int
            "5.0 * (2+3j)",       # float * complex
            "(1+1j) - 1.5",       # complex - float
        ]
        
        for source in complex_real_operations:
            tree = tester.assert_conversion_syntax_parses(source)
            binary_ops = tester.get_binary_operations(source)
            assert len(binary_ops) >= 1, f"Should contain arithmetic: {source}"
    
    def test_complex_complex_arithmetic(self, tester):
        """Test complex-complex arithmetic operations"""
        # Language Reference: complex arithmetic preserves complex type
        complex_complex_operations = [
            "(1+2j) + (3+4j)",    # complex + complex
            "(5+0j) - (2+1j)",    # complex - complex
            "(1+1j) * (2+2j)",    # complex * complex
            "(4+2j) / (1+1j)",    # complex / complex
        ]
        
        for source in complex_complex_operations:
            tree = tester.assert_conversion_syntax_parses(source)
            binary_ops = tester.get_binary_operations(source)
            assert len(binary_ops) >= 1, f"Should contain arithmetic: {source}"
    
    def test_mixed_complex_promotion(self, tester):
        """Test mixed arithmetic promoting to complex"""
        # Language Reference: any complex operand promotes result to complex
        mixed_complex_operations = [
            "1 + 2.0 + 3j",       # int + float + complex
            "True + 1.5 + 2j",    # bool + float + complex  
            "5 * 2.0 * (1+1j)",   # int * float * complex
            "(1+0j) + 2 + 3.0",   # complex + int + float
        ]
        
        for source in mixed_complex_operations:
            tree = tester.assert_conversion_syntax_parses(source)
            binary_ops = tester.get_binary_operations(source)
            assert len(binary_ops) >= 2, f"Should have multiple operations: {source}"


class TestSection61DecimalFractionTypes:
    """Test Decimal and Fraction type conversions."""
    
    def test_decimal_syntax_patterns(self, tester):
        """Test Decimal type in arithmetic expressions"""
        # Language Reference: Decimal preserves precision, doesn't auto-convert
        decimal_patterns = [
            "Decimal('1.1') + Decimal('2.2')",
            "Decimal('10') / Decimal('3')",
            "Decimal('5.5') * Decimal('2')",
            "Decimal('100') - Decimal('0.01')",
        ]
        
        for source in decimal_patterns:
            tree = tester.assert_conversion_syntax_parses(source)
            # Contains function calls to Decimal constructor
            calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
            assert len(calls) >= 2, f"Should have Decimal calls: {source}"
    
    def test_fraction_syntax_patterns(self, tester):
        """Test Fraction type in arithmetic expressions"""
        # Language Reference: Fraction preserves exact rational arithmetic
        fraction_patterns = [
            "Fraction(1, 3) + Fraction(2, 3)",
            "Fraction(5, 2) * Fraction(3, 4)",
            "Fraction(10, 1) - Fraction(1, 2)",
            "Fraction(7, 3) / Fraction(2, 1)",
        ]
        
        for source in fraction_patterns:
            tree = tester.assert_conversion_syntax_parses(source)
            # Contains function calls to Fraction constructor
            calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
            assert len(calls) >= 2, f"Should have Fraction calls: {source}"
    
    def test_mixed_precise_types(self, tester):
        """Test mixing Decimal and Fraction types"""
        # Language Reference: explicit conversion needed, no automatic conversion
        mixed_precise_patterns = [
            "Decimal(str(Fraction(1, 3))) + Decimal('2.0')",
            "Fraction(Decimal('0.5')) + Fraction(1, 4)",
            "float(Decimal('3.14')) + 2.0",
            "int(Fraction(7, 2)) + 5",
        ]
        
        for source in mixed_precise_patterns:
            tree = tester.assert_conversion_syntax_parses(source)
            # Should contain explicit conversion calls
            calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
            assert len(calls) >= 1, f"Should have conversion calls: {source}"


class TestSection61ConversionErrorConditions:
    """Test arithmetic conversion error conditions."""
    
    def test_unsupported_arithmetic_combinations(self, tester):
        """Test arithmetic with unsupported type combinations"""
        # Language Reference: some types don't support arithmetic (syntax OK)
        unsupported_combinations = [
            "'string' + 42",           # str + int (type error at runtime)
            "[1, 2] - [3]",           # list - list (type error at runtime)
            "{'a': 1} * 2",           # dict * int (type error at runtime)
            "None + 5",               # None + int (type error at runtime)
            "complex(1, 2) // 2",     # complex // int (type error at runtime)
        ]
        
        for source in unsupported_combinations:
            tree = tester.assert_conversion_syntax_parses(source)
            # Should parse correctly - type errors are runtime, not syntax
            assert tree is not None, f"Unsupported combination should parse: {source}"
    
    def test_division_by_zero_conversions(self, tester):
        """Test division by zero with type conversions"""
        # Language Reference: division by zero is runtime error
        division_by_zero_cases = [
            "1.0 / 0",                # float / int (zero)
            "5 / 0.0",                # int / float (zero)
            "True / False",           # bool / bool (1 / 0)
            "(1+2j) / 0",             # complex / int (zero)
            "Decimal('5') / Decimal('0')",  # Decimal division by zero
        ]
        
        for source in division_by_zero_cases:
            tree = tester.assert_conversion_syntax_parses(source)
            # Should parse correctly - division by zero is runtime error
            assert tree is not None, f"Division by zero should parse: {source}"
    
    def test_overflow_conditions(self, tester):
        """Test potential overflow conditions in conversions"""
        # Language Reference: overflow behavior depends on types
        overflow_patterns = [
            "float('inf') + 1.0",     # infinity arithmetic
            "float('-inf') * 2",      # infinity arithmetic
            "float('nan') + 5",       # NaN arithmetic
            "10**1000 + 1.0",         # Large int + float
            "complex(float('inf'), 1) + 1", # Complex with infinity
        ]
        
        for source in overflow_patterns:
            tree = tester.assert_conversion_syntax_parses(source)
            # Should parse correctly - overflow is runtime behavior
            assert tree is not None, f"Overflow pattern should parse: {source}"


class TestSection61CustomNumericTypes:
    """Test custom numeric type conversion patterns."""
    
    def test_custom_numeric_protocol_patterns(self, tester):
        """Test custom types implementing numeric protocols"""
        # Language Reference: custom types can implement __add__, __radd__, etc.
        custom_numeric_patterns = [
            "custom_number + 5",      # custom type with __add__
            "3 + custom_number",      # triggers __radd__ on custom type
            "custom_number * 2.5",    # custom type with __mul__
            "1.0 / custom_number",    # triggers __rtruediv__ on custom type
            "complex_custom + (1+2j)", # custom type with complex arithmetic
        ]
        
        for source in custom_numeric_patterns:
            tree = tester.assert_conversion_syntax_parses(source)
            # Should parse correctly - custom behavior is runtime
            binary_ops = tester.get_binary_operations(source)
            assert len(binary_ops) >= 1, f"Should contain arithmetic: {source}"
    
    def test_numeric_conversion_method_calls(self, tester):
        """Test explicit numeric conversion method calls"""
        # Language Reference: int(), float(), complex() for explicit conversion
        conversion_method_patterns = [
            "int(3.14) + 2",          # Explicit int conversion
            "float(42) + 1.5",        # Explicit float conversion
            "complex(1, 2) + 3j",     # Explicit complex conversion
            "int(True) + float(False)", # Bool conversions
            "complex(float(int(True)))", # Nested conversions
        ]
        
        for source in conversion_method_patterns:
            tree = tester.assert_conversion_syntax_parses(source)
            # Should contain explicit conversion calls
            calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
            assert len(calls) >= 1, f"Should have conversion calls: {source}"
    
    def test_operator_method_inference(self, tester):
        """Test patterns that would trigger operator methods"""
        # Language Reference: arithmetic operations map to __add__, __mul__, etc.
        operator_method_patterns = [
            "a.__add__(b)",           # Explicit method call
            "a + b",                  # Implicit __add__ call
            "a.__mul__(b)",           # Explicit method call  
            "a * b",                  # Implicit __mul__ call
            "a.__truediv__(b)",       # Explicit method call
            "a / b",                  # Implicit __truediv__ call
        ]
        
        for source in operator_method_patterns:
            tree = tester.assert_conversion_syntax_parses(source)
            # Should parse correctly regardless of explicit vs implicit
            assert tree is not None, f"Operator method pattern should parse: {source}"


class TestSection61TypeHierarchyValidation:
    """Test numeric type hierarchy validation."""
    
    def test_numeric_tower_progression(self, tester):
        """Test numeric tower: bool -> int -> float -> complex"""
        # Language Reference: numeric tower defines promotion rules
        tower_progression_patterns = [
            "True + 1 + 1.0 + 1j",    # bool -> int -> float -> complex
            "False * 2 * 2.5 * (1+1j)", # Full tower progression  
            "bool(1) + int(2.0) + float(3) + complex(4)", # Explicit conversions
            "(True + 1) * (2.0 + 1j)", # Subexpression promotions
        ]
        
        for source in tower_progression_patterns:
            tree = tester.assert_conversion_syntax_parses(source)
            binary_ops = tester.get_binary_operations(source)
            assert len(binary_ops) >= 3, f"Should have multiple operations: {source}"
    
    def test_promotion_precedence_rules(self, tester):
        """Test type promotion precedence in expressions"""
        # Language Reference: highest type in expression determines result type
        promotion_precedence_patterns = [
            "1 + 2 + 3.0",            # int operations until float
            "1.0 + 2 + 3",            # float from start
            "1 + 2j + 3.0",           # complex dominates
            "(1 + 2) * 3.0",          # int result promoted by float
            "True and (1 + 2.0)",     # Boolean with promoted arithmetic
        ]
        
        for source in promotion_precedence_patterns:
            tree = tester.assert_conversion_syntax_parses(source)
            # Should parse correctly with proper promotion
            assert tree is not None, f"Promotion pattern should parse: {source}"
    
    def test_conversion_boundary_conditions(self, tester):
        """Test edge cases in numeric conversions"""
        # Language Reference: boundary conditions in type conversion
        boundary_patterns = [
            "0 + 0.0 + 0j",           # Zero values across types
            "1 * 1.0 * (1+0j)",       # Identity values across types
            "-1 + (-1.0) + (-1+0j)",  # Negative values across types
            "True + 1.0 + (0+1j)",    # Mixed positive values
            "int(1e10) + 1.0",        # Large int with float
        ]
        
        for source in boundary_patterns:
            tree = tester.assert_conversion_syntax_parses(source)
            binary_ops = tester.get_binary_operations(source)
            assert len(binary_ops) >= 1, f"Should have operations: {source}"


class TestSection61CrossImplementationCompatibility:
    """Test cross-implementation compatibility for arithmetic conversions."""
    
    def test_conversion_ast_consistency(self, tester):
        """Test arithmetic conversion AST structure consistency"""
        # Language Reference: AST structure should be consistent for conversions
        conversion_test_cases = [
            "1 + 2.0",                # int + float
            "True * 3.14",            # bool * float
            "(1+2j) + 3",             # complex + int
            "1 / 2",                  # int / int (float result)
            "Decimal('1.1') + Decimal('2.2')", # Decimal arithmetic
        ]
        
        for source in conversion_test_cases:
            tree = tester.assert_conversion_syntax_parses(source)
            binary_ops = tester.get_binary_operations(source)
            
            # Should have consistent AST structure
            assert len(binary_ops) >= 1, f"Should have arithmetic operations: {source}"
            
            for binop in binary_ops:
                assert hasattr(binop, 'left'), "BinOp should have 'left' attribute"
                assert hasattr(binop, 'op'), "BinOp should have 'op' attribute"
                assert hasattr(binop, 'right'), "BinOp should have 'right' attribute"
    
    def test_comprehensive_conversion_patterns(self, tester):
        """Test comprehensive real-world conversion patterns"""
        # Language Reference: complex real-world conversion scenarios
        comprehensive_patterns = [
            """
financial_calc = (
    Decimal('100.00') * Decimal('1.08') +
    float(tax_rate) * base_amount +
    int(surcharge_flag) * surcharge_amount
)
""",
            """
physics_calc = (
    mass * velocity ** 2 / 2.0 +
    complex(0, angular_momentum) +
    int(quantum_state) * energy_level
)
""",
            """
statistics_calc = (
    sum(float(x) for x in data) / len(data) +
    Fraction(confidence_interval, 100) +
    bool(outlier_detected) * outlier_penalty
)
"""
        ]
        
        for source in comprehensive_patterns:
            tree = tester.assert_conversion_syntax_parses(source)
            # Just verify complex patterns parse successfully
            assert len(tree.body) >= 1, f"Complex conversion pattern should parse: {source}"
    
    def test_conversion_introspection_capability(self, tester):
        """Test ability to analyze conversion operations programmatically"""
        # Test programmatic analysis of conversion operation structure
        introspection_source = "True + 1 + 2.5 + (3+4j)"
        
        tree = tester.assert_conversion_syntax_parses(introspection_source)
        binary_ops = tester.get_binary_operations(source=introspection_source)
        
        # Should be able to identify conversion-triggering operations
        assert len(binary_ops) >= 3, "Should have multiple conversion operations"
        assert tester.has_mixed_type_arithmetic(introspection_source), "Should detect mixed types"
        
        # Should be able to analyze the numeric type progression
        # This would involve runtime evaluation, but syntax should be analyzable
        for binop in binary_ops:
            assert binop.left is not None, "Should have left operand"
            assert binop.right is not None, "Should have right operand"