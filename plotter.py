"""
Plotting helper for computor v2

Exposes plot_function(evaluator, function_obj, start, end, points=200)
which tries to use matplotlib when available and falls back to a small ASCII
plot when matplotlib is not installed or cannot be used.
"""
from typing import List
import math
import tempfile
import os

def _float_from_value(val):
    """Return a float from Rational or Complex where possible, otherwise raise."""
    from types_system import Rational, Complex
    if isinstance(val, Rational):
        return float(val.value)
    if isinstance(val, Complex):
        # Only accept purely real values for plotting
        if val.imag.value == 0:
            return float(val.real.value)
        raise ValueError("Complex value with non-zero imaginary part cannot be plotted")
    if isinstance(val, (int, float)):
        return float(val)
    raise TypeError(f"Cannot convert {type(val)} to float for plotting")


def plot_function(evaluator, function_obj, start: float, end: float, points: int = 200):
    """Sample the given single-argument Function object over [start, end].

    evaluator: an Evaluator instance (used only to copy current variables)
    function_obj: types_system.Function instance
    Returns: a short message (path to saved PNG) or an ASCII plot string.
    """
    from types_system import Function, Rational

    if not isinstance(function_obj, Function):
        raise TypeError("plot_function expects a Function object")
    if points < 2:
        raise ValueError("points must be at least 2")
    if start == end:
        raise ValueError("start and end must differ")

    # build sampling xs
    xs = [start + i * (end - start) / (points - 1) for i in range(points)]
    ys = []

    # Evaluate for each x; skip points that error or return non-scalar
    for x in xs:
        try:
            # Make a local evaluator with same variables
            local_evaluator = evaluator.__class__(evaluator.variables)
            # Bind argument name to Rational(x)
            local_evaluator.assign(function_obj.arg_name, Rational(float(x)))
            val = local_evaluator.evaluate(function_obj.body_ast)
            y = _float_from_value(val)
            ys.append(y)
        except Exception:
            # mark as NaN so plotting can skip
            ys.append(float('nan'))

    # Try matplotlib first
    try:
        import matplotlib
        # Use Agg to avoid requiring a display
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        # prepare data, filter out NaNs
        xs_plot = [x for x, y in zip(xs, ys) if not math.isnan(y)]
        ys_plot = [y for y in ys if not math.isnan(y)]

        if not xs_plot:
            return "No plottable numeric points were produced"

        plt.figure(figsize=(6, 3))
        plt.plot(xs_plot, ys_plot, marker='.', linestyle='-', markersize=3)
        title = f"{function_obj.name or 'f'}({function_obj.arg_name})"
        plt.title(title)
        plt.xlabel(function_obj.arg_name)
        plt.ylabel('f')
        plt.grid(True)

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.png', prefix='computor_plot_')
        tmp_path = tmp.name
        tmp.close()
        plt.tight_layout()
        plt.savefig(tmp_path)
        plt.close()
        return f"Plot saved to {tmp_path}"
    except Exception:
        # Fallback to ASCII plot
        try:
            cols = 60
            rows = 20
            # filter valid points
            pairs = [(x, y) for x, y in zip(xs, ys) if not math.isnan(y) and math.isfinite(y)]
            if not pairs:
                return "No plottable numeric points were produced"
            xs_valid = [p[0] for p in pairs]
            ys_valid = [p[1] for p in pairs]
            ymin = min(ys_valid)
            ymax = max(ys_valid)
            if ymin == ymax:
                ymin -= 1
                ymax += 1
            grid = [[' ' for _ in range(cols)] for _ in range(rows)]
            for i, (x, y) in enumerate(pairs):
                # map x to column
                col = int((i / (len(pairs) - 1)) * (cols - 1))
                # map y to row (top is 0)
                row = int((1 - (y - ymin) / (ymax - ymin)) * (rows - 1))
                row = max(0, min(rows - 1, row))
                grid[row][col] = '*'

            # Compose ASCII lines
            lines = []
            for r in grid:
                lines.append(''.join(r))
            footer = f"x in [{start}, {end}], {len(pairs)}/{len(xs)} points plottable"
            return "\n".join(lines) + "\n" + footer
        except Exception as e:
            return f"Plot failed: {e}"
