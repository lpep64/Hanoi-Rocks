"""
Tower of Hanoi Master Solver - Standalone Version
No external imports. All code inlined.
Default settings: discard duplicates, greedy_3, bfs_3, with destination_peg flag.
"""

from typing import List, Tuple, Dict, Optional
from copy import deepcopy
from collections import deque, Counter
import heapq

# ==========================================
# Custom Exceptions
# ==========================================

class UnsolvableStateError(Exception):
    """Raised when the puzzle configuration is provably unsolvable."""
    pass

class InvalidFlagCombinationError(Exception):
    """Raised when flag combination leads to contradictory requirements."""
    pass

class InvalidStateError(Exception):
    """Raised when input state is malformed or invalid."""
    pass


# ==========================================
# Move Class (from hanoi_state.py)
# ==========================================

class Move:
    """Represents a single move in the Tower of Hanoi puzzle with complete state information."""
    
    def __init__(self, disk: int, initial_peg: str, initial_height: int, destination_peg: str, destination_height: int):
        self.disk = disk
        self.initial_peg = initial_peg
        self.initial_height = initial_height
        self.destination_peg = destination_peg
        self.destination_height = destination_height
        self.disk_label = None  # Optional label for duplicate disks
    
    def __repr__(self):
        label = f" '{self.disk_label}'" if self.disk_label else ""
        return (f"Move(disk={self.disk}{label}, {self.initial_peg}[h={self.initial_height}] -> "
                f"{self.destination_peg}[h={self.destination_height}])")
    
    def __str__(self):
        label = f" ({self.disk_label})" if self.disk_label else ""
        return (f"Move disk {self.disk}{label} from {self.initial_peg} (height {self.initial_height}) "
                f"to {self.destination_peg} (height {self.destination_height})")


# ==========================================
# TowerState Class (from hanoi_state.py)
# ==========================================

class TowerState:
    """Tracks the current state of all three pegs in the Tower of Hanoi puzzle."""
    
    def __init__(self, initial_state: List[List[int]] = None, n: int = None, 
                 source='A', destination='C', auxiliary='B'):
        self.source = source
        self.destination = destination
        self.auxiliary = auxiliary
        self.peg_names = [source, auxiliary, destination]
        self.pegs = {}
        
        if initial_state is not None:
            if len(initial_state) != 3:
                raise ValueError("initial_state must contain exactly 3 lists")
            
            all_disks = []
            for p in initial_state:
                all_disks.extend(p)
                
            if not all_disks:
                 raise ValueError("initial_state must contain at least one disk")
            
            self.n = max(all_disks)
            
            if sorted(all_disks) != list(range(1, self.n + 1)):
                 raise ValueError(f"Disks must range from 1 to {self.n} without duplicates or gaps.")

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
            self.n = n if n else 3
            self.pegs = {
                source: list(range(self.n, 0, -1)),
                auxiliary: [],
                destination: []
            }

    def get_height(self, peg: str) -> int:
        return len(self.pegs[peg])

    def find_disk_peg(self, disk_size: int) -> str:
        for name, stack in self.pegs.items():
            if disk_size in stack:
                return name
        raise ValueError(f"Disk {disk_size} not found in any peg state.")

    def get_auxiliary(self, peg1: str, peg2: str) -> str:
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
             top = self.pegs[to_peg][-1]
             raise ValueError(f"Illegal Move: Cannot place disk {disk} on top of {top} at peg {to_peg}")

        disk = self.pegs[from_peg].pop()
        initial_height = len(self.pegs[from_peg])
        
        self.pegs[to_peg].append(disk)
        destination_height = len(self.pegs[to_peg]) - 1
        
        return Move(disk, from_peg, initial_height, to_peg, destination_height)


def solve_hanoi_from_image(initial_state: List[List[int]], 
                           source='A', destination='C', auxiliary='B') -> Tuple[List[Move], TowerState]:
    """Solves Tower of Hanoi from an arbitrary initial state image using recursive logic."""
    
    state = TowerState(initial_state=initial_state, source=source, 
                       destination=destination, auxiliary=auxiliary)
    moves = []

    def solve_recursive(k: int, target_peg: str):
        if k == 0:
            return

        current_peg = state.find_disk_peg(k)

        if current_peg == target_peg:
            solve_recursive(k - 1, target_peg)
        else:
            aux_peg = state.get_auxiliary(current_peg, target_peg)
            solve_recursive(k - 1, aux_peg)
            move_obj = state.move_disk(current_peg, target_peg)
            moves.append(move_obj)
            solve_recursive(k - 1, target_peg)

    solve_recursive(state.n, destination)
    return moves, state


# ==========================================
# Legality Checker (from illegal_check.py)
# ==========================================

def check_legality(state: List[List[int]]) -> bool:
    """Determines if a given Tower of Hanoi state is legal."""
    
    if not isinstance(state, list) or len(state) != 5:
        raise ValueError("Input state must be a list containing exactly 5 sub-lists.")

    if len(state[3]) > 0:
        return False
    if len(state[4]) > 0:
        return False

    for peg_index in range(3):
        peg = state[peg_index]
        for j in range(len(peg) - 1):
            disk_underneath = peg[j]
            disk_on_top = peg[j + 1]
            if disk_on_top > disk_underneath:
                return False

    return True


# ==========================================
# IllegalSolver Class (from illegal_stack.py)
# ==========================================

class IllegalSolver:
    def __init__(self, initial_state):
        self.state = [list(p) for p in initial_state]
        self.moves = []
        
        self.PEG_A = 0
        self.PEG_B = 1
        self.PEG_C = 2
        self.PEG_QUEUE = 3
        self.PEG_GROUND = 4
        
        self.peg_names = {0: 'A', 1: 'B', 2: 'C', 3: 'Queue', 4: 'Ground'}

    def _execute_physical_move(self, from_idx, to_idx):
        if not self.state[from_idx]:
            raise ValueError(f"Cannot move from empty peg {self.peg_names[from_idx]}")
            
        disk = self.state[from_idx].pop()
        initial_height = len(self.state[from_idx])
        
        self.state[to_idx].append(disk)
        destination_height = len(self.state[to_idx]) - 1
        
        move_obj = Move(
            disk=disk,
            initial_peg=self.peg_names[from_idx],
            initial_height=initial_height,
            destination_peg=self.peg_names[to_idx],
            destination_height=destination_height
        )
        self.moves.append(move_obj)
        return move_obj

    def solve_a_star_3peg(self):
        """Uses BFS to find the SHORTEST path to ANY legal state. Only uses 3 standard pegs (A, B, C)."""
        print(f"[IllegalSolver] Strategy: BFS 3-Peg (no Queue assistance)")
        
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
            
            sources = [0, 1, 2, 3, 4]
            targets = [0, 1, 2]
            
            for src_idx in sources:
                if not current_s[src_idx]:
                    continue
                
                for tgt_idx in targets:
                    if src_idx == tgt_idx:
                        continue
                    
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
# GroundSolver Class (from illegal_ground.py)
# ==========================================

class GroundSolver:
    def __init__(self, state):
        self.state = [list(p) for p in state]
        self.moves = []
        
        self.PEG_A = 0
        self.PEG_B = 1
        self.PEG_C = 2
        self.PEG_QUEUE = 3
        self.PEG_GROUND = 4
        
        self.peg_names = {0: 'A', 1: 'B', 2: 'C', 3: 'Queue', 4: 'Ground'}
    
    def _execute_physical_move(self, from_idx, to_idx):
        if not self.state[from_idx]:
            raise ValueError(f"Cannot move from empty peg {self.peg_names[from_idx]}")
            
        disk = self.state[from_idx].pop()
        initial_height = len(self.state[from_idx])
        
        self.state[to_idx].append(disk)
        destination_height = len(self.state[to_idx]) - 1
        
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
        return len(self.state[self.PEG_GROUND]) > 0
    
    def calculate_violation_score(self, disk: int, peg_idx: int) -> int:
        if peg_idx == self.PEG_QUEUE:
            return 0
        
        peg = self.state[peg_idx]
        if not peg:
            return 0
        
        top_disk = peg[-1]
        if top_disk > disk:
            return 0
        
        return disk - top_disk
    
    def solve_greedy_3(self) -> Tuple[List[Move], List[List[int]]]:
        """Greedy 3-peg strategy: Place largest ground disk on peg with minimum violation."""
        
        while self.has_ground_disks():
            ground_disks = sorted(self.state[self.PEG_GROUND], reverse=True)
            largest_disk = ground_disks[0]
            
            best_peg = self.PEG_A
            best_score = float('inf')
            
            for peg_idx in [self.PEG_A, self.PEG_B, self.PEG_C]:
                score = self.calculate_violation_score(largest_disk, peg_idx)
                if score < best_score:
                    best_score = score
                    best_peg = peg_idx
            
            temp_moves = []
            while self.state[self.PEG_GROUND][-1] != largest_disk:
                temp_disk = self.state[self.PEG_GROUND].pop()
                temp_moves.append(temp_disk)
            
            self._execute_physical_move(self.PEG_GROUND, best_peg)
            
            for temp_disk in reversed(temp_moves):
                self.state[self.PEG_GROUND].append(temp_disk)
        
        return self.moves, self.state


# ==========================================
# State Preprocessing
# ==========================================

def preprocess_state(state: List[List[int]], duplicate_strategy: str) -> Tuple[List[List[int]], Dict]:
    """Preprocess the input state to handle duplicates and create disk mapping."""
    
    all_disks = []
    for peg_idx, peg in enumerate(state):
        for disk in peg:
            all_disks.append(disk)
    
    if not all_disks:
        raise InvalidStateError("State must contain at least one disk")
    
    disk_counts = Counter(all_disks)
    has_duplicates = any(count > 1 for count in disk_counts.values())
    
    disk_info = {
        'has_duplicates': has_duplicates,
        'mapping': {},
        'id_map': {},
        'reverse_map': {}
    }
    
    if duplicate_strategy == 'discard':
        # Keep first occurrence of each disk value
        seen = set()
        unique_disks = []
        for peg in state:
            for disk in peg:
                if disk not in seen:
                    unique_disks.append(disk)
                    seen.add(disk)
        unique_disks = sorted(unique_disks)
        
        disk_mapping = {disk: i+1 for i, disk in enumerate(unique_disks)}
        disk_info['mapping'] = disk_mapping
        
        processed_state = []
        for peg in state:
            new_peg = []
            seen_in_peg = set()
            for disk in peg:
                if disk not in seen_in_peg:
                    new_peg.append(disk_mapping[disk])
                    seen_in_peg.add(disk)
            processed_state.append(new_peg)
        
        return processed_state, disk_info
    else:
        raise InvalidFlagCombinationError(f"Invalid duplicate_strategy: {duplicate_strategy}")


# ==========================================
# Ground Disk Resolution
# ==========================================

def resolve_ground_disks(state: List[List[int]], ground_strategy: str) -> Tuple[List[Move], List[List[int]]]:
    """Resolve ground disk violations using specified strategy."""
    
    if not state[4]:
        return [], state
    
    solver = GroundSolver(state)
    
    if ground_strategy == 'greedy_3':
        moves, final_state = solver.solve_greedy_3()
    else:
        raise InvalidFlagCombinationError(f"Invalid ground_strategy: {ground_strategy}")
    
    return moves, final_state


# ==========================================
# Illegal State Resolution
# ==========================================

def resolve_illegal_state(state: List[List[int]], illegal_resolution: str) -> Tuple[List[Move], List[List[int]]]:
    """Resolve illegal stacking using specified strategy."""
    
    if check_legality(state):
        return [], state
    
    solver = IllegalSolver(state)
    
    if illegal_resolution == 'bfs_3peg':
        moves, final_state = solver.solve_a_star_3peg()
    else:
        raise InvalidFlagCombinationError(f"Invalid illegal_resolution: {illegal_resolution}")
    
    if not check_legality(final_state):
        raise UnsolvableStateError(f"Failed to resolve illegal state using strategy '{illegal_resolution}'")
    
    return moves, final_state


# ==========================================
# Standard 3-Peg Solver
# ==========================================

def solve_standard_3peg(state: List[List[int]], target_peg_idx: int) -> Tuple[List[Move], List[List[int]]]:
    """Solve using standard 3-peg logic (ignoring Queue peg)."""
    
    three_peg_state = [state[0], state[1], state[2]]
    
    if state[3] or state[4]:
        raise ValueError("Cannot solve with standard 3-peg when Queue or Ground contain disks")
    
    all_disks = []
    for peg in three_peg_state:
        all_disks.extend(peg)
    
    if all_disks:
        unique_disks = sorted(set(all_disks))
        disk_mapping = {disk: i+1 for i, disk in enumerate(unique_disks)}
        
        normalized_state = []
        for peg in three_peg_state:
            normalized_state.append([disk_mapping[d] for d in peg])
        
        three_peg_state = normalized_state
        total_disks = len(unique_disks)
    else:
        total_disks = 0
    
    if three_peg_state[target_peg_idx] and len(three_peg_state[target_peg_idx]) == total_disks:
        return [], state
    
    peg_names = ['A', 'B', 'C']
    target_name = peg_names[target_peg_idx]
    
    peg_map = {}
    if target_peg_idx == 0:
        rearranged_state = [three_peg_state[1], three_peg_state[2], three_peg_state[0]]
        rearranged_names = ['B', 'C', 'A']
        peg_map = {0: 1, 1: 2, 2: 0}
    elif target_peg_idx == 1:
        rearranged_state = [three_peg_state[0], three_peg_state[2], three_peg_state[1]]
        rearranged_names = ['A', 'C', 'B']
        peg_map = {0: 0, 1: 2, 2: 1}
    else:
        rearranged_state = three_peg_state
        rearranged_names = ['A', 'B', 'C']
        peg_map = {0: 0, 1: 1, 2: 2}
    
    try:
        moves, final_tower_state = solve_hanoi_from_image(
            rearranged_state,
            source=rearranged_names[0],
            destination=rearranged_names[2],
            auxiliary=rearranged_names[1]
        )
    except Exception as e:
        raise UnsolvableStateError(f"Standard 3-peg solver failed: {str(e)}")
    
    final_state = [[], [], [], [], []]
    
    for peg_name in final_tower_state.pegs:
        if peg_name == 'A':
            final_state[0] = final_tower_state.pegs[peg_name]
        elif peg_name == 'B':
            final_state[1] = final_tower_state.pegs[peg_name]
        elif peg_name == 'C':
            final_state[2] = final_tower_state.pegs[peg_name]
    
    return moves, final_state


# ==========================================
# Main Solver Function
# ==========================================

def solve_hanoi(initial_state: List[List[int]], destination_peg: int = 2) -> List[Move]:
    """
    Master solver for Tower of Hanoi.
    
    Args:
        initial_state: List of 5 lists representing [Peg A, Peg B, Peg C, Queue Peg, Ground]
        destination_peg: Index of target peg (0=A, 1=B, 2=C). Default: 2 (C)
    
    Returns:
        List of Move objects representing the solution
    
    Default Configuration:
        - duplicate_strategy: 'discard' (first occurrence only)
        - ground_strategy: 'greedy_3' (minimize violations on 3 pegs)
        - illegal_resolution: 'bfs_3peg' (optimal 3-peg pathfinding)
    """
    
    # Validate input
    if not isinstance(initial_state, list) or len(initial_state) != 5:
        raise InvalidStateError("initial_state must be a list of 5 lists [A, B, C, Queue, Ground]")
    
    for i, peg in enumerate(initial_state):
        if not isinstance(peg, list):
            raise InvalidStateError(f"Peg at index {i} must be a list")
    
    if destination_peg not in [0, 1, 2]:
        raise InvalidFlagCombinationError("destination_peg must be 0 (A), 1 (B), or 2 (C)")
    
    # Fixed configuration
    duplicate_strategy = 'discard'
    ground_strategy = 'greedy_3'
    illegal_resolution = 'bfs_3peg'
    
    all_moves = []
    
    # Step 1: Preprocess (discard duplicates)
    current_state, disk_info = preprocess_state(initial_state, duplicate_strategy)
    
    # Step 2: Resolve ground disks
    if current_state[4]:
        ground_moves, current_state = resolve_ground_disks(current_state, ground_strategy)
        all_moves.extend(ground_moves)
    
    # Step 3: Resolve illegal stacking
    if not check_legality(current_state):
        illegal_moves, current_state = resolve_illegal_state(current_state, illegal_resolution)
        all_moves.extend(illegal_moves)
    
    # Step 4: Verify legal state
    if not check_legality(current_state):
        raise UnsolvableStateError("After preprocessing and resolution, state is still illegal.")
    
    # Step 5: Solve to destination
    solution_moves, final_state = solve_standard_3peg(current_state, destination_peg)
    all_moves.extend(solution_moves)
    
    num_disks = len(disk_info.get('mapping', {}))
    
    if final_state[destination_peg] and len(final_state[destination_peg]) == num_disks:
        return all_moves
    else:
        raise UnsolvableStateError("Solution incomplete")


# ==========================================
# Main Test
# ==========================================

if __name__ == "__main__":
    print("Tower of Hanoi Master Solver - Standalone Version")
    print("Defaults: discard duplicates, greedy_3, bfs_3peg\n")
    
    # Test case
    test_state = [
        [3, 2, 1],  # Peg A
        [],         # Peg B
        [],         # Peg C
        [],         # Queue
        []          # Ground
    ]
    
    print(f"Solving state: {test_state}")
    print(f"Destination: Peg C (index 2)\n")
    
    try:
        moves = solve_hanoi(test_state, destination_peg=2)
        print(f"✓ Solved in {len(moves)} moves\n")
        
        for i, move in enumerate(moves[:10], 1):
            print(f"{i}. {move}")
        
        if len(moves) > 10:
            print(f"... ({len(moves) - 10} more moves)")
    except Exception as e:
        print(f"✗ Error: {e}")
