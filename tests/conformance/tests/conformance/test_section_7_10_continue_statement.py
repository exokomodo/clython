"""
Section 7.10: Continue Statement - Conformance Test Suite

Tests Python Language Reference Section 7.10 compliance across implementations.
Based on formal continue statement syntax definitions and prose assertions for loop continuation behavior.

Grammar tested:
    continue_stmt: 'continue'

Language Reference requirements tested:
    - Continue statement syntax validation
    - Loop continuation semantics and behavior
    - Continue statement placement within loop contexts
    - Nested loop continue behavior and scope
    - Syntactic context requirements for continue
    - Error conditions for invalid continue usage
    - Continue statement AST structure validation
    - Cross-implementation continue compatibility
"""

import ast
import pytest
import sys
from typing import Any


class ContinueTester:
    """Helper class for testing continue statement conformance.
    
    Focuses on AST structure validation for continue syntax and loop
    control flow patterns that can be statically analyzed for cross-implementation compatibility.
    """
    
    def assert_continue_syntax_parses(self, source: str):
        """Test that continue statement syntax parses correctly.
        
        Args:
            source: Python source code with continue statements
        """
        try:
            tree = ast.parse(source)
            return tree
        except SyntaxError as e:
            pytest.fail(f"Continue syntax should be valid but failed to parse: {source}\\nError: {e}")
    
    def assert_continue_syntax_error(self, source: str):
        """Test that invalid continue syntax raises SyntaxError.
        
        Args:
            source: Python source code that should be invalid
        """
        with pytest.raises(SyntaxError):
            ast.parse(source)
    
    def get_continue_statements(self, source: str) -> list:
        """Get Continue AST nodes from source.
        
        Args:
            source: Python source code
            
        Returns:
            List of ast.Continue nodes
        """
        tree = ast.parse(source)
        continues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Continue):
                continues.append(node)
        
        return continues
    
    def has_loop_statements(self, source: str) -> bool:
        """Check if source contains loop statements.
        
        Args:
            source: Python source code
            
        Returns:
            True if contains for or while loops
        """
        tree = ast.parse(source)
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                return True
        
        return False
    
    def get_loop_depth(self, source: str) -> int:
        """Get maximum loop nesting depth.
        
        Args:
            source: Python source code
            
        Returns:
            Maximum depth of nested loops
        """
        tree = ast.parse(source)
        
        def count_depth(node, current_depth=0):
            max_depth = current_depth
            
            if isinstance(node, (ast.For, ast.While)):
                current_depth += 1
                max_depth = current_depth
            
            for child in ast.iter_child_nodes(node):
                child_depth = count_depth(child, current_depth)
                max_depth = max(max_depth, child_depth)
            
            return max_depth
        
        return count_depth(tree)
    
    def get_conditional_statements(self, source: str) -> list:
        """Get If AST nodes from source.
        
        Args:
            source: Python source code
            
        Returns:
            List of ast.If nodes
        """
        tree = ast.parse(source)
        conditionals = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                conditionals.append(node)
        
        return conditionals


@pytest.fixture
def tester():
    """Provide ContinueTester instance for tests."""
    return ContinueTester()


class TestSection710BasicContinueSyntax:
    """Test basic continue statement syntax."""
    
    def test_simple_continue_in_for_loop(self, tester):
        """Test simple continue statement in for loops"""
        # Language Reference: continue_stmt: 'continue'
        simple_for_continue_patterns = [
            """
for i in range(10):
    if i % 2 == 0:
        continue
    print(i)
""",
            """
for item in [1, 2, 3, 4, 5]:
    if item == 3:
        continue
    result = item * 2
""",
            """
for x in "hello":
    if x == 'l':
        continue
    process(x)
""",
            """
for index, value in enumerate([1, 2, 3]):
    if index == 1:
        continue
    use_value(value)
"""
        ]
        
        for source in simple_for_continue_patterns:
            tree = tester.assert_continue_syntax_parses(source)
            continue_nodes = tester.get_continue_statements(source)
            assert len(continue_nodes) == 1, f"Should have one continue statement: {source}"
            assert tester.has_loop_statements(source), f"Should have loop statements: {source}"
    
    def test_simple_continue_in_while_loop(self, tester):
        """Test simple continue statement in while loops"""
        # Language Reference: continue works in while loops
        simple_while_continue_patterns = [
            """
i = 0
while i < 10:
    i += 1
    if i % 2 == 0:
        continue
    print(i)
""",
            """
counter = 0
while counter < 5:
    counter += 1
    if counter == 3:
        continue
    process(counter)
""",
            """
found = False
attempts = 0
while not found and attempts < 10:
    attempts += 1
    if not check_condition():
        continue
    found = True
""",
            """
items = [1, 2, 3, 4, 5]
index = 0
while index < len(items):
    item = items[index]
    index += 1
    if item < 3:
        continue
    handle_item(item)
"""
        ]
        
        for source in simple_while_continue_patterns:
            tree = tester.assert_continue_syntax_parses(source)
            continue_nodes = tester.get_continue_statements(source)
            assert len(continue_nodes) == 1, f"Should have one continue statement: {source}"
            assert tester.has_loop_statements(source), f"Should have loop statements: {source}"
    
    def test_multiple_continue_statements(self, tester):
        """Test multiple continue statements in same loop"""
        # Language Reference: multiple continues allowed in same loop
        multiple_continue_patterns = [
            """
for i in range(20):
    if i < 5:
        continue
    if i > 15:
        continue
    if i % 2 == 0:
        continue
    print(i)
""",
            """
for item in data:
    if item is None:
        continue
    if not validate(item):
        continue
    process(item)
""",
            """
while condition:
    value = get_next_value()
    if value < 0:
        continue
    if value > 100:
        continue
    handle_value(value)
""",
            """
for line in file_lines:
    if line.startswith('#'):
        continue  # Skip comments
    if not line.strip():
        continue  # Skip empty lines
    process_line(line)
"""
        ]
        
        for source in multiple_continue_patterns:
            tree = tester.assert_continue_syntax_parses(source)
            continue_nodes = tester.get_continue_statements(source)
            assert len(continue_nodes) >= 2, f"Should have multiple continue statements: {source}"
    
    def test_continue_in_conditional_blocks(self, tester):
        """Test continue statements within conditional blocks"""
        # Language Reference: continue can appear in if/elif/else within loops
        conditional_continue_patterns = [
            """
for i in range(10):
    if i % 2 == 0:
        continue
    else:
        print(i)
""",
            """
for item in items:
    if condition1(item):
        handle_condition1(item)
        continue
    elif condition2(item):
        continue
    else:
        handle_default(item)
""",
            """
while running:
    event = get_event()
    if event.type == 'quit':
        break
    elif event.type == 'skip':
        continue
    elif not event.is_valid():
        continue
    else:
        process_event(event)
""",
            """
for x in range(100):
    if x < 10:
        if x % 2 == 0:
            continue
        print(f"Odd single digit: {x}")
    elif x < 50:
        continue
    else:
        print(f"Large number: {x}")
"""
        ]
        
        for source in conditional_continue_patterns:
            tree = tester.assert_continue_syntax_parses(source)
            continue_nodes = tester.get_continue_statements(source)
            assert len(continue_nodes) >= 1, f"Should have continue statements: {source}"
            
            conditional_nodes = tester.get_conditional_statements(source)
            assert len(conditional_nodes) >= 1, f"Should have conditional statements: {source}"


class TestSection710NestedLoopContinue:
    """Test continue behavior in nested loops."""
    
    def test_continue_in_nested_for_loops(self, tester):
        """Test continue in nested for loops"""
        # Language Reference: continue affects innermost loop only
        nested_for_continue_patterns = [
            """
for i in range(3):
    for j in range(3):
        if j == 1:
            continue  # Continues inner loop only
        print(i, j)
""",
            """
for outer in range(5):
    for inner in range(5):
        if inner % 2 == 0:
            continue
        if outer == inner:
            continue
        process(outer, inner)
""",
            """
for row in matrix:
    for col_index, value in enumerate(row):
        if value < 0:
            continue
        if col_index % 2 == 0:
            continue
        handle_value(value)
""",
            """
for category in categories:
    for item in category.items:
        if not item.is_valid:
            continue
        for attribute in item.attributes:
            if attribute.is_private:
                continue
            use_attribute(attribute)
"""
        ]
        
        for source in nested_for_continue_patterns:
            tree = tester.assert_continue_syntax_parses(source)
            continue_nodes = tester.get_continue_statements(source)
            assert len(continue_nodes) >= 1, f"Should have continue statements: {source}"
            
            loop_depth = tester.get_loop_depth(source)
            assert loop_depth >= 2, f"Should have nested loops: {source}"
    
    def test_continue_in_nested_while_loops(self, tester):
        """Test continue in nested while loops"""
        # Language Reference: continue affects innermost loop
        nested_while_continue_patterns = [
            """
i = 0
while i < 3:
    j = 0
    while j < 3:
        j += 1
        if j == 2:
            continue
        print(i, j)
    i += 1
""",
            """
outer_condition = True
while outer_condition:
    inner_condition = True
    while inner_condition:
        data = get_data()
        if not data:
            continue
        if process_data(data):
            inner_condition = False
        else:
            continue
    outer_condition = check_outer()
""",
            """
reader = DataReader()
while reader.has_data():
    chunk = reader.read_chunk()
    processor = ChunkProcessor(chunk)
    while processor.has_items():
        item = processor.next_item()
        if not validate_item(item):
            continue
        handle_item(item)
"""
        ]
        
        for source in nested_while_continue_patterns:
            tree = tester.assert_continue_syntax_parses(source)
            continue_nodes = tester.get_continue_statements(source)
            assert len(continue_nodes) >= 1, f"Should have continue statements: {source}"
            
            loop_depth = tester.get_loop_depth(source)
            assert loop_depth >= 2, f"Should have nested loops: {source}"
    
    def test_continue_in_mixed_nested_loops(self, tester):
        """Test continue in mixed for/while nested loops"""
        # Language Reference: continue works in mixed loop types
        mixed_nested_continue_patterns = [
            """
for i in range(10):
    j = 0
    while j < 10:
        j += 1
        if (i + j) % 3 == 0:
            continue
        print(i, j)
""",
            """
while condition:
    for item in get_items():
        if not process_item(item):
            continue
        if item.requires_special_handling:
            continue
        finalize_item(item)
    update_condition()
""",
            """
for batch in data_batches:
    index = 0
    while index < len(batch):
        item = batch[index]
        index += 1
        if item in skip_set:
            continue
        for processor in processors:
            if not processor.can_handle(item):
                continue
            processor.process(item)
            break
"""
        ]
        
        for source in mixed_nested_continue_patterns:
            tree = tester.assert_continue_syntax_parses(source)
            continue_nodes = tester.get_continue_statements(source)
            assert len(continue_nodes) >= 1, f"Should have continue statements: {source}"
    
    def test_continue_with_loop_else_clauses(self, tester):
        """Test continue interaction with loop else clauses"""
        # Language Reference: continue doesn't affect else clause execution
        loop_else_continue_patterns = [
            """
for i in range(10):
    if i % 2 == 0:
        continue
    print(i)
else:
    print("Loop completed normally")
""",
            """
while condition:
    value = get_value()
    if not validate(value):
        continue
    process(value)
    if should_break(value):
        break
else:
    print("While loop completed without break")
""",
            """
for item in items:
    for sub_item in item:
        if sub_item in skip_list:
            continue
        if handle_sub_item(sub_item):
            break
    else:
        finalize_item(item)
        continue
    handle_break_case(item)
"""
        ]
        
        for source in loop_else_continue_patterns:
            tree = tester.assert_continue_syntax_parses(source)
            continue_nodes = tester.get_continue_statements(source)
            assert len(continue_nodes) >= 1, f"Should have continue statements: {source}"


class TestSection710ContinueErrorConditions:
    """Test continue statement error conditions."""
    
    def test_continue_outside_loop_error(self, tester):
        """Test continue outside loop context"""
        # Language Reference: continue only valid inside loops
        # Note: Some continue restrictions are checked at compile time, not parse time
        outside_loop_patterns = [
            "continue",  # Module level - parses but may fail at compile/runtime
            """
def function():
    continue  # Function level - parses but may fail at compile/runtime
""",
        ]
        
        for source in outside_loop_patterns:
            # These parse successfully but would fail at compile/runtime
            tree = tester.assert_continue_syntax_parses(source)
            continue_nodes = tester.get_continue_statements(source)
            assert len(continue_nodes) >= 1, f"Continue should parse: {source}"
    
    def test_continue_in_finally_block_restrictions(self, tester):
        """Test continue in finally block restrictions"""
        # Language Reference: continue in finally can be problematic
        # Note: Some restrictions are runtime, not syntax
        finally_continue_patterns = [
            """
for i in range(10):
    try:
        process(i)
    finally:
        if i % 2 == 0:
            continue  # May be restricted in some contexts
""",
        ]
        
        for source in finally_continue_patterns:
            # This may parse but could cause runtime issues
            tree = tester.assert_continue_syntax_parses(source)
            continue_nodes = tester.get_continue_statements(source)
            assert len(continue_nodes) >= 1, f"Continue should parse in finally: {source}"
    
    def test_continue_with_function_definitions(self, tester):
        """Test continue with nested function definitions"""
        # Language Reference: continue affects loop, not nested functions
        function_definition_patterns = [
            """
for i in range(10):
    def inner_function():
        # continue here would be invalid
        return i * 2
    
    if i % 2 == 0:
        continue
    result = inner_function()
""",
            """
while condition:
    def process_data(data):
        if not data:
            return None  # Not continue
        return data.upper()
    
    item = get_item()
    if not validate(item):
        continue
    process_data(item)
"""
        ]
        
        for source in function_definition_patterns:
            tree = tester.assert_continue_syntax_parses(source)
            continue_nodes = tester.get_continue_statements(source)
            assert len(continue_nodes) >= 1, f"Should have continue statements: {source}"


class TestSection710ContinueWithControlStructures:
    """Test continue interaction with other control structures."""
    
    def test_continue_with_try_except(self, tester):
        """Test continue in try/except blocks within loops"""
        # Language Reference: continue works in try/except within loops
        try_except_continue_patterns = [
            """
for item in items:
    try:
        result = process(item)
        if not result:
            continue
        handle_result(result)
    except ProcessingError:
        continue
    except Exception as e:
        log_error(e)
        continue
""",
            """
while running:
    try:
        data = get_data()
        if not validate_data(data):
            continue
    except DataError:
        continue
    except ConnectionError:
        break
    else:
        process_data(data)
    finally:
        cleanup()
""",
            """
for file_path in file_paths:
    try:
        with open(file_path) as f:
            content = f.read()
            if not content.strip():
                continue
            process_content(content)
    except FileNotFoundError:
        continue
    except PermissionError:
        log_permission_error(file_path)
        continue
"""
        ]
        
        for source in try_except_continue_patterns:
            tree = tester.assert_continue_syntax_parses(source)
            continue_nodes = tester.get_continue_statements(source)
            assert len(continue_nodes) >= 1, f"Should have continue statements: {source}"
    
    def test_continue_with_context_managers(self, tester):
        """Test continue with context managers (with statements)"""
        # Language Reference: continue works with context managers in loops
        context_manager_continue_patterns = [
            """
for file_name in file_names:
    if not file_name.endswith('.txt'):
        continue
    with open(file_name) as f:
        data = f.read()
        if not data:
            continue
        process_data(data)
""",
            """
while has_resources():
    resource = get_resource()
    if not resource.is_available():
        continue
    
    with resource.acquire() as handle:
        if not handle.is_valid():
            continue
        result = handle.perform_operation()
        if result.success:
            handle.commit()
        else:
            continue
""",
            """
for config_file in config_files:
    try:
        with open(config_file) as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        continue
    
    if not validate_config(config):
        continue
    
    apply_config(config)
"""
        ]
        
        for source in context_manager_continue_patterns:
            tree = tester.assert_continue_syntax_parses(source)
            continue_nodes = tester.get_continue_statements(source)
            assert len(continue_nodes) >= 1, f"Should have continue statements: {source}"
    
    def test_continue_with_comprehensions(self, tester):
        """Test continue interaction with comprehensions"""
        # Language Reference: continue doesn't affect comprehensions directly
        comprehension_continue_patterns = [
            """
for batch in data_batches:
    if not batch:
        continue
    
    # Comprehensions have their own scope
    results = [process_item(item) for item in batch if item.is_valid()]
    filtered = [r for r in results if r is not None]
    
    if not filtered:
        continue
    
    handle_results(filtered)
""",
            """
while condition:
    items = get_items()
    if not items:
        continue
    
    # Generator expression with filtering
    processed = (transform(item) for item in items if should_process(item))
    
    for result in processed:
        if not validate_result(result):
            continue  # This continue affects the for loop
        store_result(result)
""",
            """
for data_set in data_sets:
    if data_set.is_empty():
        continue
    
    # Dict comprehension
    mapping = {item.id: item.value for item in data_set if item.is_active()}
    
    if not mapping:
        continue
    
    process_mapping(mapping)
"""
        ]
        
        for source in comprehension_continue_patterns:
            tree = tester.assert_continue_syntax_parses(source)
            continue_nodes = tester.get_continue_statements(source)
            assert len(continue_nodes) >= 1, f"Should have continue statements: {source}"


class TestSection710ContinueASTStructure:
    """Test continue AST structure validation."""
    
    def test_continue_ast_node_structure(self, tester):
        """Test Continue AST node structure"""
        # Language Reference: AST structure for continue statements
        continue_ast_cases = [
            """
for i in range(10):
    if i % 2 == 0:
        continue
    print(i)
""",
            """
while condition:
    item = get_item()
    if not item:
        continue
    process_item(item)
"""
        ]
        
        for source in continue_ast_cases:
            tree = tester.assert_continue_syntax_parses(source)
            continue_nodes = tester.get_continue_statements(source)
            assert len(continue_nodes) >= 1, f"Should have continue nodes: {source}"
            
            for continue_node in continue_nodes:
                # Continue nodes are simple - just verify type
                assert isinstance(continue_node, ast.Continue), "Should be Continue node"
                # Continue has no attributes beyond the base node
    
    def test_continue_statement_positioning(self, tester):
        """Test continue statement positioning in AST"""
        # Language Reference: continue can appear anywhere within loop body
        positioning_cases = [
            """
for i in range(10):
    continue  # At beginning of loop body
""",
            """
for i in range(10):
    setup(i)
    continue  # In middle of loop body
""",
            """
for i in range(10):
    setup(i)
    process(i)
    continue  # At end of loop body
""",
        ]
        
        for source in positioning_cases:
            tree = tester.assert_continue_syntax_parses(source)
            continue_nodes = tester.get_continue_statements(source)
            assert len(continue_nodes) == 1, f"Should have one continue statement: {source}"
    
    def test_multiple_continue_statements_ast(self, tester):
        """Test multiple continue statements in AST"""
        # Language Reference: multiple continue statements create multiple AST nodes
        multiple_continue_source = """
for i in range(20):
    if i < 5:
        continue
    if i > 15:
        continue
    if i % 2 == 0:
        continue
    print(i)
"""
        
        tree = tester.assert_continue_syntax_parses(multiple_continue_source)
        continue_nodes = tester.get_continue_statements(multiple_continue_source)
        assert len(continue_nodes) == 3, "Should have three continue statements"
        
        # All should be Continue nodes
        for continue_node in continue_nodes:
            assert isinstance(continue_node, ast.Continue), "Should be Continue node"


class TestSection710CrossImplementationCompatibility:
    """Test cross-implementation compatibility for continue statements."""
    
    def test_continue_ast_consistency(self, tester):
        """Test continue AST consistency across implementations"""
        # Language Reference: continue AST should be consistent
        consistency_test_cases = [
            """
for item in items:
    if not validate(item):
        continue
    process(item)
""",
            """
while running:
    event = get_event()
    if event.type == 'skip':
        continue
    handle_event(event)
""",
            """
for i in range(100):
    for j in range(100):
        if (i + j) % 10 == 0:
            continue
        compute(i, j)
"""
        ]
        
        for source in consistency_test_cases:
            tree = tester.assert_continue_syntax_parses(source)
            
            # Should have consistent continue structure
            continue_nodes = tester.get_continue_statements(source)
            assert len(continue_nodes) >= 1, f"Should have continue statements: {source}"
            
            for continue_node in continue_nodes:
                assert isinstance(continue_node, ast.Continue), "Should be Continue node"
    
    def test_comprehensive_continue_patterns(self, tester):
        """Test comprehensive real-world continue patterns"""
        # Language Reference: complex continue usage scenarios
        comprehensive_patterns = [
            """
# Data processing pipeline with continue
def process_data_pipeline(data_stream):
    for batch in data_stream:
        if not batch or batch.is_empty():
            continue
            
        # Validation phase
        for item in batch:
            if not item.is_valid():
                continue
            if item.requires_preprocessing():
                item = preprocess(item)
                if not item:  # Preprocessing failed
                    continue
            
            # Processing phase
            try:
                result = process_item(item)
                if not result.success:
                    continue
                store_result(result)
            except ProcessingError:
                continue
""",
            """
# Event loop with continue statements
def event_loop():
    while True:
        try:
            event = get_next_event(timeout=1.0)
        except TimeoutError:
            continue
        except ShutdownSignal:
            break
            
        if not event:
            continue
            
        # Event filtering
        if event.priority < MIN_PRIORITY:
            continue
        if event.source in BLACKLISTED_SOURCES:
            continue
            
        # Event processing
        for handler in event_handlers:
            if not handler.can_handle(event):
                continue
            try:
                if handler.handle(event):
                    break  # Event handled successfully
            except HandlerError:
                continue  # Try next handler
        else:
            # No handler could process the event
            log_unhandled_event(event)
            continue
"""
        ]
        
        for source in comprehensive_patterns:
            tree = tester.assert_continue_syntax_parses(source)
            
            # Should have multiple continue usages
            continue_nodes = tester.get_continue_statements(source)
            assert len(continue_nodes) >= 3, f"Should have multiple continue statements: {source}"
    
    def test_continue_introspection(self, tester):
        """Test ability to analyze continue statements programmatically"""
        # Test programmatic analysis of continue structure
        introspection_source = """
for outer_index in range(10):
    if outer_index % 3 == 0:
        continue
        
    for inner_index in range(5):
        if inner_index == 2:
            continue
        if outer_index + inner_index > 8:
            continue
            
        while condition(outer_index, inner_index):
            value = compute(outer_index, inner_index)
            if not validate(value):
                continue
            process(value)
            update_condition()
"""
        
        tree = tester.assert_continue_syntax_parses(introspection_source)
        
        # Should identify all continue statements
        continue_nodes = tester.get_continue_statements(introspection_source)
        assert len(continue_nodes) >= 4, "Should have multiple continue statements"
        
        # Should detect nested loop structure
        loop_depth = tester.get_loop_depth(introspection_source)
        assert loop_depth >= 3, "Should have deeply nested loops"
        
        # All continue nodes should be ast.Continue
        for continue_node in continue_nodes:
            assert isinstance(continue_node, ast.Continue), "Should be Continue node"
        
        # Should have loop statements
        assert tester.has_loop_statements(introspection_source), "Should have loop statements"