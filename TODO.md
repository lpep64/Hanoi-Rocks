# Hanoi-Rocks TODO List

## ✅ Completed Features

### Ground State Handling
- ✅ **Greedy Placement** (`illegal_ground.py`)
  - Places largest ground disk with minimum violation
  - Always prioritizes largest disk first
  
- ✅ **Patient Wait** (`illegal_ground.py`)
  - Waits for legal move opportunity
  - Integrates with stack solutions

### Illegal Stack Handling
- ✅ **Dig Out Algorithm** (`illegal_stack.py`)
  - Surgical fix targeting first illegal overlap
  - Uses Queue peg for temporary storage
  
- ✅ **BFS (Breadth-First Search) Algorithm** (`illegal_stack.py`)
  - Optimal pathfinding to ANY legal state
  - Guarantees shortest path (no heuristic needed)
  - Explores level-by-level until legality achieved

### Environment & Randomness
- ✅ **Randomizer** (`randomizer.py`)
  - Simulates physical testbed errors
  - 50% move, 25% remove, 25% add disk
  - Seeded randomness for reproducibility
  - Creates structured pre-corrupted initial states

### Statistical Analysis Framework
- ✅ **Experiment Configuration** (`experiment_config.py`)
  - 2³ factorial design (8 conditions)
  - Factor A: Stack algorithm (Dig Out vs BFS)
  - Factor B: Ground algorithm (Greedy vs Patient)
  - Factor C: Corruption rate (5% vs 10%)
  - 50 trials per condition (400 total)

- ✅ **State Validator** (`state_validator.py`)
  - Validates state transitions
  - Checks solution correctness
  - Tracks disk conservation

- ✅ **Experiment Runner** (`run_tests.py`)
  - Orchestrates 400 trials
  - Implements Generate→Execute→Validate→Corrupt→Regenerate loop
  - Tracks moves, regenerations, corruptions
  - Outputs results to CSV

- ✅ **Results Analyzer** (`results_analyzer.py`)
  - 3-way ANOVA analysis
  - Descriptive statistics by factor
  - Summary reports and CSV export

## 🚀 Next Steps

### Testing & Validation
- ✅ BFS vs Dig-Out comparison tests (`test_illegal_comparison.py`)
- ✅ BFS validation method in `state_validator.py`
- [ ] Unit tests for `illegal_ground.py`
- [ ] Unit tests for `randomizer.py`
- [ ] Integration tests for experiment pipeline
- [ ] Edge case testing (extreme corruption rates, large n)
- [ ] Performance benchmarking for BFS vs Dig-Out

### Analysis Enhancements
- [ ] Interaction plots (2-way and 3-way)
- [ ] Box plots and histograms
- [ ] Post-hoc tests (Tukey HSD)
- [ ] Effect size calculations (η²)
- [ ] Assumptions validation (normality, homoscedasticity)

### Documentation
- [ ] API documentation for all modules
- [ ] Usage examples and tutorials
- [ ] Experimental design rationale document
- [ ] Results interpretation guide

### Future Experiments
- [ ] Test with different disk counts (3, 7, 10)
- [ ] Additional corruption rates (15%, 20%)
- [ ] Additional ground algorithms
- [ ] Alternative stack algorithms (Bubble Sort, Total Evacuation)
- [ ] Hybrid strategies