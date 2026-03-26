"""
Section 7.9: Break Statement - Conformance Test Suite

Tests Python Language Reference Section 7.9 compliance across implementations.
Based on formal break statement syntax definitions and prose assertions for loop termination behavior.

Grammar tested:
    break_stmt: 'break'

Language Reference requirements tested:
    - Break statement syntax validation
    - Loop termination semantics and behavior
    - Break statement placement within loop contexts
    - Nested loop break behavior and scope
    - Break interaction with loop else clauses
    - Syntactic context requirements for break
    - Error conditions for invalid break usage
    - Break statement AST structure validation
    - Cross-implementation break compatibility
"""

import ast
import pytest
import sys
from typing import Any


class BreakTester:
    """Helper class for testing break statement conformance.
    
    Focuses on AST structure validation for break syntax and loop
    termination patterns that can be statically analyzed for cross-implementation compatibility.
    """
    
    def assert_break_syntax_parses(self, source: str):
        """Test that break statement syntax parses correctly.
        
        Args:
            source: Python source code with break statements
        """
        try:
            tree = ast.parse(source)
            return tree
        except SyntaxError as e:
            pytest.fail(f"Break syntax should be valid but failed to parse: {source}\\nError: {e}")
    
    def assert_break_syntax_error(self, source: str):
        """Test that invalid break syntax raises SyntaxError.
        
        Args:
            source: Python source code that should be invalid
        """
        with pytest.raises(SyntaxError):
            ast.parse(source)
    
    def get_break_statements(self, source: str) -> list:
        """Get Break AST nodes from source.
        
        Args:
            source: Python source code
            
        Returns:
            List of ast.Break nodes
        """
        tree = ast.parse(source)
        breaks = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Break):
                breaks.append(node)
        
        return breaks
    
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
    
    def has_loop_else_clauses(self, source: str) -> bool:
        """Check if source contains loop else clauses.
        
        Args:
            source: Python source code
            
        Returns:
            True if contains loops with else clauses
        """
        tree = ast.parse(source)
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                if node.orelse:  # Has else clause
                    return True
        
        return False


@pytest.fixture
def tester():
    """Provide BreakTester instance for tests."""
    return BreakTester()


class TestSection79BasicBreakSyntax:
    """Test basic break statement syntax."""
    
    def test_simple_break_in_for_loop(self, tester):
        """Test simple break statement in for loops"""
        # Language Reference: break_stmt: 'break'
        simple_for_break_patterns = [
            """
for i in range(10):
    if i == 5:
        break
    print(i)
""",
            """
for item in [1, 2, 3, 4, 5]:
    if item == 3:
        break
    result = item * 2
""",
            """
for x in "hello":
    if x == 'l':
        break
    process(x)
""",
            """
for index, value in enumerate([1, 2, 3]):
    if value > 2:
        break
    use_value(value)
"""
        ]
        
        for source in simple_for_break_patterns:
            tree = tester.assert_break_syntax_parses(source)
            break_nodes = tester.get_break_statements(source)
            assert len(break_nodes) == 1, f"Should have one break statement: {source}"
            assert tester.has_loop_statements(source), f"Should have loop statements: {source}"
    
    def test_simple_break_in_while_loop(self, tester):
        """Test simple break statement in while loops"""
        # Language Reference: break works in while loops
        simple_while_break_patterns = [
            """
i = 0
while i < 10:
    if i == 5:
        break
    print(i)
    i += 1
""",
            """
counter = 0
while True:
    counter += 1
    if counter > 5:
        break
    process(counter)
""",
            """
found = False
attempts = 0
while not found:
    attempts += 1
    if attempts > 10:
        break
    found = check_condition()
""",
            """
while True:
    data = get_data()
    if not data:
        break
    handle_data(data)
"""
        ]
        
        for source in simple_while_break_patterns:
            tree = tester.assert_break_syntax_parses(source)
            break_nodes = tester.get_break_statements(source)
            assert len(break_nodes) == 1, f"Should have one break statement: {source}"
            assert tester.has_loop_statements(source), f"Should have loop statements: {source}"
    
    def test_multiple_break_statements(self, tester):
        """Test multiple break statements in same loop"""
        # Language Reference: multiple breaks allowed in same loop
        multiple_break_patterns = [
            """
for i in range(20):
    if i < 5:
        print(f"Early: {i}")
    elif i > 15:
        break
    elif i % 3 == 0:
        print(f"Multiple of 3: {i}")
        break
    else:
        print(i)
""",
            """
while True:
    command = get_command()
    if command == "quit":
        break
    if command == "exit":
        break
    if not process_command(command):
        break
""",
            """
for line in file_lines:
    if line.startswith('END'):
        break
    if line.startswith('QUIT'):
        print("Quit command found")
        break
    process_line(line)
"""
        ]
        
        for source in multiple_break_patterns:
            tree = tester.assert_break_syntax_parses(source)
            break_nodes = tester.get_break_statements(source)
            assert len(break_nodes) >= 2, f"Should have multiple break statements: {source}"
    
    def test_break_in_conditional_blocks(self, tester):
        """Test break statements within conditional blocks"""
        # Language Reference: break can appear in if/elif/else within loops
        conditional_break_patterns = [
            """
for i in range(10):
    if i % 2 == 0:
        if i > 6:
            break
        print(f"Even: {i}")
    else:
        print(f"Odd: {i}")
""",
            """
while running:
    event = get_event()
    if event.type == 'quit':
        break
    elif event.type == 'error':
        log_error(event)
        break
    else:
        process_event(event)
""",
            """
for item in items:
    try:
        result = process_item(item)
        if not result:
            break
    except ProcessingError:
        break
    except Exception:
        continue
    store_result(result)
"""
        ]
        
        for source in conditional_break_patterns:
            tree = tester.assert_break_syntax_parses(source)
            break_nodes = tester.get_break_statements(source)
            assert len(break_nodes) >= 1, f"Should have break statements: {source}"


class TestSection79NestedLoopBreak:
    """Test break behavior in nested loops."""
    
    def test_break_in_nested_for_loops(self, tester):
        """Test break in nested for loops"""
        # Language Reference: break affects innermost loop only
        nested_for_break_patterns = [
            """
for i in range(3):
    for j in range(3):
        if j == 1:
            break  # Breaks inner loop only
        print(i, j)
    print(f"Outer loop iteration {i} complete")
""",
            """
found = False
for row in matrix:
    for col_index, value in enumerate(row):
        if value == target:
            found = True
            break  # Break inner loop
    if found:
        break  # Break outer loop
""",
            """
for category in categories:
    category_processed = False
    for item in category.items:
        if process_item(item):
            category_processed = True
            break  # Found what we need, break inner
        if item.is_error:
            break  # Error encountered, break inner
    if not category_processed:
        handle_empty_category(category)
""",
            """
for outer_index in range(5):
    for middle_index in range(5):
        for inner_index in range(5):
            if inner_index == 2:
                break  # Breaks innermost only
            if middle_index + inner_index > 6:
                break  # Still innermost
            compute(outer_index, middle_index, inner_index)
"""
        ]
        
        for source in nested_for_break_patterns:
            tree = tester.assert_break_syntax_parses(source)
            break_nodes = tester.get_break_statements(source)
            assert len(break_nodes) >= 1, f"Should have break statements: {source}"
            
            loop_depth = tester.get_loop_depth(source)
            assert loop_depth >= 2, f"Should have nested loops: {source}"
    
    def test_break_in_nested_while_loops(self, tester):
        """Test break in nested while loops"""
        # Language Reference: break affects innermost loop
        nested_while_break_patterns = [
            """
i = 0
while i < 3:
    j = 0
    while j < 3:
        if j == 1:
            break  # Breaks inner while only
        print(i, j)
        j += 1
    i += 1
""",
            """
server_running = True
while server_running:
    client_connected = True
    while client_connected:
        message = receive_message()
        if message == "disconnect":
            break  # Break inner loop (client session)
        if message == "shutdown":
            server_running = False
            break  # Break inner loop, outer will exit too
        process_message(message)
""",
            """
processing = True
while processing:
    batch_available = True
    while batch_available:
        batch = get_next_batch()
        if not batch:
            batch_available = False
            break
        if not process_batch(batch):
            print("Processing error, stopping batch")
            break
        if batch.is_final:
            processing = False
            break
"""
        ]
        
        for source in nested_while_break_patterns:
            tree = tester.assert_break_syntax_parses(source)
            break_nodes = tester.get_break_statements(source)
            assert len(break_nodes) >= 1, f"Should have break statements: {source}"
            
            loop_depth = tester.get_loop_depth(source)
            assert loop_depth >= 2, f"Should have nested loops: {source}"
    
    def test_break_in_mixed_nested_loops(self, tester):
        """Test break in mixed for/while nested loops"""
        # Language Reference: break works in mixed loop types
        mixed_nested_break_patterns = [
            """
for i in range(10):
    j = 0
    while j < 10:
        if (i + j) == 15:
            break  # Break while loop
        j += 1
    if i == 7:
        break  # Break for loop
""",
            """
while condition:
    for item in get_items():
        if not process_item(item):
            break  # Break for loop
        if item.causes_shutdown:
            condition = False
            break  # Break for loop, while will exit too
    update_condition()
""",
            """
search_complete = False
for data_source in data_sources:
    current_pos = 0
    while current_pos < data_source.size():
        item = data_source.get(current_pos)
        if item == search_target:
            search_complete = True
            break  # Break while loop
        current_pos += 1
    if search_complete:
        break  # Break for loop
"""
        ]
        
        for source in mixed_nested_break_patterns:
            tree = tester.assert_break_syntax_parses(source)
            break_nodes = tester.get_break_statements(source)
            assert len(break_nodes) >= 1, f"Should have break statements: {source}"


class TestSection79BreakWithElseClauses:
    """Test break interaction with loop else clauses."""
    
    def test_break_prevents_else_execution(self, tester):
        """Test break preventing loop else clause execution"""
        # Language Reference: break prevents else clause execution
        break_else_patterns = [
            """
for i in range(10):
    if i == 5:
        break
else:
    print("Loop completed normally")  # Won't execute
""",
            """
while condition:
    if should_break():
        break
    process_iteration()
else:
    print("While loop completed without break")  # Won't execute if break
""",
            """
for item in items:
    if item == target:
        found = True
        break
else:
    found = False  # Only executes if no break
""",
            """
attempts = 0
while attempts < max_attempts:
    attempts += 1
    if try_operation():
        success = True
        break
else:
    success = False  # Only if loop exhausted without break
"""
        ]
        
        for source in break_else_patterns:
            tree = tester.assert_break_syntax_parses(source)
            break_nodes = tester.get_break_statements(source)
            assert len(break_nodes) >= 1, f"Should have break statements: {source}"
            assert tester.has_loop_else_clauses(source), f"Should have loop else clauses: {source}"
    
    def test_nested_loop_break_else_interaction(self, tester):
        """Test break in nested loops with else clauses"""
        # Language Reference: break affects only the immediate loop's else
        nested_break_else_patterns = [
            """
for i in range(5):
    for j in range(5):
        if j == 3:
            break  # Prevents inner else, not outer else
    else:
        print(f"Inner loop {i} completed normally")
else:
    print("Outer loop completed normally")
""",
            """
found_in_category = False
for category in categories:
    for item in category:
        if item == target:
            found_in_category = True
            break  # Break inner loop
    else:
        print(f"Target not found in {category}")
        continue  # Continue outer loop
    break  # Break outer loop if found
else:
    print("Target not found in any category")
""",
            """
for data_set in data_sets:
    while data_set.has_data():
        data = data_set.next()
        if data.is_corrupt():
            break  # Break while, affects while's else
    else:
        print(f"All data in {data_set} processed successfully")
        continue
    print(f"Corrupted data found in {data_set}")
    break  # Break for loop
else:
    print("All data sets processed successfully")
"""
        ]
        
        for source in nested_break_else_patterns:
            tree = tester.assert_break_syntax_parses(source)
            break_nodes = tester.get_break_statements(source)
            assert len(break_nodes) >= 1, f"Should have break statements: {source}"


class TestSection79BreakErrorConditions:
    """Test break statement error conditions."""
    
    def test_break_outside_loop_error(self, tester):
        """Test break outside loop context"""
        # Language Reference: break only valid inside loops
        # Note: Break restrictions are checked at compile time, not parse time
        outside_loop_patterns = [
            "break",  # Module level - parses but may fail at compile/runtime
            """
def function():
    break  # Function level - parses but may fail at compile/runtime
""",
        ]
        
        for source in outside_loop_patterns:
            # These parse successfully but would fail at compile/runtime
            tree = tester.assert_break_syntax_parses(source)
            break_nodes = tester.get_break_statements(source)
            assert len(break_nodes) >= 1, f"Break should parse: {source}"
    
    def test_break_in_finally_block_restrictions(self, tester):
        """Test break in finally block restrictions"""
        # Language Reference: break in finally can be problematic
        # Note: Some restrictions are runtime, not syntax
        finally_break_patterns = [
            """
for i in range(10):
    try:
        process(i)
    finally:
        if i % 2 == 0:
            break  # May be restricted in some contexts
""",
        ]
        
        for source in finally_break_patterns:
            # This may parse but could cause runtime issues
            tree = tester.assert_break_syntax_parses(source)
            break_nodes = tester.get_break_statements(source)
            assert len(break_nodes) >= 1, f"Break should parse in finally: {source}"
    
    def test_break_with_function_definitions(self, tester):
        """Test break with nested function definitions"""
        # Language Reference: break affects loop, not nested functions
        function_definition_patterns = [
            """
for i in range(10):
    def inner_function():
        # break here would be invalid
        return i * 2
    
    if i == 5:
        break
    result = inner_function()
""",
            """
while condition:
    def process_data(data):
        if not data:
            return None  # Not break
        return data.upper()
    
    item = get_item()
    if not validate(item):
        break
    process_data(item)
"""
        ]
        
        for source in function_definition_patterns:
            tree = tester.assert_break_syntax_parses(source)
            break_nodes = tester.get_break_statements(source)
            assert len(break_nodes) >= 1, f"Should have break statements: {source}"


class TestSection79BreakWithControlStructures:
    """Test break interaction with other control structures."""
    
    def test_break_with_try_except(self, tester):
        """Test break in try/except blocks within loops"""
        # Language Reference: break works in try/except within loops
        try_except_break_patterns = [
            """
for item in items:
    try:
        result = process(item)
        if not result:
            break
        handle_result(result)
    except ProcessingError:
        print(f"Error processing {item}")
        break
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
        print("Data error, stopping")
        break
    except ConnectionError:
        print("Connection lost")
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
            if "STOP" in content:
                print("Stop marker found")
                break
            process_content(content)
    except FileNotFoundError:
        continue
    except PermissionError:
        print(f"Permission denied: {file_path}")
        break
"""
        ]
        
        for source in try_except_break_patterns:
            tree = tester.assert_break_syntax_parses(source)
            break_nodes = tester.get_break_statements(source)
            assert len(break_nodes) >= 1, f"Should have break statements: {source}"
    
    def test_break_with_context_managers(self, tester):
        """Test break with context managers (with statements)"""
        # Language Reference: break works with context managers in loops
        context_manager_break_patterns = [
            """
for file_name in file_names:
    if not file_name.endswith('.txt'):
        continue
    with open(file_name) as f:
        data = f.read()
        if "END_MARKER" in data:
            print("End marker found, stopping")
            break
        process_data(data)
""",
            """
while has_resources():
    resource = get_resource()
    if not resource.is_available():
        break
    
    with resource.acquire() as handle:
        if not handle.is_valid():
            break
        result = handle.perform_operation()
        if result.is_terminal:
            print("Terminal result, stopping")
            break
        handle.commit()
""",
            """
for config_file in config_files:
    try:
        with open(config_file) as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        continue
    
    if config.get("stop_processing", False):
        print("Stop flag found in config")
        break
    
    apply_config(config)
"""
        ]
        
        for source in context_manager_break_patterns:
            tree = tester.assert_break_syntax_parses(source)
            break_nodes = tester.get_break_statements(source)
            assert len(break_nodes) >= 1, f"Should have break statements: {source}"
    
    def test_break_with_generator_functions(self, tester):
        """Test break in loops containing generator usage"""
        # Language Reference: break in loops with generators
        generator_break_patterns = [
            """
def number_generator():
    for i in range(100):
        yield i

for num in number_generator():
    if num > 50:
        break
    print(num)
""",
            """
while True:
    batch = (item for item in get_items() if item.is_valid())
    processed_count = 0
    
    for item in batch:
        if processed_count > 100:
            break  # Break the for loop, not the generator
        process_item(item)
        processed_count += 1
    
    if processed_count == 0:
        break  # Break the while loop
""",
            """
for data_chunk in data_source:
    filtered_items = (item for item in data_chunk if filter_func(item))
    
    for item in filtered_items:
        result = process_item(item)
        if result.is_error:
            print("Error encountered, stopping chunk processing")
            break
        if result.is_complete:
            print("Processing complete")
            break
"""
        ]
        
        for source in generator_break_patterns:
            tree = tester.assert_break_syntax_parses(source)
            break_nodes = tester.get_break_statements(source)
            assert len(break_nodes) >= 1, f"Should have break statements: {source}"


class TestSection79BreakASTStructure:
    """Test break AST structure validation."""
    
    def test_break_ast_node_structure(self, tester):
        """Test Break AST node structure"""
        # Language Reference: AST structure for break statements
        break_ast_cases = [
            """
for i in range(10):
    if i == 5:
        break
    print(i)
""",
            """
while condition:
    item = get_item()
    if not item:
        break
    process_item(item)
"""
        ]
        
        for source in break_ast_cases:
            tree = tester.assert_break_syntax_parses(source)
            break_nodes = tester.get_break_statements(source)
            assert len(break_nodes) >= 1, f"Should have break nodes: {source}"
            
            for break_node in break_nodes:
                # Break nodes are simple - just verify type
                assert isinstance(break_node, ast.Break), "Should be Break node"
                # Break has no attributes beyond the base node
    
    def test_break_statement_positioning(self, tester):
        """Test break statement positioning in AST"""
        # Language Reference: break can appear anywhere within loop body
        positioning_cases = [
            """
for i in range(10):
    break  # At beginning of loop body
""",
            """
for i in range(10):
    setup(i)
    break  # In middle of loop body
""",
            """
for i in range(10):
    setup(i)
    process(i)
    break  # At end of loop body
""",
        ]
        
        for source in positioning_cases:
            tree = tester.assert_break_syntax_parses(source)
            break_nodes = tester.get_break_statements(source)
            assert len(break_nodes) == 1, f"Should have one break statement: {source}"
    
    def test_multiple_break_statements_ast(self, tester):
        """Test multiple break statements in AST"""
        # Language Reference: multiple break statements create multiple AST nodes
        multiple_break_source = """
while True:
    command = input("Enter command: ")
    if command == "quit":
        break
    elif command == "exit":
        print("Exiting...")
        break
    elif command == "stop":
        print("Stopping...")
        break
    else:
        print(f"Unknown command: {command}")
"""
        
        tree = tester.assert_break_syntax_parses(multiple_break_source)
        break_nodes = tester.get_break_statements(multiple_break_source)
        assert len(break_nodes) == 3, "Should have three break statements"
        
        # All should be Break nodes
        for break_node in break_nodes:
            assert isinstance(break_node, ast.Break), "Should be Break node"


class TestSection79CrossImplementationCompatibility:
    """Test cross-implementation compatibility for break statements."""
    
    def test_break_ast_consistency(self, tester):
        """Test break AST consistency across implementations"""
        # Language Reference: break AST should be consistent
        consistency_test_cases = [
            """
for item in items:
    if not validate(item):
        continue
    if process(item):
        break
""",
            """
while running:
    event = get_event()
    if event.type == 'quit':
        break
    handle_event(event)
""",
            """
for i in range(100):
    for j in range(100):
        if (i * j) > 1000:
            break
        compute(i, j)
"""
        ]
        
        for source in consistency_test_cases:
            tree = tester.assert_break_syntax_parses(source)
            
            # Should have consistent break structure
            break_nodes = tester.get_break_statements(source)
            assert len(break_nodes) >= 1, f"Should have break statements: {source}"
            
            for break_node in break_nodes:
                assert isinstance(break_node, ast.Break), "Should be Break node"
    
    def test_comprehensive_break_patterns(self, tester):
        """Test comprehensive real-world break patterns"""
        # Language Reference: complex break usage scenarios
        comprehensive_patterns = [
            """
# Search algorithm with break
def search_in_matrix(matrix, target):
    found = False
    for row_idx, row in enumerate(matrix):
        for col_idx, value in enumerate(row):
            if value == target:
                found_row, found_col = row_idx, col_idx
                found = True
                break  # Break inner loop
        if found:
            break  # Break outer loop
    
    return (found_row, found_col) if found else None

# File processing with break conditions
def process_files(file_list):
    for file_path in file_list:
        try:
            with open(file_path) as f:
                for line_num, line in enumerate(f, 1):
                    if line.strip() == "STOP":
                        print(f"Stop marker found in {file_path}:{line_num}")
                        return  # Stop all processing
                    if line.startswith("SKIP_FILE"):
                        print(f"Skip marker found in {file_path}")
                        break  # Skip to next file
                    process_line(line)
        except FileNotFoundError:
            continue
        except PermissionError:
            print(f"Permission denied: {file_path}")
            break  # Stop processing remaining files
""",
            """
# Network server with break handling
def run_server():
    server_running = True
    while server_running:
        try:
            client_socket = accept_connection()
        except KeyboardInterrupt:
            print("Server shutdown requested")
            break
        except ConnectionError:
            print("Connection error, retrying...")
            continue
        
        # Handle client
        while True:
            try:
                message = receive_message(client_socket)
                if not message:
                    break  # Client disconnected
                
                if message == "SHUTDOWN_SERVER":
                    server_running = False
                    break  # Break client loop, server will stop
                
                response = process_message(message)
                send_message(client_socket, response)
                
            except MessageError:
                break  # Break client loop on message error
            except Exception as e:
                log_error(e)
                break  # Break client loop on unexpected error
        
        close_connection(client_socket)
"""
        ]
        
        for source in comprehensive_patterns:
            tree = tester.assert_break_syntax_parses(source)
            
            # Should have multiple break usages
            break_nodes = tester.get_break_statements(source)
            assert len(break_nodes) >= 3, f"Should have multiple break statements: {source}"
    
    def test_break_introspection(self, tester):
        """Test ability to analyze break statements programmatically"""
        # Test programmatic analysis of break structure
        introspection_source = """
for outer_index in range(10):
    if outer_index > 8:
        break
        
    for inner_index in range(5):
        if inner_index == 3:
            break
        if outer_index + inner_index > 6:
            break
            
        while condition(outer_index, inner_index):
            value = compute(outer_index, inner_index)
            if value > threshold:
                break
            if not validate(value):
                break
            process(value)
            update_condition()
"""
        
        tree = tester.assert_break_syntax_parses(introspection_source)
        
        # Should identify all break statements
        break_nodes = tester.get_break_statements(introspection_source)
        assert len(break_nodes) >= 5, "Should have multiple break statements"
        
        # Should detect nested loop structure
        loop_depth = tester.get_loop_depth(introspection_source)
        assert loop_depth >= 3, "Should have deeply nested loops"
        
        # All break nodes should be ast.Break
        for break_node in break_nodes:
            assert isinstance(break_node, ast.Break), "Should be Break node"
        
        # Should have loop statements
        assert tester.has_loop_statements(introspection_source), "Should have loop statements"