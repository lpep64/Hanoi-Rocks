"""
Tower of Hanoi - Height Tracking Solution
Based on dynamic programming approach with detailed state tracking for each move.
Tracks disk position, initial height, and destination height.
"""

class Move:
    """
    Represents a single move in the Tower of Hanoi puzzle with state information.
    """
    def __init__(self, disk, initial_peg, initial_height, destination_peg, destination_height):
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
    """
    def __init__(self, n, source='A', destination='C', auxiliary='B'):
        """
        Initialize the tower state with n disks on the source peg.
        
        Args:
            n: Number of disks
            source: Source peg
            destination: Destination peg
            auxiliary: Auxiliary peg
        """
        self.pegs = {source: list(range(n, 0, -1)), destination: [], auxiliary: []}
        self.source = source
        self.destination = destination
        self.auxiliary = auxiliary
    
    def get_height(self, peg):
        """Get the current height (number of disks) on a peg."""
        return len(self.pegs[peg])
    
    def get_top_disk(self, peg):
        """Get the top disk on a peg, or None if empty."""
        return self.pegs[peg][-1] if self.pegs[peg] else None
    
    def move_disk(self, from_peg, to_peg):
        """
        Move the top disk from one peg to another and return a Move object.
        
        Returns:
            Move object with complete state information
        """
        if not self.pegs[from_peg]:
            raise ValueError(f"Cannot move from empty peg {from_peg}")
        
        disk = self.pegs[from_peg].pop()
        initial_height = len(self.pegs[from_peg])  # Height before removal
        
        self.pegs[to_peg].append(disk)
        destination_height = len(self.pegs[to_peg]) - 1  # Height after addition (0-indexed)
        
        return Move(disk, from_peg, initial_height, to_peg, destination_height)
    
    def copy(self):
        """Create a deep copy of the current state."""
        new_state = TowerState.__new__(TowerState)
        new_state.pegs = {peg: disks[:] for peg, disks in self.pegs.items()}
        new_state.source = self.source
        new_state.destination = self.destination
        new_state.auxiliary = self.auxiliary
        return new_state
    
    def __repr__(self):
        return f"TowerState({self.pegs})"


def hanoi_state_tracking(n, source='A', destination='C', auxiliary='B', memo=None):
    """
    Solve Tower of Hanoi with state tracking using dynamic programming.
    
    Args:
        n: Number of disks
        source: Source rod
        destination: Destination rod
        auxiliary: Auxiliary rod
        memo: Dictionary to store memoized results
    
    Returns:
        List of Move objects with complete state information
    """
    if memo is None:
        memo = {}
    
    # Create a key for memoization
    key = (n, source, destination, auxiliary)
    
    # Check if already computed
    if key in memo:
        return memo[key]
    
    # Initialize state tracker
    state = TowerState(n, source, destination, auxiliary)
    moves = []
    
    def solve(num_disks, src, dest, aux, current_state):
        """Recursive helper function that tracks state."""
        if num_disks == 1:
            move = current_state.move_disk(src, dest)
            moves.append(move)
        else:
            # Move n-1 disks from source to auxiliary
            solve(num_disks - 1, src, aux, dest, current_state)
            
            # Move the largest disk from source to destination
            move = current_state.move_disk(src, dest)
            moves.append(move)
            
            # Move n-1 disks from auxiliary to destination
            solve(num_disks - 1, aux, dest, src, current_state)
    
    solve(n, source, destination, auxiliary, state)
    
    # Store in memo
    memo[key] = moves
    return moves


def hanoi_state_tracking_iterative(n, source='A', destination='C', auxiliary='B'):
    """
    Iterative solution with state tracking.
    Uses an explicit stack to avoid recursion while tracking state.
    
    Args:
        n: Number of disks
        source: Source rod
        destination: Destination rod
        auxiliary: Auxiliary rod
    
    Returns:
        List of Move objects with complete state information
    """
    state = TowerState(n, source, destination, auxiliary)
    moves = []
    
    # Stack holds tuples of (n, source, dest, aux, is_processing)
    stack = [(n, source, destination, auxiliary, False)]
    
    while stack:
        num_disks, src, dest, aux, is_processing = stack.pop()
        
        if num_disks == 1:
            move = state.move_disk(src, dest)
            moves.append(move)
        else:
            if not is_processing:
                # Push operations in reverse order
                # Third: Move n-1 disks from auxiliary to destination
                stack.append((num_disks - 1, aux, dest, src, False))
                # Second: Move the largest disk
                stack.append((1, src, dest, aux, False))
                # First: Move n-1 disks from source to auxiliary
                stack.append((num_disks - 1, src, aux, dest, False))
    
    return moves

if __name__ == "__main__":
    # Example usage
    num_disks = 5
    print(f"Solving Tower of Hanoi for {num_disks} disks with Height Tracking")
    
    moves = hanoi_state_tracking(num_disks)
    
    for i in moves:
        print(i)