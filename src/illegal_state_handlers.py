"""
Illegal State Handlers

A collection of functions to resolve illegal states in the Tower of Hanoi simulation.
Each handler implements a specific strategy for fixing violations.

The SimulationRunner will call these functions directly based on the experimental configuration.
Each function modifies the environment state in-place and returns the number of "moves"
the resolution cost.

Handler Categories:
1. Ground Handlers: Place disks from ground back onto pegs
2. Duplicate Handlers: Resolve duplicate disk instances
3. Formation Handlers: Fix illegal stacking (large disk on small disk)
"""


def resolve_ground_best_fit(env, disk):
    """
    Best-Fit Ground Handler
    
    Finds the best-fit legal peg for a disk on the ground.
    "Best-fit" means the peg where the top disk is closest in size (but still larger).
    If no perfect fit exists, uses first-available strategy as fallback.
    
    Args:
        env (Environment): The environment instance to modify
        disk (int): The disk ID currently on the ground
    
    Returns:
        int: Number of moves the resolution cost (always 1)
    """
    best_peg = None
    smallest_gap = float('inf')
    
    # Find the peg with the smallest legal gap
    for peg_name in ['A', 'B', 'C']:
        peg_disks = env.pegs[peg_name]
        if not peg_disks:
            # Empty peg is always valid, but gap is large
            gap = env.disk_count + 1 - disk
            if gap < smallest_gap:
                smallest_gap = gap
                best_peg = peg_name
        elif peg_disks[-1] > disk:
            # Top disk is larger than our disk (legal placement)
            gap = peg_disks[-1] - disk
            if gap < smallest_gap:
                smallest_gap = gap
                best_peg = peg_name
    
    # Place the disk on the best-fit peg
    if best_peg:
        env.ground.remove(disk)
        env.pegs[best_peg].append(disk)
    else:
        # This shouldn't happen, but fallback to first available
        env.ground.remove(disk)
        env.pegs['A'].append(disk)
    
    return 1


def resolve_ground_first_available(env, disk):
    """
    First-Available Ground Handler
    
    Finds the first peg (A, B, C) where the disk can be legally placed.
    Checks pegs in order: A, then B, then C.
    
    Args:
        env (Environment): The environment instance to modify
        disk (int): The disk ID currently on the ground
    
    Returns:
        int: Number of moves the resolution cost (always 1)
    """
    # Try each peg in order
    for peg_name in ['A', 'B', 'C']:
        peg_disks = env.pegs[peg_name]
        if not peg_disks or peg_disks[-1] > disk:
            # Legal placement found
            env.ground.remove(disk)
            env.pegs[peg_name].append(disk)
            return 1
    
    # If no legal placement (shouldn't happen), force it onto A
    env.ground.remove(disk)
    env.pegs['A'].append(disk)
    return 1


def resolve_duplicates_keep(env, disk):
    """
    Keep Duplicates Handler
    
    Assumes duplicates are interchangeable and do not need to be removed.
    The system will continue solving with multiple instances of the same disk.
    This is the "permissive" strategy.
    
    Args:
        env (Environment): The environment instance to modify
        disk (int): The duplicate disk ID
    
    Returns:
        int: Number of moves the resolution cost (always 0)
    """
    # No action needed - we allow duplicates
    return 0


def resolve_duplicates_discard(env, disk):
    """
    Discard Duplicates Handler
    
    Finds and removes one instance of the duplicate disk.
    Removes the most accessible instance (top of a peg).
    
    Strategy:
    1. Find all locations of the duplicate disk
    2. Remove the instance that is on top of a peg (most accessible)
    3. If multiple are on top, remove from the first peg found
    
    Args:
        env (Environment): The environment instance to modify
        disk (int): The duplicate disk ID
    
    Returns:
        int: Number of moves the resolution cost (always 1)
    """
    # Find all instances of the duplicate disk
    for peg_name in ['A', 'B', 'C']:
        peg_disks = env.pegs[peg_name]
        if peg_disks and peg_disks[-1] == disk:
            # Found the disk on top of this peg - remove it
            env.pegs[peg_name].pop()
            return 1
    
    # If not on top of any peg, remove the first instance found
    for peg_name in ['A', 'B', 'C']:
        if disk in env.pegs[peg_name]:
            env.pegs[peg_name].remove(disk)
            return 1
    
    return 1


def resolve_formation_deepest(env, details):
    """
    Deepest Formation Handler
    
    Resolves the deepest violation by removing all disks above it, 
    fixing the violation with a swap, then carefully rebuilding.
    
    Args:
        env (Environment): The environment instance to modify
        details (tuple): (peg_name, index) where index is the location of violation
    
    Returns:
        int: Number of moves the resolution cost
    """
    peg_name, violation_index = details
    peg_disks = env.pegs[peg_name]
    
    if len(peg_disks) <= violation_index + 1:
        return 0
    
    # Collect all disks above the violation
    disks_above = []
    while len(peg_disks) > violation_index + 2:
        disks_above.insert(0, peg_disks.pop())
    
    # Now we have just the two violating disks at the top
    # Swap them to fix the violation
    if len(peg_disks) > violation_index + 1:
        peg_disks[violation_index], peg_disks[violation_index + 1] = \
            peg_disks[violation_index + 1], peg_disks[violation_index]
    
    # Put the disks back on top in order
    for disk in disks_above:
        peg_disks.append(disk)
    
    # Cost is proportional to number of disks we had to move
    return len(disks_above) + 2


def resolve_formation_bubble(env, details):
    """
    Bubble Formation Handler
    
    Resolves violations by simply swapping the two disks involved in the violation.
    This is the simplest and fastest approach.
    
    Args:
        env (Environment): The environment instance to modify
        details (tuple): (peg_name, index) where index is the location of violation
    
    Returns:
        int: Number of moves the resolution cost
    """
    peg_name, violation_index = details
    peg_disks = env.pegs[peg_name]
    
    # The violation is: peg_disks[violation_index] < peg_disks[violation_index + 1]
    # (smaller disk below larger disk)
    
    if len(peg_disks) <= violation_index + 1:
        return 0
    
    # Simple fix: just swap them to correct the order
    peg_disks[violation_index], peg_disks[violation_index + 1] = \
        peg_disks[violation_index + 1], peg_disks[violation_index]
    
    # This costs 2 moves conceptually (remove top, remove bottom, place bottom, place top)
    return 2


def resolve_formation_buffer(env, details):
    """
    Buffer Formation Handler
    
    Moves the offending disk directly to a legal peg without using ground.
    This avoids creating ElementOnGround violations.
    
    Args:
        env (Environment): The environment instance to modify
        details (tuple): (peg_name, index) where index is the location of violation
    
    Returns:
        int: Number of moves the resolution cost
    """
    peg_name, violation_index = details
    peg_disks = env.pegs[peg_name]
    
    if len(peg_disks) <= violation_index + 1:
        return 0
    
    # Get the offending disk (larger disk on top of smaller)
    offending_disk = peg_disks.pop(violation_index + 1)
    
    # Try to place it on another peg legally
    placed = False
    for target_peg in ['A', 'B', 'C']:
        if target_peg != peg_name:
            if not env.pegs[target_peg] or env.pegs[target_peg][-1] > offending_disk:
                env.pegs[target_peg].append(offending_disk)
                placed = True
                break
    
    if not placed:
        # No legal place, put it back at the bottom of original peg
        env.pegs[peg_name].insert(0, offending_disk)
    
    return 1
