"""
Tower of Hanoi - State Legality Checker
Validates states including the standard 3 pegs, plus a 4th queue peg and a ground peg.
"""

from typing import List

def check_legality(state: List[List[int]]) -> bool:
    """
    Determines if a given Tower of Hanoi state is legal.
    
    The state is expected to be a list of 5 lists:
    Index 0: Peg A (Standard)
    Index 1: Peg B (Standard)
    Index 2: Peg C (Standard)
    Index 3: 4th Queue Peg (Must be empty)
    Index 4: Ground Peg (Must be empty)
    
    Disks in the lists are ordered from bottom to top (e.g., [3, 2, 1]).
    
    Returns:
        bool: True if legal, False if illegal.
    """
    
    # 1. Validate Input Structure
    if not isinstance(state, list) or len(state) != 5:
        raise ValueError("Input state must be a list containing exactly 5 sub-lists.")

    # 2. Check Forbidden Zones (Index 3 and 4)
    # Rule: If any disk is present on the 4th (index 3) or ground (index 4) pegs, state is illegal.
    if len(state[3]) > 0:
        return False
    if len(state[4]) > 0:
        return False

    # 3. Check Stacking Order on Standard Pegs (Indices 0, 1, 2)
    # Rule: If any disk is bigger than the one underneath it, state is illegal.
    for peg_index in range(3):
        peg = state[peg_index]
        
        # Iterate through the stack from bottom up
        # We stop at len(peg) - 1 because we compare j with j+1
        for j in range(len(peg) - 1):
            disk_underneath = peg[j]
            disk_on_top = peg[j + 1]
            
            # In a valid stack (bottom to top), the disk on top must be smaller.
            # If the top disk is larger than the one below it, it's illegal.
            if disk_on_top > disk_underneath:
                return False

    # If all checks pass
    return True


if __name__ == "__main__":
    # --- Test Cases ---

    # Case 1: Legal Standard State (All on A)
    # Structure: [A, B, C, Queue, Ground]
    state_legal = [
        [3, 2, 1], 
        [], 
        [], 
        [], 
        []
    ]
    print(f"Test Case 1 (Legal Standard): {check_legality(state_legal)}") # Expected: True

    # Case 2: Illegal Stacking (Larger on top of smaller on Peg A)
    # [1, 2] means 1 is at bottom, 2 is on top. 2 > 1 is illegal.
    state_illegal_stack = [
        [1, 2], 
        [3], 
        [], 
        [], 
        []
    ]
    print(f"Test Case 2 (Illegal Stacking): {check_legality(state_illegal_stack)}") # Expected: False

    # Case 3: Illegal 4th Peg Usage
    # Valid stacking on A/B/C, but disk present on 4th peg
    state_illegal_queue = [
        [3, 2], 
        [1], 
        [], 
        [4],  # Disk here makes it illegal
        []
    ]
    print(f"Test Case 3 (Illegal 4th Peg): {check_legality(state_illegal_queue)}") # Expected: False

    # Case 4: Illegal Ground Detection
    # Valid stacking, but disk detected on ground
    state_illegal_ground = [
        [3, 2, 1], 
        [], 
        [], 
        [], 
        [5]   # Disk here makes it illegal
    ]
    print(f"Test Case 4 (Illegal Ground): {check_legality(state_illegal_ground)}") # Expected: False