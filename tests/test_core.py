"""
Comprehensive test suite for hanoi_state.py
Tests Move class, TowerState class, and solve_hanoi_from_image function
Tests various LEGAL configurations for n=3, n=5, and n=7
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from hanoi.core.move import Move, TowerState, solve_hanoi_from_image
import time

def test_move_class():
    """Test the Move class initialization and string representations"""
    print("\n=== Testing Move Class ===")
    
    # Test basic move creation
    move = Move(disk=1, initial_peg='A', initial_height=2, 
                destination_peg='B', destination_height=0)
    
    assert move.disk == 1
    assert move.initial_peg == 'A'
    assert move.initial_height == 2
    assert move.destination_peg == 'B'
    assert move.destination_height == 0
    
    # Test string representation
    assert "disk=1" in repr(move)
    assert "A[h=2]" in repr(move)
    assert "B[h=0]" in repr(move)
    
    print("✓ Move class working correctly")
    

def test_tower_state_initialization():
    """Test TowerState initialization with various configurations"""
    print("\n=== Testing TowerState Initialization ===")
    
    # Test standard initialization
    state1 = TowerState(n=3)
    assert state1.n == 3
    assert state1.pegs['A'] == [3, 2, 1]
    assert state1.pegs['B'] == []
    assert state1.pegs['C'] == []
    print("✓ Standard initialization (n=3)")
    
    # Test from initial state
    state2 = TowerState(initial_state=[[3, 2, 1], [], []])
    assert state2.n == 3
    assert state2.pegs['A'] == [3, 2, 1]
    print("✓ Initialization from initial_state")
    
    # Test with custom peg names
    state3 = TowerState(initial_state=[[2, 1], [], [3]], 
                       source='X', destination='Z', auxiliary='Y')
    assert state3.source == 'X'
    assert state3.destination == 'Z'
    assert state3.auxiliary == 'Y'
    print("✓ Custom peg names")
    
    # Test scattered state
    state4 = TowerState(initial_state=[[3], [2], [1]])
    assert state4.n == 3
    assert state4.pegs['A'] == [3]
    assert state4.pegs['B'] == [2]
    assert state4.pegs['C'] == [1]
    print("✓ Scattered initial state")


def test_tower_state_validation():
    """Test TowerState validation for invalid configurations"""
    print("\n=== Testing TowerState Validation ===")
    
    # Test invalid: wrong number of pegs
    try:
        TowerState(initial_state=[[3, 2, 1], []])
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "exactly 3 lists" in str(e)
        print("✓ Rejects wrong number of pegs")
    
    # Test invalid: empty state
    try:
        TowerState(initial_state=[[], [], []])
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "at least one disk" in str(e)
        print("✓ Rejects empty state")
    
    # Test invalid: disk gaps
    try:
        TowerState(initial_state=[[3, 1], [], []])
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "without duplicates or gaps" in str(e)
        print("✓ Rejects missing disk numbers")
    
    # Test invalid: duplicates
    try:
        TowerState(initial_state=[[2, 1], [2], []])
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "without duplicates or gaps" in str(e)
        print("✓ Rejects duplicate disks")
    
    # Test invalid: larger on top of smaller
    try:
        TowerState(initial_state=[[2, 3, 1], [], []])
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "larger disk on top of smaller" in str(e)
        print("✓ Rejects invalid stacking")


def test_tower_state_methods():
    """Test TowerState helper methods"""
    print("\n=== Testing TowerState Methods ===")
    
    state = TowerState(initial_state=[[3, 2], [1], []])
    
    # Test get_height
    assert state.get_height('A') == 2
    assert state.get_height('B') == 1
    assert state.get_height('C') == 0
    print("✓ get_height method")
    
    # Test find_disk_peg
    assert state.find_disk_peg(1) == 'B'
    assert state.find_disk_peg(2) == 'A'
    assert state.find_disk_peg(3) == 'A'
    print("✓ find_disk_peg method")
    
    # Test find_disk_peg with non-existent disk
    try:
        state.find_disk_peg(99)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "not found" in str(e)
        print("✓ find_disk_peg error handling")
    
    # Test get_auxiliary
    assert state.get_auxiliary('A', 'B') == 'C'
    assert state.get_auxiliary('A', 'C') == 'B'
    assert state.get_auxiliary('B', 'C') == 'A'
    print("✓ get_auxiliary method")
    
    # Test can_place_disk
    assert state.can_place_disk(1, 'A') == True  # 1 can go on 2
    assert state.can_place_disk(3, 'B') == False  # 3 cannot go on 1
    assert state.can_place_disk(1, 'C') == True  # Empty peg
    print("✓ can_place_disk method")


def test_move_disk():
    """Test the move_disk method with height tracking"""
    print("\n=== Testing move_disk Method ===")
    
    state = TowerState(initial_state=[[3, 2, 1], [], []])
    
    # Move disk 1 from A to C
    move1 = state.move_disk('A', 'C')
    assert move1.disk == 1
    assert move1.initial_peg == 'A'
    assert move1.initial_height == 2  # Was at position 2 on A
    assert move1.destination_peg == 'C'
    assert move1.destination_height == 0  # Now at position 0 on C
    assert state.pegs['A'] == [3, 2]
    assert state.pegs['C'] == [1]
    print("✓ Valid move with correct height tracking")
    
    # Move disk 2 from A to B
    move2 = state.move_disk('A', 'B')
    assert move2.disk == 2
    assert move2.initial_height == 1
    assert move2.destination_height == 0
    print("✓ Second move")
    
    # Test invalid move (from empty peg)
    try:
        state.move_disk('C', 'A')  # C only has disk 1
        state.move_disk('C', 'A')  # Now C is empty
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "empty peg" in str(e)
        print("✓ Rejects move from empty peg")
    
    # Test invalid move (larger on smaller)
    state2 = TowerState(initial_state=[[3], [2], [1]])
    try:
        state2.move_disk('A', 'C')  # Cannot place 3 on 1
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Illegal Move" in str(e)
        print("✓ Rejects illegal move (larger on smaller)")


def test_solve_basic_cases():
    """Test solving basic configurations"""
    print("\n=== Testing Basic Solve Cases ===")
    
    # Test already solved
    moves, final = solve_hanoi_from_image([[], [], [3, 2, 1]])
    assert len(moves) == 0
    assert final.pegs['C'] == [3, 2, 1]
    print("✓ Already solved (0 moves)")
    
    # Test standard n=3
    moves, final = solve_hanoi_from_image([[3, 2, 1], [], []])
    assert len(moves) == 7  # 2^3 - 1 = 7
    assert final.pegs['C'] == [3, 2, 1]
    assert final.pegs['A'] == []
    assert final.pegs['B'] == []
    print(f"✓ Standard n=3 ({len(moves)} moves)")
    
    # Test single disk
    moves, final = solve_hanoi_from_image([[1], [], []])
    assert len(moves) == 1
    assert final.pegs['C'] == [1]
    print(f"✓ Single disk ({len(moves)} move)")
    
    # Test two disks
    moves, final = solve_hanoi_from_image([[2, 1], [], []])
    assert len(moves) == 3  # 2^2 - 1 = 3
    assert final.pegs['C'] == [2, 1]
    print(f"✓ Two disks ({len(moves)} moves)")


def test_solve_scattered_states():
    """Test solving scattered configurations"""
    print("\n=== Testing Scattered State Solutions ===")
    
    # n=3: All separate
    moves, final = solve_hanoi_from_image([[3], [2], [1]])
    assert final.pegs['C'] == [3, 2, 1]
    assert final.pegs['A'] == []
    assert final.pegs['B'] == []
    print(f"✓ n=3: All separate pegs ({len(moves)} moves)")
    
    # n=3: Reverse spread
    moves, final = solve_hanoi_from_image([[1], [2], [3]])
    assert final.pegs['C'] == [3, 2, 1]
    print(f"✓ n=3: Reverse spread ({len(moves)} moves)")
    
    # n=3: Two on A, one on B
    moves, final = solve_hanoi_from_image([[3, 1], [2], []])
    assert final.pegs['C'] == [3, 2, 1]
    print(f"✓ n=3: Two on A, one on B ({len(moves)} moves)")


def test_move_height_tracking():
    """Test that height tracking is accurate throughout solving"""
    print("\n=== Testing Height Tracking ===")
    
    initial = [[3, 2, 1], [], []]
    moves, final = solve_hanoi_from_image(initial)
    
    # Verify first move
    assert moves[0].disk == 1
    assert moves[0].initial_height == 2
    assert moves[0].destination_height == 0
    print("✓ First move heights correct")
    
    # Verify all moves have valid heights
    for move in moves:
        assert move.initial_height >= 0
        assert move.destination_height >= 0
        assert isinstance(move.disk, int)
    print(f"✓ All {len(moves)} moves have valid height tracking")


def test_comprehensive_configurations():
    """Test comprehensive set of valid configurations"""
    print("\n=== Testing Comprehensive Configurations ===")
    
    test_cases = [
        # n=3 configurations
        {'name': 'n=3: Standard', 'state': [[3, 2, 1], [], []]},
        {'name': 'n=3: All on B', 'state': [[], [3, 2, 1], []]},
        {'name': 'n=3: All on C (solved)', 'state': [[], [], [3, 2, 1]]},
        {'name': 'n=3: Spread evenly', 'state': [[3], [2], [1]]},
        {'name': 'n=3: Two-one split', 'state': [[3, 2], [], [1]]},
        
        # n=5 configurations
        {'name': 'n=5: Standard', 'state': [[5, 4, 3, 2, 1], [], []]},
        {'name': 'n=5: All on B', 'state': [[], [5, 4, 3, 2, 1], []]},
        {'name': 'n=5: Mixed', 'state': [[5, 4], [3, 2], [1]]},
        {'name': 'n=5: Complex', 'state': [[4, 1], [3, 2], [5]]},
        
        # n=7 configurations
        {'name': 'n=7: Standard', 'state': [[7, 6, 5, 4, 3, 2, 1], [], []]},
        {'name': 'n=7: Scattered', 'state': [[7, 5, 3], [6, 4], [2, 1]]},
    ]
    
    passed = 0
    for test_case in test_cases:
        try:
            moves, final = solve_hanoi_from_image(test_case['state'])
            
            # Verify solution is correct
            n = max([disk for peg in test_case['state'] for disk in peg])
            expected_final = list(range(n, 0, -1))
            
            assert final.pegs['C'] == expected_final, f"Final state incorrect for {test_case['name']}"
            assert final.pegs['A'] == []
            assert final.pegs['B'] == []
            
            # Verify no disk moved twice in a row
            for i in range(len(moves) - 1):
                assert moves[i].disk != moves[i+1].disk, f"Disk {moves[i].disk} moved twice in a row"
            
            passed += 1
            print(f"✓ {test_case['name']}: {len(moves)} moves")
            
        except Exception as e:
            print(f"✗ {test_case['name']}: {e}")
    
    print(f"\nPassed {passed}/{len(test_cases)} comprehensive tests")


def test_optimality():
    """Verify that standard cases produce optimal move counts"""
    print("\n=== Testing Optimality ===")
    
    # Standard positions should produce 2^n - 1 moves
    test_cases = [
        ([[1], [], []], 1, 2**1 - 1),
        ([[2, 1], [], []], 2, 2**2 - 1),
        ([[3, 2, 1], [], []], 3, 2**3 - 1),
        ([[4, 3, 2, 1], [], []], 4, 2**4 - 1),
        ([[5, 4, 3, 2, 1], [], []], 5, 2**5 - 1),
    ]
    
    for state, n, expected_moves in test_cases:
        moves, final = solve_hanoi_from_image(state)
        assert len(moves) == expected_moves, f"n={n}: expected {expected_moves}, got {len(moves)}"
        print(f"✓ n={n}: {len(moves)} moves (optimal)")


def test_custom_peg_names():
    """Test solving with custom peg names"""
    print("\n=== Testing Custom Peg Names ===")
    
    moves, final = solve_hanoi_from_image(
        [[3, 2, 1], [], []],
        source='X',
        destination='Z',
        auxiliary='Y'
    )
    
    assert final.pegs['Z'] == [3, 2, 1]
    assert final.pegs['X'] == []
    assert final.pegs['Y'] == []
    
    # Verify moves use custom peg names
    for move in moves:
        assert move.initial_peg in ['X', 'Y', 'Z']
        assert move.destination_peg in ['X', 'Y', 'Z']
    
    print(f"✓ Custom peg names work correctly ({len(moves)} moves)")


def run_performance_test():
    """Test performance on larger configurations"""
    print("\n=== Performance Test ===")
    
    test_cases = [
        ([[5, 4, 3, 2, 1], [], []], 5),
        ([[7, 6, 5, 4, 3, 2, 1], [], []], 7),
        ([[8, 7, 6, 5, 4, 3, 2, 1], [], []], 8),
    ]
    
    for state, n in test_cases:
        start = time.time()
        moves, final = solve_hanoi_from_image(state)
        elapsed = time.time() - start
        
        expected = 2**n - 1
        assert len(moves) == expected
        assert final.pegs['C'] == list(range(n, 0, -1))
        
        print(f"✓ n={n}: {len(moves)} moves in {elapsed:.4f}s")


def main():
    """Run all tests"""
    print("=" * 70)
    print("COMPREHENSIVE TEST SUITE FOR HANOI_STATE.PY")
    print("=" * 70)
    
    try:
        test_move_class()
        test_tower_state_initialization()
        test_tower_state_validation()
        test_tower_state_methods()
        test_move_disk()
        test_solve_basic_cases()
        test_solve_scattered_states()
        test_move_height_tracking()
        test_comprehensive_configurations()
        test_optimality()
        test_custom_peg_names()
        run_performance_test()
        
        print("\n" + "=" * 70)
        print("ALL TESTS PASSED! ✓")
        print("=" * 70)
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        raise


if __name__ == "__main__":
    main()
