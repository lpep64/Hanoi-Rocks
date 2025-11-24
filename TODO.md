# Hanoi-Rocks TODO List

### Ground State Handling (Feature)
Implement different strategies for reaching legal ground state:

- [ ] **Immediate Correction** (`hanoi_ground_immediate.py`)
  - Correct to nearest legal state immediately
  - Minimize correction moves

- [ ] **First Legal Move** (`hanoi_ground_first.py`)
  - Find and execute first available legal move
  - Track path to legality

### Duplicate Handling
- [ ] Detect duplicate disk scenarios
- [ ] Implement resolution strategy
- [ ] Add validation for duplicate states

## 🎲 Environment & Configuration

### Randomness Integration
- [ ] Create environment variable system
- [ ] Implement random state generator
- [ ] Add seed control for reproducibility
- [ ] Configuration file support (`.env` or config file)
- [ ] Random initial state generator with configurable:
  - Legal vs illegal state probability
  - Number of disks
  - Constraint violations

## 🧪 Testing & Validation

### Comprehensive Testing
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

### ANOVA Analysis
- [ ] Set up data collection framework
- [ ] Compare move counts across:
  - [ ] Different solving algorithms
  - [ ] Legal vs illegal initial states
  - [ ] Correction strategies
- [ ] Statistical significance testing
- [ ] Visualization of results
- [ ] Export results to CSV/JSON