"""
Interactive Visualizer Demo

Allows you to configure and run a single simulation with visualization enabled.
This lets you see the algorithm in action without running the full experiment.
"""

import json
import uuid
from src.simulation_runner import SimulationRunner


def get_user_input():
    """
    Prompt user for simulation parameters.
    
    Returns:
        dict: Configuration parameters for the simulation
    """
    print("=" * 70)
    print(" Real-World Tower of Hanoi - Interactive Visualizer Demo")
    print("=" * 70)
    print()
    print("Configure your simulation parameters:")
    print()
    
    # Disk count
    while True:
        disk_input = input("Disk count (3, 5, 7, or 9) [default: 3]: ").strip()
        if disk_input == "":
            disk_count = 3
            break
        try:
            disk_count = int(disk_input)
            if disk_count in [3, 5, 7, 9]:
                break
            else:
                print("  Please enter 3, 5, 7, or 9")
        except ValueError:
            print("  Please enter a valid number")
    
    # Alteration rate
    while True:
        alt_input = input("Target alteration % (0, 10, 20, or 30) [default: 10]: ").strip()
        if alt_input == "":
            alteration_rate = 10
            break
        try:
            alteration_rate = int(alt_input)
            if alteration_rate in [0, 10, 20, 30]:
                break
            else:
                print("  Please enter 0, 10, 20, or 30")
        except ValueError:
            print("  Please enter a valid number")
    
    # Formation handler
    print()
    print("Formation Handler options:")
    print("  1. deepest  - Resolve deepest violation first")
    print("  2. bubble   - Resolve top-most violation first")
    print("  3. buffer   - Use ground as temporary buffer")
    while True:
        form_input = input("Choose formation handler (1, 2, or 3) [default: 1]: ").strip()
        if form_input == "" or form_input == "1":
            formation_handler = "deepest"
            break
        elif form_input == "2":
            formation_handler = "bubble"
            break
        elif form_input == "3":
            formation_handler = "buffer"
            break
        else:
            print("  Please enter 1, 2, or 3")
    
    # Ground handler
    print()
    print("Ground Handler options:")
    print("  1. best-fit        - Place on peg with closest larger disk")
    print("  2. first-available - Place on first legal peg")
    while True:
        ground_input = input("Choose ground handler (1 or 2) [default: 1]: ").strip()
        if ground_input == "" or ground_input == "1":
            ground_handler = "best-fit"
            break
        elif ground_input == "2":
            ground_handler = "first-available"
            break
        else:
            print("  Please enter 1 or 2")
    
    # Duplicate handler
    print()
    print("Duplicate Handler options:")
    print("  1. keep    - Allow duplicates")
    print("  2. discard - Remove duplicate instances")
    while True:
        dup_input = input("Choose duplicate handler (1 or 2) [default: 1]: ").strip()
        if dup_input == "" or dup_input == "1":
            duplicate_handler = "keep"
            break
        elif dup_input == "2":
            duplicate_handler = "discard"
            break
        else:
            print("  Please enter 1 or 2")
    
    # Visualization speed
    print()
    while True:
        speed_input = input("Visualization delay in ms (50-1000) [default: 200]: ").strip()
        if speed_input == "":
            delay_ms = 200
            break
        try:
            delay_ms = int(speed_input)
            if 50 <= delay_ms <= 1000:
                break
            else:
                print("  Please enter a value between 50 and 1000")
        except ValueError:
            print("  Please enter a valid number")
    
    return {
        'disk_count': disk_count,
        'alteration_rate': alteration_rate,
        'formation_handler': formation_handler,
        'ground_handler': ground_handler,
        'duplicate_handler': duplicate_handler,
        'delay_ms': delay_ms
    }


def main():
    """
    Main execution function.
    """
    # Get user configuration
    config = get_user_input()
    
    print()
    print("=" * 70)
    print(" Starting Simulation with Visualization")
    print("=" * 70)
    print(f" Disk Count: {config['disk_count']}")
    print(f" Alteration Rate: {config['alteration_rate']}%")
    print(f" Formation Handler: {config['formation_handler']}")
    print(f" Ground Handler: {config['ground_handler']}")
    print(f" Duplicate Handler: {config['duplicate_handler']}")
    print(f" Visualization Delay: {config['delay_ms']} ms")
    print("=" * 70)
    print()
    input("Press Enter to start...")
    print()
    
    # Create simulation parameters with visualization enabled
    sim_params = {
        'replications_per_combination': 1,
        'max_moves_timeout_factor': 50,
        'visualizer_enabled': True,
        'visualizer_delay_ms': config['delay_ms']
    }
    
    # Generate unique run ID
    run_id = str(uuid.uuid4())
    
    # Create and run simulation
    try:
        runner = SimulationRunner(
            run_id=run_id,
            disk_count=config['disk_count'],
            alteration_rate=config['alteration_rate'],
            formation_handler_strategy=config['formation_handler'],
            ground_handler_strategy=config['ground_handler'],
            duplicate_handler_strategy=config['duplicate_handler'],
            sim_params=sim_params
        )
        
        summary_data = runner.run()
        
        # Display final results
        print()
        print("=" * 70)
        print(" SIMULATION COMPLETE")
        print("=" * 70)
        print(f" Run ID: {summary_data['run_id']}")
        print(f" Solvable: {'YES' if summary_data['is_solvable'] else 'NO'}")
        if summary_data['is_solvable']:
            print(f" Total Moves: {summary_data['total_moves_to_solve']}")
            theoretical_min = (2 ** config['disk_count']) - 1
            overhead = summary_data['total_moves_to_solve'] - theoretical_min
            overhead_pct = (overhead / theoretical_min) * 100
            print(f" Theoretical Minimum: {theoretical_min}")
            print(f" Overhead: {overhead} moves ({overhead_pct:.1f}%)")
        print(f" Total Alterations: {summary_data['total_alterations']}")
        print(f" Total Illegal States: {summary_data['total_illegal_states']}")
        print(f" Actual Alteration %: {summary_data['actual_alteration_percent']:.2f}%")
        print(f" Detailed Log: {summary_data['raw_move_log_path']}")
        print("=" * 70)
        print()
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
