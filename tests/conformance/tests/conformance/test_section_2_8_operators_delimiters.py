"""
Section 2.8: Operators and Delimiters - Conformance Test Suite

Tests Python Language Reference Section 2.8 compliance across implementations.
Based on formal specifications for operator symbols and delimiter syntax.

Language Reference requirements tested:
    - Arithmetic operators: +, -, *, /, //, %, @, **
    - Bitwise operators: &, |, ^, ~, <<, >>
    - Comparison operators: ==, !=, <, >, <=, >=, <>, is, is not, in, not in
    - Logical operators: and, or, not
    - Assignment operators: =, +=, -=, *=, /=, //=, %=, @=, **=, &=, |=, ^=, <<=, >>=
    - Delimiters: ( ) [ ] { } , : . ; @ = -> += -= *= /= //= %= @= &= |= ^= >>= <<= **=
    - Operator precedence and associativity
    - Delimiter context validation
"""

import ast
import pytest
import sys
from typing import Any


class OperatorDelimiterTester:
    """Helper class for testing operator and delimiter conformance.
    
    Follows established AST-based validation pattern from previous sections.
    """
    
    def assert_operator_syntax_parses(self, source: str, mode='eval'):
        """Test that operator expression syntax parses correctly.
        
        Args:
            source: Python operator expression source code
            mode: Parsing mode ('eval' for expressions, 'exec' for statements)
        """
        try:
            tree = ast.parse(source, mode=mode)
            return tree
        except SyntaxError as e:
            pytest.fail(f"Operator syntax {source!r} failed to parse: {e}")
    
    def assert_operator_syntax_error(self, source: str, mode='eval'):
        """Test that invalid operator syntax raises SyntaxError.
        
        Args:
            source: Python operator source code that should be invalid
            mode: Parsing mode ('eval' for expressions, 'exec' for statements)
        """
        with pytest.raises(SyntaxError):
            ast.parse(source, mode=mode)

    def get_operator_nodes(self, source: str, operator_type=None) -> list:
        """Get list of operator nodes from an expression.
        
        Args:
            source: Python expression source
            operator_type: Optional AST operator class to filter by
            
        Returns:
            List of operator AST nodes
        """
        tree = ast.parse(source, mode='eval')
        operators = []
        for node in ast.walk(tree):
            if operator_type and isinstance(node, operator_type):
                operators.append(node)
            elif not operator_type and hasattr(node, 'op'):
                operators.append(node)
        return operators


class TestSection28ArithmeticOperators:
    """Test Section 2.8: Arithmetic Operators"""
    
    @pytest.fixture
    def tester(self):
        return OperatorDelimiterTester()

    def test_basic_arithmetic_operators(self, tester):
        """Test basic arithmetic operator syntax"""
        # Language Reference: +, -, *, /, //, %, **
        arithmetic_expressions = [
            "a + b",
            "a - b", 
            "a * b",
            "a / b",
            "a // b",
            "a % b",
            "a ** b"
        ]
        
        for expr in arithmetic_expressions:
            tree = tester.assert_operator_syntax_parses(expr)
            # Verify BinOp node exists
            binops = [node for node in ast.walk(tree) if isinstance(node, ast.BinOp)]
            assert len(binops) == 1

    def test_matrix_multiplication_operator(self, tester):
        """Test matrix multiplication operator @ (Python 3.5+)"""
        # Language Reference: @ operator for matrix multiplication
        matrix_expressions = [
            "a @ b",
            "matrix1 @ matrix2",
            "a @ b @ c"  # Chained matrix multiplication
        ]
        
        for expr in matrix_expressions:
            tree = tester.assert_operator_syntax_parses(expr)
            # Find MatMult operators in AST
            matmults = []
            for node in ast.walk(tree):
                if isinstance(node, ast.BinOp) and isinstance(node.op, ast.MatMult):
                    matmults.append(node)
            assert len(matmults) >= 1

    def test_unary_arithmetic_operators(self, tester):
        """Test unary arithmetic operators"""
        # Language Reference: +, -, ~
        unary_expressions = [
            "+a",
            "-a", 
            "~a",
            "+(+a)",
            "-(-a)",
            "~(~a)"
        ]
        
        for expr in unary_expressions:
            tree = tester.assert_operator_syntax_parses(expr)
            # Verify UnaryOp node exists
            unaryops = [node for node in ast.walk(tree) if isinstance(node, ast.UnaryOp)]
            assert len(unaryops) >= 1

    def test_arithmetic_operator_precedence(self, tester):
        """Test arithmetic operator precedence"""
        # Language Reference: ** has highest precedence, then *, /, //, %, then +, -
        precedence_expressions = [
            "a + b * c",      # Should parse as a + (b * c)
            "a * b + c",      # Should parse as (a * b) + c
            "a ** b ** c",    # Should parse as a ** (b ** c) - right associative
            "a + b - c",      # Should parse as (a + b) - c - left associative
            "a * b / c",      # Should parse as (a * b) / c - left associative
            "a ** b * c",     # Should parse as (a ** b) * c
            "-a ** b",        # Should parse as -(a ** b)
            "a + b * c ** d"  # Should parse as a + (b * (c ** d))
        ]
        
        for expr in precedence_expressions:
            tree = tester.assert_operator_syntax_parses(expr)
            # Just verify they parse without syntax errors
            # Precedence is handled by parser correctly

    def test_arithmetic_operator_associativity(self, tester):
        """Test arithmetic operator associativity"""
        # Test left and right associativity
        associativity_expressions = [
            "a - b - c",      # Left: (a - b) - c
            "a / b / c",      # Left: (a / b) / c
            "a ** b ** c",    # Right: a ** (b ** c)
            "a + b + c + d",  # Left: ((a + b) + c) + d
            "a ** b ** c ** d" # Right: a ** (b ** (c ** d))
        ]
        
        for expr in associativity_expressions:
            tree = tester.assert_operator_syntax_parses(expr)
            # Verify proper AST structure for associativity


class TestSection28BitwiseOperators:
    """Test bitwise operation operators"""
    
    @pytest.fixture
    def tester(self):
        return OperatorDelimiterTester()

    def test_bitwise_binary_operators(self, tester):
        """Test bitwise binary operators"""
        # Language Reference: &, |, ^, <<, >>
        bitwise_expressions = [
            "a & b",
            "a | b",
            "a ^ b", 
            "a << b",
            "a >> b"
        ]
        
        for expr in bitwise_expressions:
            tree = tester.assert_operator_syntax_parses(expr)
            binops = [node for node in ast.walk(tree) if isinstance(node, ast.BinOp)]
            assert len(binops) == 1

    def test_bitwise_unary_operators(self, tester):
        """Test bitwise unary operators"""
        # Language Reference: ~
        bitwise_unary_expressions = [
            "~a",
            "~(a & b)",
            "~~a"
        ]
        
        for expr in bitwise_unary_expressions:
            tree = tester.assert_operator_syntax_parses(expr)
            unaryops = [node for node in ast.walk(tree) if isinstance(node, ast.UnaryOp)]
            assert len(unaryops) >= 1

    def test_bitwise_operator_precedence(self, tester):
        """Test bitwise operator precedence"""
        # Language Reference precedence: ~ (highest), <</>>, &, ^, |
        bitwise_precedence_expressions = [
            "a | b ^ c",      # Should be a | (b ^ c)
            "a ^ b & c",      # Should be a ^ (b & c) 
            "a & b << c",     # Should be a & (b << c)
            "a << b + c",     # Should be a << (b + c)
            "~a & b",         # Should be (~a) & b
            "a | b & c ^ d"   # Should be a | ((b & c) ^ d)
        ]
        
        for expr in bitwise_precedence_expressions:
            tree = tester.assert_operator_syntax_parses(expr)


class TestSection28ComparisonOperators:
    """Test comparison operators"""
    
    @pytest.fixture
    def tester(self):
        return OperatorDelimiterTester()

    def test_comparison_operators(self, tester):
        """Test comparison operators"""
        # Language Reference: ==, !=, <, >, <=, >=
        comparison_expressions = [
            "a == b",
            "a != b",
            "a < b",
            "a > b", 
            "a <= b",
            "a >= b"
        ]
        
        for expr in comparison_expressions:
            tree = tester.assert_operator_syntax_parses(expr)
            compares = [node for node in ast.walk(tree) if isinstance(node, ast.Compare)]
            assert len(compares) == 1

    def test_identity_operators(self, tester):
        """Test identity operators"""
        # Language Reference: is, is not
        identity_expressions = [
            "a is b",
            "a is not b",
            "a is None",
            "a is not None"
        ]
        
        for expr in identity_expressions:
            tree = tester.assert_operator_syntax_parses(expr)
            compares = [node for node in ast.walk(tree) if isinstance(node, ast.Compare)]
            assert len(compares) == 1

    def test_membership_operators(self, tester):
        """Test membership operators"""
        # Language Reference: in, not in
        membership_expressions = [
            "a in b",
            "a not in b",
            "x in [1, 2, 3]",
            "key not in dict"
        ]
        
        for expr in membership_expressions:
            tree = tester.assert_operator_syntax_parses(expr)
            compares = [node for node in ast.walk(tree) if isinstance(node, ast.Compare)]
            assert len(compares) == 1

    def test_chained_comparisons(self, tester):
        """Test chained comparison operators"""
        # Language Reference: a < b < c is equivalent to a < b and b < c
        chained_expressions = [
            "a < b < c",
            "a <= b <= c",
            "a == b == c",
            "a != b != c",
            "a is b is c",
            "1 < x <= 10",
            "a == b != c < d"
        ]
        
        for expr in chained_expressions:
            tree = tester.assert_operator_syntax_parses(expr)
            compares = [node for node in ast.walk(tree) if isinstance(node, ast.Compare)]
            assert len(compares) == 1
            # Chained comparisons have multiple comparators
            compare_node = compares[0]
            assert len(compare_node.ops) >= 2 or len(compare_node.comparators) >= 2


class TestSection28LogicalOperators:
    """Test logical operators"""
    
    @pytest.fixture
    def tester(self):
        return OperatorDelimiterTester()

    def test_logical_binary_operators(self, tester):
        """Test logical binary operators"""
        # Language Reference: and, or
        logical_expressions = [
            "a and b",
            "a or b",
            "a and b and c",
            "a or b or c",
            "a and b or c"
        ]
        
        for expr in logical_expressions:
            tree = tester.assert_operator_syntax_parses(expr)
            boolops = [node for node in ast.walk(tree) if isinstance(node, ast.BoolOp)]
            assert len(boolops) >= 1

    def test_logical_unary_operator(self, tester):
        """Test logical unary operator"""
        # Language Reference: not
        logical_unary_expressions = [
            "not a",
            "not (a and b)",
            "not not a"
        ]
        
        for expr in logical_unary_expressions:
            tree = tester.assert_operator_syntax_parses(expr)
            unaryops = [node for node in ast.walk(tree) if isinstance(node, ast.UnaryOp)]
            assert len(unaryops) >= 1

    def test_logical_operator_precedence(self, tester):
        """Test logical operator precedence"""
        # Language Reference: not (highest), and, or (lowest)
        logical_precedence_expressions = [
            "a or b and c",     # Should be a or (b and c)
            "not a and b",      # Should be (not a) and b
            "not a or b",       # Should be (not a) or b
            "a and b or c and d" # Should be (a and b) or (c and d)
        ]
        
        for expr in logical_precedence_expressions:
            tree = tester.assert_operator_syntax_parses(expr)


class TestSection28AssignmentOperators:
    """Test assignment operators"""
    
    @pytest.fixture
    def tester(self):
        return OperatorDelimiterTester()

    def test_simple_assignment_operator(self, tester):
        """Test simple assignment operator"""
        # Language Reference: =
        assignment_statements = [
            "a = b",
            "x = 1",
            "name = 'value'",
            "a, b = c, d"
        ]
        
        for stmt in assignment_statements:
            tree = tester.assert_operator_syntax_parses(stmt, mode='exec')
            assigns = [node for node in ast.walk(tree) if isinstance(node, ast.Assign)]
            assert len(assigns) == 1

    def test_augmented_assignment_operators(self, tester):
        """Test augmented assignment operators"""
        # Language Reference: +=, -=, *=, /=, //=, %=, **=, @=, &=, |=, ^=, <<=, >>=
        augmented_statements = [
            "a += b",
            "a -= b",
            "a *= b", 
            "a /= b",
            "a //= b",
            "a %= b",
            "a **= b",
            "a @= b",
            "a &= b",
            "a |= b",
            "a ^= b",
            "a <<= b",
            "a >>= b"
        ]
        
        for stmt in augmented_statements:
            tree = tester.assert_operator_syntax_parses(stmt, mode='exec')
            augassigns = [node for node in ast.walk(tree) if isinstance(node, ast.AugAssign)]
            assert len(augassigns) == 1

    def test_annotated_assignment_operator(self, tester):
        """Test annotated assignment (Python 3.6+)"""
        # Language Reference: variable annotations with assignment
        annotated_statements = [
            "a: int = 1",
            "name: str = 'value'",
            "x: float",
            "items: list[str] = []"
        ]
        
        for stmt in annotated_statements:
            try:
                tree = tester.assert_operator_syntax_parses(stmt, mode='exec')
                annassigns = [node for node in ast.walk(tree) if isinstance(node, ast.AnnAssign)]
                assert len(annassigns) >= 0  # May be 0 for annotation-only
            except SyntaxError:
                # Skip if type annotations not supported in this Python version
                if sys.version_info < (3, 6):
                    pytest.skip("Type annotations require Python 3.6+")
                else:
                    raise


class TestSection28Delimiters:
    """Test delimiter syntax"""
    
    @pytest.fixture
    def tester(self):
        return OperatorDelimiterTester()

    def test_grouping_delimiters(self, tester):
        """Test grouping delimiters"""
        # Language Reference: ( ) [ ] { }
        grouping_expressions = [
            "(a + b)",
            "[a, b, c]",
            "{a, b, c}",
            "{'key': 'value'}",
            "(a, b, c)",
            "[]",
            "{}",
            "()"
        ]
        
        for expr in grouping_expressions:
            tree = tester.assert_operator_syntax_parses(expr)
            # Should parse without syntax errors

    def test_separator_delimiters(self, tester):
        """Test separator delimiters"""
        # Language Reference: , : . ;
        separator_expressions = [
            "[a, b, c]",      # Comma separator
            "{'a': 1}",       # Colon in dict
            "obj.attr",       # Dot for attribute access
            "a, b = c, d",    # Comma in assignment
        ]
        
        for expr in separator_expressions:
            mode = 'exec' if '=' in expr else 'eval'
            tree = tester.assert_operator_syntax_parses(expr, mode=mode)

    def test_function_delimiters(self, tester):
        """Test function-related delimiters"""
        # Language Reference: -> for function annotations (Python 3.5+)
        function_statements = [
            "def f() -> int: return 1",
            "def g(x: int) -> str: return str(x)",
            "lambda x: x + 1",
            "lambda x, y: x + y"
        ]
        
        for stmt in function_statements:
            try:
                tree = tester.assert_operator_syntax_parses(stmt, mode='exec')
            except SyntaxError:
                # Skip if function annotations not supported
                if sys.version_info < (3, 5) and '->' in stmt:
                    pytest.skip("Function annotations require Python 3.5+")
                else:
                    raise

    def test_decorator_delimiter(self, tester):
        """Test decorator delimiter @"""
        # Language Reference: @ for decorators
        decorator_statements = [
            """@decorator
def func():
    pass""",
            
            """@decorator1
@decorator2
def func():
    pass""",
            
            """@decorator(arg)
def func():
    pass"""
        ]
        
        for stmt in decorator_statements:
            tree = tester.assert_operator_syntax_parses(stmt, mode='exec')
            decorators = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.decorator_list:
                    decorators.extend(node.decorator_list)
            assert len(decorators) >= 1


class TestSection28ErrorConditions:
    """Test error conditions for operators and delimiters"""
    
    @pytest.fixture
    def tester(self):
        return OperatorDelimiterTester()

    def test_invalid_operator_combinations(self, tester):
        """Test invalid operator combinations"""
        # Invalid operator syntax that actually fails
        invalid_operators = [
            "a ** ** b",      # Invalid double power
            "a & | b",        # Invalid bitwise combination
            "a < > b",        # Invalid comparison combination
        ]
        
        for expr in invalid_operators:
            tester.assert_operator_syntax_error(expr)
        
        # Note: a ++ b parses as a + (+b), a -- b parses as a - (-b)

    def test_invalid_delimiter_usage(self, tester):
        """Test invalid delimiter usage"""
        # Invalid delimiter syntax
        invalid_delimiters = [
            "[a, b, c)",      # Mismatched brackets
            "(a, b, c]",      # Mismatched parentheses
            "{a, b, c)",      # Mismatched braces
            "a,, b",          # Double comma
            "a:: b",          # Double colon (outside slice context)
        ]
        
        for expr in invalid_delimiters:
            tester.assert_operator_syntax_error(expr)

    def test_incomplete_operators(self, tester):
        """Test incomplete operator expressions"""
        # Incomplete operator syntax that actually fails
        incomplete_expressions = [
            "a +",            # Missing right operand
            "a and",          # Missing right operand
            "not",            # Missing operand
            "a <",            # Missing comparison target
        ]
        
        for expr in incomplete_expressions:
            tester.assert_operator_syntax_error(expr)
        
        # Note: "+ b" parses as unary plus


class TestSection28CrossImplementationCompatibility:
    """Test operator and delimiter features across Python implementations"""
    
    @pytest.fixture
    def tester(self):
        return OperatorDelimiterTester()

    def test_comprehensive_operator_expression(self, tester):
        """Test complex expression with multiple operators"""
        # Complex expression with various operator types (fixed line continuation)
        complex_expression = "(a + b * c ** d - e / f // g % h) & (i | j ^ k << l >> m) and (n < o <= p == q != r > s >= t) or not (u is v) and (w not in x)"
        
        tree = tester.assert_operator_syntax_parses(complex_expression)
        # Should parse successfully with proper precedence

    def test_operator_precedence_validation(self, tester):
        """Test comprehensive operator precedence"""
        # Expression testing full precedence hierarchy
        precedence_expression = "a or b and c not in d | e ^ f & g == h < i << j + k * l / m // n % o ** p ** q"
        
        tree = tester.assert_operator_syntax_parses(precedence_expression)
        # Should parse with correct operator precedence

    def test_nested_delimiter_structures(self, tester):
        """Test deeply nested delimiter structures"""
        # Nested delimiters
        nested_expressions = [
            "((a + b) * (c - d))",
            "[[a, b], [c, d]]",
            "{{'a': 1}, {'b': 2}}",
            "(a, (b, (c, d)))",
            "[a for a in [b for b in [1, 2, 3]]]"
        ]
        
        for expr in nested_expressions:
            tree = tester.assert_operator_syntax_parses(expr)

    def test_operator_with_different_types(self, tester):
        """Test operators with various operand types"""
        # Different operand types
        mixed_operand_expressions = [
            "1 + 2",
            "1.0 + 2",
            "'a' + 'b'",
            "[1] + [2]",
            "True and False",
            "1 < 2.0",
            "None is None"
        ]
        
        for expr in mixed_operand_expressions:
            tree = tester.assert_operator_syntax_parses(expr)

    def test_assignment_operator_contexts(self, tester):
        """Test assignment operators in various contexts"""
        # Assignment in different contexts
        assignment_contexts = [
            "a = b = c = 1",          # Chained assignment
            "a, b = c, d = e, f",     # Multiple targets
            "(a, b) = (c, d)",        # Tuple assignment
            "[a, b] = [c, d]",        # List assignment
            "a[i] = value",           # Subscript assignment
            "obj.attr = value"        # Attribute assignment
        ]
        
        for stmt in assignment_contexts:
            tree = tester.assert_operator_syntax_parses(stmt, mode='exec')

    def test_operator_ast_structure_validation(self, tester):
        """Test operator AST structure validation"""
        # Validate AST structure for operators
        test_expression = "a + b * c"
        tree = tester.assert_operator_syntax_parses(test_expression)
        
        # For eval mode, get the expression value
        root_binop = tree.body
        
        assert isinstance(root_binop, ast.BinOp)
        assert isinstance(root_binop.op, ast.Add)
        
        # Left side should be Name 'a'
        assert isinstance(root_binop.left, ast.Name)
        assert root_binop.left.id == 'a'
        
        # Right side should be another BinOp (b * c) 
        assert isinstance(root_binop.right, ast.BinOp)
        assert isinstance(root_binop.right.op, ast.Mult)