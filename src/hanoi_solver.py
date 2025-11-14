"""
Pure Tower of Hanoi Solver

Implements the classic recursive Tower of Hanoi algorithm.
This solver provides the "ideal" next move for a given state,
assuming no environmental interference.

Key Responsibilities:
1. Determine the optimal next move for any legal Hanoi state
2. Provide the recursive solution strategy
3. Support re-solving from arbitrary intermediate states
"""


class HanoiSolver:
    """
    Classic Tower of Hanoi solver using recursive algorithm.
    
    The solver can determine the next optimal move from any legal state
    by analyzing which disk needs to move next to progress toward the goal.
    """
    
    def __init__(self):
        """Initialize the solver."""
        self.move_sequence = []
        self.cached_solution = []  # Pre-computed solution path
        self.solution_index = 0     # Current position in solution
        self.last_state_hash = None # Track if state was altered
    
    def solve_full(self, n, source='A', target='C', auxiliary='B'):
        """
        Generate the complete sequence of moves for n disks.
        
        This is a helper method for testing and understanding the algorithm.
        The simulation doesn't use this directly, but rather gets moves one at a time.
        
        Args:
            n (int): Number of disks to move
            source (str): Source peg
            target (str): Target peg
            auxiliary (str): Auxiliary peg
        
        Returns:
            list: List of move dictionaries [{'from': 'A', 'to': 'C', 'disk': n}, ...]
        """
        self.move_sequence = []
        self._hanoi_recursive(n, source, target, auxiliary)
        return self.move_sequence
    
    def _hanoi_recursive(self, n, source, target, auxiliary):
        """
        Recursive helper for solving Tower of Hanoi.
        
        Algorithm:
        1. Move n-1 disks from source to auxiliary (using target as spare)
        2. Move disk n from source to target
        3. Move n-1 disks from auxiliary to target (using source as spare)
        """
        if n <= 0:
            return
        
        # Move n-1 disks from source to auxiliary
        self._hanoi_recursive(n - 1, source, auxiliary, target)
        
        # Move disk n from source to target
        self.move_sequence.append({
            'from': source,
            'to': target,
            'disk': n
        })
        
        # Move n-1 disks from auxiliary to target
        self._hanoi_recursive(n - 1, auxiliary, target, source)
    
    def get_next_optimal_move(self, current_state, n, source, target, auxiliary):
        """
        Determine the next optimal move using pre-computed solution path.
        
        Strategy:
        1. If no cached solution exists, generate the full solution from current state
        2. Check if current state matches expected state in solution path
        3. If state was altered (doesn't match), regenerate solution from current state
        4. Return the next move from the solution path
        
        This approach handles alterations by regenerating the solution when needed.
        
        Args:
            current_state (dict): Current peg configuration {'A': [...], 'B': [...], 'C': [...]}
            n (int): Number of disks in the current subproblem
            source (str): Source peg for the current subproblem
            target (str): Target peg for the current subproblem
            auxiliary (str): Auxiliary peg for the current subproblem
        
        Returns:
            dict or None: Move dictionary {'from': str, 'to': str, 'disk': int}
                         Returns None if goal is reached
        """
        if n <= 0:
            return None
        
        # Check if we've reached the goal
        goal = list(range(n, 0, -1))
        if current_state[target] == goal and not current_state[source] and not current_state[auxiliary]:
            return None
        
        # Create a hash of current state to detect alterations
        state_hash = (tuple(current_state['A']), tuple(current_state['B']), tuple(current_state['C']))
        
        # Check if we need to generate/regenerate the solution
        need_regenerate = False
        
        if not self.cached_solution:
            # First call - generate initial solution
            need_regenerate = True
        elif state_hash != self.last_state_hash:
            # State was altered - need to regenerate from current position
            need_regenerate = True
        
        if need_regenerate:
            # Generate solution from current state to goal
            self.cached_solution = self._solve_from_state(current_state, n, target)
            self.solution_index = 0
        
        # Find the next legal move from our cached solution
        while self.solution_index < len(self.cached_solution):
            move = self.cached_solution[self.solution_index]
            
            # Check if this move is legal in current state
            if self._is_move_legal(current_state, move):
                # Simulate the move to update our expected state hash
                simulated_state = self._simulate_move(current_state, move)
                self.last_state_hash = (tuple(simulated_state['A']), 
                                       tuple(simulated_state['B']), 
                                       tuple(simulated_state['C']))
                self.solution_index += 1
                return move
            else:
                # Move is not legal (shouldn't happen with fresh solution)
                # Regenerate and try again
                self.cached_solution = self._solve_from_state(current_state, n, target)
                self.solution_index = 0
                if not self.cached_solution:
                    return None
        
        # Reached end of solution but not at goal - regenerate
        self.cached_solution = self._solve_from_state(current_state, n, target)
        self.solution_index = 0
        if self.cached_solution:
            move = self.cached_solution[0]
            if self._is_move_legal(current_state, move):
                simulated_state = self._simulate_move(current_state, move)
                self.last_state_hash = (tuple(simulated_state['A']), 
                                       tuple(simulated_state['B']), 
                                       tuple(simulated_state['C']))
                self.solution_index = 1
                return move
        
        return None
    
    def _solve_from_state(self, current_state, n, target):
        """
        Generate a solution sequence from an arbitrary state to goal using BFS with pruning.
        
        This finds a path from the current (possibly perturbed) state
        to the goal state where all disks are on the target peg.
        
        Args:
            current_state (dict): Current state
            n (int): Number of disks
            target (str): Target peg
        
        Returns:
            list: Sequence of moves to solve from current state
        """
        from collections import deque
        
        # Goal state: all disks on target peg in order
        goal_pegs = {'A': [], 'B': [], 'C': []}
        goal_pegs[target] = list(range(n, 0, -1))
        goal_state = (tuple(goal_pegs['A']), tuple(goal_pegs['B']), tuple(goal_pegs['C']))
        
        # Initial state as tuple
        start_state = (tuple(current_state['A']), tuple(current_state['B']), tuple(current_state['C']))
        
        # Check if already at goal
        if start_state == goal_state:
            return []
        
        # For disk counts > 4, use a depth-limited search with heuristic
        if n > 4:
            # Use a simpler greedy approach for larger problems
            return self._greedy_solve(current_state, n, target)
        
        # BFS to find shortest path (only for n <= 4)
        queue = deque([(start_state, [])])
        visited = {start_state}
        max_iterations = 10000  # Reduced safety limit
        iterations = 0
        
        while queue and iterations < max_iterations:
            iterations += 1
            state_tuple, path = queue.popleft()
            
            # Convert tuple back to dict for easier manipulation
            state = {
                'A': list(state_tuple[0]),
                'B': list(state_tuple[1]),
                'C': list(state_tuple[2])
            }
            
            # Try all possible legal moves
            for from_peg in ['A', 'B', 'C']:
                if not state[from_peg]:
                    continue
                    
                disk = state[from_peg][-1]
                
                for to_peg in ['A', 'B', 'C']:
                    if from_peg == to_peg:
                        continue
                    
                    # Check if move is legal
                    if state[to_peg] and state[to_peg][-1] < disk:
                        continue
                    
                    # Make the move
                    new_state = {
                        'A': list(state['A']),
                        'B': list(state['B']),
                        'C': list(state['C'])
                    }
                    new_state[from_peg] = new_state[from_peg][:-1]
                    new_state[to_peg] = new_state[to_peg] + [disk]
                    
                    new_state_tuple = (tuple(new_state['A']), tuple(new_state['B']), tuple(new_state['C']))
                    
                    if new_state_tuple in visited:
                        continue
                    
                    visited.add(new_state_tuple)
                    new_path = path + [{'from': from_peg, 'to': to_peg, 'disk': disk}]
                    
                    # Check if we reached the goal
                    if new_state_tuple == goal_state:
                        return new_path
                    
                    queue.append((new_state_tuple, new_path))
        
        # If BFS failed, fall back to greedy approach
        return self._greedy_solve(current_state, n, target)
    
    def _greedy_solve(self, current_state, n, target):
        """
        Greedy solver for larger disk counts (n > 4).
        
        Generates moves by following classic Hanoi pattern but checking current state
        at each step.
        
        Args:
            current_state (dict): Current state
            n (int): Number of disks
            target (str): Target peg
        
        Returns:
            list: Sequence of moves
        """
        # Determine source and auxiliary from target
        pegs = ['A', 'B', 'C']
        other_pegs = [p for p in pegs if p != target]
        source = other_pegs[0]
        auxiliary = other_pegs[1]
        
        # Generate the full ideal solution
        ideal_moves = self.solve_full(n, source, target, auxiliary)
        
        # Simulate through the ideal solution, but verify each move
        # If a move is invalid, try to "fix" the state first
        sim_state = {
            'A': list(current_state['A']),
            'B': list(current_state['B']),
            'C': list(current_state['C'])
        }
        
        result_moves = []
        goal = list(range(n, 0, -1))
        max_moves = len(ideal_moves) * 3  # Allow some extra moves for corrections
        
        ideal_idx = 0
        while ideal_idx < len(ideal_moves) and len(result_moves) < max_moves:
            # Check if we've reached goal
            if sim_state[target] == goal:
                break
            
            ideal_move = ideal_moves[ideal_idx]
            
            # Check if this ideal move is currently legal
            if self._is_move_legal(sim_state, ideal_move):
                # Execute it
                result_moves.append(ideal_move)
                sim_state[ideal_move['from']].remove(ideal_move['disk'])
                sim_state[ideal_move['to']].append(ideal_move['disk'])
                ideal_idx += 1
            else:
                # Can't do ideal move - try to make progress by moving any legal disk
                move_made = False
                for from_peg in [target, source, auxiliary]:
                    if sim_state[from_peg]:
                        disk = sim_state[from_peg][-1]
                        for to_peg in [target, auxiliary, source]:
                            if from_peg != to_peg and self._can_place_disk(sim_state, to_peg, disk):
                                move = {'from': from_peg, 'to': to_peg, 'disk': disk}
                                result_moves.append(move)
                                sim_state[from_peg].remove(disk)
                                sim_state[to_peg].append(disk)
                                move_made = True
                                break
                        if move_made:
                            break
                
                if not move_made:
                    # Stuck - skip to next ideal move
                    ideal_idx += 1
        
        return result_moves
    
    def _is_move_legal(self, state, move):
        """Check if a move is legal in the given state."""
        from_peg = move['from']
        to_peg = move['to']
        disk = move['disk']
        
        # Check disk is on from_peg and is exposed
        if not state[from_peg] or state[from_peg][-1] != disk:
            return False
        
        # Check to_peg can accept the disk
        if state[to_peg] and state[to_peg][-1] < disk:
            return False
        
        return True
    
    def _simulate_move(self, state, move):
        """Simulate a move and return the resulting state."""
        new_state = {
            'A': list(state['A']),
            'B': list(state['B']),
            'C': list(state['C'])
        }
        
        disk = new_state[move['from']].pop()
        new_state[move['to']].append(disk)
        
        return new_state
    
    def _find_disk(self, state, disk):
        """
        Find which peg contains a specific disk.
        
        Args:
            state (dict): Current state
            disk (int): Disk ID to find
        
        Returns:
            str or None: Peg name ('A', 'B', 'C') or None if not found
        """
        for peg_name, peg_disks in state.items():
            if disk in peg_disks:
                return peg_name
        return None
    
    def _is_disk_exposed(self, state, peg, disk):
        """
        Check if a disk is on top of its peg (no disks above it).
        
        Args:
            state (dict): Current state
            peg (str): Peg name
            disk (int): Disk ID
        
        Returns:
            bool: True if disk is exposed, False otherwise
        """
        if peg is None:
            return False
        peg_disks = state[peg]
        if not peg_disks or peg_disks[-1] != disk:
            return False
        return True
    
    def _can_place_disk(self, state, peg, disk):
        """
        Check if a disk can legally be placed on a peg.
        
        Args:
            state (dict): Current state
            peg (str): Target peg
            disk (int): Disk ID to place
        
        Returns:
            bool: True if placement is legal, False otherwise
        """
        peg_disks = state[peg]
        if not peg_disks:
            return True  # Empty peg always accepts
        return peg_disks[-1] > disk  # Top disk must be larger
    
    def get_minimum_moves(self, n):
        """
        Calculate the theoretical minimum number of moves for n disks.
        
        Args:
            n (int): Number of disks
        
        Returns:
            int: Minimum moves = 2^n - 1
        """
        return (2 ** n) - 1
