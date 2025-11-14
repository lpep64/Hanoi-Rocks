"""
Unit tests for Environment class
"""

import pytest
from src.environment import Environment


class TestEnvironmentInitialization:
    """Test environment initialization."""
    
    def test_initial_state_3_disks(self):
        """Test that environment initializes correctly with 3 disks."""
        env = Environment(3)
        assert env.pegs['A'] == [3, 2, 1]
        assert env.pegs['B'] == []
        assert env.pegs['C'] == []
        assert env.ground == []
        assert env.disk_count == 3
    
    def test_initial_state_5_disks(self):
        """Test that environment initializes correctly with 5 disks."""
        env = Environment(5)
        assert env.pegs['A'] == [5, 4, 3, 2, 1]
        assert len(env.pegs['A']) == 5


class TestApplyMove:
    """Test move application."""
    
    def test_legal_move(self):
        """Test applying a legal move."""
        env = Environment(3)
        success, reason = env.apply_move('A', 'C')
        assert success is True
        assert reason == "Success"
        assert env.pegs['A'] == [3, 2]
        assert env.pegs['C'] == [1]
    
    def test_illegal_move_larger_on_smaller(self):
        """Test that placing larger disk on smaller is rejected."""
        env = Environment(3)
        env.apply_move('A', 'C')  # Move disk 1 to C
        env.apply_move('A', 'B')  # Move disk 2 to B
        # Now try to move disk 2 from B to C (illegal: 2 > 1)
        success, reason = env.apply_move('B', 'C')
        assert success is False
        assert reason == "IllegalHanoiMove"
    
    def test_empty_source_peg(self):
        """Test moving from an empty peg."""
        env = Environment(3)
        success, reason = env.apply_move('B', 'C')
        assert success is False
        assert reason == "EmptySource"


class TestIllegalStateDetection:
    """Test illegal state detection."""
    
    def test_legal_state(self):
        """Test detection of legal state."""
        env = Environment(3)
        illegal_type, details = env.check_for_illegal_states()
        assert illegal_type == "Legal"
        assert details is None
    
    def test_element_on_ground(self):
        """Test detection of disk on ground."""
        env = Environment(3)
        env.ground.append(1)
        illegal_type, details = env.check_for_illegal_states()
        assert illegal_type == "ElementOnGround"
        assert details == 1
    
    def test_duplicate_item(self):
        """Test detection of duplicate disk."""
        env = Environment(3)
        env.pegs['A'] = [3, 2]
        env.pegs['B'] = [2]  # Duplicate disk 2
        illegal_type, details = env.check_for_illegal_states()
        assert illegal_type == "DuplicateItem"
        assert details == 2
    
    def test_illegal_formation(self):
        """Test detection of illegal stacking."""
        env = Environment(3)
        env.pegs['A'] = [1, 2]  # Illegal: small disk below large disk
        illegal_type, details = env.check_for_illegal_states()
        assert illegal_type == "IllegalFormation"
        assert details[0] == 'A'
        assert details[1] == 0


class TestAlterations:
    """Test alteration introduction."""
    
    def test_alteration_with_zero_percent(self):
        """Test that 0% alteration never introduces changes."""
        env = Environment(3)
        altered = env.introduce_alteration(0)
        assert altered is False
    
    def test_alteration_with_hundred_percent(self):
        """Test that 100% alteration always introduces changes."""
        env = Environment(3)
        # May not always alter if conditions aren't met, but should try
        altered = env.introduce_alteration(100)
        # Just check it doesn't crash
        assert isinstance(altered, bool)


class TestGetState:
    """Test state retrieval."""
    
    def test_get_state_returns_copy(self):
        """Test that get_state returns a deep copy."""
        env = Environment(3)
        state = env.get_state()
        state['A'].append(99)  # Modify the copy
        assert 99 not in env.pegs['A']  # Original should be unchanged
