"""
Quick test run to verify the experiment framework works with BFS
"""

import sys
import os

# Add parent directories to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../illegal_solutions')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../state_solutions')))

from run_tests import ExperimentRunner
from experiment_config import CONDITIONS

# Create runner
runner = ExperimentRunner()

# Test just one trial from Condition 5 (BFS + Greedy + 5%)
print("="*70)
print("TEST RUN: Single Trial")
print("="*70)

condition = CONDITIONS[4]  # Condition 5: a_star + greedy + 5%
print(f"\nCondition: {condition['stack_algorithm']} + {condition['ground_algorithm']} + {condition['corruption_rate']*100:.0f}%")

try:
    result = runner.run_single_trial(condition, trial_num=1, seed=100)
    print("\n✅ Trial completed successfully!")
    print(f"Results:")
    for key, value in result.items():
        print(f"  {key}: {value}")
except Exception as e:
    print(f"\n❌ Trial failed with error:")
    print(f"  {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
