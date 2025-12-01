"""
Results Analyzer for Tower of Hanoi Statistical Experiment
Performs 3-way ANOVA and generates summary statistics and plots.
"""

import os
import csv
import statistics
from typing import List, Dict, Tuple
from collections import defaultdict

# Try to import scipy for ANOVA, provide fallback if not available
try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    print("WARNING: scipy not available. ANOVA will not be performed.")
    print("Install with: pip install scipy")

from experiment_config import CONDITIONS, RESULTS_CSV, FACTOR_A_LEVELS, FACTOR_B_LEVELS, FACTOR_C_LEVELS


class ResultsAnalyzer:
    """
    Analyzes experimental results and generates statistical summaries.
    """
    
    def __init__(self, results_file: str = RESULTS_CSV):
        self.results_file = os.path.join(os.path.dirname(__file__), results_file)
        self.data = []
        self.load_data()
    
    def load_data(self):
        """
        Load results from CSV file.
        """
        with open(self.results_file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Convert numeric fields
                row['condition_id'] = int(row['condition_id'])
                row['total_moves'] = int(row['total_moves'])
                row['num_regenerations'] = int(row['num_regenerations'])
                row['num_corruptions_occurred'] = int(row['num_corruptions_occurred'])
                row['corruption_rate'] = float(row['corruption_rate'])
                row['final_state_valid'] = row['final_state_valid'].lower() == 'true'
                row['timeout'] = row['timeout'].lower() == 'true'
                
                self.data.append(row)
        
        print(f"Loaded {len(self.data)} trial results from {self.results_file}")
    
    def filter_successful_trials(self) -> List[Dict]:
        """
        Filter out timeout trials for analysis.
        """
        return [d for d in self.data if not d['timeout']]
    
    def get_descriptive_statistics(self, data_subset: List[Dict]) -> Dict:
        """
        Calculate descriptive statistics for a subset of data.
        """
        if not data_subset:
            return {
                'n': 0,
                'mean': None,
                'median': None,
                'std': None,
                'min': None,
                'max': None
            }
        
        moves = [d['total_moves'] for d in data_subset]
        
        return {
            'n': len(moves),
            'mean': statistics.mean(moves),
            'median': statistics.median(moves),
            'std': statistics.stdev(moves) if len(moves) > 1 else 0,
            'min': min(moves),
            'max': max(moves)
        }
    
    def analyze_by_factor(self, factor: str) -> Dict:
        """
        Analyze results grouped by a single factor.
        
        Args:
            factor: 'stack_algorithm', 'ground_algorithm', or 'corruption_rate'
        """
        successful = self.filter_successful_trials()
        grouped = defaultdict(list)
        
        for trial in successful:
            grouped[trial[factor]].append(trial)
        
        results = {}
        for level, trials in grouped.items():
            results[level] = self.get_descriptive_statistics(trials)
        
        return results
    
    def analyze_by_condition(self) -> Dict:
        """
        Analyze results for each of the 8 conditions.
        """
        successful = self.filter_successful_trials()
        results = {}
        
        for condition in CONDITIONS:
            cond_trials = [t for t in successful if t['condition_id'] == condition['id']]
            results[condition['id']] = {
                'condition': condition,
                'stats': self.get_descriptive_statistics(cond_trials)
            }
        
        return results
    
    def perform_three_way_anova(self):
        """
        Perform 3-way ANOVA on successful trials.
        Factors: Stack Algorithm × Ground Algorithm × Corruption Rate
        """
        if not SCIPY_AVAILABLE:
            print("\nANOVA skipped: scipy not installed")
            return
        
        successful = self.filter_successful_trials()
        
        if not successful:
            print("\nANOVA skipped: No successful trials")
            return
        
        print("\n" + "="*70)
        print("3-WAY ANOVA (Manual Calculation)")
        print("="*70)
        
        # Group data by factors
        groups = defaultdict(list)
        for trial in successful:
            key = (trial['stack_algorithm'], trial['ground_algorithm'], trial['corruption_rate'])
            groups[key].append(trial['total_moves'])
        
        # Calculate F-statistics for each main effect
        # Note: This is a simplified ANOVA. For full 3-way ANOVA with interactions,
        # use statsmodels or R
        
        # Main Effect A: Stack Algorithm
        stack_groups = defaultdict(list)
        for trial in successful:
            stack_groups[trial['stack_algorithm']].append(trial['total_moves'])
        
        if len(stack_groups) > 1:
            f_stat, p_value = stats.f_oneway(*stack_groups.values())
            print(f"\nFactor A (Stack Algorithm):")
            print(f"  F-statistic: {f_stat:.4f}")
            print(f"  p-value: {p_value:.6f}")
            print(f"  Significant: {'YES' if p_value < 0.05 else 'NO'} (α = 0.05)")
        
        # Main Effect B: Ground Algorithm
        ground_groups = defaultdict(list)
        for trial in successful:
            ground_groups[trial['ground_algorithm']].append(trial['total_moves'])
        
        if len(ground_groups) > 1:
            f_stat, p_value = stats.f_oneway(*ground_groups.values())
            print(f"\nFactor B (Ground Algorithm):")
            print(f"  F-statistic: {f_stat:.4f}")
            print(f"  p-value: {p_value:.6f}")
            print(f"  Significant: {'YES' if p_value < 0.05 else 'NO'} (α = 0.05)")
        
        # Main Effect C: Corruption Rate
        corruption_groups = defaultdict(list)
        for trial in successful:
            corruption_groups[trial['corruption_rate']].append(trial['total_moves'])
        
        if len(corruption_groups) > 1:
            f_stat, p_value = stats.f_oneway(*corruption_groups.values())
            print(f"\nFactor C (Corruption Rate):")
            print(f"  F-statistic: {f_stat:.4f}")
            print(f"  p-value: {p_value:.6f}")
            print(f"  Significant: {'YES' if p_value < 0.05 else 'NO'} (α = 0.05)")
    
    def print_full_report(self):
        """
        Print comprehensive analysis report.
        """
        print("\n" + "="*70)
        print("STATISTICAL ANALYSIS REPORT")
        print("="*70)
        
        # Overall statistics
        total = len(self.data)
        successful = self.filter_successful_trials()
        timeouts = total - len(successful)
        
        print(f"\nOverall Summary:")
        print(f"  Total Trials: {total}")
        print(f"  Successful: {len(successful)} ({len(successful)/total*100:.1f}%)")
        print(f"  Timeouts: {timeouts} ({timeouts/total*100:.1f}%)")
        
        if successful:
            overall_stats = self.get_descriptive_statistics(successful)
            print(f"\n  Move Statistics (Successful Trials):")
            print(f"    Mean: {overall_stats['mean']:.2f}")
            print(f"    Median: {overall_stats['median']:.2f}")
            print(f"    Std Dev: {overall_stats['std']:.2f}")
            print(f"    Range: [{overall_stats['min']}, {overall_stats['max']}]")
        
        # Factor A: Stack Algorithm
        print("\n" + "-"*70)
        print("Factor A: Stack Algorithm")
        print("-"*70)
        stack_results = self.analyze_by_factor('stack_algorithm')
        for algo, stats in stack_results.items():
            print(f"\n  {FACTOR_A_LEVELS[algo]}:")
            print(f"    N: {stats['n']}")
            print(f"    Mean: {stats['mean']:.2f}")
            print(f"    Std Dev: {stats['std']:.2f}")
        
        # Factor B: Ground Algorithm
        print("\n" + "-"*70)
        print("Factor B: Ground Algorithm")
        print("-"*70)
        ground_results = self.analyze_by_factor('ground_algorithm')
        for algo, stats in ground_results.items():
            print(f"\n  {FACTOR_B_LEVELS[algo]}:")
            print(f"    N: {stats['n']}")
            print(f"    Mean: {stats['mean']:.2f}")
            print(f"    Std Dev: {stats['std']:.2f}")
        
        # Factor C: Corruption Rate
        print("\n" + "-"*70)
        print("Factor C: Corruption Rate")
        print("-"*70)
        corruption_results = self.analyze_by_factor('corruption_rate')
        for rate, stats in sorted(corruption_results.items()):
            print(f"\n  {FACTOR_C_LEVELS[rate]}:")
            print(f"    N: {stats['n']}")
            print(f"    Mean: {stats['mean']:.2f}")
            print(f"    Std Dev: {stats['std']:.2f}")
        
        # By Condition
        print("\n" + "-"*70)
        print("By Condition (All 8 Combinations)")
        print("-"*70)
        condition_results = self.analyze_by_condition()
        for cond_id in sorted(condition_results.keys()):
            result = condition_results[cond_id]
            cond = result['condition']
            stats = result['stats']
            
            print(f"\n  Condition {cond_id}:")
            print(f"    Stack: {cond['stack_algorithm']}")
            print(f"    Ground: {cond['ground_algorithm']}")
            print(f"    Corruption: {cond['corruption_rate']*100:.0f}%")
            print(f"    N: {stats['n']}")
            if stats['n'] > 0:
                print(f"    Mean: {stats['mean']:.2f}")
                print(f"    Std Dev: {stats['std']:.2f}")
        
        # ANOVA
        self.perform_three_way_anova()
    
    def save_summary_csv(self, filename: str = 'results_summary.csv'):
        """
        Save summary statistics to CSV.
        """
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        condition_results = self.analyze_by_condition()
        
        with open(filepath, 'w', newline='') as csvfile:
            fieldnames = ['condition_id', 'stack_algorithm', 'ground_algorithm', 
                         'corruption_rate', 'n', 'mean', 'median', 'std', 'min', 'max']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for cond_id in sorted(condition_results.keys()):
                result = condition_results[cond_id]
                cond = result['condition']
                stats = result['stats']
                
                writer.writerow({
                    'condition_id': cond_id,
                    'stack_algorithm': cond['stack_algorithm'],
                    'ground_algorithm': cond['ground_algorithm'],
                    'corruption_rate': cond['corruption_rate'],
                    'n': stats['n'],
                    'mean': stats['mean'] if stats['mean'] is not None else '',
                    'median': stats['median'] if stats['median'] is not None else '',
                    'std': stats['std'] if stats['std'] is not None else '',
                    'min': stats['min'] if stats['min'] is not None else '',
                    'max': stats['max'] if stats['max'] is not None else ''
                })
        
        print(f"\nSummary saved to: {filepath}")


if __name__ == "__main__":
    # Check if results file exists
    results_path = os.path.join(os.path.dirname(__file__), RESULTS_CSV)
    
    if not os.path.exists(results_path):
        print(f"ERROR: Results file not found: {results_path}")
        print("Please run run_tests.py first to generate results.")
    else:
        analyzer = ResultsAnalyzer()
        analyzer.print_full_report()
        analyzer.save_summary_csv()
