#!/usr/bin/env python3
"""
Test suite for computor v2
"""

from interpreter import Interpreter
from types_system import Rational, Complex, Matrix


def test_rational_operations():
    """Test rational number operations."""
    print("Testing rational numbers...")
    interp = Interpreter()
    
    # Basic arithmetic
    assert interp.execute("2 + 3") == "5"
    assert interp.execute("10 - 4") == "6"
    assert interp.execute("3 * 4") == "12"
    assert interp.execute("15 / 3") == "5"
    assert interp.execute("7 / 2") == "7/2"
    
    # With parentheses
    assert interp.execute("(2 + 3) * 4") == "20"
    assert interp.execute("2 + 3 * 4") == "14"
    
    print("✓ Rational operations passed")


def test_complex_operations():
    """Test complex number operations."""
    print("Testing complex numbers...")
    interp = Interpreter()
    
    # Basic complex
    assert interp.execute("i") == "i"
    assert interp.execute("2 + 3 * i") == "2 + 3i"
    assert interp.execute("5 * i") == "5i"
    
    # Complex arithmetic
    result = interp.execute("(2 + 3*i) + (1 + 2*i)")
    assert result == "3 + 5i"
    
    result = interp.execute("(2 + i) * (3 + 2*i)")
    # (2+i)(3+2i) = 6 + 4i + 3i + 2i^2 = 6 + 7i - 2 = 4 + 7i
    assert result == "4 + 7i"
    
    print("✓ Complex operations passed")


def test_matrix_operations():
    """Test matrix operations."""
    print("Testing matrices...")
    interp = Interpreter()
    
    # Matrix creation
    result = interp.execute("[[1, 2], [3, 4]]")
    assert "1" in result and "2" in result and "3" in result and "4" in result
    
    # Matrix addition
    interp.execute("A = [[1, 2], [3, 4]]")
    interp.execute("B = [[5, 6], [7, 8]]")
    result = interp.execute("A + B")
    assert "6" in result and "8" in result and "10" in result and "12" in result
    
    print("✓ Matrix operations passed")


def test_variable_assignment():
    """Test variable assignment."""
    print("Testing variable assignment...")
    interp = Interpreter()
    
    # Simple assignment
    interp.execute("x = 5")
    assert interp.execute("x") == "5"
    
    # Expression assignment
    interp.execute("y = 2 + 3")
    assert interp.execute("y") == "5"
    
    # Variable to variable
    interp.execute("z = y")
    assert interp.execute("z") == "5"
    
    # Reassignment to different type
    interp.execute("a = 10")
    assert interp.execute("a") == "10"
    interp.execute("a = 2 + 3*i")
    assert interp.execute("a") == "2 + 3i"
    
    print("✓ Variable assignment passed")


def test_equation_solving():
    """Test equation solving."""
    print("Testing equation solving...")
    interp = Interpreter()
    
    # Linear equation
    result = interp.execute("2*x + 5 = 13 ?")
    assert "4" in result or "solution" in result.lower()
    
    # Quadratic with two solutions
    result = interp.execute("x^2 - 5*x + 6 = 0 ?")
    assert "degree: 2" in result.lower()
    
    # Quadratic with discriminant zero
    result = interp.execute("x^2 - 4*x + 4 = 0 ?")
    assert "2" in result
    
    print("✓ Equation solving passed")


def test_mixed_operations():
    """Test operations between types."""
    print("Testing mixed operations...")
    interp = Interpreter()
    
    # Rational with complex
    result = interp.execute("5 + 3*i")
    assert result == "5 + 3i"
    
    # Matrix scalar multiplication
    interp.execute("M = [[1, 2], [3, 4]]")
    result = interp.execute("M * 2")
    assert "2" in result and "4" in result and "6" in result and "8" in result
    
    print("✓ Mixed operations passed")


def main():
    """Run all tests."""
    print("Running computor v2 tests...\n")
    
    try:
        test_rational_operations()
        test_complex_operations()
        test_matrix_operations()
        test_variable_assignment()
        test_equation_solving()
        test_mixed_operations()
        
        print("\n✅ All tests passed!")
        return 0
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
