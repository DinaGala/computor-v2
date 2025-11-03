#!/usr/bin/env python3
"""
Computor v2 - Command interpreter for mathematical expressions
Supports: Rational numbers, Complex numbers, Matrices, and polynomial equations
"""

import sys
from interpreter import Interpreter


def main():
    """Main entry point for the computor v2 interpreter."""
    interpreter = Interpreter()
    
    if len(sys.argv) > 1:
        # Execute command from arguments
        command = ' '.join(sys.argv[1:])
        try:
            result = interpreter.execute(command)
            if result is not None:
                print(result)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Interactive REPL mode
        print("Computor v2 - Mathematical Expression Interpreter")
        print("Type 'exit' or 'quit' to leave")
        print()
        
        while True:
            try:
                line = input("> ")
                line = line.strip()
                
                if not line:
                    continue
                    
                if line.lower() in ('exit', 'quit'):
                    break
                    
                result = interpreter.execute(line)
                if result is not None:
                    print(result)
                    
            except EOFError:
                break
            except KeyboardInterrupt:
                print()
                break
            except Exception as e:
                print(f"Error: {e}")


if __name__ == "__main__":
    main()
