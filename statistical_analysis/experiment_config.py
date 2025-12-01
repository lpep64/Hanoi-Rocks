"""
Experimental Configuration for Tower of Hanoi Statistical Analysis
Defines factors, levels, and constants for the 2^3 factorial experiment.
"""

# ==========================================
# Experimental Design: 2^3 Factorial
# ==========================================
# Factor A: Illegal Stack Solution (2 levels)
# Factor B: Illegal Ground Solution (2 levels)
# Factor C: Environment Randomness (2 levels)
# Total: 8 conditions

# Factor A: Illegal Stack Algorithm
FACTOR_A_LEVELS = {
    'dig_out': 'Dig Out (Surgical Fix)',
    'a_star': 'BFS (Optimal Shortest Path to Legality)'
}

# Factor B: Illegal Ground Algorithm
FACTOR_B_LEVELS = {
    'greedy': 'Greedy Placement (Min Violation)',
    'patient': 'Patient Wait (Legal Move Only)'
}

# Factor C: Environment Randomness Rate
FACTOR_C_LEVELS = {
    0.05: '5% Corruption Rate',
    0.10: '10% Corruption Rate'
}

# ==========================================
# Experimental Constants
# ==========================================
NUM_DISKS = 5  # All tests use 5 disks
NUM_TRIALS_PER_CONDITION = 50  # 50 trials per condition
TOTAL_CONDITIONS = 8  # 2^3
TOTAL_TRIALS = TOTAL_CONDITIONS * NUM_TRIALS_PER_CONDITION  # 400 trials

# Timeout and penalty
MAX_MOVES = 5000  # Maximum moves before timeout
TIMEOUT_PENALTY = 5001  # Value recorded for timeout trials

# Pre-corruption settings
NUM_INITIAL_CORRUPTIONS = 3  # Number of corruptions to create initial illegal state

# ==========================================
# Condition Matrix
# ==========================================
# Generate all 8 condition combinations
CONDITIONS = []
for stack_algo in FACTOR_A_LEVELS.keys():
    for ground_algo in FACTOR_B_LEVELS.keys():
        for corruption_rate in FACTOR_C_LEVELS.keys():
            CONDITIONS.append({
                'id': len(CONDITIONS) + 1,
                'stack_algorithm': stack_algo,
                'ground_algorithm': ground_algo,
                'corruption_rate': corruption_rate,
                'stack_name': FACTOR_A_LEVELS[stack_algo],
                'ground_name': FACTOR_B_LEVELS[ground_algo],
                'corruption_name': FACTOR_C_LEVELS[corruption_rate]
            })

# ==========================================
# Output Configuration
# ==========================================
RESULTS_CSV = 'results.csv'
RESULTS_SUMMARY_CSV = 'results_summary.csv'
PLOTS_DIR = 'plots'

# CSV Column Headers
CSV_HEADERS = [
    'trial_id',
    'condition_id',
    'stack_algorithm',
    'ground_algorithm',
    'corruption_rate',
    'seed',
    'total_moves',
    'num_regenerations',
    'num_corruptions_occurred',
    'final_state_valid',
    'timeout'
]

# ==========================================
# Validation Goals
# ==========================================
def is_solved(state):
    """
    Check if state is solved:
    - All disks on Peg C
    - Legal descending order
    - No disks on Queue or Ground
    """
    # State format: [A, B, C, Queue, Ground]
    peg_c = state[2]
    
    # Check no disks on other pegs
    if any(len(state[i]) > 0 for i in [0, 1, 3, 4]):
        return False
    
    # Check all disks on C
    if len(peg_c) == 0:
        return False
    
    # Check descending order (bottom to top: large to small)
    for i in range(len(peg_c) - 1):
        if peg_c[i] <= peg_c[i + 1]:  # Should be strictly decreasing
            return False
    
    return True


def is_state_legal(state):
    """
    Check if state is legal (no Queue/Ground violations, no stack violations).
    Uses the check_legality function from illegal_check module.
    """
    # Import here to avoid circular dependency
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../illegal_solutions')))
    from illegal_check import check_legality
    
    return check_legality(state)


if __name__ == "__main__":
    # Display experimental configuration
    print("="*60)
    print("EXPERIMENTAL CONFIGURATION")
    print("="*60)
    
    print(f"\nDesign: 2^3 Factorial")
    print(f"Total Conditions: {TOTAL_CONDITIONS}")
    print(f"Trials per Condition: {NUM_TRIALS_PER_CONDITION}")
    print(f"Total Trials: {TOTAL_TRIALS}")
    
    print(f"\n--- Factor A: Illegal Stack Algorithm ---")
    for key, value in FACTOR_A_LEVELS.items():
        print(f"  {key}: {value}")
    
    print(f"\n--- Factor B: Illegal Ground Algorithm ---")
    for key, value in FACTOR_B_LEVELS.items():
        print(f"  {key}: {value}")
    
    print(f"\n--- Factor C: Environment Randomness ---")
    for key, value in FACTOR_C_LEVELS.items():
        print(f"  {key*100:.0f}%: {value}")
    
    print(f"\n--- Constants ---")
    print(f"  Number of Disks: {NUM_DISKS}")
    print(f"  Max Moves: {MAX_MOVES}")
    print(f"  Timeout Penalty: {TIMEOUT_PENALTY}")
    print(f"  Initial Corruptions: {NUM_INITIAL_CORRUPTIONS}")
    
    print(f"\n--- Condition Matrix ---")
    for cond in CONDITIONS:
        print(f"  Condition {cond['id']}: {cond['stack_algorithm']} + {cond['ground_algorithm']} + {cond['corruption_rate']*100:.0f}%")
    
    print("\n" + "="*60)
