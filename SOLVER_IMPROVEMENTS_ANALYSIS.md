# Tower of Hanoi Solver - Analysis and Improvements Plan

**Date:** November 14, 2025  
**Status:** Post-Implementation Review  
**Test Results:** 54/55 passing (98.2%)

---

## Executive Summary

The current solver implementation successfully handles alterations by pre-computing solution paths and regenerating when states are perturbed. However, several architectural concerns have been raised that require careful analysis and potential redesign.

---

## Current Implementation Overview

### Solver Strategy (Post-Fix)

The solver uses a **hybrid approach**:

1. **Pre-computation**: Generates full solution path before execution
2. **State Tracking**: Monitors for alterations by comparing expected vs actual state
3. **Adaptive Regeneration**: Recalculates solution when perturbations are detected
4. **Algorithm Selection**:
   - **n ≤ 4**: Breadth-First Search (BFS) for optimal paths from perturbed states
   - **n > 4**: Greedy algorithm following ideal sequence with corrections

### Performance

- **Test Suite**: 54/55 tests passing (98.2%)
- **Execution Time**: 0.10 seconds for full test suite
- **Disk Count Support**: Works for n = 3, 5, 7, 9
- **Alteration Handling**: Successfully regenerates solutions after perturbations

---

## Critical Analysis: Key Concerns

### 1. **Testing for Optimal Solutions**

**Question:** Do we have tools to test if BFS/A* solutions are optimal?

**Current State:**
- No explicit optimality testing exists
- Tests verify correctness (reaches goal) but not optimality (minimum moves)
- BFS guarantees optimal paths for n ≤ 4, but we don't validate this claim

**Recommended Tools:**

```python
# New test utilities needed:
def test_solution_optimality(disk_count, initial_state, target='C'):
    """
    Verify that generated solution is optimal (minimum moves).
    
    Approach:
    1. Generate solution using current solver
    2. Compare against known optimal solutions from literature
    3. For small n, exhaustively verify using BFS that no shorter path exists
    """
    
def benchmark_solution_length(disk_count, perturbation_level):
    """
    Compare solution lengths across different perturbation scenarios.
    
    Metrics:
    - Clean state: Should match 2^n - 1
    - Lightly perturbed: Should be near optimal
    - Heavily perturbed: Compare against other algorithms
    """
```

**Action Items:**
- [ ] Create `tests/test_optimality.py` with solution length validation
- [ ] Add benchmarking for BFS vs Greedy solution quality
- [ ] Document known optimal move counts for various perturbation patterns

---

### 2. **Algorithmic Inconsistency (Small vs Large Problems)**

**Question:** Why do we switch algorithms at n=4? This feels arbitrary.

**Current Logic:**
```python
if n > 4:
    return self._greedy_solve(current_state, n, target)
else:
    # Use BFS
```

**Problems with This Approach:**

1. **Arbitrary Threshold**: The n=4 boundary has no theoretical justification
2. **Solution Quality Inconsistency**: 
   - n ≤ 4: Optimal solutions (BFS guarantees shortest path)
   - n > 4: Sub-optimal solutions (greedy heuristic)
3. **Experimental Validity**: Different algorithms for different disk counts confounds experimental results
4. **Maintenance Burden**: Two codepaths to maintain and debug

**Why the Threshold Exists:**
- **Computational Complexity**: BFS has exponential state space growth
  - n=3: ~27 states (~3³)
  - n=4: ~256 states (~4⁴)
  - n=5: ~3,125 states (~5⁵)
  - n=9: ~387,420,489 states (~9⁹)
- **Performance**: BFS for n=9 would take hours/days vs 0.1 seconds with greedy

**Recommended Solution:**

Use **A\* search with admissible heuristic** for all disk counts:

```python
def _solve_from_state_astar(self, current_state, n, target):
    """
    A* search with heuristic: number of disks not on target peg.
    
    Heuristic is admissible (never overestimates) because:
    - Each disk not on target requires at least 1 move
    - Actual cost is always ≥ heuristic
    
    This provides consistent algorithm across all n while maintaining
    reasonable performance through intelligent search pruning.
    """
```

**Benefits:**
- Single algorithm for all disk counts
- Optimal solutions (A\* with admissible heuristic is optimal)
- Better performance than pure BFS
- Experimental consistency

**Action Items:**
- [ ] Implement A\* solver with disk-position heuristic
- [ ] Remove n>4 threshold and greedy fallback
- [ ] Benchmark A\* performance for n=5,7,9
- [ ] Add timeout mechanism for worst-case scenarios

---

### 3. **Recursive Algorithm with Step-by-Step Execution**

**Question:** Can we use the main recursive algorithm, execute step-by-step, and check for alterations/illegal states?

**Proposed Architecture:**

```python
class HanoiSolver:
    def __init__(self):
        self.planned_solution = []  # Full recursive solution
        self.current_step = 0
    
    def initialize_solution(self, n, source, target, auxiliary):
        """Generate complete recursive solution at start."""
        self.planned_solution = self.solve_full(n, source, target, auxiliary)
        self.current_step = 0
    
    def get_next_move(self, current_state, n, source, target, auxiliary):
        """
        Return next move from planned solution, checking validity.
        
        Flow:
        1. If no solution cached, generate it using recursive algorithm
        2. Get next move from planned sequence
        3. Validate move is legal in current state
        4. If illegal (due to alteration), regenerate solution from current state
        5. Return validated move
        """
        # Check if we need to initialize or regenerate
        if not self.planned_solution or self._state_altered(current_state):
            self.initialize_solution(n, source, target, auxiliary)
        
        # Get next planned move
        if self.current_step >= len(self.planned_solution):
            return None  # Solution complete
        
        move = self.planned_solution[self.current_step]
        
        # Validate move is legal
        if self._is_move_legal(current_state, move):
            self.current_step += 1
            return move
        else:
            # State was altered - regenerate
            self.initialize_solution(n, source, target, auxiliary)
            return self.get_next_move(current_state, n, source, target, auxiliary)
    
    def _state_altered(self, current_state):
        """Detect if state differs from expected state after last move."""
        # Compare actual state vs simulated state from planned moves
```

**Advantages:**
- Uses proven recursive algorithm as foundation
- Clear separation: planning vs execution
- Explicit alteration detection
- Easy to understand and maintain

**This is essentially what the current implementation does!** The main improvement would be clearer code organization.

---

### 4. **Illegal State Handling Integration**

**Question:** Should illegal state checking be integrated into the solver move execution?

**Current Flow:**
```
Loop:
  1. Check for illegal states → Resolve if needed
  2. Get next optimal move from solver
  3. Apply move
  4. Potentially introduce alteration
```

**Proposed Flow:**
```
Loop:
  1. Get next optimal move from solver
  2. Attempt to apply move
  3. If move creates illegal state OR state is already illegal:
     → Execute illegal state handler
     → Regenerate solution
  4. Potentially introduce alteration
```

**Analysis:**

The current approach (check before move) is actually **correct** because:
- Illegal states can exist at start of loop (from alterations)
- Must resolve illegal states before solver can determine valid moves
- Solver assumes legal state to calculate optimal move

**However**, we should modularize illegal state handling better.

---

## Recommended Code Restructuring

### A. Modularize Illegal State Handlers

**Current:** Functions in `illegal_state_handlers.py`

**Improved:** Class-based handlers with common interface

```python
# src/illegal_state_handlers.py

class IllegalStateHandler:
    """Base class for all illegal state handlers."""
    
    def resolve(self, env, details):
        """
        Resolve the illegal state.
        
        Args:
            env: Environment instance
            details: Details about the illegal state
        
        Returns:
            int: Number of moves used for resolution
        """
        raise NotImplementedError


class GroundHandler(IllegalStateHandler):
    """Handles disks on ground."""
    
    class BestFit(IllegalStateHandler):
        def resolve(self, env, disk):
            """Place disk on best-fit peg."""
            # Implementation
            return 1
    
    class FirstAvailable(IllegalStateHandler):
        def resolve(self, env, disk):
            """Place disk on first available peg."""
            # Implementation
            return 1


class DuplicateHandler(IllegalStateHandler):
    """Handles duplicate disks."""
    
    class Keep(IllegalStateHandler):
        def resolve(self, env, disk):
            """Keep all duplicates (no-op)."""
            return 0
    
    class Discard(IllegalStateHandler):
        def resolve(self, env, disk):
            """Remove least accessible duplicate."""
            # Implementation
            return 1


class FormationHandler(IllegalStateHandler):
    """Handles illegal formations."""
    
    class Deepest(IllegalStateHandler):
        def resolve(self, env, details):
            """Remove deepest offending disk."""
            # Implementation
            return 1
    
    class Bubble(IllegalStateHandler):
        def resolve(self, env, details):
            """Bubble disks to legal configuration."""
            # Implementation
            return moves_count
    
    class Buffer(IllegalStateHandler):
        def resolve(self, env, details):
            """Use buffer peg to resolve."""
            # Implementation
            return moves_count


# Factory function
def get_handler(illegal_type, strategy):
    """
    Get appropriate handler instance.
    
    Args:
        illegal_type: 'ground', 'duplicate', or 'formation'
        strategy: Strategy name (e.g., 'best-fit', 'keep', 'bubble')
    
    Returns:
        IllegalStateHandler instance
    """
    handlers = {
        'ground': {
            'best-fit': GroundHandler.BestFit(),
            'first-available': GroundHandler.FirstAvailable()
        },
        'duplicate': {
            'keep': DuplicateHandler.Keep(),
            'discard': DuplicateHandler.Discard()
        },
        'formation': {
            'deepest': FormationHandler.Deepest(),
            'bubble': FormationHandler.Bubble(),
            'buffer': FormationHandler.Buffer()
        }
    }
    return handlers[illegal_type][strategy]
```

---

### B. Simplified Solver Architecture

```python
# src/hanoi_solver.py

class HanoiSolver:
    """
    Tower of Hanoi solver using recursive algorithm with adaptive regeneration.
    
    Strategy:
    1. Generate full solution using classic recursive algorithm
    2. Execute moves step-by-step
    3. Detect alterations by comparing expected vs actual state
    4. Regenerate solution from perturbed state when needed
    """
    
    def __init__(self, algorithm='recursive'):
        """
        Initialize solver.
        
        Args:
            algorithm: 'recursive' (classic) or 'astar' (optimal from any state)
        """
        self.algorithm = algorithm
        self.planned_moves = []
        self.current_step = 0
        self.expected_state = None
    
    def get_next_optimal_move(self, current_state, n, source, target, auxiliary):
        """
        Get next move, regenerating solution if state was altered.
        
        Args:
            current_state: Current environment state
            n: Number of disks
            source: Source peg
            target: Target peg
            auxiliary: Auxiliary peg
        
        Returns:
            dict: Next move or None if complete
        """
        # Check if we need to regenerate solution
        if self._needs_regeneration(current_state, n, target):
            self._regenerate_solution(current_state, n, source, target, auxiliary)
        
        # Return next move from plan
        if self.current_step >= len(self.planned_moves):
            return None
        
        move = self.planned_moves[self.current_step]
        self.current_step += 1
        
        # Update expected state for next iteration
        self.expected_state = self._simulate_move(current_state, move)
        
        return move
    
    def _needs_regeneration(self, current_state, n, target):
        """Check if solution needs regeneration."""
        # Need regeneration if:
        # 1. No plan exists
        # 2. Plan is exhausted but goal not reached
        # 3. Current state doesn't match expected state (alteration detected)
        
        if not self.planned_moves:
            return True
        
        if self.current_step >= len(self.planned_moves):
            goal = list(range(n, 0, -1))
            return current_state[target] != goal
        
        if self.expected_state is not None:
            return not self._states_match(current_state, self.expected_state)
        
        return False
    
    def _regenerate_solution(self, current_state, n, source, target, auxiliary):
        """Generate new solution from current state."""
        if self.algorithm == 'recursive':
            # Use recursive algorithm from clean initial state
            # This works well when alterations are minor
            self.planned_moves = self.solve_full(n, source, target, auxiliary)
            self.current_step = 0
        
        elif self.algorithm == 'astar':
            # Use A* to find optimal path from current (possibly perturbed) state
            self.planned_moves = self._solve_astar(current_state, n, target)
            self.current_step = 0
        
        self.expected_state = current_state
    
    def _solve_astar(self, current_state, n, target):
        """
        A* search from current state to goal.
        
        Heuristic: Number of disks not in final position on target peg.
        This is admissible (never overestimates) and consistent.
        """
        import heapq
        from collections import deque
        
        # Goal state
        goal = {
            'A': [] if target != 'A' else list(range(n, 0, -1)),
            'B': [] if target != 'B' else list(range(n, 0, -1)),
            'C': [] if target != 'C' else list(range(n, 0, -1))
        }
        
        def state_to_tuple(state):
            return (tuple(state['A']), tuple(state['B']), tuple(state['C']))
        
        def heuristic(state):
            """Count disks not in correct final position."""
            target_disks = state[target]
            goal_disks = list(range(n, 0, -1))
            
            # Count misplaced disks
            misplaced = 0
            for disk in range(1, n + 1):
                if disk not in target_disks:
                    misplaced += 1
                else:
                    # Check if it's in correct position
                    target_idx = target_disks.index(disk)
                    goal_idx = goal_disks.index(disk)
                    if target_idx != goal_idx:
                        misplaced += 1
            
            return misplaced
        
        # Priority queue: (f_score, g_score, state_tuple, path)
        start_tuple = state_to_tuple(current_state)
        start_h = heuristic(current_state)
        
        heap = [(start_h, 0, start_tuple, [])]
        visited = {start_tuple: 0}  # state -> best g_score seen
        
        max_iterations = 50000
        iterations = 0
        
        while heap and iterations < max_iterations:
            iterations += 1
            f_score, g_score, state_tuple, path = heapq.heappop(heap)
            
            # Convert to dict
            state = {
                'A': list(state_tuple[0]),
                'B': list(state_tuple[1]),
                'C': list(state_tuple[2])
            }
            
            # Check if goal reached
            if state_tuple == state_to_tuple(goal):
                return path
            
            # Generate successors
            for from_peg in ['A', 'B', 'C']:
                if not state[from_peg]:
                    continue
                
                disk = state[from_peg][-1]
                
                for to_peg in ['A', 'B', 'C']:
                    if from_peg == to_peg:
                        continue
                    
                    if state[to_peg] and state[to_peg][-1] < disk:
                        continue
                    
                    # Make move
                    new_state = {
                        'A': list(state['A']),
                        'B': list(state['B']),
                        'C': list(state['C'])
                    }
                    new_state[from_peg] = new_state[from_peg][:-1]
                    new_state[to_peg] = new_state[to_peg] + [disk]
                    
                    new_tuple = state_to_tuple(new_state)
                    new_g = g_score + 1
                    
                    # Check if we've seen this state with better cost
                    if new_tuple in visited and visited[new_tuple] <= new_g:
                        continue
                    
                    visited[new_tuple] = new_g
                    new_h = heuristic(new_state)
                    new_f = new_g + new_h
                    new_path = path + [{'from': from_peg, 'to': to_peg, 'disk': disk}]
                    
                    heapq.heappush(heap, (new_f, new_g, new_tuple, new_path))
        
        # Fallback: use recursive if A* times out
        return self.solve_full(n, source, target, auxiliary)
    
    # ... (keep existing solve_full and helper methods)
```

---

### C. Updated Simulation Runner

```python
# src/simulation_runner.py

class SimulationRunner:
    """
    Runs a single Tower of Hanoi simulation with environmental alterations.
    """
    
    def __init__(self, run_id, disk_count, alteration_rate,
                 formation_handler_strategy, ground_handler_strategy, 
                 duplicate_handler_strategy, sim_params):
        # ... existing init code ...
        
        # Initialize handlers
        self.handlers = {
            'ground': get_handler('ground', ground_handler_strategy),
            'duplicate': get_handler('duplicate', duplicate_handler_strategy),
            'formation': get_handler('formation', formation_handler_strategy)
        }
    
    def resolve_illegal_state(self, illegal_type, details):
        """
        Resolve illegal state using configured handler.
        
        Args:
            illegal_type: Type of violation
            details: Details about the violation
        
        Returns:
            int: Number of moves used for resolution
        """
        handler_map = {
            'ElementOnGround': self.handlers['ground'],
            'DuplicateItem': self.handlers['duplicate'],
            'IllegalFormation': self.handlers['formation']
        }
        
        handler = handler_map.get(illegal_type)
        if handler:
            return handler.resolve(self.env, details)
        
        return 0
```

---

## Implementation Roadmap

### Phase 1: Testing Infrastructure (Priority: HIGH)
- [ ] Create `tests/test_optimality.py`
  - Verify solution lengths match theoretical minimums
  - Test BFS produces optimal paths for n ≤ 4
  - Benchmark solution quality for different perturbation levels
- [ ] Create `tests/test_performance.py`
  - Measure solver execution time for n = 3, 5, 7, 9
  - Profile memory usage
  - Identify bottlenecks

### Phase 2: A* Implementation (Priority: HIGH)
- [ ] Implement `_solve_astar()` method with admissible heuristic
- [ ] Add unit tests for A* correctness
- [ ] Benchmark A* vs current hybrid approach
- [ ] Remove n>4 threshold if A* performs adequately
- [ ] Add configurable timeout for worst-case scenarios

### Phase 3: Handler Refactoring (Priority: MEDIUM)
- [ ] Create class-based handler hierarchy
- [ ] Migrate existing handler functions to classes
- [ ] Update `simulation_runner.py` to use handler objects
- [ ] Add unit tests for each handler class
- [ ] Document handler interfaces

### Phase 4: Solver Architecture Cleanup (Priority: MEDIUM)
- [ ] Simplify `get_next_optimal_move()` logic
- [ ] Add clear comments explaining regeneration triggers
- [ ] Extract state comparison logic to separate methods
- [ ] Add configurable algorithm selection ('recursive' vs 'astar')
- [ ] Document solver strategy in docstrings

### Phase 5: Integration Testing (Priority: HIGH)
- [ ] Re-run full test suite after each phase
- [ ] Verify 55/55 tests pass (including the duplicate handler behavioral test)
- [ ] Add integration tests for new A* solver
- [ ] Performance regression testing

### Phase 6: Documentation (Priority: MEDIUM)
- [ ] Update README.md with new solver architecture
- [ ] Create ARCHITECTURE.md explaining system design
- [ ] Document algorithm selection criteria
- [ ] Add inline comments for complex logic
- [ ] Create visual diagrams of solver flow

---

## Open Questions

1. **Performance vs Optimality Trade-off:**
   - Is optimal solution quality worth potential performance cost for n=9?
   - Should we offer user-configurable algorithm selection?

2. **Experimental Validity:**
   - Do we need identical algorithms across all disk counts for fair comparison?
   - Or is it acceptable to use different algorithms if they produce similar quality results?

3. **Timeout Handling:**
   - What should happen if A* search times out for heavily perturbed n=9 states?
   - Fallback to greedy? Report as unsolvable?

4. **Handler Move Counting:**
   - Should handler moves count toward total move count?
   - How does this affect timeout thresholds?

---

## Conclusion

The current solver implementation is **functional and passes 98% of tests**. The main concerns are:

1. **Algorithmic inconsistency** (n ≤ 4 vs n > 4)
2. **Lack of optimality testing**
3. **Code organization** (handlers could be more modular)

The recommended path forward:

1. **Implement A* solver** to replace hybrid BFS/greedy approach
2. **Add optimality testing** to verify solution quality
3. **Refactor handlers** to class-based architecture
4. **Improve documentation** for maintainability

These changes will make the system more theoretically sound, experimentally valid, and maintainable going forward.

---

**Next Steps:** Review this document, prioritize action items, and decide on implementation schedule.
