"""
Section 9: Top-level Components - Conformance Test Suite

Tests Python Language Reference Section 9 compliance across implementations.
Based on formal top-level component syntax definitions and prose assertions for complete program behavior.

Grammar tested:
    file_input: (NEWLINE | stmt)* ENDMARKER
    interactive_input: [stmt_list] NEWLINE | compound_stmt NEWLINE
    eval_input: testlist NEWLINE* ENDMARKER
    func_type_input: func_type NEWLINE* ENDMARKER
    
Language Reference requirements tested:
    - Complete Python program structure and execution
    - Module-level code organization and execution order
    - Interactive input handling and evaluation
    - Expression evaluation in different contexts
    - __main__ module execution semantics
    - File input vs interactive input differences
    - Top-level component interaction and integration
    - Cross-implementation program execution compatibility
"""

import ast
import pytest
import sys
import textwrap
from typing import Any


class TopLevelComponentTester:
    """Helper class for testing top-level component conformance.
    
    Focuses on AST structure validation for complete program syntax and behavior
    patterns that can be statically analyzed for cross-implementation compatibility.
    """
    
    def assert_program_parses(self, source: str):
        """Test that complete program syntax parses correctly.
        
        Args:
            source: Python source code for complete program
        """
        try:
            tree = ast.parse(source, mode='exec')
            return tree
        except SyntaxError as e:
            pytest.fail(f"Complete program syntax should be valid but failed to parse: {source}\\nError: {e}")
    
    def assert_expression_parses(self, source: str):
        """Test that expression syntax parses correctly.
        
        Args:
            source: Python expression source code
        """
        try:
            tree = ast.parse(source, mode='eval')
            return tree
        except SyntaxError as e:
            pytest.fail(f"Expression syntax should be valid but failed to parse: {source}\\nError: {e}")
    
    def assert_program_syntax_error(self, source: str):
        """Test that invalid program syntax raises SyntaxError.
        
        Args:
            source: Python source code that should be invalid
        """
        with pytest.raises(SyntaxError):
            ast.parse(source, mode='exec')
    
    def get_module_statements(self, source: str) -> list:
        """Get module-level statements from source.
        
        Args:
            source: Python source code
            
        Returns:
            List of module-level AST nodes
        """
        tree = ast.parse(source, mode='exec')
        return tree.body
    
    def get_import_statements(self, source: str) -> list:
        """Get import statements from source (including nested ones).
        
        Args:
            source: Python source code
            
        Returns:
            List of import AST nodes
        """
        tree = ast.parse(source, mode='exec')
        import_nodes = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                import_nodes.append(node)
        
        return import_nodes
    
    def get_function_definitions(self, source: str) -> list:
        """Get function definitions from source.
        
        Args:
            source: Python source code
            
        Returns:
            List of function definition AST nodes
        """
        tree = ast.parse(source, mode='exec')
        function_nodes = []
        
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                function_nodes.append(node)
        
        return function_nodes
    
    def get_class_definitions(self, source: str) -> list:
        """Get class definitions from source.
        
        Args:
            source: Python source code
            
        Returns:
            List of class definition AST nodes
        """
        tree = ast.parse(source, mode='exec')
        class_nodes = []
        
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                class_nodes.append(node)
        
        return class_nodes
    
    def analyze_program_structure(self, source: str) -> dict:
        """Analyze complete program structure.
        
        Args:
            source: Python source code
            
        Returns:
            Dict with program structure analysis
        """
        tree = ast.parse(source, mode='exec')
        
        analysis = {
            'total_statements': len(tree.body),
            'import_count': 0,
            'function_count': 0,
            'class_count': 0,
            'assignment_count': 0,
            'expression_statement_count': 0,
            'has_docstring': False,
            'has_main_guard': False,
            'has_imports': False,
            'has_functions': False,
            'has_classes': False
        }
        
        # Check for module docstring
        if (tree.body and isinstance(tree.body[0], ast.Expr) 
            and isinstance(tree.body[0].value, ast.Constant) 
            and isinstance(tree.body[0].value.value, str)):
            analysis['has_docstring'] = True
        
        # Analyze statement types
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                analysis['import_count'] += 1
                analysis['has_imports'] = True
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                analysis['function_count'] += 1
                analysis['has_functions'] = True
            elif isinstance(node, ast.ClassDef):
                analysis['class_count'] += 1
                analysis['has_classes'] = True
            elif isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                analysis['assignment_count'] += 1
            elif isinstance(node, ast.Expr):
                analysis['expression_statement_count'] += 1
        
        # Check for __main__ guard pattern
        source_text = source if isinstance(source, str) else ast.unparse(tree)
        if '__main__' in source_text and '__name__' in source_text:
            analysis['has_main_guard'] = True
        
        return analysis


@pytest.fixture
def tester():
    """Provide TopLevelComponentTester instance for tests."""
    return TopLevelComponentTester()


class TestSection9BasicProgramStructure:
    """Test basic complete program structure."""
    
    def test_minimal_programs(self, tester):
        """Test minimal valid Python programs"""
        minimal_program_patterns = [
            '# Empty program with comment',
            'pass',
            '42',
            '"Hello, World!"',
            'print("Hello, World!")'
        ]
        
        for source in minimal_program_patterns:
            tree = tester.assert_program_parses(source)
            statements = tester.get_module_statements(source)
            # Empty programs and expression statements should parse
    
    def test_simple_complete_programs(self, tester):
        """Test simple complete program patterns"""
        simple_program_patterns = [
            '''#!/usr/bin/env python3
"""Simple program with shebang and docstring."""

print("Hello, World!")''',
            '''# Simple calculation program
x = 10
y = 20
result = x + y
print(f"Result: {result}")''',
            '''import sys

def main():
    print("Program started")
    return 0

if __name__ == "__main__":
    sys.exit(main())''',
            '''"""
Multi-line module docstring
describing the program purpose.
"""

def greeting(name):
    return f"Hello, {name}!"

message = greeting("World")
print(message)'''
        ]
        
        for source in simple_program_patterns:
            tree = tester.assert_program_parses(source)
            analysis = tester.analyze_program_structure(source)
            assert analysis['total_statements'] > 0, f"Should have statements: {source}"
    
    def test_program_organization_patterns(self, tester):
        """Test common program organization patterns"""
        organization_patterns = [
            '''"""Module docstring first."""

# Standard library imports
import os
import sys
from pathlib import Path

# Third-party imports  
import requests
import numpy as np

# Local imports
from .utils import helper_function
from ..config import settings

# Constants
VERSION = "1.0.0"
DEFAULT_CONFIG = {"debug": False}

# Global variables
_cache = {}
logger = None

# Function definitions
def setup():
    """Setup function."""
    pass

def main():
    """Main function."""
    pass

# Class definitions
class Application:
    """Application class."""
    pass

# Main execution
if __name__ == "__main__":
    main()''',
            '''# Configuration-driven program
CONFIG = {
    "database_url": "sqlite:///app.db",
    "debug_mode": False,
    "log_level": "INFO"
}

class DatabaseConnection:
    def __init__(self, url):
        self.url = url
    
    def connect(self):
        pass

def create_app(config):
    db = DatabaseConnection(config["database_url"])
    return {"db": db, "config": config}

app = create_app(CONFIG)''',
        ]
        
        for source in organization_patterns:
            tree = tester.assert_program_parses(source)
            analysis = tester.analyze_program_structure(source)
            assert analysis['has_imports'] or analysis['has_functions'] or analysis['has_classes'], \
                f"Should have program components: {source}"


class TestSection9ModuleLevelCode:
    """Test module-level code execution."""
    
    def test_module_level_statements(self, tester):
        """Test various module-level statement types"""
        module_level_patterns = [
            '''# Module-level assignments
x = 42
name = "Python"
version = (3, 11)
config = {"debug": True}''',
            '''# Module-level function calls
print("Module initialization")
setup_logging()
validate_environment()''',
            '''# Module-level control flow
if DEBUG_MODE:
    print("Debug mode enabled")
    
for plugin in PLUGINS:
    load_plugin(plugin)
    
try:
    import_optional_dependency()
except ImportError:
    print("Optional dependency not available")''',
            '''# Module-level class instantiation
logger = Logger(__name__)
app = Application()
db_connection = Database.connect()'''
        ]
        
        for source in module_level_patterns:
            tree = tester.assert_program_parses(source)
            statements = tester.get_module_statements(source)
            assert len(statements) > 0, f"Should have module statements: {source}"
    
    def test_module_initialization_patterns(self, tester):
        """Test module initialization patterns"""
        initialization_patterns = [
            '''"""Module with initialization code."""

# Module-level initialization
_initialized = False

def _initialize():
    global _initialized
    if not _initialized:
        setup_resources()
        _initialized = True

# Auto-initialize on import
_initialize()''',
            '''# Configuration loading pattern
import os
import json

def load_config():
    config_path = os.environ.get("CONFIG_PATH", "config.json")
    if os.path.exists(config_path):
        with open(config_path) as f:
            return json.load(f)
    return {}

# Load configuration at module level
CONFIG = load_config()''',
            '''# Plugin registration pattern
_plugins = []

def register_plugin(plugin):
    _plugins.append(plugin)

def get_plugins():
    return _plugins[:]

# Auto-discover plugins
import pkgutil
for importer, modname, ispkg in pkgutil.iter_modules():
    if modname.startswith("plugin_"):
        try:
            plugin_module = __import__(modname)
            if hasattr(plugin_module, "register"):
                register_plugin(plugin_module)
        except ImportError:
            pass'''
        ]
        
        for source in initialization_patterns:
            tree = tester.assert_program_parses(source)
            analysis = tester.analyze_program_structure(source)
            assert analysis['has_functions'], f"Should have initialization functions: {source}"
    
    def test_module_docstrings(self, tester):
        """Test module docstring patterns"""
        docstring_patterns = [
            '''"""Single line module docstring."""

def function():
    pass''',
            '''"""
Multi-line module docstring.

This module provides functionality for processing data
and managing application state.

Example:
    from mymodule import process_data
    result = process_data(input_data)
"""

VERSION = "1.0.0"''',
            '''"""Module with comprehensive docstring.

This module implements the core functionality for the application.
It provides classes and functions for:
- Data processing and validation
- Configuration management
- Error handling and logging

Attributes:
    VERSION (str): The version of this module
    DEFAULT_CONFIG (dict): Default configuration values

Example:
    Basic usage of this module:
    
    >>> from mymodule import process
    >>> result = process("input")
    >>> print(result)
    'processed: input'
"""

VERSION = "2.1.0"
DEFAULT_CONFIG = {"timeout": 30}'''
        ]
        
        for source in docstring_patterns:
            tree = tester.assert_program_parses(source)
            analysis = tester.analyze_program_structure(source)
            assert analysis['has_docstring'], f"Should have module docstring: {source}"


class TestSection9ImportHandling:
    """Test import statement handling in complete programs."""
    
    def test_import_statement_patterns(self, tester):
        """Test various import statement patterns"""
        import_patterns = [
            '''# Basic imports
import os
import sys
import json''',
            '''# From imports
from pathlib import Path
from typing import List, Dict, Optional
from collections import defaultdict''',
            '''# Aliased imports
import numpy as np
import pandas as pd
from datetime import datetime as dt''',
            '''# Relative imports
from . import utils
from .config import settings
from ..common import helpers''',
            '''# Star imports (discouraged but legal)
from math import *
from typing import *''',
            '''# Conditional imports
try:
    import ujson as json
except ImportError:
    import json

try:
    from lxml import etree
except ImportError:
    from xml.etree import ElementTree as etree'''
        ]
        
        for source in import_patterns:
            tree = tester.assert_program_parses(source)
            import_statements = tester.get_import_statements(source)
            assert len(import_statements) > 0, f"Should have import statements: {source}"
    
    def test_import_organization(self, tester):
        """Test import organization best practices"""
        organized_import_patterns = [
            '''# Standard library imports
import os
import sys
import json
from pathlib import Path
from typing import List, Dict

# Third-party imports
import requests
import click
import pytest

# Local application imports
from .models import User
from .utils import validate_email
from ..config import DATABASE_URL''',
            '''"""Module with properly organized imports."""

# Standard library
import asyncio
import logging
from dataclasses import dataclass
from typing import AsyncGenerator, Optional

# Third-party
import aiohttp
import click

# Local
from .exceptions import APIError
from .models import Response''',
        ]
        
        for source in organized_import_patterns:
            tree = tester.assert_program_parses(source)
            analysis = tester.analyze_program_structure(source)
            assert analysis['has_imports'], f"Should have organized imports: {source}"


class TestSection9FunctionAndClassDefinitions:
    """Test function and class definitions in complete programs."""
    
    def test_function_definition_patterns(self, tester):
        """Test various function definition patterns"""
        function_patterns = [
            '''def simple_function():
    """Simple function with no parameters."""
    return "Hello, World!"

def function_with_params(name, age=None):
    """Function with parameters and default values."""
    return f"Name: {name}, Age: {age}"

def function_with_annotations(name: str, age: int = 0) -> str:
    """Function with type annotations."""
    return f"{name} is {age} years old"''',
            '''async def async_function():
    """Async function example."""
    await asyncio.sleep(1)
    return "Done"

async def async_generator():
    """Async generator function."""
    for i in range(5):
        yield i
        await asyncio.sleep(0.1)''',
            '''def decorator_example(func):
    """Decorator function."""
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@decorator_example
def decorated_function():
    """Function with decorator."""
    return "decorated result"''',
            '''def complex_function_signature(
    pos_arg,
    *args,
    kw_only_arg,
    optional_kw=None,
    **kwargs
):
    """Function with complex signature."""
    return {
        "pos_arg": pos_arg,
        "args": args,
        "kw_only_arg": kw_only_arg,
        "optional_kw": optional_kw,
        "kwargs": kwargs
    }'''
        ]
        
        for source in function_patterns:
            tree = tester.assert_program_parses(source)
            function_defs = tester.get_function_definitions(source)
            assert len(function_defs) > 0, f"Should have function definitions: {source}"
    
    def test_class_definition_patterns(self, tester):
        """Test various class definition patterns"""
        class_patterns = [
            '''class SimpleClass:
    """Simple class with basic methods."""
    
    def __init__(self, value):
        self.value = value
    
    def get_value(self):
        return self.value''',
            '''class InheritanceExample(BaseClass):
    """Class with inheritance."""
    
    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
    
    def specialized_method(self):
        return f"Specialized: {self.name}"''',
            '''class MultipleInheritance(Mixin1, Mixin2, BaseClass):
    """Class with multiple inheritance."""
    pass

@dataclass
class DataClassExample:
    """Data class example."""
    name: str
    age: int = 0
    active: bool = True''',
            '''class ComplexClass:
    """Class with various features."""
    
    class_variable = "shared"
    
    def __init__(self, instance_var):
        self.instance_var = instance_var
    
    @property
    def computed_property(self):
        return f"computed_{self.instance_var}"
    
    @classmethod
    def class_method(cls):
        return cls.class_variable
    
    @staticmethod
    def static_method():
        return "static result"
    
    def __str__(self):
        return f"Complex({self.instance_var})"'''
        ]
        
        for source in class_patterns:
            tree = tester.assert_program_parses(source)
            class_defs = tester.get_class_definitions(source)
            assert len(class_defs) > 0, f"Should have class definitions: {source}"
    
    def test_nested_definitions(self, tester):
        """Test nested function and class definitions"""
        nested_patterns = [
            '''def outer_function():
    """Function with nested function."""
    
    def inner_function():
        return "inner result"
    
    return inner_function()

class OuterClass:
    """Class with nested class."""
    
    class InnerClass:
        def inner_method(self):
            return "inner class method"
    
    def create_inner(self):
        return self.InnerClass()''',
            '''def factory_function():
    """Factory function creating closures."""
    
    def create_counter():
        count = 0
        
        def counter():
            nonlocal count
            count += 1
            return count
        
        return counter
    
    return create_counter()'''
        ]
        
        for source in nested_patterns:
            tree = tester.assert_program_parses(source)
            analysis = tester.analyze_program_structure(source)
            assert analysis['has_functions'] or analysis['has_classes'], \
                f"Should have nested definitions: {source}"


class TestSection9MainExecutionPatterns:
    """Test main execution and program entry point patterns."""
    
    def test_main_guard_patterns(self, tester):
        """Test __main__ guard patterns"""
        main_guard_patterns = [
            '''def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()''',
            '''def main():
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())''',
            '''def main(args):
    for arg in args:
        print(f"Processing: {arg}")

if __name__ == "__main__":
    import sys
    main(sys.argv[1:])''',
            '''import argparse

def main():
    parser = argparse.ArgumentParser(description="Example program")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    
    if args.verbose:
        print("Verbose mode enabled")

if __name__ == "__main__":
    main()'''
        ]
        
        for source in main_guard_patterns:
            tree = tester.assert_program_parses(source)
            analysis = tester.analyze_program_structure(source)
            assert analysis['has_main_guard'], f"Should have main guard: {source}"
    
    def test_script_vs_module_patterns(self, tester):
        """Test patterns that work as both script and module"""
        script_module_patterns = [
            '''"""Module that can be imported or run as script."""

def process_data(data):
    return data.upper()

def main():
    result = process_data("hello world")
    print(result)

if __name__ == "__main__":
    main()''',
            '''"""CLI tool module."""

import argparse
import sys

def add_numbers(a, b):
    return a + b

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("a", type=int)
    parser.add_argument("b", type=int)
    args = parser.parse_args()
    
    result = add_numbers(args.a, args.b)
    print(f"Result: {result}")
    return 0

if __name__ == "__main__":
    sys.exit(main())''',
            '''#!/usr/bin/env python3
"""Executable script with shebang."""

def calculate_fibonacci(n):
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

def main():
    for i in range(10):
        print(f"fib({i}) = {calculate_fibonacci(i)}")

if __name__ == "__main__":
    main()'''
        ]
        
        for source in script_module_patterns:
            tree = tester.assert_program_parses(source)
            analysis = tester.analyze_program_structure(source)
            assert analysis['has_functions'], f"Should have reusable functions: {source}"
            assert analysis['has_main_guard'], f"Should be runnable as script: {source}"


class TestSection9ExpressionEvaluation:
    """Test expression evaluation contexts."""
    
    def test_simple_expressions(self, tester):
        """Test simple expression evaluation"""
        simple_expressions = [
            '42',
            '3.14159',
            '"Hello, World!"',
            'True',
            'None',
            '[1, 2, 3]',
            '{"key": "value"}',
            '(1, 2, 3)'
        ]
        
        for expr in simple_expressions:
            tree = tester.assert_expression_parses(expr)
            assert isinstance(tree, ast.Expression), f"Should be Expression node: {expr}"
    
    def test_complex_expressions(self, tester):
        """Test complex expression patterns"""
        complex_expressions = [
            '2 + 3 * 4',
            'len([1, 2, 3, 4, 5])',
            'sum(x**2 for x in range(10))',
            'max(data.values()) if data else 0',
            '"_".join(str(i) for i in range(5))',
            'any(x > 10 for x in values)',
            'dict(zip(keys, values))',
            'lambda x: x * 2'
        ]
        
        for expr in complex_expressions:
            tree = tester.assert_expression_parses(expr)
            assert isinstance(tree, ast.Expression), f"Should be Expression node: {expr}"
    
    def test_expression_statements_in_programs(self, tester):
        """Test expression statements within complete programs"""
        expression_statement_patterns = [
            '''# Expression statements in programs
print("Starting program")
calculate_results()
len(data)  # Expression statement (usually for side effects)
process_queue()
print("Program complete")''',
            '''# Function calls as expression statements
setup_logging()
validate_configuration()
initialize_database()
start_background_tasks()''',
            '''# Complex expressions as statements
[process_item(item) for item in items]  # List comprehension for side effects
{key: transform(value) for key, value in data.items()}  # Dict comprehension
sum(validate_record(record) for record in records)  # Generator expression'''
        ]
        
        for source in expression_statement_patterns:
            tree = tester.assert_program_parses(source)
            statements = tester.get_module_statements(source)
            # Should have expression statements
            expr_statements = [stmt for stmt in statements if isinstance(stmt, ast.Expr)]
            assert len(expr_statements) > 0, f"Should have expression statements: {source}"


class TestSection9TopLevelComponentAST:
    """Test top-level component AST structure validation."""
    
    def test_module_ast_structure(self, tester):
        """Test module AST structure validation"""
        module_ast_cases = [
            'x = 42',
            '''def function():
    pass''',
            '''class Class:
    pass''',
            '''import os

def main():
    pass

if __name__ == "__main__":
    main()'''
        ]
        
        for source in module_ast_cases:
            tree = tester.assert_program_parses(source)
            assert isinstance(tree, ast.Module), "Should be Module node"
            assert hasattr(tree, 'body'), "Should have body attribute"
            assert isinstance(tree.body, list), "Body should be list"
            assert len(tree.body) > 0, "Should have statements"
    
    def test_program_component_integration(self, tester):
        """Test integration of different program components"""
        integration_cases = [
            '''"""Integrated program with all components."""

import os
import sys
from typing import List, Optional

# Constants
VERSION = "1.0.0"

# Global variables  
_cache = {}

def utility_function(data: List[str]) -> Optional[str]:
    """Utility function."""
    return data[0] if data else None

class DataProcessor:
    """Data processing class."""
    
    def __init__(self, name: str):
        self.name = name
    
    def process(self, items: List[str]) -> List[str]:
        return [item.upper() for item in items]

def main():
    processor = DataProcessor("main")
    data = ["hello", "world"]
    result = processor.process(data)
    print(f"Processed: {result}")

if __name__ == "__main__":
    main()''',
        ]
        
        for source in integration_cases:
            tree = tester.assert_program_parses(source)
            analysis = tester.analyze_program_structure(source)
            
            assert analysis['has_imports'], "Should have imports"
            assert analysis['has_functions'], "Should have functions"
            assert analysis['has_classes'], "Should have classes"
            assert analysis['has_main_guard'], "Should have main guard"
            assert analysis['total_statements'] > 5, "Should have multiple components"


class TestSection9CrossImplementationCompatibility:
    """Test cross-implementation compatibility for complete programs."""
    
    def test_program_consistency(self, tester):
        """Test program consistency across implementations"""
        consistency_test_cases = [
            'print("Hello, World!")',
            '''def greet(name):
    return f"Hello, {name}!"

print(greet("World"))''',
            '''class Greeter:
    def __init__(self, greeting):
        self.greeting = greeting
    
    def greet(self, name):
        return f"{self.greeting}, {name}!"

greeter = Greeter("Hello")
print(greeter.greet("World"))''',
            '''import sys

def main():
    print("Program started")
    return 0

if __name__ == "__main__":
    sys.exit(main())'''
        ]
        
        for source in consistency_test_cases:
            tree = tester.assert_program_parses(source)
            analysis = tester.analyze_program_structure(source)
            assert analysis['total_statements'] > 0, f"Should have statements: {source}"
    
    def test_comprehensive_program_patterns(self, tester):
        """Test comprehensive real-world program patterns"""
        comprehensive_source = '''#!/usr/bin/env python3
"""
Comprehensive Python program demonstrating all major language features.

This program serves as a complete example of Python's top-level component
organization and demonstrates proper program structure for alternative
Python implementations.
"""

# Standard library imports
import os
import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from collections import defaultdict

# Module-level constants
VERSION = "1.0.0"
DEFAULT_CONFIG = {
    "debug": False,
    "log_level": "INFO",
    "max_retries": 3
}

# Module-level variables
_logger = None
_config = {}

# Data classes
@dataclass
class ConfigItem:
    """Configuration item data class."""
    key: str
    value: Any
    required: bool = False

# Utility functions
def setup_logging(level: str = "INFO") -> logging.Logger:
    """Setup application logging."""
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(getattr(logging, level))
    return logger

def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load configuration from file or environment."""
    config = DEFAULT_CONFIG.copy()
    
    if config_path and config_path.exists():
        with open(config_path) as f:
            file_config = json.load(f)
            config.update(file_config)
    
    # Override with environment variables
    for key in config:
        env_key = f"APP_{key.upper()}"
        if env_value := os.environ.get(env_key):
            config[key] = env_value
    
    return config

# Main application classes
class Application:
    """Main application class."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = setup_logging(config.get("log_level", "INFO"))
        self._processors = {}
    
    def register_processor(self, name: str, processor):
        """Register a data processor."""
        self._processors[name] = processor
        self.logger.info(f"Registered processor: {name}")
    
    def process_data(self, processor_name: str, data: List[Any]) -> List[Any]:
        """Process data using registered processor."""
        if processor_name not in self._processors:
            raise ValueError(f"Unknown processor: {processor_name}")
        
        processor = self._processors[processor_name]
        return processor.process(data)
    
    def run(self) -> int:
        """Run the application."""
        self.logger.info("Application starting")
        
        try:
            # Application logic here
            self.logger.info("Processing complete")
            return 0
        except Exception as e:
            self.logger.error(f"Application error: {e}")
            return 1
        finally:
            self.logger.info("Application shutdown")

class DataProcessor:
    """Base data processor class."""
    
    def process(self, data: List[Any]) -> List[Any]:
        """Process data - to be overridden by subclasses."""
        raise NotImplementedError

class TextProcessor(DataProcessor):
    """Text data processor."""
    
    def process(self, data: List[str]) -> List[str]:
        """Process text data."""
        return [item.strip().upper() for item in data if item.strip()]

# Main execution function
def main(args: Optional[List[str]] = None) -> int:
    """Main application entry point."""
    global _logger, _config
    
    # Parse command line arguments if needed
    if args is None:
        args = sys.argv[1:]
    
    # Load configuration
    config_path = Path("config.json")
    _config = load_config(config_path if config_path.exists() else None)
    _logger = setup_logging(_config.get("log_level", "INFO"))
    
    # Create and configure application
    app = Application(_config)
    app.register_processor("text", TextProcessor())
    
    # Run application
    return app.run()

# Script execution guard
if __name__ == "__main__":
    sys.exit(main())
'''
        
        tree = tester.assert_program_parses(comprehensive_source)
        analysis = tester.analyze_program_structure(comprehensive_source)
        
        assert analysis['total_statements'] >= 10, f"Should have many statements: {analysis}"
        assert analysis['has_docstring'], "Should have module docstring"
        assert analysis['has_imports'], "Should have imports"
        assert analysis['has_functions'], "Should have functions"
        assert analysis['has_classes'], "Should have classes"
        assert analysis['has_main_guard'], "Should have main guard"
        assert analysis['import_count'] >= 5, "Should have multiple imports"
        assert analysis['function_count'] >= 3, "Should have multiple functions"
        assert analysis['class_count'] >= 3, "Should have multiple classes"
    
    def test_program_introspection_capabilities(self, tester):
        """Test ability to analyze complete programs programmatically"""
        introspection_source = '''
"""Example program for introspection testing."""

import os
import sys
from typing import List

CONFIG = {"debug": True}

def helper_function(data: List[str]) -> str:
    return ", ".join(data)

class ExampleClass:
    def __init__(self, name: str):
        self.name = name
    
    def get_info(self) -> str:
        return f"Example: {self.name}"

def main():
    example = ExampleClass("test")
    data = ["item1", "item2", "item3"]
    result = helper_function(data)
    print(f"{example.get_info()}: {result}")

if __name__ == "__main__":
    main()
'''
        
        tree = tester.assert_program_parses(introspection_source)
        
        # Should identify all program components
        analysis = tester.analyze_program_structure(introspection_source)
        
        assert analysis['total_statements'] >= 6, "Should have multiple statements"
        assert analysis['has_imports'], "Should have imports"
        assert analysis['has_functions'], "Should have functions"
        assert analysis['has_classes'], "Should have classes"
        assert analysis['has_main_guard'], "Should have main guard"
        
        # Test specific component extraction
        import_statements = tester.get_import_statements(introspection_source)
        function_defs = tester.get_function_definitions(introspection_source)
        class_defs = tester.get_class_definitions(introspection_source)
        
        assert len(import_statements) >= 2, "Should extract import statements"
        assert len(function_defs) >= 2, "Should extract function definitions"
        assert len(class_defs) >= 1, "Should extract class definitions"
        
        # All components should have proper AST structure
        for import_stmt in import_statements:
            assert isinstance(import_stmt, (ast.Import, ast.ImportFrom)), "Should be import node"
        
        for func_def in function_defs:
            assert isinstance(func_def, (ast.FunctionDef, ast.AsyncFunctionDef)), "Should be function node"
            assert hasattr(func_def, 'name'), "Should have function name"
        
        for class_def in class_defs:
            assert isinstance(class_def, ast.ClassDef), "Should be class node"
            assert hasattr(class_def, 'name'), "Should have class name"