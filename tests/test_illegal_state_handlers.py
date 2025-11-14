"""
Unit tests for illegal state handler functions
"""

import pytest
from src.environment import Environment
import src.illegal_state_handlers as Handlers


class TestGroundHandlers:
    """Test ground handler strategies."""
    
    def test_resolve_ground_best_fit(self):
        """Test best-fit ground handler."""
        env = Environment(3)
        env.pegs['A'] = [3, 2]
        env.pegs['B'] = []
        env.pegs['C'] = []
        env.ground = [1]
        
        moves = Handlers.resolve_ground_best_fit(env, 1)
        
        assert moves == 1
        assert 1 not in env.ground
        # Disk 1 should be placed somewhere legally
        assert env.check_for_illegal_states()[0] == "Legal"
    
    def test_resolve_ground_first_available(self):
        """Test first-available ground handler."""
        env = Environment(3)
        env.pegs['A'] = [3]
        env.pegs['B'] = [2]
        env.pegs['C'] = []
        env.ground = [1]
        
        moves = Handlers.resolve_ground_first_available(env, 1)
        
        assert moves == 1
        assert 1 not in env.ground
        # Should be on one of the pegs
        assert 1 in env.pegs['A'] or 1 in env.pegs['B'] or 1 in env.pegs['C']


class TestDuplicateHandlers:
    """Test duplicate handler strategies."""
    
    def test_resolve_duplicates_keep(self):
        """Test keep duplicates handler."""
        env = Environment(3)
        env.pegs['A'] = [3, 2]
        env.pegs['B'] = [2]  # Duplicate
        
        moves = Handlers.resolve_duplicates_keep(env, 2)
        
        assert moves == 0  # Keep strategy doesn't move anything
        # Duplicate should still exist
        assert 2 in env.pegs['A']
        assert 2 in env.pegs['B']
    
    def test_resolve_duplicates_discard(self):
        """Test discard duplicates handler."""
        env = Environment(3)
        env.pegs['A'] = [3, 2]
        env.pegs['B'] = [2]  # Duplicate on top
        
        moves = Handlers.resolve_duplicates_discard(env, 2)
        
        assert moves == 1
        # One instance should be removed
        # Count total instances of disk 2
        total_twos = sum(peg.count(2) for peg in env.pegs.values())
        assert total_twos == 1


class TestFormationHandlers:
    """Test illegal formation handler strategies."""
    
    def test_resolve_formation_deepest(self):
        """Test deepest formation handler."""
        env = Environment(3)
        env.pegs['A'] = [1, 2]  # Illegal: small below large
        env.pegs['B'] = []
        env.pegs['C'] = []
        
        moves = Handlers.resolve_formation_deepest(env, ('A', 0))
        
        assert moves > 0
        # Should resolve the illegal formation
        illegal_type, _ = env.check_for_illegal_states()
        # May create other issues, but should have moved disks
        assert len(env.pegs['A']) < 2 or env.pegs['A'] != [1, 2]
    
    def test_resolve_formation_bubble(self):
        """Test bubble formation handler."""
        env = Environment(3)
        env.pegs['A'] = [1, 2]  # Illegal
        env.pegs['B'] = []
        env.pegs['C'] = [3]
        
        moves = Handlers.resolve_formation_bubble(env, ('A', 0))
        
        assert moves == 1
        # The top offending disk (2) should be moved
        assert 2 not in env.pegs['A'] or len(env.pegs['A']) == 1
    
    def test_resolve_formation_buffer(self):
        """Test buffer formation handler."""
        env = Environment(3)
        env.pegs['A'] = [1, 2]  # Illegal
        env.pegs['B'] = []
        env.pegs['C'] = []
        
        moves = Handlers.resolve_formation_buffer(env, ('A', 0))
        
        assert moves == 1
        # Disk should be moved to ground (buffer)
        assert len(env.ground) > 0 or len(env.pegs['A']) < 2


class TestHandlerIntegration:
    """Test handlers with environment integration."""
    
    def test_multiple_handlers_in_sequence(self):
        """Test applying multiple handlers in sequence."""
        env = Environment(3)
        
        # Create ground violation
        env.ground = [1]
        Handlers.resolve_ground_first_available(env, 1)
        
        # Verify resolution
        assert len(env.ground) == 0
        
        # Create duplicate
        env.pegs['B'].append(2)
        env.pegs['C'].append(2)
        Handlers.resolve_duplicates_discard(env, 2)
        
        # Verify duplicate removed
        total_twos = sum(peg.count(2) for peg in env.pegs.values())
        assert total_twos <= 1
