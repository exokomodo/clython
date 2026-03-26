"""
Section 7.1: Expression Statements - Conformance Test Suite

Tests Python Language Reference Section 7.1 compliance across implementations.
Based on formal specifications for expression statement syntax and evaluation.

Language Reference requirements tested:
    - Simple expression statements: expression
    - Expression evaluation as statements
    - Expression statement vs assignment distinction
    - Side-effect expression statements
    - Expression statement context and precedence
    - Statement-level expression evaluation
    - Expression statement termination
    - Complex expression statement patterns
"""

import ast
import pytest
import sys
from typing import Any


class ExpressionStatementTester:
    """Helper class for testing expression statement conformance.
    
    Follows established AST-based validation pattern from previous sections.
    """
    
    def assert_expr_stmt_syntax_parses(self, source: str):
        """Test that expression statement syntax parses correctly.
        
        Args:
            source: Python expression statement source code
        """
        try:
            tree = ast.parse(source, mode='exec')
            # Verify the AST contains expression statement
            for node in tree.body:
                if isinstance(node, ast.Expr):
                    return tree
            # If no Expr node found, check if it's another valid statement type
            if len(tree.body) > 0:
                return tree
            pytest.fail(f"Expected expression statement not found in parsed AST for: {source}")
        except SyntaxError as e:
            pytest.fail(f"Expression statement syntax {source!r} failed to parse: {e}")
    
    def assert_expr_stmt_syntax_error(self, source: str):
        """Test that invalid expression statement syntax raises SyntaxError.
        
        Args:
            source: Python expression statement source that should be invalid
        """
        with pytest.raises(SyntaxError):
            ast.parse(source, mode='exec')

    def get_expression_statement_nodes(self, source: str) -> list:
        """Get expression statement nodes from source code.
        
        Args:
            source: Python expression statement source
            
        Returns:
            List of Expr AST nodes
        """
        tree = ast.parse(source, mode='exec')
        expr_nodes = []
        for node in tree.body:
            if isinstance(node, ast.Expr):
                expr_nodes.append(node)
        return expr_nodes

    def is_expression_statement(self, source: str) -> bool:
        """Check if source is parsed as expression statement.
        
        Args:
            source: Python statement source
            
        Returns:
            True if parsed as expression statement, False otherwise
        """
        try:
            tree = ast.parse(source, mode='exec')
            if len(tree.body) == 1 and isinstance(tree.body[0], ast.Expr):
                return True
            return False
        except:
            return False

    def get_expression_type(self, source: str):
        """Get the type of expression in expression statement.
        
        Args:
            source: Python expression statement source
            
        Returns:
            Type of the expression AST node
        """
        expr_nodes = self.get_expression_statement_nodes(source)
        if expr_nodes:
            return type(expr_nodes[0].value)
        return None


class TestSection71SimpleExpressionStatements:
    """Test Section 7.1: Simple Expression Statement Syntax"""
    
    @pytest.fixture
    def tester(self):
        return ExpressionStatementTester()

    def test_simple_expression_statements(self, tester):
        """Test simple expression statements"""
        # Language Reference: expression_stmt: expression_list
        simple_expressions = [
            "42",
            "3.14",
            "'hello'",
            "True",
            "None",
            "variable",
            "function",
            "module.attribute"
        ]
        
        for stmt in simple_expressions:
            tree = tester.assert_expr_stmt_syntax_parses(stmt)
            assert tester.is_expression_statement(stmt)

    def test_literal_expression_statements(self, tester):
        """Test literal expression statements"""
        # Various literal types as statements
        literal_statements = [
            "123",
            "0xff",
            "0o755",
            "0b1010",
            "3.14159",
            "2.5e-3",
            "'single quotes'",
            '"double quotes"',
            "'''triple single'''",
            '"""triple double"""',
            "r'raw string'",
            "b'bytes'",
            "f'formatted {value}'"
        ]
        
        for stmt in literal_statements:
            try:
                tree = tester.assert_expr_stmt_syntax_parses(stmt)
                assert tester.is_expression_statement(stmt)
            except AssertionError:
                # Some f-string or bytes patterns may need variable context
                if 'value' in stmt or sys.version_info < (3, 6):
                    pytest.skip(f"Skipping context-dependent literal: {stmt}")
                else:
                    raise

    def test_name_expression_statements(self, tester):
        """Test name/identifier expression statements"""
        # Name expressions as statements
        name_statements = [
            "variable",
            "function_name", 
            "class_name",
            "module_name",
            "_private",
            "__dunder__",
            "CamelCase",
            "snake_case",
            "CONSTANT"
        ]
        
        for stmt in name_statements:
            tree = tester.assert_expr_stmt_syntax_parses(stmt)
            assert tester.is_expression_statement(stmt)

    def test_constant_expression_statements(self, tester):
        """Test constant expression statements"""
        # Built-in constant expressions
        constant_statements = [
            "True",
            "False", 
            "None",
            "Ellipsis",
            "__debug__"
        ]
        
        for stmt in constant_statements:
            tree = tester.assert_expr_stmt_syntax_parses(stmt)
            assert tester.is_expression_statement(stmt)


class TestSection71FunctionCallStatements:
    """Test function call expression statements"""
    
    @pytest.fixture
    def tester(self):
        return ExpressionStatementTester()

    def test_simple_function_call_statements(self, tester):
        """Test simple function call statements"""
        # Function calls as statements
        call_statements = [
            "print()",
            "func()",
            "process(data)",
            "calculate(x, y)",
            "handler(request, response)",
            "validator(value, schema)"
        ]
        
        for stmt in call_statements:
            tree = tester.assert_expr_stmt_syntax_parses(stmt)
            assert tester.is_expression_statement(stmt)
            # Should be a Call expression
            expr_type = tester.get_expression_type(stmt)
            assert expr_type == ast.Call

    def test_method_call_statements(self, tester):
        """Test method call expression statements"""
        # Method calls as statements
        method_statements = [
            "obj.method()",
            "instance.process(data)",
            "self.validate()",
            "service.execute(command)",
            "parser.parse(text)",
            "logger.info(message)"
        ]
        
        for stmt in method_statements:
            tree = tester.assert_expr_stmt_syntax_parses(stmt)
            assert tester.is_expression_statement(stmt)
            expr_type = tester.get_expression_type(stmt)
            assert expr_type == ast.Call

    def test_chained_method_call_statements(self, tester):
        """Test chained method call statements"""
        # Chained method calls as statements
        chained_statements = [
            "obj.method1().method2()",
            "builder.add(item).build()",
            "query.filter(condition).order(field).execute()",
            "text.strip().lower().replace(' ', '_')",
            "data.transform().validate().save()"
        ]
        
        for stmt in chained_statements:
            tree = tester.assert_expr_stmt_syntax_parses(stmt)
            assert tester.is_expression_statement(stmt)
            expr_type = tester.get_expression_type(stmt)
            assert expr_type == ast.Call

    def test_nested_function_call_statements(self, tester):
        """Test nested function call statements"""
        # Nested function calls as statements  
        nested_statements = [
            "print(str(value))",
            "process(transform(data))",
            "validate(parse(normalize(input)))",
            "execute(compile(optimize(code)))",
            "display(format(calculate(x, y)))"
        ]
        
        for stmt in nested_statements:
            tree = tester.assert_expr_stmt_syntax_parses(stmt)
            assert tester.is_expression_statement(stmt)
            expr_type = tester.get_expression_type(stmt)
            assert expr_type == ast.Call


class TestSection71AttributeAccessStatements:
    """Test attribute access expression statements"""
    
    @pytest.fixture
    def tester(self):
        return ExpressionStatementTester()

    def test_simple_attribute_statements(self, tester):
        """Test simple attribute access statements"""
        # Attribute access as statements
        attribute_statements = [
            "obj.attr",
            "instance.value",
            "module.function",
            "class_name.method",
            "self.property",
            "config.setting"
        ]
        
        for stmt in attribute_statements:
            tree = tester.assert_expr_stmt_syntax_parses(stmt)
            assert tester.is_expression_statement(stmt)
            expr_type = tester.get_expression_type(stmt)
            assert expr_type == ast.Attribute

    def test_chained_attribute_statements(self, tester):
        """Test chained attribute access statements"""
        # Chained attribute access as statements
        chained_statements = [
            "obj.attr.subattr",
            "app.config.database.host",
            "service.client.connection.status",
            "parser.results.metadata.version",
            "instance.handler.logger.level"
        ]
        
        for stmt in chained_statements:
            tree = tester.assert_expr_stmt_syntax_parses(stmt)
            assert tester.is_expression_statement(stmt)
            expr_type = tester.get_expression_type(stmt)
            assert expr_type == ast.Attribute

    def test_attribute_with_subscript_statements(self, tester):
        """Test attribute access with subscript statements"""
        # Mixed attribute and subscript as statements
        mixed_statements = [
            "obj.items[0]",
            "data[key].value",
            "config.sections['main'].setting",
            "results.data[index].field",
            "cache[key].metadata.timestamp"
        ]
        
        for stmt in mixed_statements:
            tree = tester.assert_expr_stmt_syntax_parses(stmt)
            assert tester.is_expression_statement(stmt)


class TestSection71SubscriptStatements:
    """Test subscript expression statements"""
    
    @pytest.fixture
    def tester(self):
        return ExpressionStatementTester()

    def test_simple_subscript_statements(self, tester):
        """Test simple subscript statements"""
        # Subscript access as statements
        subscript_statements = [
            "array[0]",
            "dict[key]", 
            "items[index]",
            "data['name']",
            "cache[cache_key]",
            "lookup[hash_value]"
        ]
        
        for stmt in subscript_statements:
            tree = tester.assert_expr_stmt_syntax_parses(stmt)
            assert tester.is_expression_statement(stmt)
            expr_type = tester.get_expression_type(stmt)
            assert expr_type == ast.Subscript

    def test_chained_subscript_statements(self, tester):
        """Test chained subscript statements"""
        # Chained subscripts as statements
        chained_statements = [
            "matrix[row][col]",
            "data[section][key]",
            "nested[a][b][c]",
            "tree['root']['children'][0]",
            "cache[group][category][item]"
        ]
        
        for stmt in chained_statements:
            tree = tester.assert_expr_stmt_syntax_parses(stmt)
            assert tester.is_expression_statement(stmt)
            expr_type = tester.get_expression_type(stmt)
            assert expr_type == ast.Subscript

    def test_slice_statements(self, tester):
        """Test slice expression statements"""
        # Slice expressions as statements
        slice_statements = [
            "array[1:5]",
            "text[:10]",
            "data[start:end]",
            "items[::2]",
            "buffer[offset:offset + size]",
            "sequence[::-1]"
        ]
        
        for stmt in slice_statements:
            tree = tester.assert_expr_stmt_syntax_parses(stmt)
            assert tester.is_expression_statement(stmt)
            expr_type = tester.get_expression_type(stmt)
            assert expr_type == ast.Subscript


class TestSection71BinaryOperationStatements:
    """Test binary operation expression statements"""
    
    @pytest.fixture
    def tester(self):
        return ExpressionStatementTester()

    def test_arithmetic_operation_statements(self, tester):
        """Test arithmetic operation statements"""
        # Arithmetic expressions as statements
        arithmetic_statements = [
            "x + y",
            "a - b", 
            "x * y",
            "a / b",
            "x // y",
            "a % b",
            "x ** y",
            "x @ y"  # Matrix multiplication (Python 3.5+)
        ]
        
        for stmt in arithmetic_statements:
            try:
                tree = tester.assert_expr_stmt_syntax_parses(stmt)
                assert tester.is_expression_statement(stmt)
                expr_type = tester.get_expression_type(stmt)
                assert expr_type == ast.BinOp
            except AssertionError:
                # Skip @ operator on older Python versions
                if '@' in stmt and sys.version_info < (3, 5):
                    pytest.skip("Matrix multiplication @ requires Python 3.5+")
                else:
                    raise

    def test_comparison_statements(self, tester):
        """Test comparison expression statements"""
        # Comparison expressions as statements
        comparison_statements = [
            "x == y",
            "a != b",
            "x < y",
            "a <= b", 
            "x > y",
            "a >= b",
            "x is y",
            "a is not b",
            "x in y",
            "a not in b"
        ]
        
        for stmt in comparison_statements:
            tree = tester.assert_expr_stmt_syntax_parses(stmt)
            assert tester.is_expression_statement(stmt)
            expr_type = tester.get_expression_type(stmt)
            assert expr_type == ast.Compare

    def test_logical_operation_statements(self, tester):
        """Test logical operation statements"""
        # Logical expressions as statements
        logical_statements = [
            "x and y",
            "a or b",
            "not x",
            "x and y and z",
            "a or b or c",
            "not (x and y)",
            "(x or y) and z"
        ]
        
        for stmt in logical_statements:
            tree = tester.assert_expr_stmt_syntax_parses(stmt)
            assert tester.is_expression_statement(stmt)

    def test_bitwise_operation_statements(self, tester):
        """Test bitwise operation statements"""
        # Bitwise expressions as statements
        bitwise_statements = [
            "x | y",
            "a & b",
            "x ^ y",
            "~x",
            "a << 2",
            "b >> 1",
            "x & 0xFF",
            "flags | mask"
        ]
        
        for stmt in bitwise_statements:
            tree = tester.assert_expr_stmt_syntax_parses(stmt)
            assert tester.is_expression_statement(stmt)


class TestSection71UnaryOperationStatements:
    """Test unary operation expression statements"""
    
    @pytest.fixture
    def tester(self):
        return ExpressionStatementTester()

    def test_unary_arithmetic_statements(self, tester):
        """Test unary arithmetic operation statements"""
        # Unary arithmetic as statements
        unary_statements = [
            "+x",
            "-x",
            "+42",
            "-3.14",
            "+variable",
            "-expression"
        ]
        
        for stmt in unary_statements:
            tree = tester.assert_expr_stmt_syntax_parses(stmt)
            assert tester.is_expression_statement(stmt)
            expr_type = tester.get_expression_type(stmt)
            assert expr_type == ast.UnaryOp

    def test_unary_logical_statements(self, tester):
        """Test unary logical operation statements"""
        # Logical not as statements
        logical_unary_statements = [
            "not x",
            "not True",
            "not (x and y)",
            "not function()",
            "not obj.method()",
            "not array[index]"
        ]
        
        for stmt in logical_unary_statements:
            tree = tester.assert_expr_stmt_syntax_parses(stmt)
            assert tester.is_expression_statement(stmt)
            expr_type = tester.get_expression_type(stmt)
            assert expr_type == ast.UnaryOp

    def test_unary_bitwise_statements(self, tester):
        """Test unary bitwise operation statements"""
        # Bitwise complement as statements
        bitwise_unary_statements = [
            "~x",
            "~0",
            "~flags",
            "~mask",
            "~(a | b)",
            "~variable"
        ]
        
        for stmt in bitwise_unary_statements:
            tree = tester.assert_expr_stmt_syntax_parses(stmt)
            assert tester.is_expression_statement(stmt)
            expr_type = tester.get_expression_type(stmt)
            assert expr_type == ast.UnaryOp


class TestSection71ConditionalExpressionStatements:
    """Test conditional expression statements"""
    
    @pytest.fixture
    def tester(self):
        return ExpressionStatementTester()

    def test_ternary_conditional_statements(self, tester):
        """Test ternary conditional expression statements"""
        # Conditional expressions as statements
        conditional_statements = [
            "x if condition else y",
            "value if test else default",
            "result if success else error",
            "data if valid else None",
            "item if found else alternative",
            "obj.method() if obj else fallback()"
        ]
        
        for stmt in conditional_statements:
            tree = tester.assert_expr_stmt_syntax_parses(stmt)
            assert tester.is_expression_statement(stmt)
            expr_type = tester.get_expression_type(stmt)
            assert expr_type == ast.IfExp

    def test_nested_conditional_statements(self, tester):
        """Test nested conditional expression statements"""
        # Nested conditional expressions
        nested_statements = [
            "a if x else b if y else c",
            "first if cond1 else second if cond2 else third",
            "(a if inner_cond else b) if outer_cond else c",
            "value if check() else default if fallback() else error"
        ]
        
        for stmt in nested_statements:
            tree = tester.assert_expr_stmt_syntax_parses(stmt)
            assert tester.is_expression_statement(stmt)
            expr_type = tester.get_expression_type(stmt)
            assert expr_type == ast.IfExp


class TestSection71LambdaExpressionStatements:
    """Test lambda expression statements"""
    
    @pytest.fixture
    def tester(self):
        return ExpressionStatementTester()

    def test_simple_lambda_statements(self, tester):
        """Test simple lambda expression statements"""
        # Lambda expressions as statements
        lambda_statements = [
            "lambda: None",
            "lambda x: x",
            "lambda x, y: x + y",
            "lambda *args: sum(args)",
            "lambda **kwargs: kwargs",
            "lambda x=default: x * 2"
        ]
        
        for stmt in lambda_statements:
            tree = tester.assert_expr_stmt_syntax_parses(stmt)
            assert tester.is_expression_statement(stmt)
            expr_type = tester.get_expression_type(stmt)
            assert expr_type == ast.Lambda

    def test_complex_lambda_statements(self, tester):
        """Test complex lambda expression statements"""
        # Complex lambda expressions
        complex_lambda_statements = [
            "lambda x: x if x > 0 else 0",
            "lambda items: [item.upper() for item in items]",
            "lambda obj: obj.method() if obj else None",
            "lambda x, y=default: process(x, y)",
            "lambda *args, **kwargs: function(*args, **kwargs)"
        ]
        
        for stmt in complex_lambda_statements:
            tree = tester.assert_expr_stmt_syntax_parses(stmt)
            assert tester.is_expression_statement(stmt)
            expr_type = tester.get_expression_type(stmt)
            assert expr_type == ast.Lambda


class TestSection71ComprehensionStatements:
    """Test comprehension expression statements"""
    
    @pytest.fixture
    def tester(self):
        return ExpressionStatementTester()

    def test_list_comprehension_statements(self, tester):
        """Test list comprehension statements"""
        # List comprehensions as statements
        list_comp_statements = [
            "[x for x in items]",
            "[x * 2 for x in range(10)]",
            "[item.upper() for item in strings]",
            "[x for x in data if x > 0]",
            "[func(x) for x in items if predicate(x)]",
            "[[y for y in row] for row in matrix]"
        ]
        
        for stmt in list_comp_statements:
            tree = tester.assert_expr_stmt_syntax_parses(stmt)
            assert tester.is_expression_statement(stmt)
            expr_type = tester.get_expression_type(stmt)
            assert expr_type == ast.ListComp

    def test_set_comprehension_statements(self, tester):
        """Test set comprehension statements"""
        # Set comprehensions as statements
        set_comp_statements = [
            "{x for x in items}",
            "{x * 2 for x in range(10)}",
            "{item.lower() for item in strings}",
            "{x for x in data if x % 2 == 0}",
            "{func(x) for x in items if valid(x)}"
        ]
        
        for stmt in set_comp_statements:
            tree = tester.assert_expr_stmt_syntax_parses(stmt)
            assert tester.is_expression_statement(stmt)
            expr_type = tester.get_expression_type(stmt)
            assert expr_type == ast.SetComp

    def test_dict_comprehension_statements(self, tester):
        """Test dict comprehension statements"""
        # Dict comprehensions as statements
        dict_comp_statements = [
            "{k: v for k, v in items}",
            "{x: x**2 for x in range(5)}",
            "{key: value.upper() for key, value in pairs}",
            "{k: v for k, v in data.items() if v is not None}",
            "{func(k): transform(v) for k, v in mapping.items()}"
        ]
        
        for stmt in dict_comp_statements:
            tree = tester.assert_expr_stmt_syntax_parses(stmt)
            assert tester.is_expression_statement(stmt)
            expr_type = tester.get_expression_type(stmt)
            assert expr_type == ast.DictComp

    def test_generator_expression_statements(self, tester):
        """Test generator expression statements"""
        # Generator expressions as statements  
        gen_expr_statements = [
            "(x for x in items)",
            "(x * 2 for x in range(10))",
            "(item.strip() for item in lines)",
            "(x for x in data if x.active)",
            "(process(item) for item in batch if valid(item))"
        ]
        
        for stmt in gen_expr_statements:
            tree = tester.assert_expr_stmt_syntax_parses(stmt)
            assert tester.is_expression_statement(stmt)
            expr_type = tester.get_expression_type(stmt)
            assert expr_type == ast.GeneratorExp


class TestSection71ErrorConditions:
    """Test error conditions for expression statements"""
    
    @pytest.fixture
    def tester(self):
        return ExpressionStatementTester()

    def test_incomplete_expressions(self, tester):
        """Test incomplete expression statements"""
        # Incomplete expressions that should fail
        incomplete_expressions = [
            "x +",                        # Incomplete binary operation
            "not",                        # Incomplete unary operation
            "if condition",               # Incomplete conditional
            "lambda",                     # Incomplete lambda
            "[x for",                     # Incomplete comprehension
            "func(",                      # Incomplete function call
        ]
        
        for expr in incomplete_expressions:
            tester.assert_expr_stmt_syntax_error(expr)

    def test_invalid_operators(self, tester):
        """Test invalid operator usage"""
        # Invalid operator patterns that actually fail parsing
        invalid_operators = [
            "x === y",                    # Invalid triple equals
            "a !== b",                    # Invalid not triple equals
            "x <> y",                     # Invalid diamond operator (Python 2 style)
        ]
        
        for expr in invalid_operators:
            tester.assert_expr_stmt_syntax_error(expr)
        
        # Note: x ++ y and a -- b are valid (parsed as x + (+y) and a - (-b))

    def test_malformed_comprehensions(self, tester):
        """Test malformed comprehension syntax"""
        # Invalid comprehension patterns
        invalid_comprehensions = [
            "[x for]",                    # Missing iterator
            "[for x in items]",           # Missing expression
            "{x: for x in items}",        # Invalid dict comprehension
            "[x for x in]",               # Missing iterable
        ]
        
        for expr in invalid_comprehensions:
            tester.assert_expr_stmt_syntax_error(expr)


class TestSection71CrossImplementationCompatibility:
    """Test expression statement features across Python implementations"""
    
    @pytest.fixture
    def tester(self):
        return ExpressionStatementTester()

    def test_comprehensive_expression_statement_patterns(self, tester):
        """Test complex expression statement combinations"""
        # Complex expression statement patterns
        comprehensive_patterns = [
            "func(obj.method(arg)[key].attr for obj in items if obj.valid)",
            "sum(item.value * rate for item in data if item.active and item.value > threshold)",
            "process([transform(x) for x in batch]) if batch else handle_empty()",
            "cache.get(key, compute_default(params)) or fallback_value",
            "logger.info(f'Processing {len(items)} items') if debug_enabled else None"
        ]
        
        for stmt in comprehensive_patterns:
            try:
                tree = tester.assert_expr_stmt_syntax_parses(stmt)
                assert tester.is_expression_statement(stmt)
            except AssertionError:
                # Some patterns may require specific Python versions
                if 'f\'' in stmt and sys.version_info < (3, 6):
                    pytest.skip("F-strings require Python 3.6+")
                else:
                    raise

    def test_expression_statement_ast_validation(self, tester):
        """Test AST structure validation for expression statements"""
        # Complex expression for AST validation
        complex_expr_stmt = "process(data.transform().validate()) if data else log_error('No data')"
        
        tree = tester.assert_expr_stmt_syntax_parses(complex_expr_stmt)
        assert tester.is_expression_statement(complex_expr_stmt)
        
        # Verify it's an expression statement
        expr_nodes = tester.get_expression_statement_nodes(complex_expr_stmt)
        assert len(expr_nodes) == 1
        
        # Verify the expression type
        expr_type = tester.get_expression_type(complex_expr_stmt)
        assert expr_type == ast.IfExp

    def test_expression_statement_edge_cases(self, tester):
        """Test edge cases in expression statements"""
        # Edge cases and corner scenarios
        edge_case_statements = [
            "42",                         # Simple literal
            "variable",                   # Simple name
            "()",                         # Empty tuple
            "[]",                         # Empty list
            "{}",                         # Empty dict  
            "None",                       # None literal
            "...",                        # Ellipsis literal
            "True and False",             # Boolean expression
            "1 + 2 * 3 - 4 / 5",         # Complex arithmetic
            "f() or g() and h()"          # Complex logical
        ]
        
        for stmt in edge_case_statements:
            tree = tester.assert_expr_stmt_syntax_parses(stmt)
            assert tester.is_expression_statement(stmt)

    def test_expression_vs_assignment_distinction(self, tester):
        """Test distinction between expression statements and assignments"""
        # Expression statements (not assignments)
        expression_statements = [
            "func()",                     # Function call
            "obj.method()",               # Method call
            "value",                      # Name expression
            "items[0]",                   # Subscript expression
            "x + y",                      # Binary operation
        ]
        
        # Assignment statements (not expression statements)
        assignment_statements = [
            "x = 1",                      # Simple assignment
            "obj.attr = value",           # Attribute assignment
            "items[0] = new_value",       # Subscript assignment
            "x += 1",                     # Augmented assignment
        ]
        
        # Test expression statements
        for stmt in expression_statements:
            tree = tester.assert_expr_stmt_syntax_parses(stmt)
            assert tester.is_expression_statement(stmt)
        
        # Test assignment statements (should not be expression statements)
        for stmt in assignment_statements:
            tree = tester.assert_expr_stmt_syntax_parses(stmt)
            assert not tester.is_expression_statement(stmt)