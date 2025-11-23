"""
Comprehensive test suite for hanoi_image.py
Tests various LEGAL configurations for n=3, n=5, and n=7
All configurations ensure no larger disks are on top of smaller ones
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'state_solutions'))
from hanoi_image import solve_hanoi_from_image
import time

# Comprehensive test cases with legal configurations
test_cases = [
    # ========== n=3 configurations ==========
    {'name': 'n=3: Standard (all on A)', 'state': [[3, 2, 1], [], []]},
    {'name': 'n=3: All on B', 'state': [[], [3, 2, 1], []]},
    {'name': 'n=3: All on C (already solved)', 'state': [[], [], [3, 2, 1]]},
    {'name': 'n=3: Largest on A, others spread', 'state': [[3], [2], [1]]},
    {'name': 'n=3: Reverse spread', 'state': [[1], [2], [3]]},
    {'name': 'n=3: Two on A, one on B', 'state': [[3, 1], [2], []]},
    {'name': 'n=3: Two on B, one on C', 'state': [[], [3, 2], [1]]},
    {'name': 'n=3: Two on A, one on C', 'state': [[3, 2], [], [1]]},
    {'name': 'n=3: One on A, two on C', 'state': [[1], [], [3, 2]]},
    {'name': 'n=3: Two on C, one on A', 'state': [[2], [], [3, 1]]},
    {'name': 'n=3: One on B, two on C', 'state': [[], [1], [3, 2]]},
    {'name': 'n=3: Two on B, one on A', 'state': [[1], [3, 2], []]},
    {'name': 'n=3: Alternating A-B-C', 'state': [[2], [3], [1]]},
    {'name': 'n=3: All separate', 'state': [[1], [3], [2]]},
    {'name': 'n=3: Two on A, one on C', 'state': [[3, 1], [], [2]]},
    
    # ========== n=5 configurations ==========
    {'name': 'n=5: Standard (all on A)', 'state': [[5, 4, 3, 2, 1], [], []]},
    {'name': 'n=5: All on B', 'state': [[], [5, 4, 3, 2, 1], []]},
    {'name': 'n=5: All on C (already solved)', 'state': [[], [], [5, 4, 3, 2, 1]]},
    {'name': 'n=5: Four on A, one on B', 'state': [[5, 4, 3, 2], [1], []]},
    {'name': 'n=5: Four on A, one on C', 'state': [[5, 4, 3, 2], [], [1]]},
    {'name': 'n=5: Three on A, two on B', 'state': [[5, 4, 3], [2, 1], []]},
    {'name': 'n=5: Three on A, two on C', 'state': [[5, 4, 3], [], [2, 1]]},
    {'name': 'n=5: Three on A, one each', 'state': [[5, 4, 3], [2], [1]]},
    {'name': 'n=5: Two-two-one split', 'state': [[5, 4], [3, 2], [1]]},
    {'name': 'n=5: Two-one-two split', 'state': [[5, 4], [3], [2, 1]]},
    {'name': 'n=5: Complex A', 'state': [[4, 1], [3, 2], [5]]},
    {'name': 'n=5: Complex B', 'state': [[5, 2], [4, 3], [1]]},
    {'name': 'n=5: Partial spread', 'state': [[3, 1], [5, 4], [2]]},
    {'name': 'n=5: Mixed distribution A', 'state': [[5, 3], [4, 2], [1]]},
    {'name': 'n=5: Mixed distribution B', 'state': [[4, 2], [5, 3], [1]]},
    {'name': 'n=5: Three on B, two on A', 'state': [[5, 4], [3, 2, 1], []]},
    {'name': 'n=5: Three on B, two on C', 'state': [[], [5, 4, 3], [2, 1]]},
    {'name': 'n=5: Three on C, two on A', 'state': [[5, 4], [], [3, 2, 1]]},
    {'name': 'n=5: Largest separate', 'state': [[4, 3, 2, 1], [5], []]},
    {'name': 'n=5: One-three-one split', 'state': [[5], [4, 3, 2], [1]]},
    {'name': 'n=5: Scattered evenly', 'state': [[5, 3], [4, 1], [2]]},
    {'name': 'n=5: Another scatter', 'state': [[3, 2], [5, 4], [1]]},
    {'name': 'n=5: Four on B, one on A', 'state': [[1], [5, 4, 3, 2], []]},
    {'name': 'n=5: Four on C, one on B', 'state': [[], [1], [5, 4, 3, 2]]},
    {'name': 'n=5: All separate pegs', 'state': [[5, 1], [4], [3, 2]]},
    
    # ========== n=7 configurations ==========
    {'name': 'n=7: Standard (all on A)', 'state': [[7, 6, 5, 4, 3, 2, 1], [], []]},
    {'name': 'n=7: All on B', 'state': [[], [7, 6, 5, 4, 3, 2, 1], []]},
    {'name': 'n=7: All on C (already solved)', 'state': [[], [], [7, 6, 5, 4, 3, 2, 1]]},
    {'name': 'n=7: Six on A, one on B', 'state': [[7, 6, 5, 4, 3, 2], [1], []]},
    {'name': 'n=7: Six on A, one on C', 'state': [[7, 6, 5, 4, 3, 2], [], [1]]},
    {'name': 'n=7: Five on A, two on B', 'state': [[7, 6, 5, 4, 3], [2, 1], []]},
    {'name': 'n=7: Five on A, two on C', 'state': [[7, 6, 5, 4, 3], [], [2, 1]]},
    {'name': 'n=7: Five on A, one each', 'state': [[7, 6, 5, 4, 3], [2], [1]]},
    {'name': 'n=7: Four-three split on A-B', 'state': [[7, 6, 5, 4], [3, 2, 1], []]},
    {'name': 'n=7: Four-three split on A-C', 'state': [[7, 6, 5, 4], [], [3, 2, 1]]},
    {'name': 'n=7: Four-two-one split', 'state': [[7, 6, 5, 4], [3, 2], [1]]},
    {'name': 'n=7: Three-three-one split', 'state': [[7, 6, 5], [4, 3, 2], [1]]},
    {'name': 'n=7: Three-two-two split', 'state': [[7, 6, 5], [4, 3], [2, 1]]},
    {'name': 'n=7: Mixed across three pegs A', 'state': [[6, 2], [7, 5, 4], [3, 1]]},
    {'name': 'n=7: Mixed across three pegs B', 'state': [[5, 1], [7, 6], [4, 3, 2]]},
    {'name': 'n=7: Complex distribution A', 'state': [[7, 4, 2], [6, 5], [3, 1]]},
    {'name': 'n=7: Complex distribution B', 'state': [[6, 3, 1], [7, 5], [4, 2]]},
    {'name': 'n=7: Scattered pattern A', 'state': [[7, 5, 3], [6, 4], [2, 1]]},
    {'name': 'n=7: Scattered pattern B', 'state': [[5, 3, 1], [7, 6, 4], [2]]},
    {'name': 'n=7: Two-two-three split', 'state': [[7, 6], [5, 4], [3, 2, 1]]},
    {'name': 'n=7: One-two-four split', 'state': [[7], [6, 5], [4, 3, 2, 1]]},
    {'name': 'n=7: Six on B, one on A', 'state': [[1], [7, 6, 5, 4, 3, 2], []]},
    {'name': 'n=7: Six on C, one on B', 'state': [[], [1], [7, 6, 5, 4, 3, 2]]},
    {'name': 'n=7: Five on B, two on A', 'state': [[7, 6], [5, 4, 3, 2, 1], []]},
    {'name': 'n=7: Five on C, two on B', 'state': [[], [7, 6], [5, 4, 3, 2, 1]]},
    {'name': 'n=7: Four on each peg varied', 'state': [[7, 6, 3, 1], [5, 4], [2]]},
    {'name': 'n=7: Another complex mix', 'state': [[6, 4, 2], [7, 5, 3], [1]]},
    {'name': 'n=7: Largest separate on B', 'state': [[6, 5, 4, 3, 2, 1], [7], []]},
    {'name': 'n=7: Largest separate on C', 'state': [[6, 5, 4, 3, 2, 1], [], [7]]},
    {'name': 'n=7: Even distribution', 'state': [[7, 5, 2], [6, 4, 1], [3]]},
    
    # ========== n=9 configurations ==========
    {'name': 'n=9: Standard (all on A)', 'state': [[9, 8, 7, 6, 5, 4, 3, 2, 1], [], []]},
    {'name': 'n=9: All on B', 'state': [[], [9, 8, 7, 6, 5, 4, 3, 2, 1], []]},
    {'name': 'n=9: All on C (already solved)', 'state': [[], [], [9, 8, 7, 6, 5, 4, 3, 2, 1]]},
    {'name': 'n=9: Eight on A, one on B', 'state': [[9, 8, 7, 6, 5, 4, 3, 2], [1], []]},
    {'name': 'n=9: Eight on A, one on C', 'state': [[9, 8, 7, 6, 5, 4, 3, 2], [], [1]]},
    {'name': 'n=9: Seven on A, two on B', 'state': [[9, 8, 7, 6, 5, 4, 3], [2, 1], []]},
    {'name': 'n=9: Seven on A, two on C', 'state': [[9, 8, 7, 6, 5, 4, 3], [], [2, 1]]},
    {'name': 'n=9: Six on A, three on B', 'state': [[9, 8, 7, 6, 5, 4], [3, 2, 1], []]},
    {'name': 'n=9: Six on A, three on C', 'state': [[9, 8, 7, 6, 5, 4], [], [3, 2, 1]]},
    {'name': 'n=9: Five on A, four on B', 'state': [[9, 8, 7, 6, 5], [4, 3, 2, 1], []]},
    {'name': 'n=9: Five on A, four on C', 'state': [[9, 8, 7, 6, 5], [], [4, 3, 2, 1]]},
    {'name': 'n=9: Four-four-one split', 'state': [[9, 8, 7, 6], [5, 4, 3, 2], [1]]},
    {'name': 'n=9: Four-three-two split', 'state': [[9, 8, 7, 6], [5, 4, 3], [2, 1]]},
    {'name': 'n=9: Three-three-three split', 'state': [[9, 8, 7], [6, 5, 4], [3, 2, 1]]},
    {'name': 'n=9: Mixed distribution A', 'state': [[9, 7, 5, 3, 1], [8, 6, 4], [2]]},
    {'name': 'n=9: Mixed distribution B', 'state': [[8, 5, 2], [9, 7, 6, 4], [3, 1]]},
    {'name': 'n=9: Complex distribution A', 'state': [[9, 6, 3], [8, 7, 5], [4, 2, 1]]},
    {'name': 'n=9: Complex distribution B', 'state': [[7, 4, 1], [9, 8, 6, 5], [3, 2]]},
    {'name': 'n=9: Eight on B, one on A', 'state': [[1], [9, 8, 7, 6, 5, 4, 3, 2], []]},
    {'name': 'n=9: Eight on C, one on B', 'state': [[], [1], [9, 8, 7, 6, 5, 4, 3, 2]]},
    {'name': 'n=9: Seven on B, two on A', 'state': [[9, 8], [7, 6, 5, 4, 3, 2, 1], []]},
    {'name': 'n=9: Seven on C, two on B', 'state': [[], [9, 8], [7, 6, 5, 4, 3, 2, 1]]},
    {'name': 'n=9: Largest separate on B', 'state': [[8, 7, 6, 5, 4, 3, 2, 1], [9], []]},
    {'name': 'n=9: Largest separate on C', 'state': [[8, 7, 6, 5, 4, 3, 2, 1], [], [9]]},
    {'name': 'n=9: Even spread', 'state': [[9, 6, 3], [8, 5, 2], [7, 4, 1]]},
]

def run_tests():
    """Run all test cases and display results."""
    print('=' * 80)
    print('COMPREHENSIVE TEST SUITE FOR HANOI_IMAGE.PY')
    print('Testing legal configurations for n=3, n=5, and n=7')
    print('=' * 80)
    print()
    
    total_tests = len(test_cases)
    passed = 0
    failed = 0
    results = []
    
    for idx, test in enumerate(test_cases, 1):
        try:
            start_time = time.time()
            moves, final_state = solve_hanoi_from_image(test['state'])
            elapsed = time.time() - start_time
            
            n = max([d for peg in test['state'] for d in peg])
            expected_final = list(range(n, 0, -1))
            
            success = final_state.pegs['C'] == expected_final
            
            if success:
                status = 'PASS'
                passed += 1
            else:
                status = 'FAIL'
                failed += 1
            
            results.append({
                'name': test['name'],
                'n': n,
                'moves': len(moves),
                'time': elapsed,
                'status': status,
                'initial': test['state']
            })
            
            # Display progress
            print(f'[{idx:2d}/{total_tests}] {status:4s} | {test["name"]:45s} | Moves: {len(moves):4d} | Time: {elapsed:.4f}s')
            
        except Exception as e:
            failed += 1
            print(f'[{idx:2d}/{total_tests}] FAIL | {test["name"]:45s} | ERROR: {str(e)}')
    
    print()
    print('=' * 80)
    print('SUMMARY')
    print('=' * 80)
    print(f'Total Tests: {total_tests}')
    print(f'Passed: {passed} ({100*passed/total_tests:.1f}%)')
    print(f'Failed: {failed} ({100*failed/total_tests:.1f}%)')
    print()
    
    # Group by n and show statistics
    from collections import defaultdict
    by_n = defaultdict(list)
    for r in results:
        by_n[r['n']].append(r)
    
    print('STATISTICS BY NUMBER OF DISKS:')
    print('-' * 80)
    print(f'{"n":<3} | {"Tests":<6} | {"Avg Moves":<10} | {"Min":<6} | {"Max":<6} | {"Avg Time":<12}')
    print('-' * 80)
    
    for n in sorted(by_n.keys()):
        tests_for_n = by_n[n]
        avg_moves = sum(t['moves'] for t in tests_for_n) / len(tests_for_n)
        min_moves = min(t['moves'] for t in tests_for_n)
        max_moves = max(t['moves'] for t in tests_for_n)
        avg_time = sum(t['time'] for t in tests_for_n) / len(tests_for_n)
        
        print(f'{n:<3} | {len(tests_for_n):<6} | {avg_moves:<10.1f} | {min_moves:<6} | {max_moves:<6} | {avg_time:<12.6f}s')
    
    print('=' * 80)    
    
    return results

if __name__ == "__main__":
    results = run_tests()
