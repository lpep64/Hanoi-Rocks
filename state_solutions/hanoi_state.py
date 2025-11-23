"""
Tower of Hanoi - Generalized Solver with Height Tracking
Solves Tower of Hanoi from any arbitrary initial state configuration.
Tracks disk position, initial height, and destination height for every move.
"""

from typing import List, Tuple, Dict, Optional

class Move:
    """
    Represents a single move in the Tower of Hanoi puzzle with complete state information.
    """
    def __init__(self, disk: int, initial_peg: str, initial_height: int, destination_peg: str, destination_height: int):
        """
        Initialize a move with complete state information.
        
        Args:
            disk: The disk number being moved (1 is smallest)
            initial_peg: The peg the disk is moving from ('A', 'B', or 'C')
            initial_height: The height position on the initial peg (0 is bottom)
            destination_peg: The peg the disk is moving to ('A', 'B', or 'C')
            destination_height: The height position on the destination peg after move
        """
        self.disk = disk
        self.initial_peg = initial_peg
        self.initial_height = initial_height
        self.destination_peg = destination_peg
        self.destination_height = destination_height
    
    def __repr__(self):
        return (f"Move(disk={self.disk}, {self.initial_peg}[h={self.initial_height}] -> "
                f"{self.destination_peg}[h={self.destination_height}])")
    
    def __str__(self):
        return (f"Move disk {self.disk} from {self.initial_peg} (height {self.initial_height}) "
                f"to {self.destination_peg} (height {self.destination_height})")


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
            # --- Validation Logic ---
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

            # Initialize pegs
            self.pegs = {
                source: list(initial_state[0]),
                auxiliary: list(initial_state[1]),
                destination: list(initial_state[2])
            }
            
            # Validate legal Hanoi state (smaller on top of larger)
            for name, stack in self.pegs.items():
                for i in range(len(stack) - 1):
                    if stack[i] <= stack[i+1]:
                        raise ValueError(f"Invalid stack on peg {name}: larger disk on top of smaller.")
        else:
            # Standard initialization if no image provided
            self.n = n if n else 3
            self.pegs = {
                source: list(range(self.n, 0, -1)),
                auxiliary: [],
                destination: []
            }

    def get_height(self, peg: str) -> int:
        """Get the current height (number of disks) on a peg."""
        return len(self.pegs[peg])

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
        """
        Move the top disk from one peg to another and return a detailed Move object.
        """
        if not self.pegs[from_peg]:
            raise ValueError(f"Cannot move from empty peg {from_peg}")
            
        # Validation before move
        disk = self.pegs[from_peg][-1]
        if not self.can_place_disk(disk, to_peg):
             top = self.pegs[to_peg][-1]
             raise ValueError(f"Illegal Move: Cannot place disk {disk} on top of {top} at peg {to_peg}")

        # --- Height Calculation & Execution ---
        
        # 1. Remove from Source
        disk = self.pegs[from_peg].pop()
        # The height index is the length of the list AFTER pop (0-based index of the item that was just there)
        # Example: [3, 2, 1] -> pop 1 -> [3, 2] (len 2). 1 was at index 2.
        initial_height = len(self.pegs[from_peg])
        
        # 2. Add to Destination
        self.pegs[to_peg].append(disk)
        # The height index is len - 1 (0-based index of the new item)
        destination_height = len(self.pegs[to_peg]) - 1
        
        return Move(disk, from_peg, initial_height, to_peg, destination_height)


def solve_hanoi_from_image(initial_state: List[List[int]], 
                           source='A', destination='C', auxiliary='B') -> Tuple[List[Move], TowerState]:
    """
    Solves Tower of Hanoi from an arbitrary initial state image using recursive logic.
    Returns moves with full height tracking metadata.
    """
    # Initialize state with the arbitrary image
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

        current_peg = state.find_disk_peg(k)

        if current_peg == target_peg:
            # Disk k is already at target. 
            # Just ensure the stack of (k-1) gets placed on top of it here.
            solve_recursive(k - 1, target_peg)
        else:
            # Disk k needs to move.
            aux_peg = state.get_auxiliary(current_peg, target_peg)

            # 1. clear the way (move k-1 out of the way to aux)
            solve_recursive(k - 1, aux_peg)

            # 2. move disk k (capturing the detailed Move object)
            move_obj = state.move_disk(current_peg, target_peg)
            moves.append(move_obj)

            # 3. fill the stack (move k-1 on top of k at target)
            solve_recursive(k - 1, target_peg)

    # Start recursion
    solve_recursive(state.n, destination)

    return moves, state

if __name__ == "__main__":
    # Test Case: Arbitrary scattered state
    # A has 3, B has 2, C has 1. Goal -> All to C.
    # We expect moves that show height changes clearly.
    initial_state = [[3], [2], [1]]
    
    print(f"Solving for state: {initial_state}")
    moves, final = solve_hanoi_from_image(initial_state)
    
    print(f"\nTotal Moves: {len(moves)}")
    print("-" * 60)
    for m in moves:
        print(m)
    print("-" * 60)
    
    print("\nFinal State configuration:")
    print(final.pegs)