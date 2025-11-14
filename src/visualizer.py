"""
ASCII Visualizer for Tower of Hanoi

Simple text-based real-time visualizer for the Tower of Hanoi simulation.
Displays the current state of all three pegs, disks on the ground,
and simulation statistics.
"""

import os
import sys


class HanoiVisualizer:
    """
    ASCII-based visualizer for Tower of Hanoi state.
    
    Draws the current configuration of pegs, disks, and ground state
    in a human-readable format in the terminal.
    """
    
    def __init__(self, initial_pegs, disk_count):
        """
        Initialize the visualizer.
        
        Args:
            initial_pegs (dict): Initial peg configuration (not used, but kept for API compatibility)
            disk_count (int): Maximum number of disks in the simulation
        """
        self.disk_count = disk_count
        # Calculate width for each peg column
        # Each disk is represented by '=' symbols, widest disk needs (disk_count * 2) characters
        self.peg_width = (self.disk_count * 2) + 3
    
    def clear_screen(self):
        """Clear the terminal screen for redrawing."""
        # Windows
        if os.name == 'nt':
            os.system('cls')
        # Unix/Linux/Mac
        else:
            os.system('clear')
    
    def get_disk_str(self, disk_size):
        """
        Create a string representation of a disk.
        
        Args:
            disk_size (int): Size of the disk (0 means empty space)
        
        Returns:
            str: Centered string representation of the disk
        """
        if disk_size == 0:
            # Empty space
            return "|".center(self.peg_width)
        
        # Create disk representation with '=' symbols
        # Disk size 1 = "=", size 2 = "==", size 3 = "===", etc.
        disk_chars = "=" * disk_size
        return disk_chars.center(self.peg_width)
    
    def draw(self, pegs, ground, status_message):
        """
        Draw the current state of the Tower of Hanoi simulation.
        
        Args:
            pegs (dict): Current peg configuration {'A': [...], 'B': [...], 'C': [...]}
                        List format: [bottom, ..., top]
            ground (list): List of disk IDs currently on the ground
            status_message (str): Status text to display (e.g., "Move: 42 / Alterations: 5")
        """
        self.clear_screen()
        
        # Header
        print("=" * (self.peg_width * 3 + 6))
        print("   Real-Time Tower of Hanoi Simulation".center(self.peg_width * 3 + 6))
        print("=" * (self.peg_width * 3 + 6))
        print()
        
        # Create padded copies of pegs for uniform display
        # Pad each peg to disk_count height with zeros (empty spaces)
        padded_pegs = {}
        for peg_name in ['A', 'B', 'C']:
            stack = list(pegs[peg_name])
            # Pad with zeros to reach disk_count height
            while len(stack) < self.disk_count:
                stack.append(0)
            padded_pegs[peg_name] = stack
        
        # Draw pegs from top to bottom
        # Index disk_count-1 is the top of the tower
        for level in range(self.disk_count - 1, -1, -1):
            disk_a = self.get_disk_str(padded_pegs['A'][level])
            disk_b = self.get_disk_str(padded_pegs['B'][level])
            disk_c = self.get_disk_str(padded_pegs['C'][level])
            print(f"{disk_a}  {disk_b}  {disk_c}")
        
        # Draw base line
        base = "─" * self.peg_width
        print(f"{base}  {base}  {base}")
        
        # Draw peg labels
        peg_a = "Peg A".center(self.peg_width)
        peg_b = "Peg B".center(self.peg_width)
        peg_c = "Peg C".center(self.peg_width)
        print(f"{peg_a}  {peg_b}  {peg_c}")
        
        print()
        print("=" * (self.peg_width * 3 + 6))
        
        # Display ground state
        if ground:
            ground_str = ", ".join([f"Disk {d}" for d in ground])
            print(f"ON GROUND: {ground_str}")
        else:
            print("ON GROUND: (empty)")
        
        # Display status
        print(f"STATUS: {status_message}")
        print("=" * (self.peg_width * 3 + 6))
        
        # Flush output to ensure immediate display
        sys.stdout.flush()
    
    def draw_final(self, pegs, ground, is_solvable, total_moves, alterations, illegal_states):
        """
        Draw the final state with summary statistics.
        
        Args:
            pegs (dict): Final peg configuration
            ground (list): Final ground state
            is_solvable (bool): Whether the simulation succeeded
            total_moves (int): Total moves executed
            alterations (int): Total alterations introduced
            illegal_states (int): Total illegal states encountered
        """
        self.draw(pegs, ground, "SIMULATION COMPLETE")
        
        print()
        print("FINAL RESULTS:")
        print(f"  Solvable: {'YES' if is_solvable else 'NO'}")
        print(f"  Total Moves: {total_moves}")
        print(f"  Total Alterations: {alterations}")
        print(f"  Total Illegal States: {illegal_states}")
        if total_moves > 0:
            actual_pct = (alterations / total_moves) * 100
            print(f"  Actual Alteration %: {actual_pct:.2f}%")
        print()
