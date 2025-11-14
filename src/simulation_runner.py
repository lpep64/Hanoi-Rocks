"""
Simulation Runner

Orchestrates a single, complete simulation run from start to finish.
It is configured by run_experiment.py with specific factor values.

Key Responsibilities:
1. Initialize environment with specified parameters
2. Run the main simulation loop until completion or timeout
3. Handle illegal state detection and resolution
4. Collect and return summary statistics
"""

import time
import os
from src.environment import Environment
from src.hanoi_solver import HanoiSolver
import src.illegal_state_handlers as Handlers
from src.visualizer import HanoiVisualizer


class SimulationRunner:
    """
    Runs a single Tower of Hanoi simulation with environmental alterations.
    
    Manages the interaction between the environment, solver, and illegal state handlers.
    Tracks all statistics and produces detailed logs.
    """
    
    def __init__(self, run_id, disk_count, alteration_rate,
                 formation_handler_strategy, ground_handler_strategy, duplicate_handler_strategy,
                 sim_params):
        """
        Initialize a simulation run with specific experimental parameters.
        
        Args:
            run_id (str): Unique identifier for this run (UUID)
            disk_count (int): Number of disks (Factor A)
            alteration_rate (int): Target alteration percentage 0-100 (Factor B)
            formation_handler_strategy (str): Strategy for illegal formations (Factor C)
            ground_handler_strategy (str): Strategy for ground elements (Factor D)
            duplicate_handler_strategy (str): Strategy for duplicates (Factor E)
            sim_params (dict): Simulation parameters from config.json
        """
        self.run_id = run_id
        self.disk_count = disk_count
        self.target_alteration_rate = alteration_rate
        
        # Store strategy names for logging
        self.formation_handler_strategy = formation_handler_strategy
        self.ground_handler_strategy = ground_handler_strategy
        self.duplicate_handler_strategy = duplicate_handler_strategy
        
        # Initialize core components
        self.env = Environment(disk_count)
        self.solver = HanoiSolver()
        
        # Calculate timeout threshold
        # Theoretical minimum moves is 2^n - 1
        # Timeout is minimum * timeout_factor
        theoretical_min = (2 ** self.disk_count) - 1
        self.max_moves = theoretical_min * sim_params['max_moves_timeout_factor']
        
        # Statistics trackers
        self.total_moves = 0
        self.alterations_count = 0
        self.illegal_states_count = 0
        self.consecutive_illegal_states = 0  # Track consecutive illegal states
        self.max_consecutive_illegal_states = 100  # Abort if we hit this many in a row
        self.move_log = []  # Detailed log of every action
        
        # Visualizer setup
        self.visualizer_enabled = sim_params['visualizer_enabled']
        self.visualizer_delay = sim_params['visualizer_delay_ms'] / 1000.0
        if self.visualizer_enabled:
            self.visualizer = HanoiVisualizer(self.env.pegs, self.disk_count)
    
    def run(self):
        """
        Execute the main simulation loop.
        
        Returns:
            dict: Summary data for logging to CSV
        """
        # Define the target (goal) state
        target_state_peg_c = list(range(self.disk_count, 0, -1))
        
        # Main simulation loop
        while True:
            # Get current state (deep copy for safety)
            current_state = self.env.get_state()
            
            # 1. Check for win condition
            # Success: all disks on peg C, nothing on A or B, nothing on ground
            if (current_state['C'] == target_state_peg_c and
                not current_state['A'] and
                not current_state['B'] and
                not self.env.ground):
                return self.format_results(is_solvable=True)
            
            # 2. Check for timeout condition
            if self.total_moves >= self.max_moves:
                return self.format_results(is_solvable=False)
            
            # 3. Visualize current state (if enabled)
            if self.visualizer_enabled:
                status = f"Move: {self.total_moves} | Alterations: {self.alterations_count} | Illegal States: {self.illegal_states_count}"
                self.visualizer.draw(self.env.pegs, self.env.ground, status)
                time.sleep(self.visualizer_delay)
            
            # 4. Check for and resolve illegal states BEFORE making next move
            illegal_type, details = self.env.check_for_illegal_states()
            
            if illegal_type != "Legal":
                # Illegal state detected - must resolve it
                self.illegal_states_count += 1
                self.consecutive_illegal_states += 1
                
                # Safety check: if too many consecutive illegal states, abort
                if self.consecutive_illegal_states > self.max_consecutive_illegal_states:
                    self.move_log.append(f"[Move {self.total_moves}] ABORT: Too many consecutive illegal states ({self.consecutive_illegal_states})")
                    return self.format_results(is_solvable=False)
                
                resolution_moves = self.resolve_illegal_state(illegal_type, details)
                self.total_moves += resolution_moves
                handler_name = self.get_handler_name(illegal_type)
                self.move_log.append(f"[Move {self.total_moves}] Resolved {illegal_type} using {handler_name} ({resolution_moves} moves)")
                
                # Introduce potential alteration even after illegal state resolution
                if self.env.introduce_alteration(self.target_alteration_rate):
                    self.alterations_count += 1
                    self.move_log.append(f"[Move {self.total_moves}] *** ALTERATION INTRODUCED (post-resolution) ***")
                
                continue  # Re-check state after resolution
            
            # 5. State is legal - reset consecutive counter and get next optimal move from solver
            self.consecutive_illegal_states = 0  # Reset counter when state is legal
            
            # Determine the current subproblem parameters
            n, src, tgt, aux = self.determine_current_subproblem(current_state)
            
            if n == 0:
                # No more disks to move - should have triggered win condition
                # This is an edge case
                return self.format_results(is_solvable=False)
            
            next_move = self.solver.get_next_optimal_move(current_state, n, src, tgt, aux)
            
            if next_move is None:
                # Solver cannot find a valid move from this state
                # This indicates the state is unsolvable or trapped
                self.move_log.append(f"[Move {self.total_moves}] ERROR: Solver returned no valid move")
                return self.format_results(is_solvable=False)
            
            # 6. Apply the optimal move
            success, reason = self.env.apply_move(next_move['from'], next_move['to'])
            
            if not success:
                # Move failed - this shouldn't happen if solver and environment are aligned
                self.move_log.append(f"[Move {self.total_moves}] CRITICAL: Move failed - {reason}")
                self.move_log.append(f"  Attempted: Disk {next_move['disk']} from {next_move['from']} to {next_move['to']}")
                return self.format_results(is_solvable=False)
            
            # Move succeeded
            self.total_moves += 1
            self.move_log.append(f"[Move {self.total_moves}] Moved disk {next_move['disk']} from {next_move['from']} to {next_move['to']}")
            
            # 7. Potentially introduce an alteration AFTER the move
            if self.env.introduce_alteration(self.target_alteration_rate):
                self.alterations_count += 1
                self.move_log.append(f"[Move {self.total_moves}] *** ALTERATION INTRODUCED ***")
    
    def resolve_illegal_state(self, illegal_type, details):
        """
        Call the appropriate handler function based on configuration.
        
        Args:
            illegal_type (str): Type of illegal state
            details: Contextual information about the violation
        
        Returns:
            int: Number of moves the resolution cost
        """
        if illegal_type == "ElementOnGround":
            # Use configured ground handler strategy
            handler_func = getattr(Handlers, f"resolve_ground_{self.ground_handler_strategy.replace('-', '_')}")
            return handler_func(self.env, details)
        
        elif illegal_type == "DuplicateItem":
            # Use configured duplicate handler strategy
            handler_func = getattr(Handlers, f"resolve_duplicates_{self.duplicate_handler_strategy}")
            return handler_func(self.env, details)
        
        elif illegal_type == "IllegalFormation":
            # Use configured formation handler strategy
            handler_func = getattr(Handlers, f"resolve_formation_{self.formation_handler_strategy}")
            return handler_func(self.env, details)
        
        return 0  # Should not be reached
    
    def get_handler_name(self, illegal_type):
        """
        Get the handler strategy name for logging.
        
        Args:
            illegal_type (str): Type of illegal state
        
        Returns:
            str: Strategy name
        """
        if illegal_type == "ElementOnGround":
            return self.ground_handler_strategy
        if illegal_type == "DuplicateItem":
            return self.duplicate_handler_strategy
        if illegal_type == "IllegalFormation":
            return self.formation_handler_strategy
        return "unknown"
    
    def determine_current_subproblem(self, current_state):
        """
        Determine the current Tower of Hanoi subproblem parameters.
        
        The solver's get_next_optimal_move handles arbitrary intermediate states,
        so we always pass the full problem specification: move all disks from A to C.
        The solver will recursively determine the correct next move regardless of
        the current disk positions.
        
        Args:
            current_state (dict): Current peg configuration
        
        Returns:
            tuple: (n, source, target, auxiliary)
                - n: number of disks in subproblem
                - source: source peg name
                - target: target peg name
                - auxiliary: auxiliary peg name
        """
        # Always solve the full problem: move all disks from A to C using B as auxiliary
        # The solver will analyze the current state and determine the correct next move
        return self.disk_count, 'A', 'C', 'B'
    
    def format_results(self, is_solvable):
        """
        Format the simulation results for CSV logging.
        
        Args:
            is_solvable (bool): Whether the simulation reached the goal state
        
        Returns:
            dict: Summary data matching DataLogger schema
        """
        # Write detailed move log to file
        log_dir = 'data/raw_move_logs'
        os.makedirs(log_dir, exist_ok=True)
        log_file_path = f"{log_dir}/{self.run_id}.log"
        
        with open(log_file_path, 'w') as log_f:
            log_f.write(f"Run ID: {self.run_id}\n")
            log_f.write(f"Disk Count: {self.disk_count}\n")
            log_f.write(f"Target Alteration %: {self.target_alteration_rate}\n")
            log_f.write(f"Formation Handler: {self.formation_handler_strategy}\n")
            log_f.write(f"Ground Handler: {self.ground_handler_strategy}\n")
            log_f.write(f"Duplicate Handler: {self.duplicate_handler_strategy}\n")
            log_f.write(f"Is Solvable: {is_solvable}\n")
            log_f.write(f"\n{'='*60}\n")
            log_f.write(f"DETAILED MOVE LOG\n")
            log_f.write(f"{'='*60}\n\n")
            log_f.write("\n".join(self.move_log))
        
        # Calculate actual alteration percentage
        if self.total_moves > 0:
            actual_alt_pct = (self.alterations_count / self.total_moves) * 100
        else:
            actual_alt_pct = 0.0
        
        # Return structured data for CSV
        return {
            "run_id": self.run_id,
            "run_timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            "disk_count": self.disk_count,
            "target_alteration_percent": self.target_alteration_rate,
            "illegal_formation_handler": self.formation_handler_strategy,
            "ground_handler": self.ground_handler_strategy,
            "duplicate_handler": self.duplicate_handler_strategy,
            "is_solvable": is_solvable,
            "total_moves_to_solve": self.total_moves if is_solvable else None,
            "total_alterations": self.alterations_count,
            "total_illegal_states": self.illegal_states_count,
            "actual_alteration_percent": actual_alt_pct,
            "raw_move_log_path": log_file_path
        }
