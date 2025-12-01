"""
Comparison Tests: BFS vs Dig-Out for Illegal State Correction
Tests which strategy finds legality faster and with fewer moves.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../illegal_solutions')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../statistical_analysis')))

import pytest
from illegal_stack import solve_illegal_dig_out, solve_illegal_a_star
from illegal_check import check_legality
from state_validator import StateValidator


class TestBFSvsDigOut:
    """Compare BFS (optimal) vs Dig-Out (heuristic) performance."""
    
    def setup_method(self):
        """Setup validator for each test."""
        self.validator = StateValidator()
    
    def test_01_simple_violation_comparison(self):
        """Compare both strategies on simple stacking violation."""
        state = [[3, 4], [2], [1], [], []]  # 4 on 3 is illegal
        
        # Dig-Out
        moves_digout, final_digout = solve_illegal_dig_out([list(p) for p in state])
        assert check_legality(final_digout), "Dig-Out must achieve legality"
        
        # BFS
        moves_bfs, final_bfs = solve_illegal_a_star([list(p) for p in state])
        assert check_legality(final_bfs), "BFS must achieve legality"
        
        print(f"\n  Dig-Out: {len(moves_digout)} moves")
        print(f"  BFS:     {len(moves_bfs)} moves (optimal)")
        
        # BFS should be optimal (<=)
        assert len(moves_bfs) <= len(moves_digout), "BFS should find optimal or equal path"
    
    def test_02_complex_violation_comparison(self):
        """Compare on complex multi-violation state."""
        state = [[4, 3, 5], [2], [1], [], []]  # Multiple violations
        
        moves_digout, final_digout = solve_illegal_dig_out([list(p) for p in state])
        moves_bfs, final_bfs = solve_illegal_a_star([list(p) for p in state])
        
        assert check_legality(final_digout), "Dig-Out must achieve legality"
        assert check_legality(final_bfs), "BFS must achieve legality"
        
        print(f"\n  Dig-Out: {len(moves_digout)} moves")
        print(f"  BFS:     {len(moves_bfs)} moves (optimal)")
        
        assert len(moves_bfs) <= len(moves_digout), "BFS should be optimal"
    
    def test_03_ground_disks_comparison(self):
        """Compare when disks start on Ground."""
        state = [[3], [2], [1], [], [5, 4]]  # Disks on Ground
        
        moves_digout, final_digout = solve_illegal_dig_out([list(p) for p in state])
        moves_bfs, final_bfs = solve_illegal_a_star([list(p) for p in state])
        
        assert check_legality(final_digout), "Dig-Out must achieve legality"
        assert check_legality(final_bfs), "BFS must achieve legality"
        assert len(final_digout[4]) == 0, "Dig-Out must clear Ground"
        assert len(final_bfs[4]) == 0, "BFS must clear Ground"
        
        print(f"\n  Dig-Out: {len(moves_digout)} moves")
        print(f"  BFS:     {len(moves_bfs)} moves (optimal)")
        
        assert len(moves_bfs) <= len(moves_digout), "BFS should be optimal"
    
    def test_04_worst_case_comparison(self):
        """Compare on worst-case scenario (many violations)."""
        state = [[5, 4, 3, 2, 1], [], [], [], []]  # Inverted tower
        
        moves_digout, final_digout = solve_illegal_dig_out([list(p) for p in state])
        moves_bfs, final_bfs = solve_illegal_a_star([list(p) for p in state])
        
        assert check_legality(final_digout), "Dig-Out must achieve legality"
        assert check_legality(final_bfs), "BFS must achieve legality"
        
        print(f"\n  Dig-Out: {len(moves_digout)} moves")
        print(f"  BFS:     {len(moves_bfs)} moves (optimal)")
        
        assert len(moves_bfs) <= len(moves_digout), "BFS should be optimal"
    
    def test_05_efficiency_ratio(self):
        """Calculate efficiency ratio: BFS moves / Dig-Out moves."""
        test_cases = [
            [[3, 4], [2], [1], [], []],
            [[4, 3, 5], [2], [1], [], []],
            [[5, 4, 3, 2, 1], [], [], [], []],
            [[3], [2], [1], [], [5, 4]],
        ]
        
        ratios = []
        for state in test_cases:
            moves_digout, _ = solve_illegal_dig_out([list(p) for p in state])
            moves_bfs, _ = solve_illegal_a_star([list(p) for p in state])
            
            ratio = len(moves_bfs) / len(moves_digout) if len(moves_digout) > 0 else 1.0
            ratios.append(ratio)
            print(f"  State: {state[0][:3]} - Ratio: {ratio:.2f} (BFS/Dig-Out)")
        
        avg_ratio = sum(ratios) / len(ratios)
        print(f"\n  Average efficiency ratio: {avg_ratio:.2f}")
        print(f"  (1.0 = equal, <1.0 = BFS is better)")
    
    def test_06_validate_bfs_with_validator(self):
        """Test BFS validation method."""
        initial_state = [[3, 4], [2], [1], [], []]
        moves, final_state = solve_illegal_a_star([list(p) for p in initial_state])
        
        is_valid, message = self.validator.validate_bfs_solution(initial_state, moves, final_state)
        assert is_valid, f"BFS solution should be valid: {message}"
        print(f"\n  Validation message: {message}")
    
    def test_07_validate_digout_with_validator(self):
        """Test Dig-Out validation method."""
        initial_state = [[3, 4], [2], [1], [], []]
        moves, final_state = solve_illegal_dig_out([list(p) for p in initial_state])
        
        is_valid, message = self.validator.validate_digout_solution(initial_state, moves, final_state)
        assert is_valid, f"Dig-Out solution should be valid: {message}"
        print(f"\n  Validation message: {message}")
    
    def test_08_queue_disk_handling(self):
        """Test that both methods can handle disks in Queue."""
        state = [[3, 4], [2], [], [5, 1], []]  # Violations on A and Queue
        
        moves_digout, final_digout = solve_illegal_dig_out([list(p) for p in state])
        moves_bfs, final_bfs = solve_illegal_a_star([list(p) for p in state])
        
        assert check_legality(final_digout), "Dig-Out must achieve legality"
        assert check_legality(final_bfs), "BFS must achieve legality"
        
        print(f"\n  Dig-Out: {len(moves_digout)} moves, Queue: {final_digout[3]}")
        print(f"  BFS:     {len(moves_bfs)} moves, Queue: {final_bfs[3]}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
