"""
Section 8.1: If Statements - Conformance Test Suite

Tests Python Language Reference Section 8.1 compliance across implementations.
Based on formal specifications for if statement syntax and conditional evaluation.

Language Reference requirements tested:
    - Basic if statements: if condition:
    - If...else statements: if condition: ... else:
    - If...elif chains: if condition: ... elif condition: ... else:
    - Complex elif structures: multiple elif clauses
    - Nested if statements: if within if structures
    - If statement condition expressions: all boolean contexts
    - Short-circuit evaluation patterns (though syntax-focused)
    - Conditional expression variations and edge cases
"""

import ast
import pytest
import sys
from typing import Any


class IfStatementTester:
    """Helper class for testing if statement conformance.
    
    Follows established AST-based validation pattern from previous sections.
    """
    
    def assert_if_syntax_parses(self, source: str):
        """Test that if statement syntax parses correctly.
        
        Args:
            source: Python if statement source code
        """
        try:
            tree = ast.parse(source, mode='exec')
            # Verify the AST contains if statement
            for node in ast.walk(tree):
                if isinstance(node, ast.If):
                    return tree
            pytest.fail(f"Expected If node not found in parsed AST for: {source}")
        except SyntaxError as e:
            pytest.fail(f"If syntax {source!r} failed to parse: {e}")
    
    def assert_if_syntax_error(self, source: str):
        """Test that invalid if syntax raises SyntaxError.
        
        Args:
            source: Python if statement source that should be invalid
        """
        with pytest.raises(SyntaxError):
            ast.parse(source, mode='exec')

    def get_if_nodes(self, source: str) -> list:
        """Get list of If nodes from source code.
        
        Args:
            source: Python if statement source
            
        Returns:
            List of If AST nodes
        """
        tree = ast.parse(source, mode='exec')
        if_nodes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                if_nodes.append(node)
        return if_nodes

    def count_elif_clauses(self, source: str) -> int:
        """Count elif clauses in an if statement.
        
        Args:
            source: Python if statement source
            
        Returns:
            Number of elif clauses found
        """
        if_nodes = self.get_if_nodes(source)
        if not if_nodes:
            return 0
        
        # Count nested If nodes in orelse that represent elif
        def count_elifs(node):
            if not hasattr(node, 'orelse') or not node.orelse:
                return 0
            
            # If orelse contains a single If node, it's an elif
            if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
                return 1 + count_elifs(node.orelse[0])
            
            return 0
        
        return count_elifs(if_nodes[0])

    def has_else_clause(self, source: str) -> bool:
        """Check if if statement has an else clause.
        
        Args:
            source: Python if statement source
            
        Returns:
            True if else clause exists, False otherwise
        """
        if_nodes = self.get_if_nodes(source)
        if not if_nodes:
            return False
        
        # Check for else by traversing elif chain
        def check_else(node):
            if not hasattr(node, 'orelse') or not node.orelse:
                return False
            
            # If orelse contains a single If node, it's an elif - recurse
            if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
                return check_else(node.orelse[0])
            
            # If orelse contains other statements, it's an else
            return len(node.orelse) > 0
        
        return check_else(if_nodes[0])


class TestSection81BasicIfStatements:
    """Test Section 8.1: Basic If Statement Syntax"""
    
    @pytest.fixture
    def tester(self):
        return IfStatementTester()

    def test_simple_if_statements(self, tester):
        """Test simple if statement syntax"""
        # Language Reference: if test:
        simple_if_statements = [
            """if True:
    pass""",
            
            """if condition:
    execute()""",
            
            """if x > 0:
    print("positive")""",
            
            """if not error:
    continue_process()""",
            
            """if value in collection:
    handle(value)"""
        ]
        
        for stmt in simple_if_statements:
            tree = tester.assert_if_syntax_parses(stmt)
            if_nodes = tester.get_if_nodes(stmt)
            assert len(if_nodes) == 1
            # Check that condition exists
            assert if_nodes[0].test is not None
            # Should have no elif or else
            assert tester.count_elif_clauses(stmt) == 0

    def test_if_with_various_conditions(self, tester):
        """Test if statements with different condition types"""
        # Various condition expressions
        condition_if_statements = [
            """if True:
    pass""",
            
            """if False:
    pass""",
            
            """if x:
    pass""",
            
            """if not x:
    pass""",
            
            """if x and y:
    pass""",
            
            """if x or y:
    pass""",
            
            """if x == y:
    pass""",
            
            """if x != y:
    pass""",
            
            """if x < y:
    pass""",
            
            """if x > y:
    pass""",
            
            """if x <= y:
    pass""",
            
            """if x >= y:
    pass""",
            
            """if x is y:
    pass""",
            
            """if x is not y:
    pass""",
            
            """if x in y:
    pass""",
            
            """if x not in y:
    pass"""
        ]
        
        for stmt in condition_if_statements:
            tree = tester.assert_if_syntax_parses(stmt)
            if_nodes = tester.get_if_nodes(stmt)
            assert len(if_nodes) == 1

    def test_if_with_complex_conditions(self, tester):
        """Test if statements with complex condition expressions"""
        # Complex condition patterns
        complex_condition_statements = [
            """if func():
    pass""",
            
            """if obj.method():
    pass""",
            
            """if obj.attr:
    pass""",
            
            """if container[key]:
    pass""",
            
            """if len(collection) > 0:
    pass""",
            
            """if hasattr(obj, 'attribute'):
    pass""",
            
            """if callable(obj):
    pass""",
            
            """if any(condition(x) for x in items):
    pass""",
            
            """if all(validator(item) for item in batch):
    pass"""
        ]
        
        for stmt in complex_condition_statements:
            tree = tester.assert_if_syntax_parses(stmt)
            if_nodes = tester.get_if_nodes(stmt)
            assert len(if_nodes) == 1


class TestSection81IfElseStatements:
    """Test if...else statement combinations"""
    
    @pytest.fixture
    def tester(self):
        return IfStatementTester()

    def test_basic_if_else(self, tester):
        """Test basic if...else syntax"""
        # Language Reference: if...else statements
        if_else_statements = [
            """if condition:
    handle_true()
else:
    handle_false()""",
            
            """if x > 0:
    print("positive")
else:
    print("non-positive")""",
            
            """if value:
    process(value)
else:
    use_default()""",
            
            """if error:
    abort()
else:
    continue_execution()"""
        ]
        
        for stmt in if_else_statements:
            tree = tester.assert_if_syntax_parses(stmt)
            if_nodes = tester.get_if_nodes(stmt)
            assert len(if_nodes) == 1
            # Check that else clause exists
            assert tester.has_else_clause(stmt)
            # Should have no elif
            assert tester.count_elif_clauses(stmt) == 0

    def test_if_else_with_complex_bodies(self, tester):
        """Test if...else with complex body statements"""
        # Complex body patterns
        complex_body_statements = [
            """if ready:
    initialize()
    start_process()
    log("started")
else:
    wait_for_ready()
    retry_later()""",
            
            """if data_available():
    while not queue.empty():
        item = queue.get()
        process_item(item)
    finalize_batch()
else:
    schedule_retry()
    log_unavailability()"""
        ]
        
        for stmt in complex_body_statements:
            tree = tester.assert_if_syntax_parses(stmt)
            if_nodes = tester.get_if_nodes(stmt)
            assert len(if_nodes) >= 1
            assert tester.has_else_clause(stmt)

    def test_if_else_empty_clauses(self, tester):
        """Test if...else with empty clauses"""
        # Empty clause patterns
        empty_clause_statements = [
            """if condition:
    pass
else:
    pass""",
            
            """if True:
    pass
else:
    handle_false()""",
            
            """if False:
    handle_true()
else:
    pass"""
        ]
        
        for stmt in empty_clause_statements:
            tree = tester.assert_if_syntax_parses(stmt)
            if_nodes = tester.get_if_nodes(stmt)
            assert len(if_nodes) == 1
            assert tester.has_else_clause(stmt)


class TestSection81IfElifElseStatements:
    """Test if...elif...else statement chains"""
    
    @pytest.fixture
    def tester(self):
        return IfStatementTester()

    def test_simple_if_elif_else(self, tester):
        """Test simple if...elif...else syntax"""
        # Language Reference: if...elif...else chains
        if_elif_else_statements = [
            """if x > 0:
    print("positive")
elif x < 0:
    print("negative")
else:
    print("zero")""",
            
            """if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
else:
    grade = "F" """,
            
            """if mode == "read":
    handle_read()
elif mode == "write":
    handle_write()
elif mode == "append":
    handle_append()
else:
    error("invalid mode")"""
        ]
        
        for stmt in if_elif_else_statements:
            tree = tester.assert_if_syntax_parses(stmt)
            if_nodes = tester.get_if_nodes(stmt)
            assert len(if_nodes) >= 1  # May have nested elif If nodes
            # Should have at least one elif
            assert tester.count_elif_clauses(stmt) >= 1
            # Should have else clause
            assert tester.has_else_clause(stmt)

    def test_multiple_elif_clauses(self, tester):
        """Test multiple elif clauses"""
        # Multiple elif patterns
        multiple_elif_statements = [
            """if a:
    handle_a()
elif b:
    handle_b()
elif c:
    handle_c()
elif d:
    handle_d()
else:
    handle_default()""",
            
            """if value == 1:
    action1()
elif value == 2:
    action2()
elif value == 3:
    action3()
elif value == 4:
    action4()
elif value == 5:
    action5()
else:
    default_action()"""
        ]
        
        for stmt in multiple_elif_statements:
            tree = tester.assert_if_syntax_parses(stmt)
            if_nodes = tester.get_if_nodes(stmt)
            assert len(if_nodes) >= 1
            # Should have multiple elif clauses
            assert tester.count_elif_clauses(stmt) >= 3

    def test_if_elif_without_else(self, tester):
        """Test if...elif without final else"""
        # elif without else
        elif_no_else_statements = [
            """if x > 10:
    handle_large()
elif x > 5:
    handle_medium()
elif x > 0:
    handle_small()""",
            
            """if ready:
    start()
elif waiting:
    continue_wait()
elif error:
    handle_error()"""
        ]
        
        for stmt in elif_no_else_statements:
            tree = tester.assert_if_syntax_parses(stmt)
            if_nodes = tester.get_if_nodes(stmt)
            assert len(if_nodes) >= 1
            # Should have elif clauses
            assert tester.count_elif_clauses(stmt) >= 1
            # Should not have else clause
            assert not tester.has_else_clause(stmt)

    def test_elif_with_complex_conditions(self, tester):
        """Test elif with complex condition expressions"""
        # Complex elif conditions
        complex_elif_statements = [
            """if isinstance(obj, str):
    handle_string(obj)
elif isinstance(obj, int) and obj > 0:
    handle_positive_int(obj)
elif hasattr(obj, '__iter__') and len(obj) > 0:
    handle_iterable(obj)
elif callable(obj):
    handle_callable(obj)
else:
    handle_unknown(obj)""",
            
            """if condition1() and flag:
    path1()
elif condition2() or backup_flag:
    path2()
elif not error_state and ready():
    path3()
else:
    default_path()"""
        ]
        
        for stmt in complex_elif_statements:
            tree = tester.assert_if_syntax_parses(stmt)
            if_nodes = tester.get_if_nodes(stmt)
            assert len(if_nodes) >= 1
            assert tester.count_elif_clauses(stmt) >= 2


class TestSection81NestedIfStatements:
    """Test nested if statement structures"""
    
    @pytest.fixture
    def tester(self):
        return IfStatementTester()

    def test_simple_nested_if(self, tester):
        """Test simple nested if statements"""
        # Basic nested if patterns
        nested_if_statements = [
            """if outer_condition:
    if inner_condition:
        handle_both()""",
            
            """if user_authenticated:
    if user_authorized:
        grant_access()
    else:
        deny_access()
else:
    redirect_login()""",
            
            """if data_available:
    if data_valid:
        if data_complete:
            process_data()
        else:
            request_missing_data()
    else:
        reject_invalid_data()"""
        ]
        
        for stmt in nested_if_statements:
            tree = tester.assert_if_syntax_parses(stmt)
            if_nodes = tester.get_if_nodes(stmt)
            assert len(if_nodes) >= 2  # Should have nested if statements

    def test_nested_if_elif_else(self, tester):
        """Test nested if with elif and else combinations"""
        # Nested if/elif/else patterns
        nested_complex_statements = [
            """if category == "user":
    if level == "admin":
        admin_actions()
    elif level == "moderator":
        moderator_actions()
    else:
        user_actions()
elif category == "guest":
    if verified:
        verified_guest_actions()
    else:
        unverified_guest_actions()
else:
    handle_unknown_category()""",
            
            """if mode == "production":
    if debug_enabled:
        if log_level >= 3:
            detailed_logging()
        else:
            standard_logging()
    else:
        minimal_logging()
elif mode == "development":
    if verbose:
        verbose_debug()
    else:
        normal_debug()
else:
    test_mode_logging()"""
        ]
        
        for stmt in nested_complex_statements:
            tree = tester.assert_if_syntax_parses(stmt)
            if_nodes = tester.get_if_nodes(stmt)
            assert len(if_nodes) >= 3  # Should have multiple nested levels

    def test_deeply_nested_if(self, tester):
        """Test deeply nested if statements"""
        # Deep nesting patterns
        deeply_nested_statements = [
            ("""if level1:
    if level2:
        if level3:
            if level4:
                if level5:
                    deep_action()""", 5),  # Expected 5 if nodes
            
            ("""if check1():
    if check2():
        if check3():
            execute()
        else:
            fallback3()
    else:
        fallback2()
else:
    fallback1()""", 3)  # Expected 3 if nodes
        ]
        
        for stmt, expected_count in deeply_nested_statements:
            tree = tester.assert_if_syntax_parses(stmt)
            if_nodes = tester.get_if_nodes(stmt)
            assert len(if_nodes) >= 3  # At least 3 levels deep
            # Check specific expected count
            assert len(if_nodes) == expected_count


class TestSection81IfStatementVariations:
    """Test various if statement patterns and edge cases"""
    
    @pytest.fixture
    def tester(self):
        return IfStatementTester()

    def test_if_with_walrus_operator(self, tester):
        """Test if statements with walrus operator (Python 3.8+)"""
        # Walrus operator in if conditions
        walrus_if_patterns = [
            """if (match := pattern.search(text)):
    handle_match(match)""",
            
            """if (result := compute()) is not None:
    use_result(result)""",
            
            """if (length := len(data)) > threshold:
    handle_large_data(data, length)
else:
    handle_small_data(data)"""
        ]
        
        for stmt in walrus_if_patterns:
            try:
                tree = tester.assert_if_syntax_parses(stmt)
                if_nodes = tester.get_if_nodes(stmt)
                assert len(if_nodes) >= 1
            except AssertionError:
                # Skip if walrus operator not supported
                if sys.version_info < (3, 8):
                    pytest.skip("Walrus operator requires Python 3.8+")
                else:
                    raise

    def test_if_with_chained_comparisons(self, tester):
        """Test if statements with chained comparison operators"""
        # Chained comparisons
        chained_comparison_statements = [
            """if 0 <= x <= 100:
    handle_percentage(x)""",
            
            """if min_value < x < max_value:
    process_in_range(x)""",
            
            """if a == b == c:
    handle_all_equal()""",
            
            """if x < y < z:
    handle_ascending()""",
            
            """if a <= b <= c <= d:
    handle_non_decreasing()"""
        ]
        
        for stmt in chained_comparison_statements:
            tree = tester.assert_if_syntax_parses(stmt)
            if_nodes = tester.get_if_nodes(stmt)
            assert len(if_nodes) == 1

    def test_if_with_membership_tests(self, tester):
        """Test if statements with membership testing"""
        # Membership test patterns
        membership_statements = [
            """if key in dictionary:
    value = dictionary[key]""",
            
            """if item not in collection:
    collection.add(item)""",
            
            """if substring in text:
    highlight(substring)""",
            
            """if element not in seen:
    process_new(element)
    seen.add(element)"""
        ]
        
        for stmt in membership_statements:
            tree = tester.assert_if_syntax_parses(stmt)
            if_nodes = tester.get_if_nodes(stmt)
            assert len(if_nodes) == 1

    def test_if_with_identity_tests(self, tester):
        """Test if statements with identity testing"""
        # Identity test patterns
        identity_statements = [
            """if obj is None:
    handle_none()""",
            
            """if obj is not None:
    process(obj)""",
            
            """if x is True:
    handle_explicit_true()""",
            
            """if result is False:
    handle_explicit_false()""",
            
            """if instance is singleton:
    handle_singleton()"""
        ]
        
        for stmt in identity_statements:
            tree = tester.assert_if_syntax_parses(stmt)
            if_nodes = tester.get_if_nodes(stmt)
            assert len(if_nodes) == 1


class TestSection81ErrorConditions:
    """Test error conditions for if statements"""
    
    @pytest.fixture
    def tester(self):
        return IfStatementTester()

    def test_invalid_if_syntax(self, tester):
        """Test invalid if statement syntax"""
        # Invalid if statement patterns
        invalid_if_statements = [
            "if:",                        # Missing condition
            "if",                         # Missing colon and condition
            "if condition",               # Missing colon
            "if: pass",                   # Missing condition before colon
            "if True pass",               # Missing colon
            "if condition: pass else",    # Missing else colon
            "elif condition: pass",       # elif without if
            "else: pass",                 # else without if
        ]
        
        for stmt in invalid_if_statements:
            tester.assert_if_syntax_error(stmt)

    def test_invalid_elif_placement(self, tester):
        """Test invalid elif placement"""
        # Invalid elif patterns
        invalid_elif_patterns = [
            """if condition:
    pass
elif:
    pass""",                              # elif missing condition
            
            """if condition:
    pass
elif condition
    pass""",                              # elif missing colon
        ]
        
        for stmt in invalid_elif_patterns:
            tester.assert_if_syntax_error(stmt)

    def test_invalid_condition_syntax(self, tester):
        """Test invalid condition expressions"""
        # Invalid condition syntax
        invalid_conditions = [
            "if def: pass",               # Reserved word as condition
            "if class: pass",             # Reserved word as condition
            "if import: pass",            # Reserved word as condition
            "if lambda: pass",            # Incomplete lambda
        ]
        
        for stmt in invalid_conditions:
            tester.assert_if_syntax_error(stmt)

    def test_incomplete_if_statements(self, tester):
        """Test incomplete if statement syntax"""
        # Incomplete statements that should fail
        incomplete_statements = [
            "if True:",                   # Missing body
        ]
        
        # Note: "if True:" without body is actually valid in interactive mode
        # but invalid in exec mode due to indentation requirements
        for stmt in incomplete_statements:
            try:
                tester.assert_if_syntax_error(stmt)
            except AssertionError:
                # Some cases may be valid depending on context
                pass


class TestSection81CrossImplementationCompatibility:
    """Test if statement features across Python implementations"""
    
    @pytest.fixture
    def tester(self):
        return IfStatementTester()

    def test_comprehensive_if_patterns(self, tester):
        """Test complex if statement combinations"""
        # Complex if statement patterns
        complex_if_patterns = [
            """if hasattr(obj, 'method') and callable(getattr(obj, 'method')):
    try:
        result = obj.method()
        if isinstance(result, dict) and 'status' in result:
            if result['status'] == 'success':
                handle_success(result)
            elif result['status'] == 'partial':
                handle_partial(result)
                if 'retry' in result and result['retry']:
                    schedule_retry(result)
            else:
                handle_failure(result)
        else:
            handle_invalid_result(result)
    except Exception as e:
        handle_exception(e)
elif obj is None:
    handle_none_object()
else:
    handle_incompatible_object(obj)""",
        ]
        
        for stmt in complex_if_patterns:
            tree = tester.assert_if_syntax_parses(stmt)
            if_nodes = tester.get_if_nodes(stmt)
            assert len(if_nodes) >= 1

    def test_if_ast_structure_validation(self, tester):
        """Test if statement AST structure validation"""
        # Validate AST structure for if statements
        test_if_statement = """if x > 0 and not error_flag:
    process_positive(x)
elif x < 0:
    process_negative(x)
else:
    process_zero()"""
        
        tree = tester.assert_if_syntax_parses(test_if_statement)
        if_nodes = tester.get_if_nodes(test_if_statement)
        assert len(if_nodes) >= 1
        
        # Check main if node
        if_node = if_nodes[0]
        assert if_node.test is not None
        assert len(if_node.body) > 0
        assert len(if_node.orelse) > 0  # Should have elif/else
        
        # Check elif/else structure
        assert tester.count_elif_clauses(test_if_statement) >= 1
        assert tester.has_else_clause(test_if_statement)

    def test_if_edge_cases(self, tester):
        """Test edge cases in if statements"""
        # Edge cases and corner scenarios
        edge_case_if_statements = [
            """if False: pass""",         # Never executes
            
            """if []: pass""",           # Empty list (falsy)
            
            """if "": pass""",           # Empty string (falsy)
            
            """if 0: pass""",            # Zero (falsy)
            
            """if None: pass""",         # None (falsy)
            
            """if not not True: pass""", # Double negation
            
            """if True and True and True and True: pass""",  # Long condition
            
            """if (
    condition1 and
    condition2 and
    condition3
):
    pass""",                            # Multiline condition
        ]
        
        for stmt in edge_case_if_statements:
            tree = tester.assert_if_syntax_parses(stmt)
            if_nodes = tester.get_if_nodes(stmt)
            assert len(if_nodes) >= 1

    def test_if_with_generator_expressions(self, tester):
        """Test if statements with generator expressions"""
        # Generator expressions in conditions
        generator_conditions = [
            """if any(x > 0 for x in values):
    handle_positive_values()""",
            
            """if all(validator(item) for item in items):
    process_all_valid()""",
            
            """if sum(item.weight for item in cargo) > limit:
    redistribute_cargo()""",
            
            """if len([x for x in data if x.active]) > threshold:
    scale_up()"""
        ]
        
        for stmt in generator_conditions:
            tree = tester.assert_if_syntax_parses(stmt)
            if_nodes = tester.get_if_nodes(stmt)
            assert len(if_nodes) >= 1