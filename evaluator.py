"""
Evaluator for mathematical expressions
"""

from types_system import Rational, Complex, Matrix
from typing import Dict, Any, Union
import math
import cmath


class Evaluator:
    """Evaluates parsed expressions."""
    
    def __init__(self, variables: Dict[str, Any] = None):
        # Store variables case-insensitively: keys are lowercase
        self.variables = {}
        if variables:
            for k, v in variables.items():
                self.variables[k.lower()] = v
        # Angle mode for trigonometric functions: 'radians' or 'degrees'
        # Default: radians
        self.angle_mode = 'radians'

        # Built-in functions (lowercase keys)
        # Each builtin is a Python callable that accepts one argument (Rational/Complex/int/float)
        self.builtins = {
            'sin': self._builtin_sin,
            'cos': self._builtin_cos,
            'tan': self._builtin_tan,
            'exp': self._builtin_exp,
            'log': self._builtin_log,
            'sqrt': self._builtin_sqrt,
            'norm': self._builtin_norm,
            'inv': self._builtin_inv,
            'abs': self._builtin_abs,
            'floor': self._builtin_floor,
            'ceil': self._builtin_ceil,
        }
    
    def evaluate(self, ast):
        """Evaluate an AST node."""
        if ast is None:
            return None
        
        node_type = ast[0]
        
        if node_type == 'number':
            value = ast[1]
            if '.' in value:
                return Rational(float(value))
            return Rational(int(value))
        
        elif node_type == 'variable':
            var_name = ast[1]
            # Lookup variables case-insensitively via get_variable
            val = self.get_variable(var_name)
            if val is None:
                raise NameError(f"Variable '{var_name}' is not defined")
            return val
        
        elif node_type == 'imaginary':
            return Complex(0, 1)
        
        elif node_type == 'matrix':
            rows_ast = ast[1]
            rows = []
            for row_ast in rows_ast:
                row = [self.evaluate(elem) for elem in row_ast]
                # Convert to Rational if needed
                row_values = []
                for elem in row:
                    if isinstance(elem, Rational):
                        row_values.append(elem)
                    elif isinstance(elem, (int, float)):
                        row_values.append(Rational(elem))
                    else:
                        raise TypeError(f"Matrix elements must be rational numbers, got {type(elem)}")
                rows.append(row_values)
            return Matrix(rows)
        
        elif node_type == 'binop':
            op = ast[1]
            left = self.evaluate(ast[2])
            right = self.evaluate(ast[3])
            return self.apply_binop(op, left, right)
        
        elif node_type == 'unary':
            op = ast[1]
            operand = self.evaluate(ast[2])
            if op == '-':
                return -operand
            raise ValueError(f"Unknown unary operator: {op}")

        elif node_type == 'call':
            # Function call: ('call', name, arg_ast)
            func_name = ast[1]
            arg_ast = ast[2]
            arg_value = self.evaluate(arg_ast)
            func = self.get_variable(func_name)
            if func is None:
                raise NameError(f"Function '{func_name}' is not defined")
            # Lazy: expect a Function object
            from types_system import Function
            # If it's a user-defined Function, evaluate its AST in a local evaluator
            if isinstance(func, Function):
                local_vars = dict(self.variables)
                local_vars[func.arg_name] = arg_value
                local_evaluator = Evaluator(local_vars)
                return local_evaluator.evaluate(func.body_ast)

            # If it's a python callable (builtin), call it with the evaluated argument
            if callable(func):
                return func(arg_value)

            raise TypeError(f"'{func_name}' is not callable")
        
        else:
            raise ValueError(f"Unknown node type: {node_type}")
    
    def apply_binop(self, op: str, left, right):
        """Apply binary operation."""
        if op == '+':
            return left + right
        elif op == '-':
            return left - right
        elif op == '*':
            # Matrix * Matrix has two semantics:
            # - If both have identical dimensions: element-wise multiplication (previous behavior)
            # - If dimensions are compatible for matrix multiplication (cols of left == rows of right)
            #   and at least one operand is vector-shaped (1xN or Nx1), treat '*' as matmul convenience
            if isinstance(left, Matrix) and isinstance(right, Matrix):
                # exact same dims -> element-wise
                if left.rows == right.rows and left.cols == right.cols:
                    result = []
                    for i in range(left.rows):
                        row = []
                        for j in range(left.cols):
                            row.append(left.data[i][j] * right.data[i][j])
                        result.append(row)
                    return Matrix(result)

                # if shapes are compatible for matrix multiplication, and one is vector-shaped,
                # do matrix multiplication as a convenience for matrix-vector operations
                if left.cols == right.rows and (left.is_vector() or right.is_vector()):
                    return left.matmul(right)

                raise ValueError("Matrix dimensions incompatible for '*' operation")

            return left * right
        elif op == '/':
            return left / right
        elif op == '%':
            # Modulo operator: only supported for rationals (or ints/floats)
            # Complex modulo is not defined here.
            if isinstance(left, Rational) and isinstance(right, Rational):
                return left % right
            elif isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return Rational(left % right)
            else:
                raise TypeError("Modulo operator supported only for rational/integer operands")
        elif op == '**' or op == 'MATMUL':
            # Matrix multiplication operator '**'
            if isinstance(left, Matrix) and isinstance(right, Matrix):
                return left.matmul(right)
            # Allow scalar * matrix with matmul as well? disallow to avoid ambiguity
            raise TypeError("Matrix multiplication '**' requires two matrices")
        elif op == '^':
            # Handle power operation
            # Rational power
            if isinstance(left, Rational) and isinstance(right, Rational):
                return left ** right
            # Matrix power: integer non-negative exponent
            if isinstance(left, Matrix):
                # Right must be Rational with integer >= 0
                if isinstance(right, Rational) and right.value.denominator == 1:
                    n = int(right.value)
                    if n == 0:
                        if left.rows != left.cols:
                            raise ValueError("Matrix power requires a square matrix")
                        # identity
                        I = []
                        for i in range(left.rows):
                            row = []
                            for j in range(left.cols):
                                row.append(Rational(1) if i == j else Rational(0))
                            I.append(row)
                        return Matrix(I)
                    if n > 0:
                        if left.rows != left.cols:
                            raise ValueError("Matrix power requires a square matrix")
                        result = left
                        for _ in range(n - 1):
                            result = result.matmul(left)
                        return result
                    # negative integer exponent: compute inverse then positive power
                    if n < 0:
                        if left.rows != left.cols:
                            raise ValueError("Matrix power requires a square matrix")
                        inv = left.inverse()
                        k = -n
                        if k == 1:
                            return inv
                        result = inv
                        for _ in range(k - 1):
                            result = result.matmul(inv)
                        return result
                else:
                    raise TypeError("Matrix exponent must be an integer")
            if isinstance(left, Complex):
                # Complex power is not implemented for simplicity
                raise TypeError("Complex power operation not supported")
            else:
                raise TypeError(f"Cannot apply power to {type(left)} and {type(right)}")
        else:
            raise ValueError(f"Unknown operator: {op}")
    
    def assign(self, var_name: str, value):
        """Assign a value to a variable (case-insensitive)."""
        if var_name.lower() == 'i':
            raise NameError("'i' is reserved for the imaginary unit and cannot be used as a variable name")
        self.variables[var_name.lower()] = value
    
    def get_variable(self, var_name: str):
        """Get a variable value."""
        key = var_name.lower()
        if key in self.variables:
            return self.variables.get(key)
        # fall back to builtins
        return self.builtins.get(key)

    # --- builtin implementations ---
    def _to_python_complex(self, v):
        """Convert Rational/Complex/int/float to a python complex number."""
        if isinstance(v, Complex):
            return complex(float(v.real.value), float(v.imag.value))
        if isinstance(v, Rational):
            return complex(float(v.value), 0.0)
        if isinstance(v, (int, float)):
            return complex(float(v), 0.0)
        raise TypeError(f"Cannot convert {type(v)} to numeric for builtin")

    def set_angle_mode(self, mode: str):
        """Set angle mode for trig functions. mode is 'radians' or 'degrees'."""
        if mode.lower() in ('rad', 'radians'):
            self.angle_mode = 'radians'
        elif mode.lower() in ('deg', 'degree', 'degrees'):
            self.angle_mode = 'degrees'
        else:
            raise ValueError("Unknown angle mode: choose 'radians' or 'degrees'")

    def _from_python_number(self, z):
        """Convert a python real/complex number to Rational or Complex where appropriate."""
        from types_system import Rational, Complex
        if isinstance(z, complex):
            real = Rational(float(z.real))
            imag = Rational(float(z.imag))
            if imag.value == 0:
                return real
            return Complex(real, imag)
        # real
        return Rational(float(z))

    def _builtin_sin(self, arg):
        z = self._to_python_complex(arg)
        # If angle mode is degrees and z is purely real, convert degrees -> radians
        if self.angle_mode == 'degrees' and z.imag == 0:
            z = complex(math.radians(z.real), 0.0)
        res = cmath.sin(z)
        return self._from_python_number(res)

    def _builtin_cos(self, arg):
        z = self._to_python_complex(arg)
        if self.angle_mode == 'degrees' and z.imag == 0:
            z = complex(math.radians(z.real), 0.0)
        res = cmath.cos(z)
        return self._from_python_number(res)

    def _builtin_tan(self, arg):
        z = self._to_python_complex(arg)
        if self.angle_mode == 'degrees' and z.imag == 0:
            z = complex(math.radians(z.real), 0.0)
        res = cmath.tan(z)
        return self._from_python_number(res)

    def _builtin_exp(self, arg):
        z = self._to_python_complex(arg)
        res = cmath.exp(z)
        return self._from_python_number(res)

    def _builtin_log(self, arg):
        z = self._to_python_complex(arg)
        res = cmath.log(z)
        return self._from_python_number(res)

    def _builtin_sqrt(self, arg):
        z = self._to_python_complex(arg)
        res = cmath.sqrt(z)
        return self._from_python_number(res)

    def _builtin_abs(self, arg):
        # magnitude
        z = self._to_python_complex(arg)
        val = abs(z)
        return self._from_python_number(val)

    def _builtin_norm(self, arg):
        """Compute a norm:
        - scalar (Rational/Complex/int/float): magnitude (same as abs)
        - Matrix: Frobenius norm (sqrt of sum of squared magnitudes of entries)
        """
        from types_system import Matrix
        # scalar-like: delegate to abs
        if isinstance(arg, (int, float, Rational, Complex)):
            return self._builtin_abs(arg)
        if isinstance(arg, Matrix):
            # sum squares of absolute values of each entry
            total = 0+0j
            for i in range(arg.rows):
                for j in range(arg.cols):
                    entry = arg.data[i][j]
                    z = self._to_python_complex(entry)
                    total += (z.real * z.real + z.imag * z.imag)
            # total is real non-negative
            res = math.sqrt(total.real)
            return self._from_python_number(res)
        # If it's a 1-D matrix (vector-like) it will still be handled above as Matrix
        raise TypeError(f"norm() not supported for type {type(arg)}")

    def _builtin_inv(self, arg):
        """Return inverse of a matrix or reciprocal of a scalar.

        For scalars (Rational/int/float) returns 1/arg (Rational where possible).
        For Complex returns reciprocal as Complex.
        For Matrix returns exact inverse (Matrix.inverse) or raises if not invertible.
        """
        from types_system import Matrix, Rational, Complex
        if isinstance(arg, Matrix):
            return arg.inverse()
        if isinstance(arg, Rational):
            if arg.value == 0:
                raise ZeroDivisionError("Division by zero")
            return Rational(1) / arg
        if isinstance(arg, Complex):
            # (a+bi)^{-1} = (a-bi)/(a^2 + b^2)
            denom = arg.real * arg.real + arg.imag * arg.imag
            if denom.value == 0:
                raise ZeroDivisionError("Division by zero")
            real = arg.real / denom
            imag = -arg.imag / denom
            return Complex(real, imag)
        if isinstance(arg, (int, float)):
            if arg == 0:
                raise ZeroDivisionError("Division by zero")
            return Rational(1) / Rational(arg)
        raise TypeError(f"inv() not supported for type {type(arg)}")

    def _builtin_floor(self, arg):
        z = self._to_python_complex(arg)
        if z.imag != 0:
            raise TypeError("floor/ceil only supported for real arguments")
        return Rational(math.floor(z.real))

    def _builtin_ceil(self, arg):
        z = self._to_python_complex(arg)
        if z.imag != 0:
            raise TypeError("floor/ceil only supported for real arguments")
        return Rational(math.ceil(z.real))
