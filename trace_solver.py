"""
Trace through solver logic with a specific state
"""
from src.hanoi_solver import HanoiSolver

solver = HanoiSolver()

# Simulate the state after move 9: A=[5], B=[4], C=[3, 2, 1]
# We're calling get_next_optimal_move(state, 5, 'A', 'C', 'B')
state = {'A': [5], 'B': [4], 'C': [3, 2, 1]}

print("State: A=[5], B=[4], C=[3, 2, 1]")
print("Calling: get_next_optimal_move(state, n=5, source='A', target='C', aux='B')")
print()

# The solver will:
# 1. Find disk 5 - it's on A (source) ✓
# 2. Check if disk 5 is on target C - NO
# 3. Check if disk 5 is on source A - YES
# 4. Check if disk 5 is exposed - YES (no disks on top)
# 5. Check if target C can accept disk 5 - NO (has disk 1 on top, 1 < 5)
# 6. So it recursively calls: get_next_optimal_move(state, 4, 'C', 'B', 'A')
#    This means: move 4 disks from C to B using A as auxiliary

print("Solver sees disk 5 is on source A, exposed, but target C is blocked")
print("Recursive call: get_next_optimal_move(state, n=4, source='C', target='B', aux='A')")
print("This means: move disk 4 from C to B (but disk 4 is NOT on C!)")
print()

# Now let's see what happens with that recursive call
# State: A=[5], B=[4], C=[3, 2, 1]
# Call: n=4, source='C', target='B', aux='A'
# 1. Find disk 4 - it's on B
# 2. Check if disk 4 is on target B - YES!
# 3. Disk is already on target, work on next smaller subproblem
# 4. Recursive call: get_next_optimal_move(state, 3, 'A', 'B', 'C')
#    This means: move 3 disks from A (auxiliary) to B (target) using C (source) as auxiliary

print("Solver sees disk 4 is already on target B")
print("Recursive call: get_next_optimal_move(state, n=3, source='A', target='B', aux='C')")
print("This means: move disk 3 from A to B (but disk 3 is NOT on A!)")
print()

# State: A=[5], B=[4], C=[3, 2, 1]
# Call: n=3, source='A', target='B', aux='C'
# 1. Find disk 3 - it's on C (auxiliary)
# 2. Check if disk 3 is on target B - NO
# 3. Check if disk 3 is on source A - NO
# 4. Disk is on auxiliary peg C
# 5. Check if disk 3 is exposed on C - NO (has disks 2, 1 on top)
# 6. Disk 3 is buried on auxiliary
# 7. Recursive call: get_next_optimal_move(state, 2, 'C', 'B', 'A')
#    This means: expose disk 3 by moving smaller disks from C to B

print("Solver sees disk 3 is on auxiliary peg C, buried")
print("Recursive call: get_next_optimal_move(state, n=2, source='C', target='B', aux='A')")
print("This means: move disk 2 from C to B")
print()

# Continue tracing...
# State: A=[5], B=[4], C=[3, 2, 1]
# Call: n=2, source='C', target='B', aux='A'
# 1. Find disk 2 - it's on C (source)
# 2. Check if disk 2 is on target B - NO
# 3. Check if disk 2 is on source C - YES
# 4. Check if disk 2 is exposed on C - NO (has disk 1 on top)
# 5. Need to move smaller disks off it
# 6. Recursive call: get_next_optimal_move(state, 1, 'C', 'A', 'B')
#    This means: move disk 1 from C to A

print("Solver sees disk 2 is on source C, buried")
print("Recursive call: get_next_optimal_move(state, n=1, source='C', target='A', aux='B')")
print("This means: move disk 1 from C to A")
print()

# State: A=[5], B=[4], C=[3, 2, 1]
# Call: n=1, source='C', target='A', aux='B'
# 1. Find disk 1 - it's on C (source)
# 2. Check if disk 1 is on target A - NO
# 3. Check if disk 1 is on source C - YES
# 4. Check if disk 1 is exposed on C - YES
# 5. Check if target A can accept disk 1 - NO! (has disk 5, and 5 < 1 is False, so 5 is not larger than 1)
#    Actually wait: 5 > 1, so YES it can accept
# 6. Return: {'from': 'C', 'to': 'A', 'disk': 1}

print("Solver sees disk 1 is on source C, exposed")
print("Target A has disk 5, which is larger than 1, so legal")
print("RETURN: Move disk 1 from C to A")
print()

print("Let's verify with actual solver:")
move = solver.get_next_optimal_move(state, 5, 'A', 'C', 'B')
print(f"Solver returned: {move}")
