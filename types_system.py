"""
Type system for computor v2
Includes: Rational, Complex, Matrix types
"""

from fractions import Fraction
from typing import Union, List
import re


class Rational:
    """Rational number representation using Fraction."""
    
    def __init__(self, value):
        if isinstance(value, Fraction):
            self.value = value
        elif isinstance(value, Rational):
            self.value = value.value
        elif isinstance(value, (int, float)):
            self.value = Fraction(value).limit_denominator()
        elif isinstance(value, str):
            self.value = Fraction(value).limit_denominator()
        else:
            self.value = Fraction(value).limit_denominator()
    
    def __add__(self, other):
        if isinstance(other, Rational):
            return Rational(self.value + other.value)
        elif isinstance(other, (int, float)):
            return Rational(self.value + Fraction(other))
        elif isinstance(other, Complex):
            # Convert to Complex and add
            return Complex(self, 0) + other
        raise TypeError(f"Cannot add Rational and {type(other)}")
    
    def __sub__(self, other):
        if isinstance(other, Rational):
            return Rational(self.value - other.value)
        elif isinstance(other, (int, float)):
            return Rational(self.value - Fraction(other))
        elif isinstance(other, Complex):
            # Convert to Complex and subtract
            return Complex(self, 0) - other
        raise TypeError(f"Cannot subtract Rational and {type(other)}")
    
    def __mul__(self, other):
        if isinstance(other, Rational):
            return Rational(self.value * other.value)
        elif isinstance(other, (int, float)):
            return Rational(self.value * Fraction(other))
        elif isinstance(other, Complex):
            # Convert to Complex and multiply
            return Complex(self, 0) * other
        raise TypeError(f"Cannot multiply Rational and {type(other)}")
    
    def __truediv__(self, other):
        if isinstance(other, Rational):
            if other.value == 0:
                raise ZeroDivisionError("Division by zero")
            return Rational(self.value / other.value)
        elif isinstance(other, (int, float)):
            if other == 0:
                raise ZeroDivisionError("Division by zero")
            return Rational(self.value / Fraction(other))
        elif isinstance(other, Complex):
            # Convert to Complex and divide
            return Complex(self, 0) / other
        raise TypeError(f"Cannot divide Rational and {type(other)}")
    
    def __pow__(self, other):
        if isinstance(other, Rational):
            exp = other.value
            if exp.denominator == 1:
                return Rational(self.value ** int(exp))
            else:
                # For fractional powers, convert to float
                return Rational(float(self.value) ** float(exp))
        elif isinstance(other, int):
            return Rational(self.value ** other)
        raise TypeError(f"Cannot exponentiate Rational with {type(other)}")
    
    def __neg__(self):
        return Rational(-self.value)
    
    def __str__(self):
        if self.value.denominator == 1:
            return str(self.value.numerator)
        return f"{self.value.numerator}/{self.value.denominator}"
    
    def __repr__(self):
        return f"Rational({str(self)})"
    
    def __eq__(self, other):
        if isinstance(other, Rational):
            return self.value == other.value
        return False

    def __mod__(self, other):
        """Modulo operation for rationals."""
        from fractions import Fraction
        if isinstance(other, Rational):
            if other.value == 0:
                raise ZeroDivisionError("Modulo by zero")
            return Rational(self.value % other.value)
        elif isinstance(other, (int, float)):
            if other == 0:
                raise ZeroDivisionError("Modulo by zero")
            return Rational(self.value % Fraction(other))
        raise TypeError(f"Cannot modulo Rational and {type(other)}")


class Complex:
    """Complex number with rational coefficients."""
    
    def __init__(self, real, imag=0):
        if isinstance(real, Rational):
            self.real = real
        else:
            self.real = Rational(real)
            
        if isinstance(imag, Rational):
            self.imag = imag
        else:
            self.imag = Rational(imag)
    
    def __add__(self, other):
        if isinstance(other, Complex):
            return Complex(self.real + other.real, self.imag + other.imag)
        elif isinstance(other, (Rational, int, float)):
            return Complex(self.real + Rational(other), self.imag)
        raise TypeError(f"Cannot add Complex and {type(other)}")
    
    def __sub__(self, other):
        if isinstance(other, Complex):
            return Complex(self.real - other.real, self.imag - other.imag)
        elif isinstance(other, (Rational, int, float)):
            return Complex(self.real - Rational(other), self.imag)
        raise TypeError(f"Cannot subtract Complex and {type(other)}")
    
    def __mul__(self, other):
        if isinstance(other, Complex):
            # (a + bi)(c + di) = (ac - bd) + (ad + bc)i
            real = self.real * other.real - self.imag * other.imag
            imag = self.real * other.imag + self.imag * other.real
            return Complex(real, imag)
        elif isinstance(other, (Rational, int, float)):
            rat = Rational(other)
            return Complex(self.real * rat, self.imag * rat)
        raise TypeError(f"Cannot multiply Complex and {type(other)}")
    
    def __truediv__(self, other):
        if isinstance(other, Complex):
            # (a + bi)/(c + di) = [(a + bi)(c - di)] / (c² + d²)
            denom = other.real * other.real + other.imag * other.imag
            if denom.value == 0:
                raise ZeroDivisionError("Division by zero")
            real = (self.real * other.real + self.imag * other.imag) / denom
            imag = (self.imag * other.real - self.real * other.imag) / denom
            return Complex(real, imag)
        elif isinstance(other, (Rational, int, float)):
            rat = Rational(other)
            if rat.value == 0:
                raise ZeroDivisionError("Division by zero")
            return Complex(self.real / rat, self.imag / rat)
        raise TypeError(f"Cannot divide Complex and {type(other)}")
    
    def __neg__(self):
        return Complex(-self.real, -self.imag)
    
    def __str__(self):
        if self.imag.value == 0:
            return str(self.real)
        elif self.real.value == 0:
            if self.imag.value == 1:
                return "i"
            elif self.imag.value == -1:
                return "-i"
            return f"{self.imag}i"
        else:
            imag_str = str(self.imag)
            if self.imag.value > 0:
                if self.imag.value == 1:
                    return f"{self.real} + i"
                return f"{self.real} + {imag_str}i"
            else:
                if self.imag.value == -1:
                    return f"{self.real} - i"
                return f"{self.real} - {imag_str[1:]}i"
    
    def __repr__(self):
        return f"Complex({self.real}, {self.imag})"
    
    def __eq__(self, other):
        if isinstance(other, Complex):
            return self.real == other.real and self.imag == other.imag
        return False


class Matrix:
    """Matrix type with rational elements."""
    
    def __init__(self, data: List[List]):
        if not data or not data[0]:
            raise ValueError("Matrix cannot be empty")
        
        # Convert all elements to Rational
        self.rows = len(data)
        self.cols = len(data[0])
        
        # Check all rows have same length
        for row in data:
            if len(row) != self.cols:
                raise ValueError("All rows must have the same length")
        
        self.data = []
        for row in data:
            new_row = []
            for elem in row:
                if isinstance(elem, Rational):
                    new_row.append(elem)
                else:
                    new_row.append(Rational(elem))
            self.data.append(new_row)
    
    def __add__(self, other):
        if not isinstance(other, Matrix):
            raise TypeError("Can only add Matrix to Matrix")
        if self.rows != other.rows or self.cols != other.cols:
            raise ValueError("Matrices must have same dimensions for addition")
        
        result = []
        for i in range(self.rows):
            row = []
            for j in range(self.cols):
                row.append(self.data[i][j] + other.data[i][j])
            result.append(row)
        return Matrix(result)
    
    def __sub__(self, other):
        if not isinstance(other, Matrix):
            raise TypeError("Can only subtract Matrix from Matrix")
        if self.rows != other.rows or self.cols != other.cols:
            raise ValueError("Matrices must have same dimensions for subtraction")
        
        result = []
        for i in range(self.rows):
            row = []
            for j in range(self.cols):
                row.append(self.data[i][j] - other.data[i][j])
            result.append(row)
        return Matrix(result)
    
    def __mul__(self, other):
        if isinstance(other, Matrix):
            # Element-wise multiplication: dimensions must match
            if self.rows != other.rows or self.cols != other.cols:
                raise ValueError("Matrix dimensions must match for element-wise multiplication")

            result = []
            for i in range(self.rows):
                row = []
                for j in range(self.cols):
                    row.append(self.data[i][j] * other.data[i][j])
                result.append(row)
            return Matrix(result)
        elif isinstance(other, (Rational, int, float)):
            # Scalar multiplication
            rat = Rational(other) if not isinstance(other, Rational) else other
            result = []
            for i in range(self.rows):
                row = []
                for j in range(self.cols):
                    row.append(self.data[i][j] * rat)
                result.append(row)
            return Matrix(result)
        raise TypeError(f"Cannot multiply Matrix and {type(other)}")

    def matmul(self, other):
        """Matrix multiplication (dot product) operator for Matrix objects."""
        if not isinstance(other, Matrix):
            raise TypeError("Matrix multiplication requires another Matrix")
        if self.cols != other.rows:
            raise ValueError("Matrix dimensions incompatible for multiplication")

        result = []
        for i in range(self.rows):
            row = []
            for j in range(other.cols):
                sum_val = Rational(0)
                for k in range(self.cols):
                    sum_val = sum_val + (self.data[i][k] * other.data[k][j])
                row.append(sum_val)
            result.append(row)
        return Matrix(result)
    
    def __str__(self):
        # Render each row on its own line for readability, without outer brackets
        lines = []
        for row in self.data:
            elements = [str(elem) for elem in row]
            lines.append("[ " + " , ".join(elements) + " ]")
        return "\n".join(lines)
    
    def __repr__(self):
        return f"Matrix({self.data})"
    
    def __eq__(self, other):
        if not isinstance(other, Matrix):
            return False
        if self.rows != other.rows or self.cols != other.cols:
            return False
        for i in range(self.rows):
            for j in range(self.cols):
                if self.data[i][j] != other.data[i][j]:
                    return False
        return True


class Function:
    """Simple function container for single-variable functions.

    Stores the argument name and the AST for the function body.
    """
    def __init__(self, arg_name: str, body_ast, name: str = None):
        self.arg_name = arg_name
        self.body_ast = body_ast
        self.name = name

    def __repr__(self):
        return f"Function(name={self.name}, arg={self.arg_name}, body={self.body_ast})"
