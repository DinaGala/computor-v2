# Computor v2 - Usage Guide

A command interpreter in Python that supports rational numbers, complex numbers, matrices, and polynomial equation solving.

## Installation

No special installation required. Just ensure you have Python 3.6+ installed.

```bash
python3 computor.py
```

## Features

### 1. Rational Numbers
The interpreter uses exact rational arithmetic (fractions) for precise calculations.

```
> 7 / 2
7/2
> 15 / 3
5
> 1/3 + 1/6
1/2
```

### 2. Complex Numbers
Complex numbers with rational coefficients. Use `i` for the imaginary unit.

```
> 2 + 3*i
2 + 3i
> (2 + i) * (3 + 2*i)
4 + 7i
> i * i
-1
```

### 3. Matrices
Matrices with rational elements. Supports addition, subtraction, multiplication, and scalar operations.

```
> [[1, 2], [3, 4]]
[ [ 1 , 2 ] ; [ 3 , 4 ] ]
> M = [[1, 2], [3, 4]]
> M * 2
[ [ 2 , 4 ] ; [ 6 , 8 ] ]
> A = [[1, 0], [0, 1]]
> B = [[2, 3], [4, 5]]
> A + B
[ [ 3 , 3 ] ; [ 4 , 6 ] ]
```

### 4. Variable Assignment
Assign values to variables with automatic type inference.

```
> x = 5
> y = 2 + 3*i
> z = [[1, 2], [3, 4]]
> result = x + 10
> result
15
```

### 5. Variable Reassignment
Variables can be reassigned to different types.

```
> a = 10
> a
10
> a = 2 + 3*i
> a
2 + 3i
> a = [[1, 2], [3, 4]]
> a
[ [ 1 , 2 ] ; [ 3 , 4 ] ]
```

### 6. Variable-to-Variable Assignment
Assign one variable to another.

```
> x = 5
> y = x
> y
5
```

### 7. Expression Evaluation
Evaluate complex mathematical expressions.

```
> (2 + 3) * 4 - 5
15
> 2^3 + 1
9
```

### 8. Polynomial Equation Solving
Solve polynomial equations of degree ≤ 2.

```
> x^2 - 5*x + 6 = 0 ?
Reduced form: x^2 - 5 * x + 6 = 0
Polynomial degree: 2
Discriminant: 1
Discriminant is strictly positive, the two solutions are:
3
2

> 2*x + 5 = 13 ?
Reduced form: 2 * x - 8 = 0
Polynomial degree: 1
The solution is:
4

> x^2 + x + 1 = 0 ?
Reduced form: x^2 + x + 1 = 0
Polynomial degree: 2
Discriminant: -3
Discriminant is strictly negative, the two complex solutions are:
-1/2 + 1.732050807568877193176604123436845839023590087890625i
-1/2 - 1.732050807568877193176604123436845839023590087890625i
```

## Usage Modes

### Interactive Mode (REPL)
Run without arguments to enter interactive mode:

```bash
python3 computor.py
```

Then type expressions and commands:
```
> x = 5
> x + 10
15
> quit
```

### Command-Line Mode
Pass an expression as an argument:

```bash
python3 computor.py "5 + 3 * 2"
# Output: 11

python3 computor.py "2 + 3*i"
# Output: 2 + 3i
```

## Special Commands

- `vars` - List all defined variables
- `exit` or `quit` - Exit the interpreter (interactive mode only)

- `display` / `show` - Aliases for `vars` to list defined variables and their values

- `history` - Show a numbered list of recently executed commands
- `history results` - Show commands together with execution result and timestamp
- `history clear` - Clear the saved command-result history

## Operations Supported

### Arithmetic Operations
- Addition: `+`
- Subtraction: `-`
- Multiplication: `*`
- Division: `/`
- Power: `^` or `**`

### Supported Type Combinations
- Rational + Rational = Rational
- Rational + Complex = Complex
- Complex + Complex = Complex
- Matrix + Matrix = Matrix (same dimensions)
- Matrix * Matrix = Matrix (compatible dimensions)
- Matrix * Scalar = Matrix
- Scalar * Matrix = Matrix

## Examples

### Example 1: Basic Arithmetic
```
> 5 + 3
8
> 10 - 4
6
> 7 / 2
7/2
```

### Example 2: Complex Numbers
```
> c1 = 2 + 3*i
> c2 = 1 - i
> c1 + c2
3 + 2i
> c1 * c2
5 + i
```

### Example 3: Matrix Operations
```
> A = [[1, 2], [3, 4]]
> B = [[5, 6], [7, 8]]
> A + B
[ [ 6 , 8 ] ; [ 10 , 12 ] ]
> A * B
[ [ 19 , 22 ] ; [ 43 , 50 ] ]
```

### Example 4: Solving Equations
```
> x^2 - 4 = 0 ?
Reduced form: x^2 - 4 = 0
Polynomial degree: 2
Discriminant: 16
Discriminant is strictly positive, the two solutions are:
2
-2
```

### Example 5: Mixed Types
```
> scalar = 3
> complex_num = 2 + i
> result = scalar + complex_num
> result
5 + i
```

## Built-in functions

Computor v2 includes a set of common mathematical functions you can use directly in expressions. These accept numeric arguments (rational or complex) and return a numeric result when possible.

Common built-ins

- sin(x) — sine of x (x in radians)
- cos(x) — cosine of x (x in radians)
- tan(x) — tangent of x (x in radians)
- exp(x) — exponential e^x
- log(x) — natural logarithm (ln); behavior for non-positive real x follows complex rules
- sqrt(x) — principal square root; sqrt of a negative real returns a complex result
- abs(x) — absolute value (magnitude for complex numbers)
- floor(x), ceil(x) — integer floor/ceiling (when available)

- norm(X) — norm of a scalar/vector/matrix:
	- scalar: magnitude (same as `abs`)
	- vector (1×n or n×1 matrix): Euclidean (L2) norm
	- matrix (n×m): Frobenius norm (sqrt of sum of squared absolute values of all elements)

Usage examples:

```
> x = 3 + 4*i
> abs(x)
5
> M = [[1,2],[3,4]]
> norm(M)
5.477225575051661
```

Angle mode

Trig functions interpret their arguments according to the interpreter's current angle mode. By default the interpreter uses radians. You can view or change the mode with the `angles` command in the REPL:

```
> angles
angle mode: radians
> angles deg
angle mode set to degrees
> sin(90)
1.0
> angles rad
angle mode set to radians
> sin(1.57079632679)
1.0
```

Use `angles` with no argument to display the current mode. Use `angles deg` or `angles rad` to switch between degrees and radians.
- exp(x) — exponential e^x
- log(x) — natural logarithm (ln); behavior for non-positive real x follows complex rules
- sqrt(x) — principal square root; sqrt of a negative real returns a complex result
- abs(x) — absolute value (magnitude for complex numbers)
- floor(x), ceil(x) — integer floor/ceiling (when available)

Usage examples

```
> sin(1)
0.8414709848078965

> sqrt(4)
2

> sqrt(-1)
i

> exp(1)
2.718281828459045

> abs(-3/2)
3/2
```

Notes and behavior

- Arguments may be Rational or Complex; many of the transcendental functions return decimal approximations when necessary (e.g., sin, exp) because exact rational results are not generally available.
- `sqrt` of a negative real returns a `Complex` value (the interpreter prints `i` for the imaginary unit).
- `log` of a non-positive real will produce a complex result using the principal branch (if applicable).
- Use `abs` for magnitudes: `abs(2 + 3*i)` → `sqrt(13)` or its decimal/approximate representation depending on evaluation rules.
- If you need exact rational outputs, prefer arithmetic and power operations that preserve rationals; built-in transcendental functions typically produce floating-point results.

## Error Handling

The interpreter provides helpful error messages:

```
> undefined_var + 5
Error: Variable 'undefined_var' is not defined

> [[1, 2], [3]] 
Error: All rows must have the same length

> 5 / 0
Error: Division by zero
```

## Plotting functions

The interpreter provides a small `plot` command to visualize single-argument functions you define in the REPL.

Syntax

```
plot <function_name> <start> <end> [points]
```

- `function_name` — name of a previously defined single-argument function, e.g. `f` when you defined `f(x) = x^2 - 1`.
- `start`, `end` — numeric (floating) bounds of the plotting interval. `start` and `end` must differ.
- `points` — optional integer number of sampling points (default: 200). Must be >= 2.

Examples

```
> f(x) = x^2 - 1
> plot f -2 2
Plot saved to /tmp/computor_plot_xxxx.png

> g(t) = sin(t)  # if you have a sin implementation in your functions
> plot g 0 6.28 400
```

Behavior and notes

- The `plot` command only accepts named, single-argument `Function` objects (the project's `Function` type).
- The plotter samples the function at `points` evenly spaced values between `start` and `end` and evaluates the function AST at each sample.
- Only scalar real values are plottable: points that evaluate to complex numbers with non-zero imaginary part or matrices are skipped.
- If `matplotlib` is installed, the plotter uses it in headless mode (Agg) and writes a PNG image to a temporary file; the command returns the path to the PNG.
- If `matplotlib` is not available, the plotter falls back to a compact ASCII-art plot (60×20 grid) printed in the REPL.
- If no numeric points are plottable (all samples fail or are non-scalar), the command will report that no plottable points were produced.

Tips

- Install matplotlib to get image output (recommended):

```bash
pip install matplotlib
```

- Use a moderate number of `points` (200–1000) depending on performance and desired smoothness.
- If your function is expensive to evaluate, reduce the number of `points`.

## Matrix inverse

You can compute the inverse of a square matrix using `inv(M)` or the `^` operator with exponent `-1`.

Examples:

```
> A = [[1, 2], [3, 4]]
> inv(A)
[-2 , 1 ]
[ 1.5 , -0.5 ]

> A^-1
[-2 , 1 ]
[ 1.5 , -0.5 ]
```

Notes:

- Only square matrices have inverses. Attempting to invert a non-square matrix raises an error.
- Inversion is computed exactly using rational arithmetic where possible; if the matrix is singular, a ValueError is raised.
- `A^-1` is syntactic sugar for `A ^ -1` and uses the same logic (negative integer exponents require invertible square matrices).
