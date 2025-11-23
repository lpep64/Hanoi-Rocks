"""
Tower of Hanoi - Recursive Solution
Classic recursive implementation of the Tower of Hanoi puzzle.
"""

def hanoi_recursive(n, source, destination, auxiliary, moves=None):
    """
    Solve Tower of Hanoi using recursion.
    
    Args:
        n: Number of disks
        source: Source rod (e.g., 'A')
        destination: Destination rod (e.g., 'C')
        auxiliary: Auxiliary rod (e.g., 'B')
        moves: List to store moves (optional)
    
    Returns:
        List of moves if moves list provided, otherwise None
    """
    if moves is None:
        moves = []
    
    if n == 1:
        moves.append((1, source, destination))
        return moves
    
    # Move n-1 disks from source to auxiliary using destination
    hanoi_recursive(n - 1, source, auxiliary, destination, moves)
    
    # Move the largest disk from source to destination
    moves.append((n, source, destination))
    
    # Move n-1 disks from auxiliary to destination using source
    hanoi_recursive(n - 1, auxiliary, destination, source, moves)
    
    return moves


def count_moves(n):
    """
    Calculate the number of moves required for n disks.
    Formula: 2^n - 1
    """
    return 2**n - 1


if __name__ == "__main__":
    # Example usage
    num_disks = 5
    print(f"Solving Tower of Hanoi for {num_disks} disks with Recursive")
    
    moves = hanoi_recursive(num_disks, 'A', 'C', 'B')
    
    for i in moves:
        print(i)
