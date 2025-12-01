# Hanoi-Rocks 🗼

A comprehensive Tower of Hanoi solver collection featuring multiple solution approaches, including recursive, iterative, dynamic programming, generalized state-based solvers, and **statistical analysis framework** for comparing illegal state resolution strategies under environmental randomness.

## 📋 Project Overview

This project implements various solutions to the classic Tower of Hanoi puzzle, with a focus on:
- Multiple solving algorithms (recursive, iterative, dynamic programming)
- Generalized solvers that work from any legal initial state
- Illegal state resolution with multiple strategies
- Environmental randomness simulation
- **Statistical experimentation framework (2³ factorial design)**
- Detailed move tracking with position and height information

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
Handles illegal states using 4th Queue peg and Ground violations:

#### Stack Violation Solvers
- **`illegal_stack.py`**: Contains 2 algorithms for statistical analysis
  - **Dig Out**: Surgical fix targeting first illegal overlap
  - **BFS (Breadth-First Search)**: Optimal pathfinding to ANY legal state (shortest path guaranteed)

#### Ground Violation Solvers
- **`illegal_ground.py`**: Contains 2 strategies
  - **Greedy Placement**: Places largest ground disk with minimum violation
  - **Patient Wait**: Waits for legal move opportunity

#### Environment Simulation
- **`randomizer.py`**: Simulates physical testbed errors
  - 50% chance: Move disk to random location
  - 25% chance: Remove disk from existence
  - 25% chance: Add new disk at n+1
  - Seeded randomness for reproducibility

#### Validation
- **`illegal_check.py`**: Validates state legality (no Queue/Ground violations, proper stacking)

### Statistical Analysis (`statistical_analysis/`)
**2³ Factorial Experiment** comparing illegal state resolution strategies:

#### Experimental Factors
- **Factor A**: Stack Algorithm (Dig Out vs BFS)
- **Factor B**: Ground Algorithm (Greedy vs Patient)
- **Factor C**: Corruption Rate (5% vs 10% per move)

#### Framework Components
- **`experiment_config.py`**: Experimental design constants and configuration
  - 8 conditions × 50 trials = **400 total trials**
  - All tests use 5 disks
  - Max 5000 moves before timeout (penalty: 5001)

- **`state_validator.py`**: State transition validation
  - Checks solution correctness
  - Validates disk conservation
  - Detects illegal configurations

- **`run_tests.py`**: Main orchestrator
  - Generates corrupted initial states
  - Implements **Generate→Execute→Validate→Corrupt→Regenerate** loop
  - Tracks: total moves, regenerations, corruptions
  - Outputs: `results.csv`

- **`results_analyzer.py`**: Statistical analysis
  - 3-way ANOVA (requires scipy)
  - Descriptive statistics by factor
  - Condition-level summaries
  - Outputs: `results_summary.csv`

## 🧪 Testing

Comprehensive test suite in `tests/`:
- `test_hanoi_state.py`: Tests for state-based solutions
- `test_hanoi_image.py`: Tests for image-based solutions
- `test_adapter.py`: Vision adapter tests
- `test_illegal.py`: Illegal state handler tests

Run tests:
```bash
python tests/test_hanoi_state.py
python tests/test_illegal.py
```

## 💻 Usage

### Basic Example (Recursive)
```python
from base_solutions.hanoi_recursive import hanoi_recursive

moves = hanoi_recursive(n=5, source='A', destination='C', auxiliary='B')
for move in moves:
    print(move)
```

### Illegal State Resolution
```python
from illegal_solutions.illegal_stack import solve_illegal_dig_out
from illegal_solutions.illegal_ground import solve_ground_greedy

# State format: [A, B, C, Queue, Ground]
illegal_state = [
    [3, 1],  # Stack violation on A
    [2],
    [],
    [],
    [5, 4]   # Ground violations
]

# Solve ground violations first
moves, state = solve_ground_greedy(illegal_state)

# Then solve stack violations
moves, final_state = solve_illegal_dig_out(state)
```

### Run Statistical Experiment
```bash
# Run all 400 trials (takes 10-30 minutes)
cd statistical_analysis
python run_tests.py

# Analyze results (requires scipy)
python results_analyzer.py
```

### Environment Randomness Simulation
```python
from illegal_solutions.randomizer import Randomizer

# Initialize with seed for reproducibility
rand = Randomizer(seed=42)

# Create corrupted initial state
state = rand.create_corrupted_initial_state(n=5, num_corruptions=3)

# Apply corruption during solving
corruption_event = rand.corrupt_state(state, corruption_rate=0.10)
if corruption_event:
    print(f"Corruption: {corruption_event['type']}")
```

## 📊 Project Status

- ✅ Base recursive, iterative, and DP solutions
- ✅ Generalized state-based solver
- ✅ Illegal stack solvers (Dig Out, A*)
- ✅ Illegal ground solvers (Greedy, Patient)
- ✅ Environment randomness simulation
- ✅ Statistical experiment framework (2³ factorial)
- ✅ ANOVA analysis tools
- 🚧 Interaction plots and visualizations
- 🚧 Additional post-hoc tests
- 🚧 Complete API documentation

## 🛠️ Requirements

### Core Functionality
- Python 3.7+
- No external dependencies

### Statistical Analysis (Optional)
```bash
pip install scipy  # For ANOVA
pip install matplotlib  # For plots (future)
```

## 📖 Experimental Design

The statistical analysis framework implements a **2³ factorial experiment**:

| Condition | Stack Algo | Ground Algo | Corruption | Trials |
|-----------|------------|-------------|------------|--------|
| 1 | Dig Out | Greedy | 5% | 50 |
| 2 | Dig Out | Greedy | 10% | 50 |
| 3 | Dig Out | Patient | 5% | 50 |
| 4 | Dig Out | Patient | 10% | 50 |
| 5 | BFS | Greedy | 5% | 50 |
| 6 | BFS | Greedy | 10% | 50 |
| 7 | BFS | Patient | 5% | 50 |
| 8 | BFS | Patient | 10% | 50 |

**Goal**: Determine optimal combination for minimizing total moves to solution under environmental disturbances.

## 📝 License

This project is part of research/educational work exploring Tower of Hanoi solutions and state transitions.

## 👤 Author

lpep64 (Lord-of-this-World)
