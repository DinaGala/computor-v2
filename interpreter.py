"""
Main interpreter module
Coordinates parsing, evaluation, and solving
"""

from parser import Lexer, Parser
from evaluator import Evaluator
from solver import EquationSolver
from types_system import Rational, Complex, Matrix


class Interpreter:
    """Main interpreter for computor v2."""
    
    def __init__(self):
        self.evaluator = Evaluator()
        self.solver = EquationSolver(self.evaluator)
    
    def execute(self, line: str):
        """Execute a line of input."""
        line = line.strip()
        
        if not line:
            return None
        
        # Special commands
        if line.lower() == 'vars':
            return self.list_variables()
        
        # Tokenize
        try:
            lexer = Lexer(line)
            tokens = lexer.tokenize()
        except SyntaxError as e:
            raise SyntaxError(f"Syntax error: {e}")
        
        # Parse
        try:
            parser = Parser(tokens)
            ast = parser.parse()
        except SyntaxError as e:
            raise SyntaxError(f"Parse error: {e}")
        
        if ast is None:
            return None
        
        # Execute based on AST type
        node_type = ast[0]
        
        if node_type == 'assign':
            # Variable assignment
            var_name = ast[1]
            expr_ast = ast[2]
            value = self.evaluator.evaluate(expr_ast)
            self.evaluator.assign(var_name, value)
            return None  # Assignments don't output anything
        
        elif node_type == 'equation':
            # Solve equation
            left_ast = ast[1]
            right_ast = ast[2]
            return self.solver.solve(left_ast, right_ast)
        
        else:
            # Evaluate expression
            result = self.evaluator.evaluate(ast)
            return self.format_result(result)
    
    def format_result(self, value):
        """Format a value for output."""
        if isinstance(value, (Rational, Complex, Matrix)):
            return str(value)
        elif isinstance(value, (int, float)):
            return str(Rational(value))
        else:
            return str(value)
    
    def list_variables(self):
        """List all defined variables."""
        if not self.evaluator.variables:
            return "No variables defined"
        
        result = []
        for name, value in sorted(self.evaluator.variables.items()):
            value_str = self.format_result(value)
            result.append(f"{name} = {value_str}")
        return "\n".join(result)
