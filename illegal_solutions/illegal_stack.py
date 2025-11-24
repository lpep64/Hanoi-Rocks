"""
Tower of Hanoi - Illegal State Solvers
Contains 4 distinct algorithms to solve illegal states using a 4th Queue peg.
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
        print(f"[{self.__class__.__name__}] Strategy: Dig Out")
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
    # Algorithm 2: Bubble Sort
    # ==========================================
    def solve_bubble_sort(self):
        """
        Iteratively scans stacks. If a pair is out of order, unstacks to that depth, 
        swaps the pair using Queue, and restacks.
        """
        print(f"[{self.__class__.__name__}] Strategy: Bubble Sort")
        
        for peg_idx in [self.PEG_A, self.PEG_B, self.PEG_C]:
            is_sorted = False
            while not is_sorted:
                is_sorted = True
                stack = self.state[peg_idx]
                if len(stack) < 2: continue
                
                for i in range(len(stack) - 1):
                    if stack[i] < stack[i+1]: # Inversion found
                        is_sorted = False
                        
                        # Unstack blockers
                        items_above = len(stack) - 1 - (i + 1)
                        for _ in range(items_above):
                            self._execute_physical_move(peg_idx, self.PEG_QUEUE)
                        
                        # Swap Pair
                        self._execute_physical_move(peg_idx, self.PEG_QUEUE) # Top (Big)
                        self._execute_physical_move(peg_idx, self.PEG_QUEUE) # Bottom (Small)
                        
                        temp_peg = (peg_idx + 1) % 3
                        self._execute_physical_move(self.PEG_QUEUE, temp_peg) # Small -> Temp
                        self._execute_physical_move(self.PEG_QUEUE, peg_idx) # Big -> Base
                        self._execute_physical_move(temp_peg, peg_idx) # Small -> Top
                        
                        # Restack
                        for _ in range(items_above):
                             self._execute_physical_move(self.PEG_QUEUE, peg_idx)
                        break 
        
        self._clear_ground_and_queue_to_legal()
        return self.moves, self.state

    # ==========================================
    # Algorithm 3: Total Evacuation (Flatten & Rebuild)
    # ==========================================
    def solve_total_evacuation(self):
        """
        Moves EVERY disk from A, B, C, and Ground into the Queue.
        Then, reconstructs the tower on Peg C from largest to smallest.
        Guarantees a solution but uses many moves.
        """
        print(f"[{self.__class__.__name__}] Strategy: Total Evacuation")

        # Phase 1: Flatten everything to Queue
        # We assume Queue has infinite capacity and no rules
        sources = [self.PEG_A, self.PEG_B, self.PEG_C, self.PEG_GROUND]
        for src in sources:
            while self.state[src]:
                self._execute_physical_move(src, self.PEG_QUEUE)
        
        # Phase 2: Rebuild to C (Selection Sort Logic)
        # All disks are in Queue. We need to find Max, put on C, repeat.
        # We use PEG_A as a temporary stack while digging in Queue.
        
        total_disks = len(self.state[self.PEG_QUEUE])
        if total_disks == 0: return self.moves, self.state

        # Determine the order we need (Largest to Smallest)
        all_disks = sorted(self.state[self.PEG_QUEUE], reverse=True)
        
        for target_disk in all_disks:
            # We know target_disk is in Queue (or temporarily in A during a shuffle, 
            # but we enforce flushing A back to Queue).
            
            # 1. Dig out target_disk from Queue
            # Move items from Queue to A unti we hit target_disk
            while self.state[self.PEG_QUEUE][-1] != target_disk:
                self._execute_physical_move(self.PEG_QUEUE, self.PEG_A)
            
            # 2. Move Target to C
            self._execute_physical_move(self.PEG_QUEUE, self.PEG_C)
            
            # 3. Flush A back to Queue to keep state simple for next iteration
            while self.state[self.PEG_A]:
                self._execute_physical_move(self.PEG_A, self.PEG_QUEUE)
                
        return self.moves, self.state

    # ==========================================
    # Algorithm 4: A* (A-Star) Pathfinding
    # ==========================================
    def solve_a_star(self):
        """
        Uses A* Search to find the shortest path to a legal state where all disks are on Peg C.
        Treats the problem as a graph traversal.
        """
        print(f"[{self.__class__.__name__}] Strategy: A* Search")
        
        # Heuristic Function: Lower is better
        def heuristic(current_state_tuple):
            # Cost = (Disks NOT on C) + (Weight Penalty for Ground/Queue)
            # We want to encourage moving disks to C, and clearing Ground/Queue.
            # State tuple: ( (A..), (B..), (C..), (Q..), (G..) )
            c_peg = current_state_tuple[2]
            ground_peg = current_state_tuple[4]
            queue_peg = current_state_tuple[3]
            
            # Count total disks
            total = sum(len(p) for p in current_state_tuple)
            score = (total - len(c_peg)) * 10 
            score += len(ground_peg) * 50 # High penalty for ground
            score += len(queue_peg) * 5   # Mild penalty for queue
            
            # Reward having largest disks at bottom of C (Correctness)
            # If C is [3, 1], that's bad. If C is [3, 2], that's good.
            # Actually, check_legality handles validity. Here we just want proximity.
            return score

        def get_state_tuple(s):
            return tuple(tuple(peg) for peg in s)

        # Priority Queue: (f_score, move_count, state_tuple, path_of_moves)
        start_tuple = get_state_tuple(self.state)
        pq = [(heuristic(start_tuple), 0, start_tuple, [])]
        visited = {start_tuple: 0}
        
        best_path = None
        
        # Limit iterations to prevent hanging on complex states
        iterations = 0
        limit = 5000 

        while pq:
            f, g, current_s, path = heapq.heappop(pq)
            iterations += 1
            
            # Check Goal: Is it legal? (We strictly want everything on C for this solver)
            # Convert tuple back to list for check_legality
            current_list_state = [list(p) for p in current_s]
            
            # Specific Goal for A*: All disks on C, ordered.
            # We can use check_legality, but strictly we want check_legality AND len(C) == total
            if check_legality(current_list_state):
                # Check if all disks are on C
                total_disks = sum(len(x) for x in current_list_state)
                if len(current_list_state[self.PEG_C]) == total_disks:
                    best_path = path
                    break
            
            if iterations > limit:
                print("A* limit reached, returning partial or failing.")
                break

            # Generate Legal Next Moves
            # Sources: A, B, C, Queue, Ground
            # Targets: A, B, C, Queue (Never Ground)
            
            sources = [0, 1, 2, 3, 4]
            targets = [0, 1, 2, 3] # Queue is 3
            
            for src_idx in sources:
                if not current_s[src_idx]: continue
                
                disk = current_s[src_idx][-1]
                
                for tgt_idx in targets:
                    if src_idx == tgt_idx: continue
                    
                    # Logic: Can we place disk on tgt?
                    can_place = False
                    
                    if tgt_idx == self.PEG_QUEUE:
                        can_place = True # Queue accepts anything
                    else:
                        # Standard Peg Rules
                        if not current_s[tgt_idx]:
                            can_place = True
                        elif current_s[tgt_idx][-1] > disk:
                            can_place = True
                            
                    if can_place:
                        # Create New State
                        new_state_lists = [list(p) for p in current_s]
                        d = new_state_lists[src_idx].pop()
                        new_state_lists[tgt_idx].append(d)
                        new_state_tuple = get_state_tuple(new_state_lists)
                        
                        new_g = g + 1
                        
                        if new_state_tuple not in visited or new_g < visited[new_state_tuple]:
                            visited[new_state_tuple] = new_g
                            new_h = heuristic(new_state_tuple)
                            
                            # Record the move details
                            move_info = (src_idx, tgt_idx) # We'll reconstruct full objects later
                            new_path = path + [move_info]
                            
                            heapq.heappush(pq, (new_g + new_h, new_g, new_state_tuple, new_path))

        if best_path:
            print(f"A* Solution found in {len(best_path)} moves.")
            # Execute the path on the REAL self.state to generate Move objects
            for src, tgt in best_path:
                self._execute_physical_move(src, tgt)
        else:
            print("A* failed to find a solution within limit.")

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
    return IllegalSolver(state).solve_dig_out()

def solve_illegal_bubble_sort(state):
    return IllegalSolver(state).solve_bubble_sort()

def solve_illegal_total_evacuation(state):
    return IllegalSolver(state).solve_total_evacuation()

def solve_illegal_a_star(state):
    return IllegalSolver(state).solve_a_star()


if __name__ == "__main__":
    # Test Case: Mixed Illegal State
    # Peg A: [3, 1] (Validish)
    # Peg B: [2] (Validish)
    # Peg C: []
    # Queue: [4] (Illegal location)
    # Ground: [5] (Illegal location)
    # Goal: All on C.
    
    # We clone this for 4 tests
    base_state = [
        [3, 1], [2], [], [4], [5]
    ]
    
    print("\n" + "="*50)
    print("TEST 1: Dig Out Strategy")
    moves, final = solve_illegal_dig_out(base_state)
    print(f"Moves: {len(moves)} | Final Valid: {check_legality(final)}")
    
    print("\n" + "="*50)
    print("TEST 2: Bubble Sort Strategy")
    moves, final = solve_illegal_bubble_sort(base_state)
    print(f"Moves: {len(moves)} | Final Valid: {check_legality(final)}")
    
    print("\n" + "="*50)
    print("TEST 3: Total Evacuation Strategy")
    moves, final = solve_illegal_total_evacuation(base_state)
    print(f"Moves: {len(moves)} | Final Valid: {check_legality(final)}")
    # Verify strict goal (all on C)
    print(f"All on C? {len(final[2]) == 5}")
    
    print("\n" + "="*50)
    print("TEST 4: A* Search Strategy")
    # A* is expensive, let's use a smaller state for speed demo
    # Peg A: [2, 3] (Illegal order), Peg B: [1]
    small_illegal = [[2, 3], [1], [], [], []]
    moves, final = solve_illegal_a_star(small_illegal)
    print(f"Moves: {len(moves)} | Final Valid: {check_legality(final)}")
    print(f"All on C? {len(final[2]) == 3}")