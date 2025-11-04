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

        # Aliases for listing variables
        if line.lower() in ('display', 'show'):
            return self.list_variables()

        # Angle mode command: 'angles' to show mode, or 'angles rad' / 'angles deg' to set
        if line.lower().startswith('angles'):
            parts = line.split()
            if len(parts) == 1:
                # show current mode
                return f"angle mode: {self.evaluator.angle_mode}"
            elif len(parts) == 2:
                mode = parts[1]
                try:
                    self.evaluator.set_angle_mode(mode)
                    return f"angle mode set to {self.evaluator.angle_mode}"
                except Exception as e:
                    raise SyntaxError(str(e))
            else:
                raise SyntaxError("Usage: angles [rad|deg]")

        # Plot command: plot <func> <start> <end> [points]
        if line.lower().startswith('plot '):
            parts = line.split()
            if len(parts) < 4:
                raise SyntaxError("Usage: plot <function> <start> <end> [points]")
            func_name = parts[1]
            try:
                start = float(parts[2])
                end = float(parts[3])
            except ValueError:
                raise SyntaxError("Start and end must be numeric")
            points = 200
            if len(parts) >= 5:
                try:
                    points = int(parts[4])
                except ValueError:
                    raise SyntaxError("points must be an integer")

            # Lookup the function object
            func_obj = self.evaluator.get_variable(func_name)
            if func_obj is None:
                raise NameError(f"Function '{func_name}' is not defined")
            from types_system import Function
            if not isinstance(func_obj, Function):
                raise TypeError(f"'{func_name}' is not a function")

            # Lazy import of plotting helper
            try:
                from plotter import plot_function
            except Exception as e:
                raise RuntimeError(f"Plotting helper unavailable: {e}")

            return plot_function(self.evaluator, func_obj, start, end, points)
        
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
            # Return the assigned value so the REPL can echo it (and allow type changes by inference)
            return self.format_result(value)

        elif node_type == 'fun_assign':
            # Function assignment: store the argument name and body AST
            func_name = ast[1]
            arg_name = ast[2]
            body_ast = ast[3]
            # Lazy container; evaluator will store it as-is
            from types_system import Function
            func = Function(arg_name, body_ast, name=func_name)
            self.evaluator.assign(func_name, func)
            # Return a pretty-printed version of the function body with
            # any non-argument variables folded to their current values.
            return self.render_function_body(body_ast, arg_name)
        
        elif node_type == 'equation':
            # Solve equation
            left_ast = ast[1]
            right_ast = ast[2]
            # If right_ast is None, it's an evaluation request like 'expr = ?'
            if right_ast is None:
                # Try to inline user-defined function calls symbolically so expressions
                # like funA(funB(x)) = ? produce a composed expression rather than
                # attempting to numerically evaluate the free variable 'x'.
                try:
                    inlined = self.inline_function_calls(left_ast)
                    # If the inlined AST still contains variables, render it structurally
                    if self.ast_has_variables(inlined):
                        return self.ast_to_string(inlined)
                    # Otherwise evaluate normally
                    val = self.evaluator.evaluate(inlined)
                    return self.format_result(val)
                except Exception:
                    # Fallback to numeric evaluation (will raise if variables are missing)
                    val = self.evaluator.evaluate(left_ast)
                    return self.format_result(val)
            return self.solver.solve(left_ast, right_ast)
        
        else:
            # Evaluate expression
            result = self.evaluator.evaluate(ast)
            return self.format_result(result)
    
    def format_result(self, value):
        """Format a value for output."""
        if isinstance(value, (Rational, Complex, Matrix)):
            return str(value)
        # Functions
        from types_system import Function
        if isinstance(value, Function):
            # Show function body (using argument name in representation)
            return self.ast_to_string(value.body_ast)
        elif isinstance(value, (int, float)):
            # Print native floats/ints directly (builtins often return floats)
            return str(value)
        else:
            return str(value)

    def ast_to_string(self, ast):
        """Convert an AST back to a readable expression string."""
        if ast is None:
            return ""

        node_type = ast[0]

        if node_type == 'number':
            return ast[1]

        if node_type == 'variable':
            return ast[1]

        if node_type == 'imaginary':
            return 'i'

        if node_type == 'matrix':
            # Reconstruct matrix literal
            rows = []
            for row_ast in ast[1]:
                row_elems = [self.ast_to_string(elem) for elem in row_ast]
                rows.append('[ ' + ' , '.join(row_elems) + ' ]')
            return '[ ' + ' ; '.join(rows) + ' ]'

        if node_type == 'unary':
            op = ast[1]
            operand_ast = ast[2]
            operand = self.ast_to_string(operand_ast)
            # Parenthesize operand if it's a binary operation for clarity: - (x + 2)
            if operand_ast and operand_ast[0] == 'binop':
                return f"{op}({operand})"
            return f"{op}{operand}"

        if node_type == 'binop':
            op = ast[1]
            left_ast = ast[2]
            right_ast = ast[3]

            def prec(a):
                if a == '^':
                    return 4
                if a in ('*', '/', '%'):
                    return 3
                if a in ('+', '-'):
                    return 2
                return 0

            left = self.ast_to_string(left_ast)
            right = self.ast_to_string(right_ast)

            # Parenthesize children when their operator precedence is lower than parent
            if left_ast and left_ast[0] == 'binop':
                if prec(left_ast[1]) < prec(op) or (op == '^'):
                    left = f"({left})"

            if right_ast and right_ast[0] == 'binop':
                if prec(right_ast[1]) < prec(op) or (op == '^'):
                    right = f"({right})"

            # Use ^ for power
            if op == '^':
                return f"{left}^{right}"
            return f"{left} {op} {right}"

        # Fallback
        return str(ast)

    def contains_arg(self, ast, arg_name):
        """Return True if AST contains a reference to arg_name."""
        if ast is None:
            return False
        node_type = ast[0]
        if node_type == 'variable':
            return ast[1] == arg_name
        if node_type in ('number', 'imaginary'):
            return False
        if node_type == 'matrix':
            for row in ast[1]:
                for elem in row:
                    if self.contains_arg(elem, arg_name):
                        return True
            return False
        if node_type == 'unary':
            return self.contains_arg(ast[2], arg_name)
        if node_type == 'binop':
            return self.contains_arg(ast[2], arg_name) or self.contains_arg(ast[3], arg_name)
        if node_type == 'call':
            # arguments inside calls may contain arg_name
            return self.contains_arg(ast[2], arg_name)
        return False

    def format_value_for_display(self, value):
        """Format evaluated values for function-body display.

        This is intentionally permissive: for Rational with non-1 denominator we
        convert to a decimal string for readability in function signatures.
        Tests that care about precise fraction strings still use evaluator outputs.
        """
        from types_system import Rational, Complex
        if isinstance(value, Rational):
            if value.value.denominator == 1:
                return str(value.value.numerator)
            # show decimal for function-body display
            return str(float(value.value))
        if isinstance(value, Complex):
            return str(value)
        return str(value)

    def render_function_body(self, body_ast, arg_name):
        """Render function body AST substituting known variable values where possible.

        If a subtree does not contain the argument name, it will be evaluated now
        using the current evaluator variables and rendered as a concrete value.
        Otherwise the expression is rendered symbolically, leaving the argument
        name intact.
        """
        # If subtree does not contain arg_name -> evaluate and format
        if not self.contains_arg(body_ast, arg_name):
            try:
                val = self.evaluator.evaluate(body_ast)
                return self.format_value_for_display(val) if val is not None else ""
            except Exception:
                # fall back to structural rendering
                return self.ast_to_string(body_ast)

        node_type = body_ast[0]
        if node_type == 'binop':
            left_ast = body_ast[2]
            right_ast = body_ast[3]
            op = body_ast[1]

            def prec(a):
                if a == '^':
                    return 4
                if a in ('*', '/', '%'):
                    return 3
                if a in ('+', '-'):
                    return 2
                return 0

            # Special handling for addition/subtraction: flatten constant terms
            if op in ('+', '-'):
                from types_system import Rational

                def flatten(ast_node):
                    """Return (sym_terms, const_sum) where sym_terms is list of (str, sign)
                    and const_sum is a Rational sum of constant-only subtrees.
                    """
                    if ast_node[0] == 'binop' and ast_node[1] in ('+', '-'):
                        left_terms, left_const = flatten(ast_node[2])
                        right_terms, right_const = flatten(ast_node[3])
                        if ast_node[1] == '+':
                            return left_terms + right_terms, left_const + right_const
                        else:
                            # subtraction: right terms invert sign
                            inverted = [(s, -sign) for (s, sign) in right_terms]
                            return left_terms + inverted, left_const - right_const

                    # If subtree contains the function arg, keep as symbolic term
                    if self.contains_arg(ast_node, arg_name):
                        term = self.render_function_body(ast_node, arg_name)
                        return ([(term, 1)], Rational(0))

                    # Otherwise evaluate constant subtree
                    try:
                        val = self.evaluator.evaluate(ast_node)
                        if isinstance(val, Rational):
                            return ([], val)
                        elif isinstance(val, (int, float)):
                            return ([], Rational(val))
                        else:
                            # Non-rational constant (e.g., complex/matrix) -> keep symbolic
                            term = self.render_function_body(ast_node, arg_name)
                            return ([(term, 1)], Rational(0))
                    except Exception:
                        # If evaluation fails, fallback to symbolic
                        term = self.render_function_body(ast_node, arg_name)
                        return ([(term, 1)], Rational(0))

                terms, const_sum = flatten(body_ast)

                sym_terms = terms
                # Build output preferring constant first, then symbolic terms
                out_parts = []
                if const_sum.value != 0:
                    const_str = self.format_value_for_display(const_sum)
                    out_parts.append(const_str)

                for term, sign in sym_terms:
                    if not out_parts:
                        # first printed term: sign attaches directly if negative
                        if sign == 1:
                            out_parts.append(term)
                        else:
                            out_parts.append(f"- {term}")
                    else:
                        # subsequent terms: always prefix with + or -
                        if sign == 1:
                            out_parts.append(f"+ {term}")
                        else:
                            out_parts.append(f"- {term}")

                return ' '.join(out_parts).strip()

            # Fallback: non-add/sub handling uses precedence parenthesis
            left = self.render_function_body(left_ast, arg_name)
            right = self.render_function_body(right_ast, arg_name)

            if left_ast and left_ast[0] == 'binop':
                if prec(left_ast[1]) < prec(op) or (op == '^'):
                    left = f"({left})"

            if right_ast and right_ast[0] == 'binop':
                if prec(right_ast[1]) < prec(op) or (op == '^'):
                    right = f"({right})"

            if op == '^':
                return f"{left}^{right}"
            return f"{left} {op} {right}"
        if node_type == 'unary':
            return f"{body_ast[1]}{self.render_function_body(body_ast[2], arg_name)}"
        if node_type == 'variable':
            return body_ast[1]
        if node_type == 'number':
            return body_ast[1]
        if node_type == 'imaginary':
            return 'i'
        if node_type == 'matrix':
            rows = []
            for row_ast in body_ast[1]:
                row_elems = [self.render_function_body(elem, arg_name) for elem in row_ast]
                rows.append('[ ' + ' , '.join(row_elems) + ' ]')
            return '[ ' + ' ; '.join(rows) + ' ]'
        if node_type == 'call':
            func_name = body_ast[1]
            arg_str = self.render_function_body(body_ast[2], arg_name)
            return f"{func_name}({arg_str})"

        return self.ast_to_string(body_ast)
    
    def list_variables(self):
        """List all defined variables."""
        if not self.evaluator.variables:
            return "No variables defined"
        
        result = []
        for name, value in sorted(self.evaluator.variables.items()):
            # names are stored lowercase in evaluator; display them in lowercase for consistency
            value_str = self.format_result(value)
            result.append(f"{name} = {value_str}")
        return "\n".join(result)

    def inline_function_calls(self, ast_node):
        """Return a new AST where user-defined Function calls are inlined by
        substituting the function body with the actual argument AST.

        Only inlines calls where the callee is a `Function` stored in the evaluator.
        """
        from copy import deepcopy
        if ast_node is None:
            return None

        node_type = ast_node[0]

        if node_type == 'call':
            func_name = ast_node[1]
            arg_ast = ast_node[2]
            # Try to get a user-defined Function
            func_obj = self.evaluator.get_variable(func_name)
            from types_system import Function
            if isinstance(func_obj, Function):
                # Substitute argument occurrences in the function body with the provided arg_ast
                body_copy = deepcopy(func_obj.body_ast)
                substituted = self._substitute_arg(body_copy, func_obj.arg_name, deepcopy(arg_ast))
                # After substituting, recursively inline inside the substituted body
                return self.inline_function_calls(substituted)
            else:
                # Not a user function: keep call but recurse into its argument
                return ('call', func_name, self.inline_function_calls(arg_ast))

        if node_type == 'binop':
            return ('binop', ast_node[1], self.inline_function_calls(ast_node[2]), self.inline_function_calls(ast_node[3]))

        if node_type == 'unary':
            return ('unary', ast_node[1], self.inline_function_calls(ast_node[2]))

        if node_type == 'matrix':
            new_rows = []
            for row in ast_node[1]:
                new_rows.append([self.inline_function_calls(elem) for elem in row])
            return ('matrix', new_rows)

        # numbers, variables, imaginary -> return deep copy
        from copy import deepcopy as _dc
        return _dc(ast_node)

    def _substitute_arg(self, ast_node, arg_name, replacement_ast):
        """Recursively replace variable nodes named arg_name with replacement_ast.

        Returns a new AST (does not modify inputs).
        """
        from copy import deepcopy
        if ast_node is None:
            return None
        node_type = ast_node[0]
        if node_type == 'variable':
            if ast_node[1] == arg_name:
                return deepcopy(replacement_ast)
            return ('variable', ast_node[1])
        if node_type == 'number':
            return ('number', ast_node[1])
        if node_type == 'imaginary':
            return ('imaginary',)
        if node_type == 'unary':
            return ('unary', ast_node[1], self._substitute_arg(ast_node[2], arg_name, replacement_ast))
        if node_type == 'binop':
            return ('binop', ast_node[1], self._substitute_arg(ast_node[2], arg_name, replacement_ast), self._substitute_arg(ast_node[3], arg_name, replacement_ast))
        if node_type == 'call':
            return ('call', ast_node[1], self._substitute_arg(ast_node[2], arg_name, replacement_ast))
        if node_type == 'matrix':
            new_rows = []
            for row in ast_node[1]:
                new_rows.append([self._substitute_arg(elem, arg_name, replacement_ast) for elem in row])
            return ('matrix', new_rows)
        # fallback: deepcopy
        return deepcopy(ast_node)

    def ast_has_variables(self, ast_node):
        """Return True if AST contains any variable nodes."""
        if ast_node is None:
            return False
        node_type = ast_node[0]
        if node_type == 'variable':
            return True
        if node_type in ('number', 'imaginary'):
            return False
        if node_type == 'matrix':
            for row in ast_node[1]:
                for elem in row:
                    if self.ast_has_variables(elem):
                        return True
            return False
        if node_type == 'unary':
            return self.ast_has_variables(ast_node[2])
        if node_type == 'binop':
            return self.ast_has_variables(ast_node[2]) or self.ast_has_variables(ast_node[3])
        if node_type == 'call':
            return self.ast_has_variables(ast_node[2])
        return False
