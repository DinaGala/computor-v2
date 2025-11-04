#!/usr/bin/env python3
"""
Computor v2 - Command interpreter for mathematical expressions
Supports: Rational numbers, Complex numbers, Matrices, and polynomial equations
"""

import sys
import os
import atexit
import json
from datetime import datetime

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
    # Command -> result history (JSONL). Stores objects: {time: iso, cmd: str, result: str}
    history_results_file = os.path.expanduser(os.getenv("COMPUTOR_HISTORY_RESULTS", "~/.computor_history_results"))
    history_entries = []

    # Load existing command-result history (if any)
    try:
        if os.path.exists(history_results_file):
            with open(history_results_file, 'r', encoding='utf-8') as hf:
                for line in hf:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                        history_entries.append(obj)
                    except Exception:
                        # ignore malformed lines
                        continue
    except Exception:
        # don't fail startup for history read errors
        history_entries = []
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
            # Also flush command-result history on exit
            def _write_hist_results():
                try:
                    # ensure directory exists
                    hr_dir = os.path.dirname(history_results_file)
                    if hr_dir and not os.path.exists(hr_dir):
                        os.makedirs(hr_dir, exist_ok=True)
                    # append any in-memory entries that weren't persisted
                    # (we persist per-command below, so this is a no-op in normal flow)
                    with open(history_results_file, 'a', encoding='utf-8') as hf:
                        for entry in history_entries:
                            hf.write(json.dumps(entry, ensure_ascii=False) + "\n")
                except Exception:
                    pass

            atexit.register(_write_hist_results)
    if len(sys.argv) > 1:
        # Execute command from arguments
        command = ' '.join(sys.argv[1:])
        try:
            result = interpreter.execute(command)
            if result is not None:
                print(result)
            # persist command+result to history_results_file
            try:
                entry = {"time": datetime.utcnow().isoformat() + "Z", "cmd": command, "result": str(result)}
                # append to memory and file
                history_entries.append(entry)
                with open(history_results_file, 'a', encoding='utf-8') as hf:
                    hf.write(json.dumps(entry, ensure_ascii=False) + "\n")
            except Exception:
                pass
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

                # History commands (show/ results / clear)
                if line.lower().startswith('history') or line.lower() in ('hist',):
                    parts = line.split()
                    if len(parts) == 1:
                        # show commands only (numbered)
                        if not history_entries:
                            print("No history available")
                        else:
                            for i, e in enumerate(history_entries, start=1):
                                print(f"{i}: {e.get('cmd')}")
                        continue
                    elif len(parts) == 2 and parts[1].lower() in ('results', 'all'):
                        if not history_entries:
                            print("No history available")
                        else:
                            for i, e in enumerate(history_entries, start=1):
                                t = e.get('time', '')
                                cmd = e.get('cmd', '')
                                res = e.get('result', '')
                                print(f"{i} [{t}] > {cmd}\n  => {res}")
                        continue
                    elif len(parts) == 2 and parts[1].lower() == 'clear':
                        try:
                            # truncate history results file
                            open(history_results_file, 'w', encoding='utf-8').close()
                            history_entries.clear()
                            print("History cleared")
                        except Exception:
                            print("Failed to clear history")
                        continue
                    else:
                        print("Usage: history [results|clear]")
                        continue
                    
                result = interpreter.execute(line)
                if result is not None:
                    print(result)
                    # persist command+result to history_results_file
                    try:
                        entry = {"time": datetime.utcnow().isoformat() + "Z", "cmd": line, "result": str(result)}
                        history_entries.append(entry)
                        with open(history_results_file, 'a', encoding='utf-8') as hf:
                            hf.write(json.dumps(entry, ensure_ascii=False) + "\n")
                    except Exception:
                        pass
                    
            except EOFError:
                break
            except KeyboardInterrupt:
                print()
                break
            except Exception as e:
                print(f"Error: {e}")


if __name__ == "__main__":
    main()
