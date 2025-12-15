"""
Hanoi-Rocks: Advanced Tower of Hanoi Solver
Handles complex variations including illegal states, ground disks, gaps, and duplicates.
"""

__version__ = "1.0.0"

from hanoi.core.move import Move, TowerState
from hanoi.core.solver import solve_hanoi_from_image
from hanoi.illegal.checker import check_legality
from hanoi.illegal.stack_resolver import IllegalSolver
from hanoi.illegal.ground_resolver import GroundSolver

__all__ = [
    'Move',
    'TowerState',
    'solve_hanoi_from_image',
    'check_legality',
    'IllegalSolver',
    'GroundSolver',
]
