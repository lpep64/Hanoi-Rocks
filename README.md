# Hanoi-Rocks 🗼

**Advanced Tower of Hanoi Solver with Complex Variations**

A comprehensive research and application project for solving Tower of Hanoi puzzles with advanced features including illegal state resolution, ground disk retrieval, gap handling, duplicate disks, and flexible destination pegs.

---

## 🚀 Quick Start

### Basic Usage

```python
from hanoi_final_flag import solve_hanoi

# Simple 3-disk problem
state = [[3, 2, 1], [], [], [], []]
flags = {
    'target_peg': 2,  # Solve to Peg C
    'duplicate_strategy': 'discard',
    'ground_strategy': 'greedy_3',
    'illegal_resolution': 'bfs_3peg'
}

moves = solve_hanoi(state, flags)
for move in moves:
    print(move)
```

### Streamlit Visualization

```bash
streamlit run app.py
```

Visit `http://localhost:8501` for an interactive web interface with visual disk rendering and move-by-move playback.

---

## 📁 Project Structure

```
Hanoi-Rocks/
├── README.md                          # This file
├── hanoi_final.py                     # Standalone solver (no imports, fixed defaults)
├── hanoi_final_flag.py                # Full-featured master solver
├── app.py                              # Streamlit visualization app
│
├── hanoi/                              # Core library package
│   ├── core/                           # Core solving logic
│   ├── illegal/                        # Illegal state resolution
│   ├── base/                           # Research baseline algorithms
│   └── utils/                          # Helper functions
│
├── tests/                              # Consolidated test suite
│   ├── test_core.py                    # Core functionality tests
│   ├── test_hanoi_image.py             # 95 comprehensive state tests
│   ├── test_adapter.py                 # Vision adapter tests
│   └── test_solver_integration.py      # Integration tests
│
└── statistical_analysis/               # Research experiments (unchanged)
```

---

## 🎯 Key Features

### 1. **hanoi_final.py** - Standalone Solver
- ✅ Zero external imports (fully self-contained)
- ✅ Fixed configuration: `discard`, `greedy_3`, `bfs_3peg`
- ✅ Simple API: `solve_hanoi(state, destination_peg=2)`

### 2. **hanoi_final_flag.py** - Master Solver

**Duplicate Handling:**
- `'merge'`: Keep duplicates as separate physical disks (1a, 1b)
- `'discard'`: Remove duplicate disk instances

**Ground Strategy (4 variants):**
- `'greedy_3'`: Minimize violations using 3 pegs
- `'greedy_4'`: Minimize violations using 4 pegs
- `'patient_3'`: Only move when legal placement exists (3 pegs)
- `'patient_4'`: Only move when legal placement exists (4 pegs)

**Illegal Resolution (5 algorithms):**
- `'bubble_sort'`: Swap adjacent illegal disks
- `'total_evacuation'`: Clear illegal peg and redistribute
- `'dig_out'`: Surgical fix for first illegal overlap
- `'bfs_3peg'`: Optimal pathfinding without Queue ⭐ **Recommended**
- `'bfs_4peg'`: Optimal pathfinding with Queue assistance

**State Format:** 5-array `[Peg A, Peg B, Peg C, Queue, Ground]`
- Disks ordered bottom-to-top: `[3, 2, 1]` = disk 3 at bottom

### 3. **app.py** - Streamlit Visualization
- 📊 Graphical disk rendering
- ▶️ Move-by-move playback
- ⚙️ Interactive state editor
- 🎚️ Strategy configuration
- 📈 Solution statistics

---

## 🧪 Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test suites
python tests/test_core.py
python tests/test_hanoi_image.py           # 95 test cases
python tests/test_solver_integration.py
```

**Test Coverage:**
- ✅ 95 comprehensive state configurations
- ✅ All 5 illegal resolution algorithms
- ✅ All 4 ground retrieval strategies
- ✅ Edge cases: gaps, duplicates, illegal states

---

## 💡 Usage Examples

### Example 1: Ground Disks
```python
state = [
    [5, 3],     # Peg A
    [4],        # Peg B
    [],         # Peg C
    [],         # Queue
    [2, 1]      # Ground (illegal!)
]

flags = {'target_peg': 2, 'duplicate_strategy': 'discard',
         'ground_strategy': 'greedy_3', 'illegal_resolution': 'bfs_3peg'}

moves = solve_hanoi(state, flags)
```

### Example 2: Illegal Stacking
```python
state = [
    [1, 2],     # ILLEGAL! (2 on top of 1)
    [3], [], [], []
]

moves = solve_hanoi(state, flags)  # BFS fixes illegal state first
```

### Example 3: Duplicate Disks
```python
state = [
    [1],        # Peg A
    [2, 4],     # Peg B
    [3, 1],     # Peg C (duplicate disk 1)
    [], [5]
]

flags = {'target_peg': 2, 'duplicate_strategy': 'merge',
         'ground_strategy': 'greedy_3', 'illegal_resolution': 'bfs_3peg'}

moves = solve_hanoi(state, flags)
# Duplicates labeled as 1a, 1b
```

---

## 📦 Dependencies

```bash
pip install streamlit plotly pytest
```

---

## 🏗️ Architecture

### Import Structure
- `hanoi.core` → Base classes (Move, TowerState)
- `hanoi.illegal` → Resolution algorithms
- `hanoi.base` → Research baselines
- Entry points (`hanoi_final.py`, `hanoi_final_flag.py`, `app.py`) at root

### Testing Strategy
- Unit tests: Individual components
- Integration tests: End-to-end workflows
- Comprehensive tests: 95 state configurations

---

## 🔬 Statistical Analysis

The `statistical_analysis/` folder contains research experiments:
- Algorithm performance comparison
- Move count optimization
- Strategy effectiveness metrics
- R-based analysis (`analysis.Rmd`)

---

## 🤝 Contributing

Research project optimized for reproducible experiments and educational use.

---

*Built with Python 3.13+ | Streamlit | Plotly*
