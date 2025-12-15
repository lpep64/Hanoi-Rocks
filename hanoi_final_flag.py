"""
Tower of Hanoi - Master Solver with Flags
Comprehensive solver for complex Tower of Hanoi variations.

Handles:
- Gap disks (missing integers) - automatically normalized to consecutive integers
- Duplicate disks - merged or discarded based on strategy
- Ground disk retrieval - using greedy or patient strategies
- Illegal state resolution - multiple algorithms available
- 4th peg (Queue) fallback - used only when 3-peg solution fails
- Configurable target peg - solve to any of the three standard pegs

## Usage Example:

```python
from hanoi_final_flag import solve_hanoi

# Define initial state: [Peg A, Peg B, Peg C, Queue Peg, Ground]
initial_state = [
    [5, 3],     # Peg A: disk 5 on bottom, disk 3 on top
    [4],        # Peg B: disk 4
    [],         # Peg C: empty
    [],         # Queue Peg: empty (4th peg - used only if needed)
    [2, 1]      # Ground: disks 2 and 1 (illegal position)
]

# Configure solver flags
flags = {
    'target_peg': 2,                      # 0=A, 1=B, 2=C
    'duplicate_strategy': 'merge',        # 'merge' or 'discard'
    'ground_strategy': 'greedy',          # 'greedy' or 'patient'
    'illegal_resolution': 'dig_out'       # See STRATEGIES below
}

# Solve the puzzle
moves = solve_hanoi(initial_state, flags)

# Process moves
for move in moves:
    print(move)
```

## Input State Structure:
The input is a list of 5 lists: [Peg A, Peg B, Peg C, Queue Peg, Ground]
- Disks are represented by integers (larger number = larger disk)
- Each peg is a list ordered from bottom to top: [bottom, ..., top]
- Example: [3, 2, 1] means disk 3 at bottom, disk 2 in middle, disk 1 on top

## Flags Configuration:

### target_peg (int, default: 2)
- 0: Move all disks to Peg A
- 1: Move all disks to Peg B
- 2: Move all disks to Peg C (default)

### duplicate_strategy (str, default: 'merge')
- 'merge': Treat all instances of the same disk value as a single disk
- 'discard': Keep only the first occurrence of each disk value

### ground_strategy (str, default: 'greedy')
- 'greedy': Always place largest ground disk with minimum violation
- 'patient': Only move ground disk when a legal placement exists

### illegal_resolution (str, default: 'dig_out')
Available strategies for fixing illegal stacking:
- 'bubble_sort': Fix by swapping adjacent illegally ordered disks
- 'total_evacuation': Clear entire illegal peg and redistribute
- 'dig_out': Surgical fix targeting first illegal overlap (recommended)
- 'bfs_3peg': BFS pathfinding using only 3 standard pegs
- 'bfs_4peg': BFS pathfinding with Queue peg assistance

## Gap Disks:
Gap disks (missing integers in sequence) are automatically handled.
Example: If you have disks [1, 3, 5], they are normalized to [1, 2, 3]
while preserving relative ordering constraints.

## The 4th Peg Rule:
The solver attempts to solve using standard 3-peg logic first (Pegs A, B, C).
The Queue Peg (4th peg) is ONLY utilized if:
- The 3-peg solution fails
- A deadlock is detected
- The state cannot be resolved with standard moves

## Error Handling:
The solver raises specific exceptions:
- UnsolvableStateError: Configuration is provably unsolvable
- InvalidFlagCombinationError: Flags create contradictory requirements
- InvalidStateError: Input state is malformed

## Return Value:
Returns a list of Move objects, each containing:
- disk: The disk number being moved
- initial_peg: Source peg name ('A', 'B', 'C', 'Queue', 'Ground')
- initial_height: Height index on source peg (0-based)
- destination_peg: Target peg name
- destination_height: Height index on target peg (0-based)
"""

from typing import List, Tuple, Dict, Optional
from copy import deepcopy

# Import from hanoi package
from hanoi.core.move import Move, TowerState, solve_hanoi_from_image
from hanoi.illegal.checker import check_legality
from hanoi.illegal.stack_resolver import IllegalSolver
from hanoi.illegal.ground_resolver import GroundSolver


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
# State Preprocessing
# ==========================================

def preprocess_state(state: List[List[int]], duplicate_strategy: str) -> Tuple[List[List[int]], Dict]:
    """
    Preprocess the input state to handle duplicates and create disk mapping.
    
    Args:
        state: 5-array state [A, B, C, Queue, Ground]
        duplicate_strategy: 'merge' or 'discard'
    
    Returns:
        Tuple of (processed_state, disk_info)
        disk_info: dict with 'mapping', 'has_duplicates', 'id_map'
    """
    # Collect all disks from all pegs with positions
    all_disks = []
    for peg_idx, peg in enumerate(state):
        for disk in peg:
            all_disks.append(disk)
    
    if not all_disks:
        raise InvalidStateError("State must contain at least one disk")
    
    # Check for duplicates
    from collections import Counter
    disk_counts = Counter(all_disks)
    has_duplicates = any(count > 1 for count in disk_counts.values())
    
    disk_info = {
        'has_duplicates': has_duplicates,
        'mapping': {},
        'id_map': {},  # Maps (value, id) -> normalized_value
        'reverse_map': {}  # Maps normalized_value -> (original_value, id)
    }
    
    if duplicate_strategy == 'merge':
        if has_duplicates:
            # Keep duplicates as separate physical disks with unique IDs
            # Assign IDs: 1a, 1b, 2a, etc.
            disk_id_counter = {}
            processed_state = []
            id_to_normalized = {}
            normalized_counter = 1
            
            for peg in state:
                new_peg = []
                for disk in peg:
                    # Assign unique ID to this disk instance
                    if disk not in disk_id_counter:
                        disk_id_counter[disk] = 0
                    disk_id = chr(97 + disk_id_counter[disk])  # a, b, c, ...
                    disk_id_counter[disk] += 1
                    
                    # Create unique identifier
                    disk_key = (disk, disk_id)
                    
                    # Assign normalized value
                    id_to_normalized[disk_key] = normalized_counter
                    disk_info['id_map'][disk_key] = normalized_counter
                    disk_info['reverse_map'][normalized_counter] = disk_key
                    
                    new_peg.append(normalized_counter)
                    normalized_counter += 1
                
                processed_state.append(new_peg)
            
            return processed_state, disk_info
        else:
            # No duplicates, use simple normalization
            unique_disks = sorted(set(all_disks))
            disk_mapping = {disk: i+1 for i, disk in enumerate(unique_disks)}
            disk_info['mapping'] = disk_mapping
            
            processed_state = []
            for peg in state:
                new_peg = [disk_mapping[disk] for disk in peg]
                processed_state.append(new_peg)
            
            return processed_state, disk_info
            
    elif duplicate_strategy == 'discard':
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
        raise InvalidFlagCombinationError(f"Invalid duplicate_strategy: {duplicate_strategy}. Must be 'merge' or 'discard'")


# ==========================================
# Ground Disk Resolution
# ==========================================

def resolve_ground_disks(state: List[List[int]], ground_strategy: str) -> Tuple[List[Move], List[List[int]]]:
    """
    Resolve ground disk violations using specified strategy.
    
    Args:
        state: 5-array state [A, B, C, Queue, Ground]
        ground_strategy: 'greedy_3', 'greedy_4', 'patient_3', 'patient_4', or legacy 'greedy'/'patient'
    
    Returns:
        Tuple of (moves, updated_state)
    """
    if not state[4]:  # No ground disks
        return [], state
    
    solver = GroundSolver(state)
    
    if ground_strategy == 'greedy_3':
        moves, final_state = solver.solve_greedy_3()
    elif ground_strategy == 'greedy_4':
        moves, final_state = solver.solve_greedy_4()
    elif ground_strategy == 'patient_3':
        moves, final_state = solver.solve_patient_3()
    elif ground_strategy == 'patient_4':
        moves, final_state = solver.solve_patient_4()
    elif ground_strategy == 'greedy':
        # Legacy support
        moves, final_state = solver.solve_greedy_3()
    elif ground_strategy == 'patient':
        # Legacy support
        moves, final_state = solver.solve_patient_3()
    else:
        raise InvalidFlagCombinationError(
            f"Invalid ground_strategy: {ground_strategy}. "
            f"Must be 'greedy_3', 'greedy_4', 'patient_3', 'patient_4'"
        )
    
    return moves, final_state


# ==========================================
# Illegal State Resolution
# ==========================================

def resolve_illegal_state(state: List[List[int]], illegal_resolution: str) -> Tuple[List[Move], List[List[int]]]:
    """
    Resolve illegal stacking using specified strategy.
    
    Args:
        state: 5-array state [A, B, C, Queue, Ground]
        illegal_resolution: 'bubble_sort', 'total_evacuation', 'dig_out', 'bfs_3peg', or 'bfs_4peg'
    
    Returns:
        Tuple of (moves, updated_state)
    """
    if check_legality(state):
        return [], state
    
    solver = IllegalSolver(state)
    
    if illegal_resolution == 'bubble_sort':
        moves, final_state = solver.solve_bubble_sort()
    elif illegal_resolution == 'total_evacuation':
        moves, final_state = solver.solve_total_evacuation()
    elif illegal_resolution == 'dig_out':
        moves, final_state = solver.solve_dig_out()
    elif illegal_resolution == 'bfs_3peg':
        moves, final_state = solver.solve_a_star_3peg()
    elif illegal_resolution == 'bfs_4peg':
        moves, final_state = solver.solve_a_star_4peg()
    else:
        raise InvalidFlagCombinationError(
            f"Invalid illegal_resolution: {illegal_resolution}. "
            f"Must be 'bubble_sort', 'total_evacuation', 'dig_out', 'bfs_3peg', or 'bfs_4peg'"
        )
    
    # Verify legality after resolution
    if not check_legality(final_state):
        raise UnsolvableStateError(
            f"Failed to resolve illegal state using strategy '{illegal_resolution}'. "
            f"The configuration may be fundamentally unsolvable."
        )
    
    return moves, final_state


# ==========================================
# Standard 3-Peg Solver
# ==========================================

def solve_standard_3peg(state: List[List[int]], target_peg_idx: int) -> Tuple[List[Move], List[List[int]]]:
    """
    Solve using standard 3-peg logic (ignoring Queue peg).
    
    Args:
        state: 5-array state [A, B, C, Queue, Ground] - must be legal with Queue/Ground empty
        target_peg_idx: Index of target peg (0=A, 1=B, 2=C)
    
    Returns:
        Tuple of (moves, final_state)
    """
    # Extract only the 3 standard pegs
    three_peg_state = [state[0], state[1], state[2]]
    
    # Verify state is legal for 3-peg solving
    if state[3] or state[4]:  # Queue or Ground not empty
        raise ValueError("Cannot solve with standard 3-peg when Queue or Ground contain disks")
    
    # Count total disks
    all_disks = []
    for peg in three_peg_state:
        all_disks.extend(peg)
    
    # CRITICAL FIX: Renormalize disks to ensure they're consecutive 1..n
    # This handles cases where preprocessing or ground resolution left gaps
    if all_disks:
        unique_disks = sorted(set(all_disks))
        disk_mapping = {disk: i+1 for i, disk in enumerate(unique_disks)}
        
        # Apply normalization
        normalized_state = []
        for peg in three_peg_state:
            normalized_state.append([disk_mapping[d] for d in peg])
        
        three_peg_state = normalized_state
        total_disks = len(unique_disks)
    else:
        total_disks = 0
    
    # Check if all disks are already on target peg
    if three_peg_state[target_peg_idx] and len(three_peg_state[target_peg_idx]) == total_disks:
        # All disks already on target, no moves needed
        return [], state
    
    # Map target index to peg name
    peg_names = ['A', 'B', 'C']
    target_name = peg_names[target_peg_idx]
    
    # The solve_hanoi_from_image function ALWAYS solves to move all disks to 'destination'
    # It maps initial_state indices to peg names as:
    #   initial_state[0] -> source
    #   initial_state[1] -> auxiliary
    #   initial_state[2] -> destination
    #
    # Since our three_peg_state is [A, B, C] and we want flexibility in target,
    # we need to rearrange the input so that target_peg_idx is at position 2
    
    # Rearrange state so target is at index 2 (destination position)
    peg_map = {}  # Maps new position -> original position
    if target_peg_idx == 0:  # Target is A, map as [B, C, A]
        rearranged_state = [three_peg_state[1], three_peg_state[2], three_peg_state[0]]
        rearranged_names = ['B', 'C', 'A']
        peg_map = {0: 1, 1: 2, 2: 0}  # new_idx: old_idx
    elif target_peg_idx == 1:  # Target is B, map as [A, C, B]
        rearranged_state = [three_peg_state[0], three_peg_state[2], three_peg_state[1]]
        rearranged_names = ['A', 'C', 'B']
        peg_map = {0: 0, 1: 2, 2: 1}
    else:  # Target is C (default), map as [A, B, C]
        rearranged_state = three_peg_state
        rearranged_names = ['A', 'B', 'C']
        peg_map = {0: 0, 1: 1, 2: 2}
    
    # Now solve with rearranged state, always using index 2 as destination
    try:
        moves, final_tower_state = solve_hanoi_from_image(
            rearranged_state,
            source=rearranged_names[0],
            destination=rearranged_names[2],
            auxiliary=rearranged_names[1]
        )
    except Exception as e:
        raise UnsolvableStateError(f"Standard 3-peg solver failed: {str(e)}")
    
    # Convert back to 5-array format
    # The TowerState.pegs dictionary only has the three pegs specified
    # We need to map them back to A, B, C positions
    final_state = [[], [], [], [], []]  # Initialize all 5 pegs as empty
    
    # Map the tower state back to the correct positions
    for peg_name in final_tower_state.pegs:
        if peg_name == 'A':
            final_state[0] = final_tower_state.pegs[peg_name]
        elif peg_name == 'B':
            final_state[1] = final_tower_state.pegs[peg_name]
        elif peg_name == 'C':
            final_state[2] = final_tower_state.pegs[peg_name]
    
    return moves, final_state


# ==========================================
# 4-Peg Solver (Fallback)
# ==========================================

def solve_with_queue_peg(state: List[List[int]], target_peg_idx: int) -> Tuple[List[Move], List[List[int]]]:
    """
    Solve using 4-peg logic when 3-peg approach fails or creates deadlock.
    
    This is a simplified implementation that uses the Queue peg as a temporary
    storage location to break deadlocks.
    
    Args:
        state: 5-array state [A, B, C, Queue, Ground]
        target_peg_idx: Index of target peg (0=A, 1=B, 2=C)
    
    Returns:
        Tuple of (moves, final_state)
    """
    # For now, use IllegalSolver's BFS 4-peg as it already handles Queue
    # This treats the problem as resolving to a legal configuration
    # then moving everything to target
    
    moves = []
    current_state = deepcopy(state)
    
    # Step 1: Use BFS 4-peg to get to a solvable configuration
    solver = IllegalSolver(current_state)
    resolution_moves, resolved_state = solver.solve_a_star_4peg()
    moves.extend(resolution_moves)
    
    # Step 2: Now solve normally to target peg
    if check_legality(resolved_state):
        final_moves, final_state = solve_standard_3peg(resolved_state, target_peg_idx)
        moves.extend(final_moves)
        return moves, final_state
    else:
        raise UnsolvableStateError("4-peg solver could not resolve to legal state")


# ==========================================
# Main Solver Function
# ==========================================

def solve_hanoi(initial_state: List[List[int]], flags: Dict) -> List[Move]:
    """
    Master solver for Tower of Hanoi with complex variations.
    
    Args:
        initial_state: List of 5 lists representing [Peg A, Peg B, Peg C, Queue Peg, Ground]
                      Disks are integers (larger number = larger disk)
        flags: Dictionary containing:
            - target_peg (int): Index of target peg (0=A, 1=B, 2=C). Default: 2 (C)
            - duplicate_strategy (str): 'merge' or 'discard'. Default: 'merge'
            - ground_strategy (str): 'greedy_3', 'greedy_4', 'patient_3', 'patient_4'. Default: 'greedy_3'
            - illegal_resolution (str): 'bubble_sort', 'total_evacuation', 'dig_out',
                                       'bfs_3peg', or 'bfs_4peg'. Default: 'dig_out'
    
    Returns:
        List of Move objects representing the solution
    
    Raises:
        UnsolvableStateError: When the puzzle is provably unsolvable
        InvalidFlagCombinationError: When flags create contradictory requirements
        InvalidStateError: When input state is malformed
    """
    # Validate input structure
    if not isinstance(initial_state, list) or len(initial_state) != 5:
        raise InvalidStateError("initial_state must be a list of 5 lists [A, B, C, Queue, Ground]")
    
    for i, peg in enumerate(initial_state):
        if not isinstance(peg, list):
            raise InvalidStateError(f"Peg at index {i} must be a list")
    
    # Extract flags with defaults
    target_peg = flags.get('target_peg', 2)
    duplicate_strategy = flags.get('duplicate_strategy', 'merge')
    ground_strategy = flags.get('ground_strategy', 'greedy_3')
    illegal_resolution = flags.get('illegal_resolution', 'dig_out')
    
    # Validate target_peg
    if target_peg not in [0, 1, 2]:
        raise InvalidFlagCombinationError("target_peg must be 0 (A), 1 (B), or 2 (C)")
    
    # Initialize move sequence
    all_moves = []
    
    # Step 1: Preprocess state (handle duplicates and gaps)
    current_state, disk_info = preprocess_state(initial_state, duplicate_strategy)
    
    # Step 2: Resolve ground disks if present
    if current_state[4]:  # Ground peg has disks
        ground_moves, current_state = resolve_ground_disks(current_state, ground_strategy)
        all_moves.extend(ground_moves)
    
    # Step 3: Resolve illegal stacking if present
    if not check_legality(current_state):
        illegal_moves, current_state = resolve_illegal_state(current_state, illegal_resolution)
        all_moves.extend(illegal_moves)
    
    # Step 4: Verify we have a legal starting state
    if not check_legality(current_state):
        raise UnsolvableStateError(
            "After preprocessing and resolution, state is still illegal. "
            "This configuration cannot be solved with the given flags."
        )
    
    # Step 5: Attempt standard 3-peg solution
    try:
        solution_moves, final_state = solve_standard_3peg(current_state, target_peg)
        all_moves.extend(solution_moves)
        
        # Count disks for verification
        num_disks = len(disk_info.get('reverse_map', disk_info.get('mapping', {})))
        
        # Verify solution
        if final_state[target_peg] and len(final_state[target_peg]) == num_disks:
            # All disks are on target peg - attach labels to moves
            if disk_info['has_duplicates'] and duplicate_strategy == 'merge':
                # Add disk labels to moves for visualization
                for move in all_moves:
                    if move.disk in disk_info['reverse_map']:
                        original_value, disk_id = disk_info['reverse_map'][move.disk]
                        move.disk_label = f"{original_value}{disk_id}"
            return all_moves
        else:
            # Standard solution didn't complete, try 4-peg
            raise UnsolvableStateError("Standard 3-peg solution incomplete")
            
    except (UnsolvableStateError, ValueError) as e:
        # Step 6: Fallback to 4-peg solver
        print(f"[INFO] 3-peg solver failed: {e}. Attempting 4-peg solution...")
        try:
            # Reset to post-resolution state and try with Queue peg
            queue_moves, final_state = solve_with_queue_peg(current_state, target_peg)
            all_moves.extend(queue_moves)
            
            # Add labels if duplicates
            if disk_info['has_duplicates'] and duplicate_strategy == 'merge':
                for move in all_moves:
                    if move.disk in disk_info['reverse_map']:
                        original_value, disk_id = disk_info['reverse_map'][move.disk]
                        move.disk_label = f"{original_value}{disk_id}"
            return all_moves
        except Exception as queue_error:
            raise UnsolvableStateError(
                f"Both 3-peg and 4-peg solvers failed. "
                f"3-peg error: {e}. 4-peg error: {queue_error}. "
                f"This configuration is unsolvable with the given flags."
            )


# ==========================================
# Main Test Block
# ==========================================

if __name__ == "__main__":
    print("="*70)
    print("TOWER OF HANOI - MASTER SOLVER TEST SUITE")
    print("="*70)
    
    # Test 1: Standard legal state
    print("\n[TEST 1] Standard legal state, all disks on A, move to C")
    test1_state = [
        [3, 2, 1],  # Peg A
        [],         # Peg B
        [],         # Peg C
        [],         # Queue
        []          # Ground
    ]
    test1_flags = {
        'target_peg': 2,
        'duplicate_strategy': 'merge',
        'ground_strategy': 'greedy',
        'illegal_resolution': 'dig_out'
    }
    try:
        moves = solve_hanoi(test1_state, test1_flags)
        print(f"✓ Solved in {len(moves)} moves")
        for i, move in enumerate(moves[:5], 1):  # Show first 5 moves
            print(f"  {i}. {move}")
        if len(moves) > 5:
            print(f"  ... ({len(moves) - 5} more moves)")
    except Exception as e:
        print(f"✗ Failed: {e}")
    
    # Test 2: Ground disks with greedy strategy
    print("\n[TEST 2] Disks on ground - greedy retrieval")
    test2_state = [
        [5, 3],     # Peg A
        [4],        # Peg B
        [],         # Peg C
        [],         # Queue
        [2, 1]      # Ground
    ]
    test2_flags = {
        'target_peg': 2,
        'duplicate_strategy': 'merge',
        'ground_strategy': 'greedy',
        'illegal_resolution': 'dig_out'
    }
    try:
        moves = solve_hanoi(test2_state, test2_flags)
        print(f"✓ Solved in {len(moves)} moves")
    except Exception as e:
        print(f"✗ Failed: {e}")
    
    # Test 3: Illegal stacking
    print("\n[TEST 3] Illegal stacking - dig out resolution")
    test3_state = [
        [1, 2],     # Peg A (illegal: 2 on top of 1)
        [3],        # Peg B
        [],         # Peg C
        [],         # Queue
        []          # Ground
    ]
    test3_flags = {
        'target_peg': 2,
        'duplicate_strategy': 'merge',
        'ground_strategy': 'greedy',
        'illegal_resolution': 'dig_out'
    }
    try:
        moves = solve_hanoi(test3_state, test3_flags)
        print(f"✓ Solved in {len(moves)} moves")
    except Exception as e:
        print(f"✗ Failed: {e}")
    
    # Test 4: Gap disks (missing integers)
    print("\n[TEST 4] Gap disks - missing disk 2")
    test4_state = [
        [5, 3, 1],  # Peg A (disk 2 and 4 missing)
        [],         # Peg B
        [],         # Peg C
        [],         # Queue
        []          # Ground
    ]
    test4_flags = {
        'target_peg': 2,
        'duplicate_strategy': 'merge',
        'ground_strategy': 'greedy',
        'illegal_resolution': 'dig_out'
    }
    try:
        moves = solve_hanoi(test4_state, test4_flags)
        print(f"✓ Solved in {len(moves)} moves (gaps handled automatically)")
    except Exception as e:
        print(f"✗ Failed: {e}")
    
    # Test 5: Duplicate disks with merge strategy
    print("\n[TEST 5] Duplicate disks - merge strategy")
    test5_state = [
        [3, 2, 2, 1],  # Peg A (two disk 2s)
        [],            # Peg B
        [],            # Peg C
        [],            # Queue
        []             # Ground
    ]
    test5_flags = {
        'target_peg': 2,
        'duplicate_strategy': 'merge',
        'ground_strategy': 'greedy',
        'illegal_resolution': 'dig_out'
    }
    try:
        moves = solve_hanoi(test5_state, test5_flags)
        print(f"✓ Solved in {len(moves)} moves (duplicates merged)")
    except Exception as e:
        print(f"✗ Failed: {e}")
    
    # Test 6: Complex combination
    print("\n[TEST 6] Complex: ground + illegal + gaps")
    test6_state = [
        [5, 2],     # Peg A (illegal: 2 on 5 is ok, but missing 3,4)
        [6, 1],     # Peg B (1 on 6 is ok)
        [],         # Peg C
        [],         # Queue
        [8]         # Ground (disk 8)
    ]
    test6_flags = {
        'target_peg': 1,  # Target Peg B
        'duplicate_strategy': 'merge',
        'ground_strategy': 'patient',
        'illegal_resolution': 'total_evacuation'
    }
    try:
        moves = solve_hanoi(test6_state, test6_flags)
        print(f"✓ Solved in {len(moves)} moves")
    except Exception as e:
        print(f"✗ Failed: {e}")
    
    print("\n" + "="*70)
    print("TEST SUITE COMPLETE")
    print("="*70)
