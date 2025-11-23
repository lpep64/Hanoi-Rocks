# Hanoi-Rocks TODO List

## 🚧 Illegal Solutions (Priority: High)

### 1. Illegal State Handling Scripts
Create solvers that handle different illegal state types:

- [ ] **Bubble Handler** (`hanoi_bubble.py`)
  - Detect and handle bubble violations (smaller disk below larger)
  - Implement bubble correction algorithm
  - Track correction moves separately

- [ ] **Stack Handler** (`hanoi_stack.py`)
  - Stack-based illegal state resolution
  - LIFO approach to state correction

- [ ] **Queue Handler** (`hanoi_queue.py`)
  - Queue-based illegal state resolution
  - FIFO approach to state correction

### 2. Ground State Handling (Feature)
Implement different strategies for reaching legal ground state:

- [ ] **Immediate Correction** (`hanoi_ground_immediate.py`)
  - Correct to nearest legal state immediately
  - Minimize correction moves

- [ ] **First Legal Move** (`hanoi_ground_first.py`)
  - Find and execute first available legal move
  - Track path to legality

### 3. Duplicate Handling
- [ ] Detect duplicate disk scenarios
- [ ] Implement resolution strategy
- [ ] Add validation for duplicate states

## 🎲 Environment & Configuration

### 4. Randomness Integration
- [ ] Create environment variable system
- [ ] Implement random state generator
- [ ] Add seed control for reproducibility
- [ ] Configuration file support (`.env` or config file)
- [ ] Random initial state generator with configurable:
  - Legal vs illegal state probability
  - Number of disks
  - Constraint violations

## 🧪 Testing & Validation

### 5. Comprehensive Testing
- [ ] Test suite for illegal state handlers
  - [ ] Bubble handler tests
  - [ ] Stack handler tests
  - [ ] Queue handler tests
- [ ] Ground state handling tests
- [ ] Duplicate detection tests
- [ ] Integration tests for full pipeline
- [ ] Edge case testing (n=1, n=10, empty pegs)
- [ ] Performance benchmarks

## 📊 Statistical Analysis

### 6. ANOVA Analysis
- [ ] Set up data collection framework
- [ ] Compare move counts across:
  - [ ] Different solving algorithms
  - [ ] Legal vs illegal initial states
  - [ ] Correction strategies
- [ ] Statistical significance testing
- [ ] Visualization of results
- [ ] Export results to CSV/JSON

## 📝 Documentation

### 7. Documentation Updates
- [x] Update README.md with project overview
- [x] Update .gitignore
- [ ] Add docstrings to all illegal solution functions
- [ ] Create usage examples for illegal handlers
- [ ] Document correction algorithms
- [ ] Add complexity analysis
- [ ] Create visual diagrams for state transitions
- [ ] Write research paper/technical report (if applicable)

## 🔮 Future Enhancements

### 8. Additional Features (Low Priority)
- [ ] GUI visualization of moves
- [ ] Animation of disk movements
- [ ] Web interface
- [ ] Performance optimization
- [ ] Multi-threading for large n values
- [ ] Export move sequences to video/GIF

---

**Last Updated:** November 23, 2025  
**Project:** Hanoi-Rocks  
**Status:** Base solutions complete, illegal solutions in development