"""Clython runtime tests — Section 6.1: Arithmetic Conversions.

Tests that the Clython interpreter correctly handles numeric type
promotion rules (bool → int → float → complex) in arithmetic.
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


class TestArithmeticConversionsRuntime:
    def test_int_plus_float_gives_float(self):
        """int + float promotes to float"""
        out, err, rc = clython_run("print(type(1 + 2.0).__name__)")
        assert rc == 0
        assert out == "float"

    def test_float_plus_int_gives_float(self):
        """float + int promotes to float"""
        out, err, rc = clython_run("print(type(2.5 + 1).__name__)")
        assert rc == 0
        assert out == "float"

    def test_int_plus_int_gives_int(self):
        """int + int stays int"""
        out, err, rc = clython_run("print(type(1 + 2).__name__)")
        assert rc == 0
        assert out == "int"

    def test_int_division_gives_float(self):
        """int / int (true division) gives float in Python 3"""
        out, err, rc = clython_run("print(type(5 / 2).__name__)")
        assert rc == 0
        assert out == "float"

    def test_floor_division_int_gives_int(self):
        """int // int gives int"""
        out, err, rc = clython_run("print(type(7 // 2).__name__)")
        assert rc == 0
        assert out == "int"

    def test_float_floor_division_gives_float(self):
        """float // int gives float"""
        out, err, rc = clython_run("print(type(7.0 // 2).__name__)")
        assert rc == 0
        assert out == "float"

    def test_bool_plus_int(self):
        """True + 1 == 2 (bool treated as int)"""
        out, err, rc = clython_run("print(True + 1)")
        assert rc == 0
        assert out == "2"

    def test_false_plus_int(self):
        """False + 5 == 5"""
        out, err, rc = clython_run("print(False + 5)")
        assert rc == 0
        assert out == "5"

    def test_bool_plus_float(self):
        """True + 1.0 gives float"""
        out, err, rc = clython_run("print(type(True + 1.0).__name__, True + 1.0)")
        assert rc == 0
        assert out == "float 2.0"

    def test_bool_times_int(self):
        """True * 10 == 10"""
        out, err, rc = clython_run("print(True * 10)")
        assert rc == 0
        assert out == "10"

    def test_complex_plus_int(self):
        """complex + int gives complex"""
        out, err, rc = clython_run("print(type((1+2j) + 3).__name__)")
        assert rc == 0
        assert out == "complex"

    def test_complex_plus_float(self):
        """complex + float gives complex"""
        out, err, rc = clython_run("print(type((1+2j) + 1.5).__name__)")
        assert rc == 0
        assert out == "complex"

    def test_int_plus_complex(self):
        """int + complex gives complex"""
        out, err, rc = clython_run("print(type(5 + (1+2j)).__name__)")
        assert rc == 0
        assert out == "complex"

    def test_mixed_arithmetic_value_correct(self):
        """1 + 2.0 == 3.0"""
        out, err, rc = clython_run("print(1 + 2.0)")
        assert rc == 0
        assert out == "3.0"

    def test_int_subtraction_value(self):
        """10 - 3 == 7"""
        out, err, rc = clython_run("print(10 - 3)")
        assert rc == 0
        assert out == "7"

    def test_float_multiplication_value(self):
        """2.5 * 4 == 10.0"""
        out, err, rc = clython_run("print(2.5 * 4)")
        assert rc == 0
        assert out == "10.0"

    def test_division_value(self):
        """5 / 2 == 2.5"""
        out, err, rc = clython_run("print(5 / 2)")
        assert rc == 0
        assert out == "2.5"

    def test_floor_division_value(self):
        """7 // 2 == 3"""
        out, err, rc = clython_run("print(7 // 2)")
        assert rc == 0
        assert out == "3"

    def test_modulo_value(self):
        """10 % 3 == 1"""
        out, err, rc = clython_run("print(10 % 3)")
        assert rc == 0
        assert out == "1"

    def test_exponent_int(self):
        """2 ** 10 == 1024"""
        out, err, rc = clython_run("print(2 ** 10)")
        assert rc == 0
        assert out == "1024"

    def test_exponent_float(self):
        """4.0 ** 0.5 == 2.0"""
        out, err, rc = clython_run("print(4.0 ** 0.5)")
        assert rc == 0
        assert out == "2.0"

    def test_chained_promotion(self):
        """1 + 2 + 3.0 gives float"""
        out, err, rc = clython_run("print(type(1 + 2 + 3.0).__name__)")
        assert rc == 0
        assert out == "float"

    def test_bool_bool_arithmetic(self):
        """True + True == 2"""
        out, err, rc = clython_run("print(True + True)")
        assert rc == 0
        assert out == "2"

    def test_negative_int_arithmetic(self):
        """-5 + 3 == -2"""
        out, err, rc = clython_run("print(-5 + 3)")
        assert rc == 0
        assert out == "-2"

    def test_large_int_arithmetic(self):
        """Python int is arbitrary precision"""
        out, err, rc = clython_run("print(10 ** 20 + 1)")
        assert rc == 0
        assert out == "100000000000000000001"
