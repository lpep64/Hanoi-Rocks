class VisionAdapter:
    """Converts vision system output to solver input format"""
    
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
    
    def validate_configuration(self, vision_data):
        """Ensure vision data represents valid Hanoi state"""
        for peg, disks in vision_data.items():
            # Check disks are sorted (small to large top to bottom)
            if disks != sorted(disks):
                raise ValueError(f"Invalid disk order on {peg}")
        return True