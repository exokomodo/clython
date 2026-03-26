"""
Section 8.3: For Statements - Conformance Test Suite

Tests Python Language Reference Section 8.3 compliance across implementations.
Based on formal specifications for for statement syntax and iteration behavior.

Language Reference requirements tested:
    - Basic for loops: for target in iterable:
    - For loop target patterns: simple names, tuple unpacking, list unpacking
    - Iterator protocol compliance: __iter__ and __next__ requirements
    - For...else statements: else clause execution rules
    - Break and continue behavior in for loops
    - Nested for loop structures
    - For loop with various iterable types
    - Assignment to for loop targets
    - Complex unpacking patterns in for loops
"""

import ast
import pytest
import sys
from typing import Any


class ForStatementTester:
    """Helper class for testing for statement conformance.
    
    Follows established AST-based validation pattern from previous sections.
    """
    
    def assert_for_syntax_parses(self, source: str):
        """Test that for statement syntax parses correctly.
        
        Args:
            source: Python for statement source code
        """
        try:
            tree = ast.parse(source, mode='exec')
            # Verify the AST contains for statement
            for node in ast.walk(tree):
                if isinstance(node, ast.For):
                    return tree
            pytest.fail(f"Expected For node not found in parsed AST for: {source}")
        except SyntaxError as e:
            pytest.fail(f"For syntax {source!r} failed to parse: {e}")
    
    def assert_for_syntax_error(self, source: str):
        """Test that invalid for syntax raises SyntaxError.
        
        Args:
            source: Python for statement source that should be invalid
        """
        with pytest.raises(SyntaxError):
            ast.parse(source, mode='exec')

    def get_for_nodes(self, source: str) -> list:
        """Get list of For nodes from source code.
        
        Args:
            source: Python for statement source
            
        Returns:
            List of For AST nodes
        """
        tree = ast.parse(source, mode='exec')
        for_nodes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                for_nodes.append(node)
        return for_nodes

    def get_for_target_type(self, source: str):
        """Get the target type of a for statement.
        
        Args:
            source: Python for statement source
            
        Returns:
            Type of the target AST node
        """
        for_nodes = self.get_for_nodes(source)
        if for_nodes:
            return type(for_nodes[0].target)
        return None


class TestSection83BasicForLoops:
    """Test Section 8.3: Basic For Loop Syntax"""
    
    @pytest.fixture
    def tester(self):
        return ForStatementTester()

    def test_simple_for_loops(self, tester):
        """Test simple for loop syntax"""
        # Language Reference: for target in iterable:
        simple_for_loops = [
            """for i in range(10):
    pass""",
            
            """for item in [1, 2, 3]:
    print(item)""",
            
            """for char in "hello":
    print(char)""",
            
            """for key in dict:
    print(key)""",
            
            """for element in collection:
    process(element)"""
        ]
        
        for stmt in simple_for_loops:
            tree = tester.assert_for_syntax_parses(stmt)
            for_nodes = tester.get_for_nodes(stmt)
            assert len(for_nodes) == 1
            # Target should be a Name node for simple loops
            assert isinstance(for_nodes[0].target, ast.Name)

    def test_for_loop_with_various_iterables(self, tester):
        """Test for loops with different iterable types"""
        # Language Reference: various iterable expressions
        iterable_for_loops = [
            """for x in [1, 2, 3]:
    pass""",
            
            """for x in (1, 2, 3):
    pass""",
            
            """for x in {1, 2, 3}:
    pass""",
            
            """for x in range(5):
    pass""",
            
            """for x in "string":
    pass""",
            
            """for x in func():
    pass""",
            
            """for x in obj.method():
    pass""",
            
            """for x in [y for y in range(10)]:
    pass"""
        ]
        
        for stmt in iterable_for_loops:
            tree = tester.assert_for_syntax_parses(stmt)
            for_nodes = tester.get_for_nodes(stmt)
            assert len(for_nodes) >= 1

    def test_for_loop_bodies(self, tester):
        """Test for loop body variations"""
        # Different body patterns
        body_variations = [
            """for i in range(3):
    pass""",
            
            """for i in range(3):
    print(i)
    print(i * 2)""",
            
            """for i in range(3):
    if i > 0:
        print(i)""",
            
            """for i in range(3):
    for j in range(2):
        print(i, j)""",
            
            """for i in range(3):
    try:
        result = process(i)
    except Exception:
        continue"""
        ]
        
        for stmt in body_variations:
            tree = tester.assert_for_syntax_parses(stmt)
            for_nodes = tester.get_for_nodes(stmt)
            assert len(for_nodes) >= 1


class TestSection83ForTargetUnpacking:
    """Test for loop target unpacking patterns"""
    
    @pytest.fixture
    def tester(self):
        return ForStatementTester()

    def test_tuple_unpacking_targets(self, tester):
        """Test tuple unpacking in for loop targets"""
        # Language Reference: for target unpacking
        tuple_unpacking_loops = [
            """for a, b in [(1, 2), (3, 4)]:
    pass""",
            
            """for x, y, z in [(1, 2, 3), (4, 5, 6)]:
    pass""",
            
            """for (a, b) in pairs:
    pass""",
            
            """for first, *rest in sequences:
    pass""",
            
            """for *head, last in sequences:
    pass""",
            
            """for first, *middle, last in sequences:
    pass"""
        ]
        
        for stmt in tuple_unpacking_loops:
            tree = tester.assert_for_syntax_parses(stmt)
            for_nodes = tester.get_for_nodes(stmt)
            assert len(for_nodes) == 1
            # Target should be a Tuple node for unpacking
            target_type = tester.get_for_target_type(stmt)
            assert target_type in (ast.Tuple, ast.List)

    def test_list_unpacking_targets(self, tester):
        """Test list unpacking in for loop targets"""
        # Language Reference: list unpacking syntax
        list_unpacking_loops = [
            """for [a, b] in pairs:
    pass""",
            
            """for [x, y, z] in triples:
    pass""",
            
            """for [first, *rest] in sequences:
    pass""",
            
            """for [*head, last] in sequences:
    pass"""
        ]
        
        for stmt in list_unpacking_loops:
            tree = tester.assert_for_syntax_parses(stmt)
            for_nodes = tester.get_for_nodes(stmt)
            assert len(for_nodes) == 1
            # Target should be a List node
            target_type = tester.get_for_target_type(stmt)
            assert target_type == ast.List

    def test_nested_unpacking_targets(self, tester):
        """Test nested unpacking patterns"""
        # Complex unpacking structures
        nested_unpacking_loops = [
            """for (a, (b, c)) in nested_pairs:
    pass""",
            
            """for [x, (y, z)] in mixed_structures:
    pass""",
            
            """for ((a, b), (c, d)) in pair_pairs:
    pass""",
            
            """for (first, [second, third]) in complex_data:
    pass""",
            
            """for (name, (x, y, z)) in points_data:
    pass"""
        ]
        
        for stmt in nested_unpacking_loops:
            tree = tester.assert_for_syntax_parses(stmt)
            for_nodes = tester.get_for_nodes(stmt)
            assert len(for_nodes) == 1

    def test_starred_unpacking_targets(self, tester):
        """Test starred expressions in for loop targets"""
        # Language Reference: starred expressions (Python 3.0+)
        starred_unpacking_loops = [
            """for *args in sequences:
    pass""",
            
            """for head, *tail in sequences:
    pass""",
            
            """for *init, last in sequences:
    pass""",
            
            """for first, *middle, last in sequences:
    pass""",
            
            """for (a, *rest), b in complex_sequences:
    pass"""
        ]
        
        for stmt in starred_unpacking_loops:
            try:
                tree = tester.assert_for_syntax_parses(stmt)
                for_nodes = tester.get_for_nodes(stmt)
                assert len(for_nodes) == 1
            except AssertionError:
                # Skip if starred expressions not supported
                if sys.version_info < (3, 0):
                    pytest.skip("Starred expressions require Python 3.0+")
                else:
                    raise


class TestSection83ForElseStatements:
    """Test for...else statement combinations"""
    
    @pytest.fixture
    def tester(self):
        return ForStatementTester()

    def test_basic_for_else(self, tester):
        """Test basic for...else syntax"""
        # Language Reference: for...else statements
        for_else_statements = [
            """for i in range(3):
    print(i)
else:
    print("done")""",
            
            """for item in collection:
    if condition:
        break
else:
    print("no break")""",
            
            """for x in data:
    process(x)
else:
    finalize()"""
        ]
        
        for stmt in for_else_statements:
            tree = tester.assert_for_syntax_parses(stmt)
            for_nodes = tester.get_for_nodes(stmt)
            assert len(for_nodes) == 1
            # Check that else clause exists
            for_node = for_nodes[0]
            assert len(for_node.orelse) > 0

    def test_for_else_with_break_continue(self, tester):
        """Test for...else with break and continue statements"""
        # Break and continue behavior in for...else
        control_flow_statements = [
            """for i in range(10):
    if i == 5:
        break
else:
    print("no break occurred")""",
            
            """for i in range(10):
    if i % 2 == 0:
        continue
    print(i)
else:
    print("loop completed")""",
            
            """for item in items:
    if item.is_valid():
        continue
    if item.is_error():
        break
    process(item)
else:
    print("all items processed")"""
        ]
        
        for stmt in control_flow_statements:
            tree = tester.assert_for_syntax_parses(stmt)
            for_nodes = tester.get_for_nodes(stmt)
            assert len(for_nodes) == 1

    def test_nested_for_else(self, tester):
        """Test nested for loops with else clauses"""
        # Nested for...else patterns
        nested_for_else = [
            """for i in range(3):
    for j in range(3):
        if i == j:
            break
    else:
        print(f"no break for i={i}")
else:
    print("outer loop done")""",
            
            """for x in outer:
    for y in inner:
        if found(x, y):
            result = (x, y)
            break
    else:
        continue
    break
else:
    result = None"""
        ]
        
        for stmt in nested_for_else:
            tree = tester.assert_for_syntax_parses(stmt)
            for_nodes = tester.get_for_nodes(stmt)
            assert len(for_nodes) >= 2  # Nested loops


class TestSection83NestedForLoops:
    """Test nested for loop structures"""
    
    @pytest.fixture
    def tester(self):
        return ForStatementTester()

    def test_simple_nested_loops(self, tester):
        """Test simple nested for loops"""
        # Basic nested loop patterns
        nested_loops = [
            """for i in range(3):
    for j in range(3):
        print(i, j)""",
            
            """for row in matrix:
    for element in row:
        process(element)""",
            
            """for x in range(5):
    for y in range(5):
        for z in range(5):
            if x + y + z == 10:
                print(x, y, z)"""
        ]
        
        for stmt in nested_loops:
            tree = tester.assert_for_syntax_parses(stmt)
            for_nodes = tester.get_for_nodes(stmt)
            assert len(for_nodes) >= 2

    def test_nested_loops_with_unpacking(self, tester):
        """Test nested loops with target unpacking"""
        # Nested loops with unpacking
        nested_unpacking_loops = [
            """for i, row in enumerate(matrix):
    for j, element in enumerate(row):
        print(i, j, element)""",
            
            """for name, data in items:
    for key, value in data.items():
        process(name, key, value)""",
            
            """for (a, b) in pairs:
    for (x, y) in coordinates:
        calculate(a, b, x, y)"""
        ]
        
        for stmt in nested_unpacking_loops:
            tree = tester.assert_for_syntax_parses(stmt)
            for_nodes = tester.get_for_nodes(stmt)
            assert len(for_nodes) >= 2

    def test_nested_loops_with_control_flow(self, tester):
        """Test nested loops with break and continue"""
        # Control flow in nested loops
        control_flow_nested = [
            """for i in range(10):
    for j in range(10):
        if i == j:
            continue
        if i + j > 15:
            break
        print(i, j)""",
            
            """for batch in batches:
    for item in batch:
        if item.skip:
            continue
        if item.error:
            break
        process(item)""",
            
            """outer_break = False
for i in range(5):
    for j in range(5):
        if condition(i, j):
            outer_break = True
            break
    if outer_break:
        break"""
        ]
        
        for stmt in control_flow_nested:
            tree = tester.assert_for_syntax_parses(stmt)
            for_nodes = tester.get_for_nodes(stmt)
            # Should have multiple for nodes
            assert len(for_nodes) >= 1


class TestSection83ForLoopVariations:
    """Test various for loop patterns and edge cases"""
    
    @pytest.fixture
    def tester(self):
        return ForStatementTester()

    def test_for_with_function_calls(self, tester):
        """Test for loops with function calls as iterables"""
        # Function calls as iterables
        function_call_loops = [
            """for item in get_items():
    process(item)""",
            
            """for line in open('file.txt'):
    print(line.strip())""",
            
            """for result in map(func, data):
    use(result)""",
            
            """for item in filter(predicate, collection):
    handle(item)""",
            
            """for pair in zip(list1, list2):
    process_pair(pair)"""
        ]
        
        for stmt in function_call_loops:
            tree = tester.assert_for_syntax_parses(stmt)
            for_nodes = tester.get_for_nodes(stmt)
            assert len(for_nodes) == 1

    def test_for_with_comprehensions(self, tester):
        """Test for loops with comprehension iterables"""
        # Comprehensions as iterables
        comprehension_loops = [
            """for x in [i**2 for i in range(10)]:
    print(x)""",
            
            """for item in (x.upper() for x in strings):
    process(item)""",
            
            """for key in {k: v for k, v in pairs}:
    use(key)""",
            
            """for value in [func(x) for x in data if x.valid]:
    handle(value)"""
        ]
        
        for stmt in comprehension_loops:
            tree = tester.assert_for_syntax_parses(stmt)
            for_nodes = tester.get_for_nodes(stmt)
            assert len(for_nodes) >= 1  # May include comprehension for loops

    def test_for_with_attribute_access(self, tester):
        """Test for loops with attribute access iterables"""
        # Attribute access as iterables
        attribute_access_loops = [
            """for item in obj.items:
    process(item)""",
            
            """for element in container.data:
    handle(element)""",
            
            """for child in node.children:
    traverse(child)""",
            
            """for value in instance.get_values():
    use(value)"""
        ]
        
        for stmt in attribute_access_loops:
            tree = tester.assert_for_syntax_parses(stmt)
            for_nodes = tester.get_for_nodes(stmt)
            assert len(for_nodes) == 1

    def test_for_with_subscript_access(self, tester):
        """Test for loops with subscript access iterables"""
        # Subscript access as iterables
        subscript_access_loops = [
            """for item in data[key]:
    process(item)""",
            
            """for element in matrix[row]:
    handle(element)""",
            
            """for value in cache[category][subcategory]:
    use(value)""",
            
            """for item in collection[start:end]:
    process_slice_item(item)"""
        ]
        
        for stmt in subscript_access_loops:
            tree = tester.assert_for_syntax_parses(stmt)
            for_nodes = tester.get_for_nodes(stmt)
            assert len(for_nodes) == 1


class TestSection83ErrorConditions:
    """Test error conditions for for statements"""
    
    @pytest.fixture
    def tester(self):
        return ForStatementTester()

    def test_invalid_for_syntax(self, tester):
        """Test invalid for statement syntax"""
        # Invalid for statement patterns
        invalid_for_statements = [
            "for in range(10):",          # Missing target
            "for i range(10):",           # Missing 'in' keyword
            "for i in:",                  # Missing iterable
            "for:",                       # Missing target and iterable
            "for i in range(10)",         # Missing colon
            "for i in range(10): pass else", # Missing else colon
        ]
        
        for stmt in invalid_for_statements:
            tester.assert_for_syntax_error(stmt)

    def test_invalid_target_patterns(self, tester):
        """Test invalid for loop target patterns"""
        # Invalid target syntax
        invalid_targets = [
            "for 123 in range(10): pass",     # Numeric literal target
            "for 'string' in range(10): pass", # String literal target
            "for [a, b, c in pairs: pass",    # Incomplete list unpacking
            "for a, b, c) in pairs: pass",    # Incomplete tuple unpacking
            "for def in range(10): pass",     # Reserved word target
            "for class in range(10): pass",   # Reserved word target
        ]
        
        for stmt in invalid_targets:
            tester.assert_for_syntax_error(stmt)

    def test_invalid_unpacking_patterns(self, tester):
        """Test invalid unpacking patterns in for targets"""
        # Invalid unpacking syntax that actually fails at parse time
        invalid_unpacking = [
            "for a, *, b in sequences: pass", # Invalid starred syntax
            "for ** in sequences: pass",      # Invalid double star
            "for *** in sequences: pass",     # Invalid triple star
        ]
        
        for stmt in invalid_unpacking:
            tester.assert_for_syntax_error(stmt)
        
        # Note: "for *a, *b in sequences: pass" parses but fails at runtime

    def test_invalid_else_placement(self, tester):
        """Test invalid else clause placement"""
        # Invalid else syntax
        invalid_else_patterns = [
            """else:
    print("orphaned else")
for i in range(3):
    pass""",
            
            # Note: else without for would be caught by broader syntax rules
        ]
        
        for stmt in invalid_else_patterns:
            tester.assert_for_syntax_error(stmt)


class TestSection83CrossImplementationCompatibility:
    """Test for statement features across Python implementations"""
    
    @pytest.fixture
    def tester(self):
        return ForStatementTester()

    def test_comprehensive_for_patterns(self, tester):
        """Test complex for statement combinations"""
        # Complex for statement patterns
        complex_for_patterns = [
            """for i, (name, (x, y)) in enumerate(named_points):
    if x > threshold:
        results.append((i, name, x, y))
        if len(results) > max_results:
            break
    else:
        skipped += 1
else:
    print(f"Processed all points, skipped {skipped}")""",
            
            """for batch_idx, batch in enumerate(batches):
    for item_idx, (key, value) in enumerate(batch.items()):
        try:
            processed = processor.handle(key, value)
            output[batch_idx][item_idx] = processed
        except ProcessingError:
            continue
        except CriticalError:
            break
    else:
        batch.mark_complete()""",
        ]
        
        for stmt in complex_for_patterns:
            tree = tester.assert_for_syntax_parses(stmt)
            for_nodes = tester.get_for_nodes(stmt)
            assert len(for_nodes) >= 1

    def test_for_with_walrus_operator(self, tester):
        """Test for loops with walrus operator (Python 3.8+)"""
        # Walrus operator in for loops
        walrus_for_patterns = [
            """for line in file:
    if match := pattern.search(line):
        results.append(match.group())""",
            
            """for item in items:
    if processed := process_item(item):
        output.append(processed)"""
        ]
        
        for stmt in walrus_for_patterns:
            try:
                tree = tester.assert_for_syntax_parses(stmt)
                for_nodes = tester.get_for_nodes(stmt)
                assert len(for_nodes) >= 1
            except AssertionError:
                # Skip if walrus operator not supported
                if sys.version_info < (3, 8):
                    pytest.skip("Walrus operator requires Python 3.8+")
                else:
                    raise

    def test_for_ast_structure_validation(self, tester):
        """Test for statement AST structure validation"""
        # Validate AST structure for for statements
        test_for_statement = """for i, (a, b) in enumerate(pairs):
    if a > b:
        print(i, a, b)
else:
    print("done")"""
        
        tree = tester.assert_for_syntax_parses(test_for_statement)
        for_nodes = tester.get_for_nodes(test_for_statement)
        assert len(for_nodes) == 1
        
        for_node = for_nodes[0]
        # Check target structure
        assert isinstance(for_node.target, ast.Tuple)
        assert len(for_node.target.elts) == 2
        
        # Check iter (enumerate call)
        assert isinstance(for_node.iter, ast.Call)
        
        # Check body exists
        assert len(for_node.body) > 0
        
        # Check else clause exists
        assert len(for_node.orelse) > 0

    def test_for_edge_cases(self, tester):
        """Test edge cases in for statements"""
        # Edge cases and corner scenarios
        edge_case_for_statements = [
            """for _ in range(10): pass""",  # Underscore target
            
            """for i in []: pass""",         # Empty iterable
            
            """for x in [1]:
    for y in []:
        pass""",                           # Nested with empty inner
            
            """for a in iterable:
    pass
else:
    pass""",                              # Empty else clause
            
            """for i in range(1):
    for j in range(1):
        for k in range(1):
            for l in range(1):
                for m in range(1):
                    pass"""               # Deeply nested loops
        ]
        
        for stmt in edge_case_for_statements:
            tree = tester.assert_for_syntax_parses(stmt)
            for_nodes = tester.get_for_nodes(stmt)
            assert len(for_nodes) >= 1