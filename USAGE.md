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
