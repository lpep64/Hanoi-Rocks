"""
Tower of Hanoi - Iterative Solution
Standard iterative implementation using stack-based approach.
"""

def hanoi_iterative(n, source='A', destination='C', auxiliary='B'):
    """
    Solve Tower of Hanoi using iterative approach with explicit stack.
    
    Args:
        n: Number of disks
        source: Source rod (e.g., 'A')
        destination: Destination rod (e.g., 'C')
        auxiliary: Auxiliary rod (e.g., 'B')
    
    Returns:
        List of moves
    """
    moves = []
    stack = [(n, source, destination, auxiliary, False)]
    
    while stack:
        disks, src, dest, aux, processed = stack.pop()
        
        if disks == 1:
            moves.append((1, src, dest))
        elif not processed:
            # Push operations in reverse order
            # Step 3: Move n-1 disks from auxiliary to destination
            stack.append((disks - 1, aux, dest, src, False))
            
            # Step 2: Move disk n from source to destination
            stack.append((1, src, dest, aux, True))
            move_data = (disks, src, dest)
            
            # Step 1: Move n-1 disks from source to auxiliary
            stack.append((disks - 1, src, aux, dest, False))
        else:
            # This is the middle disk move for n > 1
            moves.append((disks, src, dest))
    
    return moves

def move_disk(pegs, from_peg, to_peg, moves):
    """
    Move a disk between two pegs following the rules.
    """
    if not pegs[from_peg] and not pegs[to_peg]:
        return
    
    if not pegs[from_peg]:
        from_peg, to_peg = to_peg, from_peg
    elif not pegs[to_peg]:
        pass
    elif pegs[from_peg][-1] > pegs[to_peg][-1]:
        from_peg, to_peg = to_peg, from_peg
    
    disk = pegs[from_peg].pop()
    pegs[to_peg].append(disk)
    moves.append((disk, from_peg, to_peg))


if __name__ == "__main__":
    # Example usage
    num_disks = 5
    print(f"Solving Tower of Hanoi for {num_disks} disks with Iterative")
    
    moves = hanoi_iterative(num_disks)
    
    for i in moves:
        print(i)