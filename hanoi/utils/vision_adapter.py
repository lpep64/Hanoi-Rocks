"""Utilities for converting between vision-system and solver representations.

Vision representation:
- Peg keys like 'A', 'B', 'C'
- Disk stacks ordered top-to-bottom (smallest first)

Solver representation:
- Peg keys like 'A', 'B', 'C'
- Disk stacks ordered bottom-to-top (largest first)
"""


class VisionAdapter:
    """Converts vision system output to solver input format."""

    def convert_vision_to_solver(self, vision_data):
        """
        Args:
            vision_data: dict with peg names as keys, 
                        arrays of disk sizes (top to bottom)
        Returns:
            dict with peg names as keys,
                 arrays of disk sizes (bottom to top)
        """
        solver_data = {}
        for peg, disks in vision_data.items():
            # Reverse the order: top→bottom becomes bottom→top
            solver_data[peg] = list(reversed(disks))
        return solver_data

    def convert_solver_to_vision(self, solver_data):
        """Convert solver format (bottom→top) back to vision format (top→bottom)."""
        vision_data = {}
        for peg, disks in solver_data.items():
            vision_data[peg] = list(reversed(disks))
        return vision_data
    
    def validate_configuration(self, vision_data):
        """Ensure vision data represents valid Hanoi state"""
        for peg, disks in vision_data.items():
            # Check disks are sorted (small to large top to bottom)
            if disks != sorted(disks):
                raise ValueError(f"Invalid disk order on {peg}")
        return True


def vision_to_solver(vision_data):
    """Convenience wrapper for converting vision-format input to solver format."""
    return VisionAdapter().convert_vision_to_solver(vision_data)


def solver_to_vision(solver_data):
    """Convenience wrapper for converting solver-format input to vision format."""
    return VisionAdapter().convert_solver_to_vision(solver_data)