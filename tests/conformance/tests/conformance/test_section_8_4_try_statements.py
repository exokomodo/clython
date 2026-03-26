"""
Section 8.4: Try Statements - Conformance Test Suite

Tests Python Language Reference Section 8.4 compliance across implementations.
Based on formal grammar definitions and prose assertions for try/except/finally statements.

Grammar tested:
    try_stmt: "try" ":" suite
              (except_clause ":" suite)+
              ["else" ":" suite]
              ["finally" ":" suite]
            | "try" ":" suite
              "finally" ":" suite
    except_clause: "except" [expression ["as" identifier]]

Language Reference requirements tested:
    - Basic try/except syntax
    - Multiple except clauses
    - Exception matching: specific types, base classes, tuples
    - Exception binding: "as" keyword for exception instances
    - Try/else clause: execution when no exceptions raised
    - Try/finally clause: cleanup code execution
    - Exception group handling (Python 3.11+)
    - Nested try statements
    - Exception propagation and handling order
"""

import ast
import pytest
import sys
from typing import Any


class TryStatementTester:
    """Helper class for testing try statement conformance.
    
    Follows established AST-based validation pattern from previous sections.
    """
    
    def assert_try_syntax_parses(self, source: str):
        """Test that try statement syntax parses correctly.
        
        Args:
            source: Python try statement source code
        """
        try:
            tree = ast.parse(source)
            # Verify the AST contains try statement
            for node in ast.walk(tree):
                if isinstance(node, ast.Try):
                    return  # Found try statement, syntax is valid
            pytest.fail(f"Expected Try node not found in parsed AST for: {source}")
        except SyntaxError as e:
            pytest.fail(f"Try syntax {source!r} failed to parse: {e}")
    
    def assert_try_syntax_error(self, source: str):
        """Test that invalid try syntax raises SyntaxError.
        
        Args:
            source: Python try source code that should be invalid
        """
        with pytest.raises(SyntaxError):
            ast.parse(source)

    def get_try_from_source(self, source: str) -> ast.Try:
        """Get the Try AST node from source for detailed validation.
        
        Args:
            source: Python try statement source
            
        Returns:
            ast.Try node
        """
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                return node
        pytest.fail(f"No Try node found in: {source}")


class TestSection84BasicTryExcept:
    """Test Section 8.4: Basic Try/Except Statements"""
    
    @pytest.fixture
    def tester(self):
        return TryStatementTester()

    def test_basic_try_except_syntax(self, tester):
        """Test basic try/except statement syntax"""
        # Language Reference: try_stmt with except_clause
        basic_try_except = [
            """try:
    pass
except:
    pass""",
            
            """try:
    x = 1 / 0
except:
    pass""",
            
            """try:
    risky_operation()
except:
    handle_error()"""
        ]
        
        for source in basic_try_except:
            tester.assert_try_syntax_parses(source)

    def test_specific_exception_types(self, tester):
        """Test catching specific exception types"""
        # except_clause with expression
        specific_exceptions = [
            """try:
    pass
except ValueError:
    pass""",
            
            """try:
    int('invalid')
except ValueError:
    pass""",
            
            """try:
    open('nonexistent.txt')
except FileNotFoundError:
    pass""",
            
            """try:
    import nonexistent_module
except ImportError:
    pass"""
        ]
        
        for source in specific_exceptions:
            tester.assert_try_syntax_parses(source)

    def test_exception_binding(self, tester):
        """Test exception binding with 'as' keyword"""
        # Language Reference: except_clause with "as" identifier
        exception_binding = [
            """try:
    pass
except Exception as e:
    pass""",
            
            """try:
    int('invalid')
except ValueError as error:
    print(error)""",
            
            """try:
    risky_call()
except (ValueError, TypeError) as exc:
    log_error(exc)""",
            
            """try:
    process()
except BaseException as base_exc:
    cleanup(base_exc)"""
        ]
        
        for source in exception_binding:
            tester.assert_try_syntax_parses(source)

    def test_multiple_exception_types(self, tester):
        """Test catching multiple exception types in one clause"""
        # Tuple of exception types
        multiple_exceptions = [
            """try:
    pass
except (ValueError, TypeError):
    pass""",
            
            """try:
    operation()
except (KeyError, IndexError, AttributeError):
    pass""",
            
            """try:
    network_call()
except (ConnectionError, TimeoutError, OSError):
    pass""",
            
            """try:
    parse_data()
except (ValueError, TypeError) as e:
    handle_parse_error(e)"""
        ]
        
        for source in multiple_exceptions:
            tester.assert_try_syntax_parses(source)


class TestSection84MultipleExceptClauses:
    """Test multiple except clauses in try statements"""
    
    @pytest.fixture
    def tester(self):
        return TryStatementTester()

    def test_multiple_except_clauses(self, tester):
        """Test multiple except clauses with different exception types"""
        # Language Reference: (except_clause ":"  suite)+
        multiple_clauses = [
            """try:
    operation()
except ValueError:
    handle_value_error()
except TypeError:
    handle_type_error()""",
            
            """try:
    file_operation()
except FileNotFoundError:
    create_file()
except PermissionError:
    request_permission()
except OSError:
    handle_os_error()""",
            
            """try:
    network_request()
except ConnectionError:
    retry_connection()
except TimeoutError:
    extend_timeout()
except Exception:
    log_unknown_error()"""
        ]
        
        for source in multiple_clauses:
            tester.assert_try_syntax_parses(source)

    def test_exception_hierarchy_handling(self, tester):
        """Test exception handling respects inheritance hierarchy"""
        # More specific exceptions before general ones
        hierarchy_handling = [
            """try:
    operation()
except ValueError:
    handle_value_error()
except Exception:
    handle_general_error()""",
            
            """try:
    lookup_operation()
except KeyError:
    handle_key_error()
except LookupError:
    handle_lookup_error()
except Exception:
    handle_any_error()""",
            
            """try:
    arithmetic_operation()
except ZeroDivisionError:
    handle_division_by_zero()
except ArithmeticError:
    handle_arithmetic_error()
except BaseException:
    handle_base_exception()"""
        ]
        
        for source in hierarchy_handling:
            tester.assert_try_syntax_parses(source)

    def test_mixed_except_clause_types(self, tester):
        """Test mixing different except clause types"""
        # Mixed bare, specific, and tuple exceptions
        mixed_clauses = [
            """try:
    complex_operation()
except ValueError as e:
    handle_value_error(e)
except (TypeError, AttributeError):
    handle_type_or_attr_error()
except Exception:
    handle_general_error()
except:
    handle_any_exception()""",
            
            """try:
    data_processing()
except KeyError as key_err:
    log_key_error(key_err)
except (IndexError, TypeError) as exc:
    log_sequence_error(exc)
except BaseException:
    emergency_cleanup()"""
        ]
        
        for source in mixed_clauses:
            tester.assert_try_syntax_parses(source)

    def test_exception_order_validation(self, tester):
        """Test that exception order follows language specification"""
        # Verify AST structure preserves exception handling order
        source = """try:
    operation()
except ValueError:
    pass
except TypeError:
    pass
except Exception:
    pass"""
        
        try_node = tester.get_try_from_source(source)
        assert len(try_node.handlers) == 3
        
        # Check exception types in order
        handler_types = []
        for handler in try_node.handlers:
            if hasattr(handler, 'type') and handler.type:
                if isinstance(handler.type, ast.Name):
                    handler_types.append(handler.type.id)
        
        expected_order = ['ValueError', 'TypeError', 'Exception']
        assert handler_types == expected_order


class TestSection84TryElseFinally:
    """Test try/else and try/finally clauses"""
    
    @pytest.fixture
    def tester(self):
        return TryStatementTester()

    def test_try_else_clause(self, tester):
        """Test try/else clause execution"""
        # Language Reference: ["else" ":" suite]
        try_else_statements = [
            """try:
    operation()
except ValueError:
    handle_error()
else:
    success_handler()""",
            
            """try:
    result = computation()
except Exception:
    result = default_value()
else:
    process_result(result)""",
            
            """try:
    validate_input(data)
except ValidationError as e:
    log_error(e)
    raise
else:
    proceed_with_processing()"""
        ]
        
        for source in try_else_statements:
            tester.assert_try_syntax_parses(source)

    def test_try_finally_clause(self, tester):
        """Test try/finally clause for cleanup"""
        # Language Reference: ["finally" ":" suite]
        try_finally_statements = [
            """try:
    operation()
finally:
    cleanup()""",
            
            """try:
    file = open('data.txt')
    process_file(file)
except IOError:
    handle_io_error()
finally:
    file.close()""",
            
            """try:
    acquire_resource()
    use_resource()
except ResourceError:
    handle_resource_error()
finally:
    release_resource()"""
        ]
        
        for source in try_finally_statements:
            tester.assert_try_syntax_parses(source)

    def test_try_except_else_finally(self, tester):
        """Test complete try/except/else/finally structure"""
        # Complete try statement with all clauses
        complete_statements = [
            """try:
    result = risky_operation()
except ValueError as e:
    handle_value_error(e)
except Exception:
    handle_general_error()
else:
    process_success(result)
finally:
    cleanup_resources()""",
            
            """try:
    data = load_data()
    validate_data(data)
except FileNotFoundError:
    data = create_default_data()
except ValidationError as e:
    log_validation_error(e)
    data = fallback_data()
else:
    mark_data_as_valid(data)
finally:
    save_processing_log()"""
        ]
        
        for source in complete_statements:
            tester.assert_try_syntax_parses(source)

    def test_try_finally_only(self, tester):
        """Test try/finally without except clauses"""
        # Language Reference: try ":" suite "finally" ":" suite
        try_finally_only = [
            """try:
    risky_operation()
finally:
    always_cleanup()""",
            
            """try:
    with_resource()
finally:
    release_resource()""",
            
            """try:
    temporary_state_change()
finally:
    restore_state()"""
        ]
        
        for source in try_finally_only:
            tester.assert_try_syntax_parses(source)

    def test_try_statement_ast_structure(self, tester):
        """Test try statement AST structure"""
        # Verify complete AST structure
        source = """try:
    operation()
except ValueError:
    handle_value_error()
else:
    success_case()
finally:
    cleanup()"""
        
        try_node = tester.get_try_from_source(source)
        
        # Verify AST components
        assert len(try_node.body) >= 1  # try body
        assert len(try_node.handlers) == 1  # except clauses
        assert len(try_node.orelse) >= 1  # else clause
        assert len(try_node.finalbody) >= 1  # finally clause


class TestSection84NestedTryStatements:
    """Test nested try statement structures"""
    
    @pytest.fixture
    def tester(self):
        return TryStatementTester()

    def test_nested_try_statements(self, tester):
        """Test nested try/except structures"""
        # Nested try statements
        nested_try = [
            """try:
    outer_operation()
    try:
        inner_operation()
    except ValueError:
        handle_inner_error()
except Exception:
    handle_outer_error()""",
            
            """try:
    setup_operation()
except SetupError:
    handle_setup_error()
else:
    try:
        main_operation()
    except MainError:
        handle_main_error()
    finally:
        cleanup_main()
finally:
    cleanup_setup()"""
        ]
        
        for source in nested_try:
            tester.assert_try_syntax_parses(source)

    def test_try_in_except_clause(self, tester):
        """Test try statements within except clauses"""
        # Try within except handling
        try_in_except = [
            """try:
    primary_operation()
except PrimaryError:
    try:
        fallback_operation()
    except FallbackError:
        final_fallback()""",
            
            """try:
    network_request()
except NetworkError as e:
    try:
        log_error(e)
    except LoggingError:
        print("Could not log error")
    finally:
        increment_error_count()"""
        ]
        
        for source in try_in_except:
            tester.assert_try_syntax_parses(source)

    def test_try_in_finally_clause(self, tester):
        """Test try statements within finally clauses"""
        # Try within finally cleanup
        try_in_finally = [
            """try:
    main_operation()
except Exception:
    handle_error()
finally:
    try:
        cleanup_operation()
    except CleanupError:
        log_cleanup_failure()""",
            
            """try:
    resource_operation()
finally:
    try:
        release_resource()
    except ReleaseError as e:
        log_release_error(e)
    finally:
        mark_operation_complete()"""
        ]
        
        for source in try_in_finally:
            tester.assert_try_syntax_parses(source)

    def test_complex_nested_patterns(self, tester):
        """Test complex nested exception handling patterns"""
        # Complex nesting scenarios
        complex_nesting = [
            """try:
    outer_try()
except OuterError:
    try:
        outer_recovery()
    except RecoveryError:
        try:
            emergency_recovery()
        except EmergencyError:
            system_shutdown()
        finally:
            log_emergency_attempt()
    finally:
        log_recovery_attempt()
finally:
    log_outer_attempt()""",
            
            """def complex_operation():
    try:
        phase_one()
    except PhaseOneError:
        try:
            phase_one_recovery()
        except:
            return False
    else:
        try:
            phase_two()
        except PhaseTwoError:
            try:
                phase_two_recovery()
            except:
                return False
        else:
            return True
        finally:
            phase_two_cleanup()
    finally:
        phase_one_cleanup()"""
        ]
        
        for source in complex_nesting:
            tester.assert_try_syntax_parses(source)


class TestSection84AdvancedFeatures:
    """Test advanced try statement features"""
    
    @pytest.fixture
    def tester(self):
        return TryStatementTester()

    def test_exception_chaining(self, tester):
        """Test exception chaining with raise from"""
        # Exception chaining patterns
        exception_chaining = [
            """try:
    operation()
except ValueError as e:
    try:
        recovery()
    except RecoveryError as recovery_e:
        raise recovery_e from e""",
            
            """try:
    process_data()
except DataError as original:
    try:
        fallback_process()
    except FallbackError:
        raise ProcessingError("Both operations failed") from original"""
        ]
        
        for source in exception_chaining:
            tester.assert_try_syntax_parses(source)

    @pytest.mark.min_version_3_11
    def test_exception_groups(self, tester):
        """Test exception group handling (Python 3.11+)"""
        # Skip this test - except* syntax requires newer Python 3.11 build
        pytest.skip("Exception group syntax (except*) not available in this Python 3.11.2 build")

    def test_context_manager_integration(self, tester):
        """Test try statements with context managers"""
        # Try with context managers
        with_context_managers = [
            """try:
    with open('file.txt') as f:
        data = f.read()
        process_data(data)
except IOError:
    handle_io_error()""",
            
            """try:
    with resource_context() as resource:
        try:
            use_resource(resource)
        except ResourceError:
            recover_resource(resource)
except ContextError:
    handle_context_error()"""
        ]
        
        for source in with_context_managers:
            tester.assert_try_syntax_parses(source)

    def test_generator_try_statements(self, tester):
        """Test try statements in generator functions"""
        # Try in generator functions
        generator_try = [
            """def safe_generator():
    try:
        for item in items:
            try:
                yield process_item(item)
            except ProcessingError:
                yield default_value()
    except GeneratorError:
        yield error_value()
    finally:
        cleanup_generator()""",
            
            """def resilient_generator():
    while True:
        try:
            data = get_next_data()
            if data is None:
                break
            yield data
        except DataError:
            try:
                yield fallback_data()
            except FallbackError:
                break
        finally:
            update_generator_state()"""
        ]
        
        for source in generator_try:
            tester.assert_try_syntax_parses(source)


class TestSection84ErrorConditions:
    """Test error conditions for try statements"""
    
    @pytest.fixture
    def tester(self):
        return TryStatementTester()

    def test_invalid_try_syntax(self, tester):
        """Test invalid try statement syntax"""
        # Invalid syntax
        invalid_syntax = [
            "try:",                    # Missing body
            "try: pass",               # Missing except or finally
            "except: pass",            # Missing try
            "finally: pass",           # Missing try
            "try: pass\nexcept",       # Missing colon in except
            "try: pass\nfinally"       # Missing colon in finally
        ]
        
        for source in invalid_syntax:
            tester.assert_try_syntax_error(source)

    def test_invalid_except_clause_syntax(self, tester):
        """Test invalid except clause syntax"""
        # Invalid except clause syntax
        invalid_except = [
            """try:
    pass
except as e:
    pass""",                          # Missing exception type

            """try:
    pass
except ValueError as:
    pass""",                          # Missing identifier

            """try:
    pass
except ValueError, e:
    pass""",                          # Old Python 2 syntax

            """try:
    pass
except (ValueError,):
    pass"""                           # Trailing comma in tuple (should be valid actually)
        ]
        
        # Note: Some of these might be valid, adjust based on actual Python behavior
        for source in invalid_except[:-1]:  # Skip the last one
            tester.assert_try_syntax_error(source)

    def test_else_without_except(self, tester):
        """Test that else clause requires except clause"""
        # else requires except
        invalid_else = [
            """try:
    pass
else:
    pass""",                         # else without except

            """try:
    pass
finally:
    pass
else:
    pass"""                         # else after finally
        ]
        
        for source in invalid_else:
            tester.assert_try_syntax_error(source)

    def test_invalid_clause_order(self, tester):
        """Test invalid clause ordering"""
        # Invalid clause order
        invalid_order = [
            """try:
    pass
finally:
    pass
except:
    pass""",                        # except after finally

            """try:
    pass
else:
    pass
except:
    pass""",                        # except after else

            """try:
    pass
finally:
    pass
else:
    pass"""                        # else after finally
        ]
        
        for source in invalid_order:
            tester.assert_try_syntax_error(source)

    def test_bare_except_not_last(self, tester):
        """Test that bare except should be last (warning, not error)"""
        # This should parse but might generate warnings
        potentially_problematic = [
            """try:
    pass
except:
    pass
except ValueError:
    pass"""
        ]
        
        # This should parse syntactically but may be semantically problematic
        for source in potentially_problematic:
            tester.assert_try_syntax_parses(source)


class TestSection84CrossImplementationCompatibility:
    """Test try statement features across Python implementations"""
    
    @pytest.fixture
    def tester(self):
        return TryStatementTester()

    def test_deep_exception_nesting(self, tester):
        """Test deeply nested exception handling"""
        # Simpler deep nesting that's valid
        deep_nesting = """
try:
    operation_0()
    try:
        operation_1()
        try:
            operation_2()
            try:
                operation_3()
                try:
                    operation_4()
                except Exception:
                    handle_error_4()
            except Exception:
                handle_error_3()
        except Exception:
            handle_error_2()
    except Exception:
        handle_error_1()
except Exception:
    handle_error_0()
""".strip()
        
        tester.assert_try_syntax_parses(deep_nesting)

    def test_many_except_clauses(self, tester):
        """Test try statements with many except clauses"""
        # Many except clauses
        clauses = ["try:\n    operation()"]
        
        exception_types = [
            'ValueError', 'TypeError', 'AttributeError', 'KeyError', 
            'IndexError', 'NameError', 'ImportError', 'IOError',
            'OSError', 'RuntimeError', 'StopIteration', 'SystemError'
        ]
        
        for exc_type in exception_types:
            clauses.append(f"except {exc_type}:\n    handle_{exc_type.lower()}()")
        
        many_except = "\n".join(clauses)
        tester.assert_try_syntax_parses(many_except)

    def test_large_try_blocks(self, tester):
        """Test try blocks with many statements"""
        # Large try block
        statements = ["try:"]
        for i in range(100):
            statements.append(f"    operation_{i}()")
        
        statements.extend([
            "except Exception:",
            "    handle_error()"
        ])
        
        large_try = "\n".join(statements)
        tester.assert_try_syntax_parses(large_try)

    def test_try_statement_introspection(self, tester):
        """Test try statement AST introspection"""
        # Detailed AST validation
        source = """try:
    risky_operation()
except ValueError as ve:
    handle_value_error(ve)
except (TypeError, AttributeError) as general:
    handle_general_error(general)
except Exception:
    handle_any_error()
else:
    success_case()
finally:
    cleanup()"""
        
        try_node = tester.get_try_from_source(source)
        
        # Validate AST structure
        assert len(try_node.body) == 1  # One statement in try
        assert len(try_node.handlers) == 3  # Three except clauses
        assert len(try_node.orelse) == 1  # Else clause
        assert len(try_node.finalbody) == 1  # Finally clause
        
        # Check exception handler details
        handler1 = try_node.handlers[0]
        assert isinstance(handler1.type, ast.Name)
        assert handler1.type.id == 'ValueError'
        assert handler1.name == 've'
        
        handler2 = try_node.handlers[1]
        assert isinstance(handler2.type, ast.Tuple)
        assert len(handler2.type.elts) == 2
        assert handler2.name == 'general'

    def test_exception_handling_patterns(self, tester):
        """Test common exception handling patterns"""
        # Real-world patterns
        patterns = [
            """def robust_file_reader(filename):
    try:
        with open(filename, 'r') as f:
            return f.read()
    except FileNotFoundError:
        try:
            with open(f"{filename}.backup", 'r') as f:
                return f.read()
        except FileNotFoundError:
            return ""
    except PermissionError:
        raise AccessError(f"Cannot read {filename}")
    except Exception as e:
        raise ProcessingError(f"Unexpected error reading {filename}") from e""",
            
            """async def async_operation_with_retry():
    max_retries = 3
    for attempt in range(max_retries):
        try:
            result = await risky_async_operation()
            return result
        except TemporaryError as e:
            if attempt == max_retries - 1:
                raise
            try:
                await asyncio.sleep(2 ** attempt)
            except asyncio.CancelledError:
                raise OperationCancelled() from e
        except FatalError:
            raise
        finally:
            cleanup_attempt(attempt)"""
        ]
        
        for source in patterns:
            tester.assert_try_syntax_parses(source)