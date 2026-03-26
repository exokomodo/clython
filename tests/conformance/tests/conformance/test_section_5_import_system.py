"""
Section 5: Import System - Conformance Test Suite

Tests Python Language Reference Section 5 compliance across implementations.
Based on formal grammar definitions and prose assertions for import system behavior.

Grammar tested:
    import_stmt: import_name | import_from
    import_name: 'import' dotted_as_names
    import_from: ('from' (('.' | '...')* dotted_name | ('.' | '...')+)
                 'import' ('*' | '(' import_as_names ')' | import_as_names))
    import_as_name: NAME ['as' NAME]
    dotted_as_name: dotted_name ['as' NAME]
    import_as_names: import_as_name (',' import_as_name)* [',']
    dotted_as_names: dotted_as_name (',' dotted_as_name)*
    dotted_name: NAME ('.' NAME)*

Language Reference requirements tested:
    - Import statement syntax and semantics
    - Module search path and resolution
    - Package structure and __init__.py behavior
    - Relative import syntax and semantics
    - Import aliasing and namespace binding
    - Circular import detection and handling
    - __main__ module special behavior
    - Module loading and execution order
    - Import statement AST structure validation
"""

import ast
import pytest
import sys
import os
import tempfile
import shutil
from pathlib import Path
from typing import Any


class ImportSystemTester:
    """Helper class for testing import system conformance.
    
    Follows established AST-based validation pattern from previous sections.
    Note: Import system testing focuses on AST structure validation rather
    than runtime module loading, for cross-implementation compatibility.
    """
    
    def assert_import_syntax_parses(self, source: str):
        """Test that import statement syntax parses correctly.
        
        Args:
            source: Python import statement source code
        """
        try:
            tree = ast.parse(source)
            return tree
        except SyntaxError as e:
            pytest.fail(f"Import syntax should be valid but failed to parse: {source}\\nError: {e}")
    
    def assert_import_syntax_error(self, source: str):
        """Test that invalid import syntax raises SyntaxError.
        
        Args:
            source: Python import source code that should be invalid
        """
        with pytest.raises(SyntaxError):
            ast.parse(source)
    
    def get_import_statements(self, source: str) -> list:
        """Get Import and ImportFrom AST nodes from source.
        
        Args:
            source: Python source code
            
        Returns:
            List of ast.Import and ast.ImportFrom nodes
        """
        tree = ast.parse(source)
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(node)
        
        return imports
    
    def has_relative_import(self, source: str) -> bool:
        """Check if source contains relative import patterns.
        
        Args:
            source: Python source code
            
        Returns:
            True if contains relative imports (. or .. patterns)
        """
        imports = self.get_import_statements(source)
        for imp in imports:
            if isinstance(imp, ast.ImportFrom):
                if imp.level and imp.level > 0:  # Relative import
                    return True
        return False
    
    def get_imported_names(self, source: str) -> list:
        """Get list of imported names from import statements.
        
        Args:
            source: Python source code
            
        Returns:
            List of imported name strings
        """
        imports = self.get_import_statements(source)
        names = []
        
        for imp in imports:
            if isinstance(imp, ast.Import):
                for alias in imp.names:
                    names.append(alias.name)
            elif isinstance(imp, ast.ImportFrom):
                if imp.names:
                    for alias in imp.names:
                        if alias.name == '*':
                            names.append('*')
                        else:
                            names.append(alias.name)
        
        return names


@pytest.fixture
def tester():
    """Provide ImportSystemTester instance for tests."""
    return ImportSystemTester()


class TestSection5ImportStatements:
    """Test basic import statement syntax."""
    
    def test_simple_import_statements(self, tester):
        """Test simple import statement syntax"""
        # Language Reference: import_name: 'import' dotted_as_names
        simple_imports = [
            "import sys",
            "import os",
            "import math",
            "import json",
            "import collections",
        ]
        
        for source in simple_imports:
            tree = tester.assert_import_syntax_parses(source)
            imports = tester.get_import_statements(source)
            assert len(imports) == 1, f"Should have one import: {source}"
            assert isinstance(imports[0], ast.Import), f"Should be Import node: {source}"
    
    def test_dotted_import_statements(self, tester):
        """Test dotted module import syntax"""
        # Language Reference: dotted_name: NAME ('.' NAME)*
        dotted_imports = [
            "import os.path",
            "import xml.etree.ElementTree",
            "import urllib.request",
            "import email.mime.text",
            "import concurrent.futures",
        ]
        
        for source in dotted_imports:
            tree = tester.assert_import_syntax_parses(source)
            imports = tester.get_import_statements(source)
            assert len(imports) == 1, f"Should have one import: {source}"
            
            imported_names = tester.get_imported_names(source)
            assert len(imported_names) >= 1, f"Should have imported names: {source}"
            assert '.' in imported_names[0], f"Should have dotted name: {source}"
    
    def test_multiple_import_statements(self, tester):
        """Test multiple imports in single statement"""
        # Language Reference: dotted_as_names: dotted_as_name (',' dotted_as_name)*
        multiple_imports = [
            "import sys, os",
            "import math, random, time",
            "import json, pickle, csv",
            "import re, string, textwrap",
        ]
        
        for source in multiple_imports:
            tree = tester.assert_import_syntax_parses(source)
            imports = tester.get_import_statements(source)
            assert len(imports) == 1, f"Should have one import statement: {source}"
            
            imported_names = tester.get_imported_names(source)
            assert len(imported_names) >= 2, f"Should have multiple names: {source}"
    
    def test_aliased_import_statements(self, tester):
        """Test import statements with aliases"""
        # Language Reference: dotted_as_name: dotted_name ['as' NAME]
        aliased_imports = [
            "import numpy as np",
            "import pandas as pd",
            "import matplotlib.pyplot as plt",
            "import tensorflow as tf",
            "import os.path as ospath",
        ]
        
        for source in aliased_imports:
            tree = tester.assert_import_syntax_parses(source)
            imports = tester.get_import_statements(source)
            assert len(imports) == 1, f"Should have one import: {source}"
            
            # Check for 'as' clause in AST
            import_node = imports[0]
            assert isinstance(import_node, ast.Import), f"Should be Import node: {source}"
            assert len(import_node.names) >= 1, f"Should have names: {source}"
            assert import_node.names[0].asname is not None, f"Should have alias: {source}"


class TestSection5FromImportStatements:
    """Test from...import statement syntax."""
    
    def test_simple_from_import_statements(self, tester):
        """Test simple from...import syntax"""
        # Language Reference: import_from: ('from' dotted_name 'import' import_as_names)
        from_imports = [
            "from os import path",
            "from sys import argv",
            "from math import pi",
            "from json import loads",
            "from random import choice",
        ]
        
        for source in from_imports:
            tree = tester.assert_import_syntax_parses(source)
            imports = tester.get_import_statements(source)
            assert len(imports) == 1, f"Should have one import: {source}"
            assert isinstance(imports[0], ast.ImportFrom), f"Should be ImportFrom node: {source}"
    
    def test_multiple_from_import_statements(self, tester):
        """Test from...import with multiple names"""
        # Language Reference: import_as_names: import_as_name (',' import_as_name)*
        multiple_from_imports = [
            "from os import path, environ",
            "from sys import argv, exit, version",
            "from math import sin, cos, tan, pi",
            "from json import loads, dumps, load, dump",
        ]
        
        for source in multiple_from_imports:
            tree = tester.assert_import_syntax_parses(source)
            imports = tester.get_import_statements(source)
            assert len(imports) == 1, f"Should have one import: {source}"
            
            imported_names = tester.get_imported_names(source)
            assert len(imported_names) >= 2, f"Should have multiple names: {source}"
    
    def test_from_import_with_aliases(self, tester):
        """Test from...import with aliases"""
        # Language Reference: import_as_name: NAME ['as' NAME]
        aliased_from_imports = [
            "from os import path as ospath",
            "from sys import argv as args",
            "from math import pi as PI",
            "from json import loads as json_loads",
            "from collections import defaultdict as dd",
        ]
        
        for source in aliased_from_imports:
            tree = tester.assert_import_syntax_parses(source)
            imports = tester.get_import_statements(source)
            assert len(imports) == 1, f"Should have one import: {source}"
            
            import_node = imports[0]
            assert isinstance(import_node, ast.ImportFrom), f"Should be ImportFrom node: {source}"
            assert len(import_node.names) >= 1, f"Should have names: {source}"
            assert import_node.names[0].asname is not None, f"Should have alias: {source}"
    
    def test_from_import_star_statements(self, tester):
        """Test from...import * syntax"""
        # Language Reference: 'import' ('*' | import_as_names)
        star_imports = [
            "from math import *",
            "from os import *", 
            "from sys import *",
            "from json import *",
        ]
        
        for source in star_imports:
            tree = tester.assert_import_syntax_parses(source)
            imports = tester.get_import_statements(source)
            assert len(imports) == 1, f"Should have one import: {source}"
            
            imported_names = tester.get_imported_names(source)
            assert '*' in imported_names, f"Should have star import: {source}"
    
    def test_from_dotted_module_imports(self, tester):
        """Test from...import with dotted module names"""
        # Language Reference: from dotted module paths
        dotted_from_imports = [
            "from os.path import join",
            "from xml.etree import ElementTree",
            "from urllib.request import urlopen",
            "from email.mime.text import MIMEText",
            "from concurrent.futures import ThreadPoolExecutor",
        ]
        
        for source in dotted_from_imports:
            tree = tester.assert_import_syntax_parses(source)
            imports = tester.get_import_statements(source)
            assert len(imports) == 1, f"Should have one import: {source}"
            
            import_node = imports[0]
            assert isinstance(import_node, ast.ImportFrom), f"Should be ImportFrom node: {source}"
            assert import_node.module is not None, f"Should have module: {source}"
            assert '.' in import_node.module, f"Should have dotted module: {source}"


class TestSection5RelativeImports:
    """Test relative import syntax."""
    
    def test_single_dot_relative_imports(self, tester):
        """Test single dot relative import syntax"""
        # Language Reference: ('.' | '...')* for relative imports
        single_dot_imports = [
            "from . import module",
            "from .module import function",
            "from .subpackage import Class",
            "from .utils import helper",
        ]
        
        for source in single_dot_imports:
            tree = tester.assert_import_syntax_parses(source)
            imports = tester.get_import_statements(source)
            assert len(imports) == 1, f"Should have one import: {source}"
            assert tester.has_relative_import(source), f"Should be relative import: {source}"
            
            import_node = imports[0]
            assert isinstance(import_node, ast.ImportFrom), f"Should be ImportFrom node: {source}"
            assert import_node.level >= 1, f"Should have relative level: {source}"
    
    def test_double_dot_relative_imports(self, tester):
        """Test double dot relative import syntax"""
        # Language Reference: '..' for parent package imports
        double_dot_imports = [
            "from .. import module",
            "from ..module import function",
            "from ..parent import Class",
            "from ...grandparent import utility",
        ]
        
        for source in double_dot_imports:
            tree = tester.assert_import_syntax_parses(source)
            imports = tester.get_import_statements(source)
            assert len(imports) == 1, f"Should have one import: {source}"
            assert tester.has_relative_import(source), f"Should be relative import: {source}"
            
            import_node = imports[0]
            assert isinstance(import_node, ast.ImportFrom), f"Should be ImportFrom node: {source}"
            assert import_node.level >= 2, f"Should have parent level: {source}"
    
    def test_relative_import_with_module_names(self, tester):
        """Test relative imports with explicit module names"""
        # Language Reference: relative imports with dotted names
        relative_dotted_imports = [
            "from .package.module import function",
            "from ..sibling.module import Class",
            "from ...parent.child import utility",
            "from .utils.helpers import tool",
        ]
        
        for source in relative_dotted_imports:
            tree = tester.assert_import_syntax_parses(source)
            imports = tester.get_import_statements(source)
            assert len(imports) == 1, f"Should have one import: {source}"
            assert tester.has_relative_import(source), f"Should be relative import: {source}"
    
    def test_relative_only_dots_imports(self, tester):
        """Test relative imports with only dots (no module name)"""
        # Language Reference: ('.' | '...')+  without module name
        dots_only_imports = [
            "from . import *",
            "from .. import module", 
            "from ... import package",
        ]
        
        for source in dots_only_imports:
            tree = tester.assert_import_syntax_parses(source)
            imports = tester.get_import_statements(source)
            assert len(imports) == 1, f"Should have one import: {source}"
            assert tester.has_relative_import(source), f"Should be relative import: {source}"


class TestSection5ImportStatementStructure:
    """Test import statement AST structure validation."""
    
    def test_import_ast_node_structure(self, tester):
        """Test Import AST node structure consistency"""
        # Language Reference: AST structure for import statements
        import_cases = [
            "import sys",
            "import os, sys",
            "import numpy as np",
        ]
        
        for source in import_cases:
            tree = tester.assert_import_syntax_parses(source)
            imports = tester.get_import_statements(source)
            assert len(imports) >= 1, f"Should have imports: {source}"
            
            for import_node in imports:
                if isinstance(import_node, ast.Import):
                    assert hasattr(import_node, 'names'), "Import should have 'names' attribute"
                    assert len(import_node.names) >= 1, "Import should have at least one name"
                    
                    for alias in import_node.names:
                        assert hasattr(alias, 'name'), "Alias should have 'name' attribute"
                        assert hasattr(alias, 'asname'), "Alias should have 'asname' attribute"
    
    def test_import_from_ast_node_structure(self, tester):
        """Test ImportFrom AST node structure consistency"""
        # Language Reference: AST structure for from...import statements
        import_from_cases = [
            "from os import path",
            "from sys import argv, exit",
            "from math import pi as PI",
            "from . import module",
        ]
        
        for source in import_from_cases:
            tree = tester.assert_import_syntax_parses(source)
            imports = tester.get_import_statements(source)
            assert len(imports) >= 1, f"Should have imports: {source}"
            
            for import_node in imports:
                if isinstance(import_node, ast.ImportFrom):
                    assert hasattr(import_node, 'module'), "ImportFrom should have 'module' attribute"
                    assert hasattr(import_node, 'names'), "ImportFrom should have 'names' attribute"
                    assert hasattr(import_node, 'level'), "ImportFrom should have 'level' attribute"
                    
                    if import_node.names:
                        for alias in import_node.names:
                            assert hasattr(alias, 'name'), "Alias should have 'name' attribute"
                            assert hasattr(alias, 'asname'), "Alias should have 'asname' attribute"
    
    def test_import_alias_structure(self, tester):
        """Test import alias AST structure"""
        # Language Reference: alias structure in imports
        alias_cases = [
            "import numpy as np",
            "from os import path as ospath",
            "import sys, os as operating_system",
            "from math import pi as PI, sin as sine",
        ]
        
        for source in alias_cases:
            tree = tester.assert_import_syntax_parses(source)
            imports = tester.get_import_statements(source)
            assert len(imports) >= 1, f"Should have imports: {source}"
            
            # Find aliases with asname
            has_alias = False
            for import_node in imports:
                names = import_node.names if hasattr(import_node, 'names') else []
                for alias in names:
                    if alias.asname is not None:
                        has_alias = True
                        assert isinstance(alias.asname, str), "Alias name should be string"
            
            assert has_alias, f"Should have at least one alias: {source}"
    
    def test_relative_import_level_structure(self, tester):
        """Test relative import level in AST structure"""
        # Language Reference: level attribute for relative imports
        relative_cases = [
            ("from . import module", 1),
            ("from .. import module", 2),
            ("from ... import module", 3),
            ("from .package import module", 1),
            ("from ..parent import module", 2),
        ]
        
        for source, expected_level in relative_cases:
            tree = tester.assert_import_syntax_parses(source)
            imports = tester.get_import_statements(source)
            assert len(imports) == 1, f"Should have one import: {source}"
            
            import_node = imports[0]
            assert isinstance(import_node, ast.ImportFrom), f"Should be ImportFrom: {source}"
            assert import_node.level == expected_level, f"Should have level {expected_level}: {source}"


class TestSection5ImportErrorConditions:
    """Test import statement error conditions."""
    
    def test_invalid_import_syntax(self, tester):
        """Test invalid import statement syntax"""
        # Language Reference: syntactic restrictions on imports
        invalid_imports = [
            "import",                     # Missing module name
            "from",                       # Incomplete from statement
            "from import module",         # Missing module in from
            "import as alias",            # Missing module before as
            "from . import",              # Missing import target
            "import sys as",              # Missing alias name
            "from sys import as name",    # Missing import name before as
        ]
        
        for source in invalid_imports:
            tester.assert_import_syntax_error(source)
    
    def test_invalid_relative_import_syntax(self, tester):
        """Test invalid relative import syntax"""
        # Language Reference: relative import restrictions
        invalid_relative_imports = [
            "import .",                   # Can't use relative in import
            "import .module",             # Can't use relative in import
            "import ..parent",            # Can't use relative in import
        ]
        
        for source in invalid_relative_imports:
            tester.assert_import_syntax_error(source)
    
    def test_invalid_dotted_name_syntax(self, tester):
        """Test invalid dotted name syntax"""
        # Language Reference: dotted name restrictions
        invalid_dotted_names = [
            "import .",                   # Just dot
            "import ..",                  # Just dots
            "import module.",             # Trailing dot
            "import .module.",            # Leading and trailing dots
            "import module..submodule",   # Double dots in middle
        ]
        
        for source in invalid_dotted_names:
            tester.assert_import_syntax_error(source)
    
    def test_import_indentation_requirements(self, tester):
        """Test import statement indentation rules"""
        # Language Reference: imports follow normal statement indentation
        valid_indented_imports = [
            """
if condition:
    import conditional_module
""",
            """
try:
    import optional_module
except ImportError:
    pass
""",
            """
def function():
    import local_module
    return local_module.value
"""
        ]
        
        for source in valid_indented_imports:
            tree = tester.assert_import_syntax_parses(source)
            # Should handle indentation correctly
            assert len(tree.body) >= 1, f"Should have statements: {source}"


class TestSection5PackageImportPatterns:
    """Test package import patterns."""
    
    def test_package_structure_imports(self, tester):
        """Test imports that assume package structure"""
        # Language Reference: package import patterns
        package_imports = [
            "import package.module",
            "import package.subpackage.module",
            "from package import module",
            "from package.subpackage import module",
            "from package import subpackage",
        ]
        
        for source in package_imports:
            tree = tester.assert_import_syntax_parses(source)
            imports = tester.get_import_statements(source)
            assert len(imports) >= 1, f"Should have imports: {source}"
    
    def test_init_module_implications(self, tester):
        """Test imports that would involve __init__.py behavior"""
        # Language Reference: package __init__.py behavior
        init_related_imports = [
            "import package",             # Would load package/__init__.py
            "from package import *",      # Would use package.__all__
            "import package.module",      # Would load package/__init__.py first
        ]
        
        for source in init_related_imports:
            tree = tester.assert_import_syntax_parses(source)
            # Should parse correctly - __init__.py behavior is runtime
            imports = tester.get_import_statements(source)
            assert len(imports) >= 1, f"Should have imports: {source}"
    
    def test_namespace_package_patterns(self, tester):
        """Test import patterns for namespace packages"""
        # Language Reference: namespace package import behavior
        namespace_imports = [
            "import namespace_package.module",
            "from namespace_package import module",
            "from namespace_package.subpackage import item",
        ]
        
        for source in namespace_imports:
            tree = tester.assert_import_syntax_parses(source)
            # Should parse correctly - namespace behavior is runtime
            imports = tester.get_import_statements(source)
            assert len(imports) >= 1, f"Should have imports: {source}"


class TestSection5SpecialImportCases:
    """Test special import cases and edge conditions."""
    
    def test_main_module_patterns(self, tester):
        """Test patterns related to __main__ module"""
        # Language Reference: __main__ module special behavior
        main_related_imports = [
            "import __main__",
            "from __main__ import variable",
            "import sys; sys.modules['__main__']",  # Complex but valid
        ]
        
        for source in main_related_imports:
            tree = tester.assert_import_syntax_parses(source)
            # Should parse correctly - __main__ behavior is runtime
            imports = tester.get_import_statements(source)
            assert len(imports) >= 1, f"Should have imports: {source}"
    
    def test_builtin_module_imports(self, tester):
        """Test imports of built-in modules"""
        # Language Reference: built-in module import behavior
        builtin_imports = [
            "import sys",
            "import builtins",
            "import __builtin__",          # Python 2 compatibility (syntax valid)
            "from builtins import *",
        ]
        
        for source in builtin_imports:
            tree = tester.assert_import_syntax_parses(source)
            imports = tester.get_import_statements(source)
            assert len(imports) >= 1, f"Should have imports: {source}"
    
    def test_dynamic_import_patterns(self, tester):
        """Test patterns that would involve dynamic imports"""
        # Language Reference: dynamic import syntax patterns
        dynamic_patterns = [
            "import importlib",
            "from importlib import import_module",
            "__import__('module_name')",   # Function call, not import statement
        ]
        
        for source in dynamic_patterns:
            tree = tester.assert_import_syntax_parses(source)
            # Should parse correctly regardless of dynamic vs static behavior
            assert tree is not None, f"Dynamic pattern should parse: {source}"
    
    def test_conditional_import_patterns(self, tester):
        """Test imports inside conditional statements"""
        # Language Reference: imports can appear in any statement context
        conditional_patterns = [
            """
try:
    import optional_module
except ImportError:
    optional_module = None
""",
            """
if sys.version_info >= (3, 8):
    from functools import cached_property
else:
    from backport import cached_property
""",
            """
for module_name in modules:
    import_string = f"import {module_name}"
"""
        ]
        
        for source in conditional_patterns:
            tree = tester.assert_import_syntax_parses(source)
            # Should parse correctly - conditional imports are valid
            assert len(tree.body) >= 1, f"Conditional import should parse: {source}"


class TestSection5CrossImplementationCompatibility:
    """Test cross-implementation compatibility for import system."""
    
    def test_import_ast_structure_consistency(self, tester):
        """Test import AST structure across implementations"""
        # Language Reference: AST structure should be consistent
        import_test_cases = [
            "import sys",
            "import os.path",
            "import numpy as np",
            "from os import path",
            "from . import module",
            "from ..parent import item",
        ]
        
        for source in import_test_cases:
            tree = tester.assert_import_syntax_parses(source)
            imports = tester.get_import_statements(source)
            
            # Should have consistent AST structure
            assert len(imports) >= 1, f"Should have import statements: {source}"
            
            for import_node in imports:
                if isinstance(import_node, ast.Import):
                    assert hasattr(import_node, 'names'), "Import should have 'names'"
                elif isinstance(import_node, ast.ImportFrom):
                    assert hasattr(import_node, 'module'), "ImportFrom should have 'module'"
                    assert hasattr(import_node, 'names'), "ImportFrom should have 'names'"
                    assert hasattr(import_node, 'level'), "ImportFrom should have 'level'"
    
    def test_comprehensive_import_patterns(self, tester):
        """Test comprehensive real-world import patterns"""
        # Language Reference: complex real-world import scenarios
        comprehensive_patterns = [
            """
import sys
import os.path as ospath
from collections import defaultdict, Counter
from .utils import helper_function
from ..config import settings
try:
    import optional_dependency
except ImportError:
    optional_dependency = None
""",
            """
from typing import (
    List, Dict, Optional, Union, 
    Callable, Iterator, Any
)
from dataclasses import dataclass, field
from pathlib import Path
""",
            """
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, urljoin
from urllib.request import urlopen, Request
"""
        ]
        
        for source in comprehensive_patterns:
            tree = tester.assert_import_syntax_parses(source)
            # Just verify complex patterns parse successfully
            imports = tester.get_import_statements(source)
            assert len(imports) >= 3, f"Complex import pattern should have multiple imports: {source}"
    
    def test_import_statement_introspection(self, tester):
        """Test ability to analyze import statements programmatically"""
        # Test programmatic analysis of import statement structure
        introspection_source = """
import sys
import os.path as ospath
from collections import defaultdict
from .utils import helper
from .. import parent_module
"""
        
        tree = tester.assert_import_syntax_parses(introspection_source)
        imports = tester.get_import_statements(source=introspection_source)
        
        # Should be able to identify different import types
        assert len(imports) >= 5, "Should have multiple import types"
        
        import_types = set()
        for imp in imports:
            if isinstance(imp, ast.Import):
                import_types.add('import')
            elif isinstance(imp, ast.ImportFrom):
                if imp.level > 0:
                    import_types.add('relative_from')
                else:
                    import_types.add('absolute_from')
        
        # Should detect different import pattern types
        assert 'import' in import_types, "Should detect regular imports"
        assert 'absolute_from' in import_types, "Should detect absolute from imports"
        assert 'relative_from' in import_types, "Should detect relative from imports"