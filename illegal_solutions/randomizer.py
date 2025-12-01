"""
Tower of Hanoi - Environment Randomizer
Simulates physical testbed errors by randomly corrupting state:
- Move disk to random location (67%)
- Remove disk from existence (33%)

Note: 'Add disk' corruption removed to keep problem solvable.
"""

import random
from typing import List, Tuple, Dict, Optional


class Randomizer:
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize randomizer with optional seed for reproducibility.
        
        Args:
            seed: Random seed for reproducibility (None for no seeding)
        """
        self.seed = seed
        if seed is not None:
            random.seed(seed)
        
        # Define peg indices
        self.PEG_A = 0
        self.PEG_B = 1
        self.PEG_C = 2
        self.PEG_QUEUE = 3
        self.PEG_GROUND = 4
        
        self.peg_names = {0: 'A', 1: 'B', 2: 'C', 3: 'Queue', 4: 'Ground'}
    
    def should_corrupt(self, corruption_rate: float) -> bool:
        """
        Determine if corruption should occur based on rate.
        
        Args:
            corruption_rate: Probability of corruption (e.g., 0.05 for 5%, 0.10 for 10%)
        
        Returns:
            bool: True if corruption should occur
        """
        return random.random() < corruption_rate
    
    def get_all_disks_with_locations(self, state: List[List[int]]) -> List[Tuple[int, int, int]]:
        """
        Get all disks with their locations.
        
        Returns:
            List of tuples: (disk_size, peg_index, height_on_peg)
        """
        disks = []
        for peg_idx in range(5):
            for height, disk in enumerate(state[peg_idx]):
                disks.append((disk, peg_idx, height))
        return disks
    
    def get_max_disk_size(self, state: List[List[int]]) -> int:
        """
        Get the maximum disk size currently in the state.
        Returns 0 if no disks exist.
        """
        all_disks = []
        for peg in state:
            all_disks.extend(peg)
        return max(all_disks) if all_disks else 0
    
    def select_corruption_type(self) -> str:
        """
        Select corruption type based on probabilities:
        - 67% move (2/3)
        - 33% remove (1/3)
        - NO add disk (removed to keep problem solvable)
        
        Returns:
            str: 'move' or 'remove'
        """
        rand_val = random.random()
        if rand_val < 0.67:
            return 'move'
        else:
            return 'remove'
    
    def corrupt_state(self, state: List[List[int]], corruption_rate: float) -> Optional[Dict]:
        """
        Apply corruption to state if random check passes.
        Modifies state in-place and returns corruption details.
        
        Args:
            state: The 5-array state [A, B, C, Queue, Ground]
            corruption_rate: Probability of corruption (0.05 or 0.10)
        
        Returns:
            Dict with corruption details, or None if no corruption occurred
            {
                'type': 'move'|'remove'|'add',
                'disk': disk_size,
                'from_peg': peg_index (for move/remove),
                'from_height': height (for move/remove),
                'to_peg': peg_index (for move/add),
                'to_height': height (for move/add)
            }
        """
        if not self.should_corrupt(corruption_rate):
            return None
        
        corruption_type = self.select_corruption_type()
        
        if corruption_type == 'move':
            return self._corrupt_move(state)
        else:  # 'remove'
            return self._corrupt_remove(state)
    
    def _corrupt_move(self, state: List[List[int]]) -> Optional[Dict]:
        """
        Move a random disk to a random location.
        """
        disks = self.get_all_disks_with_locations(state)
        if not disks:
            return None  # No disks to move
        
        # Select random disk
        disk_size, from_peg, from_height = random.choice(disks)
        
        # Remove disk from current location
        state[from_peg].remove(disk_size)
        
        # Select random destination peg
        to_peg = random.randint(0, 4)
        
        # Select random height on destination peg (or append to top)
        if state[to_peg]:
            # Insert at random position (including append)
            to_height = random.randint(0, len(state[to_peg]))
            state[to_peg].insert(to_height, disk_size)
        else:
            # Empty peg, place at bottom
            to_height = 0
            state[to_peg].append(disk_size)
        
        return {
            'type': 'move',
            'disk': disk_size,
            'from_peg': self.peg_names[from_peg],
            'from_height': from_height,
            'to_peg': self.peg_names[to_peg],
            'to_height': to_height
        }
    
    def _corrupt_remove(self, state: List[List[int]]) -> Optional[Dict]:
        """
        Remove a random disk from existence.
        """
        disks = self.get_all_disks_with_locations(state)
        if not disks:
            return None  # No disks to remove
        
        # Select random disk
        disk_size, from_peg, from_height = random.choice(disks)
        
        # Remove disk permanently
        state[from_peg].remove(disk_size)
        
        return {
            'type': 'remove',
            'disk': disk_size,
            'from_peg': self.peg_names[from_peg],
            'from_height': from_height
        }
    
    def _corrupt_add(self, state: List[List[int]]) -> Dict:
        """
        Add a new disk of size (current_max + 1) at random location.
        Note: This method is kept for backward compatibility but not used in current corruption flow.
        """
        max_disk = self.get_max_disk_size(state)
        new_disk = max_disk + 1
        
        # Select random destination peg
        to_peg = random.randint(0, 4)
        
        # Select random height on destination peg
        if state[to_peg]:
            to_height = random.randint(0, len(state[to_peg]))
            state[to_peg].insert(to_height, new_disk)
        else:
            to_height = 0
            state[to_peg].append(new_disk)
        
        return {
            'type': 'add',
            'disk': new_disk,
            'to_peg': self.peg_names[to_peg],
            'to_height': to_height
        }
    
    def create_corrupted_initial_state(self, n: int = 5, num_corruptions: int = 3) -> List[List[int]]:
        """
        Create initial state starting from legal tower on A, then apply corruptions.
        Guarantees at least 1 ground disk and 1 stack violation.
        
        Args:
            n: Number of disks (default 5)
            num_corruptions: Number of corruption operations to apply
        
        Returns:
            Corrupted state [A, B, C, Queue, Ground]
        """
        # Start with legal state on Peg A
        state = [list(range(n, 0, -1)), [], [], [], []]
        
        # Ensure at least 1 disk goes to ground
        ground_disk = random.choice(range(1, n + 1))
        state[self.PEG_A].remove(ground_disk)
        state[self.PEG_GROUND].append(ground_disk)
        
        # Apply random corruptions (only moves now)
        for _ in range(num_corruptions - 1):
            self._corrupt_move(state)
        
        # Ensure at least 1 stack violation exists on A, B, or C
        # Check current state
        has_violation = False
        for peg_idx in [self.PEG_A, self.PEG_B, self.PEG_C]:
            peg = state[peg_idx]
            for i in range(len(peg) - 1):
                if peg[i] < peg[i + 1]:  # Violation: larger on top of smaller
                    has_violation = True
                    break
            if has_violation:
                break
        
        # If no violation, create one
        if not has_violation:
            # Find a peg with at least 2 disks
            target_peg = None
            for peg_idx in [self.PEG_A, self.PEG_B, self.PEG_C]:
                if len(state[peg_idx]) >= 2:
                    target_peg = peg_idx
                    break
            
            if target_peg is not None:
                # Swap top two disks to create violation
                state[target_peg][-1], state[target_peg][-2] = state[target_peg][-2], state[target_peg][-1]
            else:
                # Not enough disks on standard pegs, force a violation
                # Move any disk from ground/queue to a peg with a smaller disk
                for peg_idx in [self.PEG_GROUND, self.PEG_QUEUE]:
                    if state[peg_idx]:
                        disk = state[peg_idx].pop()
                        # Place on peg with smaller disk
                        for target in [self.PEG_A, self.PEG_B, self.PEG_C]:
                            if state[target] and state[target][-1] < disk:
                                state[target].append(disk)
                                break
                        else:
                            # If no suitable target, just place on A
                            state[self.PEG_A].append(disk)
                        break
        
        return state


if __name__ == "__main__":
    # Test corruption mechanisms
    print("="*60)
    print("Randomizer Test Suite")
    print("="*60)
    
    # Test 1: Seeded randomness for reproducibility
    print("\nTest 1: Seeded Randomness (seed=42)")
    rand1 = Randomizer(seed=42)
    state1 = [[5, 4, 3], [2], [1], [], []]
    result1 = rand1.corrupt_state(state1, corruption_rate=1.0)  # Force corruption
    print(f"Corruption: {result1}")
    print(f"State after: {state1}")
    
    # Test 2: Move corruption
    print("\nTest 2: Move Corruption")
    rand2 = Randomizer(seed=100)
    state2 = [[5, 4], [3, 2], [1], [], []]
    for i in range(3):
        result = rand2.corrupt_state(state2, corruption_rate=1.0)
        if result and result['type'] == 'move':
            print(f"  Move {i+1}: Disk {result['disk']} from {result['from_peg']} to {result['to_peg']}")
            print(f"    State: {state2}")
            break
    
    # Test 3: Remove corruption
    print("\nTest 3: Remove Corruption")
    rand3 = Randomizer(seed=200)
    state3 = [[5, 4], [3, 2], [1], [], []]
    initial_count = sum(len(p) for p in state3)
    for _ in range(10):
        result = rand3.corrupt_state(state3, corruption_rate=1.0)
        if result and result['type'] == 'remove':
            print(f"  Removed disk {result['disk']} from {result['from_peg']}")
            print(f"    State: {state3}")
            print(f"    Disk count: {initial_count} -> {sum(len(p) for p in state3)}")
            break
    
    # Test 4: Add corruption
    print("\nTest 4: Add Corruption")
    rand4 = Randomizer(seed=300)
    state4 = [[5, 4], [3, 2], [1], [], []]
    initial_max = rand4.get_max_disk_size(state4)
    for _ in range(10):
        result = rand4.corrupt_state(state4, corruption_rate=1.0)
        if result and result['type'] == 'add':
            print(f"  Added disk {result['disk']} to {result['to_peg']}")
            print(f"    State: {state4}")
            print(f"    Max disk: {initial_max} -> {rand4.get_max_disk_size(state4)}")
            break
    
    # Test 5: Corruption rate check
    print("\nTest 5: Corruption Rate (10% over 100 trials)")
    rand5 = Randomizer(seed=400)
    corruption_count = 0
    for _ in range(100):
        state5 = [[5, 4, 3, 2, 1], [], [], [], []]
        result = rand5.corrupt_state(state5, corruption_rate=0.10)
        if result:
            corruption_count += 1
    print(f"  Corruptions: {corruption_count}/100 (expected ~10)")
    
    # Test 6: Create corrupted initial state
    print("\nTest 6: Create Corrupted Initial State")
    rand6 = Randomizer(seed=500)
    state6 = rand6.create_corrupted_initial_state(n=5, num_corruptions=3)
    print(f"  State: {state6}")
    print(f"  Ground disks: {state6[4]}")
    print(f"  Has ground disk: {len(state6[4]) > 0}")
    
    # Check for stack violation
    has_violation = False
    for peg_idx in [0, 1, 2]:
        peg = state6[peg_idx]
        for i in range(len(peg) - 1):
            if peg[i] < peg[i + 1]:
                has_violation = True
                print(f"  Stack violation found on peg {rand6.peg_names[peg_idx]}")
                break
    print(f"  Has stack violation: {has_violation}")
