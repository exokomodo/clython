"""Clython runtime tests — Section 7.11: Import Statements.

Tests that the Clython interpreter correctly handles import statements
including simple imports, from-imports, aliases, and wildcard imports.
"""
import os
import subprocess
import pytest

CLYTHON_BIN = os.environ.get("CLYTHON_BIN")


def clython_run(source: str, *, timeout: int = 10):
    result = subprocess.run(
        [CLYTHON_BIN, "-c", source],
        capture_output=True, text=True, timeout=timeout
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode


pytestmark = pytest.mark.skipif(
    not CLYTHON_BIN, reason="CLYTHON_BIN not set — skipping Clython-specific tests"
)


class TestImportStatementRuntime:
    def test_import_os(self):
        """import os makes os available"""
        out, err, rc = clython_run(
            "import os\nprint(type(os).__name__)"
        )
        assert rc == 0
        assert out == "module"

    def test_import_sys(self):
        """import sys makes sys available"""
        out, err, rc = clython_run(
            "import sys\nprint(type(sys).__name__)"
        )
        assert rc == 0
        assert out == "module"

    def test_import_math(self):
        """import math and use a function"""
        out, err, rc = clython_run(
            "import math\nprint(math.floor(3.7))"
        )
        assert rc == 0
        assert out == "3"

    def test_import_dotted(self):
        """import os.path provides access via os.path"""
        out, err, rc = clython_run(
            "import os.path\nprint(type(os.path).__name__)"
        )
        assert rc == 0
        assert out == "module"

    def test_import_alias(self):
        """import math as m creates alias"""
        out, err, rc = clython_run(
            "import math as m\nprint(m.floor(2.9))"
        )
        assert rc == 0
        assert out == "2"

    def test_import_multiple(self):
        """import os, sys in one statement"""
        out, err, rc = clython_run(
            "import os, sys\nprint(type(os).__name__, type(sys).__name__)"
        )
        assert rc == 0
        assert out == "module module"

    def test_from_import_name(self):
        """from math import sqrt works"""
        out, err, rc = clython_run(
            "from math import sqrt\nprint(sqrt(9))"
        )
        assert rc == 0
        assert out == "3.0"

    def test_from_import_multiple_names(self):
        """from math import sqrt, floor"""
        out, err, rc = clython_run(
            "from math import sqrt, floor\nprint(sqrt(4), floor(3.9))"
        )
        assert rc == 0
        assert out == "2.0 3"

    def test_from_import_alias(self):
        """from math import sqrt as sq"""
        out, err, rc = clython_run(
            "from math import sqrt as sq\nprint(sq(16))"
        )
        assert rc == 0
        assert out == "4.0"

    def test_from_import_os_path(self):
        """from os import path makes path available directly"""
        out, err, rc = clython_run(
            "from os import path\nprint(type(path).__name__)"
        )
        assert rc == 0
        assert out == "module"

    def test_import_nonexistent_raises(self):
        """import of non-existent module raises ImportError/ModuleNotFoundError"""
        out, err, rc = clython_run(
            "try:\n    import nonexistent_module_xyz\nexcept (ImportError, ModuleNotFoundError):\n    print('import error')"
        )
        assert rc == 0
        assert out == "import error"

    def test_from_import_collections(self):
        """from collections import defaultdict"""
        out, err, rc = clython_run(
            "from collections import defaultdict\n"
            "d = defaultdict(int)\nd['a'] += 1\nprint(d['a'])"
        )
        assert rc == 0
        assert out == "1"

    def test_import_in_function(self):
        """import inside a function works at call time"""
        out, err, rc = clython_run(
            "def f():\n    import math\n    return math.pi\n"
            "print(round(f(), 4))"
        )
        assert rc == 0
        assert out == "3.1416"

    def test_import_json_and_use(self):
        """import json and use dumps"""
        out, err, rc = clython_run(
            "import json\nprint(json.dumps({'a': 1}))"
        )
        assert rc == 0
        assert out == '{"a": 1}'

    def test_from_import_star(self):
        """from math import * makes math names available"""
        out, err, rc = clython_run(
            "from math import *\nprint(floor(3.7))"
        )
        assert rc == 0
        assert out == "3"

    def test_import_as_name_not_original(self):
        """after 'import math as m', 'math' is NOT bound"""
        out, err, rc = clython_run(
            "import math as m\n"
            "try:\n    print(math)\nexcept NameError:\n    print('math not bound')"
        )
        assert rc == 0
        assert out == "math not bound"

    def test_from_import_as_name_not_original(self):
        """after 'from math import sqrt as sq', 'sqrt' is NOT bound"""
        out, err, rc = clython_run(
            "from math import sqrt as sq\n"
            "try:\n    sq(4)\n    print('sq works')\nexcept NameError:\n    print('sq not bound')\n"
            "try:\n    sqrt(4)\nexcept NameError:\n    print('sqrt not bound')"
        )
        assert rc == 0
        assert out == "sq works\nsqrt not bound"

    def test_import_random_and_use(self):
        """import random module"""
        out, err, rc = clython_run(
            "import random\nrandom.seed(42)\nprint(type(random.randint(1, 10)).__name__)"
        )
        assert rc == 0
        assert out == "int"
