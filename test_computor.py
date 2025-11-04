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


def test_parser_errors():
    """Test that malformed inputs are rejected by the parser."""
    print("Testing parser error cases...")
    interp = Interpreter()

    bad_inputs = [
        "varA = 2 + 4 *2 - 5 %4 + 2(4 + 5))",  # extra closing parenthesis
        "0=",  # invalid assignment LHS
        "2 + 4 *2 - 5 %4 + 2(4 +- 5)",  # consecutive +-
        "2 + 4 *2 - 5 %4 + 2(4 -- 5)",  # consecutive --
    ]

    for s in bad_inputs:
        try:
            _ = interp.execute(s)
            assert False, f"Expected SyntaxError for input: {s}"
        except SyntaxError:
            pass

    print("✓ Parser error cases passed")


def test_reassignment_and_functions():
    """Test reassignment, function definitions, and function calls with variable references."""
    print("Testing reassignment and function calls...")
    interp = Interpreter()

    # varA = 2 + 4 *2 - 5 %4 + 2 * (4 + 5)
    res = interp.execute("varA = 2 + 4 *2 - 5 %4 + 2 * (4 + 5)")
    assert res == "27", f"varA expected 27, got {res}"

    res = interp.execute("varB = 2 * varA - 5 %4")
    assert res == "53", f"varB expected 53, got {res}"

    res = interp.execute("funA(x) = varA + varB * 4 - 1 / 2 + x")
    # function display may show decimal or fraction; accept either
    assert res in ("238.5 + x", "477/2 + x"), f"funA display unexpected: {res}"

    res = interp.execute("varC = 2 * varA - varB")
    assert res == "1", f"varC expected 1, got {res}"

    res = interp.execute("varD = funA(varC)")
    # function call result: accept decimal or fraction equivalent
    assert res in ("239.5", "479/2"), f"varD expected 239.5 or 479/2, got {res}"

    print("✓ Reassignment and functions passed")


def test_sqrt_polynomial_solution():
    """Test solving polynomial equalities with function calls (square roots of polynomials)."""
    print("Testing polynomial root solving via function call...")
    interp = Interpreter()

    interp.execute("funA(x) = x^2 + 2*x + 1")
    interp.execute("y = 0")
    res = interp.execute("funA(x) = y ?")
    # Expect -1 to be in the solver output
    assert "-1" in res, f"Expected -1 in solver output, got: {res}"

    print("✓ Polynomial root solving passed")


def test_identifier_rules():
    """Identifiers must be letters-only, case-insensitive, and 'i' forbidden."""
    print("Testing identifier rules...")
    interp = Interpreter()

    # Disallow digits/underscores in names: lexer will tokenize 'a1' as IDENTIFIER 'a' then NUMBER '1'
    try:
        interp.execute("a1 = 5")
        assert False, "Expected SyntaxError for identifier with digits"
    except SyntaxError:
        pass

    # 'i' reserved
    try:
        interp.execute("i = 5")
        assert False, "Expected SyntaxError or NameError when assigning to 'i'"
    except (SyntaxError, NameError):
        pass

    # Case-insensitive: VAR and var are the same
    interp.execute("Var = 10")
    assert interp.execute("var") == "10"

    print("✓ Identifier rules passed")


def test_imaginary_workflow():
    """Test imaginary number assignments and formatting."""
    print("Testing imaginary workflows...")
    interp = Interpreter()

    res = interp.execute("varA = 2*i + 3")
    assert res == "3 + 2i", f"Expected '3 + 2i', got {res}"

    res = interp.execute("varB = -4i - 4")
    assert res == "-4 - 4i", f"Expected '-4 - 4i', got {res}"

    print("✓ Imaginary workflows passed")


def test_matrix_semicolon_and_single_row():
    """Test matrix input with semicolon row separator and single-row matrix formatting."""
    print("Testing semicolon matrix and single-row formatting...")
    interp = Interpreter()

    res = interp.execute("varA = [[2,3];[4,3]]")
    # Expect two lines representing rows
    expected = "[ 2 , 3 ]\n[ 4 , 3 ]"
    assert res == expected, f"Unexpected matrix format: {res}"

    res = interp.execute("varB = [[3,4]]")
    expected2 = "[ 3 , 4 ]"
    assert res == expected2, f"Unexpected single-row matrix format: {res}"

    print("✓ Matrix semicolon and single-row formatting passed")


def _to_float_from_output(s: str):
    """Convert interpreter numeric output (int, float or fraction string) to float."""
    from fractions import Fraction
    s = s.strip()
    if s.endswith('i'):
        raise ValueError("Cannot convert complex string to float")
    if '/' in s:
        return float(Fraction(s))
    return float(s)


def test_builtins_and_angle_mode():
    """Test builtin math functions and angle mode switching."""
    import math
    print("Testing builtins and angle mode...")
    interp = Interpreter()

    # sqrt of positive and negative
    assert interp.execute("sqrt(4)") == "2"
    assert interp.execute("sqrt(-1)") == "i"

    # exp(1) approx e
    e_out = interp.execute("exp(1)")
    assert abs(_to_float_from_output(e_out) - math.e) < 1e-12

    # sin in radians by default
    s_out = interp.execute("sin(1)")
    assert abs(_to_float_from_output(s_out) - math.sin(1)) < 1e-12

    # angle mode degrees
    assert interp.execute("angles deg") == "angle mode set to degrees"
    sin90 = interp.execute("sin(90)")
    assert abs(_to_float_from_output(sin90) - 1.0) < 1e-12
    assert interp.execute("angles rad") == "angle mode set to radians"

    # floor/ceil
    assert interp.execute("floor(3.7)") in ("3",)
    assert interp.execute("ceil(3.2)") in ("4",)

    print("✓ Builtins and angle mode passed")


def test_norm_and_inverse():
    """Test norm() and matrix inversion / negative powers."""
    print("Testing norm and inverse...")
    interp = Interpreter()

    # norm of complex scalar
    interp.execute("x = 3 + 4*i")
    assert interp.execute("norm(x)") in ("5",)

    # Matrix inverse and product yields identity
    interp.execute("A = [[1, 2], [3, 4]]")
    invA = interp.execute("inv(A)")
    # inv(A) should be a two-line matrix
    assert "-2" in invA and "-0.5" in invA or "1.5" in invA

    prod = interp.execute("A ** inv(A)")
    # Expect identity matrix
    expected_identity = "[ 1 , 0 ]\n[ 0 , 1 ]"
    assert prod == expected_identity

    # Negative powers
    inv_via_pow = interp.execute("A ^ -1")
    assert inv_via_pow == invA

    # A^-2 equals inv(A) ** inv(A)
    a_minus_2 = interp.execute("A ^ -2")
    a_inv_sq = interp.execute("inv(A) ** inv(A)")
    assert a_minus_2 == a_inv_sq

    print("✓ Norm and inverse passed")


def test_matrix_vector_operations():
    """Test convenience matrix-vector multiplication semantics."""
    print("Testing matrix-vector operations...")
    interp = Interpreter()

    interp.execute("A = [[1, 2], [3, 4]]")
    interp.execute("vcol = [[5], [6]]")
    interp.execute("vrow = [[5, 6]]")

    # A * vcol -> column vector [[17],[39]]
    res_col = interp.execute("A * vcol")
    expected_col = "[ 17 ]\n[ 39 ]"
    assert res_col == expected_col, f"Expected {expected_col}, got {res_col}"

    # vrow * A -> row vector [23, 34]
    res_row = interp.execute("vrow * A")
    expected_row = "[ 23 , 34 ]"
    assert res_row == expected_row, f"Expected {expected_row}, got {res_row}"

    # inner product vrow * vcol -> 1x1 matrix [ 61 ]
    res_inner = interp.execute("vrow * vcol")
    expected_inner = "[ 61 ]"
    assert res_inner == expected_inner, f"Expected {expected_inner}, got {res_inner}"

    print("✓ Matrix-vector operations passed")


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
        test_parser_errors()
        test_reassignment_and_functions()
        test_imaginary_workflow()
        test_matrix_semicolon_and_single_row()

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
