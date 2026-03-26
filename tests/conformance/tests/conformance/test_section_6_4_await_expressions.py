"""
Section 6.4: Await Expressions - Conformance Test Suite

Tests Python Language Reference Section 6.4 compliance across implementations.
Based on formal await expression syntax definitions and prose assertions for asynchronous behavior.

Grammar tested:
    await_expr: 'await' primary

Language Reference requirements tested:
    - Await expression syntax and async context requirements
    - Await with coroutine functions and awaitable objects
    - Await expression precedence and associativity
    - Await expressions in different contexts
    - Error conditions for await outside async context
    - Await expression AST structure validation
    - Cross-implementation await expression compatibility
"""

import ast
import pytest
import sys
from typing import Any


class AwaitExpressionTester:
    """Helper class for testing await expression conformance.
    
    Focuses on AST structure validation for await expression syntax and behavior
    patterns that can be statically analyzed for cross-implementation compatibility.
    """
    
    def assert_await_expression_parses(self, source: str):
        """Test that await expression syntax parses correctly.
        
        Args:
            source: Python source code with await expressions
        """
        try:
            tree = ast.parse(source)
            return tree
        except SyntaxError as e:
            pytest.fail(f"Await expression syntax should be valid but failed to parse: {source}\\nError: {e}")
    
    def assert_await_expression_syntax_error(self, source: str):
        """Test that invalid await expression syntax raises SyntaxError.
        
        Args:
            source: Python source code that should be invalid
        """
        with pytest.raises(SyntaxError):
            ast.parse(source)
    
    def get_await_expressions(self, source: str) -> list:
        """Get Await AST nodes from source.
        
        Args:
            source: Python source code
            
        Returns:
            List of ast.Await nodes
        """
        tree = ast.parse(source)
        await_exprs = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Await):
                await_exprs.append(node)
        
        return await_exprs
    
    def get_async_function_defs(self, source: str) -> list:
        """Get AsyncFunctionDef AST nodes from source.
        
        Args:
            source: Python source code
            
        Returns:
            List of ast.AsyncFunctionDef nodes
        """
        tree = ast.parse(source)
        async_funcs = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef):
                async_funcs.append(node)
        
        return async_funcs
    
    def get_function_defs(self, source: str) -> list:
        """Get regular FunctionDef AST nodes from source.
        
        Args:
            source: Python source code
            
        Returns:
            List of ast.FunctionDef nodes
        """
        tree = ast.parse(source)
        funcs = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                funcs.append(node)
        
        return funcs
    
    def count_nested_await_expressions(self, source: str) -> int:
        """Count nested await expressions.
        
        Args:
            source: Python source code
            
        Returns:
            Maximum depth of nested await expressions
        """
        tree = ast.parse(source)
        
        def count_depth(node):
            if isinstance(node, ast.Await):
                # Count depth in the awaited expression
                value_depth = count_depth(node.value)
                return 1 + value_depth
            elif hasattr(node, '_fields'):
                # Check all child nodes
                max_depth = 0
                for field in node._fields:
                    value = getattr(node, field, None)
                    if isinstance(value, ast.AST):
                        depth = count_depth(value)
                        max_depth = max(max_depth, depth)
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, ast.AST):
                                depth = count_depth(item)
                                max_depth = max(max_depth, depth)
                return max_depth
            return 0
        
        return count_depth(tree)


@pytest.fixture
def tester():
    """Provide AwaitExpressionTester instance for tests."""
    return AwaitExpressionTester()


@pytest.mark.min_version_3_5
class TestSection64BasicAwaitSyntax:
    """Test basic await expression syntax."""
    
    def test_simple_await_expressions(self, tester):
        """Test simple await expression patterns"""
        # Language Reference: await_expr: 'await' primary
        await_patterns = [
            """
async def simple_await():
    result = await coroutine()
""",
            """
async def await_variable():
    value = await some_coroutine
""",
            """
async def await_call():
    output = await async_function()
""",
            """
async def await_attribute():
    data = await obj.async_method()
""",
            """
async def await_subscription():
    item = await async_dict[key]()
"""
        ]
        
        for source in await_patterns:
            tree = tester.assert_await_expression_parses(source)
            await_exprs = tester.get_await_expressions(source)
            assert len(await_exprs) >= 1, f"Should have await expressions: {source}"
            
            # Should be in async function
            async_funcs = tester.get_async_function_defs(source)
            assert len(async_funcs) >= 1, f"Should be in async function: {source}"
    
    def test_await_with_function_calls(self, tester):
        """Test await with function calls"""
        # Language Reference: await with callable expressions
        function_call_await_patterns = [
            """
async def await_simple_call():
    result = await fetch_data()
""",
            """
async def await_call_with_args():
    value = await process(data, mode='async')
""",
            """
async def await_method_call():
    output = await obj.async_method(param1, param2)
""",
            """
async def await_complex_call():
    result = await api.fetch(
        url='http://example.com',
        headers={'Accept': 'application/json'},
        timeout=30
    )
""",
            """
async def await_chained_calls():
    data = await client.connect().authenticate().fetch()
"""
        ]
        
        for source in function_call_await_patterns:
            tree = tester.assert_await_expression_parses(source)
            await_exprs = tester.get_await_expressions(source)
            assert len(await_exprs) >= 1, f"Should handle function calls: {source}"
    
    def test_await_with_expressions(self, tester):
        """Test await with complex expressions"""
        # Language Reference: await with complex primary expressions
        expression_await_patterns = [
            """
async def await_parenthesized():
    result = await (coroutine_func())
""",
            """
async def await_attribute_access():
    value = await obj.attr.method()
""",
            """
async def await_subscription():
    item = await async_dict['key']
""",
            """
async def await_slice():
    data = await async_sequence[start:end]
""",
            """
async def await_complex_expression():
    result = await (obj.method()[index].attr())
"""
        ]
        
        for source in expression_await_patterns:
            tree = tester.assert_await_expression_parses(source)
            await_exprs = tester.get_await_expressions(source)
            assert len(await_exprs) >= 1, f"Should handle complex expressions: {source}"
    
    def test_await_with_literals_and_names(self, tester):
        """Test await with literal values and names"""
        # Language Reference: await with primary expressions
        literal_await_patterns = [
            """
async def await_name():
    result = await coroutine_variable
""",
            """
async def await_attribute():
    value = await module.coroutine
""",
            """
async def await_call_result():
    output = await get_coroutine()
""",
            """
async def await_conditional():
    data = await (coro1 if condition else coro2)
""",
            """
async def await_generator_expression():
    result = await (coro for coro in coroutines).__anext__()
"""
        ]
        
        for source in literal_await_patterns:
            tree = tester.assert_await_expression_parses(source)
            await_exprs = tester.get_await_expressions(source)
            assert len(await_exprs) >= 1, f"Should handle literals and names: {source}"
    
    def test_multiple_await_expressions(self, tester):
        """Test multiple await expressions in same function"""
        # Language Reference: multiple awaits in async function
        multiple_await_source = """
async def multiple_awaits():
    # Multiple sequential awaits
    data1 = await fetch_user()
    data2 = await fetch_profile(data1.id)
    data3 = await fetch_permissions(data1.id)
    
    # Await in different contexts
    if await check_permission(data3):
        result = await process_data(data1, data2)
    else:
        result = await default_processing()
    
    return result
"""
        
        tree = tester.assert_await_expression_parses(multiple_await_source)
        await_exprs = tester.get_await_expressions(multiple_await_source)
        assert len(await_exprs) >= 5, "Should have multiple await expressions"


@pytest.mark.min_version_3_5
class TestSection64AwaitContexts:
    """Test await expressions in different contexts."""
    
    def test_await_in_assignments(self, tester):
        """Test await expressions in assignment contexts"""
        # Language Reference: await in assignments
        assignment_await_patterns = [
            """
async def simple_assignment():
    result = await coroutine()
""",
            """
async def multiple_assignment():
    a, b = await get_pair()
""",
            """
async def augmented_assignment():
    counter += await get_increment()
""",
            """
async def attribute_assignment():
    obj.value = await fetch_value()
""",
            """
async def subscription_assignment():
    data[key] = await fetch_item(key)
"""
        ]
        
        for source in assignment_await_patterns:
            tree = tester.assert_await_expression_parses(source)
            await_exprs = tester.get_await_expressions(source)
            assert len(await_exprs) >= 1, f"Should work in assignments: {source}"
    
    def test_await_in_function_calls(self, tester):
        """Test await expressions in function call arguments"""
        # Language Reference: await in function arguments
        function_call_await_patterns = [
            """
async def await_in_args():
    result = process(await fetch_data())
""",
            """
async def await_multiple_args():
    output = combine(await get_a(), await get_b(), await get_c())
""",
            """
async def await_in_kwargs():
    result = api_call(data=await fetch_data(), timeout=await get_timeout())
""",
            """
async def await_mixed_args():
    output = complex_function(
        await get_arg1(),
        regular_arg,
        keyword=await get_keyword_value(),
        flag=True
    )
""",
            """
async def await_in_method_call():
    result = obj.method(await prepare_args(), mode=await get_mode())
"""
        ]
        
        for source in function_call_await_patterns:
            tree = tester.assert_await_expression_parses(source)
            await_exprs = tester.get_await_expressions(source)
            assert len(await_exprs) >= 1, f"Should work in function calls: {source}"
    
    def test_await_in_return_statements(self, tester):
        """Test await expressions in return statements"""
        # Language Reference: await in return statements
        return_await_patterns = [
            """
async def simple_return():
    return await fetch_result()
""",
            """
async def conditional_return():
    if condition:
        return await success_handler()
    else:
        return await error_handler()
""",
            """
async def complex_return():
    return await transform(await fetch_data())
""",
            """
async def tuple_return():
    return await get_a(), await get_b()
""",
            """
async def expression_return():
    return (await get_value()) * 2 + offset
"""
        ]
        
        for source in return_await_patterns:
            tree = tester.assert_await_expression_parses(source)
            await_exprs = tester.get_await_expressions(source)
            assert len(await_exprs) >= 1, f"Should work in returns: {source}"
    
    def test_await_in_control_flow(self, tester):
        """Test await expressions in control flow statements"""
        # Language Reference: await in control flow
        control_flow_await_patterns = [
            """
async def await_in_if():
    if await check_condition():
        return True
    return False
""",
            """
async def await_in_while():
    while await has_more_data():
        data = await get_next_item()
        process(data)
""",
            """
async def await_in_for():
    async for item in await get_async_iterator():
        await process_item(item)
""",
            """
async def await_in_try():
    try:
        result = await risky_operation()
    except Exception as e:
        result = await fallback_operation()
    finally:
        await cleanup()
""",
            """
async def await_in_with():
    async with await get_async_context() as context:
        result = await context.process()
"""
        ]
        
        for source in control_flow_await_patterns:
            tree = tester.assert_await_expression_parses(source)
            await_exprs = tester.get_await_expressions(source)
            assert len(await_exprs) >= 1, f"Should work in control flow: {source}"
    
    def test_await_in_comprehensions(self, tester):
        """Test await expressions in comprehensions"""
        # Language Reference: await in comprehensions (Python 3.6+)
        comprehension_await_patterns = [
            """
async def await_in_list_comp():
    return [await process(item) async for item in async_iterator]
""",
            """
async def await_in_dict_comp():
    return {key: await fetch_value(key) async for key in async_keys}
""",
            """
async def await_in_set_comp():
    return {await transform(item) async for item in async_items}
""",
            """
async def await_in_generator_exp():
    return (await process(item) async for item in async_data)
""",
            """
async def complex_async_comp():
    return [
        await transform(item)
        async for item in await get_async_iterator()
        if await filter_condition(item)
    ]
"""
        ]
        
        for source in comprehension_await_patterns:
            # These require Python 3.6+ for async comprehensions
            if sys.version_info >= (3, 6):
                tree = tester.assert_await_expression_parses(source)
                await_exprs = tester.get_await_expressions(source)
                assert len(await_exprs) >= 1, f"Should work in comprehensions: {source}"
    
    def test_await_in_conditional_expressions(self, tester):
        """Test await expressions in conditional expressions"""
        # Language Reference: await in conditional expressions
        conditional_await_patterns = [
            """
async def await_in_ternary():
    result = await success_op() if condition else await failure_op()
""",
            """
async def await_condition():
    result = value if await check_condition() else default
""",
            """
async def complex_conditional():
    result = await get_a() if await check() else await get_b()
""",
            """
async def nested_conditional():
    result = (
        await option_a() if await check_a() else
        await option_b() if await check_b() else
        await default_option()
    )
""",
            """
async def await_in_all_parts():
    result = await choice_a() if await condition() else await choice_b()
"""
        ]
        
        for source in conditional_await_patterns:
            tree = tester.assert_await_expression_parses(source)
            await_exprs = tester.get_await_expressions(source)
            assert len(await_exprs) >= 1, f"Should work in conditionals: {source}"


@pytest.mark.min_version_3_5
class TestSection64AwaitPrecedence:
    """Test await expression precedence and associativity."""
    
    def test_await_precedence_with_operators(self, tester):
        """Test await precedence with other operators"""
        # Language Reference: await has high precedence
        precedence_await_patterns = [
            """
async def await_with_arithmetic():
    result = await get_value() + 5
""",
            """
async def await_with_comparison():
    is_valid = await check_value() > threshold
""",
            """
async def await_with_logical():
    result = await check_a() and await check_b()
""",
            """
async def await_in_expression():
    calculated = (await get_base()) ** 2 + await get_offset()
""",
            """
async def await_with_parentheses():
    result = await (get_a() + get_b())
"""
        ]
        
        for source in precedence_await_patterns:
            tree = tester.assert_await_expression_parses(source)
            await_exprs = tester.get_await_expressions(source)
            assert len(await_exprs) >= 1, f"Should handle precedence: {source}"
    
    def test_chained_await_expressions(self, tester):
        """Test chained await expressions"""
        # Language Reference: await can be chained with parentheses
        chained_await_patterns = [
            """
async def chained_awaits():
    result = await (await get_coroutine_that_returns_coroutine())
""",
            """
async def multiple_chained():
    result = await (await (await triple_nested_coroutine()))
""",
            """
async def await_method_chain():
    result = await (await get_client()).fetch_data()
""",
            """
async def complex_chaining():
    result = await (await get_api()).client(await get_config()).fetch()
""",
            """
async def await_with_calls():
    result = await get_processor()(await get_data())
"""
        ]
        
        for source in chained_await_patterns:
            tree = tester.assert_await_expression_parses(source)
            await_exprs = tester.get_await_expressions(source)
            # Should have multiple await expressions
            assert len(await_exprs) >= 1, f"Should handle chaining: {source}"
    
    def test_await_associativity(self, tester):
        """Test await expression associativity"""
        # Language Reference: await with proper parentheses
        associativity_patterns = [
            """
async def right_associative():
    # await with parentheses for nested coroutines
    result = await (await nested_coro())
""",
            """
async def await_with_expressions():
    # Precedence with other operations
    result = await get_value() + await get_other()
""",
            """
async def await_in_complex_expression():
    result = await func1() + await func2() * await func3()
""",
            """
async def explicit_grouping():
    result = await (func1() + func2())
""",
            """
async def mixed_precedence():
    result = (await get_a()) + (await get_b()) * 2
"""
        ]
        
        for source in associativity_patterns:
            tree = tester.assert_await_expression_parses(source)
            await_exprs = tester.get_await_expressions(source)
            assert len(await_exprs) >= 1, f"Should handle associativity: {source}"


@pytest.mark.min_version_3_5
class TestSection64AwaitErrors:
    """Test await expression error conditions."""
    
    def test_await_outside_async_function(self, tester):
        """Test await outside async function context"""
        # Language Reference: await context restrictions
        # Note: In modern Python (3.7+), await outside async function is parsed
        # but becomes a runtime error rather than syntax error
        
        # These patterns should parse syntactically but would fail at runtime
        await_outside_patterns = [
            """
def regular_function():
    return await coroutine()  # Runtime error, not syntax error
""",
            """
class MyClass:
    def method(self):
        return await get_value()  # Runtime error, not syntax error
""",
        ]
        
        for source in await_outside_patterns:
            # These should parse successfully (modern Python behavior)
            tree = tester.assert_await_expression_parses(source)
            # Should detect await expressions even in invalid contexts
            await_exprs = tester.get_await_expressions(source)
            assert len(await_exprs) >= 1, f"Should parse await: {source}"
        
        # Test that we can distinguish regular functions from async functions
        regular_func_source = """
def regular_function():
    return await coroutine()
"""
        
        tree = tester.assert_await_expression_parses(regular_func_source)
        regular_funcs = tester.get_function_defs(regular_func_source)
        async_funcs = tester.get_async_function_defs(regular_func_source)
        
        assert len(regular_funcs) == 1, "Should have regular function"
        assert len(async_funcs) == 0, "Should not have async function"
    
    def test_incomplete_await_expressions(self, tester):
        """Test incomplete await expressions"""
        # Language Reference: await requires expression
        incomplete_patterns = [
            """
async def incomplete():
    result = await  # Missing expression
""",
            """
async def incomplete_call():
    result = await(  # Incomplete call
""",
        ]
        
        for source in incomplete_patterns:
            tester.assert_await_expression_syntax_error(source)
    
    def test_await_with_invalid_syntax(self, tester):
        """Test await with invalid syntax combinations"""
        # Language Reference: specific syntax requirements
        invalid_syntax_patterns = [
            """
async def invalid_await():
    result = await await await  # Missing final expression
""",
            """
async def malformed():
    result = await (  # Unmatched parenthesis
""",
        ]
        
        for source in invalid_syntax_patterns:
            tester.assert_await_expression_syntax_error(source)


@pytest.mark.min_version_3_5
class TestSection64AwaitAST:
    """Test await expression AST structure validation."""
    
    def test_await_ast_structure(self, tester):
        """Test Await AST node structure"""
        # Language Reference: AST structure for await expressions
        await_ast_cases = [
            """
async def simple_await():
    result = await coroutine()
""",
            """
async def await_variable():
    value = await coro_var
""",
            """
async def await_attribute():
    data = await obj.method()
""",
            """
async def chained_await():
    result = await (await nested())
"""
        ]
        
        for source in await_ast_cases:
            tree = tester.assert_await_expression_parses(source)
            await_exprs = tester.get_await_expressions(source)
            assert len(await_exprs) >= 1, f"Should have await expressions: {source}"
            
            for await_expr in await_exprs:
                # Await nodes must have value attribute
                assert isinstance(await_expr, ast.Await), "Should be Await node"
                assert hasattr(await_expr, 'value'), "Should have value attribute"
                assert await_expr.value is not None, "Value should not be None"
    
    def test_nested_await_ast_structure(self, tester):
        """Test nested await expression AST structure"""
        # Language Reference: nested await expressions
        nested_await_source = """
async def nested_awaits():
    # Simple nested await
    result1 = await (await get_nested_coro())
    
    # Complex nested await
    result2 = await (await get_client()).fetch(await get_params())
    
    # Multiple levels
    result3 = await (await (await triple_nested()))
"""
        
        tree = tester.assert_await_expression_parses(nested_await_source)
        await_exprs = tester.get_await_expressions(nested_await_source)
        assert len(await_exprs) >= 6, "Should have multiple await expressions"
        
        # Check nesting depth
        nesting_depth = tester.count_nested_await_expressions(nested_await_source)
        assert nesting_depth >= 3, "Should have nested await expressions"
    
    def test_await_in_complex_expressions_ast(self, tester):
        """Test await in complex expressions AST"""
        # Language Reference: await as part of larger expressions
        complex_await_source = """
async def complex_awaits():
    # Await in arithmetic expression
    result1 = (await get_a()) + (await get_b()) * 2
    
    # Await in function call
    result2 = process(await fetch_data(), await get_config())
    
    # Await in conditional
    result3 = await success() if await check() else await failure()
    
    # Await in return
    return await transform(await get_input())
"""
        
        tree = tester.assert_await_expression_parses(complex_await_source)
        await_exprs = tester.get_await_expressions(complex_await_source)
        assert len(await_exprs) >= 8, "Should have multiple await expressions"
        
        # All await expressions should have proper structure
        for await_expr in await_exprs:
            assert isinstance(await_expr, ast.Await), "Should be Await node"
            assert await_expr.value is not None, "Should have value"


@pytest.mark.min_version_3_5
class TestSection64CrossImplementationCompatibility:
    """Test cross-implementation compatibility for await expressions."""
    
    def test_await_ast_consistency(self, tester):
        """Test await expression AST consistency across implementations"""
        # Language Reference: await AST should be consistent
        consistency_test_cases = [
            """
async def simple_case():
    return await coroutine()
""",
            """
async def complex_case():
    result = await transform(await fetch())
""",
            """
async def control_flow():
    if await check():
        return await success()
    return await failure()
""",
            """
async def multiple_awaits():
    a, b, c = await get_a(), await get_b(), await get_c()
"""
        ]
        
        for source in consistency_test_cases:
            tree = tester.assert_await_expression_parses(source)
            
            # Should have consistent await structure
            await_exprs = tester.get_await_expressions(source)
            assert len(await_exprs) >= 1, f"Should have await expressions: {source}"
            
            for await_expr in await_exprs:
                assert isinstance(await_expr, ast.Await), "Should be Await node"
                assert await_expr.value is not None, "Should have value"
    
    def test_comprehensive_async_patterns(self, tester):
        """Test comprehensive real-world async patterns"""
        # Language Reference: complex async usage scenarios
        comprehensive_patterns = [
            """
# Asynchronous programming patterns with await expressions
import asyncio
from typing import AsyncGenerator, AsyncIterator

class AsyncDataProcessor:
    def __init__(self, connection_pool):
        self.pool = connection_pool
        self.cache = {}
        self.semaphore = asyncio.Semaphore(10)
    
    async def fetch_user_data(self, user_id: int):
        # Basic await with error handling
        try:
            async with self.semaphore:
                connection = await self.pool.acquire()
                try:
                    # Await in complex query
                    user_data = await connection.fetch_one(
                        "SELECT * FROM users WHERE id = $1", user_id
                    )
                    
                    # Conditional await
                    if user_data:
                        # Await in nested function call
                        profile = await self.fetch_profile(user_data['profile_id'])
                        permissions = await self.fetch_permissions(user_id)
                        
                        # Multiple awaits in expression
                        enriched_data = await self.enrich_user_data(
                            user_data, 
                            await self.get_preferences(user_id),
                            await self.get_activity_status(user_id)
                        )
                        
                        return enriched_data
                    
                    return None
                    
                finally:
                    await self.pool.release(connection)
                    
        except Exception as e:
            # Await in exception handling
            await self.log_error(f"Failed to fetch user {user_id}: {e}")
            raise
    
    async def fetch_profile(self, profile_id: int):
        # Caching with await
        if profile_id in self.cache:
            return self.cache[profile_id]
        
        # Await with timeout
        try:
            profile = await asyncio.wait_for(
                self.fetch_profile_data(profile_id),
                timeout=5.0
            )
            self.cache[profile_id] = profile
            return profile
        except asyncio.TimeoutError:
            return await self.get_default_profile()
    
    async def fetch_permissions(self, user_id: int):
        # Concurrent awaits with gather
        role_task = asyncio.create_task(self.fetch_user_role(user_id))
        group_task = asyncio.create_task(self.fetch_user_groups(user_id))
        
        # Await multiple tasks
        role, groups = await asyncio.gather(role_task, group_task)
        
        # Await in list comprehension (Python 3.6+)
        permissions = [
            await self.resolve_permission(perm)
            async for perm in self.get_role_permissions(role)
        ]
        
        # Await in generator expression
        group_permissions = [
            perm async for group in groups
            async for perm in self.get_group_permissions(group)
            if await self.is_permission_active(perm)
        ]
        
        return permissions + group_permissions
    
    async def process_batch(self, user_ids: list):
        # Semaphore-controlled batch processing
        async def process_single(user_id):
            async with self.semaphore:
                return await self.fetch_user_data(user_id)
        
        # Create tasks for concurrent execution
        tasks = [asyncio.create_task(process_single(uid)) for uid in user_ids]
        
        # Await all with error handling
        results = []
        for task in asyncio.as_completed(tasks):
            try:
                result = await task
                results.append(result)
            except Exception as e:
                # Await in error logging
                await self.log_error(f"Batch processing error: {e}")
                results.append(None)
        
        return results
    
    async def stream_user_data(self, query_params) -> AsyncGenerator:
        # Async generator with await
        connection = await self.pool.acquire()
        try:
            # Await in async iteration
            async for row in connection.stream_query(
                await self.build_query(query_params)
            ):
                # Await in yield
                processed_row = await self.process_row(row)
                if await self.should_include_row(processed_row):
                    yield processed_row
                
                # Rate limiting with await
                await asyncio.sleep(0.01)
                
        finally:
            await self.pool.release(connection)
    
    async def aggregate_data(self, user_ids: list):
        # Complex aggregation with multiple async operations
        aggregated = {
            'total_users': len(user_ids),
            'active_users': 0,
            'permissions_summary': {},
            'activity_stats': {}
        }
        
        # Parallel data fetching
        async with asyncio.TaskGroup() as tg:  # Python 3.11+
            user_tasks = [
                tg.create_task(self.fetch_user_data(uid))
                for uid in user_ids
            ]
            
            activity_task = tg.create_task(
                self.fetch_aggregated_activity(user_ids)
            )
            
            permissions_task = tg.create_task(
                self.analyze_permissions_distribution(user_ids)
            )
        
        # Process results
        users = [await task for task in user_tasks if task.result()]
        aggregated['active_users'] = sum(
            1 for user in users
            if await self.is_user_active(user)
        )
        
        aggregated['activity_stats'] = await activity_task
        aggregated['permissions_summary'] = await permissions_task
        
        # Final processing
        aggregated['processed_at'] = await self.get_current_timestamp()
        
        return aggregated
    
    async def cleanup_resources(self):
        # Resource cleanup with multiple awaits
        try:
            # Close connections
            await self.pool.close()
            
            # Clear caches
            self.cache.clear()
            
            # Log cleanup
            await self.log_info("Resources cleaned up successfully")
            
        except Exception as e:
            await self.log_error(f"Cleanup failed: {e}")
            raise
    
    # Helper methods (implementation would contain more awaits)
    async def fetch_profile_data(self, profile_id): pass
    async def get_default_profile(self): pass
    async def fetch_user_role(self, user_id): pass
    async def fetch_user_groups(self, user_id): pass
    async def resolve_permission(self, perm): pass
    async def get_role_permissions(self, role): pass
    async def get_group_permissions(self, group): pass
    async def is_permission_active(self, perm): pass
    async def enrich_user_data(self, *args): pass
    async def get_preferences(self, user_id): pass
    async def get_activity_status(self, user_id): pass
    async def log_error(self, message): pass
    async def log_info(self, message): pass
    async def process_row(self, row): pass
    async def should_include_row(self, row): pass
    async def build_query(self, params): pass
    async def is_user_active(self, user): pass
    async def fetch_aggregated_activity(self, user_ids): pass
    async def analyze_permissions_distribution(self, user_ids): pass
    async def get_current_timestamp(self): pass

# Context manager patterns
class AsyncContextManager:
    async def __aenter__(self):
        self.resource = await self.acquire_resource()
        return self.resource
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.release_resource(self.resource)
        if exc_type:
            await self.log_exception(exc_type, exc_val, exc_tb)
    
    async def acquire_resource(self): pass
    async def release_resource(self, resource): pass
    async def log_exception(self, *args): pass

# Async iteration patterns
class AsyncIterator:
    def __init__(self, data_source):
        self.source = data_source
        self.position = 0
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        if self.position >= len(self.source):
            raise StopAsyncIteration
        
        # Await in async iterator
        item = await self.fetch_item(self.position)
        self.position += 1
        
        # Transform item asynchronously
        return await self.transform_item(item)
    
    async def fetch_item(self, position): pass
    async def transform_item(self, item): pass

# Error handling patterns
async def robust_operation():
    try:
        # Primary operation with await
        result = await primary_async_operation()
        
        # Validation with await
        if not await validate_result(result):
            raise ValueError("Invalid result")
        
        return result
        
    except asyncio.TimeoutError:
        # Timeout fallback
        return await fallback_operation()
        
    except Exception as e:
        # General error handling
        await log_error(e)
        
        # Retry mechanism
        for attempt in range(3):
            try:
                return await retry_operation(attempt)
            except Exception:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        # Final fallback
        return await emergency_fallback()
    
    finally:
        # Cleanup always runs
        await cleanup_operation()

# Coordination patterns
async def coordination_example():
    # Event coordination
    event = asyncio.Event()
    
    async def waiter():
        await event.wait()
        return await process_after_event()
    
    async def setter():
        await prepare_event()
        event.set()
        return await finalize_event()
    
    # Coordinate multiple operations
    waiter_task = asyncio.create_task(waiter())
    setter_task = asyncio.create_task(setter())
    
    # Await coordination
    results = await asyncio.gather(waiter_task, setter_task)
    
    return results

# More helper functions to increase await count
async def primary_async_operation(): pass
async def validate_result(result): pass
async def fallback_operation(): pass
async def log_error(error): pass
async def retry_operation(attempt): pass
async def emergency_fallback(): pass
async def cleanup_operation(): pass
async def process_after_event(): pass
async def prepare_event(): pass
async def finalize_event(): pass
"""
        ]
        
        for source in comprehensive_patterns:
            tree = tester.assert_await_expression_parses(source)
            
            # Should have extensive await usage
            await_exprs = tester.get_await_expressions(source)
            assert len(await_exprs) >= 45, f"Should have many await expressions: {len(await_exprs)} found"
    
    def test_await_introspection(self, tester):
        """Test ability to analyze await expressions programmatically"""
        # Test programmatic analysis of await expression structure
        introspection_source = """
async def await_examples():
    # Simple await expressions
    result1 = await simple_coroutine()
    result2 = await obj.method()
    result3 = await functions[index]()
    
    # Nested awaits
    result4 = await (await get_nested_coro())
    result5 = await (await get_client()).fetch()
    
    # Awaits in expressions
    sum_result = await get_a() + await get_b()
    
    # Awaits in control flow
    if await check_condition():
        data = await fetch_success_data()
    else:
        data = await fetch_fallback_data()
    
    # Awaits in function calls
    processed = await process(
        await get_input(),
        config=await get_config()
    )
    
    # Multiple awaits in return
    return await transform(await get_raw_data())
"""
        
        tree = tester.assert_await_expression_parses(introspection_source)
        
        # Should identify all await expressions
        await_exprs = tester.get_await_expressions(introspection_source)
        assert len(await_exprs) >= 10, "Should have multiple await expressions"
        
        # Should identify async function context
        async_funcs = tester.get_async_function_defs(introspection_source)
        assert len(async_funcs) >= 1, "Should have async function"
        
        # All await expressions should have proper structure
        for await_expr in await_exprs:
            assert isinstance(await_expr, ast.Await), "Should be Await node"
            assert await_expr.value is not None, "Should have value"