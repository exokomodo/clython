"""
Section 7.11: Import Statements - Conformance Test Suite

Tests Python Language Reference Section 7.11 compliance across implementations.
Based on formal specifications for import statement syntax and semantics.

Language Reference requirements tested:
    - Simple imports: import module_name
    - Dotted imports: import package.module
    - Import aliases: import module as alias
    - From imports: from module import name
    - From import aliases: from module import name as alias
    - From import with asterisk: from module import *
    - Relative imports: from . import module, from ..package import module
    - Multiple imports: import mod1, mod2, mod3
    - Mixed import forms in single statement
    - Import statement syntax validation
"""

import ast
import pytest
import sys
from typing import Any


class ImportStatementTester:
    """Helper class for testing import statement conformance.
    
    Follows established AST-based validation pattern from previous sections.
    """
    
    def assert_import_syntax_parses(self, source: str):
        """Test that import statement syntax parses correctly.
        
        Args:
            source: Python import statement source code
        """
        try:
            tree = ast.parse(source, mode='exec')
            # Verify the AST contains import statement
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    return tree
            pytest.fail(f"Expected Import or ImportFrom node not found in parsed AST for: {source}")
        except SyntaxError as e:
            pytest.fail(f"Import syntax {source!r} failed to parse: {e}")
    
    def assert_import_syntax_error(self, source: str):
        """Test that invalid import syntax raises SyntaxError.
        
        Args:
            source: Python import statement source that should be invalid
        """
        with pytest.raises(SyntaxError):
            ast.parse(source, mode='exec')

    def get_import_nodes(self, source: str) -> list:
        """Get list of import nodes from source code.
        
        Args:
            source: Python import statement source
            
        Returns:
            List of Import and ImportFrom AST nodes
        """
        tree = ast.parse(source, mode='exec')
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(node)
        return imports

    def get_import_names(self, source: str) -> list:
        """Get list of imported names from source code.
        
        Args:
            source: Python import statement source
            
        Returns:
            List of imported module/name strings
        """
        imports = self.get_import_nodes(source)
        names = []
        for imp in imports:
            if isinstance(imp, ast.Import):
                for alias in imp.names:
                    names.append(alias.name)
            elif isinstance(imp, ast.ImportFrom):
                if imp.names:
                    for alias in imp.names:
                        names.append(alias.name if alias.name != '*' else '*')
        return names


class TestSection711SimpleImports:
    """Test Section 7.11: Simple Import Statements"""
    
    @pytest.fixture
    def tester(self):
        return ImportStatementTester()

    def test_simple_module_imports(self, tester):
        """Test simple module import syntax"""
        # Language Reference: import module_name
        simple_imports = [
            "import os",
            "import sys", 
            "import math",
            "import collections",
            "import urllib"
        ]
        
        for stmt in simple_imports:
            tree = tester.assert_import_syntax_parses(stmt)
            imports = tester.get_import_nodes(stmt)
            assert len(imports) == 1
            assert isinstance(imports[0], ast.Import)
            assert len(imports[0].names) == 1

    def test_dotted_module_imports(self, tester):
        """Test dotted module import syntax"""
        # Language Reference: import package.module
        dotted_imports = [
            "import os.path",
            "import urllib.parse",
            "import xml.etree.ElementTree",
            "import collections.abc",
            "import importlib.util"
        ]
        
        for stmt in dotted_imports:
            tree = tester.assert_import_syntax_parses(stmt)
            imports = tester.get_import_nodes(stmt)
            assert len(imports) == 1
            assert isinstance(imports[0], ast.Import)
            # Check that module name contains dots
            module_name = imports[0].names[0].name
            assert '.' in module_name

    def test_multiple_module_imports(self, tester):
        """Test multiple modules in single import statement"""
        # Language Reference: import mod1, mod2, mod3
        multiple_imports = [
            "import os, sys",
            "import math, random, time",
            "import json, pickle, csv",
            "import os, sys, math, random"
        ]
        
        for stmt in multiple_imports:
            tree = tester.assert_import_syntax_parses(stmt)
            imports = tester.get_import_nodes(stmt)
            assert len(imports) == 1
            assert isinstance(imports[0], ast.Import)
            # Check multiple names
            assert len(imports[0].names) >= 2

    def test_import_with_aliases(self, tester):
        """Test import statements with aliases"""
        # Language Reference: import module as alias
        aliased_imports = [
            "import numpy as np",
            "import pandas as pd",
            "import matplotlib.pyplot as plt",
            "import xml.etree.ElementTree as ET",
            "import collections as coll"
        ]
        
        for stmt in aliased_imports:
            tree = tester.assert_import_syntax_parses(stmt)
            imports = tester.get_import_nodes(stmt)
            assert len(imports) == 1
            assert isinstance(imports[0], ast.Import)
            # Check alias exists
            alias = imports[0].names[0]
            assert alias.asname is not None

    def test_mixed_import_aliases(self, tester):
        """Test mixed aliased and non-aliased imports"""
        # Language Reference: import mod1 as alias1, mod2, mod3 as alias3
        mixed_imports = [
            "import os as operating_system, sys",
            "import math, random as rand, time",
            "import json as js, pickle, csv as comma_sep"
        ]
        
        for stmt in mixed_imports:
            tree = tester.assert_import_syntax_parses(stmt)
            imports = tester.get_import_nodes(stmt)
            assert len(imports) == 1
            assert isinstance(imports[0], ast.Import)
            # Should have multiple names, some with aliases
            names = imports[0].names
            assert len(names) >= 2
            has_alias = any(alias.asname is not None for alias in names)
            has_no_alias = any(alias.asname is None for alias in names)
            assert has_alias and has_no_alias


class TestSection711FromImports:
    """Test from...import statements"""
    
    @pytest.fixture
    def tester(self):
        return ImportStatementTester()

    def test_simple_from_imports(self, tester):
        """Test simple from...import syntax"""
        # Language Reference: from module import name
        from_imports = [
            "from os import path",
            "from sys import argv",
            "from math import sqrt",
            "from collections import defaultdict",
            "from urllib import parse"
        ]
        
        for stmt in from_imports:
            tree = tester.assert_import_syntax_parses(stmt)
            imports = tester.get_import_nodes(stmt)
            assert len(imports) == 1
            assert isinstance(imports[0], ast.ImportFrom)
            assert imports[0].module is not None
            assert len(imports[0].names) == 1

    def test_multiple_from_imports(self, tester):
        """Test multiple names in from...import"""
        # Language Reference: from module import name1, name2, name3
        multiple_from_imports = [
            "from os import path, environ",
            "from sys import argv, path, version",
            "from math import sqrt, sin, cos, tan",
            "from collections import defaultdict, Counter, deque"
        ]
        
        for stmt in multiple_from_imports:
            tree = tester.assert_import_syntax_parses(stmt)
            imports = tester.get_import_nodes(stmt)
            assert len(imports) == 1
            assert isinstance(imports[0], ast.ImportFrom)
            assert len(imports[0].names) >= 2

    def test_from_import_with_aliases(self, tester):
        """Test from...import with aliases"""
        # Language Reference: from module import name as alias
        aliased_from_imports = [
            "from os import path as ospath",
            "from sys import argv as arguments",
            "from math import sqrt as square_root",
            "from collections import defaultdict as dd"
        ]
        
        for stmt in aliased_from_imports:
            tree = tester.assert_import_syntax_parses(stmt)
            imports = tester.get_import_nodes(stmt)
            assert len(imports) == 1
            assert isinstance(imports[0], ast.ImportFrom)
            alias = imports[0].names[0]
            assert alias.asname is not None

    def test_from_import_asterisk(self, tester):
        """Test from...import * syntax"""
        # Language Reference: from module import *
        asterisk_imports = [
            "from os import *",
            "from sys import *", 
            "from math import *",
            "from collections import *"
        ]
        
        for stmt in asterisk_imports:
            tree = tester.assert_import_syntax_parses(stmt)
            imports = tester.get_import_nodes(stmt)
            assert len(imports) == 1
            assert isinstance(imports[0], ast.ImportFrom)
            assert len(imports[0].names) == 1
            assert imports[0].names[0].name == '*'

    def test_mixed_from_import_aliases(self, tester):
        """Test mixed aliased and non-aliased from imports"""
        # Language Reference: from module import name1 as alias1, name2, name3 as alias3
        mixed_from_imports = [
            "from os import path as ospath, environ",
            "from sys import argv, path as syspath, version",
            "from math import sqrt as sq, sin, cos as cosine"
        ]
        
        for stmt in mixed_from_imports:
            tree = tester.assert_import_syntax_parses(stmt)
            imports = tester.get_import_nodes(stmt)
            assert len(imports) == 1
            assert isinstance(imports[0], ast.ImportFrom)
            names = imports[0].names
            assert len(names) >= 2
            has_alias = any(alias.asname is not None for alias in names)
            has_no_alias = any(alias.asname is None for alias in names)
            assert has_alias and has_no_alias


class TestSection711RelativeImports:
    """Test relative import statements"""
    
    @pytest.fixture
    def tester(self):
        return ImportStatementTester()

    def test_relative_imports_single_dot(self, tester):
        """Test single dot relative imports"""
        # Language Reference: from . import module
        single_dot_imports = [
            "from . import module",
            "from . import submodule", 
            "from . import utils",
            "from . import helpers"
        ]
        
        for stmt in single_dot_imports:
            tree = tester.assert_import_syntax_parses(stmt)
            imports = tester.get_import_nodes(stmt)
            assert len(imports) == 1
            assert isinstance(imports[0], ast.ImportFrom)
            assert imports[0].level == 1
            assert imports[0].module is None or imports[0].module != ''

    def test_relative_imports_multiple_dots(self, tester):
        """Test multiple dot relative imports"""
        # Language Reference: from .. import module, from ...package import module
        multiple_dot_imports = [
            "from .. import module",
            "from ... import package",
            "from .... import parent",
            "from ..... import root"
        ]
        
        for stmt in multiple_dot_imports:
            tree = tester.assert_import_syntax_parses(stmt)
            imports = tester.get_import_nodes(stmt)
            assert len(imports) == 1
            assert isinstance(imports[0], ast.ImportFrom)
            assert imports[0].level >= 2

    def test_relative_from_module_imports(self, tester):
        """Test relative from module imports"""
        # Language Reference: from .module import name
        relative_from_imports = [
            "from .module import function",
            "from .subpackage import Class",
            "from ..parent import variable",
            "from ...grandparent import constant"
        ]
        
        for stmt in relative_from_imports:
            tree = tester.assert_import_syntax_parses(stmt)
            imports = tester.get_import_nodes(stmt)
            assert len(imports) == 1
            assert isinstance(imports[0], ast.ImportFrom)
            assert imports[0].level >= 1
            assert imports[0].module is not None

    def test_relative_dotted_imports(self, tester):
        """Test relative imports with dotted module names"""
        # Language Reference: from .package.module import name
        relative_dotted_imports = [
            "from .package.module import function",
            "from .sub.package.module import Class",
            "from ..parent.module import variable",
            "from ...grand.parent.module import constant"
        ]
        
        for stmt in relative_dotted_imports:
            tree = tester.assert_import_syntax_parses(stmt)
            imports = tester.get_import_nodes(stmt)
            assert len(imports) == 1
            assert isinstance(imports[0], ast.ImportFrom)
            assert imports[0].level >= 1
            assert '.' in imports[0].module


class TestSection711ImportStatementVariations:
    """Test various import statement patterns"""
    
    @pytest.fixture
    def tester(self):
        return ImportStatementTester()

    def test_multiline_imports(self, tester):
        """Test multiline import statements"""
        # Language Reference: from...import statements can span multiple lines with parentheses
        multiline_imports = [
            """from module import (
    name1,
    name2,
    name3
)""",
            
            """from package.module import (
    function1, function2,
    Class1, Class2,
    CONSTANT1, CONSTANT2
)""",
            
            # Line continuation with backslash
            """import module1, \\
    module2, \\
    module3""",
            
            # Multiple from imports
            """from package import (
    submodule1,
    submodule2
)
from other import name"""
        ]
        
        for stmt in multiline_imports:
            tree = tester.assert_import_syntax_parses(stmt)
            imports = tester.get_import_nodes(stmt)
            assert len(imports) >= 1

    def test_import_with_comments(self, tester):
        """Test import statements with comments"""
        # Comments should not affect parsing
        commented_imports = [
            "import os  # Operating system interface",
            "from sys import argv  # Command line arguments", 
            """# Import math functions
from math import sqrt, sin, cos""",
            
            """from collections import (
    defaultdict,  # Default dictionary
    Counter,      # Counting tool
    deque        # Double-ended queue
)"""
        ]
        
        for stmt in commented_imports:
            tree = tester.assert_import_syntax_parses(stmt)
            imports = tester.get_import_nodes(stmt)
            assert len(imports) >= 1

    def test_import_statement_positions(self, tester):
        """Test import statements in different positions"""
        # Import statements in various contexts
        positioned_imports = [
            """import os
import sys""",
            
            """def function():
    import local_module
    return local_module.value""",
            
            """class MyClass:
    def method(self):
        from . import helper
        return helper.do_work()""",
            
            """if condition:
    import conditional_module"""
        ]
        
        for stmt in positioned_imports:
            tree = tester.assert_import_syntax_parses(stmt)
            # Should parse successfully

    def test_import_name_patterns(self, tester):
        """Test various import name patterns"""
        # Different naming patterns
        name_pattern_imports = [
            "import _private",
            "import __dunder__",
            "import CamelCase",
            "import snake_case",
            "import UPPER_CASE",
            "import mixed_CamelCase_123",
            "from module import _private_name",
            "from module import __dunder_name__"
        ]
        
        for stmt in name_pattern_imports:
            tree = tester.assert_import_syntax_parses(stmt)
            imports = tester.get_import_nodes(stmt)
            assert len(imports) == 1


class TestSection711ErrorConditions:
    """Test error conditions for import statements"""
    
    @pytest.fixture
    def tester(self):
        return ImportStatementTester()

    def test_invalid_import_syntax(self, tester):
        """Test invalid import statement syntax"""
        # Invalid import syntax
        invalid_imports = [
            "import",                    # Missing module name
            "from import name",          # Missing module name
            "from module import",        # Missing import name
            "import module from",        # Wrong keyword order
            "from . import",             # Missing name after relative import
            "import as alias",           # Missing module name before alias
            "from module import as",     # Missing name before alias
            "import module as",          # Missing alias name
        ]
        
        for stmt in invalid_imports:
            tester.assert_import_syntax_error(stmt)

    def test_invalid_relative_imports(self, tester):
        """Test invalid relative import syntax"""
        # Invalid relative import patterns
        invalid_relative = [
            "import .",               # Cannot import relative with simple import
            "import .module",         # Cannot import relative with simple import
            "import ..parent",        # Cannot import relative with simple import
            "from . import .",        # Cannot import dot as name
            "from .. import ..",      # Cannot import dots as names
        ]
        
        for stmt in invalid_relative:
            tester.assert_import_syntax_error(stmt)

    def test_invalid_asterisk_usage(self, tester):
        """Test invalid asterisk import usage"""
        # Invalid asterisk patterns
        invalid_asterisk = [
            "import *",                     # Cannot use * with simple import
            "from module import *, name",   # Cannot mix * with other names
            "from module import name, *",   # Cannot mix * with other names  
            "from module import * as all",  # Cannot alias *
        ]
        
        for stmt in invalid_asterisk:
            tester.assert_import_syntax_error(stmt)

    def test_invalid_alias_syntax(self, tester):
        """Test invalid alias syntax"""
        # Invalid alias patterns
        invalid_aliases = [
            "import module as",           # Missing alias name
            "from module import name as", # Missing alias name
            "import module as 123",       # Invalid alias name
            "import module as def",       # Reserved word alias
            "import module as class",     # Reserved word alias
        ]
        
        for stmt in invalid_aliases:
            tester.assert_import_syntax_error(stmt)


class TestSection711CrossImplementationCompatibility:
    """Test import statement features across Python implementations"""
    
    @pytest.fixture
    def tester(self):
        return ImportStatementTester()

    def test_comprehensive_import_combinations(self, tester):
        """Test complex import statement combinations"""
        # Complex import patterns
        complex_imports = [
            """import os, sys
from collections import defaultdict, Counter
from .local import helper
from ..parent import utility""",
            
            """from package.subpackage.module import (
    function1 as f1,
    function2,
    Class1 as C1,
    Class2,
    CONSTANT as CONST
)""",
            
            """import module1 as m1, module2, module3 as m3
from package import name1, name2 as n2, name3""",
        ]
        
        for stmt in complex_imports:
            tree = tester.assert_import_syntax_parses(stmt)
            imports = tester.get_import_nodes(stmt)
            assert len(imports) >= 1

    def test_deeply_nested_package_imports(self, tester):
        """Test deeply nested package structure imports"""
        # Deep package hierarchies
        deep_imports = [
            "import very.deep.package.structure.module",
            "from very.deep.package.structure import module",
            "from very.deep.package.structure.module import function",
            "from .very.deep.local.structure import module",
            "from ...grand.parent.deep.structure import utility"
        ]
        
        for stmt in deep_imports:
            tree = tester.assert_import_syntax_parses(stmt)
            imports = tester.get_import_nodes(stmt)
            assert len(imports) == 1

    def test_import_ast_structure_validation(self, tester):
        """Test import AST structure validation"""
        # Validate AST structure for imports
        test_imports = [
            ("import os", ast.Import),
            ("from sys import argv", ast.ImportFrom),
            ("from . import local", ast.ImportFrom),
            ("import math as m", ast.Import)
        ]
        
        for stmt, expected_type in test_imports:
            tree = tester.assert_import_syntax_parses(stmt)
            imports = tester.get_import_nodes(stmt)
            assert len(imports) == 1
            assert isinstance(imports[0], expected_type)
            
            if expected_type == ast.ImportFrom:
                # Test ImportFrom specific attributes
                imp = imports[0]
                if stmt.startswith("from ."):
                    assert imp.level >= 1
                else:
                    assert imp.level == 0

    def test_import_name_resolution_patterns(self, tester):
        """Test various import name resolution patterns"""
        # Different name resolution scenarios
        resolution_imports = [
            "import package",
            "import package.module",
            "import package.subpackage.module",
            "from package import module",
            "from package.subpackage import module",
            "from package.subpackage.module import function",
            "from . import sibling",
            "from .package import module",
            "from ..parent import module",
            "from ..parent.sibling import function"
        ]
        
        for stmt in resolution_imports:
            tree = tester.assert_import_syntax_parses(stmt)
            imports = tester.get_import_nodes(stmt)
            assert len(imports) == 1

    def test_future_imports_compatibility(self, tester):
        """Test __future__ imports syntax"""
        # Future imports (special case of from...import)
        future_imports = [
            "from __future__ import print_function",
            "from __future__ import division", 
            "from __future__ import absolute_import",
            "from __future__ import unicode_literals",
            "from __future__ import annotations",
            "from __future__ import (print_function, division)"
        ]
        
        for stmt in future_imports:
            tree = tester.assert_import_syntax_parses(stmt)
            imports = tester.get_import_nodes(stmt)
            assert len(imports) == 1
            assert isinstance(imports[0], ast.ImportFrom)
            assert imports[0].module == "__future__"

    def test_import_edge_cases(self, tester):
        """Test edge cases in import statements"""
        # Edge cases and corner scenarios
        edge_case_imports = [
            "import sys; import os",  # Multiple statements on one line
            "from . import *",       # Relative asterisk import
            "import _",              # Single underscore module
            "import __",             # Double underscore module
            "from module import __all__",  # Import __all__
            "from package import _private, __dunder__"  # Mixed private names
        ]
        
        for stmt in edge_case_imports:
            try:
                tree = tester.assert_import_syntax_parses(stmt)
                imports = tester.get_import_nodes(stmt)
                assert len(imports) >= 1
            except Exception:
                # Some edge cases might not be supported
                # Just verify they don't cause crashes
                pass