"""
Tower of Hanoi - Dynamic Programming Solution
Uses memoization to store and reuse previously computed move sequences.
"""

def hanoi_dp(n, source='A', destination='C', auxiliary='B', memo=None):
    """
    Solve Tower of Hanoi using dynamic programming with memoization.
    
    Args:
        n: Number of disks
        source: Source rod (e.g., 'A')
        destination: Destination rod (e.g., 'C')
        auxiliary: Auxiliary rod (e.g., 'B')
        memo: Dictionary to store memoized results
    
    Returns:
        List of moves
    """
    if memo is None:
        memo = {}
    
    # Create a key for memoization
    key = (n, source, destination, auxiliary)
    
    # Check if already computed
    if key in memo:
        return memo[key]
    
    moves = []
    
    if n == 1:
        move = (1, source, destination)
        moves.append(move)
    else:
        # Move n-1 disks from source to auxiliary
        moves1 = hanoi_dp(n - 1, source, auxiliary, destination, memo)
        moves.extend(moves1)
        
        # Move the largest disk from source to destination
        move = (n, source, destination)
        moves.append(move)
        
        # Move n-1 disks from auxiliary to destination
        moves2 = hanoi_dp(n - 1, auxiliary, destination, source, memo)
        moves.extend(moves2)
    
    # Store in memo
    memo[key] = moves
    return moves


def hanoi_dp_bottom_up(n, source='A', destination='C', auxiliary='B'):
    """
    Bottom-up dynamic programming approach.
    Builds solutions from 1 disk up to n disks.
    """
    # dp[i] will store the move sequence for i disks
    dp = {}
    
    # Base case: 1 disk
    dp[1] = [(1, source, destination)]
    
    # Build up solutions for 2 to n disks
    for i in range(2, n + 1):
        moves = []
        
        # Simulate moving i-1 disks from source to auxiliary
        for disk, src, dest in dp[i - 1]:
            # Remap the moves
            new_src = src
            new_dest = dest
            if src == source:
                new_src = source
            elif src == destination:
                new_src = auxiliary
            else:
                new_src = destination
                
            if dest == source:
                new_dest = source
            elif dest == destination:
                new_dest = auxiliary
            else:
                new_dest = destination
            
            moves.append((disk, new_src, new_dest))
        
        # Move disk i from source to destination
        moves.append((i, source, destination))
        
        # Simulate moving i-1 disks from auxiliary to destination
        for disk, src, dest in dp[i - 1]:
            # Remap the moves
            new_src = src
            new_dest = dest
            if src == source:
                new_src = auxiliary
            elif src == destination:
                new_src = destination
            else:
                new_src = source
                
            if dest == source:
                new_dest = auxiliary
            elif dest == destination:
                new_dest = destination
            else:
                new_dest = source
            
            moves.append((disk, new_src, new_dest))
        
        dp[i] = moves
    
    return dp[n]


if __name__ == "__main__":
    # Example usage
    num_disks = 5
    print(f"Solving Tower of Hanoi for {num_disks} disks with Dynamic Programming")
    
    moves = hanoi_dp(num_disks)
    
    for i in moves:
        print(i)
