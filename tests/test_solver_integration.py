"""
Integration test for hanoi_final_flag.py master solver
Tests complete workflow with various edge cases
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from hanoi_final_flag import solve_hanoi, UnsolvableStateError


def test_standard_legal_state():
    """Test with standard legal starting state"""
    print("\n=== Test 1: Standard Legal State ===")
    state = [[3, 2, 1], [], [], [], []]
    flags = {
        'target_peg': 2,
        'duplicate_strategy': 'discard',
        'ground_strategy': 'greedy_3',
        'illegal_resolution': 'bfs_3peg'
    }
    
    moves = solve_hanoi(state, flags)
    print(f"✓ Solved in {len(moves)} moves")
    assert len(moves) > 0, f"Expected moves > 0"


def test_ground_disks():
    """Test ground disk retrieval"""
    print("\n=== Test 2: Ground Disks ===")
    state = [
        [5, 3],
        [4],
        [],
        [],
        [2, 1]
    ]
    flags = {
        'target_peg': 2,
        'duplicate_strategy': 'discard',
        'ground_strategy': 'greedy_3',
        'illegal_resolution': 'bfs_3peg'
    }
    
    moves = solve_hanoi(state, flags)
    print(f"✓ Solved in {len(moves)} moves")
    assert len(moves) > 0


def test_illegal_stacking():
    """Test illegal stack resolution"""
    print("\n=== Test 3: Illegal Stacking ===")
    state = [
        [1, 2],  # Illegal: 2 on top of 1
        [3],
        [],
        [],
        []
    ]
    flags = {
        'target_peg': 2,
        'duplicate_strategy': 'discard',
        'ground_strategy': 'greedy_3',
        'illegal_resolution': 'bfs_3peg'
    }
    
    moves = solve_hanoi(state, flags)
    print(f"✓ Solved in {len(moves)} moves")
    assert len(moves) > 0


def test_duplicate_discard():
    """Test duplicate disk handling with discard strategy"""
    print("\n=== Test 4: Duplicate Disks (Discard) ===")
    state = [
        [3, 2, 2, 1],  # Two disk 2s
        [],
        [],
        [],
        []
    ]
    flags = {
        'target_peg': 2,
        'duplicate_strategy': 'discard',
        'ground_strategy': 'greedy_3',
        'illegal_resolution': 'bfs_3peg'
    }
    
    moves = solve_hanoi(state, flags)
    print(f"✓ Solved in {len(moves)} moves (duplicates discarded)")
    assert len(moves) > 0  # Should solve successfully after discarding duplicate


def test_different_target():
    """Test solving to different target peg"""
    print("\n=== Test 5: Different Target (Peg A) ===")
    state = [[3, 2, 1], [], [], [], []]
    flags = {
        'target_peg': 0,  # Target A instead of C
        'duplicate_strategy': 'discard',
        'ground_strategy': 'greedy_3',
        'illegal_resolution': 'bfs_3peg'
    }
    
    moves = solve_hanoi(state, flags)
    print(f"✓ Solved in {len(moves)} moves (to Peg A)")
    assert len(moves) == 0  # Already on target peg


if __name__ == "__main__":
    print("="*70)
    print("MASTER SOLVER INTEGRATION TESTS")
    print("="*70)
    
    try:
        test_standard_legal_state()
        test_ground_disks()
        test_illegal_stacking()
        test_duplicate_discard()
        test_different_target()
        
        print("\n" + "="*70)
        print("ALL INTEGRATION TESTS PASSED! ✓")
        print("="*70)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
