"""
Debug the settled disk logic
"""
from src.hanoi_solver import HanoiSolver

solver = HanoiSolver()
state = {'A': [5], 'B': [4], 'C': [3, 2, 1]}
n = 5

print("State: A=[5], B=[4], C=[3, 2, 1]")
print("Goal: A=[], B=[], C=[5, 4, 3, 2, 1]")
print()

# Check settled disks manually
target = 'C'
target_stack = state[target]  # [3, 2, 1]

print("Target stack:", target_stack)
print()

settled_disks = set()
for i, disk in enumerate(target_stack):
    print(f"Checking disk {disk} at index {i}")
    print(f"  Disks below it: {target_stack[:i]}")
    print(f"  Larger disks (4, 5): Are they all below?")
    
    all_larger_below = True
    for larger in range(disk + 1, n + 1):
        in_stack_below = larger in target_stack[:i]
        print(f"    Disk {larger}: in_stack_below={in_stack_below}")
        if not in_stack_below:
            all_larger_below = False
    
    print(f"  all_larger_below={all_larger_below}")
    if all_larger_below:
        settled_disks.add(disk)
        print(f"  -> Disk {disk} is SETTLED")
    else:
        print(f"  -> Disk {disk} is NOT settled")
    print()

print("Settled disks:", settled_disks)
print()
print("The issue: Disks 1, 2, 3 are NOT settled because disks 4 and 5 are not below them.")
print("This is correct! They need to move out of the way.")
print()
print("But the solver keeps moving disk 1 back and forth instead of moving disk 2 or 3.")
