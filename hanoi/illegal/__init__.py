"""
Hanoi Illegal State Handlers
Resolution for illegal stacking and ground disk violations
"""

from hanoi.illegal.checker import check_legality
from hanoi.illegal.stack_resolver import IllegalSolver
from hanoi.illegal.ground_resolver import GroundSolver

__all__ = ['check_legality', 'IllegalSolver', 'GroundSolver']
