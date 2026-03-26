"""
Pytest configuration for Python Language Reference Conformance Test Suite.

Handles automatic skipping of tests based on Python version requirements
using the marker system defined in pytest.ini.
"""

import sys
import pytest


def pytest_runtest_setup(item):
    """Automatically skip tests based on version markers."""
    
    # Check for minimum version markers
    for marker in item.iter_markers():
        if marker.name.startswith('min_version_'):
            # Extract version from marker name (e.g., min_version_3_6 -> (3, 6))
            version_str = marker.name.replace('min_version_', '')
            if '_' in version_str:
                version_parts = version_str.split('_')
                required_version = tuple(int(part) for part in version_parts)
            else:
                required_version = (int(version_str),)
            
            if sys.version_info < required_version:
                pytest.skip(f"Requires Python {'.'.join(map(str, required_version))}+")
        
        # Feature-based markers
        elif marker.name == 'feature_fstrings' and sys.version_info < (3, 6):
            pytest.skip("F-strings require Python 3.6+")
        elif marker.name == 'feature_walrus' and sys.version_info < (3, 8):
            pytest.skip("Walrus operator requires Python 3.8+")
        elif marker.name == 'feature_match' and sys.version_info < (3, 10):
            pytest.skip("Match statements require Python 3.10+")
        elif marker.name == 'feature_union_types' and sys.version_info < (3, 10):
            pytest.skip("Union type syntax (X | Y) requires Python 3.10+")
        elif marker.name == 'feature_async' and sys.version_info < (3, 5):
            pytest.skip("Async/await requires Python 3.5+")
        
        # Implementation-specific markers
        elif marker.name == 'cpython_only' and not hasattr(sys, '_getframe'):
            pytest.skip("CPython-specific test")
        elif marker.name == 'pypy_skip' and hasattr(sys, 'pypy_version_info'):
            pytest.skip("Known PyPy compatibility issue")


def pytest_configure(config):
    """Configure pytest markers."""
    # Markers are already defined in pytest.ini
    pass


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add default markers where appropriate."""
    pass