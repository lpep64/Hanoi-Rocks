# Statistical Experiment Quick Start Guide

## 📁 New Files Created

### Illegal Solutions (illegal_solutions/)
1. **illegal_ground.py** - Ground disk violation solvers
   - Greedy: Places largest ground disk with min violation
   - Patient: Waits for legal move opportunity

2. **randomizer.py** - Environment corruption simulator
   - Move disk (50%), Remove disk (25%), Add disk (25%)
   - Seeded randomness for reproducibility
   - Creates structured pre-corrupted initial states

3. **illegal_stack.py** (UPDATED) - Removed Bubble Sort & Total Evacuation
   - Now contains only: Dig Out and A* Search

### Statistical Analysis (statistical_analysis/)
4. **experiment_config.py** - Experimental design configuration
   - 2³ factorial: 8 conditions × 50 trials = 400 total
   - Factor definitions and constants

5. **state_validator.py** - State validation utilities
   - Check solution correctness
   - Validate disk conservation
   - Detect illegal states

6. **run_tests.py** - Main experiment orchestrator
   - Runs all 400 trials
   - Implements Generate→Execute→Validate→Corrupt→Regenerate loop
   - Outputs: results.csv

7. **results_analyzer.py** - Statistical analysis
   - 3-way ANOVA
   - Descriptive statistics
   - Outputs: results_summary.csv

### Documentation
8. **TODO.md** (UPDATED) - Updated with completed features
9. **README.md** (UPDATED) - Comprehensive project documentation

---

## 🚀 How to Run the Experiment

### Step 1: Test Individual Components (Optional)
```bash
# Test illegal ground solver
python illegal_solutions/illegal_ground.py

# Test randomizer
python illegal_solutions/randomizer.py

# Test illegal stack solver
python illegal_solutions/illegal_stack.py

# Test state validator
python statistical_analysis/state_validator.py

# Test experiment config
python statistical_analysis/experiment_config.py
```

### Step 2: Run the Full Experiment
```bash
cd statistical_analysis
python run_tests.py
```

**Expected Runtime**: 10-30 minutes (depending on hardware)
**Output**: `results.csv` with 400 trial results

### Step 3: Analyze Results
```bash
# Requires scipy: pip install scipy
python results_analyzer.py
```

**Output**:
- Console: Comprehensive statistical report
- File: `results_summary.csv` with condition-level summaries

---

## 📊 Experimental Design Summary

### Factor A: Stack Algorithm (2 levels)
- **dig_out**: Surgical fix targeting first illegal overlap
- **a_star**: Optimal pathfinding to legal state

### Factor B: Ground Algorithm (2 levels)
- **greedy**: Place largest ground disk with minimum violation
- **patient**: Wait for legal move opportunity

### Factor C: Corruption Rate (2 levels)
- **5%**: Low environmental randomness
- **10%**: High environmental randomness

### Metrics Collected
- `total_moves`: Total moves to solution (or 5001 if timeout)
- `num_regenerations`: Number of solution regenerations
- `num_corruptions_occurred`: Number of random corruptions
- `final_state_valid`: Boolean, is final state correct?
- `timeout`: Boolean, did trial exceed 5000 moves?

---

## 🔧 Configuration Options

Edit `experiment_config.py` to adjust:

```python
NUM_DISKS = 5  # Number of disks per trial
NUM_TRIALS_PER_CONDITION = 50  # Trials per condition
MAX_MOVES = 5000  # Timeout threshold
TIMEOUT_PENALTY = 5001  # Penalty value for timeouts
NUM_INITIAL_CORRUPTIONS = 3  # Pre-corruption count
```

---

## 📈 Understanding Results

### Success Metrics
- **Mean Moves**: Lower is better (more efficient)
- **Success Rate**: % of trials without timeout
- **Regenerations**: Fewer indicates more robust solution

### ANOVA Output
- **F-statistic**: Effect size (larger = stronger effect)
- **p-value**: Significance (p < 0.05 = significant)
- Look for:
  - Main effects: Which factors matter?
  - Interactions: Do factors interact?

---

## 🐛 Troubleshooting

### Import Errors
If you see "Module not found" errors, the sys.path additions should handle this.
But you can also run from project root:
```bash
cd c:\Users\lukep\Documents\Hanoi-Rocks
python -m statistical_analysis.run_tests
```

### ANOVA Not Running
```bash
pip install scipy
```

### Slow Performance
- A* algorithm is computationally expensive
- Consider reducing `NUM_TRIALS_PER_CONDITION` to 10 for quick tests
- Or increase `MAX_MOVES` if trials are timing out

### All Trials Timeout
- Check if initial states are solvable
- Increase `MAX_MOVES` to 10000
- Verify algorithm implementations

---

## 📝 Next Steps

1. **Run pilot test**: Set `NUM_TRIALS_PER_CONDITION = 5` for quick validation
2. **Run full experiment**: Restore to 50 trials
3. **Analyze results**: Check for significant effects
4. **Visualize**: Create plots (see TODO.md for ideas)
5. **Iterate**: Adjust factors based on findings

---

## 💡 Tips

- Use `seed` parameter for reproducible results
- Monitor console output during experiments
- Check `results.csv` periodically during long runs
- Back up results before re-running experiments
- Document any manual changes to configuration

---

Good luck with your experiment! 🎉
