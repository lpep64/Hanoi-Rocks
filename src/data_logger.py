"""
Data Logger

Handles writing simulation results to CSV files.
Manages the output schema and ensures data integrity.
"""

import csv
import os
from datetime import datetime


class DataLogger:
    """
    Manages CSV output for simulation results.
    
    Writes aggregated summary data for each simulation run to results.csv.
    Handles file creation, header writing, and row appending.
    """
    
    def __init__(self, output_filepath='data/results.csv'):
        """
        Initialize the data logger.
        
        Args:
            output_filepath (str): Path to the output CSV file
        """
        self.output_filepath = output_filepath
        self.fieldnames = [
            'run_id',
            'run_timestamp',
            'disk_count',
            'target_alteration_percent',
            'illegal_formation_handler',
            'ground_handler',
            'duplicate_handler',
            'is_solvable',
            'total_moves_to_solve',
            'total_alterations',
            'total_illegal_states',
            'actual_alteration_percent',
            'raw_move_log_path'
        ]
        
        # Create the data directory if it doesn't exist
        os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
        
        # Initialize the CSV file with headers
        self._initialize_csv()
    
    def _initialize_csv(self):
        """
        Create the CSV file with headers if it doesn't exist.
        If file exists, verify headers match.
        """
        if not os.path.exists(self.output_filepath):
            with open(self.output_filepath, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writeheader()
    
    def log_run(self, summary_data):
        """
        Append a single simulation run's summary data to the CSV file.
        
        Args:
            summary_data (dict): Dictionary containing all fields defined in self.fieldnames
                Keys must match fieldnames exactly.
        
        Expected summary_data structure:
        {
            'run_id': str (UUID),
            'run_timestamp': str (ISO 8601),
            'disk_count': int,
            'target_alteration_percent': int,
            'illegal_formation_handler': str,
            'ground_handler': str,
            'duplicate_handler': str,
            'is_solvable': bool,
            'total_moves_to_solve': int or None,
            'total_alterations': int,
            'total_illegal_states': int,
            'actual_alteration_percent': float,
            'raw_move_log_path': str
        }
        """
        # Ensure the data directory exists (in case it was deleted)
        os.makedirs(os.path.dirname(self.output_filepath), exist_ok=True)
        
        # Ensure raw_move_logs directory exists
        os.makedirs('data/raw_move_logs', exist_ok=True)
        
        # Append the data to the CSV
        with open(self.output_filepath, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            writer.writerow(summary_data)
    
    def get_results_count(self):
        """
        Count the number of results logged so far (excluding header).
        
        Returns:
            int: Number of simulation runs logged
        """
        if not os.path.exists(self.output_filepath):
            return 0
        
        with open(self.output_filepath, 'r') as f:
            # Subtract 1 for header row
            return sum(1 for _ in f) - 1
