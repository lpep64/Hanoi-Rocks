"""
Tower of Hanoi - Illegal State Solvers
Contains 2 algorithms for statistical analysis:
1. Dig Out: Surgical fix targeting first illegal overlap
2. BFS (Breadth-First Search): Optimal pathfinding to ANY legal state
"""

import sys
import os
import heapq
from typing import List, Tuple, Dict

# Add the sibling directory to the path to import hanoi_state
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../state_solutions')))

from hanoi_state import Move, TowerState
from illegal_check import check_legality

class IllegalSolver:
    def __init__(self, initial_state):
        """
        Initialize with the 5-array state: [A, B, C, Queue, Ground]
        """
        self.state = [list(p) for p in initial_state] # Deep copy
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
        initial_height = len(self.state[from_idx]) # Height after pop
        
        self.state[to_idx].append(disk)
        destination_height = len(self.state[to_idx]) - 1 # Current top index
        
        move_obj = Move(
            disk=disk,
            initial_peg=self.peg_names[from_idx],
            initial_height=initial_height,
            destination_peg=self.peg_names[to_idx],
            destination_height=destination_height
        )
        self.moves.append(move_obj)
        return move_obj

    # ==========================================
    # Algorithm 1: Dig Out (Surgical Fix)
    # ==========================================
    def solve_dig_out(self):
        """
        Detects the FIRST illegal overlap, moves items above it to Queue,
        fixes the specific pair order, and replaces them.
        """
        max_iterations = 100
        itr = 0
        
        while not check_legality(self.state) and itr < max_iterations:
            itr += 1
            error_found = False
            target_peg = -1
            split_index = -1
            
            # 1. Detect Stack Errors
            for peg_idx in [self.PEG_A, self.PEG_B, self.PEG_C]:
                if error_found: break
                stack = self.state[peg_idx]
                for i in range(len(stack) - 1):
                    if stack[i+1] > stack[i]: # Top > Bottom (Illegal)
                        target_peg = peg_idx
                        split_index = i
                        error_found = True
                        break
            
            # 2. Handle Ground/Queue Cleanup if no stack errors
            if not error_found:
                self._clear_ground_and_queue_to_legal()
                continue

            # 3. Dig Phase: Move blockers to Queue
            while len(self.state[target_peg]) > split_index + 2:
                self._execute_physical_move(target_peg, self.PEG_QUEUE)
                
            # 4. Swap Phase
            # Pop Big (Illegal Top) and Small (Bottom) to Queue
            self._execute_physical_move(target_peg, self.PEG_QUEUE) # Big -> Queue
            self._execute_physical_move(target_peg, self.PEG_QUEUE) # Small -> Queue
            
            # Queue top is now [Big, Small]. 
            # Use Temp (B or C) to flip them
            temp_peg = (target_peg + 1) % 3
            self._execute_physical_move(self.PEG_QUEUE, temp_peg) # Small -> Temp
            self._execute_physical_move(self.PEG_QUEUE, target_peg) # Big -> Target (Bottom)
            self._execute_physical_move(temp_peg, target_peg) # Small -> Target (Top)
            
            # 5. Restore Phase
            while self.state[self.PEG_QUEUE]:
                # Simple restore. If this causes new illegality, the loop catches it next time.
                self._execute_physical_move(self.PEG_QUEUE, target_peg)

        return self.moves, self.state

    # ==========================================
    # Algorithm 2: BFS (Breadth-First Search)
    # ==========================================
    def solve_a_star(self):
        """
        Uses BFS to find the SHORTEST path to ANY legal state.
        Explores all states level-by-level until legality is achieved.
        Guarantees optimal solution (minimum moves to legality).
        
        Note: Named solve_a_star for backward compatibility, but implements pure BFS.
        """
        print(f"[{self.__class__.__name__}] Strategy: BFS (optimal shortest path)")
        
        from collections import deque
        
        def get_state_tuple(s):
            return tuple(tuple(peg) for peg in s)
        
        # Queue: (state_tuple, path_of_moves)
        start_tuple = get_state_tuple(self.state)
        queue = deque([(start_tuple, [])])
        visited = {start_tuple}
        
        best_path = None
        iterations = 0
        limit = 50000  # Higher limit for complex illegal states
        
        while queue:
            current_s, path = queue.popleft()
            iterations += 1
            
            # Convert tuple back to list for validation
            current_list_state = [list(p) for p in current_s]
            
            # GOAL: Any legal state (passes check_legality)
            if check_legality(current_list_state):
                best_path = path
                print(f"BFS found legal state in {len(path)} moves (explored {iterations} states)")
                break
            
            if iterations > limit:
                print(f"BFS limit reached after {iterations} iterations")
                break
            
            # Generate all possible moves (maximum exploration)
            sources = [0, 1, 2, 3, 4]  # Can move from anywhere including Ground
            targets = [0, 1, 2, 3]     # Never target Ground (output only)
            
            for src_idx in sources:
                if not current_s[src_idx]:
                    continue
                
                disk = current_s[src_idx][-1]
                
                for tgt_idx in targets:
                    if src_idx == tgt_idx:
                        continue
                    
                    # Allow all moves for maximum flexibility
                    # This includes creating temporary illegal states on standard pegs
                    can_place = False
                    
                    if tgt_idx == self.PEG_QUEUE:
                        can_place = True  # Queue accepts anything
                    else:
                        # Standard pegs: allow any placement
                        # BFS will find shortest path even through illegal intermediates
                        can_place = True
                    
                    if can_place:
                        # Create new state
                        new_state_lists = [list(p) for p in current_s]
                        d = new_state_lists[src_idx].pop()
                        new_state_lists[tgt_idx].append(d)
                        
                        new_state_tuple = get_state_tuple(new_state_lists)
                        
                        if new_state_tuple not in visited:
                            visited.add(new_state_tuple)
                            move_info = (src_idx, tgt_idx)
                            new_path = path + [move_info]
                            queue.append((new_state_tuple, new_path))
        
        if best_path:
            # Execute the path on the real state to generate Move objects
            for src, tgt in best_path:
                self._execute_physical_move(src, tgt)
        else:
            print("BFS failed to find a solution within limit.")
        
        return self.moves, self.state

    # ==========================================
    # Helpers
    # ==========================================
    def _clear_ground_and_queue_to_legal(self):
        """Helper to dump Queue/Ground to A/B/C legally if possible, or just A."""
        for peg in [self.PEG_GROUND, self.PEG_QUEUE]:
            while self.state[peg]:
                # Try to place legally on A, B, or C
                moved = False
                disk = self.state[peg][-1]
                for target in [self.PEG_A, self.PEG_B, self.PEG_C]:
                    if not self.state[target] or self.state[target][-1] > disk:
                        self._execute_physical_move(peg, target)
                        moved = True
                        break
                if not moved:
                    # Force move to A (might create new illegality, but Loop handles it)
                    self._execute_physical_move(peg, self.PEG_A)


# --- Wrapper Functions ---

def solve_illegal_dig_out(state):
    """Wrapper for Dig Out strategy - surgical fix for first illegal overlap."""
    return IllegalSolver(state).solve_dig_out()

def solve_illegal_a_star(state):
    """
    Wrapper for BFS strategy - finds shortest path to ANY legal state.
    
    Args:
        state: Initial illegal state [Peg A, Peg B, Peg C, Queue, Ground]
    
    Returns:
        Tuple of (moves, final_state)
        - moves: List of Move objects
        - final_state: Final legal state
    """
    return IllegalSolver(state).solve_a_star()


if __name__ == "__main__":
    # Test Case: Mixed Illegal State
    # Peg A: [3, 1] (Stack violation)
    # Peg B: [2]
    # Peg C: []
    # Queue: [4] (Illegal location)
    # Ground: [5] (Illegal location)
    # Goal: All on C in legal order.
    
    base_state = [
        [3, 1], [2], [], [4], [5]
    ]
    
    print("\n" + "="*50)
    print("TEST 1: Dig Out Strategy")
    print("="*50)
    moves, final = solve_illegal_dig_out(base_state)
    print(f"Moves: {len(moves)}")
    print(f"Final Valid: {check_legality(final)}")
    print(f"All on C: {len(final[2]) == 5}")
    if len(moves) > 0:
        print(f"First move: {moves[0]}")
        print(f"Last move: {moves[-1]}")
    
    print("\n" + "="*50)
    print("TEST 2: A* Search Strategy")
    print("="*50)
    # A* is expensive, use a smaller state
    # Peg A: [2, 3] (Illegal order), Peg B: [1]
    small_illegal = [[2, 3], [1], [], [], []]
    moves, final = solve_illegal_a_star(small_illegal)
    print(f"Moves: {len(moves)}")
    print(f"Final Valid: {check_legality(final)}")
    print(f"All on C: {len(final[2]) == 3}")
    if len(moves) > 0:
        print(f"First move: {moves[0]}")
        print(f"Last move: {moves[-1]}")