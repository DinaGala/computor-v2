# computor-v2

A command interpreter in Python for advanced mathematical computations.

## Features

- **Rational Numbers**: Exact arithmetic with fractions
- **Complex Numbers**: Complex numbers with rational coefficients  
- **Matrices**: Matrix operations (addition, subtraction, multiplication)
- **Polynomial Solver**: Solve equations of degree ≤ 2
- **Variable System**: Assignment, reassignment, and type inference
- **Expression Evaluation**: Full support for mathematical expressions

## Quick Start

```bash
# Interactive mode
python3 computor.py

# Command-line mode
python3 computor.py "5 + 3 * 2"
```

## Usage Examples

```
> x = 5
> x + 10
15

> 2 + 3*i
2 + 3i

> M = [[1, 2], [3, 4]]
> M * 2
[ [ 2 , 4 ] ; [ 6 , 8 ] ]

> x^2 - 5*x + 6 = 0 ?
Reduced form: x^2 - 5 * x + 6 = 0
Polynomial degree: 2
The two solutions are: 3, 2
```

See [USAGE.md](USAGE.md) for detailed documentation.
