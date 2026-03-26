# Version-Aware Testing Strategy

## Problem Statement

Python language features are added incrementally across versions. Running all conformance tests against all Python versions will fail when:

- **Python 3.6**: f-strings, underscore literals (`1_000`)
- **Python 3.8**: Walrus operator (`:=`), positional-only parameters
- **Python 3.10**: Match statements (`match`/`case`), union types (`X | Y`)
- **Python 3.11**: Exception groups, task groups
- **Python 3.12**: f-string improvements, type parameter syntax

## Solution: Pytest Markers + CI Filtering

### Marker System

**Version-based markers:**
```python
@pytest.mark.min_version_3_8        # Requires Python 3.8+
@pytest.mark.min_version_3_10       # Requires Python 3.10+
@pytest.mark.min_version_3_12       # Requires Python 3.12+
```

**Feature-based markers:**
```python
@pytest.mark.feature_fstrings       # Tests f-string features
@pytest.mark.feature_walrus         # Tests walrus operator  
@pytest.mark.feature_match          # Tests match statements
@pytest.mark.feature_union_types    # Tests X | Y syntax
```

**Implementation-specific markers:**
```python
@pytest.mark.cpython_only           # CPython-specific behavior
@pytest.mark.pypy_skip              # Skip on PyPy
```

### CI Integration

**GitHub Actions runs version-appropriate tests:**
```bash
# Python 3.10 runs only tests compatible with 3.10
pytest -m "not min_version or min_version_3_10"

# Python 3.12 runs all tests (latest version)
pytest -m "not min_version or min_version_3_12"
```

### Test Structure Example

```python
class TestSection810MatchStatements:
    """Test Section 8.10: Match statements (Python 3.10+)"""
    
    @pytest.mark.min_version_3_10
    @pytest.mark.feature_match
    def test_basic_match_syntax(self, tester):
        """Test basic match/case statement parsing"""
        code = """
        match value:
            case 1:
                result = "one"
            case _:
                result = "other"
        """
        tester.assert_parses_correctly(code)
    
    @pytest.mark.min_version_3_10
    def test_pattern_matching_guards(self, tester):
        """Test pattern matching with guards"""
        code = """
        match value:
            case x if x > 0:
                result = "positive"
        """
        tester.assert_parses_correctly(code)
```

## Pytest Configuration

**pytest.ini markers registration:**
```ini
[tool:pytest]
markers =
    min_version: tests requiring specific minimum Python version
    min_version_3_8: requires Python 3.8+ 
    min_version_3_10: requires Python 3.10+
    feature_match: tests match statement features
    cpython_only: tests specific to CPython implementation
```

## Version Detection Strategy

### Automatic Version Filtering

**CI automatically filters tests based on Python version:**

| Python Version | Tests Run |
|---------------|-----------|
| 3.10 | All tests marked compatible with 3.10 |
| 3.11 | All tests marked compatible with 3.10 + 3.11 |  
| 3.12 | All tests (latest supports everything) |

### Manual Version Testing

**Local development:**
```bash
# Test only Python 3.8 compatible features
pytest -m "not min_version or min_version_3_8"

# Test specific feature set
pytest -m "feature_fstrings"

# Test all except implementation-specific
pytest -m "not cpython_only"
```

## Implementation Guidelines

### For New Test Files

1. **Analyze Language Reference section** for version requirements
2. **Mark tests appropriately** with version/feature markers
3. **Document version rationale** in test docstrings
4. **Test locally** against multiple Python versions

### For PEP Integration

**When new PEP adds language feature:**

1. **Identify target Python version** from PEP metadata
2. **Add appropriate markers** to generated tests
3. **Update CI matrix** if new version needs testing
4. **Verify version filtering** works correctly

### Example: Processing PEP 634 (Match Statements)

```python
# Generated test would include:
@pytest.mark.min_version_3_10  # PEP 634 added in Python 3.10
@pytest.mark.feature_match     # Feature-specific grouping
def test_pep_634_match_syntax(self):
    """Test PEP 634: Structural Pattern Matching"""
    # Test implementation here
```

## Benefits

### Accurate Testing
- **No false failures** from running future features on old Python
- **Proper coverage** of version-specific behavior
- **Clear compatibility** requirements for each test

### Maintainable CI
- **Automatic filtering** based on Python version
- **Easy expansion** to new Python versions
- **Implementation-aware** testing (CPython vs PyPy)

### Development Clarity  
- **Clear version requirements** for each language feature
- **Systematic organization** of version-specific tests
- **Easy debugging** of version-related issues

## Future Extensions

### Multiple Implementation Support
```python
@pytest.mark.cpython_only
def test_cpython_specific_behavior(self):
    """Test behavior specific to CPython implementation"""
    pass

@pytest.mark.pypy_compatible  
def test_cross_implementation_behavior(self):
    """Test behavior that should work across implementations"""
    pass
```

### Conditional Feature Testing
```python
@pytest.mark.skipif(not has_feature("match_statements"), reason="Implementation doesn't support match")
def test_optional_language_feature(self):
    """Test features that some implementations might not support"""
    pass
```

This version-aware testing strategy ensures conformance tests remain accurate and maintainable as the Python language evolves.