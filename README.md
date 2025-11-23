# Hanoi-Rocks 🗼

A comprehensive Tower of Hanoi solver collection featuring multiple solution approaches, including recursive, iterative, dynamic programming, and generalized state-based solvers that can handle arbitrary initial configurations.

## 📋 Project Overview

This project implements various solutions to the classic Tower of Hanoi puzzle, with a focus on:
- Multiple solving algorithms (recursive, iterative, dynamic programming)
- Generalized solvers that work from any legal initial state
- Detailed move tracking with position and height information
- Comprehensive test coverage

## 🚀 Features

### Base Solutions (`base_solutions/`)
- **`hanoi_recursive.py`**: Classic recursive implementation
- **`hanoi_iterative.py`**: Iterative solution using explicit stack
- **`hanoi_dynamic_programming.py`**: Dynamic programming approach

### State Solutions (`state_solutions/`)
- **`hanoi_state.py`**: Generalized solver with complete state tracking
  - Solves from any legal initial configuration
  - Tracks disk position, initial height, and destination height
  - Validates state legality
- **`hanoi_height.py`**: Height-based solution tracking
- **`hanoi_image.py`**: Arbitrary initial state solver

### Illegal Solutions (`illegal_solutions/`)
Work in progress for handling illegal states and special cases:
- Bubble handling
- Stack-based handling
- Queue-based handling
- Ground state handling
- Duplicate handling

## 🧪 Testing

Comprehensive test suite in `tests/`:
- `test_hanoi_state.py`: Tests for state-based solutions
- `test_hanoi_image.py`: Tests for image-based solutions

Run tests:
```bash
python tests/test_hanoi_state.py
python tests/test_hanoi_image.py
```

## 💻 Usage

### Basic Example (Recursive)
```python
from base_solutions.hanoi_recursive import hanoi_recursive

moves = hanoi_recursive(n=5, source='A', destination='C', auxiliary='B')
for move in moves:
    print(move)
```

### Advanced Example (From Arbitrary State)
```python
from state_solutions.hanoi_state import solve_hanoi_from_image

# Define initial configuration: [Peg A, Peg B, Peg C]
initial_state = [[3, 1], [2], []]  # Disks arranged arbitrarily

moves = solve_hanoi_from_image(
    initial_state=initial_state,
    source='A',
    destination='C',
    auxiliary='B'
)

for move in moves:
    print(move)
```

## 📊 Project Status

- ✅ Base recursive, iterative, and DP solutions
- ✅ Generalized state-based solver
- ✅ Height and position tracking
- ✅ Comprehensive testing for legal states
- 🚧 Illegal state handling (in progress)
- 🚧 Randomness integration
- 🚧 Statistical analysis (ANOVAs)
- 🚧 Complete documentation

## 🛠️ Requirements

- Python 3.7+
- No external dependencies for core functionality

## 📝 License

This project is part of the research/educational work exploring Tower of Hanoi solutions and state transitions.

## 👤 Author

lpep64 (Lord-of-this-World)
