"""
Equation solver for polynomial equations of degree <= 2
"""

from types_system import Rational, Complex
from evaluator import Evaluator
from parser import Lexer, Parser
import re
from typing import List, Tuple, Union


class EquationSolver:
    """Solves polynomial equations of degree <= 2."""
    
    def __init__(self, evaluator: Evaluator):
        self.evaluator = evaluator
    
    def solve(self, left_ast, right_ast) -> str:
        """
        Solve an equation of the form left = right.
        Returns a string with the solution.
        """
        # Try to simplify to standard form: ax^2 + bx + c = 0
        # For now, we'll handle simple cases
        
        # First, try to identify the variable
        variable = self.find_variable(left_ast, right_ast)
        if not variable:
            # No variable, just evaluate both sides
            left_val = self.evaluator.evaluate(left_ast)
            right_val = self.evaluator.evaluate(right_ast)
            if left_val == right_val:
                return "The equation is always true"
            else:
                return "The equation has no solution"
        
        # Collect terms and coefficients
        left_poly = self.ast_to_polynomial(left_ast, variable)
        right_poly = self.ast_to_polynomial(right_ast, variable)
        
        # Move everything to left side: left - right = 0
        coeffs = {}
        for power, coeff in left_poly.items():
            coeffs[power] = coeffs.get(power, Rational(0)) + coeff
        for power, coeff in right_poly.items():
            coeffs[power] = coeffs.get(power, Rational(0)) - coeff
        
        # Get degree
        degree = max(coeffs.keys()) if coeffs else 0
        
        if degree > 2:
            return f"The polynomial degree is strictly greater than 2, I can't solve."
        
        # Get coefficients a, b, c for ax^2 + bx + c = 0
        c = coeffs.get(0, Rational(0))
        b = coeffs.get(1, Rational(0))
        a = coeffs.get(2, Rational(0))
        
        # Display reduced form
        reduced_form = self.format_polynomial(coeffs, variable)
        result = f"Reduced form: {reduced_form} = 0\n"
        result += f"Polynomial degree: {degree}\n"
        
        # Solve based on degree
        if degree == 0:
            if c.value == 0:
                result += "All real numbers are solutions"
            else:
                result += "No solution"
        elif degree == 1:
            # bx + c = 0 => x = -c/b
            if b.value == 0:
                result += "No solution"
            else:
                x = -c / b
                result += f"The solution is:\n{x}"
        else:  # degree == 2
            # ax^2 + bx + c = 0
            # Use quadratic formula: x = (-b ± √(b²-4ac)) / 2a
            discriminant = b * b - Rational(4) * a * c
            result += f"Discriminant: {discriminant}\n"
            
            if discriminant.value > 0:
                # Two real solutions
                sqrt_disc = Rational(float(discriminant.value) ** 0.5)
                x1 = (-b + sqrt_disc) / (Rational(2) * a)
                x2 = (-b - sqrt_disc) / (Rational(2) * a)
                result += "Discriminant is strictly positive, the two solutions are:\n"
                result += f"{x1}\n{x2}"
            elif discriminant.value == 0:
                # One solution
                x = -b / (Rational(2) * a)
                result += "Discriminant is zero, the solution is:\n"
                result += f"{x}"
            else:
                # Complex solutions
                real_part = -b / (Rational(2) * a)
                imag_part = Rational(float((-discriminant.value) ** 0.5)) / (Rational(2) * a)
                result += "Discriminant is strictly negative, the two complex solutions are:\n"
                c1 = Complex(real_part, imag_part)
                c2 = Complex(real_part, -imag_part)
                result += f"{c1}\n{c2}"
        
        return result
    
    def find_variable(self, *asts) -> str:
        """Find the variable name in the AST."""
        for ast in asts:
            var = self._find_variable_recursive(ast)
            if var:
                return var
        return None
    
    def _find_variable_recursive(self, ast) -> str:
        """Recursively find variable in AST."""
        if not ast or not isinstance(ast, tuple):
            return None
        
        node_type = ast[0]
        
        if node_type == 'variable':
            return ast[1]
        elif node_type in ('binop', 'unary'):
            for i in range(2, len(ast)):
                var = self._find_variable_recursive(ast[i])
                if var:
                    return var
        
        return None
    
    def ast_to_polynomial(self, ast, variable: str) -> dict:
        """
        Convert AST to polynomial coefficients.
        Returns dict mapping power to coefficient.
        """
        if not ast or not isinstance(ast, tuple):
            return {0: Rational(0)}
        
        node_type = ast[0]
        
        if node_type == 'number':
            return {0: Rational(ast[1])}
        
        elif node_type == 'variable':
            if ast[1] == variable:
                return {1: Rational(1)}  # x^1
            else:
                # It's a different variable, treat as constant
                val = self.evaluator.get_variable(ast[1])
                if val is None:
                    raise NameError(f"Variable '{ast[1]}' is not defined")
                if not isinstance(val, (Rational, int, float)):
                    raise TypeError(f"Variable '{ast[1]}' must be a number in equations")
                return {0: Rational(val) if not isinstance(val, Rational) else val}
        
        elif node_type == 'binop':
            op = ast[1]
            left = self.ast_to_polynomial(ast[2], variable)
            right = self.ast_to_polynomial(ast[3], variable)
            
            if op == '+':
                result = {}
                for power, coeff in left.items():
                    result[power] = result.get(power, Rational(0)) + coeff
                for power, coeff in right.items():
                    result[power] = result.get(power, Rational(0)) + coeff
                return result
            
            elif op == '-':
                result = {}
                for power, coeff in left.items():
                    result[power] = result.get(power, Rational(0)) + coeff
                for power, coeff in right.items():
                    result[power] = result.get(power, Rational(0)) - coeff
                return result
            
            elif op == '*':
                result = {}
                for p1, c1 in left.items():
                    for p2, c2 in right.items():
                        power = p1 + p2
                        result[power] = result.get(power, Rational(0)) + c1 * c2
                return result
            
            elif op == '^':
                # Handle x^n where n is a constant
                # left should be the variable, right should be constant
                if len(left) == 1 and 1 in left and left[1].value == 1:
                    # It's x^n
                    if len(right) == 1 and 0 in right:
                        coeff = right[0]
                        power = int(coeff.value)
                        return {power: Rational(1)}
                raise ValueError("Only simple polynomial forms are supported")
            
            else:
                raise ValueError(f"Operator '{op}' not supported in polynomial equations")
        
        elif node_type == 'unary':
            op = ast[1]
            operand = self.ast_to_polynomial(ast[2], variable)
            if op == '-':
                result = {}
                for power, coeff in operand.items():
                    result[power] = -coeff
                return result
            raise ValueError(f"Unary operator '{op}' not supported")
        
        else:
            raise ValueError(f"Node type '{node_type}' not supported in equations")
    
    def format_polynomial(self, coeffs: dict, variable: str) -> str:
        """Format polynomial coefficients as a string."""
        if not coeffs or all(c.value == 0 for c in coeffs.values()):
            return "0"
        
        powers = sorted(coeffs.keys(), reverse=True)
        terms = []
        
        for power in powers:
            coeff = coeffs[power]
            if coeff.value == 0:
                continue
            
            term = ""
            coeff_str = str(coeff)
            
            if power == 0:
                term = coeff_str
            elif power == 1:
                if coeff.value == 1:
                    term = variable
                elif coeff.value == -1:
                    term = f"-{variable}"
                else:
                    term = f"{coeff_str} * {variable}"
            else:
                if coeff.value == 1:
                    term = f"{variable}^{power}"
                elif coeff.value == -1:
                    term = f"-{variable}^{power}"
                else:
                    term = f"{coeff_str} * {variable}^{power}"
            
            # Handle signs
            if terms and coeff.value > 0:
                term = "+ " + term
            elif terms and coeff.value < 0 and term.startswith("-"):
                term = "- " + term[1:]
            
            terms.append(term)
        
        return " ".join(terms) if terms else "0"
