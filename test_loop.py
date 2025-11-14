"""
Test to see if solver gets stuck in a loop
"""
from src.hanoi_solver import HanoiSolver
from src.environment import Environment

solver = HanoiSolver()
env = Environment(5)

# Fast-forward to move 9 state: A=[5], B=[4], C=[3, 2, 1]
env.pegs['A'] = [5]
env.pegs['B'] = [4]
env.pegs['C'] = [3, 2, 1]

print("Starting from move 9 state: A=[5], B=[4], C=[3, 2, 1]")
print("="*70)

# Simulate next 20 moves
for i in range(20):
    state = env.get_state()
    print(f"\nMove {i+1}:")
    print(f"  State: A={state['A']}, B={state['B']}, C={state['C']}")
    
    # Always call with full problem
    move = solver.get_next_optimal_move(state, 5, 'A', 'C', 'B')
    
    if move is None:
        print("  Solver returned None - STUCK!")
        break
    
    print(f"  Solver: Move disk {move['disk']} from {move['from']} to {move['to']}")
    
    # Apply the move
    success, reason = env.apply_move(move['from'], move['to'])
    if not success:
        print(f"  ERROR: {reason}")
        break
    
    # Check if we're in a loop (disk 1 moving back and forth)
    if i > 5:
        print("  ** Checking for loop pattern **")

print("\n" + "="*70)
print(f"Final state: A={env.pegs['A']}, B={env.pegs['B']}, C={env.pegs['C']}")

# Check if solved
if env.pegs['C'] == [5, 4, 3, 2, 1] and not env.pegs['A'] and not env.pegs['B']:
    print("SOLVED!")
else:
    print("NOT SOLVED - stuck in loop or error")
