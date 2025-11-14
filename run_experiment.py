"""
Main Experiment Runner

Entry point for the entire experimental study.

Responsibilities:
1. Load configuration from config.json
2. Generate all experimental combinations (Factor A × B × C × D × E)
3. For each combination, run N replications
4. Collect and log all results to data/results.csv

Usage:
    python run_experiment.py
"""

import json
import uuid
import itertools
import time
from src.simulation_runner import SimulationRunner
from src.data_logger import DataLogger


def main():
    """
    Main execution function.
    
    Loads config, generates all 384+ experimental combinations,
    runs replications for each, and logs results.
    """
    print("=" * 70)
    print(" Real-World Tower of Hanoi - Experimental Study")
    print("=" * 70)
    print()
    
    # Load configuration
    print("Loading configuration from config.json...")
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    sim_params = config['simulation_parameters']
    factors = config['experimental_factors']
    
    print("Configuration loaded successfully.")
    print()
    print("Simulation Parameters:")
    print(f"  Replications per combination: {sim_params['replications_per_combination']}")
    print(f"  Timeout factor: {sim_params['max_moves_timeout_factor']}")
    print(f"  Visualizer enabled: {sim_params['visualizer_enabled']}")
    print(f"  Visualizer delay: {sim_params['visualizer_delay_ms']} ms")
    print()
    
    # Create all experimental combinations
    # Factor A: disk_count
    # Factor B: target_alteration_percent
    # Factor C: illegal_formation_handler
    # Factor D: ground_handler
    # Factor E: duplicate_handler
    all_combinations = list(itertools.product(
        factors['disk_count'],
        factors['target_alteration_percent'],
        factors['illegal_formation_handler'],
        factors['ground_handler'],
        factors['duplicate_handler']
    ))
    
    total_combinations = len(all_combinations)
    total_runs = total_combinations * sim_params['replications_per_combination']
    
    print("Experimental Design:")
    print(f"  Factor A (Disk Count): {factors['disk_count']}")
    print(f"  Factor B (Alteration %): {factors['target_alteration_percent']}")
    print(f"  Factor C (Formation Handler): {factors['illegal_formation_handler']}")
    print(f"  Factor D (Ground Handler): {factors['ground_handler']}")
    print(f"  Factor E (Duplicate Handler): {factors['duplicate_handler']}")
    print()
    print(f"Total unique combinations: {total_combinations}")
    print(f"Total replications per combination: {sim_params['replications_per_combination']}")
    print(f"TOTAL SIMULATION RUNS: {total_runs}")
    print()
    
    # Setup the data logger
    logger = DataLogger('data/results.csv')
    print("Data logger initialized. Results will be saved to: data/results.csv")
    print()
    
    # Prompt user to continue
    if total_runs > 100:
        response = input(f"This will run {total_runs} simulations. Continue? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("Experiment cancelled.")
            return
        print()
    
    # Start timer
    experiment_start_time = time.time()
    
    run_counter = 0
    successful_runs = 0
    failed_runs = 0
    
    # Loop over all combinations
    for combo_idx, combo in enumerate(all_combinations, 1):
        disk_count, alt_pct, form_handler, gnd_handler, dup_handler = combo
        
        print("=" * 70)
        print(f"Combination {combo_idx}/{total_combinations}")
        print(f"  Disks: {disk_count} | Alteration: {alt_pct}% | Formation: {form_handler}")
        print(f"  Ground: {gnd_handler} | Duplicate: {dup_handler}")
        print("=" * 70)
        
        # Run N replications for this specific combination
        for rep in range(sim_params['replications_per_combination']):
            run_counter += 1
            
            print(f"  Run {run_counter}/{total_runs} (Rep {rep + 1}/{sim_params['replications_per_combination']})", end=" ... ")
            
            # Generate a unique ID for this specific run
            run_id = str(uuid.uuid4())
            
            # Instantiate and run the simulation
            try:
                runner = SimulationRunner(
                    run_id=run_id,
                    disk_count=disk_count,
                    alteration_rate=alt_pct,
                    formation_handler_strategy=form_handler,
                    ground_handler_strategy=gnd_handler,
                    duplicate_handler_strategy=dup_handler,
                    sim_params=sim_params
                )
                
                summary_data = runner.run()
                
                # Log the final results
                logger.log_run(summary_data)
                
                # Track success/failure
                if summary_data['is_solvable']:
                    successful_runs += 1
                    print(f"✓ Solved in {summary_data['total_moves_to_solve']} moves")
                else:
                    failed_runs += 1
                    print("✗ Timeout (unsolvable)")
                
                # Clean up
                del runner
                
            except Exception as e:
                print(f"✗ ERROR: {str(e)}")
                failed_runs += 1
        
        print()
    
    # Experiment complete
    experiment_end_time = time.time()
    total_time = experiment_end_time - experiment_start_time
    
    print("=" * 70)
    print(" EXPERIMENT COMPLETE")
    print("=" * 70)
    print(f"Total runs executed: {run_counter}")
    print(f"Successful runs: {successful_runs}")
    print(f"Failed/timeout runs: {failed_runs}")
    print(f"Total time: {total_time:.2f} seconds ({total_time/60:.2f} minutes)")
    print(f"Average time per run: {total_time/run_counter:.2f} seconds")
    print()
    print(f"Results saved to: data/results.csv")
    print(f"Detailed logs saved to: data/raw_move_logs/")
    print()
    print("Next steps:")
    print("  1. Analyze results using the provided R Markdown file (analysis.Rmd)")
    print("  2. Run: rmarkdown::render('analysis.Rmd')")
    print()


if __name__ == "__main__":
    main()
