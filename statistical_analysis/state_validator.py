"""
State Validator for Tower of Hanoi Experiments
Validates state transitions and solution correctness during experimentation.
"""

import sys
import os
from typing import List, Tuple, Optional

# Add parent directories to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../illegal_solutions')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../state_solutions')))

from illegal_check import check_legality


class StateValidator:
    """
    Validates Tower of Hanoi states during experimental trials.
    Tracks expected vs actual states after each move.
    """
    
    def __init__(self):
        self.PEG_A = 0
        self.PEG_B = 1
        self.PEG_C = 2
        self.PEG_QUEUE = 3
        self.PEG_GROUND = 4
    
    def copy_state(self, state: List[List[int]]) -> List[List[int]]:
        """Deep copy a state."""
        return [list(peg) for peg in state]
    
    def states_match(self, state1: List[List[int]], state2: List[List[int]]) -> bool:
        """
        Check if two states are identical.
        """
        if len(state1) != len(state2):
            return False
        
        for i in range(len(state1)):
            if state1[i] != state2[i]:
                return False
        
        return True
    
    def is_solved(self, state: List[List[int]]) -> bool:
        """
        Check if state is fully solved:
        - All disks on Peg C
        - In legal descending order
        - No disks on other pegs (including Queue and Ground)
        """
        # Check no disks on A, B, Queue, Ground
        if any(len(state[i]) > 0 for i in [self.PEG_A, self.PEG_B, self.PEG_QUEUE, self.PEG_GROUND]):
            return False
        
        peg_c = state[self.PEG_C]
        
        # Check at least one disk on C
        if len(peg_c) == 0:
            return False
        
        # Check descending order (bottom to top: large to small)
        for i in range(len(peg_c) - 1):
            if peg_c[i] <= peg_c[i + 1]:  # Should be strictly decreasing
                return False
        
        return True
    
    def is_legal(self, state: List[List[int]]) -> bool:
        """
        Check if state is legal (no violations).
        """
        return check_legality(state)
    
    def count_disks(self, state: List[List[int]]) -> int:
        """
        Count total number of disks in the state.
        """
        return sum(len(peg) for peg in state)
    
    def get_all_disk_sizes(self, state: List[List[int]]) -> List[int]:
        """
        Get list of all disk sizes in the state.
        """
        disks = []
        for peg in state:
            disks.extend(peg)
        return sorted(disks)
    
    def validate_disk_conservation(self, state: List[List[int]], expected_disks: List[int]) -> Tuple[bool, str]:
        """
        Validate that the correct set of disks exists in the state.
        Returns (is_valid, error_message)
        """
        actual_disks = self.get_all_disk_sizes(state)
        expected_sorted = sorted(expected_disks)
        
        if actual_disks != expected_sorted:
            return False, f"Disk mismatch: expected {expected_sorted}, got {actual_disks}"
        
        return True, ""
    
    def simulate_move(self, state: List[List[int]], move) -> List[List[int]]:
        """
        Simulate a move on a copy of the state and return the resulting state.
        Move object has: disk, initial_peg, destination_peg
        """
        new_state = self.copy_state(state)
        
        # Map peg names to indices
        peg_map = {'A': 0, 'B': 1, 'C': 2, 'Queue': 3, 'Ground': 4}
        from_idx = peg_map[move.initial_peg]
        to_idx = peg_map[move.destination_peg]
        
        # Validate move
        if not new_state[from_idx]:
            raise ValueError(f"Invalid move: Cannot move from empty peg {move.initial_peg}")
        
        disk = new_state[from_idx][-1]
        if disk != move.disk:
            raise ValueError(f"Invalid move: Expected disk {move.disk} on top of {move.initial_peg}, found {disk}")
        
        # Execute move
        new_state[from_idx].pop()
        new_state[to_idx].append(disk)
        
        return new_state
    
    def validate_move_sequence(self, initial_state: List[List[int]], moves: List) -> Tuple[bool, List[List[int]], str]:
        """
        Validate a sequence of moves from an initial state.
        Returns (is_valid, final_state, error_message)
        """
        current_state = self.copy_state(initial_state)
        
        for i, move in enumerate(moves):
            try:
                current_state = self.simulate_move(current_state, move)
            except Exception as e:
                return False, current_state, f"Move {i+1} failed: {str(e)}"
        
        return True, current_state, ""
    
    def get_state_summary(self, state: List[List[int]]) -> str:
        """
        Get a human-readable summary of the state.
        """
        peg_names = ['A', 'B', 'C', 'Queue', 'Ground']
        summary = []
        for i, peg_name in enumerate(peg_names):
            if state[i]:
                summary.append(f"{peg_name}: {state[i]}")
            else:
                summary.append(f"{peg_name}: []")
        return " | ".join(summary)
    
    def validate_bfs_solution(self, initial_state: List[List[int]], moves: List, final_state: List[List[int]]) -> Tuple[bool, str]:
        """
        Validates a BFS solution for illegal state correction.
        BFS should find the SHORTEST path to ANY legal state.
        Returns (is_valid, diagnostic_message)
        """
        diagnostics = []
        
        # 1. Check if initial state was actually illegal
        if self.is_legal(initial_state):
            diagnostics.append("WARNING: Initial state was already legal")
        
        # 2. Validate move sequence
        valid_seq, computed_final, error = self.validate_move_sequence(initial_state, moves)
        if not valid_seq:
            return False, f"Invalid move sequence: {error}"
        
        # 3. Check final state matches computed state
        if not self.states_match(computed_final, final_state):
            return False, f"Final state mismatch"
        
        # 4. CRITICAL: Check if final state is legal
        if not self.is_legal(final_state):
            return False, "FAILED: Final state is still illegal"
        
        # 5. Check no disks in forbidden zones (Ground must be empty)
        if final_state[self.PEG_GROUND]:
            return False, f"FAILED: Ground still has disks: {final_state[self.PEG_GROUND]}"
        
        # Queue may still have disks (that's ok as long as state is legal)
        if final_state[self.PEG_QUEUE]:
            diagnostics.append(f"INFO: Queue has disks: {final_state[self.PEG_QUEUE]}")
        
        # 6. Disk conservation
        initial_disks = self.get_all_disk_sizes(initial_state)
        is_conserved, conservation_error = self.validate_disk_conservation(final_state, initial_disks)
        if not is_conserved:
            return False, conservation_error
        
        return True, " | ".join(diagnostics) if diagnostics else "Valid BFS solution (optimal path to legality)"
    
    def validate_digout_solution(self, initial_state: List[List[int]], moves: List, final_state: List[List[int]]) -> Tuple[bool, str]:
        """
        Validates a Dig-Out solution for illegal state correction.
        Dig-Out is heuristic-based and may take more moves than BFS.
        Returns (is_valid, diagnostic_message)
        """
        diagnostics = []
        
        # 1. Check if initial state was actually illegal
        if self.is_legal(initial_state):
            diagnostics.append("WARNING: Initial state was already legal")
        
        # 2. Validate move sequence
        valid_seq, computed_final, error = self.validate_move_sequence(initial_state, moves)
        if not valid_seq:
            return False, f"Invalid move sequence: {error}"
        
        # 3. Check final state matches computed state
        if not self.states_match(computed_final, final_state):
            return False, f"Final state mismatch"
        
        # 4. CRITICAL: Check if final state is legal
        if not self.is_legal(final_state):
            return False, "FAILED: Final state is still illegal"
        
        # 5. Check no disks in forbidden zones
        if final_state[self.PEG_GROUND]:
            return False, f"FAILED: Ground still has disks: {final_state[self.PEG_GROUND]}"
        
        if final_state[self.PEG_QUEUE]:
            diagnostics.append(f"INFO: Queue has disks: {final_state[self.PEG_QUEUE]}")
        
        # 6. Disk conservation
        initial_disks = self.get_all_disk_sizes(initial_state)
        is_conserved, conservation_error = self.validate_disk_conservation(final_state, initial_disks)
        if not is_conserved:
            return False, conservation_error
        
        # 7. Dig-Out specific: may use more moves than optimal
        diagnostics.append(f"Dig-Out used {len(moves)} moves (may not be optimal)")
        
        return True, " | ".join(diagnostics) if diagnostics else "Valid Dig-Out solution"


if __name__ == "__main__":
    # Test the validator
    print("="*60)
    print("State Validator Test Suite")
    print("="*60)
    
    validator = StateValidator()
    
    # Test 1: is_solved
    print("\nTest 1: is_solved()")
    solved_state = [[], [], [5, 4, 3, 2, 1], [], []]
    print(f"  State: {solved_state}")
    print(f"  Is solved: {validator.is_solved(solved_state)}")
    
    unsolved_state = [[5], [], [4, 3, 2, 1], [], []]
    print(f"  State: {unsolved_state}")
    print(f"  Is solved: {validator.is_solved(unsolved_state)}")
    
    # Test 2: is_legal
    print("\nTest 2: is_legal()")
    legal_state = [[5, 4], [3, 2], [1], [], []]
    print(f"  State: {legal_state}")
    print(f"  Is legal: {validator.is_legal(legal_state)}")
    
    illegal_state = [[3, 4], [2], [1], [], []]  # 4 on top of 3
    print(f"  State: {illegal_state}")
    print(f"  Is legal: {validator.is_legal(illegal_state)}")
    
    # Test 3: count_disks
    print("\nTest 3: count_disks()")
    state = [[5, 4, 3], [2], [1], [], []]
    print(f"  State: {state}")
    print(f"  Disk count: {validator.count_disks(state)}")
    
    # Test 4: get_state_summary
    print("\nTest 4: get_state_summary()")
    state = [[5, 4], [3], [2, 1], [], []]
    print(f"  State: {state}")
    print(f"  Summary: {validator.get_state_summary(state)}")
    
    # Test 5: states_match
    print("\nTest 5: states_match()")
    state1 = [[5, 4], [3], [2, 1], [], []]
    state2 = [[5, 4], [3], [2, 1], [], []]
    state3 = [[5, 4], [3], [1, 2], [], []]
    print(f"  State1 == State2: {validator.states_match(state1, state2)}")
    print(f"  State1 == State3: {validator.states_match(state1, state3)}")
