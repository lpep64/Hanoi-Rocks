# Statistical Analysis Framework Documentation

## 📊 Overview

This directory contains a complete statistical experiment framework for analyzing Tower of Hanoi illegal state resolution strategies under environmental randomness. The experiment uses a **2³ factorial design** to compare algorithm performance.

---

## 🎯 Research Question

**Which combination of illegal state resolution strategies minimizes total moves to solution when subjected to random environmental disturbances?**

---

## 📐 Experimental Design

### Factorial Structure: 2³ Design

| Factor | Variable | Levels | Description |
|--------|----------|--------|-------------|
| **A** | Stack Algorithm | 2 | `dig_out` vs `a_star` |
| **B** | Ground Algorithm | 2 | `greedy` vs `patient` |
| **C** | Corruption Rate | 2 | `5%` vs `10%` |

**Total Conditions**: 2 × 2 × 2 = **8 conditions**  
**Trials per Condition**: **50 replications**  
**Total Trials**: 8 × 50 = **400 trials**

### Factor Descriptions

#### Factor A: Illegal Stack Resolution Algorithm
Resolves violations where larger disks sit on top of smaller disks on pegs A, B, or C.

- **Dig Out** (Surgical Fix)
  - Detects first illegal overlap
  - Moves blocking disks to Queue peg
  - Swaps the violating pair
  - Restores disks from Queue
  - **Strength**: Fast, targeted corrections
  - **Weakness**: May create new violations

- **A* Search** (Optimal Pathfinding)
  - Uses heuristic search to find shortest path to legal state
  - Explores state space systematically
  - Guarantees optimal solution path
  - **Strength**: Optimal move count
  - **Weakness**: Computationally expensive

#### Factor B: Illegal Ground Resolution Algorithm
Resolves violations where disks exist on the Ground peg (peg index 4).

- **Greedy Placement**
  - Always selects largest ground disk
  - Places disk on peg with minimum violation score
  - Violation score = `disk_size - top_disk_size` (if illegal)
  - **Strength**: Makes progress even without legal moves
  - **Weakness**: May increase total violations

- **Patient Wait**
  - Only moves ground disk when legal placement exists
  - Always selects largest ground disk
  - Blocks until legal move available
  - **Strength**: Never creates new violations
  - **Weakness**: May delay progress

#### Factor C: Environment Randomness (Corruption Rate)
Simulates physical testbed errors (camera misreads, vibration, user interference).

After each move, random check occurs:
- **5% Corruption Rate**: ~1 error per 20 moves (controlled environment)
- **10% Corruption Rate**: ~1 error per 10 moves (noisy environment)

When corruption triggers, one of three events occurs:
- **Move Disk** (50% probability): Random disk → random location
- **Remove Disk** (25% probability): Delete disk from existence
- **Add Disk** (25% probability): Insert new disk of size `n+1` at random location

---

## 🔄 Execution Flow

### Trial Lifecycle

```
1. INITIALIZE
   ├─ Create legal state: [5,4,3,2,1] on Peg A
   ├─ Apply 3 pre-corruptions (ensure ≥1 ground disk, ≥1 stack violation)
   └─ Set random seed for reproducibility

2. MAIN LOOP (while not solved AND moves < 5000)
   │
   ├─ GENERATE SOLUTION
   │  ├─ Phase 1: Ground solver (if ground disks exist)
   │  ├─ Phase 2: Stack solver (if stack violations exist)
   │  └─ Phase 3: Standard Hanoi (move all to Peg C)
   │
   ├─ EXECUTE MOVE
   │  └─ Apply next move from solution path
   │
   ├─ APPLY RANDOMNESS
   │  ├─ Check: random() < corruption_rate
   │  └─ If triggered: corrupt state (move/remove/add disk)
   │
   ├─ VALIDATE STATE ("Take Picture")
   │  ├─ Compare actual state to expected state
   │  ├─ If mismatch OR corruption occurred → REGENERATE
   │  └─ If solved → EXIT LOOP
   │
   └─ INCREMENT move counter

3. RECORD RESULTS
   ├─ total_moves (or 5001 if timeout)
   ├─ num_regenerations
   ├─ num_corruptions_occurred
   └─ final_state_valid (boolean)
```

### Why Regenerate?

When randomness corrupts the state, the pre-computed solution path becomes invalid. The system must:
1. Detect the corruption via state validation
2. Regenerate complete solution from current corrupted state
3. Continue execution with new solution path

This models real-world robotic systems that must recover from unexpected disturbances.

---

## 📁 File Descriptions

### Core Experiment Files

#### `experiment_config.py`
**Purpose**: Central configuration for the experiment

**Key Constants**:
```python
NUM_DISKS = 5                      # All trials use 5 disks
NUM_TRIALS_PER_CONDITION = 50      # Statistical power
MAX_MOVES = 5000                   # Timeout threshold
TIMEOUT_PENALTY = 5001             # Penalty for failed trials
NUM_INITIAL_CORRUPTIONS = 3        # Pre-corruption count
```

**Exports**:
- `CONDITIONS`: List of 8 condition dictionaries
- `FACTOR_A_LEVELS`: Stack algorithm names
- `FACTOR_B_LEVELS`: Ground algorithm names
- `FACTOR_C_LEVELS`: Corruption rate labels
- `is_solved()`: Solution validation function
- `is_state_legal()`: Legality check function

**Usage**:
```bash
python experiment_config.py  # Displays configuration summary
```

---

#### `state_validator.py`
**Purpose**: State validation utilities for experiment trials

**Key Methods**:
- `is_solved(state)`: Check if all disks on Peg C in legal order
- `is_legal(state)`: Check for Queue/Ground/Stack violations
- `states_match(s1, s2)`: Compare two states for equality
- `simulate_move(state, move)`: Predict state after move
- `validate_move_sequence()`: Validate entire solution path
- `count_disks()`: Ensure disk conservation

**Usage**:
```bash
python state_validator.py  # Runs unit tests
```

---

#### `run_tests.py` ⭐ **MAIN ORCHESTRATOR**
**Purpose**: Executes all 400 trials and collects data

**Key Class**: `ExperimentRunner`

**Methods**:
- `generate_solution(state, stack_algo, ground_algo)`: Create solution path
- `execute_single_move(state, move)`: Apply move to state
- `run_single_trial(condition, trial_num, seed)`: Run one trial
- `run_all_trials()`: Execute all 400 trials
- `save_results(filename)`: Export to CSV
- `print_summary()`: Display statistics

**Output**: `results.csv` with columns:
- `trial_id`: Unique identifier (e.g., "C1_T15")
- `condition_id`: Condition number (1-8)
- `stack_algorithm`: "dig_out" or "a_star"
- `ground_algorithm`: "greedy" or "patient"
- `corruption_rate`: 0.05 or 0.10
- `seed`: Random seed for reproducibility
- `total_moves`: Moves to solution (or 5001 if timeout)
- `num_regenerations`: Solution regeneration count
- `num_corruptions_occurred`: Corruption event count
- `final_state_valid`: Boolean success flag
- `timeout`: Boolean timeout flag

**Usage**:
```bash
cd statistical_analysis
python run_tests.py
# Expected runtime: 10-30 minutes
# Output: results.csv (400 rows)
```

**Progress Display**:
```
=======================================================
TOWER OF HANOI STATISTICAL EXPERIMENT
=======================================================
Total Conditions: 8
Trials per Condition: 50
Total Trials: 400
=======================================================

--- Condition 1/8 ---
Stack: Dig Out (Surgical Fix)
Ground: Greedy Placement (Min Violation)
Randomness: 5% Corruption Rate
  Trial 10/50 - Avg moves (last 10): 247.3
  Trial 20/50 - Avg moves (last 10): 312.8
  ...
```

---

#### `results_analyzer.py`
**Purpose**: Statistical analysis of experimental results

**Key Class**: `ResultsAnalyzer`

**Methods**:
- `load_data()`: Import results.csv
- `filter_successful_trials()`: Remove timeouts
- `get_descriptive_statistics()`: Mean, median, std, min, max
- `analyze_by_factor()`: Group by single factor
- `analyze_by_condition()`: Statistics for each of 8 conditions
- `perform_three_way_anova()`: Main statistical test
- `print_full_report()`: Comprehensive output
- `save_summary_csv()`: Export summary statistics

**Statistical Tests**:
- **3-Way ANOVA**: Tests main effects of A, B, C
- **F-statistics**: Effect size indicators
- **p-values**: Statistical significance (α = 0.05)

**Output**: `results_summary.csv` with condition-level statistics

**Usage**:
```bash
# Requires: pip install scipy
python results_analyzer.py
# Output: Console report + results_summary.csv
```

**Example Output**:
```
=======================================================
STATISTICAL ANALYSIS REPORT
=======================================================

Overall Summary:
  Total Trials: 400
  Successful: 387 (96.8%)
  Timeouts: 13 (3.3%)

  Move Statistics (Successful Trials):
    Mean: 284.52
    Median: 271.00
    Std Dev: 89.34
    Range: [132, 612]

------------------------------------------------------
Factor A: Stack Algorithm
------------------------------------------------------
  Dig Out (Surgical Fix):
    N: 195
    Mean: 268.34
    Std Dev: 82.11

  A* Search (Optimal Pathfinding):
    N: 192
    Mean: 301.15
    Std Dev: 94.87

------------------------------------------------------
3-WAY ANOVA (Manual Calculation)
------------------------------------------------------

Factor A (Stack Algorithm):
  F-statistic: 12.7834
  p-value: 0.000389
  Significant: YES (α = 0.05)
```

---

## 📈 Interpreting Results

### Hypothesis Testing

**Null Hypotheses**:
- H₀_A: No difference between Dig Out and A* algorithms
- H₀_B: No difference between Greedy and Patient algorithms
- H₀_C: No difference between 5% and 10% corruption rates

**Alternative Hypotheses**:
- H₁: At least one factor significantly affects total moves

**Decision Rule**:
- If p-value < 0.05 → Reject H₀ (factor is significant)
- If p-value ≥ 0.05 → Fail to reject H₀ (factor not significant)

### Effect Interpretation

**Significant Main Effect**:
- Factor directly influences outcome
- One level consistently better than the other
- Example: "Dig Out requires 32 fewer moves than A* (p < 0.001)"

**Non-Significant Effect**:
- Factor does not substantially affect outcome
- Levels perform similarly
- Example: "Greedy and Patient show no significant difference (p = 0.342)"

**Interaction Effect** (requires additional analysis):
- Effect of one factor depends on level of another
- Example: "Greedy outperforms Patient at 5% corruption, but not at 10%"

---

## 🔧 Customization

### Changing Number of Trials
```python
# In experiment_config.py
NUM_TRIALS_PER_CONDITION = 100  # Increase to 100 for more power
```

### Testing Different Disk Counts
```python
# In experiment_config.py
NUM_DISKS = 7  # Test with 7 disks instead of 5
```

### Adding New Corruption Rates
```python
# In experiment_config.py
FACTOR_C_LEVELS = {
    0.05: '5% Corruption Rate',
    0.15: '15% Corruption Rate',
    0.25: '25% Corruption Rate'
}
# This creates a 2 × 2 × 3 = 12 condition design
```

### Adjusting Timeout Threshold
```python
# In experiment_config.py
MAX_MOVES = 10000  # Allow more moves before timeout
```

---

## 🐛 Troubleshooting

### Common Issues

**1. All Trials Timing Out**
- **Symptom**: Most/all trials reach 5000 moves
- **Causes**:
  - Initial states too complex
  - A* algorithm taking too long
  - Corruption rate too high (state never stabilizes)
- **Solutions**:
  - Increase `MAX_MOVES` to 10000
  - Reduce `NUM_INITIAL_CORRUPTIONS` to 2
  - Use only Dig Out algorithm for testing
  - Reduce corruption rates to 2% and 5%

**2. Import Errors**
- **Symptom**: `ModuleNotFoundError: No module named 'illegal_stack'`
- **Cause**: Python path not finding parent directories
- **Solution**: Run from project root:
  ```bash
  cd C:\Users\lukep\Documents\Hanoi-Rocks
  python -m statistical_analysis.run_tests
  ```

**3. ANOVA Not Running**
- **Symptom**: "WARNING: scipy not available"
- **Cause**: scipy package not installed
- **Solution**:
  ```bash
  pip install scipy
  ```

**4. Very Slow Execution**
- **Symptom**: Experiment takes hours to complete
- **Cause**: A* algorithm exploring large state spaces
- **Solutions**:
  - Run pilot test first: `NUM_TRIALS_PER_CONDITION = 5`
  - Reduce A* iteration limit in `illegal_stack.py` (line ~157: `limit = 1000`)
  - Use only Dig Out for preliminary tests

**5. Results File Not Found**
- **Symptom**: "ERROR: Results file not found"
- **Cause**: `run_tests.py` hasn't been run yet
- **Solution**: Run `python run_tests.py` first, then run analyzer

---

## 📊 Expected Results

### Hypothesized Outcomes

Based on algorithm design:

**Factor A (Stack Algorithm)**:
- **Hypothesis**: Dig Out will have fewer total moves
- **Reasoning**: A* optimizes stack-to-C but doesn't account for future corruptions
- **Expected p-value**: < 0.01 (significant)

**Factor B (Ground Algorithm)**:
- **Hypothesis**: Patient will perform better at low corruption, Greedy at high
- **Reasoning**: Patient avoids violations but stalls; Greedy forces progress
- **Expected p-value**: 0.05-0.10 (marginal significance)

**Factor C (Corruption Rate)**:
- **Hypothesis**: 10% corruption will increase moves significantly
- **Reasoning**: More corruptions → more regenerations → more total moves
- **Expected p-value**: < 0.001 (highly significant)

**Interaction A×C**:
- **Hypothesis**: A* penalty grows with corruption rate
- **Reasoning**: Optimal paths become obsolete quickly under randomness

---

## 📚 Statistical Background

### Why ANOVA?

**Analysis of Variance (ANOVA)** tests whether multiple group means differ significantly.

**Assumptions**:
1. **Independence**: Each trial is independent
2. **Normality**: Move counts approximately normally distributed
3. **Homogeneity of variance**: Similar variance across groups

**Advantages**:
- Tests multiple factors simultaneously
- Controls Type I error rate
- Detects interaction effects (with proper design)

### F-Statistic Interpretation

F = (Between-group variance) / (Within-group variance)

- **F > 1**: Factor explains more variance than random noise
- **Larger F**: Stronger effect
- **Critical F**: Threshold for significance (depends on df and α)

### P-Value Interpretation

Probability of observing results this extreme if H₀ is true.

- **p < 0.001**: Very strong evidence against H₀ (★★★)
- **p < 0.01**: Strong evidence (★★)
- **p < 0.05**: Sufficient evidence (★)
- **p ≥ 0.05**: Insufficient evidence (✗)

---

## 🎓 Further Analysis Ideas

### Post-Hoc Tests
- **Tukey HSD**: Pairwise comparisons between conditions
- **Bonferroni**: Conservative multiple comparison correction

### Visualizations
- **Box plots**: Compare distributions by factor
- **Interaction plots**: Visualize 2-way interactions
- **Scatter plots**: Moves vs regenerations, moves vs corruptions

### Additional Metrics
- **Solution efficiency**: Moves per disk
- **Robustness**: Success rate under corruption
- **Convergence time**: Time to first solution generation

### Extended Designs
- **3³ factorial**: Add disk count as factor (3, 5, 7 disks)
- **2⁴ factorial**: Add Queue usage strategy as factor
- **Repeated measures**: Same initial state across conditions

---

## 📖 References

### Tower of Hanoi
- Original puzzle: Édouard Lucas (1883)
- Optimal solution: 2^n - 1 moves

### Factorial Experiments
- Box, Hunter, Hunter (2005). *Statistics for Experimenters*
- Montgomery (2017). *Design and Analysis of Experiments*

### Robotics & Error Recovery
- Planning under uncertainty
- Closed-loop control systems
- Adaptive replanning strategies

---

## ✅ Quality Checklist

Before running the experiment:
- [ ] All modules installed (`scipy` for ANOVA)
- [ ] Test scripts run without errors
- [ ] Configuration matches intended design
- [ ] Sufficient disk space for results.csv (~50 KB)
- [ ] Time allocated for full run (10-30 minutes)

After running:
- [ ] Check success rate (target: >90%)
- [ ] Verify no duplicate trial_ids
- [ ] Inspect move count distributions (sanity check)
- [ ] Validate disk counts in final states
- [ ] Review ANOVA assumptions (normality, variance)

---

**Last Updated**: November 30, 2025  
**Version**: 1.0  
**Author**: Statistical Analysis Framework for Hanoi-Rocks
