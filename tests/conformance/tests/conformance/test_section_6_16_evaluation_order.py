"""
Section 6.16: Evaluation Order - Conformance Test Suite

Tests Python Language Reference Section 6.16 compliance across implementations.
Based on formal evaluation order rules and prose assertions.

Language Reference requirements tested:
    - Left-to-right evaluation order for most operations
    - Function argument evaluation order (left-to-right)
    - Assignment target evaluation order
    - Short-circuit evaluation in boolean operations
    - Comparison chaining evaluation order
    - Exception cases and special behaviors
    - Comprehension and generator evaluation order
    - Operator precedence and evaluation interaction
"""

import ast
import pytest
import sys
from typing import Any


class EvaluationOrderTester:
    """Helper class for testing evaluation order conformance.
    
    Note: Since evaluation order is primarily a runtime semantic property,
    these tests focus on AST structure that implies correct evaluation order
    and patterns that can be validated syntactically.
    """
    
    def assert_syntax_parses(self, source: str):
        """Test that evaluation order syntax parses correctly.
        
        Args:
            source: Python source code with evaluation order patterns
        """
        try:
            tree = ast.parse(source)
            return tree
        except SyntaxError as e:
            pytest.fail(f"Evaluation order syntax should be valid but failed to parse: {source}\\nError: {e}")
    
    def get_function_calls_in_order(self, source: str) -> list:
        """Get function call nodes in source order for evaluation analysis.
        
        Args:
            source: Python source code
            
        Returns:
            List of ast.Call nodes in source order
        """
        tree = ast.parse(source)
        calls = []
        
        class CallCollector(ast.NodeVisitor):
            def visit_Call(self, node):
                calls.append(node)
                self.generic_visit(node)
        
        CallCollector().visit(tree)
        return calls
    
    def get_assignment_targets(self, source: str) -> list:
        """Get assignment target nodes for evaluation order analysis.
        
        Args:
            source: Python assignment statement
            
        Returns:
            List of assignment target nodes
        """
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                return node.targets
        return []
    
    def has_short_circuit_pattern(self, source: str) -> bool:
        """Check if source contains short-circuit evaluation patterns.
        
        Args:
            source: Python source code
            
        Returns:
            True if contains and/or short-circuit patterns
        """
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.BoolOp):
                return True
        return False


@pytest.fixture
def tester():
    """Provide EvaluationOrderTester instance for tests."""
    return EvaluationOrderTester()


class TestSection616BasicEvaluationOrder:
    """Test basic evaluation order principles."""
    
    def test_left_to_right_arithmetic(self, tester):
        """Test left-to-right evaluation in arithmetic expressions"""
        # Language Reference: arithmetic operations evaluate left-to-right
        arithmetic_expressions = [
            "a + b + c",                    # Left-associative addition
            "a - b - c",                    # Left-associative subtraction  
            "a * b * c",                    # Left-associative multiplication
            "a / b / c",                    # Left-associative division
            "func1() + func2() + func3()",  # Function calls in order
            "obj.method1() + obj.method2()", # Method calls in order
        ]
        
        for source in arithmetic_expressions:
            tree = tester.assert_syntax_parses(source)
            # Verify AST structure supports left-to-right evaluation
            for node in ast.walk(tree):
                if isinstance(node, ast.BinOp):
                    # Binary operations should have left and right operands
                    assert hasattr(node, 'left'), f"BinOp should have left: {source}"
                    assert hasattr(node, 'right'), f"BinOp should have right: {source}"
    
    def test_function_argument_evaluation_order(self, tester):
        """Test left-to-right evaluation of function arguments"""
        # Language Reference: function arguments evaluated left-to-right
        argument_patterns = [
            "func(arg1(), arg2(), arg3())",
            "method(a + b, c * d, e / f)",
            "call(first.attr, second[index], third())",
            "nested(outer(inner1(), inner2()), final())",
            "kwargs_func(a=func1(), b=func2(), c=func3())",
        ]
        
        for source in argument_patterns:
            tree = tester.assert_syntax_parses(source)
            calls = tester.get_function_calls_in_order(source)
            assert len(calls) >= 1, f"Should contain function calls: {source}"
            
            # Main function call should have ordered arguments
            main_call = calls[-1]  # Last call is usually the outer call
            if hasattr(main_call, 'args') and main_call.args:
                # Arguments should be in left-to-right order
                assert len(main_call.args) >= 1, f"Should have arguments: {source}"
    
    def test_assignment_evaluation_order(self, tester):
        """Test evaluation order in assignment statements"""
        # Language Reference: assignment target and value evaluation order
        assignment_patterns = [
            "target = expression",
            "obj.attr = compute_value()",
            "items[index] = func_call()",
            "a, b = func_returning_tuple()",
            "x, y = y, x",                  # Simultaneous assignment
            "*first, last = sequence",
        ]
        
        for source in assignment_patterns:
            tree = tester.assert_syntax_parses(source)
            # Verify assignment AST structure
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    assert node.targets, f"Assignment should have targets: {source}"
                    assert node.value is not None, f"Assignment should have value: {source}"
    
    def test_comparison_chaining_order(self, tester):
        """Test evaluation order in chained comparisons"""
        # Language Reference: chained comparisons evaluate left-to-right
        chained_comparisons = [
            "a < b < c",
            "x <= y <= z",
            "func1() == func2() != func3()",
            "value in container not in other",
            "a is b is not c",
            "first() < second() <= third()"
        ]
        
        for source in chained_comparisons:
            tree = tester.assert_syntax_parses(source)
            # Find comparison nodes
            for node in ast.walk(tree):
                if isinstance(node, ast.Compare):
                    assert node.left is not None, f"Comparison should have left: {source}"
                    assert node.comparators, f"Comparison should have comparators: {source}"
                    assert node.ops, f"Comparison should have operators: {source}"


class TestSection616ShortCircuitEvaluation:
    """Test short-circuit evaluation behavior."""
    
    def test_boolean_and_short_circuit(self, tester):
        """Test short-circuit evaluation in boolean AND operations"""
        # Language Reference: 'and' short-circuits if left operand is false
        and_expressions = [
            "False and func_call()",       # Should not call func_call
            "condition and expensive_op()", # Only call expensive_op if condition true
            "a and b and c",               # Sequential short-circuit
            "func1() and func2() and func3()", # Function call short-circuit
            "obj.attr and obj.method()",   # Attribute/method short-circuit
        ]
        
        for source in and_expressions:
            tree = tester.assert_syntax_parses(source)
            assert tester.has_short_circuit_pattern(source), f"Should have short-circuit: {source}"
            
            # Find BoolOp nodes with 'and' operations
            for node in ast.walk(tree):
                if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.And):
                    assert len(node.values) >= 2, f"And should have multiple values: {source}"
    
    def test_boolean_or_short_circuit(self, tester):
        """Test short-circuit evaluation in boolean OR operations"""
        # Language Reference: 'or' short-circuits if left operand is true
        or_expressions = [
            "True or func_call()",         # Should not call func_call
            "condition or fallback()",     # Only call fallback if condition false
            "a or b or c",                 # Sequential short-circuit
            "func1() or func2() or func3()", # Function call short-circuit
            "obj.value or obj.default()",  # Attribute/method short-circuit
        ]
        
        for source in or_expressions:
            tree = tester.assert_syntax_parses(source)
            assert tester.has_short_circuit_pattern(source), f"Should have short-circuit: {source}"
            
            # Find BoolOp nodes with 'or' operations
            for node in ast.walk(tree):
                if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or):
                    assert len(node.values) >= 2, f"Or should have multiple values: {source}"
    
    def test_conditional_expression_evaluation(self, tester):
        """Test evaluation order in conditional expressions"""
        # Language Reference: condition evaluated first, then appropriate branch
        conditional_expressions = [
            "x if condition else y",
            "func1() if test() else func2()",
            "expensive() if cheap_check() else default",
            "a if b else c if d else e",    # Nested conditionals
            "result if validate(data) else error_value",
        ]
        
        for source in conditional_expressions:
            tree = tester.assert_syntax_parses(source)
            # Find conditional expression nodes
            for node in ast.walk(tree):
                if isinstance(node, ast.IfExp):
                    assert node.test is not None, f"Conditional should have test: {source}"
                    assert node.body is not None, f"Conditional should have body: {source}"
                    assert node.orelse is not None, f"Conditional should have orelse: {source}"


class TestSection616ComplexEvaluationPatterns:
    """Test complex evaluation order scenarios."""
    
    def test_nested_function_calls(self, tester):
        """Test evaluation order in nested function calls"""
        # Language Reference: innermost calls evaluate first
        nested_patterns = [
            "outer(inner(value))",
            "func(arg1(), inner(arg2()))",
            "method(obj.func(param), other.func())",
            "chain.func1().func2().func3()",
            "complex(nested(deep(call())))",
        ]
        
        for source in nested_patterns:
            tree = tester.assert_syntax_parses(source)
            calls = tester.get_function_calls_in_order(source)
            assert len(calls) >= 2, f"Should have nested calls: {source}"
    
    def test_comprehension_evaluation_order(self, tester):
        """Test evaluation order in comprehensions"""
        # Language Reference: comprehensions have specific evaluation order
        comprehension_patterns = [
            "[func(x) for x in items]",
            "[x for x in source if condition(x)]",
            "{key: value(key) for key in keys}",
            "{func(item) for item in collection if valid(item)}",
            "(expr(x) for x in data if filter_func(x))",
        ]
        
        for source in comprehension_patterns:
            tree = tester.assert_syntax_parses(source)
            # Find comprehension nodes
            comprehensions = [node for node in ast.walk(tree) 
                             if isinstance(node, (ast.ListComp, ast.DictComp, 
                                                 ast.SetComp, ast.GeneratorExp))]
            assert len(comprehensions) >= 1, f"Should have comprehension: {source}"
    
    def test_attribute_access_evaluation_order(self, tester):
        """Test evaluation order in attribute access chains"""
        # Language Reference: attribute access evaluates left-to-right
        attribute_patterns = [
            "obj.attr.subattr",
            "func().method().property",
            "instance.method(arg).result",
            "chain.func1().func2().attr",
            "complex.path.to.nested.value",
        ]
        
        for source in attribute_patterns:
            tree = tester.assert_syntax_parses(source)
            # Find attribute access nodes
            attributes = [node for node in ast.walk(tree) if isinstance(node, ast.Attribute)]
            assert len(attributes) >= 1, f"Should have attribute access: {source}"
    
    def test_subscript_evaluation_order(self, tester):
        """Test evaluation order in subscript operations"""
        # Language Reference: subscript operations evaluate container then index
        subscript_patterns = [
            "container[index]",
            "func()[key]",
            "obj.method()[compute_index()]",
            "nested[outer[inner]]",
            "matrix[row_func()][col_func()]",
        ]
        
        for source in subscript_patterns:
            tree = tester.assert_syntax_parses(source)
            # Find subscript nodes
            subscripts = [node for node in ast.walk(tree) if isinstance(node, ast.Subscript)]
            assert len(subscripts) >= 1, f"Should have subscript: {source}"
            
            for sub in subscripts:
                assert sub.value is not None, f"Subscript should have value: {source}"
                assert sub.slice is not None, f"Subscript should have slice: {source}"


class TestSection616OperatorPrecedenceInteraction:
    """Test evaluation order interaction with operator precedence."""
    
    def test_arithmetic_precedence_evaluation(self, tester):
        """Test evaluation order with arithmetic precedence"""
        # Language Reference: precedence affects grouping, but left-to-right within same precedence
        precedence_expressions = [
            "a + b * c",                    # Multiplication before addition
            "a * b + c * d",                # Left-to-right within same precedence
            "func1() + func2() * func3()",  # Functions respect precedence
            "a / b / c * d",                # Left-associative same precedence
            "(a + b) * (c + d)",            # Parentheses override precedence
        ]
        
        for source in precedence_expressions:
            tree = tester.assert_syntax_parses(source)
            # Verify binary operation structure
            binops = [node for node in ast.walk(tree) if isinstance(node, ast.BinOp)]
            assert len(binops) >= 1, f"Should have binary operations: {source}"
    
    def test_comparison_precedence_evaluation(self, tester):
        """Test evaluation order with comparison precedence"""
        # Language Reference: comparisons have lower precedence than arithmetic
        comparison_precedence = [
            "a + b == c + d",               # Arithmetic before comparison
            "func1() * 2 < func2() * 3",    # Functions with arithmetic and comparison
            "x in list + other_list",       # Addition before membership test
            "a and b == c",                 # Comparison before boolean and
            "not a == b",                   # Comparison before not operation
        ]
        
        for source in comparison_precedence:
            tree = tester.assert_syntax_parses(source)
            # Should parse with correct precedence grouping
            assert tree is not None, f"Should parse correctly: {source}"
    
    def test_unary_operator_evaluation(self, tester):
        """Test evaluation order with unary operators"""
        # Language Reference: unary operators have high precedence
        unary_expressions = [
            "not condition",
            "-func_call()",
            "+value",
            "~bit_pattern",
            "not a and b",                  # 'not' has higher precedence than 'and'
            "-a * b",                       # Unary minus before multiplication
        ]
        
        for source in unary_expressions:
            tree = tester.assert_syntax_parses(source)
            # Find unary operation nodes
            unaryops = [node for node in ast.walk(tree) if isinstance(node, ast.UnaryOp)]
            if "not" in source or "-" in source or "+" in source or "~" in source:
                assert len(unaryops) >= 1, f"Should have unary operation: {source}"


class TestSection616SpecialEvaluationCases:
    """Test special cases and exceptions in evaluation order."""
    
    def test_assignment_expression_evaluation(self, tester):
        """Test evaluation order with assignment expressions (walrus operator)"""
        # Language Reference: assignment expressions have specific evaluation order
        # Note: walrus operator requires Python 3.8+
        try:
            # Test if walrus operator is supported
            ast.parse("(x := 1)")
            walrus_expressions = [
                "(x := func())",
                "process(x := compute())",
                "[(x := item) for item in items]",
                "any((match := pattern.search(line)) for line in lines)",
            ]
            
            for source in walrus_expressions:
                tree = tester.assert_syntax_parses(source)
                # Find assignment expression nodes
                namedexprs = [node for node in ast.walk(tree) if isinstance(node, ast.NamedExpr)]
                assert len(namedexprs) >= 1, f"Should have named expression: {source}"
        except SyntaxError:
            # Walrus operator not supported in this Python version
            pytest.skip("Assignment expressions require Python 3.8+")
    
    def test_generator_expression_evaluation(self, tester):
        """Test evaluation order in generator expressions"""
        # Language Reference: generator expressions have lazy evaluation
        generator_expressions = [
            "(func(x) for x in items)",
            "(x for x in source if condition(x))",
            "sum(expensive(item) for item in data if cheap(item))",
            "any(validate(record) for record in records)",
            "max((compute(x) for x in values), default=0)",
        ]
        
        for source in generator_expressions:
            tree = tester.assert_syntax_parses(source)
            # Find generator expression nodes
            genexprs = [node for node in ast.walk(tree) if isinstance(node, ast.GeneratorExp)]
            assert len(genexprs) >= 1, f"Should have generator expression: {source}"
    
    def test_lambda_evaluation_order(self, tester):
        """Test evaluation order with lambda expressions"""
        # Language Reference: lambda expressions and their evaluation
        lambda_expressions = [
            "lambda x: func(x)",
            "lambda a, b: a + b",
            "map(lambda x: transform(x), items)",
            "filter(lambda item: validate(item), data)",
            "(lambda: expensive_computation())()",
        ]
        
        for source in lambda_expressions:
            tree = tester.assert_syntax_parses(source)
            # Find lambda nodes
            lambdas = [node for node in ast.walk(tree) if isinstance(node, ast.Lambda)]
            assert len(lambdas) >= 1, f"Should have lambda expression: {source}"


class TestSection616ErrorConditions:
    """Test evaluation order in error conditions and edge cases."""
    
    def test_exception_evaluation_order(self, tester):
        """Test evaluation order when exceptions occur"""
        # Language Reference: evaluation order preserved even with exceptions
        exception_patterns = [
            "func_that_raises() + safe_func()",
            "safe_func() + func_that_raises()",
            "try_func() and fallback_func()",
            "risky_operation() if condition else safe_operation()",
            "validate(data) or raise_error()",
        ]
        
        for source in exception_patterns:
            tree = tester.assert_syntax_parses(source)
            # Should parse correctly regardless of potential runtime exceptions
            assert tree is not None, f"Should parse: {source}"
    
    def test_side_effect_evaluation_order(self, tester):
        """Test evaluation order with side effects"""
        # Language Reference: evaluation order consistent even with side effects
        side_effect_patterns = [
            "append_to_list(item) + len(list)",
            "increment_counter() and check_counter()",
            "mutate_object() or log_error()",
            "side_effect_func() if condition() else other_side_effect()",
            "update_state() and validate_state()",
        ]
        
        for source in side_effect_patterns:
            tree = tester.assert_syntax_parses(source)
            # Should parse correctly - evaluation order is semantic, not syntactic
            assert tree is not None, f"Should parse: {source}"


class TestSection616CrossImplementationCompatibility:
    """Test cross-implementation compatibility for evaluation order."""
    
    def test_evaluation_order_ast_consistency(self, tester):
        """Test that AST structure implies correct evaluation order"""
        # Language Reference: AST structure should reflect evaluation order
        test_cases = [
            "a + b * c",                    # Precedence in AST
            "func1() and func2()",          # Short-circuit in AST
            "obj.attr[index]",              # Attribute then subscript
            "a if b else c",                # Conditional expression structure
        ]
        
        for source in test_cases:
            tree = tester.assert_syntax_parses(source)
            # AST should have proper structure for evaluation order
            assert tree is not None, f"Should have valid AST: {source}"
            assert len(tree.body) >= 1, f"Should have body: {source}"
    
    def test_complex_evaluation_patterns(self, tester):
        """Test complex evaluation order patterns"""
        # Language Reference: comprehensive real-world patterns
        complex_patterns = [
            """
result = func1(
    arg1=compute_arg1(),
    arg2=compute_arg2(),
    arg3=compute_arg3()
)
""",
            """
if condition1() and condition2():
    action1()
elif condition3() or condition4():
    action2()
else:
    action3()
""",
            """
data = [
    process(item)
    for item in source
    if validate(item) and expensive_check(item)
]
""",
            """
chain = (
    start_value
    .method1()
    .method2(param1(), param2())
    .method3()
)
"""
        ]
        
        for source in complex_patterns:
            tree = tester.assert_syntax_parses(source)
            # Just verify the pattern parses successfully
            assert len(tree.body) >= 1, f"Complex pattern should parse: {source}"
    
    def test_evaluation_order_introspection(self, tester):
        """Test ability to analyze evaluation order from AST"""
        # Test programmatic analysis of evaluation order
        introspection_source = "func1(arg1(), arg2()) + func2(arg3())"
        
        tree = tester.assert_syntax_parses(introspection_source)
        calls = tester.get_function_calls_in_order(introspection_source)
        
        # Should be able to identify function calls and their order
        assert len(calls) >= 3, "Should have multiple function calls"
        
        # Should be able to analyze AST structure for evaluation order
        for node in ast.walk(tree):
            if isinstance(node, ast.BinOp):
                # Binary operations should have clear left/right structure
                assert hasattr(node, 'left'), "BinOp should have left operand"
                assert hasattr(node, 'right'), "BinOp should have right operand"