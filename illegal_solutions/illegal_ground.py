"""
Tower of Hanoi - Illegal Ground State Solvers
Contains 2 strategies for handling ground disk violations:
1. Greedy: Place largest ground disk with minimum violation
2. Patient: Wait for legal move opportunity
"""

import sys
import os
from typing import List, Tuple, Optional

# Add the sibling directory to the path to import hanoi_state
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../state_solutions')))

from hanoi_state import Move

class GroundSolver:
    def __init__(self, state):
        """
        Initialize with the 5-array state: [A, B, C, Queue, Ground]
        """
        self.state = [list(p) for p in state]  # Deep copy
        self.moves = []
        
        # Define peg indices
        self.PEG_A = 0
        self.PEG_B = 1
        self.PEG_C = 2
        self.PEG_QUEUE = 3
        self.PEG_GROUND = 4
        
        self.peg_names = {0: 'A', 1: 'B', 2: 'C', 3: 'Queue', 4: 'Ground'}
    
    def _execute_physical_move(self, from_idx, to_idx):
        """
        Executes a move in the internal state and records the Move object.
        """
        if not self.state[from_idx]:
            raise ValueError(f"Cannot move from empty peg {self.peg_names[from_idx]}")
            
        disk = self.state[from_idx].pop()
        initial_height = len(self.state[from_idx])  # Height after pop
        
        self.state[to_idx].append(disk)
        destination_height = len(self.state[to_idx]) - 1  # Current top index
        
        move_obj = Move(
            disk=disk,
            initial_peg=self.peg_names[from_idx],
            initial_height=initial_height,
            destination_peg=self.peg_names[to_idx],
            destination_height=destination_height
        )
        self.moves.append(move_obj)
        return move_obj
    
    def has_ground_disks(self) -> bool:
        """Check if any disks are on the ground."""
        return len(self.state[self.PEG_GROUND]) > 0
    
    def get_largest_ground_disk(self) -> Optional[int]:
        """
        Returns the largest disk on the ground.
        Returns None if ground is empty.
        """
        if not self.state[self.PEG_GROUND]:
            return None
        return max(self.state[self.PEG_GROUND])
    
    def calculate_violation_score(self, disk: int, peg_idx: int) -> int:
        """
        Calculate violation score for placing a disk on a peg.
        Lower score = less violation.
        
        Score calculation:
        - If peg is empty: 0 (legal)
        - If top disk > disk: 0 (legal)
        - If top disk < disk: (disk - top_disk) (violation magnitude)
        """
        if peg_idx == self.PEG_QUEUE:
            return 0  # Queue accepts anything
        
        peg = self.state[peg_idx]
        if not peg:
            return 0  # Empty peg is legal
        
        top_disk = peg[-1]
        if top_disk > disk:
            return 0  # Legal placement
        
        # Violation: placing larger disk on smaller
        return disk - top_disk
    
    # ==========================================
    # Strategy 1: Greedy Placement
    # ==========================================
    def solve_greedy(self) -> Tuple[List[Move], List[List[int]]]:
        """
        Greedy strategy: Place largest ground disk on peg with minimum violation.
        Always prioritizes largest disk first.
        """
        
        while self.has_ground_disks():
            # Always pick the largest ground disk
            ground_disks = sorted(self.state[self.PEG_GROUND], reverse=True)
            largest_disk = ground_disks[0]
            
            # Find index of largest disk in ground list
            disk_index = self.state[self.PEG_GROUND].index(largest_disk)
            
            # Calculate violation scores for each standard peg
            best_peg = self.PEG_A
            best_score = float('inf')
            
            for peg_idx in [self.PEG_A, self.PEG_B, self.PEG_C]:
                score = self.calculate_violation_score(largest_disk, peg_idx)
                if score < best_score:
                    best_score = score
                    best_peg = peg_idx
            
            # Execute move: pick up largest disk from ground
            # (We need to temporarily move it to access it if it's not on top)
            temp_moves = []
            while self.state[self.PEG_GROUND][-1] != largest_disk:
                # Move top disk to queue temporarily
                temp_disk = self.state[self.PEG_GROUND].pop()
                temp_moves.append(temp_disk)
            
            # Now largest_disk is on top, move it
            self._execute_physical_move(self.PEG_GROUND, best_peg)
            
            # Restore temp disks back to ground
            for temp_disk in reversed(temp_moves):
                self.state[self.PEG_GROUND].append(temp_disk)
        
        return self.moves, self.state
    
    # ==========================================
    # Strategy 2: Patient Wait
    # ==========================================
    def solve_patient(self) -> Tuple[List[Move], List[List[int]]]:
        """
        Patient strategy: Only move ground disk when a legal placement exists.
        Returns None if no legal move is available (caller should handle stack operations).
        Always prioritizes largest disk first.
        """
        
        while self.has_ground_disks():
            # Always pick the largest ground disk
            ground_disks = sorted(self.state[self.PEG_GROUND], reverse=True)
            largest_disk = ground_disks[0]
            
            # Check if legal placement exists
            legal_move_found = False
            target_peg = None
            
            for peg_idx in [self.PEG_A, self.PEG_B, self.PEG_C]:
                score = self.calculate_violation_score(largest_disk, peg_idx)
                if score == 0:  # Legal placement
                    legal_move_found = True
                    target_peg = peg_idx
                    break
            
            if not legal_move_found:
                # No legal move available, return current state
                # Caller should proceed with stack operations
                break
            
            # Execute legal move
            temp_moves = []
            while self.state[self.PEG_GROUND][-1] != largest_disk:
                temp_disk = self.state[self.PEG_GROUND].pop()
                temp_moves.append(temp_disk)
            
            self._execute_physical_move(self.PEG_GROUND, target_peg)
            
            # Restore temp disks
            for temp_disk in reversed(temp_moves):
                self.state[self.PEG_GROUND].append(temp_disk)
        
        return self.moves, self.state
    
    def get_next_ground_move(self, strategy: str = 'greedy') -> Optional[Tuple[int, int]]:
        """
        Returns the next ground move as (from_idx, to_idx) without executing it.
        Returns None if no move is available or no ground disks exist.
        
        Args:
            strategy: 'greedy' or 'patient'
        """
        if not self.has_ground_disks():
            return None
        
        # Always pick the largest ground disk
        largest_disk = self.get_largest_ground_disk()
        
        if strategy == 'greedy':
            # Find peg with minimum violation
            best_peg = self.PEG_A
            best_score = float('inf')
            
            for peg_idx in [self.PEG_A, self.PEG_B, self.PEG_C]:
                score = self.calculate_violation_score(largest_disk, peg_idx)
                if score < best_score:
                    best_score = score
                    best_peg = peg_idx
            
            return (self.PEG_GROUND, best_peg)
        
        elif strategy == 'patient':
            # Find legal placement
            for peg_idx in [self.PEG_A, self.PEG_B, self.PEG_C]:
                score = self.calculate_violation_score(largest_disk, peg_idx)
                if score == 0:  # Legal placement
                    return (self.PEG_GROUND, peg_idx)
            
            # No legal move available
            return None
        
        return None


# --- Wrapper Functions ---

def solve_ground_greedy(state):
    """Solve ground violations using greedy strategy."""
    solver = GroundSolver(state)
    return solver.solve_greedy()

def solve_ground_patient(state):
    """Solve ground violations using patient strategy."""
    solver = GroundSolver(state)
    return solver.solve_patient()


if __name__ == "__main__":
    # Test Case 1: Multiple ground disks
    print("\n" + "="*50)
    print("TEST 1: Greedy Strategy - Multiple Ground Disks")
    state1 = [
        [5, 3],  # Peg A
        [4],     # Peg B
        [],      # Peg C
        [],      # Queue
        [2, 1]   # Ground (2 and 1 on ground)
    ]
    moves, final = solve_ground_greedy(state1)
    print(f"Moves: {len(moves)}")
    print(f"Final State: {final}")
    print(f"Ground Empty: {len(final[4]) == 0}")
    
    # Test Case 2: Patient strategy with no legal moves initially
    print("\n" + "="*50)
    print("TEST 2: Patient Strategy - Waiting for Legal Move")
    state2 = [
        [3, 2, 1],  # Peg A (all small disks)
        [],         # Peg B
        [],         # Peg C
        [],         # Queue
        [5]         # Ground (largest disk)
    ]
    moves, final = solve_ground_patient(state2)
    print(f"Moves: {len(moves)}")
    print(f"Final State: {final}")
    print(f"Ground Empty: {len(final[4]) == 0}")
    
    # Test Case 3: Greedy with varying violations
    print("\n" + "="*50)
    print("TEST 3: Greedy - Minimum Violation Selection")
    state3 = [
        [5, 4],  # Peg A (top = 4)
        [3],     # Peg B (top = 3)
        [2],     # Peg C (top = 2)
        [],      # Queue
        [1]      # Ground (disk 1, legal on any peg)
    ]
    moves, final = solve_ground_greedy(state3)
    print(f"Moves: {len(moves)}")
    print(f"Final State: {final}")
    for move in moves:
        print(f"  {move}")
