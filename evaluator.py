"""
Evaluator for mathematical expressions
"""

from types_system import Rational, Complex, Matrix
from typing import Dict, Any, Union
import math


class Evaluator:
    """Evaluates parsed expressions."""
    
    def __init__(self, variables: Dict[str, Any] = None):
        self.variables = variables if variables is not None else {}
    
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
            if var_name not in self.variables:
                raise NameError(f"Variable '{var_name}' is not defined")
            return self.variables[var_name]
        
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
        
        else:
            raise ValueError(f"Unknown node type: {node_type}")
    
    def apply_binop(self, op: str, left, right):
        """Apply binary operation."""
        if op == '+':
            return left + right
        elif op == '-':
            return left - right
        elif op == '*':
            return left * right
        elif op == '/':
            return left / right
        elif op == '^':
            # Handle power operation
            if isinstance(left, Rational) and isinstance(right, Rational):
                return left ** right
            elif isinstance(left, Complex):
                # Complex power is not implemented for simplicity
                raise TypeError("Complex power operation not supported")
            else:
                raise TypeError(f"Cannot apply power to {type(left)} and {type(right)}")
        else:
            raise ValueError(f"Unknown operator: {op}")
    
    def assign(self, var_name: str, value):
        """Assign a value to a variable."""
        self.variables[var_name] = value
    
    def get_variable(self, var_name: str):
        """Get a variable value."""
        if var_name in self.variables:
            return self.variables[var_name]
        return None
