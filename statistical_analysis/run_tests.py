"""
Main Experiment Orchestrator for Tower of Hanoi Statistical Analysis
Runs 8 conditions × 50 trials = 400 total trials
Implements: Generate → Execute → Validate → Corrupt → Regenerate loop

CRITICAL FIX (Dec 3, 2025):
- Goal is FULL SOLUTION (all disks on C in order), not just legality
- Main loop continues until is_solved() returns True
- BFS achieves legality, then Phase 3 completes solution to C
- If corruption occurs, regenerates solution from current corrupted state
- Trials only terminate when fully solved or timeout (no partial solutions)
"""

import sys
import os
import csv
import time
from typing import List, Tuple, Dict, Optional

# Add parent directories to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../illegal_solutions')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../state_solutions')))

# Import modules
from illegal_stack import solve_illegal_dig_out, solve_illegal_a_star
from illegal_ground import solve_ground_greedy, solve_ground_patient
from randomizer import Randomizer
from hanoi_state import solve_hanoi_from_image
from illegal_check import check_legality

# Import configuration
from experiment_config import (
    CONDITIONS, NUM_TRIALS_PER_CONDITION, MAX_MOVES, TIMEOUT_PENALTY,
    NUM_DISKS, NUM_INITIAL_CORRUPTIONS, CSV_HEADERS, RESULTS_CSV
)
from state_validator import StateValidator


class ExperimentRunner:
    """
    Orchestrates the statistical experiment across all conditions and trials.
    """
    
    def __init__(self):
        self.validator = StateValidator()
        self.results = []
        
        # Peg indices
        self.PEG_A = 0
        self.PEG_B = 1
        self.PEG_C = 2
        self.PEG_QUEUE = 3
        self.PEG_GROUND = 4
    
    def generate_solution(self, state: List[List[int]], stack_algo: str, ground_algo: str) -> List:
        """
        Generate complete solution path: Ground → Stack → Hanoi
        
        Returns:
            List of Move objects
        """
        current_state = [list(p) for p in state]  # Deep copy
        all_moves = []
        
        # Phase 1: Ground Solution (if ground disks exist)
        if len(current_state[self.PEG_GROUND]) > 0:
            if ground_algo == 'greedy':
                moves, current_state = solve_ground_greedy(current_state)
            else:  # patient
                moves, current_state = solve_ground_patient(current_state)
            all_moves.extend(moves)
        
        # Phase 2: Stack Solution (if illegal stacks exist)
        if not check_legality(current_state):
            if stack_algo == 'dig_out':
                moves, current_state = solve_illegal_dig_out(current_state)
            else:  # a_star (BFS implementation)
                moves, current_state = solve_illegal_a_star(current_state)
            all_moves.extend(moves)
        
        # Phase 3: Standard Hanoi Solution (move to C)
        # Only run if not already solved
        # Note: BFS achieves legality but may not solve to C, so we still need this phase
        if not self.validator.is_solved(current_state):
            # State is legal but not solved (not all on C)
            # CRITICAL FIX: BFS may leave disks in Queue - must move them to A/B/C first
            
            # Validate state before Phase 3
            # Ground should be empty by now (Phase 1 clears it)
            if current_state[self.PEG_GROUND]:
                raise ValueError(f"Ground peg still has disks after Phase 1: {current_state[self.PEG_GROUND]}")
            
            # Queue should be empty (Phase 2 algorithms must clear it)
            if current_state[self.PEG_QUEUE]:
                raise ValueError(f"Queue peg still has disks after Phase 2: {current_state[self.PEG_QUEUE]}")
            
            # Standard Hanoi solver on clean 3-peg state
            three_peg_state = [current_state[0], current_state[1], current_state[2]]
            moves, final_state_obj = solve_hanoi_from_image(three_peg_state, source='A', destination='C', auxiliary='B')
            # Extract state from TowerState object (uses pegs dict)
            current_state[0] = final_state_obj.pegs['A']
            current_state[1] = final_state_obj.pegs['B']
            current_state[2] = final_state_obj.pegs['C']
            all_moves.extend(moves)
        
        return all_moves
    
    def execute_single_move(self, state: List[List[int]], move) -> List[List[int]]:
        """
        Execute a single move on the state.
        Returns new state.
        """
        new_state = [list(p) for p in state]  # Deep copy
        
        # Map peg names to indices
        peg_map = {'A': 0, 'B': 1, 'C': 2, 'Queue': 3, 'Ground': 4}
        from_idx = peg_map[move.initial_peg]
        to_idx = peg_map[move.destination_peg]
        
        # Execute move
        disk = new_state[from_idx].pop()
        new_state[to_idx].append(disk)
        
        return new_state
    
    def run_single_trial(self, condition: Dict, trial_num: int, seed: int) -> Dict:
        """
        Run a single trial with the specified condition.
        
        Returns:
            Dict with trial results
        """
        # Extract condition parameters
        stack_algo = condition['stack_algorithm']
        ground_algo = condition['ground_algorithm']
        corruption_rate = condition['corruption_rate']
        
        # Initialize randomizer with seed
        randomizer = Randomizer(seed=seed)
        
        # Create initial corrupted state
        state = randomizer.create_corrupted_initial_state(
            n=NUM_DISKS, 
            num_corruptions=NUM_INITIAL_CORRUPTIONS
        )
        
        # Track metrics
        total_moves = 0
        num_regenerations = 0
        num_corruptions_occurred = 0
        timeout = False
        
        # Main execution loop - goal is to achieve FULL SOLUTION (all disks on C)
        while not self.validator.is_solved(state) and total_moves < MAX_MOVES:
            # Generate solution path
            solution_path = self.generate_solution(state, stack_algo, ground_algo)
            num_regenerations += 1
            
            if not solution_path:
                # No solution found, mark as timeout
                timeout = True
                break
            
            # Execute moves one by one
            for move in solution_path:
                if total_moves >= MAX_MOVES:
                    timeout = True
                    break
                
                # Execute move
                state = self.execute_single_move(state, move)
                total_moves += 1
                
                # Apply randomness check AFTER move
                corruption_result = randomizer.corrupt_state(state, corruption_rate)
                if corruption_result:
                    num_corruptions_occurred += 1
                    # State corrupted, need to regenerate solution from current state
                    break
                
                # Check if solved (goal achieved)
                if self.validator.is_solved(state):
                    break
            
            # If solved, exit main loop
            if self.validator.is_solved(state):
                break
        
        # Check timeout
        if total_moves >= MAX_MOVES:
            timeout = True
            total_moves = TIMEOUT_PENALTY
        
        # Validate final state (check if solved - all disks on C in order)
        final_state_valid = self.validator.is_solved(state)
        
        return {
            'trial_id': f"C{condition['id']}_T{trial_num}",
            'condition_id': condition['id'],
            'stack_algorithm': stack_algo,
            'ground_algorithm': ground_algo,
            'corruption_rate': corruption_rate,
            'seed': seed,
            'total_moves': total_moves,
            'num_regenerations': num_regenerations,
            'num_corruptions_occurred': num_corruptions_occurred,
            'final_state_valid': final_state_valid,
            'timeout': timeout
        }
    
    def run_all_trials(self):
        """
        Run all 400 trials (8 conditions × 50 trials).
        """
        print("="*70)
        print("TOWER OF HANOI STATISTICAL EXPERIMENT")
        print("="*70)
        print(f"Total Conditions: {len(CONDITIONS)}")
        print(f"Trials per Condition: {NUM_TRIALS_PER_CONDITION}")
        print(f"Total Trials: {len(CONDITIONS) * NUM_TRIALS_PER_CONDITION}")
        print("="*70)
        
        trial_count = 0
        start_time = time.time()
        
        for condition in CONDITIONS:
            print(f"\n--- Condition {condition['id']}/{len(CONDITIONS)} ---")
            print(f"Stack: {condition['stack_name']}")
            print(f"Ground: {condition['ground_name']}")
            print(f"Randomness: {condition['corruption_name']}")
            
            for trial_num in range(1, NUM_TRIALS_PER_CONDITION + 1):
                trial_count += 1
                # Use trial_count as seed for reproducibility
                seed = trial_count * 100
                
                try:
                    result = self.run_single_trial(condition, trial_num, seed)
                    self.results.append(result)
                    
                    # Progress update every 10 trials
                    if trial_num % 10 == 0:
                        avg_moves = sum(r['total_moves'] for r in self.results[-10:]) / 10
                        print(f"  Trial {trial_num}/{NUM_TRIALS_PER_CONDITION} - Avg moves (last 10): {avg_moves:.1f}")
                
                except Exception as e:
                    print(f"  ERROR in Trial {trial_num}: {str(e)}")
                    # Record error trial
                    self.results.append({
                        'trial_id': f"C{condition['id']}_T{trial_num}",
                        'condition_id': condition['id'],
                        'stack_algorithm': condition['stack_algorithm'],
                        'ground_algorithm': condition['ground_algorithm'],
                        'corruption_rate': condition['corruption_rate'],
                        'seed': seed,
                        'total_moves': TIMEOUT_PENALTY,
                        'num_regenerations': 0,
                        'num_corruptions_occurred': 0,
                        'final_state_valid': False,
                        'timeout': True
                    })
        
        elapsed_time = time.time() - start_time
        print("\n" + "="*70)
        print(f"EXPERIMENT COMPLETE")
        print(f"Total Trials: {len(self.results)}")
        print(f"Elapsed Time: {elapsed_time:.2f} seconds ({elapsed_time/60:.2f} minutes)")
        print("="*70)
    
    def save_results(self, filename: str = RESULTS_CSV):
        """
        Save results to CSV file.
        """
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=CSV_HEADERS)
            writer.writeheader()
            writer.writerows(self.results)
        
        print(f"\nResults saved to: {filepath}")
    
    def print_summary(self):
        """
        Print summary statistics.
        """
        print("\n" + "="*70)
        print("SUMMARY STATISTICS")
        print("="*70)
        
        # Overall statistics
        total_trials = len(self.results)
        timeouts = sum(1 for r in self.results if r['timeout'])
        successful = total_trials - timeouts
        
        print(f"\nOverall:")
        print(f"  Total Trials: {total_trials}")
        print(f"  Successful: {successful} ({successful/total_trials*100:.1f}%)")
        print(f"  Timeouts: {timeouts} ({timeouts/total_trials*100:.1f}%)")
        
        # Statistics by condition
        print(f"\nBy Condition:")
        for condition in CONDITIONS:
            cond_results = [r for r in self.results if r['condition_id'] == condition['id']]
            cond_successful = [r for r in cond_results if not r['timeout']]
            
            if cond_successful:
                avg_moves = sum(r['total_moves'] for r in cond_successful) / len(cond_successful)
                min_moves = min(r['total_moves'] for r in cond_successful)
                max_moves = max(r['total_moves'] for r in cond_successful)
                
                print(f"\n  Condition {condition['id']}:")
                print(f"    {condition['stack_algorithm']} + {condition['ground_algorithm']} + {condition['corruption_rate']*100:.0f}%")
                print(f"    Successful: {len(cond_successful)}/{len(cond_results)}")
                print(f"    Avg Moves: {avg_moves:.1f} (min: {min_moves}, max: {max_moves})")
            else:
                print(f"\n  Condition {condition['id']}: No successful trials")


if __name__ == "__main__":
    # Run the experiment
    runner = ExperimentRunner()
    runner.run_all_trials()
    runner.save_results()
    runner.print_summary()
