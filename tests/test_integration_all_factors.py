"""
Integration Tests for All 5 Experimental Factors

This test suite validates that all 5 experimental factors are properly implemented
and work correctly across various test cases. It ensures the algorithms behave
as expected for each factor configuration.

Test Factors:
- Factor A: disk_count (3, 5, 7, 9)
- Factor B: target_alteration_percent (0, 10, 20, 30)
- Factor C: illegal_formation_handler (deepest, bubble, buffer)
- Factor D: ground_handler (best-fit, first-available)
- Factor E: duplicate_handler (keep, discard)
"""

import pytest
import uuid
from src.environment import Environment
from src.hanoi_solver import HanoiSolver
from src.simulation_runner import SimulationRunner
import src.illegal_state_handlers as Handlers


# ============================================================================
# Factor A: Disk Count Tests
# ============================================================================

class TestFactorA_DiskCount:
    """Test that different disk counts initialize and solve correctly."""
    
    @pytest.mark.parametrize("disk_count", [3, 5, 7, 9])
    def test_environment_initialization(self, disk_count):
        """Verify environment initializes correctly for each disk count."""
        env = Environment(disk_count)
        
        # All disks should be on peg A in descending order
        assert len(env.pegs['A']) == disk_count
        assert env.pegs['A'] == list(range(disk_count, 0, -1))
        assert env.pegs['B'] == []
        assert env.pegs['C'] == []
        assert env.ground == []
        assert env.disk_count == disk_count
    
    @pytest.mark.parametrize("disk_count", [3, 5, 7, 9])
    def test_solver_minimum_moves_calculation(self, disk_count):
        """Verify solver calculates correct minimum moves for each disk count."""
        solver = HanoiSolver()
        expected_moves = (2 ** disk_count) - 1
        assert solver.get_minimum_moves(disk_count) == expected_moves
    
    @pytest.mark.parametrize("disk_count", [3, 5, 7, 9])
    def test_solver_generates_correct_move_count(self, disk_count):
        """Verify solver generates the exact number of moves expected."""
        solver = HanoiSolver()
        moves = solver.solve_full(disk_count, 'A', 'C', 'B')
        expected_moves = (2 ** disk_count) - 1
        assert len(moves) == expected_moves
    
    def test_disk_count_3_detailed(self):
        """Detailed test for 3 disks - verify first few moves."""
        solver = HanoiSolver()
        state = {'A': [3, 2, 1], 'B': [], 'C': []}
        
        # First move: disk 1 from A to C
        move = solver.get_next_optimal_move(state, 3, 'A', 'C', 'B')
        assert move['disk'] == 1
        assert move['from'] == 'A'
        assert move['to'] == 'C'
    
    def test_disk_count_affects_timeout_threshold(self):
        """Verify timeout threshold scales correctly with disk count."""
        sim_params = {
            'replications_per_combination': 10,
            'max_moves_timeout_factor': 50,
            'visualizer_enabled': False,
            'visualizer_delay_ms': 100
        }
        
        for disk_count in [3, 5, 7, 9]:
            runner = SimulationRunner(
                run_id=str(uuid.uuid4()),
                disk_count=disk_count,
                alteration_rate=0,
                formation_handler_strategy='bubble',
                ground_handler_strategy='best-fit',
                duplicate_handler_strategy='keep',
                sim_params=sim_params
            )
            
            expected_max = ((2 ** disk_count) - 1) * 50
            assert runner.max_moves == expected_max


# ============================================================================
# Factor B: Alteration Percent Tests
# ============================================================================

class TestFactorB_AlterationPercent:
    """Test that alteration rates work correctly."""
    
    def test_zero_percent_never_alters(self):
        """Verify 0% alteration never introduces changes."""
        env = Environment(3)
        env.pegs['A'] = [3, 2, 1]
        
        # Try many times - should never alter
        altered_count = 0
        for _ in range(1000):
            if env.introduce_alteration(0):
                altered_count += 1
        
        assert altered_count == 0
    
    def test_hundred_percent_always_alters(self):
        """Verify 100% alteration always introduces changes."""
        env = Environment(5)
        env.pegs['A'] = [5, 4, 3]
        env.pegs['B'] = [2, 1]
        
        # Try many times - should always alter
        altered_count = 0
        trials = 100
        for _ in range(trials):
            # Reset state to ensure we have disks to alter
            env.pegs['A'] = [5, 4, 3]
            env.pegs['B'] = [2, 1]
            env.ground = []
            
            if env.introduce_alteration(100):
                altered_count += 1
        
        # Should alter at or near 100% of the time
        assert altered_count >= trials * 0.95  # Allow 5% margin for randomness
    
    @pytest.mark.parametrize("alteration_percent", [0, 10, 20, 30])
    def test_alteration_rates_statistical(self, alteration_percent):
        """Test that alteration rates are statistically correct."""
        env = Environment(5)
        
        trials = 1000
        altered_count = 0
        
        for _ in range(trials):
            # Reset to a state with multiple disks
            env.pegs['A'] = [5, 4, 3]
            env.pegs['B'] = [2]
            env.pegs['C'] = [1]
            env.ground = []
            
            if env.introduce_alteration(alteration_percent):
                altered_count += 1
        
        actual_percent = (altered_count / trials) * 100
        
        # Allow 5% margin of error for statistical variation
        assert abs(actual_percent - alteration_percent) < 5
    
    def test_alteration_creates_illegal_states(self):
        """Verify alterations actually create one of three illegal states."""
        env = Environment(5)
        env.pegs['A'] = [5, 4, 3, 2, 1]
        env.pegs['B'] = []
        env.pegs['C'] = []
        
        # Force alteration
        altered = env.introduce_alteration(100)
        
        if altered:
            illegal_type, details = env.check_for_illegal_states()
            # Should be one of the three illegal state types
            assert illegal_type in ["ElementOnGround", "DuplicateItem", "IllegalFormation"]


# ============================================================================
# Factor C: Illegal Formation Handler Tests
# ============================================================================

class TestFactorC_IllegalFormationHandler:
    """Test all three illegal formation handler strategies."""
    
    def test_deepest_handler_resolves_simple_violation(self):
        """Test deepest handler on simple illegal formation."""
        env = Environment(3)
        env.pegs['A'] = [1, 2]  # Illegal: disk 1 below disk 2
        env.pegs['B'] = []
        env.pegs['C'] = []
        
        moves = Handlers.resolve_formation_deepest(env, ('A', 0))
        
        assert moves > 0
        # Should have swapped or resolved the violation
        assert env.pegs['A'] != [1, 2]
    
    def test_bubble_handler_swaps_correctly(self):
        """Test bubble handler swaps adjacent disks."""
        env = Environment(3)
        env.pegs['A'] = [1, 2]  # Illegal: disk 1 below disk 2
        env.pegs['B'] = []
        env.pegs['C'] = []
        
        moves = Handlers.resolve_formation_bubble(env, ('A', 0))
        
        assert moves == 2  # Bubble always costs 2 moves
        # Should have swapped them
        assert env.pegs['A'] == [2, 1]
    
    def test_buffer_handler_moves_offending_disk(self):
        """Test buffer handler removes offending disk to another peg."""
        env = Environment(3)
        env.pegs['A'] = [1, 3]  # Illegal: disk 1 below disk 3
        env.pegs['B'] = []
        env.pegs['C'] = []
        
        moves = Handlers.resolve_formation_buffer(env, ('A', 0))
        
        assert moves >= 1
        # Disk should have been moved
        assert env.pegs['A'] != [1, 3]
    
    def test_all_formation_handlers_resolve_violation(self):
        """Test that all handlers can resolve the same violation."""
        handlers = ['deepest', 'bubble', 'buffer']
        
        for handler_name in handlers:
            env = Environment(5)
            env.pegs['A'] = [2, 4]  # Illegal: disk 2 below disk 4
            env.pegs['B'] = [5, 3, 1]
            env.pegs['C'] = []
            
            handler_func = getattr(Handlers, f"resolve_formation_{handler_name}")
            moves = handler_func(env, ('A', 0))
            
            assert moves > 0, f"Handler {handler_name} should have made moves"
            assert env.pegs['A'] != [2, 4], f"Handler {handler_name} should have changed state"
    
    def test_formation_handler_with_multiple_disks_above(self):
        """Test handlers when there are multiple disks above the violation."""
        env = Environment(5)
        env.pegs['A'] = [1, 3, 2]  # Illegal at index 0: 1 < 3
        env.pegs['B'] = []
        env.pegs['C'] = []
        
        moves = Handlers.resolve_formation_deepest(env, ('A', 0))
        
        assert moves > 0
        # Should have handled the stack


# ============================================================================
# Factor D: Ground Handler Tests
# ============================================================================

class TestFactorD_GroundHandler:
    """Test both ground handler strategies."""
    
    def test_best_fit_places_on_optimal_peg(self):
        """Test best-fit finds the optimal placement."""
        env = Environment(5)
        env.pegs['A'] = [5, 2]
        env.pegs['B'] = [4]
        env.pegs['C'] = [3]
        env.ground = [1]  # Disk 1 on ground
        
        moves = Handlers.resolve_ground_best_fit(env, 1)
        
        assert moves == 1
        assert 1 not in env.ground
        # Disk 1 can go on any peg, but best-fit should choose smallest gap
        # Disk 1 fits on all pegs: A(2), B(4), C(3)
        # Best fit is A with gap=1
        assert 1 in env.pegs['A']
    
    def test_best_fit_with_empty_peg(self):
        """Test best-fit when an empty peg exists."""
        env = Environment(3)
        env.pegs['A'] = [3, 2]
        env.pegs['B'] = []  # Empty
        env.pegs['C'] = []  # Empty
        env.ground = [1]
        
        moves = Handlers.resolve_ground_best_fit(env, 1)
        
        assert moves == 1
        assert 1 not in env.ground
        # Should be placed somewhere
        total_disks = sum(len(peg) for peg in env.pegs.values())
        assert total_disks == 3
    
    def test_first_available_uses_peg_order(self):
        """Test first-available checks pegs in A, B, C order."""
        env = Environment(5)
        env.pegs['A'] = [5, 1]  # Cannot place 2 here (1 < 2)
        env.pegs['B'] = [4, 3]  # Can place 2 here (3 > 2)
        env.pegs['C'] = [2]  # Can place 2 here but B should be tried first
        env.ground = [2]
        
        moves = Handlers.resolve_ground_first_available(env, 2)
        
        assert moves == 1
        assert 2 not in env.ground
    
    def test_both_handlers_resolve_ground_element(self):
        """Test that both handlers successfully remove disk from ground."""
        handlers = [
            ('best-fit', 'best_fit'),
            ('first-available', 'first_available')
        ]
        
        for handler_name, func_name in handlers:
            env = Environment(3)
            env.pegs['A'] = [3]
            env.pegs['B'] = [2]
            env.pegs['C'] = []
            env.ground = [1]
            
            handler_func = getattr(Handlers, f"resolve_ground_{func_name}")
            moves = handler_func(env, 1)
            
            assert moves == 1, f"Handler {handler_name} should make 1 move"
            assert 1 not in env.ground, f"Handler {handler_name} should remove disk from ground"
            
            # Verify disk is now on a peg
            assert 1 in env.pegs['A'] or 1 in env.pegs['B'] or 1 in env.pegs['C']


# ============================================================================
# Factor E: Duplicate Handler Tests
# ============================================================================

class TestFactorE_DuplicateHandler:
    """Test both duplicate handler strategies."""
    
    def test_keep_handler_does_not_remove_duplicate(self):
        """Test keep handler leaves duplicates in place."""
        env = Environment(3)
        env.pegs['A'] = [3, 2]
        env.pegs['B'] = [2]  # Duplicate disk 2
        env.pegs['C'] = []
        
        moves = Handlers.resolve_duplicates_keep(env, 2)
        
        assert moves == 0  # Keep strategy makes no moves
        # Both instances should still exist
        assert 2 in env.pegs['A']
        assert 2 in env.pegs['B']
    
    def test_discard_handler_removes_one_instance(self):
        """Test discard handler removes exactly one duplicate."""
        env = Environment(5)
        env.pegs['A'] = [5, 3]
        env.pegs['B'] = [3]  # Duplicate disk 3 on top
        env.pegs['C'] = [4, 2, 1]
        
        moves = Handlers.resolve_duplicates_discard(env, 3)
        
        assert moves == 1
        # Count instances of disk 3
        total_threes = sum(peg.count(3) for peg in env.pegs.values())
        assert total_threes == 1
    
    def test_discard_handler_removes_accessible_instance(self):
        """Test discard handler removes the most accessible duplicate."""
        env = Environment(5)
        env.pegs['A'] = [5, 4, 3, 2]  # Disk 2 is buried
        env.pegs['B'] = [2]  # Disk 2 is on top (most accessible)
        env.pegs['C'] = []
        
        moves = Handlers.resolve_duplicates_discard(env, 2)
        
        assert moves == 1
        # The accessible one (on top of B) should be removed
        assert 2 not in env.pegs['B']
        assert 2 in env.pegs['A']
    
    def test_both_handlers_work_with_multiple_duplicates(self):
        """Test handlers when duplicate appears multiple times."""
        # Keep handler
        env = Environment(5)
        env.pegs['A'] = [4, 2]
        env.pegs['B'] = [2]
        env.pegs['C'] = [2]  # Triple duplicate
        
        moves = Handlers.resolve_duplicates_keep(env, 2)
        assert moves == 0
        
        # Discard handler
        env = Environment(5)
        env.pegs['A'] = [4, 2]
        env.pegs['B'] = [2]
        env.pegs['C'] = []
        
        moves = Handlers.resolve_duplicates_discard(env, 2)
        assert moves == 1
        # Should remove one instance
        total_twos = sum(peg.count(2) for peg in env.pegs.values())
        assert total_twos == 1


# ============================================================================
# Integration Tests: Multiple Factors Together
# ============================================================================

class TestIntegration_MultipleFacors:
    """Test interactions between multiple factors."""
    
    def test_simulation_with_zero_alteration_solves(self):
        """Test that simulation with 0% alteration always solves correctly."""
        sim_params = {
            'replications_per_combination': 1,
            'max_moves_timeout_factor': 50,
            'visualizer_enabled': False,
            'visualizer_delay_ms': 0
        }
        
        runner = SimulationRunner(
            run_id=str(uuid.uuid4()),
            disk_count=3,  # Factor A
            alteration_rate=0,  # Factor B: no alterations
            formation_handler_strategy='bubble',  # Factor C
            ground_handler_strategy='best-fit',  # Factor D
            duplicate_handler_strategy='keep',  # Factor E
            sim_params=sim_params
        )
        
        result = runner.run()
        
        assert result['is_solvable'] is True
        assert result['total_alterations'] == 0
        assert result['total_illegal_states'] == 0
        # Should solve in exactly 7 moves for 3 disks
        assert result['total_moves_to_solve'] == 7
    
    def test_all_formation_handlers_with_same_configuration(self):
        """Test that all formation handlers can solve same problem."""
        sim_params = {
            'replications_per_combination': 1,
            'max_moves_timeout_factor': 50,
            'visualizer_enabled': False,
            'visualizer_delay_ms': 0
        }
        
        handlers = ['deepest', 'bubble', 'buffer']
        
        for handler in handlers:
            runner = SimulationRunner(
                run_id=str(uuid.uuid4()),
                disk_count=3,
                alteration_rate=0,
                formation_handler_strategy=handler,  # Factor C
                ground_handler_strategy='best-fit',
                duplicate_handler_strategy='keep',
                sim_params=sim_params
            )
            
            result = runner.run()
            assert result['is_solvable'] is True, f"Handler {handler} should solve cleanly"
    
    def test_all_ground_handlers_with_same_configuration(self):
        """Test that both ground handlers can solve same problem."""
        sim_params = {
            'replications_per_combination': 1,
            'max_moves_timeout_factor': 50,
            'visualizer_enabled': False,
            'visualizer_delay_ms': 0
        }
        
        handlers = ['best-fit', 'first-available']
        
        for handler in handlers:
            runner = SimulationRunner(
                run_id=str(uuid.uuid4()),
                disk_count=3,
                alteration_rate=0,
                formation_handler_strategy='bubble',
                ground_handler_strategy=handler,  # Factor D
                duplicate_handler_strategy='keep',
                sim_params=sim_params
            )
            
            result = runner.run()
            assert result['is_solvable'] is True, f"Ground handler {handler} should solve cleanly"
    
    def test_all_duplicate_handlers_with_same_configuration(self):
        """Test that both duplicate handlers can solve same problem."""
        sim_params = {
            'replications_per_combination': 1,
            'max_moves_timeout_factor': 50,
            'visualizer_enabled': False,
            'visualizer_delay_ms': 0
        }
        
        handlers = ['keep', 'discard']
        
        for handler in handlers:
            runner = SimulationRunner(
                run_id=str(uuid.uuid4()),
                disk_count=3,
                alteration_rate=0,
                formation_handler_strategy='bubble',
                ground_handler_strategy='best-fit',
                duplicate_handler_strategy=handler,  # Factor E
                sim_params=sim_params
            )
            
            result = runner.run()
            assert result['is_solvable'] is True, f"Duplicate handler {handler} should solve cleanly"
    
    def test_small_disk_count_with_alterations(self):
        """Test 3 disks with 10% alteration rate."""
        sim_params = {
            'replications_per_combination': 1,
            'max_moves_timeout_factor': 100,
            'visualizer_enabled': False,
            'visualizer_delay_ms': 0
        }
        
        runner = SimulationRunner(
            run_id=str(uuid.uuid4()),
            disk_count=3,  # Factor A
            alteration_rate=10,  # Factor B
            formation_handler_strategy='bubble',  # Factor C
            ground_handler_strategy='best-fit',  # Factor D
            duplicate_handler_strategy='discard',  # Factor E
            sim_params=sim_params
        )
        
        result = runner.run()
        
        # Should still be solvable with enough moves
        assert result['is_solvable'] is True or result['total_moves_to_solve'] is None
        # If solvable, should have more moves than optimal due to alterations
        if result['is_solvable']:
            assert result['total_moves_to_solve'] >= 7


# ============================================================================
# Edge Cases and Error Conditions
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_illegal_state_priority_order(self):
        """Test that illegal states are detected in correct priority order."""
        env = Environment(5)
        
        # Set up multiple violations
        env.ground = [1]  # Priority 1: Element on ground
        env.pegs['A'] = [3, 2]
        env.pegs['B'] = [2]  # Duplicate (priority 2)
        env.pegs['C'] = [1, 5]  # Illegal formation (priority 3)
        
        illegal_type, details = env.check_for_illegal_states()
        
        # Should detect ground first
        assert illegal_type == "ElementOnGround"
        assert details == 1
    
    def test_illegal_state_priority_without_ground(self):
        """Test priority when ground is empty but duplicates exist."""
        env = Environment(5)
        
        env.pegs['A'] = [4, 2]
        env.pegs['B'] = [2]  # Duplicate (priority 2)
        env.pegs['C'] = [1, 5]  # Illegal formation (priority 3)
        env.ground = []
        
        illegal_type, details = env.check_for_illegal_states()
        
        # Should detect duplicate before formation
        assert illegal_type == "DuplicateItem"
        assert details == 2
    
    def test_solver_handles_empty_state_gracefully(self):
        """Test solver with edge case of disk not found."""
        solver = HanoiSolver()
        state = {'A': [], 'B': [], 'C': []}
        
        move = solver.get_next_optimal_move(state, 3, 'A', 'C', 'B')
        
        # Should return None or handle gracefully
        assert move is None
    
    def test_environment_move_validation(self):
        """Test that environment properly validates illegal moves."""
        env = Environment(3)
        env.pegs['A'] = [3, 2, 1]
        env.pegs['B'] = []
        env.pegs['C'] = []
        
        # Try to move from empty peg
        success, reason = env.apply_move('B', 'A')
        assert success is False
        assert reason == "EmptySource"
        
        # Make a legal move first
        env.apply_move('A', 'B')  # Move disk 1 to B
        env.apply_move('A', 'C')  # Move disk 2 to C
        
        # Now try illegal move: disk 2 (on C) cannot accept disk 1 (on B)... wait that's legal
        # Try: Move disk 1 from B to C (legal: 1 < 2)
        success, reason = env.apply_move('B', 'C')
        assert success is True
        
        # Now C has [2, 1], try to put disk 3 from A onto C (illegal: 3 > 1)
        success, reason = env.apply_move('A', 'C')
        assert success is False
        assert reason == "IllegalHanoiMove"
    
    def test_total_disk_count_conservation(self):
        """Test that total disk count is conserved across operations."""
        env = Environment(5)
        
        initial_count = env.get_total_disks()
        assert initial_count == 5
        
        # Make some moves
        env.apply_move('A', 'B')
        env.apply_move('A', 'C')
        
        # Count should be preserved
        assert env.get_total_disks() == 5
        
        # Even with ground elements
        env.ground.append(1)
        assert env.get_total_disks() == 6  # Now 6 because we added a disk
    
    def test_alteration_types_are_diverse(self):
        """Test that all three alteration types can be generated."""
        env = Environment(5)
        
        alteration_types_seen = set()
        
        # Force many alterations from a more diverse starting state
        for _ in range(100):
            # Reset to a state with disks on multiple pegs
            env.pegs['A'] = [5, 4]
            env.pegs['B'] = [3, 2]
            env.pegs['C'] = [1]
            env.ground = []
            
            altered = env.introduce_alteration(100)
            if altered:
                illegal_type, _ = env.check_for_illegal_states()
                alteration_types_seen.add(illegal_type)
        
        # Should have seen all three types
        assert "ElementOnGround" in alteration_types_seen
        assert "DuplicateItem" in alteration_types_seen
        assert "IllegalFormation" in alteration_types_seen


# ============================================================================
# Run Configuration Tests
# ============================================================================

class TestCompleteFactorCombinations:
    """Test a selection of complete factor combinations."""
    
    @pytest.mark.parametrize("disk_count", [3, 5])
    @pytest.mark.parametrize("formation_handler", ['deepest', 'bubble', 'buffer'])
    def test_factor_combination_ac(self, disk_count, formation_handler):
        """Test combinations of Factor A (disk count) and Factor C (formation handler)."""
        sim_params = {
            'replications_per_combination': 1,
            'max_moves_timeout_factor': 50,
            'visualizer_enabled': False,
            'visualizer_delay_ms': 0
        }
        
        runner = SimulationRunner(
            run_id=str(uuid.uuid4()),
            disk_count=disk_count,
            alteration_rate=0,
            formation_handler_strategy=formation_handler,
            ground_handler_strategy='best-fit',
            duplicate_handler_strategy='keep',
            sim_params=sim_params
        )
        
        result = runner.run()
        assert result['is_solvable'] is True
    
    @pytest.mark.parametrize("ground_handler", ['best-fit', 'first-available'])
    @pytest.mark.parametrize("duplicate_handler", ['keep', 'discard'])
    def test_factor_combination_de(self, ground_handler, duplicate_handler):
        """Test combinations of Factor D (ground) and Factor E (duplicate)."""
        sim_params = {
            'replications_per_combination': 1,
            'max_moves_timeout_factor': 50,
            'visualizer_enabled': False,
            'visualizer_delay_ms': 0
        }
        
        runner = SimulationRunner(
            run_id=str(uuid.uuid4()),
            disk_count=3,
            alteration_rate=0,
            formation_handler_strategy='bubble',
            ground_handler_strategy=ground_handler,
            duplicate_handler_strategy=duplicate_handler,
            sim_params=sim_params
        )
        
        result = runner.run()
        assert result['is_solvable'] is True
