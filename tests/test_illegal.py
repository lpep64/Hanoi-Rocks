"""
Unit Tests for Tower of Hanoi Illegal State Logic
Tests:
1. illegal_check.py (Legality Logic)
2. illegal_stack.py (Solving Algorithms: Dig Out, Bubble Sort, Total Evacuation, A*)
"""

import unittest
import sys
import os

# --- Path Setup ---
current_dir = os.path.dirname(os.path.abspath(__file__))

# 1. Path for State Solutions (HanoiState, Move classes)
state_dir = os.path.abspath(os.path.join(current_dir, '../state_solutions'))
sys.path.append(state_dir)

# 2. Path for Illegal Solutions (User requested update)
source_dir = os.path.abspath(os.path.join(current_dir, '../illegal_solutions'))
sys.path.append(source_dir)

# --- Imports ---
try:
    from illegal_check import check_legality
    from illegal_stack import (
        solve_illegal_dig_out,
        solve_illegal_a_star  # Now implements BFS for optimal path to legality
    )
    # Note: bubble_sort and total_evacuation are not yet implemented
    solve_illegal_bubble_sort = None
    solve_illegal_total_evacuation = None
except ImportError as e:
    print("CRITICAL ERROR: Could not import source modules.")
    print(f"Checked paths:\n1. {state_dir}\n2. {source_dir}")
    print(f"Error details: {e}")
    sys.exit(1)


class TestLegalityChecker(unittest.TestCase):
    """Tests strictly for the check_legality function in illegal_check.py"""

    def test_01_standard_legal_state(self):
        # [3, 2, 1] means 3 is bottom, 1 is top. Valid.
        state = [[3, 2, 1], [], [], [], []]
        self.assertTrue(check_legality(state), "Standard start state should be legal")

    def test_02_legal_scattered_state(self):
        # Disks scattered but valid order on each peg
        state = [[3], [2], [1], [], []]
        self.assertTrue(check_legality(state), "Scattered valid state should be legal")

    def test_03_illegal_stack_order(self):
        # [1, 2] means 1 is bottom, 2 is top. 2 > 1. Illegal.
        state = [[1, 2], [], [], [], []]
        self.assertFalse(check_legality(state), "Larger disk on top of smaller should be illegal")

    def test_04_illegal_queue_presence(self):
        state = [[3, 2, 1], [], [], [4], []]
        self.assertFalse(check_legality(state), "Items in Queue peg should be illegal")

    def test_05_illegal_ground_presence(self):
        state = [[3, 2, 1], [], [], [], [5]]
        self.assertFalse(check_legality(state), "Items on Ground peg should be illegal")

    def test_06_complex_illegal_state(self):
        # Illegal stack AND illegal ground
        state = [[1, 2], [], [], [], [5]]
        self.assertFalse(check_legality(state), "Complex mixed errors should be illegal")
        
    def test_07_empty_state_is_legal(self):
        # Technically 0 disks is a legal configuration
        state = [[], [], [], [], []]
        self.assertTrue(check_legality(state), "Empty state should be legal")


class TestIllegalSolvers(unittest.TestCase):
    """
    Tests for the solver algorithms in illegal_stack.py.
    """

    def setUp(self):
        # Common Test States
        
        # 1. Simple Inversion
        self.stack_error_state = [[1, 2], [3], [], [], []]

        # 2. Zone Errors (Queue/Ground)
        self.zone_error_state = [[3], [2], [], [1], [4]]
        
        # 3. Multiple Inversions (Sandwich)
        # [1, 3, 2] -> 1 bottom, 3 middle, 2 top. (3>2 is error)
        self.sandwich_state = [[1, 3, 2], [], [], [], []]
        
        # 4. Pure Cleanup
        self.pure_ground_state = [[3, 2, 1], [], [], [], [4]]

    # --- DIG OUT TESTS ---
    def test_08_dig_out_basic(self):
        moves, final = solve_illegal_dig_out(self.stack_error_state)
        self.assertTrue(check_legality(final), "Dig Out: Basic Inversion")

    def test_09_dig_out_pure_ground(self):
        """Test if Dig Out cleans up ground items even if stack is perfect."""
        moves, final = solve_illegal_dig_out(self.pure_ground_state)
        self.assertTrue(check_legality(final), "Dig Out: Pure Ground Cleanup")
        self.assertFalse(final[4], "Ground should be empty")

    def test_10_dig_out_multiple_inversions(self):
        """Test if Dig Out can handle a stack with multiple issues iteratively."""
        # [1, 3, 2, 4] -> (3 on 1 ok), (2 on 3 BAD), (4 on 2 BAD)
        complex_stack = [[1, 3, 2, 4], [], [], [], []]
        moves, final = solve_illegal_dig_out(complex_stack)
        self.assertTrue(check_legality(final), "Dig Out: Multiple Inversions")

    # --- BUBBLE SORT TESTS ---
    def test_11_bubble_sort_basic(self):
        moves, final = solve_illegal_bubble_sort(self.stack_error_state)
        self.assertTrue(check_legality(final), "Bubble Sort: Basic Inversion")

    def test_12_bubble_sort_sandwich(self):
        """Test Bubble Sort on a 'sandwich' error [1, 3, 2]"""
        moves, final = solve_illegal_bubble_sort(self.sandwich_state)
        self.assertTrue(check_legality(final), "Bubble Sort: Sandwich Error")

    def test_13_bubble_sort_deep_stack(self):
        """Stress test Bubble Sort with a larger stack (N=5) with error at bottom."""
        # [5, 4, 1, 3, 2] -> 1 under 3 is fine, 3 under 2 is BAD.
        deep_state = [[5, 4, 1, 3, 2], [], [], [], []]
        moves, final = solve_illegal_bubble_sort(deep_state)
        self.assertTrue(check_legality(final), "Bubble Sort: Deep Stack")

    # --- TOTAL EVACUATION TESTS ---
    def test_14_total_evacuation_zones(self):
        moves, final = solve_illegal_total_evacuation(self.zone_error_state)
        self.assertTrue(check_legality(final))
        # Specific Goal: All on C
        self.assertTrue(len(final[2]) == 4, "Total Evac must put all disks on C")

    def test_15_total_evacuation_inverted_start(self):
        """Test Total Evac on a completely inverted tower [1, 2, 3] on A."""
        inverted = [[1, 2, 3], [], [], [], []]
        moves, final = solve_illegal_total_evacuation(inverted)
        self.assertTrue(check_legality(final))
        self.assertEqual(final[2], [3, 2, 1], "Total Evac must reverse the inversion to C")

    # --- BFS TESTS (formerly A*) ---
    def test_16_astar_small(self):
        # BFS finds optimal path to ANY legal state (not necessarily all on C)
        small_state = [[2, 3], [1], [], [], []]
        moves, final = solve_illegal_a_star(small_state)
        self.assertTrue(check_legality(final), "BFS: Small State must be legal")
        # BFS doesn't require all on C, just legality
        self.assertEqual(len(final[4]), 0, "Ground must be empty")
        self.assertEqual(len(final[3]), 0, "Queue must be empty")

    def test_17_astar_ground_penalty(self):
        """Test that A* prioritizes removing items from Ground."""
        # A simple valid move exists (A->C), but Ground needs moving.
        state = [[2], [1], [], [], [3]] 
        moves, final = solve_illegal_a_star(state)
        self.assertTrue(check_legality(final))
        self.assertFalse(final[4], "A* final state must clear ground")

    # --- GENERIC / ROBUSTNESS ---
    def test_18_no_op_legal_state(self):
        """Ensure solvers don't break legal states."""
        legal = [[3, 2, 1], [], [], [], []]
        moves, final = solve_illegal_dig_out(legal)
        self.assertEqual(len(moves), 0, "Dig Out should do 0 moves on legal state")
        self.assertEqual(final, legal)

    def test_19_single_disk_illegal_location(self):
        """Edge case: Single disk, but in wrong place."""
        state = [[], [], [], [1], []] # 1 in Queue
        moves, final = solve_illegal_dig_out(state)
        self.assertTrue(check_legality(final))
        self.assertFalse(final[3], "Queue should be empty")

    def test_20_all_solvers_consistency(self):
        """Run all implemented solvers on the same state and ensure all return valid results."""
        base = [[1, 2], [3], [], [], []] # Clone needed inside function or re-init
        
        # We must manually clone or re-define because solvers mutate the input object
        s1 = [list(p) for p in base]
        _, f1 = solve_illegal_dig_out(s1)
        self.assertTrue(check_legality(f1))

        s2 = [list(p) for p in base]
        _, f2 = solve_illegal_a_star(s2)  # BFS implementation
        self.assertTrue(check_legality(f2))
        
        # Note: bubble_sort and total_evacuation not yet implemented
        # s3 = [list(p) for p in base]
        # _, f3 = solve_illegal_total_evacuation(s3)
        # self.assertTrue(check_legality(f3))


if __name__ == '__main__':
    unittest.main()