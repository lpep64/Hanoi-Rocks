"""
Tower of Hanoi - Illegal Ground State Solvers
Contains 2 strategies for handling ground disk violations:
1. Greedy: Place largest ground disk with minimum violation
2. Patient: Wait for legal move opportunity
"""

from typing import List, Tuple, Optional

from hanoi.core.move import Move

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
    
    def is_peg_legal(self, peg_idx: int) -> bool:
        """
        Check if a peg is currently in a legal stacking order.
        Returns True if peg is legal (bottom to top in descending order).
        """
        if peg_idx == self.PEG_QUEUE or peg_idx == self.PEG_GROUND:
            return True  # Queue and Ground don't have stacking rules
        
        peg = self.state[peg_idx]
        if len(peg) <= 1:
            return True  # Empty or single disk is always legal
        
        # Check if each disk is smaller than the one below it
        for i in range(len(peg) - 1):
            if peg[i] < peg[i + 1]:  # Larger disk on top of smaller
                return False
        
        return True
    
    # ==========================================
    # Strategy 1: Greedy 3-Peg (Legality-Aware)
    # ==========================================
    def solve_greedy_3(self) -> Tuple[List[Move], List[List[int]]]:
        """
        Greedy 3-peg strategy with legality priority:
        Priority order for placing ground disk:
        1. Legal move to legal peg (best)
        2. Illegal move to legal peg
        3. Legal move to illegal peg
        4. Illegal move to illegal peg (worst)
        
        Only considers the first 3 pegs (A, B, C).
        """
        
        while self.has_ground_disks():
            # Always pick the largest ground disk
            ground_disks = sorted(self.state[self.PEG_GROUND], reverse=True)
            largest_disk = ground_disks[0]
            
            # Categorize moves by priority
            # Priority 1: Legal move to legal peg
            priority_1 = []
            # Priority 2: Illegal move to legal peg
            priority_2 = []
            # Priority 3: Legal move to illegal peg
            priority_3 = []
            # Priority 4: Illegal move to illegal peg
            priority_4 = []
            
            for peg_idx in [self.PEG_A, self.PEG_B, self.PEG_C]:
                move_is_legal = self.calculate_violation_score(largest_disk, peg_idx) == 0
                peg_is_legal = self.is_peg_legal(peg_idx)
                violation_score = self.calculate_violation_score(largest_disk, peg_idx)
                
                if move_is_legal and peg_is_legal:
                    priority_1.append((peg_idx, violation_score))
                elif not move_is_legal and peg_is_legal:
                    priority_2.append((peg_idx, violation_score))
                elif move_is_legal and not peg_is_legal:
                    priority_3.append((peg_idx, violation_score))
                else:  # not move_is_legal and not peg_is_legal
                    priority_4.append((peg_idx, violation_score))
            
            # Select best move from highest priority group
            best_peg = None
            if priority_1:
                # Among legal moves to legal pegs, pick any (all have score 0)
                best_peg = priority_1[0][0]
            elif priority_2:
                # Among illegal moves to legal pegs, pick minimum violation
                best_peg = min(priority_2, key=lambda x: x[1])[0]
            elif priority_3:
                # Among legal moves to illegal pegs, pick any
                best_peg = priority_3[0][0]
            else:
                # Last resort: illegal move to illegal peg
                best_peg = min(priority_4, key=lambda x: x[1])[0]
            
            # Execute move
            temp_moves = []
            while self.state[self.PEG_GROUND][-1] != largest_disk:
                temp_disk = self.state[self.PEG_GROUND].pop()
                temp_moves.append(temp_disk)
            
            self._execute_physical_move(self.PEG_GROUND, best_peg)
            
            for temp_disk in reversed(temp_moves):
                self.state[self.PEG_GROUND].append(temp_disk)
        
        return self.moves, self.state
    
    # ==========================================
    # Strategy 2: Greedy 4-Peg (Legality-Aware)
    # ==========================================
    def solve_greedy_4(self) -> Tuple[List[Move], List[List[int]]]:
        """
        Greedy 4-peg strategy with legality priority:
        Priority order for placing ground disk:
        1. Legal move to legal peg (best)
        2. Illegal move to legal peg
        3. Legal move to illegal peg
        4. Illegal move to illegal peg (worst)
        
        Considers all 4 pegs (A, B, C, Queue).
        """
        
        while self.has_ground_disks():
            # Always pick the largest ground disk
            ground_disks = sorted(self.state[self.PEG_GROUND], reverse=True)
            largest_disk = ground_disks[0]
            
            # Categorize moves by priority
            priority_1 = []
            priority_2 = []
            priority_3 = []
            priority_4 = []
            
            for peg_idx in [self.PEG_A, self.PEG_B, self.PEG_C, self.PEG_QUEUE]:
                move_is_legal = self.calculate_violation_score(largest_disk, peg_idx) == 0
                peg_is_legal = self.is_peg_legal(peg_idx)
                violation_score = self.calculate_violation_score(largest_disk, peg_idx)
                
                if move_is_legal and peg_is_legal:
                    priority_1.append((peg_idx, violation_score))
                elif not move_is_legal and peg_is_legal:
                    priority_2.append((peg_idx, violation_score))
                elif move_is_legal and not peg_is_legal:
                    priority_3.append((peg_idx, violation_score))
                else:
                    priority_4.append((peg_idx, violation_score))
            
            # Select best move from highest priority group
            best_peg = None
            if priority_1:
                best_peg = priority_1[0][0]
            elif priority_2:
                best_peg = min(priority_2, key=lambda x: x[1])[0]
            elif priority_3:
                best_peg = priority_3[0][0]
            else:
                best_peg = min(priority_4, key=lambda x: x[1])[0]
            
            # Execute move
            temp_moves = []
            while self.state[self.PEG_GROUND][-1] != largest_disk:
                temp_disk = self.state[self.PEG_GROUND].pop()
                temp_moves.append(temp_disk)
            
            self._execute_physical_move(self.PEG_GROUND, best_peg)
            
            for temp_disk in reversed(temp_moves):
                self.state[self.PEG_GROUND].append(temp_disk)
        
        return self.moves, self.state
    
    # ==========================================
    # Strategy 3: Patient 3-Peg
    # ==========================================
    def solve_patient_3(self) -> Tuple[List[Move], List[List[int]]]:
        """
        Patient 3-peg strategy: Only move ground disk when a legal placement exists.
        Only considers the first 3 pegs (A, B, C).
        """
        
        while self.has_ground_disks():
            # Always pick the largest ground disk
            ground_disks = sorted(self.state[self.PEG_GROUND], reverse=True)
            largest_disk = ground_disks[0]
            
            # Check if legal placement exists on first 3 pegs
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
                break
            
            # Execute legal move
            temp_moves = []
            while self.state[self.PEG_GROUND][-1] != largest_disk:
                temp_disk = self.state[self.PEG_GROUND].pop()
                temp_moves.append(temp_disk)
            
            self._execute_physical_move(self.PEG_GROUND, target_peg)
            
            for temp_disk in reversed(temp_moves):
                self.state[self.PEG_GROUND].append(temp_disk)
        
        return self.moves, self.state
    
    # ==========================================
    # Strategy 4: Patient 4-Peg
    # ==========================================
    def solve_patient_4(self) -> Tuple[List[Move], List[List[int]]]:
        """
        Patient 4-peg strategy: Only move ground disk when a legal placement exists.
        Considers all 4 pegs (A, B, C, Queue).
        """
        
        while self.has_ground_disks():
            # Always pick the largest ground disk
            ground_disks = sorted(self.state[self.PEG_GROUND], reverse=True)
            largest_disk = ground_disks[0]
            
            # Check if legal placement exists on all 4 pegs
            legal_move_found = False
            target_peg = None
            
            for peg_idx in [self.PEG_A, self.PEG_B, self.PEG_C, self.PEG_QUEUE]:
                score = self.calculate_violation_score(largest_disk, peg_idx)
                if score == 0:  # Legal placement
                    legal_move_found = True
                    target_peg = peg_idx
                    break
            
            if not legal_move_found:
                # No legal move available, return current state
                break
            
            # Execute legal move
            temp_moves = []
            while self.state[self.PEG_GROUND][-1] != largest_disk:
                temp_disk = self.state[self.PEG_GROUND].pop()
                temp_moves.append(temp_disk)
            
            self._execute_physical_move(self.PEG_GROUND, target_peg)
            
            for temp_disk in reversed(temp_moves):
                self.state[self.PEG_GROUND].append(temp_disk)
        
        return self.moves, self.state
    
    # ==========================================
    # Legacy Methods (for backwards compatibility)
    # ==========================================
    def solve_greedy(self) -> Tuple[List[Move], List[List[int]]]:
        """Legacy greedy method - calls greedy_3."""
        return self.solve_greedy_3()
        
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
    
    
    def solve_patient(self) -> Tuple[List[Move], List[List[int]]]:
        """Legacy patient method - calls patient_3."""
        return self.solve_patient_3()


# --- Wrapper Functions ---

def solve_ground_greedy_3(state):
    """Solve ground violations using greedy 3-peg strategy."""
    solver = GroundSolver(state)
    return solver.solve_greedy_3()

def solve_ground_greedy_4(state):
    """Solve ground violations using greedy 4-peg strategy."""
    solver = GroundSolver(state)
    return solver.solve_greedy_4()

def solve_ground_patient_3(state):
    """Solve ground violations using patient 3-peg strategy."""
    solver = GroundSolver(state)
    return solver.solve_patient_3()

def solve_ground_patient_4(state):
    """Solve ground violations using patient 4-peg strategy."""
    solver = GroundSolver(state)
    return solver.solve_patient_4()

def solve_ground_greedy(state):
    """Legacy wrapper - calls greedy_3."""
    return solve_ground_greedy_3(state)

def solve_ground_patient(state):
    """Legacy wrapper - calls patient_3."""
    return solve_ground_patient_3(state)


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
