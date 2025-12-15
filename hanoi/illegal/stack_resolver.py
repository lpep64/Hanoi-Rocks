"""
Tower of Hanoi - Illegal State Solvers
Contains multiple algorithms for statistical analysis:
1. Bubble Sort: Fix illegal ordering by swapping adjacent disks
2. Total Evacuation: Clear illegal pegs to Queue, then redistribute
3. Dig Out: Surgical fix targeting first illegal overlap
4. BFS 3-peg: Optimal pathfinding without Queue assistance
5. BFS 4-peg: Optimal pathfinding with Queue assistance
"""

import heapq
from typing import List, Tuple, Dict

from hanoi.core.move import Move, TowerState
from hanoi.illegal.checker import check_legality

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
    # Algorithm 1: Bubble Sort
    # ==========================================
    def solve_bubble_sort(self):
        """
        Identifies pegs with illegal ordering and fixes them by swapping
        adjacent disks. Uses Queue for temporary storage during swaps.
        Only makes legal, realistic moves (must move blocking disks first).
        """
        max_iterations = 100
        itr = 0
        
        while not check_legality(self.state) and itr < max_iterations:
            itr += 1
            error_found = False
            
            # 1. Find first illegal peg (where top > bottom for any adjacent pair)
            for peg_idx in [self.PEG_A, self.PEG_B, self.PEG_C]:
                if error_found:
                    break
                stack = self.state[peg_idx]
                
                # Scan from bottom up for illegal pair
                for i in range(len(stack) - 1):
                    if stack[i+1] > stack[i]:  # Top disk > bottom disk (illegal)
                        # Found illegal pair at positions i and i+1
                        # Need to fix this by moving everything above i+1 first
                        target_peg = peg_idx
                        illegal_position = i
                        error_found = True
                        break
            
            if not error_found:
                # No stack errors, clear Queue/Ground if needed
                self._clear_ground_and_queue_to_legal()
                continue
            
            # 2. Move all disks above the illegal pair to Queue
            while len(self.state[target_peg]) > illegal_position + 2:
                self._execute_physical_move(target_peg, self.PEG_QUEUE)
            
            # 3. Now top two disks are the illegal pair
            # Pop both to Queue (top goes first, then bottom)
            disk_top = self.state[target_peg][-1]  # Smaller (should be on top)
            disk_bottom = self.state[target_peg][-2]  # Larger (should be on bottom)
            
            self._execute_physical_move(target_peg, self.PEG_QUEUE)  # Small -> Queue
            self._execute_physical_move(target_peg, self.PEG_QUEUE)  # Large -> Queue
            
            # Queue now has [Large, Small] (Large at bottom)
            # Need to swap: put Small back first (bottom), then Large (top)
            # But we need to temporarily use another peg
            
            temp_peg = self.PEG_QUEUE  # We'll swap in place using Queue cleverly
            # Actually, Queue has [Large, Small], we want [Small, Large] on target
            # Pop Small from Queue
            self._execute_physical_move(self.PEG_QUEUE, target_peg)  # Small -> Target
            # Pop Large from Queue  
            self._execute_physical_move(self.PEG_QUEUE, target_peg)  # Large -> Target
            
            # 4. Restore disks from Queue back to target peg
            while self.state[self.PEG_QUEUE]:
                self._execute_physical_move(self.PEG_QUEUE, target_peg)
        
        return self.moves, self.state
    
    # ==========================================
    # Algorithm 2: Total Evacuation
    # ==========================================
    def solve_total_evacuation(self):
        """
        Clears entire illegal pegs to Queue, then redistributes across
        legal pegs (A, B, C) to create a legal state.
        """
        max_iterations = 100
        itr = 0
        
        while not check_legality(self.state) and itr < max_iterations:
            itr += 1
            
            # 1. Find first illegal peg
            illegal_peg = None
            for peg_idx in [self.PEG_A, self.PEG_B, self.PEG_C]:
                stack = self.state[peg_idx]
                for i in range(len(stack) - 1):
                    if stack[i+1] > stack[i]:  # Illegal ordering
                        illegal_peg = peg_idx
                        break
                if illegal_peg is not None:
                    break
            
            # 2. Check if Queue or Ground have disks (also illegal)
            if illegal_peg is None:
                if self.state[self.PEG_QUEUE] or self.state[self.PEG_GROUND]:
                    # Clear Queue/Ground to legal pegs
                    self._clear_ground_and_queue_to_legal()
                continue
            
            # 3. Evacuate entire illegal peg to Queue
            while self.state[illegal_peg]:
                self._execute_physical_move(illegal_peg, self.PEG_QUEUE)
            
            # 4. Redistribute from Queue to legal pegs (A, B, C)
            # Try to place disks legally (on top of larger disks)
            while self.state[self.PEG_QUEUE]:
                disk = self.state[self.PEG_QUEUE][-1]
                placed = False
                
                # Try to place on any legal peg where it fits
                for target_peg in [self.PEG_A, self.PEG_B, self.PEG_C]:
                    if not self.state[target_peg] or self.state[target_peg][-1] > disk:
                        self._execute_physical_move(self.PEG_QUEUE, target_peg)
                        placed = True
                        break
                
                if not placed:
                    # Can't place legally anywhere, put on first available peg
                    # This might create temporary illegality, but next iteration will fix
                    self._execute_physical_move(self.PEG_QUEUE, self.PEG_A)
        
        return self.moves, self.state
    
    # ==========================================
    # Algorithm 3: Dig Out (Surgical Fix)
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
    # Algorithm 4: BFS 3-Peg (No Queue)
    # ==========================================
    def solve_a_star_3peg(self):
        """
        Uses BFS to find the SHORTEST path to ANY legal state.
        Only uses the 3 standard pegs (A, B, C) - ignores Queue.
        Explores all states level-by-level until legality is achieved.
        """
        print(f"[{self.__class__.__name__}] Strategy: BFS 3-Peg (no Queue assistance)")
        
        from collections import deque
        
        def get_state_tuple(s):
            return tuple(tuple(peg) for peg in s)
        
        start_tuple = get_state_tuple(self.state)
        queue = deque([(start_tuple, [])])
        visited = {start_tuple}
        
        best_path = None
        iterations = 0
        limit = 50000
        
        while queue:
            current_s, path = queue.popleft()
            iterations += 1
            
            current_list_state = [list(p) for p in current_s]
            
            if check_legality(current_list_state):
                best_path = path
                print(f"BFS 3-Peg found legal state in {len(path)} moves (explored {iterations} states)")
                break
            
            if iterations > limit:
                print(f"BFS 3-Peg limit reached after {iterations} iterations")
                break
            
            # Generate moves only between A, B, C (indices 0, 1, 2)
            # Can move FROM Queue/Ground if they have disks, but never TO them
            sources = [0, 1, 2, 3, 4]  # Can move from anywhere
            targets = [0, 1, 2]  # Only to A, B, C (no Queue, no Ground)
            
            for src_idx in sources:
                if not current_s[src_idx]:
                    continue
                
                for tgt_idx in targets:
                    if src_idx == tgt_idx:
                        continue
                    
                    # Allow all moves to standard pegs
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
            for src, tgt in best_path:
                self._execute_physical_move(src, tgt)
        else:
            print("BFS 3-Peg failed to find a solution within limit.")
        
        return self.moves, self.state
    
    # ==========================================
    # Algorithm 5: BFS 4-Peg (With Queue)
    # ==========================================
    def solve_a_star_4peg(self):
        """
        Uses BFS to find the SHORTEST path to ANY legal state.
        Can use the Queue peg (4 pegs total: A, B, C, Queue).
        Explores all states level-by-level until legality is achieved.
        Guarantees optimal solution (minimum moves to legality).
        """
        print(f"[{self.__class__.__name__}] Strategy: BFS 4-Peg (with Queue assistance)")
        
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
                    # This includes creating temporary illegal states
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
            for src, tgt in best_path:
                self._execute_physical_move(src, tgt)
        else:
            print("BFS 4-Peg failed to find a solution within limit.")
        
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

def solve_illegal_bubble_sort(state):
    """Wrapper for Bubble Sort strategy - swaps adjacent illegal disks."""
    return IllegalSolver(state).solve_bubble_sort()

def solve_illegal_total_evacuation(state):
    """Wrapper for Total Evacuation strategy - clears illegal pegs to Queue and redistributes."""
    return IllegalSolver(state).solve_total_evacuation()

def solve_illegal_dig_out(state):
    """Wrapper for Dig Out strategy - surgical fix for first illegal overlap."""
    return IllegalSolver(state).solve_dig_out()

def solve_illegal_a_star_3peg(state):
    """
    Wrapper for BFS 3-Peg strategy - finds shortest path without Queue assistance.
    
    Args:
        state: Initial illegal state [Peg A, Peg B, Peg C, Queue, Ground]
    
    Returns:
        Tuple of (moves, final_state)
        - moves: List of Move objects
        - final_state: Final legal state
    """
    return IllegalSolver(state).solve_a_star_3peg()

def solve_illegal_a_star_4peg(state):
    """
    Wrapper for BFS 4-Peg strategy - finds shortest path with Queue assistance.
    
    Args:
        state: Initial illegal state [Peg A, Peg B, Peg C, Queue, Ground]
    
    Returns:
        Tuple of (moves, final_state)
        - moves: List of Move objects
        - final_state: Final legal state
    """
    return IllegalSolver(state).solve_a_star_4peg()

# Backward compatibility alias
def solve_illegal_a_star(state):
    """Backward compatibility - defaults to 4-peg BFS."""
    return solve_illegal_a_star_4peg(state)


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
    print("TEST 1: Bubble Sort Strategy")
    print("="*50)
    moves, final = solve_illegal_bubble_sort([list(p) for p in base_state])
    print(f"Moves: {len(moves)}")
    print(f"Final Valid: {check_legality(final)}")
    if len(moves) > 0:
        print(f"First move: {moves[0]}")
        print(f"Last move: {moves[-1]}")
    
    print("\n" + "="*50)
    print("TEST 2: Total Evacuation Strategy")
    print("="*50)
    moves, final = solve_illegal_total_evacuation([list(p) for p in base_state])
    print(f"Moves: {len(moves)}")
    print(f"Final Valid: {check_legality(final)}")
    if len(moves) > 0:
        print(f"First move: {moves[0]}")
        print(f"Last move: {moves[-1]}")
    
    print("\n" + "="*50)
    print("TEST 3: Dig Out Strategy")
    print("="*50)
    moves, final = solve_illegal_dig_out([list(p) for p in base_state])
    print(f"Moves: {len(moves)}")
    print(f"Final Valid: {check_legality(final)}")
    if len(moves) > 0:
        print(f"First move: {moves[0]}")
        print(f"Last move: {moves[-1]}")
    
    print("\n" + "="*50)
    print("TEST 4: BFS 3-Peg Strategy")
    print("="*50)
    small_illegal = [[2, 3], [1], [], [], []]
    moves, final = solve_illegal_a_star_3peg(small_illegal)
    print(f"Moves: {len(moves)}")
    print(f"Final Valid: {check_legality(final)}")
    if len(moves) > 0:
        print(f"First move: {moves[0]}")
        print(f"Last move: {moves[-1]}")
    
    print("\n" + "="*50)
    print("TEST 5: BFS 4-Peg Strategy")
    print("="*50)
    small_illegal2 = [[2, 3], [1], [], [], []]
    moves, final = solve_illegal_a_star_4peg(small_illegal2)
    print(f"Moves: {len(moves)}")
    print(f"Final Valid: {check_legality(final)}")
    if len(moves) > 0:
        print(f"First move: {moves[0]}")
        print(f"Last move: {moves[-1]}")