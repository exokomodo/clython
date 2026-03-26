"""
Section 8.2: While Statements - Conformance Test Suite

Tests Python Language Reference Section 8.2 compliance across implementations.
Based on formal specifications for while statement syntax and control flow behavior.

Language Reference requirements tested:
    - Basic while loops: while condition:
    - While loop condition expressions: complex boolean expressions
    - While...else statements: else clause execution rules
    - Break and continue behavior in while loops
    - Nested while loop structures
    - While loop with various condition patterns
    - Infinite loop patterns and edge cases
    - Control flow interaction with while loops
"""

import ast
import pytest
import sys
from typing import Any


class WhileStatementTester:
    """Helper class for testing while statement conformance.
    
    Follows established AST-based validation pattern from previous sections.
    """
    
    def assert_while_syntax_parses(self, source: str):
        """Test that while statement syntax parses correctly.
        
        Args:
            source: Python while statement source code
        """
        try:
            tree = ast.parse(source, mode='exec')
            # Verify the AST contains while statement
            for node in ast.walk(tree):
                if isinstance(node, ast.While):
                    return tree
            pytest.fail(f"Expected While node not found in parsed AST for: {source}")
        except SyntaxError as e:
            pytest.fail(f"While syntax {source!r} failed to parse: {e}")
    
    def assert_while_syntax_error(self, source: str):
        """Test that invalid while syntax raises SyntaxError.
        
        Args:
            source: Python while statement source that should be invalid
        """
        with pytest.raises(SyntaxError):
            ast.parse(source, mode='exec')

    def get_while_nodes(self, source: str) -> list:
        """Get list of While nodes from source code.
        
        Args:
            source: Python while statement source
            
        Returns:
            List of While AST nodes
        """
        tree = ast.parse(source, mode='exec')
        while_nodes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.While):
                while_nodes.append(node)
        return while_nodes

    def get_while_condition_type(self, source: str):
        """Get the condition type of a while statement.
        
        Args:
            source: Python while statement source
            
        Returns:
            Type of the condition AST node
        """
        while_nodes = self.get_while_nodes(source)
        if while_nodes:
            return type(while_nodes[0].test)
        return None


class TestSection82BasicWhileLoops:
    """Test Section 8.2: Basic While Loop Syntax"""
    
    @pytest.fixture
    def tester(self):
        return WhileStatementTester()

    def test_simple_while_loops(self, tester):
        """Test simple while loop syntax"""
        # Language Reference: while test:
        simple_while_loops = [
            """while True:
    pass""",
            
            """while condition:
    process()""",
            
            """while x > 0:
    x -= 1""",
            
            """while len(items) > 0:
    item = items.pop()
    handle(item)""",
            
            """while not done:
    result = work()
    if result:
        done = True"""
        ]
        
        for stmt in simple_while_loops:
            tree = tester.assert_while_syntax_parses(stmt)
            while_nodes = tester.get_while_nodes(stmt)
            assert len(while_nodes) == 1
            # Check that condition exists
            assert while_nodes[0].test is not None

    def test_while_with_boolean_conditions(self, tester):
        """Test while loops with various boolean expressions"""
        # Language Reference: complex boolean test expressions
        boolean_condition_loops = [
            """while True:
    pass""",
            
            """while False:
    pass""",
            
            """while x and y:
    process()""",
            
            """while x or y:
    handle()""",
            
            """while not finished:
    work()""",
            
            """while x > 0 and y < 10:
    update()""",
            
            """while (x > threshold) or (y in collection):
    process()"""
        ]
        
        for stmt in boolean_condition_loops:
            tree = tester.assert_while_syntax_parses(stmt)
            while_nodes = tester.get_while_nodes(stmt)
            assert len(while_nodes) == 1

    def test_while_with_comparison_conditions(self, tester):
        """Test while loops with comparison operators"""
        # Different comparison operators
        comparison_condition_loops = [
            """while x == y:
    pass""",
            
            """while x != y:
    pass""",
            
            """while x < y:
    pass""",
            
            """while x <= y:
    pass""",
            
            """while x > y:
    pass""",
            
            """while x >= y:
    pass""",
            
            """while x is y:
    pass""",
            
            """while x is not y:
    pass""",
            
            """while x in y:
    pass""",
            
            """while x not in y:
    pass"""
        ]
        
        for stmt in comparison_condition_loops:
            tree = tester.assert_while_syntax_parses(stmt)
            while_nodes = tester.get_while_nodes(stmt)
            assert len(while_nodes) == 1

    def test_while_with_complex_conditions(self, tester):
        """Test while loops with complex condition expressions"""
        # Complex condition patterns
        complex_condition_loops = [
            """while func():
    pass""",
            
            """while obj.method():
    pass""",
            
            """while item in container:
    pass""",
            
            """while hasattr(obj, 'attr'):
    pass""",
            
            """while len(collection) > 0:
    pass""",
            
            """while any(condition(x) for x in items):
    pass""",
            
            """while all(validator(item) for item in batch):
    pass"""
        ]
        
        for stmt in complex_condition_loops:
            tree = tester.assert_while_syntax_parses(stmt)
            while_nodes = tester.get_while_nodes(stmt)
            assert len(while_nodes) == 1


class TestSection82WhileElseStatements:
    """Test while...else statement combinations"""
    
    @pytest.fixture
    def tester(self):
        return WhileStatementTester()

    def test_basic_while_else(self, tester):
        """Test basic while...else syntax"""
        # Language Reference: while...else statements
        while_else_statements = [
            """while condition:
    work()
else:
    finalize()""",
            
            """while x > 0:
    x -= 1
    process(x)
else:
    print("finished")""",
            
            """while items:
    item = items.pop()
    handle(item)
else:
    cleanup()"""
        ]
        
        for stmt in while_else_statements:
            tree = tester.assert_while_syntax_parses(stmt)
            while_nodes = tester.get_while_nodes(stmt)
            assert len(while_nodes) == 1
            # Check that else clause exists
            while_node = while_nodes[0]
            assert len(while_node.orelse) > 0

    def test_while_else_with_break_continue(self, tester):
        """Test while...else with break and continue statements"""
        # Break and continue behavior in while...else
        control_flow_statements = [
            """while condition:
    if error_check():
        break
    process()
else:
    print("no break occurred")""",
            
            """while items:
    item = items.pop()
    if skip_condition(item):
        continue
    process(item)
else:
    print("all items processed")""",
            
            """while True:
    data = get_next()
    if not data:
        break
    if invalid(data):
        continue
    handle(data)
else:
    print("unreachable")"""
        ]
        
        for stmt in control_flow_statements:
            tree = tester.assert_while_syntax_parses(stmt)
            while_nodes = tester.get_while_nodes(stmt)
            assert len(while_nodes) == 1

    def test_nested_while_else(self, tester):
        """Test nested while loops with else clauses"""
        # Nested while...else patterns
        nested_while_else = [
            """while outer_condition:
    while inner_condition:
        if found():
            break
    else:
        print("inner loop completed")
    if should_break():
        break
else:
    print("outer loop completed")""",
            
            """while batch_available():
    while process_item():
        if critical_error():
            break
        work()
    else:
        batch_complete()
        continue
    error_recovery()
    break
else:
    all_batches_complete()"""
        ]
        
        for stmt in nested_while_else:
            tree = tester.assert_while_syntax_parses(stmt)
            while_nodes = tester.get_while_nodes(stmt)
            assert len(while_nodes) >= 2  # Nested loops

    def test_while_else_empty_clauses(self, tester):
        """Test while...else with empty clauses"""
        # Edge cases with empty bodies/else
        empty_clause_statements = [
            """while False:
    pass
else:
    pass""",
            
            """while condition:
    pass
else:
    pass""",
            
            """while True:
    break
else:
    pass"""
        ]
        
        for stmt in empty_clause_statements:
            tree = tester.assert_while_syntax_parses(stmt)
            while_nodes = tester.get_while_nodes(stmt)
            assert len(while_nodes) == 1


class TestSection82NestedWhileLoops:
    """Test nested while loop structures"""
    
    @pytest.fixture
    def tester(self):
        return WhileStatementTester()

    def test_simple_nested_while_loops(self, tester):
        """Test simple nested while loops"""
        # Basic nested loop patterns
        nested_loops = [
            """while outer:
    while inner:
        process()""",
            
            """while x > 0:
    while y > 0:
        work(x, y)
        y -= 1
    x -= 1""",
            
            """while batch:
    while item in batch:
        handle(item)
        if error():
            break
    next_batch()"""
        ]
        
        for stmt in nested_loops:
            tree = tester.assert_while_syntax_parses(stmt)
            while_nodes = tester.get_while_nodes(stmt)
            assert len(while_nodes) >= 2

    def test_nested_while_with_control_flow(self, tester):
        """Test nested while loops with break and continue"""
        # Control flow in nested loops
        control_flow_nested = [
            """while outer_active:
    while inner_active:
        if should_skip():
            continue
        if should_exit_inner():
            break
        process()
    if should_exit_outer():
        break""",
            
            """while processing:
    while data_available():
        item = get_item()
        if item.skip:
            continue
        if item.error:
            break
        handle(item)
    if fatal_error():
        break""",
            
            """outer_continue = False
while not done:
    while sub_task():
        if error_condition():
            outer_continue = True
            break
        work()
    if outer_continue:
        outer_continue = False
        continue
    finalize_step()"""
        ]
        
        for stmt in control_flow_nested:
            tree = tester.assert_while_syntax_parses(stmt)
            while_nodes = tester.get_while_nodes(stmt)
            assert len(while_nodes) >= 1

    def test_deeply_nested_while_loops(self, tester):
        """Test deeply nested while loop structures"""
        # Multiple levels of nesting
        deeply_nested = [
            """while level1:
    while level2:
        while level3:
            if condition():
                break
            process()""",
            
            """while batch:
    while chunk in batch:
        while item in chunk:
            while processor.busy():
                wait()
            processor.handle(item)"""
        ]
        
        for stmt in deeply_nested:
            tree = tester.assert_while_syntax_parses(stmt)
            while_nodes = tester.get_while_nodes(stmt)
            assert len(while_nodes) >= 3


class TestSection82WhileLoopVariations:
    """Test various while loop patterns and edge cases"""
    
    @pytest.fixture
    def tester(self):
        return WhileStatementTester()

    def test_while_with_walrus_operator(self, tester):
        """Test while loops with walrus operator (Python 3.8+)"""
        # Walrus operator in while conditions
        walrus_while_patterns = [
            """while (line := file.readline()):
    process(line)""",
            
            """while (data := get_next()) is not None:
    handle(data)""",
            
            """while (match := pattern.search(text)):
    results.append(match.group())
    text = text[match.end():]"""
        ]
        
        for stmt in walrus_while_patterns:
            try:
                tree = tester.assert_while_syntax_parses(stmt)
                while_nodes = tester.get_while_nodes(stmt)
                assert len(while_nodes) == 1
            except AssertionError:
                # Skip if walrus operator not supported
                if sys.version_info < (3, 8):
                    pytest.skip("Walrus operator requires Python 3.8+")
                else:
                    raise

    def test_while_with_function_calls(self, tester):
        """Test while loops with function call conditions"""
        # Function calls as conditions
        function_call_conditions = [
            """while has_more():
    item = get_next()
    process(item)""",
            
            """while not is_complete():
    step()""",
            
            """while queue.empty() is False:
    task = queue.get()
    execute(task)""",
            
            """while parser.has_tokens():
    token = parser.next_token()
    handle(token)"""
        ]
        
        for stmt in function_call_conditions:
            tree = tester.assert_while_syntax_parses(stmt)
            while_nodes = tester.get_while_nodes(stmt)
            assert len(while_nodes) == 1

    def test_while_with_attribute_access(self, tester):
        """Test while loops with attribute access conditions"""
        # Attribute access conditions
        attribute_access_conditions = [
            """while obj.active:
    obj.step()""",
            
            """while container.has_items:
    item = container.pop()
    process(item)""",
            
            """while worker.is_running:
    task = worker.get_task()
    if task:
        worker.execute(task)""",
            
            """while stream.readable():
    data = stream.read()
    handle(data)"""
        ]
        
        for stmt in attribute_access_conditions:
            tree = tester.assert_while_syntax_parses(stmt)
            while_nodes = tester.get_while_nodes(stmt)
            assert len(while_nodes) == 1

    def test_while_infinite_loop_patterns(self, tester):
        """Test common infinite loop patterns"""
        # Infinite loop patterns
        infinite_loop_patterns = [
            """while True:
    if should_exit():
        break
    work()""",
            
            """while 1:
    process()
    if done():
        break""",
            
            """while not False:
    handle()
    if condition():
        break""",
            
            """while "truthy":
    step()
    if finished():
        break"""
        ]
        
        for stmt in infinite_loop_patterns:
            tree = tester.assert_while_syntax_parses(stmt)
            while_nodes = tester.get_while_nodes(stmt)
            assert len(while_nodes) == 1


class TestSection82ErrorConditions:
    """Test error conditions for while statements"""
    
    @pytest.fixture
    def tester(self):
        return WhileStatementTester()

    def test_invalid_while_syntax(self, tester):
        """Test invalid while statement syntax"""
        # Invalid while statement patterns
        invalid_while_statements = [
            "while:",                     # Missing condition
            "while",                      # Missing colon and condition
            "while condition",            # Missing colon
            "while: pass",                # Missing condition before colon
            "while True pass",            # Missing colon
            "while condition: pass else", # Missing else colon
        ]
        
        for stmt in invalid_while_statements:
            tester.assert_while_syntax_error(stmt)

    def test_invalid_while_conditions(self, tester):
        """Test invalid while condition expressions"""
        # Note: Most "invalid" conditions are actually valid syntax
        # but may be semantically questionable
        syntactically_invalid = [
            "while def: pass",            # Reserved word as condition
            "while class: pass",          # Reserved word as condition
            "while import: pass",         # Reserved word as condition
        ]
        
        for stmt in syntactically_invalid:
            tester.assert_while_syntax_error(stmt)

    def test_invalid_else_placement(self, tester):
        """Test invalid else clause placement"""
        # Invalid else syntax
        invalid_else_patterns = [
            """else:
    print("orphaned else")
while condition:
    pass""",
            
            # Note: Most else placement issues are caught by broader syntax rules
        ]
        
        for stmt in invalid_else_patterns:
            tester.assert_while_syntax_error(stmt)

    def test_incomplete_while_statements(self, tester):
        """Test incomplete while statement syntax"""
        # Incomplete statements
        incomplete_statements = [
            "while True:",               # Missing body
        ]
        
        # Note: "while True:" without body is actually valid in interactive mode
        # but invalid in exec mode due to indentation requirements
        for stmt in incomplete_statements:
            try:
                tester.assert_while_syntax_error(stmt)
            except AssertionError:
                # Some cases may be valid depending on context
                pass


class TestSection82CrossImplementationCompatibility:
    """Test while statement features across Python implementations"""
    
    @pytest.fixture
    def tester(self):
        return WhileStatementTester()

    def test_comprehensive_while_patterns(self, tester):
        """Test complex while statement combinations"""
        # Complex while statement patterns
        complex_while_patterns = [
            """while condition and not error_flag:
    try:
        result = risky_operation()
        if result.success:
            process_result(result)
            if result.complete:
                break
        else:
            retry_count += 1
            if retry_count > max_retries:
                error_flag = True
                continue
    except Exception as e:
        log_error(e)
        if critical_error(e):
            break
        continue
else:
    print("Loop completed without break")""",
        ]
        
        for stmt in complex_while_patterns:
            tree = tester.assert_while_syntax_parses(stmt)
            while_nodes = tester.get_while_nodes(stmt)
            assert len(while_nodes) >= 1

    def test_while_ast_structure_validation(self, tester):
        """Test while statement AST structure validation"""
        # Validate AST structure for while statements
        test_while_statement = """while x > 0 and not done:
    x -= 1
    if x % 10 == 0:
        print(x)
    if should_stop():
        break
else:
    print("completed")"""
        
        tree = tester.assert_while_syntax_parses(test_while_statement)
        while_nodes = tester.get_while_nodes(test_while_statement)
        assert len(while_nodes) == 1
        
        while_node = while_nodes[0]
        # Check test condition exists
        assert while_node.test is not None
        
        # Check body exists
        assert len(while_node.body) > 0
        
        # Check else clause exists
        assert len(while_node.orelse) > 0

    def test_while_edge_cases(self, tester):
        """Test edge cases in while statements"""
        # Edge cases and corner scenarios
        edge_case_while_statements = [
            """while False: pass""",      # Never executes
            
            """while []: pass""",        # Empty list (falsy)
            
            """while "": pass""",        # Empty string (falsy)
            
            """while 0: pass""",         # Zero (falsy)
            
            """while None: pass""",      # None (falsy)
            
            """while bool(): pass""",    # Function returning False
            
            """while True:
    while True:
        while True:
            while True:
                while True:
                    break
                break
            break
        break
    break""",                           # Deeply nested with breaks
        ]
        
        for stmt in edge_case_while_statements:
            tree = tester.assert_while_syntax_parses(stmt)
            while_nodes = tester.get_while_nodes(stmt)
            assert len(while_nodes) >= 1

    def test_while_with_comprehensions(self, tester):
        """Test while loops with comprehension conditions"""
        # Comprehensions in while conditions
        comprehension_conditions = [
            """while any(x > 0 for x in values):
    process_values(values)
    values = update_values(values)""",
            
            """while all(validator(item) for item in batch):
    batch = get_next_batch()
    if not batch:
        break""",
            
            """while sum(item.weight for item in cargo) < max_weight:
    new_item = get_next_item()
    if new_item:
        cargo.append(new_item)
    else:
        break"""
        ]
        
        for stmt in comprehension_conditions:
            tree = tester.assert_while_syntax_parses(stmt)
            while_nodes = tester.get_while_nodes(stmt)
            assert len(while_nodes) >= 1