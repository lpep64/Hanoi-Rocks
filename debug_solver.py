"""
Debug script to investigate solver failures with 5 disks
"""
import uuid
from src.simulation_runner import SimulationRunner
from src.hanoi_solver import HanoiSolver
from src.environment import Environment

print("=" * 70)
print("DEBUG: Testing Solver with 5 Disks")
print("=" * 70)

# Test 1: Can solver generate full sequence for 5 disks?
print("\nTest 1: Full solve sequence for 5 disks")
solver = HanoiSolver()
moves = solver.solve_full(5, 'A', 'C', 'B')
print(f"Generated {len(moves)} moves (expected 31)")
print(f"First 5 moves: {moves[:5]}")
print(f"Last 5 moves: {moves[-5:]}")

# Test 2: Step-by-step simulation
print("\n" + "=" * 70)
print("Test 2: Step-by-step simulation with 5 disks, 0% alteration")
print("=" * 70)

sim_params = {
    'replications_per_combination': 1,
    'max_moves_timeout_factor': 50,
    'visualizer_enabled': False,
    'visualizer_delay_ms': 0
}

runner = SimulationRunner(
    run_id=str(uuid.uuid4()),
    disk_count=5,
    alteration_rate=0,
    formation_handler_strategy='bubble',
    ground_handler_strategy='best-fit',
    duplicate_handler_strategy='keep',
    sim_params=sim_params
)

# Manually run a few steps to see what happens
env = runner.env
solver = runner.solver
target_state = list(range(5, 0, -1))

print(f"\nInitial state:")
print(f"  A: {env.pegs['A']}")
print(f"  B: {env.pegs['B']}")
print(f"  C: {env.pegs['C']}")
print(f"  Max moves allowed: {runner.max_moves}")

# Try first 10 moves
for i in range(10):
    current_state = env.get_state()
    
    # Check win
    if current_state['C'] == target_state and not current_state['A'] and not current_state['B']:
        print(f"\n✓ Solved in {i} moves!")
        break
    
    # Get next move
    n, src, tgt, aux = runner.determine_current_subproblem(current_state)
    print(f"\nMove {i+1}: Subproblem(n={n}, {src}→{tgt}, aux={aux})")
    
    if n == 0:
        print("  ERROR: Subproblem returned n=0")
        break
    
    next_move = solver.get_next_optimal_move(current_state, n, src, tgt, aux)
    
    if next_move is None:
        print("  ERROR: Solver returned None")
        print(f"  Current state: A={current_state['A']}, B={current_state['B']}, C={current_state['C']}")
        break
    
    print(f"  Solver suggests: Move disk {next_move['disk']} from {next_move['from']} to {next_move['to']}")
    
    # Apply move
    success, reason = env.apply_move(next_move['from'], next_move['to'])
    if not success:
        print(f"  ERROR: Move failed - {reason}")
        break
    
    print(f"  Result: A={env.pegs['A']}, B={env.pegs['B']}, C={env.pegs['C']}")

# Test 3: Run full simulation
print("\n" + "=" * 70)
print("Test 3: Full simulation run")
print("=" * 70)

runner2 = SimulationRunner(
    run_id=str(uuid.uuid4()),
    disk_count=5,
    alteration_rate=0,
    formation_handler_strategy='bubble',
    ground_handler_strategy='best-fit',
    duplicate_handler_strategy='keep',
    sim_params=sim_params
)

result = runner2.run()

print(f"\nResult:")
print(f"  Is Solvable: {result['is_solvable']}")
print(f"  Total Moves: {result['total_moves_to_solve']}")
print(f"  Total Alterations: {result['total_alterations']}")
print(f"  Total Illegal States: {result['total_illegal_states']}")

# Check the log file
print(f"\nLog file: {result['raw_move_log_path']}")
print("\nLast 20 lines of log:")
with open(result['raw_move_log_path'], 'r') as f:
    lines = f.readlines()
    for line in lines[-20:]:
        print(line.rstrip())
