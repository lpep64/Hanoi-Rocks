"""
Tower of Hanoi - Generalized Solver
Solves Tower of Hanoi from any arbitrary initial state configuration.
"""

from typing import List, Tuple, Dict, Optional

class Move:
    """
    Represents a single move in the Tower of Hanoi puzzle with complete state information.
    """
    def __init__(self, disk: int, initial_peg: str, initial_height: int, destination_peg: str, destination_height: int):
        self.disk = disk
        self.initial_peg = initial_peg
        self.initial_height = initial_height
        self.destination_peg = destination_peg
        self.destination_height = destination_height
    
    def __repr__(self):
        return (f"Move(disk={self.disk}, {self.initial_peg}[h={self.initial_height}] -> "
                f"{self.destination_peg}[h={self.destination_height}])")

class TowerState:
    """
    Tracks the current state of all three pegs in the Tower of Hanoi puzzle.
    Supports initialization from arbitrary initial configurations.
    """
    def __init__(self, initial_state: List[List[int]] = None, n: int = None, 
                 source='A', destination='C', auxiliary='B'):
        self.source = source
        self.destination = destination
        self.auxiliary = auxiliary
        self.peg_names = [source, auxiliary, destination]
        self.pegs = {}
        
        if initial_state is not None:
            # Validation
            if len(initial_state) != 3:
                raise ValueError("initial_state must contain exactly 3 lists")
            
            all_disks = []
            for p in initial_state:
                all_disks.extend(p)
                
            if not all_disks:
                 raise ValueError("initial_state must contain at least one disk")
            
            self.n = max(all_disks)
            
            # Validate that we have a permutation of 1..n
            if sorted(all_disks) != list(range(1, self.n + 1)):
                 raise ValueError(f"Disks must range from 1 to {self.n} without duplicates or gaps.")

            # Check Valid Hanoi State (smaller on top of larger)
            self.pegs = {
                source: list(initial_state[0]),
                auxiliary: list(initial_state[1]),
                destination: list(initial_state[2])
            }
            
            for name, stack in self.pegs.items():
                for i in range(len(stack) - 1):
                    if stack[i] <= stack[i+1]:
                        raise ValueError(f"Invalid stack on peg {name}: larger disk on top of smaller.")
        else:
            # Standard init
            self.n = n if n else 3
            self.pegs = {
                source: list(range(self.n, 0, -1)),
                auxiliary: [],
                destination: []
            }

    def find_disk_peg(self, disk_size: int) -> str:
        """Find which peg contains the specified disk."""
        for name, stack in self.pegs.items():
            if disk_size in stack:
                return name
        raise ValueError(f"Disk {disk_size} not found in any peg state.")

    def get_auxiliary(self, peg1: str, peg2: str) -> str:
        """Get the third peg that's not peg1 or peg2."""
        remaining = {self.source, self.destination, self.auxiliary} - {peg1, peg2}
        return list(remaining)[0]

    def can_place_disk(self, disk_size: int, peg: str) -> bool:
        stack = self.pegs[peg]
        if not stack:
            return True
        return stack[-1] > disk_size

    def move_disk(self, from_peg: str, to_peg: str) -> Move:
        if not self.pegs[from_peg]:
            raise ValueError(f"Cannot move from empty peg {from_peg}")
            
        disk = self.pegs[from_peg][-1]
        
        if not self.can_place_disk(disk, to_peg):
             # Get top disk of target for error message
             top = self.pegs[to_peg][-1]
             raise ValueError(f"Illegal Move: Cannot place disk {disk} on top of {top} at peg {to_peg}")

        # Execute Move
        initial_height = len(self.pegs[from_peg])
        self.pegs[from_peg].pop()
        
        self.pegs[to_peg].append(disk)
        destination_height = len(self.pegs[to_peg]) - 1 # 0-indexed height
        
        return Move(disk, from_peg, initial_height, to_peg, destination_height)

def solve_hanoi_from_image(initial_state: List[List[int]], 
                           source='A', destination='C', auxiliary='B') -> Tuple[List[Move], TowerState]:
    """
    Solves Tower of Hanoi from an arbitrary initial state image using recursive logic.
    """
    # Initialize state
    state = TowerState(initial_state=initial_state, source=source, 
                       destination=destination, auxiliary=auxiliary)
    moves = []

    def solve_recursive(k: int, target_peg: str):
        """
        Recursively ensures that disk k and all disks smaller than it (1..k-1)
        are moved to the target_peg in the correct order.
        """
        if k == 0:
            return

        # 1. Locate current disk k
        current_peg = state.find_disk_peg(k)

        if current_peg == target_peg:
            # Case A: Disk k is already at the target.
            # We don't move k. We just need to ensure the stack of (k-1)
            # gets placed on top of it at the target.
            solve_recursive(k - 1, target_peg)
        else:
            # Case B: Disk k is at 'current_peg' and needs to go to 'target_peg'.
            aux_peg = state.get_auxiliary(current_peg, target_peg)

            # Step 1: Move the stack of (k-1) disks OUT of the way (to the auxiliary peg).
            # This clears 'current_peg' (exposing disk k) AND clears 'target_peg'.
            solve_recursive(k - 1, aux_peg)

            # Step 2: Physically move disk k to the target.
            # At this specific moment, the move is guaranteed to be legal.
            move_obj = state.move_disk(current_peg, target_peg)
            moves.append(move_obj)

            # Step 3: Move the stack of (k-1) disks ON TOP of disk k at the target.
            solve_recursive(k - 1, target_peg)

    # Start the recursion with the largest disk N aiming for the final destination.
    solve_recursive(state.n, destination)

    return moves, state

if __name__ == "__main__":
    # Test Case 1: Arbitrary scattered state
    # Peg A: [3], Peg B: [2], Peg C: [1] -> Goal: All on C
    initial_state = [[3], [2], [1]]
    
    print(f"Solving for state: {initial_state}")
    moves, final = solve_hanoi_from_image(initial_state)
    
    print(f"Total Moves: {len(moves)}")
    for m in moves:
        print(m)
    
    print("\nFinal State:")
    print(final.pegs)