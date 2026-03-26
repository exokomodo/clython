"""
Section 2.3: Names (Identifiers and Keywords) - Conformance Test Suite

Tests Python Language Reference Section 2.3 compliance across implementations.
Based on formal specifications for identifier syntax and keyword recognition.

Language Reference requirements tested:
    - Identifier syntax: XID_Start and XID_Continue Unicode categories
    - ASCII identifiers: Letter/underscore start, alphanumeric continuation
    - Unicode identifiers: Non-ASCII character support, normalization rules
    - Keywords: Reserved word recognition, context sensitivity
    - Soft keywords: Contextual keyword behavior (match, case, type, _)
    - Reserved identifier classes: Single/double underscore patterns
    - Case sensitivity: Identifier distinction rules
    - Length limitations: Implementation-specific identifier length handling
    - Invalid identifier patterns: Error condition validation
"""

import ast
import pytest
import sys
import keyword
import unicodedata
from typing import Any


class NamesTester:
    """Helper class for testing names and identifiers conformance.
    
    Uses AST parsing to validate identifier recognition and keyword handling
    while ensuring cross-implementation compatibility.
    """
    
    def assert_identifier_valid(self, identifier: str):
        """Test that identifier is valid and parseable.
        
        Args:
            identifier: Python identifier to test
        """
        try:
            # Test as variable assignment
            source = f"{identifier} = 1"
            tree = ast.parse(source)
            # Should have one assignment with target name
            assert len(tree.body) == 1
            assert isinstance(tree.body[0], ast.Assign)
            return tree
        except SyntaxError as e:
            pytest.fail(f"Valid identifier {identifier!r} failed to parse: {e}")
    
    def assert_identifier_invalid(self, identifier: str):
        """Test that invalid identifier raises SyntaxError.
        
        Args:
            identifier: Invalid identifier that should fail parsing
        """
        with pytest.raises(SyntaxError):
            source = f"{identifier} = 1"
            ast.parse(source)

    def assert_keyword_recognized(self, keyword_name: str):
        """Test that keyword is properly recognized and cannot be used as identifier.
        
        Args:
            keyword_name: Python keyword to test
        """
        with pytest.raises(SyntaxError):
            source = f"{keyword_name} = 1"
            ast.parse(source)

    def assert_source_parses(self, source: str):
        """Test that source code parses successfully.
        
        Args:
            source: Python source code to parse
        """
        try:
            return ast.parse(source)
        except SyntaxError as e:
            pytest.fail(f"Source {source!r} failed to parse: {e}")

    def is_python_keyword(self, name: str) -> bool:
        """Check if name is Python keyword using keyword module.
        
        Args:
            name: Name to check
            
        Returns:
            True if name is keyword, False otherwise
        """
        return keyword.iskeyword(name)

    def is_soft_keyword(self, name: str) -> bool:
        """Check if name is Python soft keyword.
        
        Args:
            name: Name to check
            
        Returns:
            True if name is soft keyword, False otherwise
        """
        # Soft keywords introduced in Python 3.10+
        soft_keywords = {'match', 'case', '_'}
        # Type keyword in Python 3.12+
        if sys.version_info >= (3, 12):
            soft_keywords.add('type')
        return name in soft_keywords


class TestSection23IdentifierSyntax:
    """Test basic identifier syntax rules"""
    
    @pytest.fixture
    def tester(self):
        return NamesTester()

    def test_ascii_identifier_start_characters(self, tester):
        """Test valid ASCII identifier start characters"""
        # Language Reference: identifiers start with letter or underscore
        valid_starts = [
            "a", "z", "A", "Z",          # Letters
            "_", "__", "___",            # Underscores
            "_private", "_internal",     # Underscore prefixed
            "Public", "ClassName",       # Capital letters
            "variable", "function_name"  # Lowercase letters
        ]
        
        for identifier in valid_starts:
            tester.assert_identifier_valid(identifier)

    def test_ascii_identifier_continuation_characters(self, tester):
        """Test valid ASCII identifier continuation characters"""
        # Language Reference: continuation can include digits
        valid_continuations = [
            "var1", "var123", "name_with_123",  # Digits
            "snake_case", "with_underscores",   # Underscores
            "mixedCase", "CamelCase",           # Mixed case
            "a1b2c3", "x_1_y_2",               # Mixed alphanumeric
            "_1", "__2__", "___3___"            # Underscore with digits
        ]
        
        for identifier in valid_continuations:
            tester.assert_identifier_valid(identifier)

    def test_invalid_identifier_start_characters(self, tester):
        """Test invalid identifier start characters"""
        # Language Reference: identifiers cannot start with digits or special chars
        invalid_starts = [
            "1invalid",              # Digits - should be syntax error
            "2name", "9variable",    # More digits
        ]
        
        for identifier in invalid_starts:
            tester.assert_identifier_invalid(identifier)
        
        # Test assignment to expressions (not identifiers) - should fail
        expression_assignments = [
            "-invalid = 1",          # Unary minus expression
            "+name = 1",             # Unary plus expression  
            "invalid-name = 3",      # Subtraction expression
        ]
        
        for source in expression_assignments:
            # These fail because left side is expression, not identifier
            with pytest.raises(SyntaxError):
                ast.parse(source)

    def test_identifier_case_sensitivity(self, tester):
        """Test identifier case sensitivity"""
        # Language Reference: identifiers are case-sensitive
        case_variants = [
            ("name", "Name", "NAME"),
            ("variable", "Variable", "VARIABLE"),
            ("test", "Test", "TEST"),
            ("class", "Class", "CLASS")  # Note: 'class' is keyword, others aren't
        ]
        
        for variants in case_variants:
            for identifier in variants:
                if not tester.is_python_keyword(identifier):
                    tester.assert_identifier_valid(identifier)
                else:
                    tester.assert_keyword_recognized(identifier)

    def test_identifier_length_handling(self, tester):
        """Test identifier length limitations"""
        # Test reasonable length identifiers
        reasonable_lengths = [
            "a",                                    # 1 character
            "ab",                                   # 2 characters
            "short_name",                           # 10 characters
            "medium_length_identifier_name",        # 30 characters
            "very_long_but_reasonable_identifier_name_for_testing",  # 50 characters
        ]
        
        for identifier in reasonable_lengths:
            tester.assert_identifier_valid(identifier)

    def test_empty_identifier(self, tester):
        """Test empty identifier is invalid"""
        # Empty string is not valid identifier
        with pytest.raises(SyntaxError):
            ast.parse(" = 1")  # Missing identifier


class TestSection23UnicodeIdentifiers:
    """Test Unicode identifier support"""
    
    @pytest.fixture
    def tester(self):
        return NamesTester()

    def test_unicode_letter_identifiers(self, tester):
        """Test Unicode letters as identifiers"""
        # Language Reference: identifiers can use Unicode XID_Start/XID_Continue
        unicode_identifiers = [
            "café",          # French accented characters
            "naïve",         # More accented characters
            "münchen",       # German characters
            "москва",        # Cyrillic characters
            "αβγ",           # Greek letters
            "北京",          # Chinese characters
            "العربية",      # Arabic characters (if supported)
            "हिंदी",         # Hindi characters (if supported)
        ]
        
        for identifier in unicode_identifiers:
            try:
                tester.assert_identifier_valid(identifier)
            except UnicodeError:
                # Some systems may not support all Unicode in identifiers
                pytest.skip(f"Unicode identifier {identifier!r} not supported on this system")
            except SyntaxError:
                # Some Unicode characters may not be valid identifier characters
                pytest.skip(f"Unicode identifier {identifier!r} not valid in this Python implementation")

    def test_unicode_combining_characters(self, tester):
        """Test Unicode combining characters in identifiers"""
        # Combining characters should be valid in continuation
        combining_identifiers = [
            "e\u0301",       # e + combining acute accent (é)
            "a\u0300",       # a + combining grave accent (à)
            "n\u0303",       # n + combining tilde (ñ)
        ]
        
        for identifier in combining_identifiers:
            try:
                tester.assert_identifier_valid(identifier)
            except (UnicodeError, SyntaxError):
                pytest.skip(f"Combining character identifier {identifier!r} not supported")

    def test_unicode_normalization(self, tester):
        """Test Unicode normalization in identifiers"""
        # Test that different Unicode normalizations are handled
        # Note: Python may normalize identifiers internally
        test_pairs = [
            ("café", "cafe\u0301"),      # Precomposed vs decomposed
            ("naïve", "nai\u0308ve"),    # Different representations
        ]
        
        for normalized, decomposed in test_pairs:
            try:
                # Both forms should be valid identifiers
                tester.assert_identifier_valid(normalized)
                tester.assert_identifier_valid(decomposed)
            except (UnicodeError, SyntaxError):
                pytest.skip(f"Unicode normalization test {normalized!r}/{decomposed!r} not supported")

    def test_invalid_unicode_identifiers(self, tester):
        """Test invalid Unicode characters in identifiers"""
        # Characters that are not valid in identifiers
        
        # Test space character (definitely invalid in identifiers)
        with pytest.raises(SyntaxError):
            # Space makes this two separate tokens, causing syntax error
            ast.parse("name space = 1")
        
        # Test tab character within identifier (invalid)
        with pytest.raises(SyntaxError):
            ast.parse("name\ttab = 1")
        
        # Note: newline creates separate statements, so we test differently
        # Test embedded null byte (if we can construct it safely)
        try:
            # This should fail in identifier context
            with pytest.raises((SyntaxError, ValueError)):
                exec("name\x00after = 1")
        except (SyntaxError, ValueError):
            # Expected - null bytes not allowed
            pass


class TestSection23Keywords:
    """Test keyword recognition and handling"""
    
    @pytest.fixture
    def tester(self):
        return NamesTester()

    def test_python_keywords_recognized(self, tester):
        """Test that Python keywords are properly recognized"""
        # Language Reference: keywords cannot be used as identifiers
        python_keywords = [
            'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await',
            'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
            'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is',
            'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try',
            'while', 'with', 'yield'
        ]
        
        for kw in python_keywords:
            tester.assert_keyword_recognized(kw)

    def test_keyword_module_consistency(self, tester):
        """Test consistency with keyword module"""
        # keyword.kwlist should match actual keyword behavior
        for kw in keyword.kwlist:
            tester.assert_keyword_recognized(kw)

    def test_keyword_case_sensitivity(self, tester):
        """Test keyword case sensitivity"""
        # Keywords are case-sensitive
        keyword_variations = [
            ("class", "Class", "CLASS"),
            ("def", "Def", "DEF"),
            ("if", "If", "IF"),
            ("for", "For", "FOR"),
            ("None", "none", "NONE"),
            ("True", "true", "TRUE"),
            ("False", "false", "FALSE")
        ]
        
        for variants in keyword_variations:
            actual_keyword = variants[0]
            case_variants = variants[1:]
            
            # Actual keyword should be recognized
            tester.assert_keyword_recognized(actual_keyword)
            
            # Case variants should be valid identifiers
            for variant in case_variants:
                tester.assert_identifier_valid(variant)

    def test_reserved_builtins_as_identifiers(self, tester):
        """Test built-in names can be used as identifiers (but shouldn't)"""
        # Built-ins are not keywords, can be overridden (though inadvisable)
        builtin_names = [
            'int', 'str', 'list', 'dict', 'set', 'tuple',
            'len', 'max', 'min', 'sum', 'abs', 'round',
            'print', 'input', 'open', 'range', 'enumerate'
        ]
        
        for name in builtin_names:
            # Should be valid identifiers (though overriding is bad practice)
            tester.assert_identifier_valid(name)


class TestSection23SoftKeywords:
    """Test soft keyword behavior (Python 3.10+)"""
    
    @pytest.fixture
    def tester(self):
        return NamesTester()

    @pytest.mark.min_version_3_10
    def test_match_case_soft_keywords(self, tester):
        """Test match/case soft keywords in match statements"""
        # Language Reference: match/case are keywords only in match statement context
        
        # Should be valid as regular identifiers
        tester.assert_identifier_valid("match")
        tester.assert_identifier_valid("case")
        
        # Should work in match statement context
        match_source = """
x = 1
match x:
    case 1:
        result = "one"
    case 2:
        result = "two"
"""
        tree = tester.assert_source_parses(match_source)

    @pytest.mark.min_version_3_10
    def test_underscore_wildcard_pattern(self, tester):
        """Test underscore as wildcard in match statements"""
        # _ is soft keyword in match context
        
        # Should be valid as regular identifier
        tester.assert_identifier_valid("_")
        
        # Should work as wildcard in match context
        wildcard_source = """
x = 1
match x:
    case 1:
        result = "one"
    case _:
        result = "other"
"""
        tester.assert_source_parses(wildcard_source)

    @pytest.mark.min_version_3_12
    def test_type_soft_keyword(self, tester):
        """Test type soft keyword behavior (Python 3.12+)"""
        # type is soft keyword in type statement context
        
        # Should be valid as regular identifier
        tester.assert_identifier_valid("type")
        
        # Should work in type statement context (if supported)
        type_source = "type Point = tuple[float, float]"
        tester.assert_source_parses(type_source)


class TestSection23ReservedIdentifierClasses:
    """Test reserved identifier patterns"""
    
    @pytest.fixture
    def tester(self):
        return NamesTester()

    def test_single_underscore_identifiers(self, tester):
        """Test single underscore identifier patterns"""
        # Single underscore patterns are valid but have conventional meanings
        single_underscore_patterns = [
            "_",                    # Throwaway variable
            "_private",             # Private by convention
            "_internal_function",   # Internal use
            "_1", "_a", "_test"     # Various single underscore prefixes
        ]
        
        for identifier in single_underscore_patterns:
            tester.assert_identifier_valid(identifier)

    def test_double_underscore_identifiers(self, tester):
        """Test double underscore identifier patterns"""
        # Double underscore patterns trigger name mangling in classes
        double_underscore_patterns = [
            "__private",            # Name mangled in classes
            "__internal_method",    # Name mangled in classes  
            "__attr",               # Name mangled in classes
            "__1", "__a"           # Various double underscore prefixes
        ]
        
        for identifier in double_underscore_patterns:
            tester.assert_identifier_valid(identifier)

    def test_dunder_method_identifiers(self, tester):
        """Test double underscore method name patterns"""
        # Dunder (double underscore) methods are reserved for special methods
        dunder_methods = [
            "__init__", "__del__", "__str__", "__repr__",
            "__len__", "__getitem__", "__setitem__", "__delitem__",
            "__call__", "__enter__", "__exit__", "__add__", "__sub__",
            "__eq__", "__lt__", "__hash__", "__bool__", "__iter__"
        ]
        
        for method_name in dunder_methods:
            tester.assert_identifier_valid(method_name)

    def test_reserved_future_patterns(self, tester):
        """Test patterns reserved for future use"""
        # Patterns that might be reserved in future Python versions
        
        # Currently these are valid identifiers
        potentially_reserved = [
            "__future_feature__",
            "__new_method__",
            "__reserved__"
        ]
        
        for identifier in potentially_reserved:
            # Should be valid now, but might change in future
            tester.assert_identifier_valid(identifier)


class TestSection23IdentifierContexts:
    """Test identifiers in different syntactic contexts"""
    
    @pytest.fixture
    def tester(self):
        return NamesTester()

    def test_identifiers_in_function_definitions(self, tester):
        """Test identifiers as function and parameter names"""
        # Function names and parameter names follow identifier rules
        function_sources = [
            "def simple_function(): pass",
            "def function_with_params(param1, param2): pass",
            "def unicode_function_café(naïve_param): pass",
            "def _private_function(_private_param): pass",
            "def __special_method__(self, __private_attr): pass"
        ]
        
        for source in function_sources:
            try:
                tester.assert_source_parses(source)
            except (UnicodeError, SyntaxError):
                if 'café' in source or 'naïve' in source:
                    pytest.skip("Unicode identifiers not supported")
                else:
                    raise

    def test_identifiers_in_class_definitions(self, tester):
        """Test identifiers as class and attribute names"""
        # Class names follow identifier rules
        class_sources = [
            "class SimpleClass: pass",
            "class CamelCaseClass: pass", 
            "class snake_case_class: pass",
            "class _PrivateClass: pass",
            "class __SpecialClass: pass"
        ]
        
        for source in class_sources:
            tester.assert_source_parses(source)

    def test_identifiers_in_import_statements(self, tester):
        """Test identifiers in import statements"""
        # Module names and aliases follow identifier rules
        import_sources = [
            "import os",
            "import sys as system",
            "from collections import defaultdict",
            "from typing import List as ListType",
            "import package.module as pm"
        ]
        
        for source in import_sources:
            try:
                tester.assert_source_parses(source)
            except ImportError:
                # Import may fail, but parsing should succeed
                pass

    def test_identifiers_in_assignments(self, tester):
        """Test identifiers as assignment targets"""
        # Assignment targets must be valid identifiers
        assignment_sources = [
            "variable = 1",
            "snake_case_var = 2", 
            "CamelCaseVar = 3",
            "_private_var = 4",
            "__special_var = 5"
        ]
        
        for source in assignment_sources:
            tester.assert_source_parses(source)


class TestSection23ErrorConditions:
    """Test error conditions for invalid names"""
    
    @pytest.fixture
    def tester(self):
        return NamesTester()

    def test_keyword_assignment_errors(self, tester):
        """Test assignment to keywords raises SyntaxError"""
        # Cannot assign to keywords
        keyword_assignments = [
            "if = 1",
            "for = 2", 
            "def = 3",
            "class = 4",
            "None = 5",
            "True = 6",
            "False = 7"
        ]
        
        for source in keyword_assignments:
            with pytest.raises(SyntaxError):
                ast.parse(source)

    def test_invalid_identifier_syntax_errors(self, tester):
        """Test invalid identifier syntax raises SyntaxError"""
        # Test clear invalid identifier cases
        invalid_sources = [
            "1invalid = 1",          # Starts with digit
            "invalid@name = 6",      # Contains @ character  
        ]
        
        for source in invalid_sources:
            with pytest.raises(SyntaxError):
                ast.parse(source)
        
        # Test assignment to binary expressions (which are not valid assignment targets)
        expression_assignment_sources = [
            "invalid-name = 3",      # Subtraction expression (a-b is not assignable)
            "invalid+name = 4",      # Addition expression (a+b is not assignable)
        ]
        
        for source in expression_assignment_sources:
            with pytest.raises(SyntaxError):
                ast.parse(source)

    def test_unicode_error_conditions(self, tester):
        """Test Unicode error conditions"""
        # Invalid Unicode in identifiers should raise appropriate errors
        
        # Test null byte (definitely invalid)
        with pytest.raises((SyntaxError, ValueError)):
            # Python doesn't allow null bytes in source code
            ast.parse("name\x00 = 1")
        
        # Test other control characters
        try:
            with pytest.raises(SyntaxError):
                ast.parse("name\x01 = 2")  # Control character SOH
        except ValueError:
            # Some control characters may raise ValueError for null bytes
            pass


class TestSection23CrossImplementationCompatibility:
    """Test identifier handling across Python implementations"""
    
    @pytest.fixture
    def tester(self):
        return NamesTester()

    def test_comprehensive_identifier_patterns(self, tester):
        """Test complex identifier pattern combinations"""
        # Complex patterns combining various identifier rules
        complex_patterns = [
            # Mixed case with numbers and underscores
            "complexVariable_123_Name",
            "_private_method_with_123_numbers",
            "__special_dunder_method_456__",
            "CamelCase_With_Snake_case_789",
            
            # Unicode mixed with ASCII (if supported)
            "mixed_café_variable",
            "naïve_implementation_123"
        ]
        
        for identifier in complex_patterns:
            try:
                tester.assert_identifier_valid(identifier)
            except (UnicodeError, SyntaxError):
                if any(char in identifier for char in ['é', 'ï']):
                    pytest.skip(f"Unicode identifier {identifier!r} not supported")
                else:
                    raise

    def test_edge_case_identifiers(self, tester):
        """Test edge cases in identifier handling"""
        # Edge cases that might expose implementation differences
        edge_cases = [
            "_",                    # Single underscore
            "__",                   # Double underscore
            "___",                  # Triple underscore
            "_a_",                  # Underscore sandwich
            "__a__",                # Dunder pattern
            "a_",                   # Trailing underscore
            "a1b2c3d4e5",          # Many digits
        ]
        
        for identifier in edge_cases:
            tester.assert_identifier_valid(identifier)

    def test_identifier_specification_compliance(self, tester):
        """Test compliance with identifier specifications"""
        # Specific Language Reference compliance tests
        compliance_tests = [
            # Test: "identifiers are case-sensitive"
            ("Name", "name", "NAME"),
            
            # Test: "keywords cannot be used as identifiers"
            ("class", "def", "if", "for"),
            
            # Test: "identifiers start with letter or underscore"
            ("valid", "_valid", "__valid"),
            
            # Test: "continuation includes letters, digits, underscores"
            ("var123", "name_with_underscore", "mixedCase123")
        ]
        
        # Test case sensitivity
        for variants in [compliance_tests[0]]:
            for identifier in variants:
                tester.assert_identifier_valid(identifier)
        
        # Test keywords
        for keyword_name in compliance_tests[1]:
            tester.assert_keyword_recognized(keyword_name)
        
        # Test valid starts
        for identifier in compliance_tests[2]:
            tester.assert_identifier_valid(identifier)
        
        # Test valid continuations
        for identifier in compliance_tests[3]:
            tester.assert_identifier_valid(identifier)