#!/usr/bin/env python3
"""
Computor v2 - Command interpreter for mathematical expressions
Supports: Rational numbers, Complex numbers, Matrices, and polynomial equations
"""

import sys
import os
import atexit

from interpreter import Interpreter

try:
    import readline
except Exception:
    # readline may not be available in some environments (Windows without pyreadline)
    readline = None


def main():
    """Main entry point for the computor v2 interpreter."""
    interpreter = Interpreter()
    
    # Setup persistent history if readline is available
    # Allow overriding history path via environment variable COMPUTOR_HISTORY
    history_file = os.path.expanduser(os.getenv("COMPUTOR_HISTORY", "~/.computor_history"))
    if readline:
            # Ensure history directory exists (if user provided a path with dirs)
            history_dir = os.path.dirname(history_file)
            if history_dir and not os.path.exists(history_dir):
                os.makedirs(history_dir, exist_ok=True)

            # Try to read existing history; ignore failures
            try:
                if os.path.exists(history_file):
                    readline.read_history_file(history_file)
            except Exception:
                # ignore history read errors
                pass

            # Keep a reasonable amount of history
            try:
                readline.set_history_length(1000)
            except Exception:
                pass

            # Write history on exit
            def _write_history():
                try:
                    readline.write_history_file(history_file)
                except Exception:
                    pass

            atexit.register(_write_history)
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
                # Add to readline history (if available)
                try:
                    if readline:
                        # avoid adding pure whitespace (already filtered) and keep history concise
                        readline.add_history(line)
                except Exception:
                    pass
                    
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
