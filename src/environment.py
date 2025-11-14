"""
Environment Manager for Real-World Tower of Hanoi

Represents the 'real-world' state of the three pegs.
Manages the state, applies moves, and introduces alterations.

Key Responsibilities:
1. Maintain the current state of pegs A, B, C and the ground
2. Apply legal Hanoi moves between pegs
3. Introduce random alterations (perturbations) to create illegal states
4. Detect and classify illegal states
"""

import random
import copy


class Environment:
    """
    Manages the physical state of the Tower of Hanoi system.
    
    Attributes:
        pegs (dict): Dictionary with keys 'A', 'B', 'C' containing lists of disks.
                     Each list represents a stack where index 0 is the bottom.
        disk_count (int): The total number of disks in the problem.
        ground (list): Disks that have fallen to the ground (not on any peg).
        all_disk_ids (set): Set of all valid disk IDs for duplicate detection.
    """
    
    def __init__(self, disk_count):
        """
        Initialize the environment with all disks on peg A.
        
        Args:
            disk_count (int): Number of disks (typically 3, 5, 7, or 9)
        """
        # Initialize pegs: bottom-to-top, so largest disk (disk_count) is at index 0
        self.pegs = {
            'A': list(range(disk_count, 0, -1)),  # [disk_count, ..., 2, 1]
            'B': [],
            'C': []
        }
        self.disk_count = disk_count
        self.ground = []  # Disks that are not on any peg
        self.all_disk_ids = set(range(1, disk_count + 1))
    
    def get_state(self):
        """
        Returns a deep copy of the current peg state.
        
        Returns:
            dict: Deep copy of self.pegs with structure {'A': [...], 'B': [...], 'C': [...]}
        """
        return {peg: list(disks) for peg, disks in self.pegs.items()}
    
    def apply_move(self, from_peg, to_peg):
        """
        Applies a single move from one peg to another.
        Validates the move according to Hanoi rules.
        
        Args:
            from_peg (str): Source peg name ('A', 'B', or 'C')
            to_peg (str): Destination peg name ('A', 'B', or 'C')
        
        Returns:
            tuple: (success: bool, reason: str)
                - success: True if move was applied, False otherwise
                - reason: Description of result or error
        """
        # Check if source peg is empty
        if not self.pegs[from_peg]:
            return False, "EmptySource"
        
        # Get the top disk from source peg
        disk = self.pegs[from_peg][-1]  # Peek at top disk
        
        # Check if destination peg has a smaller disk on top (illegal Hanoi move)
        if self.pegs[to_peg] and self.pegs[to_peg][-1] < disk:
            return False, "IllegalHanoiMove"
        
        # Move is legal, execute it
        disk = self.pegs[from_peg].pop()
        self.pegs[to_peg].append(disk)
        return True, "Success"
    
    def introduce_alteration(self, alteration_percent):
        """
        Called after each successful move to potentially introduce a random alteration.
        Based on the percentage, randomly decides to create one of three illegal states:
        1. Move a disk to the ground
        2. Duplicate a disk on a peg
        3. Create an illegal formation (large disk on small disk)
        
        Args:
            alteration_percent (float): Probability (0-100) of introducing an alteration
        
        Returns:
            bool: True if an alteration was introduced, False otherwise
        """
        if random.random() < alteration_percent / 100.0:
            # Try to introduce an alteration - keep trying until one succeeds
            attempts = 0
            max_attempts = 10  # Prevent infinite loop
            
            while attempts < max_attempts:
                attempts += 1
                
                # Choose a random alteration type
                alteration_type = random.choice(['ground', 'duplicate', 'illegal_formation'])
                
                if alteration_type == 'ground':
                    # Move a random disk from a non-empty peg to the ground
                    non_empty_pegs = [p for p in ['A', 'B', 'C'] if self.pegs[p]]
                    if non_empty_pegs:
                        peg = random.choice(non_empty_pegs)
                        disk = self.pegs[peg].pop()
                        self.ground.append(disk)
                        return True
                
                elif alteration_type == 'duplicate':
                    # Duplicate a random disk on any peg
                    non_empty_pegs = [p for p in ['A', 'B', 'C'] if self.pegs[p]]
                    if non_empty_pegs:
                        source_peg = random.choice(non_empty_pegs)
                        target_peg = random.choice(['A', 'B', 'C'])
                        # Pick a random disk from source peg
                        disk_to_duplicate = random.choice(self.pegs[source_peg])
                        # Add duplicate to target peg (may violate stacking rules, but that's ok)
                        self.pegs[target_peg].append(disk_to_duplicate)
                        return True
                
                elif alteration_type == 'illegal_formation':
                    # Create an illegal stack by placing a large disk on top of a small disk
                    # Simplified: just pick any two non-empty pegs and try to create violation
                    non_empty_pegs = [p for p in ['A', 'B', 'C'] if self.pegs[p]]
                    if len(non_empty_pegs) >= 2:
                        # Pick two different pegs
                        source_peg = random.choice(non_empty_pegs)
                        other_pegs = [p for p in non_empty_pegs if p != source_peg]
                        target_peg = random.choice(other_pegs)
                        
                        # Get a disk from source
                        disk = self.pegs[source_peg].pop()
                        
                        # Find a target peg with a smaller top disk
                        if self.pegs[target_peg] and self.pegs[target_peg][-1] < disk:
                            # Can create illegal formation
                            self.pegs[target_peg].append(disk)
                            return True
                        else:
                            # Can't create illegal formation with this combo
                            self.pegs[source_peg].append(disk)
                            # Try again with different alteration type
                            continue
                    elif len(non_empty_pegs) == 1:
                        # Only one peg has disks - try duplicate or ground instead
                        # Force a different type
                        continue
            
            # All attempts failed - return False
            # This can happen in edge cases (e.g., all disks on one peg, can't form illegal formation)
            return False
        
        return False
    
    def check_for_illegal_states(self):
        """
        Scans the environment for violations in a specific priority order:
        1. Element on ground (highest priority)
        2. Duplicate disks
        3. Illegal formation (large disk on small disk)
        
        Returns:
            tuple: (violation_type: str, details: Any)
                - violation_type: One of "ElementOnGround", "DuplicateItem", 
                                 "IllegalFormation", or "Legal"
                - details: Contextual information about the violation
                    - For ElementOnGround: the disk ID on the ground
                    - For DuplicateItem: the duplicate disk ID
                    - For IllegalFormation: (peg_name, index) tuple
                    - For Legal: None
        """
        # Priority 1: Check if any element is on the ground
        if self.ground:
            return "ElementOnGround", self.ground[0]  # Return first disk on ground
        
        # Priority 2: Check for duplicate disks across all pegs
        all_disks = []
        for peg in self.pegs.values():
            all_disks.extend(peg)
        
        seen = set()
        for disk in all_disks:
            if disk in seen:
                return "DuplicateItem", disk
            seen.add(disk)
        
        # Priority 3: Check for illegal formations (large disk on small disk)
        # In our representation: list[0] = bottom, list[-1] = top
        # Legal stack: disks decrease in size from bottom to top
        # Illegal: disk[i] < disk[i+1] (smaller disk below larger disk)
        for peg_name, peg_disks in self.pegs.items():
            for i in range(len(peg_disks) - 1):
                # i is below i+1 in the stack
                if peg_disks[i] < peg_disks[i + 1]:
                    # Found illegal formation: smaller disk is below larger disk
                    return "IllegalFormation", (peg_name, i)
        
        # No violations found
        return "Legal", None
    
    def get_total_disks(self):
        """
        Count total disks across all pegs and ground.
        Useful for sanity checks.
        
        Returns:
            int: Total number of disks in the system
        """
        total = sum(len(peg) for peg in self.pegs.values()) + len(self.ground)
        return total
    
    def __repr__(self):
        """String representation of the environment for debugging."""
        return f"Environment(A={self.pegs['A']}, B={self.pegs['B']}, C={self.pegs['C']}, Ground={self.ground})"
