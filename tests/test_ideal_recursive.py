"""
Test the ideal recursive solver concept from ideal.py

This test explores what goes wrong when trying to use pure recursive
Hanoi algorithm with state checking and regeneration.
"""

import pytest
from src.environment import Environment
from src.hanoi_solver import HanoiSolver
import src.illegal_state_handlers as Handlers


class RecursiveSolverWithStateChecking:
    """
    Implementation of ideal.py concept: recursive solver with state validation.
    
    The idea is to use pure recursive algorithm but check state at each step.
    """
    
    def __init__(self, env, n, source='A', target='C', auxiliary='B'):
        self.env = env
        self.n = n
        self.source = source
        self.target = target
        self.auxiliary = auxiliary
        self.moves_made = 0
        self.max_moves = ((2 ** n) - 1) * 50  # Safety limit
        self.expected_state = None
        self.move_log = []
        
        # Handler strategies (hardcoded for testing)
        self.ground_handler = 'best-fit'
        self.formation_handler = 'bubble'
    
    def is_state_legal(self):
        """Check if current state is legal."""
        illegal_type, details = self.env.check_for_illegal_states()
        return illegal_type == "Legal"
    
    def is_state_expected(self):
        """Check if current state matches what we expected."""
        if self.expected_state is None:
            return True  # First move, no expectation yet
        
        current = self.env.get_state()
        return (current['A'] == self.expected_state['A'] and
                current['B'] == self.expected_state['B'] and
                current['C'] == self.expected_state['C'])
    
    def resolve_illegal_state(self):
        """Resolve any illegal states."""
        illegal_type, details = self.env.check_for_illegal_states()
        
        if illegal_type == "ElementOnGround":
            if self.ground_handler == 'best-fit':
                moves = Handlers.resolve_ground_best_fit(self.env, details)
            else:
                moves = Handlers.resolve_ground_first_available(self.env, details)
            self.moves_made += moves
            self.move_log.append(f"Resolved ground: {moves} moves")
        
        elif illegal_type == "IllegalFormation":
            if self.formation_handler == 'bubble':
                moves = Handlers.resolve_formation_bubble(self.env, details)
            elif self.formation_handler == 'deepest':
                moves = Handlers.resolve_formation_deepest(self.env, details)
            else:
                moves = Handlers.resolve_formation_buffer(self.env, details)
            self.moves_made += moves
            self.move_log.append(f"Resolved formation: {moves} moves")
        
        elif illegal_type == "DuplicateItem":
            moves = Handlers.resolve_duplicates_discard(self.env, details)
            self.moves_made += moves
            self.move_log.append(f"Resolved duplicate: {moves} moves")
    
    def move_disks(self, n, src, des, aux):
        """
        Recursive Tower of Hanoi with state checking.
        
        This is the implementation of the ideal.py concept.
        """
        # Check for timeout
        if self.moves_made >= self.max_moves:
            raise Exception(f"Timeout: exceeded {self.max_moves} moves")
        
        # Base case
        if n <= 0:
            return
        
        # Check state before proceeding
        if self.is_state_legal() and self.is_state_expected():
            # State is good - proceed with algorithm
            
            if n == 1:
                # Move the disk
                success, reason = self.env.apply_move(src, des)
                if success:
                    self.moves_made += 1
                    self.expected_state = self.env.get_state()
                    self.move_log.append(f"[{self.moves_made}] Move disk 1 from {src} to {des}")
                else:
                    raise Exception(f"Move failed: {reason}")
                return
            
            # Recursive case: move n-1 disks from src to aux
            self.move_disks(n - 1, src, aux, des)
            
            # Move disk n from src to des
            success, reason = self.env.apply_move(src, des)
            if success:
                self.moves_made += 1
                self.expected_state = self.env.get_state()
                self.move_log.append(f"[{self.moves_made}] Move disk {n} from {src} to {des}")
            else:
                raise Exception(f"Move failed: {reason}")
            
            # Move n-1 disks from aux to des
            self.move_disks(n - 1, aux, des, src)
        
        elif self.is_state_legal() and not self.is_state_expected():
            # State is legal but altered - need to regenerate solution
            self.move_log.append(f"[{self.moves_made}] State altered - REGENERATION NEEDED")
            
            # THIS IS WHERE IT BREAKS: How do we regenerate?
            # Problem 1: We're deep in recursion - can't easily restart
            # Problem 2: The recursive algorithm assumes clean sequential execution
            # Problem 3: We don't know which disks are where without analyzing state
            
            raise Exception("Cannot regenerate solution from within recursive call")
        
        else:
            # Illegal state - resolve it
            self.move_log.append(f"[{self.moves_made}] Illegal state detected")
            self.resolve_illegal_state()
            
            # After resolution, try again
            # THIS IS ALSO PROBLEMATIC: We're recursing again after fixing state
            self.move_disks(n, src, des, aux)
    
    def solve(self):
        """Run the solver."""
        try:
            self.expected_state = self.env.get_state()
            self.move_disks(self.n, self.source, self.target, self.auxiliary)
            return {
                'success': True,
                'moves': self.moves_made,
                'log': self.move_log
            }
        except Exception as e:
            return {
                'success': False,
                'moves': self.moves_made,
                'error': str(e),
                'log': self.move_log
            }


class TestIdealRecursiveConcept:
    """Tests to explore what goes wrong with ideal.py approach."""
    
    def test_clean_state_no_alterations(self):
        """Test 1: Does it work for clean state with no alterations?"""
        env = Environment(3)
        solver = RecursiveSolverWithStateChecking(env, 3)
        result = solver.solve()
        
        assert result['success'] is True
        assert result['moves'] == 7  # 2^3 - 1
        print(f"\n✓ Clean state works: {result['moves']} moves")
    
    def test_altered_state_during_execution(self):
        """Test 2: What happens when state is altered mid-execution?"""
        env = Environment(3)
        solver = RecursiveSolverWithStateChecking(env, 3)
        
        # Make a few moves manually first to simulate mid-execution
        env.apply_move('A', 'C')  # Disk 1 to C
        env.apply_move('A', 'B')  # Disk 2 to B
        
        # Now try to solve from this altered state
        result = solver.solve()
        
        # This WILL fail because recursive algorithm assumes starting position
        assert result['success'] is False
        assert 'Cannot regenerate' in result['error'] or 'Move failed' in result['error']
        print(f"\n✗ Altered state fails: {result['error']}")
        print(f"  Moves before failure: {result['moves']}")
    
    def test_illegal_state_on_ground(self):
        """Test 3: What happens with disk on ground?"""
        env = Environment(3)
        
        # Create illegal state: put disk 1 on ground
        env.pegs['A'].remove(1)
        env.ground.append(1)
        
        solver = RecursiveSolverWithStateChecking(env, 3)
        result = solver.solve()
        
        # Should resolve ground issue and continue
        # But will likely fail because state doesn't match recursive assumptions
        print(f"\n{'✓' if result['success'] else '✗'} Ground state: {result.get('error', 'Resolved')}")
        print(f"  Moves: {result['moves']}")
        print(f"  Log sample: {result['log'][:5]}")
    
    def test_illegal_formation(self):
        """Test 4: What happens with illegal formation?"""
        env = Environment(3)
        
        # Create illegal formation: put disk 2 on top of disk 1
        env.pegs['A'] = [3]
        env.pegs['B'] = [1, 2]  # Illegal!
        env.pegs['C'] = []
        
        solver = RecursiveSolverWithStateChecking(env, 3)
        result = solver.solve()
        
        print(f"\n{'✓' if result['success'] else '✗'} Formation state: {result.get('error', 'Resolved')}")
        print(f"  Moves: {result['moves']}")
    
    def test_with_environment_alterations(self):
        """Test 5: Simulate alterations happening during execution."""
        env = Environment(3)
        solver = RecursiveSolverWithStateChecking(env, 3)
        
        # Monkey-patch to introduce alteration after 3 moves
        original_apply = env.apply_move
        move_count = [0]
        
        def apply_with_alteration(from_peg, to_peg):
            result = original_apply(from_peg, to_peg)
            move_count[0] += 1
            
            # Introduce alteration after 3rd move
            if move_count[0] == 3:
                # Move disk 1 to a different peg
                if env.pegs['C'] and env.pegs['C'][-1] == 1:
                    env.pegs['C'].remove(1)
                    env.pegs['A'].append(1)
                    solver.move_log.append(f"[ALTERATION] Moved disk 1 unexpectedly")
            
            return result
        
        env.apply_move = apply_with_alteration
        result = solver.solve()
        
        print(f"\n{'✓' if result['success'] else '✗'} With alterations: {result.get('error', 'Completed')}")
        print(f"  Moves: {result['moves']}")
        print(f"  Log sample: {result['log'][-5:]}")


class TestWhereItBreaks:
    """Detailed analysis of exactly where and why it breaks."""
    
    def test_problem_1_recursive_depth(self):
        """
        PROBLEM 1: Cannot regenerate from within recursive call.
        
        When state is altered mid-recursion, we're deep in the call stack.
        The recursive algorithm encoded in the call stack assumes the original
        starting position (all disks on source peg).
        
        We can't "restart" the recursion from current state without unwinding
        the entire call stack and losing track of where we were.
        """
        print("\n=== PROBLEM 1: Recursive Depth ===")
        print("The recursive call stack encodes assumptions about disk positions.")
        print("Example: When we call move_disks(2, 'A', 'B', 'C'), the algorithm assumes:")
        print("  - Disk 2 is on peg A")
        print("  - Disk 1 is on top of disk 2 on peg A")
        print("\nIf an alteration moves disk 1 to peg C, the recursive algorithm doesn't know!")
        print("It will still try to execute: move_disks(1, 'A', 'C', 'B')")
        print("But disk 1 is NOT on A anymore - the move will fail.\n")
        
        # Demonstrate
        env = Environment(3)
        
        # Manually simulate what recursion expects
        print("Expected by recursion at depth 2:")
        print(f"  State: A=[3,2,1], B=[], C=[]")
        print(f"  Next call: move_disks(1, 'A', 'C', 'B') - move disk 1 from A to C")
        
        # But alteration changed it
        env.pegs['A'] = [3, 2]
        env.pegs['B'] = []
        env.pegs['C'] = [1]  # Disk 1 was moved by alteration
        
        print("\nActual state after alteration:")
        print(f"  State: A=[3,2], B=[], C=[1]")
        print(f"  Next call: move_disks(1, 'A', 'C', 'B') - but disk 1 is NOT on A!")
        print(f"  Result: Move fails!\n")
    
    def test_problem_2_parameter_assumptions(self):
        """
        PROBLEM 2: Recursive parameters (src, des, aux) encode expectations.
        
        When we call move_disks(n, 'A', 'C', 'B'), we're saying:
        "Move n disks from A to C using B as auxiliary"
        
        This assumes the top n disks are currently on peg A.
        If alteration moved them, the parameters are now wrong.
        """
        print("\n=== PROBLEM 2: Parameter Assumptions ===")
        print("Recursive parameters encode WHERE disks should be.")
        print("Example: move_disks(3, 'A', 'C', 'B') assumes:")
        print("  - Top 3 disks are on peg A")
        print("  - We want to move them to peg C")
        print("  - We'll use peg B as auxiliary")
        
        print("\nIf alteration moves disk 1 from A to B, parameters become invalid.")
        print("The algorithm still thinks all disks are on A!")
        print("We'd need to call move_disks(3, ???, 'C', ???) - but what are the params?")
        print("Disk 3 is on A, disk 2 is on A, disk 1 is on B - no single source peg!\n")
    
    def test_problem_3_cannot_analyze_state(self):
        """
        PROBLEM 3: Pure recursive algorithm doesn't analyze current state.
        
        Classic recursive Hanoi generates moves based purely on:
        - Number of disks (n)
        - Source, target, auxiliary pegs
        
        It does NOT look at actual disk positions. It assumes positions
        based on the move sequence so far.
        """
        print("\n=== PROBLEM 3: No State Analysis ===")
        print("Pure recursive algorithm is 'blind' to actual disk positions.")
        print("It generates moves based on mathematical pattern, not observation.")
        
        print("\nClassic algorithm logic:")
        print("  if n == 1: move from src to des")
        print("  else:")
        print("    move n-1 disks from src to aux")
        print("    move disk n from src to des")
        print("    move n-1 disks from aux to des")
        
        print("\nNotice: It never checks WHERE disks actually are!")
        print("It assumes they're where previous moves should have put them.")
        print("\nWhen alteration breaks this assumption, algorithm is lost.\n")
    
    def test_solution_iterative_approach(self):
        """
        SOLUTION: This is why we use iterative approach with state checking.
        
        Instead of pure recursion, we:
        1. Generate full solution sequence upfront
        2. Execute moves one at a time
        3. Check state after each move
        4. If state altered, regenerate solution from CURRENT state
        5. Continue execution
        """
        print("\n=== SOLUTION: Iterative with Regeneration ===")
        print("Our current solver (after fix) does this:")
        print("1. Generate solution: [move1, move2, move3, ...]")
        print("2. Execute move1, check state")
        print("3. If state altered:")
        print("   a. Generate NEW solution from altered state")
        print("   b. Continue with new solution")
        print("4. Repeat until goal reached")
        
        print("\nThis works because:")
        print("- We're not deep in recursive call stack")
        print("- We can regenerate at any time")
        print("- Each regeneration uses CURRENT state as starting point")
        print("- No assumptions about where disks 'should' be\n")
        
        # Demonstrate with actual solver
        from src.hanoi_solver import HanoiSolver
        
        env = Environment(3)
        solver = HanoiSolver()
        
        print("Example with our solver:")
        # Make a few moves
        move1 = solver.get_next_optimal_move(env.get_state(), 3, 'A', 'C', 'B')
        env.apply_move(move1['from'], move1['to'])
        print(f"Move 1: {move1}")
        
        move2 = solver.get_next_optimal_move(env.get_state(), 3, 'A', 'C', 'B')
        env.apply_move(move2['from'], move2['to'])
        print(f"Move 2: {move2}")
        
        # Introduce alteration
        print("\n[ALTERATION] Moving disk 1 from C to A")
        if env.pegs['C'] and env.pegs['C'][-1] == 1:
            env.pegs['C'].remove(1)
            env.pegs['A'].append(1)
        
        # Solver regenerates automatically
        move3 = solver.get_next_optimal_move(env.get_state(), 3, 'A', 'C', 'B')
        print(f"Move 3 (after regeneration): {move3}")
        print("✓ Solver adapted to altered state!\n")


if __name__ == "__main__":
    print("=" * 70)
    print("TESTING IDEAL.PY CONCEPT")
    print("=" * 70)
    
    # Run the tests to see where it breaks
    pytest.main([__file__, '-v', '-s'])
