"""
Evaluator for mathematical expressions
"""

from types_system import Rational, Complex, Matrix
from typing import Dict, Any, Union
import math


class Evaluator:
    """Evaluates parsed expressions."""
    
    def __init__(self, variables: Dict[str, Any] = None):
        # Store variables case-insensitively: keys are lowercase
        self.variables = {}
        if variables:
            for k, v in variables.items():
                self.variables[k.lower()] = v
    
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
            if not isinstance(func, Function):
                raise TypeError(f"'{func_name}' is not callable")

            # Prepare a local variable environment where the argument name is bound
            local_vars = dict(self.variables)
            local_vars[func.arg_name] = arg_value
            # Evaluate the function body with the combined environment
            local_evaluator = Evaluator(local_vars)
            return local_evaluator.evaluate(func.body_ast)
        
        else:
            raise ValueError(f"Unknown node type: {node_type}")
    
    def apply_binop(self, op: str, left, right):
        """Apply binary operation."""
        if op == '+':
            return left + right
        elif op == '-':
            return left - right
        elif op == '*':
            # Element-wise multiplication for matrices; scalar * matrix handled in types
            if isinstance(left, Matrix) and isinstance(right, Matrix):
                # element-wise: dimensions must match
                if left.rows != right.rows or left.cols != right.cols:
                    raise ValueError("Matrix dimensions must match for element-wise multiplication")
                result = []
                for i in range(left.rows):
                    row = []
                    for j in range(left.cols):
                        row.append(left.data[i][j] * right.data[i][j])
                    result.append(row)
                return Matrix(result)
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
                if isinstance(right, Rational) and right.value.denominator == 1 and right.value >= 0:
                    n = int(right.value)
                    # Define matrix power by repeated matrix multiplication
                    if left.rows != left.cols:
                        raise ValueError("Matrix power requires a square matrix")
                    # exponent 0 -> identity
                    if n == 0:
                        # identity
                        I = []
                        for i in range(left.rows):
                            row = []
                            for j in range(left.cols):
                                row.append(Rational(1) if i == j else Rational(0))
                            I.append(row)
                        return Matrix(I)
                    # repeated multiplication
                    result = left
                    for _ in range(n - 1):
                        # matrix multiplication
                        result = result.matmul(left)
                    return result
                else:
                    raise TypeError("Matrix exponent must be a non-negative integer")
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
        return self.variables.get(var_name.lower())
