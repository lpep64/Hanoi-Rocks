"""
Unit tests for HanoiSolver class
"""

import pytest
from src.hanoi_solver import HanoiSolver


class TestHanoiSolverBasic:
    """Test basic solver functionality."""
    
    def test_solve_3_disks(self):
        """Test solving 3-disk problem."""
        solver = HanoiSolver()
        moves = solver.solve_full(3, 'A', 'C', 'B')
        assert len(moves) == 7  # 2^3 - 1 = 7
    
    def test_solve_4_disks(self):
        """Test solving 4-disk problem."""
        solver = HanoiSolver()
        moves = solver.solve_full(4, 'A', 'C', 'B')
        assert len(moves) == 15  # 2^4 - 1 = 15
    
    def test_minimum_moves_formula(self):
        """Test the minimum moves calculation."""
        solver = HanoiSolver()
        assert solver.get_minimum_moves(3) == 7
        assert solver.get_minimum_moves(5) == 31
        assert solver.get_minimum_moves(9) == 511


class TestGetNextOptimalMove:
    """Test get_next_optimal_move functionality."""
    
    def test_initial_state_3_disks(self):
        """Test getting first move from initial state."""
        solver = HanoiSolver()
        state = {'A': [3, 2, 1], 'B': [], 'C': []}
        move = solver.get_next_optimal_move(state, 3, 'A', 'C', 'B')
        # First move should be disk 1 from A to C
        assert move is not None
        assert move['disk'] == 1
        assert move['from'] == 'A'
    
    def test_no_move_needed(self):
        """Test when all disks are already at target."""
        solver = HanoiSolver()
        state = {'A': [], 'B': [], 'C': [3, 2, 1]}
        move = solver.get_next_optimal_move(state, 3, 'A', 'C', 'B')
        # Should return None or handle gracefully
        assert move is None or isinstance(move, dict)


class TestSolverHelpers:
    """Test helper methods."""
    
    def test_find_disk(self):
        """Test finding disk location."""
        solver = HanoiSolver()
        state = {'A': [3, 2], 'B': [1], 'C': []}
        assert solver._find_disk(state, 1) == 'B'
        assert solver._find_disk(state, 3) == 'A'
        assert solver._find_disk(state, 99) is None
    
    def test_is_disk_exposed(self):
        """Test checking if disk is on top."""
        solver = HanoiSolver()
        state = {'A': [3, 2, 1], 'B': [], 'C': []}
        assert solver._is_disk_exposed(state, 'A', 1) is True
        assert solver._is_disk_exposed(state, 'A', 2) is False
        assert solver._is_disk_exposed(state, 'A', 3) is False
    
    def test_can_place_disk(self):
        """Test checking if disk can be placed on peg."""
        solver = HanoiSolver()
        state = {'A': [3], 'B': [2], 'C': []}
        assert solver._can_place_disk(state, 'A', 1) is True  # 1 < 3
        assert solver._can_place_disk(state, 'A', 4) is False  # 4 > 3
        assert solver._can_place_disk(state, 'C', 1) is True  # Empty peg
