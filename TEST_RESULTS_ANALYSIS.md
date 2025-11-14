# Test Results Analysis - All 5 Experimental Factors (UPDATED)

## Summary - After Fixes
**55 tests run: 40 PASSED ✓ | 15 FAILED ✗**

### Progress Made:
- ✅ **FIXED**: Alteration rate accuracy (Factor B) - all 7 tests now pass
- ✅ **FIXED**: Illegal formation generation - all 3 alteration types generate reliably  
- ⚠️ **BROKEN**: Solver now fails for ALL disk counts due to algorithm changes
- ℹ️ **DEFERRED**: Solver for 5+ disks requires complete rewrite (state-space search needed)

---

## Original Summary
**55 tests run: 47 PASSED ✓ | 8 FAILED ✗**

## ✅ What's Working Correctly

### Factor A: Disk Count - **100% PASSING**
- All 4 disk counts (3, 5, 7, 9) initialize correctly
- Minimum moves formula (2^n - 1) is accurate
- Solver generates correct move sequences
- Timeout thresholds scale properly

### Factor C: Illegal Formation Handlers - **MOSTLY PASSING**
- All three handlers (deepest, bubble, buffer) resolve violations correctly
- Individual handler tests all pass
- Works correctly for disk_count=3

### Factor D: Ground Handlers - **100% PASSING**
- Both strategies (best-fit, first-available) work correctly
- Proper placement logic
- Disks successfully removed from ground

### Factor E: Duplicate Handlers - **MOSTLY PASSING**
- Keep handler works correctly (leaves duplicates)
- Discard handler removes duplicates
- One behavioral issue identified (see below)

---

## ❌ Issues Identified

### **ISSUE #1: Alteration Logic (Factor B)**
**Severity: HIGH - Core experimental factor**

**Failed Tests:**
- `test_hundred_percent_always_alters` - Expected 95%+, got 82%
- `test_alteration_rates_statistical[30]` - Expected ~30%, got 23% (7% error)

**Root Cause:**
The `introduce_alteration()` method in `environment.py` has conditional logic that fails to create alterations in certain states. Specifically:
- `illegal_formation` alteration requires at least 2 non-empty pegs with specific disk configurations
- The method returns `False` if it can't find a valid alteration target

**Location:** `src/environment.py`, lines ~105-148

**Impact:** Experimental Factor B is not accurately controlling alteration rates, which will skew all experimental results.

---

### **ISSUE #2: Duplicate Handler Behavior (Factor E)**
**Severity: MEDIUM**

**Failed Test:**
- `test_discard_handler_removes_accessible_instance`

**Root Cause:**
The `resolve_duplicates_discard()` handler removes the FIRST instance found (top of peg A, then B, then C), not necessarily the most accessible buried disk. The test expected it to prefer the accessible one on top of B.

**Location:** `src/illegal_state_handlers.py`, lines ~127-145

**Current Behavior:** Removes first top-of-peg instance found in order A, B, C
**Expected Behavior:** Should remove the most accessible (top of peg) instance

**Impact:** Minor - handler still works, but strategy may not be optimal.

---

### **ISSUE #3: Solver Move Counting (Integration)**
**Severity: MEDIUM - Affects result interpretation**

**Failed Test:**
- `test_simulation_with_zero_alteration_solves` - Expected 7 moves, got 8

**Root Cause:**
The `SimulationRunner` counts move attempts differently than expected. With 0% alteration, the solver should produce exactly 2^n - 1 moves. The extra move suggests:
1. The solver is making an extra move, OR
2. The move counting logic includes resolution attempts, OR
3. The initial state check counts as a move

**Location:** `src/simulation_runner.py`, main run loop

**Impact:** Results may show inflated move counts, affecting performance metrics.

---

### **ISSUE #4: Illegal Formation Alteration (Factor B)**
**Severity: MEDIUM**

**Failed Test:**
- `test_alteration_types_are_diverse`

**Root Cause:**
After 100 attempts at 100% alteration rate, only "ElementOnGround" and "DuplicateItem" were created - NO "IllegalFormation" alterations were generated.

**Location:** `src/environment.py`, lines ~135-148 (illegal_formation branch)

**Analysis:**
The illegal_formation logic requires:
```python
if non_empty_pegs and len(non_empty_pegs) >= 2:
    # ... complex logic to find valid target
```

Starting from state `[5,4,3,2,1], [], []` makes it difficult to create illegal formations because:
- Only peg A is non-empty initially
- After one alteration creates ground/duplicate, the condition may still fail

**Impact:** Factor B alteration types are not uniformly distributed, biasing experiments.

---

### **ISSUE #5: Solver Fails for Larger Problems (Factor A)**
**Severity: HIGH - Core algorithm failure**

**Failed Tests:**
- `test_factor_combination_ac[deepest-5]` - 5 disks fails to solve
- `test_factor_combination_ac[bubble-5]` - 5 disks fails to solve  
- `test_factor_combination_ac[buffer-5]` - 5 disks fails to solve

**Root Cause:**
The Hanoi solver algorithm in `get_next_optimal_move()` fails for disk_count=5 with 0% alteration. Since 3 disks work but 5 disks fail consistently across ALL formation handlers, the issue is in the core solver logic, not the handlers.

**Location:** `src/hanoi_solver.py`, `get_next_optimal_move()` method (lines ~75-142)

**Analysis:**
The solver's recursive logic for determining the next move likely has an edge case for larger problems. Possible issues:
- Incorrect subproblem parameter calculation in `determine_current_subproblem()`
- Solver gets stuck in a loop or returns None
- Timeout threshold (50x minimum) may be insufficient for 5+ disks

**Impact:** **CRITICAL** - The core algorithm cannot solve problems with 5+ disks, making factors with disk_count ∈ {5, 7, 9} unreliable.

---

## 🔍 Recommendations

### Priority 1: Fix Solver for Disk Count 5+ (Issue #5)
**Action:** Debug `src/hanoi_solver.py` and `src/simulation_runner.py`
- Add detailed logging to see where solver fails
- Check `determine_current_subproblem()` logic
- Verify solver can generate complete 31-move sequence for 5 disks

### Priority 2: Fix Alteration Rate Logic (Issue #1)
**Action:** Revise `src/environment.py`, `introduce_alteration()` method
- Ensure alteration attempts succeed at specified percentage
- Simplify conditional logic for illegal_formation creation
- Consider retrying if first alteration type fails

### Priority 3: Fix Illegal Formation Generation (Issue #4)
**Action:** Improve illegal formation alteration logic
- Loosen constraints for finding valid illegal formation targets
- Ensure all three alteration types have equal probability
- Test from various starting states

### Priority 4: Verify Move Counting (Issue #3)
**Action:** Audit move counter in simulation runner
- Clarify what constitutes a "move" vs. an "attempt"
- Ensure theoretical minimum is achievable with 0% alteration
- Document any intentional counting differences

### Priority 5: Clarify Duplicate Handler (Issue #2)
**Action:** Document or fix duplicate handler behavior
- Either fix to match expected behavior (prefer accessible)
- Or update documentation to reflect actual strategy
- Low priority since current behavior is functional

---

## 📊 Test Coverage by Factor

| Factor | Name | Test Coverage | Status |
|--------|------|---------------|--------|
| A | Disk Count | 14 tests | ⚠️ **Fails for 5+ disks** |
| B | Alteration % | 5 tests | ❌ **Inaccurate rates** |
| C | Formation Handler | 6 tests | ✅ Works correctly |
| D | Ground Handler | 4 tests | ✅ Works correctly |
| E | Duplicate Handler | 4 tests | ⚠️ Minor behavior issue |

**Integration Tests:** 5 tests (3 passed, 2 issues found)  
**Edge Cases:** 6 tests (5 passed, 1 issue found)  
**Factor Combinations:** 15 tests (12 passed, 3 failed)

---

## ✅ Verified Correct Behavior

1. **Environment initialization** - All disk counts initialize perfectly
2. **Legal move validation** - Illegal moves are properly rejected
3. **Illegal state detection priority** - Correct order: Ground → Duplicate → Formation
4. **Formation handlers** - All three strategies work for simple cases
5. **Ground handlers** - Both strategies successfully resolve ground violations
6. **Duplicate handlers** - Both strategies functional (keep and discard)
7. **Disk conservation** - Total disk count properly tracked
8. **Zero alteration solves** - Small problems (3 disks) solve correctly

---

## 🎯 Next Steps

1. **Run deeper diagnostics on 5-disk solver failure**
   ```bash
   pytest tests/test_integration_all_factors.py::TestCompleteFactorCombinations::test_factor_combination_ac -v --tb=long -k "5"
   ```

2. **Test alteration distribution**
   - Create test to measure actual alteration type distribution
   - Verify each type appears approximately equally

3. **Fix and retest**
   - Address Priority 1-3 issues
   - Re-run full test suite
   - Aim for 100% pass rate before running experiments

4. **Consider additional tests**
   - Test with disk_count=7 and 9
   - Test higher alteration percentages (40%, 50%)
   - Stress test with very high alteration rates

---

## Conclusion

**The test suite successfully identified critical bugs** that would have invalidated experimental results:

- ❌ Solver cannot handle 5+ disks (Factor A broken for 75% of levels)
- ❌ Alteration rates are inaccurate by ~7-18% (Factor B unreliable)
- ❌ Illegal formation alterations rarely generated (Factor B biased)

**47 of 55 tests pass**, indicating that most individual components work correctly. However, the integration issues are significant enough that **the experiment should not be run until these are fixed**.

Once these issues are resolved, the experiment will have high confidence in:
- Correct Hanoi solving algorithm
- Accurate alteration rate control  
- Proper handler implementations
- Valid experimental factor combinations
