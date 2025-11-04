"""
Parser for mathematical expressions
Handles tokenization and parsing of expressions
"""

import re
from typing import List, Tuple, Union
from types_system import Rational, Complex, Matrix


class Token:
    """Represents a token in the input."""
    
    def __init__(self, type_: str, value: str, pos: int = 0):
        self.type = type_
        self.value = value
        self.pos = pos
    
    def __repr__(self):
        return f"Token({self.type}, {self.value})"


class Lexer:
    """Tokenizes mathematical expressions."""

    TOKEN_PATTERNS = [
        ('NUMBER', r'\d+\.?\d*'),
    # Identifiers: letters only (case-insensitive). Disallow names containing digits/underscores.
    ('IDENTIFIER', r'[A-Za-z]+'),
        ('ASSIGN', r'='),
        ('MODULO', r'%'),
        ('QUESTION', r'\?'),
        ('PLUS', r'\+'),
        ('MINUS', r'-'),
        # Match matrix-multiplication operator '**' before single '*'
        ('MATMUL', r'\*\*'),
        ('MULTIPLY', r'\*'),
        ('DIVIDE', r'/'),
        ('POWER', r'\^'),
        ('LPAREN', r'\('),
        ('RPAREN', r'\)'),
        ('LBRACKET', r'\['),
        ('RBRACKET', r'\]'),
        ('SEMICOLON', r';'),
        ('COMMA', r','),
        ('WHITESPACE', r'\s+'),
    ]
    
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.tokens = []
    
    def tokenize(self) -> List[Token]:
        """Convert input text into tokens."""
        self.tokens = []
        self.pos = 0
        
        while self.pos < len(self.text):
            matched = False
            
            for token_type, pattern in self.TOKEN_PATTERNS:
                regex = re.compile(pattern)
                match = regex.match(self.text, self.pos)
                
                if match:
                    value = match.group(0)
                    if token_type != 'WHITESPACE':
                        self.tokens.append(Token(token_type, value, self.pos))
                    self.pos = match.end()
                    matched = True
                    break
            
            if not matched:
                raise SyntaxError(f"Unexpected character '{self.text[self.pos]}' at position {self.pos}")
        
        return self.tokens


class Parser:
    """Parses tokens into an abstract syntax tree."""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
    
    def current_token(self) -> Token:
        """Get current token without consuming it."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None
    
    def consume(self, expected_type: str = None) -> Token:
        """Consume and return current token."""
        token = self.current_token()
        if token is None:
            raise SyntaxError("Unexpected end of input")
        if expected_type and token.type != expected_type:
            raise SyntaxError(f"Expected {expected_type}, got {token.type}")
        self.pos += 1
        return token
    
    def peek_token(self, offset: int = 1) -> Token:
        """Peek at token ahead without consuming."""
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None
    
    def parse(self):
        """Parse the token stream."""
        if not self.tokens:
            return None

        # Check if it's an equation or assignment. Prefer equation when a '?' is present
        # so inputs like `funA(x) = y ?` are treated as equations rather than assignments.
        if self.is_equation():
            result = self.parse_equation()
        elif self.is_assignment():
            result = self.parse_assignment()
        else:
            result = self.parse_expression()

        # After parsing a complete statement, there should be no leftover tokens.
        if self.current_token() is not None:
            tok = self.current_token()
            raise SyntaxError(f"Unexpected token after expression: '{tok.value}' at position {tok.pos}")

        return result
    
    def is_assignment(self) -> bool:
        """Check if this is an assignment statement."""
        # Two forms:
        # 1) IDENTIFIER = ...
        # 2) IDENTIFIER ( IDENTIFIER ) = ...  (function assignment)
        if not self.tokens:
            return False

        if len(self.tokens) >= 2 and self.tokens[0].type == 'IDENTIFIER' and self.tokens[1].type == 'ASSIGN':
            return True

        # function assignment detection
        if len(self.tokens) >= 5:
            return (self.tokens[0].type == 'IDENTIFIER' and
                    self.tokens[1].type == 'LPAREN' and
                    self.tokens[2].type == 'IDENTIFIER' and
                    self.tokens[3].type == 'RPAREN' and
                    self.tokens[4].type == 'ASSIGN')

        return False
    
    def is_equation(self) -> bool:
        """Check if this is an equation to solve."""
        # Look for pattern with = and ? but not starting with assignment
        has_equals = False
        has_question = False
        
        for i, token in enumerate(self.tokens):
            if token.type == 'ASSIGN':
                # If = is after identifier at start, it's assignment
                if i == 1 and self.tokens[0].type == 'IDENTIFIER':
                    return False
                has_equals = True
            if token.type == 'QUESTION':
                has_question = True
        
        return has_equals and has_question
    
    def parse_assignment(self):
        """Parse variable assignment."""
        identifier = self.consume('IDENTIFIER')
        # Validate identifier: letters only and not 'i'
        name = identifier.value
        if name.lower() == 'i':
            raise SyntaxError("'i' is reserved for the imaginary unit and cannot be used as a variable or function name")


        # function assignment: name(arg) = expr
        if self.current_token() and self.current_token().type == 'LPAREN':
            self.consume('LPAREN')
            arg_token = self.consume('IDENTIFIER')
            # Arg name must be letters and not 'i'
            if arg_token.value.lower() == 'i':
                raise SyntaxError("'i' is reserved for the imaginary unit and cannot be used as a variable or function argument")
            self.consume('RPAREN')
            self.consume('ASSIGN')
            expression = self.parse_expression()
            return ('fun_assign', identifier.value, arg_token.value, expression)

        # normal variable assignment
        self.consume('ASSIGN')
        expression = self.parse_expression()
        return ('assign', identifier.value, expression)
    
    def parse_equation(self):
        """Parse equation to solve."""
        # Expression = Expression? (right side may be omitted before '?')
        left = self.parse_expression()
        self.consume('ASSIGN')
        # If we immediately see QUESTION, treat as evaluation request of left
        if self.current_token() and self.current_token().type == 'QUESTION':
            self.consume('QUESTION')
            return ('equation', left, None)
        right = self.parse_expression()
        self.consume('QUESTION')
        return ('equation', left, right)
    
    def parse_expression(self):
        """Parse an expression (handles addition and subtraction)."""
        left = self.parse_term()
        
        while self.current_token() and self.current_token().type in ('PLUS', 'MINUS'):
            op = self.consume()
            # Disallow consecutive + or - sequences like '+-' or '--'
            if self.current_token() and self.current_token().type in ('PLUS', 'MINUS'):
                raise SyntaxError("Consecutive '+' or '-' operators are not allowed")
            right = self.parse_term()
            left = ('binop', op.value, left, right)

        return left
    
    def parse_term(self):
        """Parse a term (handles multiplication and division)."""
        left = self.parse_power()

        # Implicit multiplication support: when a factor is followed directly by
        # another factor (NUMBER, IDENTIFIER, LPAREN, LBRACKET) treat it as '*'.
        implicit_starters = ('NUMBER', 'IDENTIFIER', 'LPAREN', 'LBRACKET')

        while self.current_token():
            tok = self.current_token()
            if tok.type in ('MULTIPLY', 'DIVIDE', 'MODULO', 'MATMUL'):
                op = self.consume()
                right = self.parse_power()
                # Use '**' token for matrix multiplication or '*' for element-wise
                if op.type == 'MATMUL':
                    left = ('binop', '**', left, right)
                else:
                    left = ('binop', op.value, left, right)
            elif tok.type in implicit_starters:
                # implicit multiplication
                right = self.parse_power()
                left = ('binop', '*', left, right)
            else:
                break

        return left
    
    def parse_power(self):
        """Parse power expressions."""
        left = self.parse_factor()
        
        if self.current_token() and self.current_token().type == 'POWER':
            op = self.consume()
            right = self.parse_power()  # Right associative
            left = ('binop', '^', left, right)
        
        return left
    
    def parse_factor(self):
        """Parse a factor (number, variable, or parenthesized expression)."""
        token = self.current_token()
        
        if not token:
            raise SyntaxError("Unexpected end of expression")
        
        # Unary minus
        if token.type == 'MINUS':
            self.consume()
            factor = self.parse_factor()
            return ('unary', '-', factor)
        
        # Parenthesized expression
        if token.type == 'LPAREN':
            self.consume()
            expr = self.parse_expression()
            self.consume('RPAREN')
            return expr
        
        # Matrix
        if token.type == 'LBRACKET':
            return self.parse_matrix()
        
        # Number
        if token.type == 'NUMBER':
            self.consume()
            return ('number', token.value)
        
        # Identifier (variable or 'i' for imaginary)
        if token.type == 'IDENTIFIER':
            # Lookahead: could be function call or variable
            ident = token.value
            self.consume()
            if ident == 'i':
                return ('imaginary',)

            if self.current_token() and self.current_token().type == 'LPAREN':
                # function call: IDENTIFIER ( expression )
                self.consume('LPAREN')
                # allow empty arg? not supported
                arg_expr = self.parse_expression()
                self.consume('RPAREN')
                return ('call', ident, arg_expr)

            return ('variable', ident)
        
        raise SyntaxError(f"Unexpected token: {token.type}")
    
    def parse_matrix(self):
        """Parse matrix literal: [[1, 2], [3, 4]] or [1, 2; 3, 4]."""
        self.consume('LBRACKET')
        
        rows = []
        current_row = []
        
        while self.current_token() and self.current_token().type != 'RBRACKET':
            # Check for nested brackets (row format)
            if self.current_token().type == 'LBRACKET':
                self.consume('LBRACKET')
                row = []
                while self.current_token() and self.current_token().type != 'RBRACKET':
                    row.append(self.parse_expression())
                    if self.current_token() and self.current_token().type == 'COMMA':
                        self.consume('COMMA')
                    elif self.current_token() and self.current_token().type != 'RBRACKET':
                        break
                self.consume('RBRACKET')
                rows.append(row)
                
                if self.current_token() and self.current_token().type in ('COMMA', 'SEMICOLON'):
                    # Allow comma or semicolon between nested row brackets
                    if self.current_token().type == 'COMMA':
                        self.consume('COMMA')
                    else:
                        self.consume('SEMICOLON')
            else:
                # Flat format with semicolons
                current_row.append(self.parse_expression())
                
                if self.current_token() and self.current_token().type == 'SEMICOLON':
                    self.consume('SEMICOLON')
                    rows.append(current_row)
                    current_row = []
                elif self.current_token() and self.current_token().type == 'COMMA':
                    self.consume('COMMA')
                elif self.current_token() and self.current_token().type == 'RBRACKET':
                    break
        
        if current_row:
            rows.append(current_row)
        
        self.consume('RBRACKET')
        
        if not rows:
            raise SyntaxError("Empty matrix")
        
        return ('matrix', rows)
