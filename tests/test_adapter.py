"""
Test script for Vision Adapter with direct move data access.
Tests conversion between vision system (top-to-bottom) and solver (bottom-to-top).
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from vision_adapter import VisionAdapter
from state_solutions.hanoi_state import solve_hanoi_from_image

def print_move_data(moves):
    """Print move data by directly accessing move attributes"""
    print("\n" + "="*70)
    print("MOVE DATA (Direct Attribute Access)")
    print("="*70)
    
    for i, move in enumerate(moves, 1):
        print(f"Move {i}:")
        print(f"  [disk={move.disk}, "
              f"from={move.initial_peg}, "
              f"from_height={move.initial_height}, "
              f"to={move.destination_peg}, "
              f"to_height={move.destination_height}]")
    
    print("="*70)

def test_vision_conversion():
    """Test vision system to solver conversion"""
    adapter = VisionAdapter()
    
    # Simulate vision system output (top to bottom)
    print("\n" + "#"*70)
    print("TEST 1: Vision System Output (Top → Bottom)")
    print("#"*70)
    
    vision_data = {
        'A': [1, 2, 3],  # Top to bottom: small on top
        'B': [],
        'C': []
    }
    
    print("\nVision System Data (top→bottom):")
    print(f"  Peg A: {vision_data['A']}")
    print(f"  Peg B: {vision_data['B']}")
    print(f"  Peg C: {vision_data['C']}")
    
    # Convert to solver format
    solver_data = adapter.convert_vision_to_solver(vision_data)
    
    print("\nSolver Format (bottom→top):")
    print(f"  Peg A: {solver_data['A']}")
    print(f"  Peg B: {solver_data['B']}")
    print(f"  Peg C: {solver_data['C']}")
    
    # Solve using converted data
    initial_state = [solver_data['A'], solver_data['B'], solver_data['C']]
    moves, final_state = solve_hanoi_from_image(initial_state)
    
    print_move_data(moves)
    
    print("\nFinal State (bottom→top):")
    for peg, disks in final_state.pegs.items():
        print(f"  Peg {peg}: {disks}")

def test_scattered_configuration():
    """Test with disks scattered across pegs"""
    adapter = VisionAdapter()
    
    print("\n" + "#"*70)
    print("TEST 2: Scattered Configuration")
    print("#"*70)
    
    # Vision sees: A has disk 3, B has disk 2, C has disk 1
    vision_data = {
        'A': [3],
        'B': [2],
        'C': [1]
    }
    
    print("\nVision System Data (top→bottom):")
    for peg, disks in vision_data.items():
        print(f"  Peg {peg}: {disks}")
    
    # Validate and convert
    adapter.validate_configuration(vision_data)
    solver_data = adapter.convert_vision_to_solver(vision_data)
    
    print("\nSolver Format (bottom→top):")
    for peg, disks in solver_data.items():
        print(f"  Peg {peg}: {disks}")
    
    # Solve
    initial_state = [solver_data['A'], solver_data['B'], solver_data['C']]
    moves, final_state = solve_hanoi_from_image(initial_state)
    
    print_move_data(moves)

def test_complex_stacks():
    """Test with multiple disks on different pegs"""
    adapter = VisionAdapter()
    
    print("\n" + "#"*70)
    print("TEST 3: Complex Multi-Disk Stacks")
    print("#"*70)
    
    # Vision: A has [1,3,4] (top to bottom), B has [2,5], C is empty
    vision_data = {
        'A': [1, 3, 4],
        'B': [2, 5],
        'C': []
    }
    
    print("\nVision System Data (top→bottom):")
    for peg, disks in vision_data.items():
        print(f"  Peg {peg}: {disks}")
    
    # Convert and solve
    solver_data = adapter.convert_vision_to_solver(vision_data)
    
    print("\nSolver Format (bottom→top):")
    for peg, disks in solver_data.items():
        print(f"  Peg {peg}: {disks}")
    
    initial_state = [solver_data['A'], solver_data['B'], solver_data['C']]
    moves, final_state = solve_hanoi_from_image(initial_state)
    
    print_move_data(moves)
    
    print(f"\nTotal moves required: {len(moves)}")

def test_move_attributes():
    """Demonstrate all available move attributes"""
    adapter = VisionAdapter()
    
    print("\n" + "#"*70)
    print("TEST 4: All Move Attributes Demo")
    print("#"*70)
    
    vision_data = {'A': [1, 2], 'B': [3], 'C': []}
    solver_data = adapter.convert_vision_to_solver(vision_data)
    initial_state = [solver_data['A'], solver_data['B'], solver_data['C']]
    
    moves, _ = solve_hanoi_from_image(initial_state)
    
    if moves:
        first_move = moves[0]
        print("\nFirst Move Object Attributes:")
        print(f"  move.disk             = {first_move.disk}")
        print(f"  move.initial_peg      = {first_move.initial_peg}")
        print(f"  move.initial_height   = {first_move.initial_height}")
        print(f"  move.destination_peg  = {first_move.destination_peg}")
        print(f"  move.destination_height = {first_move.destination_height}")
        
        print("\nAll moves in compact format:")
        for i, m in enumerate(moves, 1):
            print(f"  {i}. [{m.disk}, {m.initial_peg}, h{m.initial_height}] "
                  f"→ [{m.destination_peg}, h{m.destination_height}]")

if __name__ == "__main__":
    # Run all tests
    test_vision_conversion()
    test_scattered_configuration()
    test_complex_stacks()
    test_move_attributes()
    
    print("\n" + "="*70)
    print("ALL TESTS COMPLETE")
    print("="*70)