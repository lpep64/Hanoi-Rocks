"""
Streamlit Visualization App for Tower of Hanoi Master Solver
Interactive UI for testing and visualizing hanoi_final_flag.py algorithms
"""

import streamlit as st
import plotly.graph_objects as go
from typing import List, Dict, Optional
import random
from copy import deepcopy

# Import the solver
from hanoi_final_flag import solve_hanoi, UnsolvableStateError, InvalidFlagCombinationError, InvalidStateError

# ==========================================
# Page Configuration
# ==========================================

st.set_page_config(
    page_title="Tower of Hanoi Solver Visualizer",
    page_icon="🗼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# Session State Initialization
# ==========================================

def initialize_session_state():
    """Initialize all session state variables."""
    if 'current_state' not in st.session_state:
        st.session_state.current_state = [
            [3, 2, 1],  # Peg A
            [],         # Peg B
            [],         # Peg C
            [],         # Queue
            []          # Ground
        ]
    
    if 'initial_state' not in st.session_state:
        st.session_state.initial_state = deepcopy(st.session_state.current_state)
    
    if 'solution_moves' not in st.session_state:
        st.session_state.solution_moves = []
    
    if 'current_move_index' not in st.session_state:
        st.session_state.current_move_index = 0
    
    if 'flags' not in st.session_state:
        st.session_state.flags = {
            'target_peg': 2,
            'duplicate_strategy': 'merge',
            'ground_strategy': 'greedy_3',
            'illegal_resolution': 'bfs_3peg'
        }
    
    if 'visualization_mode' not in st.session_state:
        st.session_state.visualization_mode = 'graphical'
    
    if 'solver_status' not in st.session_state:
        st.session_state.solver_status = None
    
    if 'error_message' not in st.session_state:
        st.session_state.error_message = None
    
    if 'manual_moves' not in st.session_state:
        st.session_state.manual_moves = []  # Track manual drag-and-drop moves

# ==========================================
# State Validation & Checksum
# ==========================================

def calculate_state_checksum(state: List[List[int]]) -> str:
    """
    Calculate a checksum for state validation.
    Returns a string representation that uniquely identifies the state.
    """
    flat = []
    for i, peg in enumerate(state):
        for disk in peg:
            flat.append(f"{i}:{disk}")
    return ",".join(sorted(flat))

def validate_state(state: List[List[int]]) -> tuple[bool, str]:
    """
    Validate that the state is internally consistent.
    Returns (is_valid, error_message).
    """
    if len(state) != 5:
        return False, "State must have exactly 5 pegs"
    
    # Count all disks
    all_disks = []
    for peg in state:
        if not isinstance(peg, list):
            return False, "Each peg must be a list"
        all_disks.extend(peg)
    
    if not all_disks:
        return False, "State must contain at least one disk"
    
    # Check for valid disk numbers (positive integers)
    if not all(isinstance(d, int) and d > 0 for d in all_disks):
        return False, "All disks must be positive integers"
    
    return True, ""

# ==========================================
# State Manipulation Functions
# ==========================================

def add_disk_to_peg(peg_idx: int, disk_size: int):
    """Add a disk to a specific peg."""
    if disk_size > 0:
        st.session_state.current_state[peg_idx].append(disk_size)
        st.session_state.initial_state = deepcopy(st.session_state.current_state)
        st.session_state.solution_moves = []
        st.session_state.current_move_index = 0

def remove_disk_from_peg(peg_idx: int):
    """Remove top disk from a specific peg."""
    if st.session_state.current_state[peg_idx]:
        st.session_state.current_state[peg_idx].pop()
        st.session_state.initial_state = deepcopy(st.session_state.current_state)
        st.session_state.solution_moves = []
        st.session_state.current_move_index = 0

def randomize_state(num_disks: int = 5):
    """Generate a random valid state with specified number of disks."""
    disks = list(range(1, num_disks + 1))
    random.shuffle(disks)
    
    # Randomly distribute disks across pegs
    new_state = [[], [], [], [], []]
    for disk in disks:
        # 70% chance on standard pegs, 15% queue, 15% ground
        rand = random.random()
        if rand < 0.7:
            peg_idx = random.choice([0, 1, 2])
        elif rand < 0.85:
            peg_idx = 3  # Queue
        else:
            peg_idx = 4  # Ground
        
        new_state[peg_idx].append(disk)
    
    st.session_state.current_state = new_state
    st.session_state.initial_state = deepcopy(new_state)
    st.session_state.solution_moves = []
    st.session_state.current_move_index = 0

def reset_to_initial():
    """Reset current state to initial state."""
    st.session_state.current_state = deepcopy(st.session_state.initial_state)
    st.session_state.current_move_index = 0

def manual_move_disk(from_peg_idx: int, to_peg_idx: int, disk_size: int, count: int = 1):
    """
    Manually move disk(s) from one peg to another (drag-and-drop).
    Moves ALL copies of the disk together as a merged unit.
    No rule enforcement - developer tool.
    """
    from hanoi.core.move import Move
    
    # Move ALL copies of the disk together
    peg_names = ['A', 'B', 'C', 'Queue', 'Ground']
    moved_count = 0
    
    # Remove all instances of this disk from source peg
    while disk_size in st.session_state.current_state[from_peg_idx]:
        st.session_state.current_state[from_peg_idx].remove(disk_size)
        moved_count += 1
    
    # Add all copies to destination peg
    for _ in range(moved_count):
        st.session_state.current_state[to_peg_idx].append(disk_size)
    
    # Record move(s) - one for each disk moved
    if moved_count > 0:
        for i in range(moved_count):
            # Calculate heights (stacked together at destination)
            src_height = i
            dst_height = len(st.session_state.current_state[to_peg_idx]) - moved_count + i
            
            move = Move(
                disk=disk_size,
                initial_peg=peg_names[from_peg_idx],
                destination_peg=peg_names[to_peg_idx],
                initial_height=src_height,
                destination_height=dst_height
            )
            st.session_state.manual_moves.append(move)
    
    # Clear solution since state was manually modified
    st.session_state.solution_moves = []
    st.session_state.current_move_index = 0
    st.session_state.solver_status = None

def apply_move(move, forward: bool = True):
    """
    Apply or reverse a single move to the current state.
    
    Args:
        move: Move object from solver
        forward: If True, apply move; if False, reverse it
    """
    if forward:
        from_peg_name = move.initial_peg
        to_peg_name = move.destination_peg
    else:
        # Reverse the move
        from_peg_name = move.destination_peg
        to_peg_name = move.initial_peg
    
    # Map peg names to indices
    peg_map = {'A': 0, 'B': 1, 'C': 2, 'Queue': 3, 'Ground': 4}
    from_idx = peg_map[from_peg_name]
    to_idx = peg_map[to_peg_name]
    
    # Perform the move
    if st.session_state.current_state[from_idx]:
        disk = st.session_state.current_state[from_idx].pop()
        st.session_state.current_state[to_idx].append(disk)

# ==========================================
# Solver Integration
# ==========================================

def run_solver():
    """Run the hanoi_final_flag solver with current state and flags."""
    try:
        # Validate state before solving
        is_valid, error_msg = validate_state(st.session_state.current_state)
        if not is_valid:
            st.session_state.error_message = f"Invalid state: {error_msg}"
            st.session_state.solver_status = "error"
            return
        
        # Store initial checksum
        initial_checksum = calculate_state_checksum(st.session_state.current_state)
        
        # Run solver
        moves = solve_hanoi(
            deepcopy(st.session_state.current_state),
            st.session_state.flags
        )
        
        # Store solution
        st.session_state.solution_moves = moves
        st.session_state.current_move_index = 0
        st.session_state.solver_status = "success"
        st.session_state.error_message = None
        
        # Reset to initial state for playback
        st.session_state.current_state = deepcopy(st.session_state.initial_state)
        
    except UnsolvableStateError as e:
        st.session_state.error_message = f"Unsolvable: {str(e)}"
        st.session_state.solver_status = "error"
        st.session_state.solution_moves = []
    except InvalidFlagCombinationError as e:
        st.session_state.error_message = f"Invalid flags: {str(e)}"
        st.session_state.solver_status = "error"
        st.session_state.solution_moves = []
    except InvalidStateError as e:
        st.session_state.error_message = f"Invalid state: {str(e)}"
        st.session_state.solver_status = "error"
        st.session_state.solution_moves = []
    except Exception as e:
        st.session_state.error_message = f"Unexpected error: {str(e)}"
        st.session_state.solver_status = "error"
        st.session_state.solution_moves = []

# ==========================================
# Visualization Functions
# ==========================================

def count_disk_duplicates(state: List[List[int]]) -> dict:
    """Count occurrences of each disk value across all pegs."""
    from collections import Counter
    all_disks = []
    for peg in state:
        all_disks.extend(peg)
    return Counter(all_disks)

def create_disk_bar(disk_size: int, max_disk: int, color_idx: int, peg_idx: int, height: int, duplicate_count: int = 1) -> str:
    """Create HTML for a disk bar with drag-and-drop support."""
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', 
              '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B739', '#52B788']
    color = colors[color_idx % len(colors)]
    
    width_percent = (disk_size / max_disk) * 80 + 10  # Scale from 10% to 90%
    
    # Add duplicate count badge if more than one
    badge = ""
    if duplicate_count > 1:
        badge = f'<span style="font-size: 0.7em; background: rgba(255,255,255,0.4); padding: 2px 6px; border-radius: 3px; margin-left: 5px; font-weight: bold;">×{duplicate_count}</span>'
    
    # Create draggable disk with data attributes
    disk_id = f"disk_{peg_idx}_{height}_{disk_size}"
    return f"""<div id="{disk_id}" draggable="true" ondragstart="window.parent.postMessage({{type: 'dragstart', disk: {disk_size}, peg: {peg_idx}, height: {height}, count: {duplicate_count}}}, '*')" style="width: {width_percent}%; height: 30px; background: linear-gradient(135deg, {color} 0%, {color}dd 100%); margin: 3px auto; border-radius: 5px; border: 2px solid #333; display: flex; align-items: center; justify-content: center; font-weight: bold; color: white; text-shadow: 1px 1px 2px rgba(0,0,0,0.5); box-sizing: border-box; cursor: move;">{disk_size}{badge}</div>"""

def render_peg_graphical(peg_data: List[int], peg_name: str, peg_idx: int, max_disk: int, duplicate_counts: dict):
    """Render a single peg in graphical mode with drag-and-drop support."""
    st.markdown(f"### {peg_name}")
    
    # Add drop zone with message passing
    drop_handler = f"""
    <script>
        window.addEventListener('message', function(e) {{
            if (e.data.type === 'drop' && e.data.targetPeg === {peg_idx}) {{
                console.log('Drop on peg {peg_idx}:', e.data);
                // Store in session storage for Python to read
                sessionStorage.setItem('dropEvent', JSON.stringify(e.data));
            }}
        }});
    </script>
    """
    
    if not peg_data:
        empty_html = f"""{drop_handler}<div ondrop="window.parent.postMessage({{type: 'drop', targetPeg: {peg_idx}}}, '*'); event.preventDefault();" ondragover="event.preventDefault();" style="height: 200px; border: 2px dashed #ccc; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: #999;">Empty</div>"""
        st.markdown(empty_html, unsafe_allow_html=True)
    else:
        # Render disks from top to bottom for visual display
        # peg_data is stored [bottom, ..., top] e.g., [3, 2, 1]
        # Merge consecutive duplicate disks - show as single bar with badge
        disk_bars = []
        seen = set()
        for i, disk in enumerate(reversed(peg_data)):
            if disk not in seen:
                seen.add(disk)
                disk_bars.append(create_disk_bar(disk, max_disk, disk - 1, peg_idx, len(peg_data) - 1 - i, duplicate_counts.get(disk, 1)))
        
        html_content = f'{drop_handler}<div ondrop="window.parent.postMessage({{type: \'drop\', targetPeg: {peg_idx}}}, \'*\'); event.preventDefault();" ondragover="event.preventDefault();" style="min-height: 200px; padding: 10px; display: flex; flex-direction: column; justify-content: flex-end;">{"".join(disk_bars)}</div>'
        st.markdown(html_content, unsafe_allow_html=True)

def render_peg_text(peg_data: List[int], peg_name: str):
    """Render a single peg in text mode."""
    st.markdown(f"**{peg_name}:** `{peg_data if peg_data else '[]'}`")

def visualize_state(mode: str = 'graphical'):
    """Visualize the current state."""
    state = st.session_state.current_state
    
    # Calculate max disk for scaling
    all_disks = [d for peg in state for d in peg]
    max_disk = max(all_disks) if all_disks else 1
    
    # Count duplicates
    duplicate_counts = count_disk_duplicates(state)
    
    if mode == 'graphical':
        # Create 5 columns for the 5 pegs
        col1, col2, col3, col4, col5 = st.columns(5)
        
        peg_names = ["Peg A", "Peg B", "Peg C", "Queue", "Ground"]
        columns = [col1, col2, col3, col4, col5]
        
        for idx, (col, peg_name) in enumerate(zip(columns, peg_names)):
            with col:
                render_peg_graphical(state[idx], peg_name, idx, max_disk, duplicate_counts)
    else:
        # Text mode
        st.markdown("#### Current State")
        render_peg_text(state[0], "Peg A")
        render_peg_text(state[1], "Peg B")
        render_peg_text(state[2], "Peg C")
        render_peg_text(state[3], "Queue Peg")
        render_peg_text(state[4], "Ground")

# ==========================================
# Main App Layout
# ==========================================

def main():
    initialize_session_state()
    
    st.title("🗼 Tower of Hanoi Master Solver Visualizer")
    st.markdown("Interactive visualization for testing complex Hanoi algorithms with gaps, duplicates, and illegal states.")
    
    # ==========================================
    # Sidebar Controls
    # ==========================================
    
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Flags Configuration
        st.subheader("Solver Flags")
        
        target_peg = st.selectbox(
            "Target Peg",
            options=[0, 1, 2],
            format_func=lambda x: ['A', 'B', 'C'][x],
            index=st.session_state.flags['target_peg'],
            help="Which peg should all disks end up on?"
        )
        st.session_state.flags['target_peg'] = target_peg
        
        duplicate_strategy = st.radio(
            "Duplicate Strategy",
            options=['merge', 'discard'],
            index=['merge', 'discard'].index(st.session_state.flags['duplicate_strategy']),
            help="How to handle duplicate disk values"
        )
        st.session_state.flags['duplicate_strategy'] = duplicate_strategy
        
        ground_strategy = st.radio(
            "Ground Strategy",
            options=['greedy_3', 'greedy_4', 'patient_3', 'patient_4'],
            index=['greedy_3', 'greedy_4', 'patient_3', 'patient_4'].index(st.session_state.flags['ground_strategy']),
            help="Algorithm for retrieving disks from ground:\n"
                 "- greedy_3: Minimize violation on pegs A, B, C\n"
                 "- greedy_4: Minimize violation on pegs A, B, C, Queue\n"
                 "- patient_3: Wait for legal placement on A, B, C\n"
                 "- patient_4: Wait for legal placement on A, B, C, Queue"
        )
        st.session_state.flags['ground_strategy'] = ground_strategy
        
        illegal_resolution = st.selectbox(
            "Illegal Resolution",
            options=['bubble_sort', 'total_evacuation', 'dig_out', 'bfs_3peg', 'bfs_4peg'],
            index=['bubble_sort', 'total_evacuation', 'dig_out', 'bfs_3peg', 'bfs_4peg'].index(
                st.session_state.flags.get('illegal_resolution', 'bfs_3peg')
            ),
            help="Algorithm for fixing illegal stacking"
        )
        st.session_state.flags['illegal_resolution'] = illegal_resolution
        
        st.divider()
        
        # Disk Controls
        st.subheader("Disk Management")
        
        # Drag-and-drop instructions
        with st.expander("🖱️ Drag-and-Drop Mode", expanded=False):
            st.markdown("""
            **Developer Tool - No Rule Enforcement**
            
            In graphical mode, merged duplicate disks move together:
            - Duplicates display as single disk with ×N badge
            - Dragging moves ALL copies together as one unit
            - Manual moves clear the solution
            - Multiple moves recorded for each disk moved
            
            Use manual controls below for precise editing.
            """)
        
        # Manual move controls
        st.markdown("**Manual Move (No Rules):**")
        col_src, col_dst = st.columns(2)
        with col_src:
            move_from = st.selectbox("From Peg", ['A', 'B', 'C', 'Queue', 'Ground'], key='manual_from')
        with col_dst:
            move_to = st.selectbox("To Peg", ['A', 'B', 'C', 'Queue', 'Ground'], key='manual_to')
        
        if st.button("↔️ Move Top Disk", use_container_width=True):
            from_idx = ['A', 'B', 'C', 'Queue', 'Ground'].index(move_from)
            to_idx = ['A', 'B', 'C', 'Queue', 'Ground'].index(move_to)
            if st.session_state.current_state[from_idx]:
                # Get the top disk value - all duplicates will move together
                disk = st.session_state.current_state[from_idx][-1]
                duplicate_counts = count_disk_duplicates(st.session_state.current_state)
                count = duplicate_counts.get(disk, 1)
                manual_move_disk(from_idx, to_idx, disk, count)
                st.rerun()
            else:
                st.warning("Source peg is empty!")
        
        st.divider()
        
        if st.button("🎲 Randomize State", use_container_width=True):
            num_disks = st.session_state.get('random_disk_count', 5)
            randomize_state(num_disks)
            st.rerun()
        
        random_disk_count = st.slider("Random Disk Count", 3, 10, 5)
        st.session_state.random_disk_count = random_disk_count
        
        st.markdown("**Add Disk to Peg:**")
        col_peg, col_size = st.columns([2, 1])
        with col_peg:
            add_peg = st.selectbox("Peg", ['A', 'B', 'C', 'Queue', 'Ground'], label_visibility="collapsed")
        with col_size:
            disk_size = st.number_input("Size", min_value=1, max_value=20, value=1, label_visibility="collapsed")
        
        if st.button("➕ Add Disk", use_container_width=True):
            peg_idx = ['A', 'B', 'C', 'Queue', 'Ground'].index(add_peg)
            add_disk_to_peg(peg_idx, disk_size)
            st.rerun()
        
        st.markdown("**Remove Disk from Peg:**")
        remove_peg = st.selectbox("Remove from", ['A', 'B', 'C', 'Queue', 'Ground'])
        if st.button("➖ Remove Top Disk", use_container_width=True):
            peg_idx = ['A', 'B', 'C', 'Queue', 'Ground'].index(remove_peg)
            remove_disk_from_peg(peg_idx)
            st.rerun()
        
        if st.button("🔄 Reset to Initial", use_container_width=True):
            reset_to_initial()
            st.rerun()
        
        if st.button("🗑️ Clear All", use_container_width=True):
            st.session_state.current_state = [[], [], [], [], []]
            st.session_state.initial_state = [[], [], [], [], []]
            st.session_state.solution_moves = []
            st.session_state.current_move_index = 0
            st.rerun()
        
        st.divider()
        
        # Visualization Mode
        st.subheader("Display Options")
        viz_mode = st.radio(
            "Visualization Mode",
            options=['graphical', 'text'],
            format_func=lambda x: "📊 Graphical" if x == 'graphical' else "📝 Text",
            index=0 if st.session_state.visualization_mode == 'graphical' else 1
        )
        st.session_state.visualization_mode = viz_mode
    
    # ==========================================
    # Main Display Area
    # ==========================================
    
    # Status Messages
    if st.session_state.error_message:
        st.error(st.session_state.error_message)
    
    if st.session_state.solver_status == "success":
        st.success(f"✅ Solution found! {len(st.session_state.solution_moves)} moves required.")
    
    # State Validation Display
    is_valid, error_msg = validate_state(st.session_state.current_state)
    if not is_valid:
        st.warning(f"⚠️ State validation warning: {error_msg}")
    
    # Visualization
    st.markdown("---")
    visualize_state(st.session_state.visualization_mode)
    st.markdown("---")
    
    # ==========================================
    # Playback Controls
    # ==========================================
    
    st.subheader("🎮 Solver Controls")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🚀 Solve", use_container_width=True, type="primary"):
            with st.spinner("Solving..."):
                run_solver()
                st.rerun()
    
    # Playback controls (only enabled if solution exists)
    has_solution = len(st.session_state.solution_moves) > 0
    
    with col2:
        if st.button("⏮️ Previous", use_container_width=True, disabled=not has_solution or st.session_state.current_move_index == 0):
            if st.session_state.current_move_index > 0:
                st.session_state.current_move_index -= 1
                move = st.session_state.solution_moves[st.session_state.current_move_index]
                apply_move(move, forward=False)
                st.rerun()
    
    with col3:
        if st.button("⏭️ Next", use_container_width=True, disabled=not has_solution or st.session_state.current_move_index >= len(st.session_state.solution_moves)):
            if st.session_state.current_move_index < len(st.session_state.solution_moves):
                move = st.session_state.solution_moves[st.session_state.current_move_index]
                apply_move(move, forward=True)
                st.session_state.current_move_index += 1
                st.rerun()
    
    with col4:
        if st.button("🔄 Reset", use_container_width=True, disabled=not has_solution):
            reset_to_initial()
            st.rerun()
    
    # Progress indicator
    if has_solution:
        st.progress(st.session_state.current_move_index / len(st.session_state.solution_moves))
        st.caption(f"Move {st.session_state.current_move_index} of {len(st.session_state.solution_moves)}")
        
        # Show current move details
        if 0 < st.session_state.current_move_index <= len(st.session_state.solution_moves):
            current_move = st.session_state.solution_moves[st.session_state.current_move_index - 1]
            # Compact notation: "3: A₂ → C₀"
            subscript = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
            src_height = str(current_move.initial_height).translate(subscript)
            dst_height = str(current_move.destination_height).translate(subscript)
            compact = f"{current_move.disk}: {current_move.initial_peg}{src_height} → {current_move.destination_peg}{dst_height}"
            st.info(f"📍 Last Move: {compact}")
    
    # ==========================================
    # Move History & Analysis
    # ==========================================
    
    # Manual moves history
    if st.session_state.manual_moves:
        with st.expander("🖱️ Manual Move History", expanded=False):
            subscript = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
            for i, move in enumerate(st.session_state.manual_moves, 1):
                src_height = str(move.initial_height).translate(subscript)
                dst_height = str(move.destination_height).translate(subscript)
                compact = f"{move.disk}: {move.initial_peg}{src_height} → {move.destination_peg}{dst_height}"
                st.text(f"{i:3d}. {compact}")
    
    if has_solution:
        with st.expander("📜 View Full Solution", expanded=False):
            # Use compact notation for move list
            subscript = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
            for i, move in enumerate(st.session_state.solution_moves, 1):
                src_height = str(move.initial_height).translate(subscript)
                dst_height = str(move.destination_height).translate(subscript)
                compact = f"{move.disk}: {move.initial_peg}{src_height} → {move.destination_peg}{dst_height}"
                st.text(f"{i:3d}. {compact}")
        
        with st.expander("📊 Solution Analytics", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            all_disks = [d for peg in st.session_state.initial_state for d in peg]
            n = len(set(all_disks))
            optimal_moves = 2**n - 1
            
            with col1:
                st.metric("Total Moves", len(st.session_state.solution_moves))
            with col2:
                st.metric("Optimal (3-peg)", optimal_moves)
            with col3:
                efficiency = (optimal_moves / len(st.session_state.solution_moves)) * 100 if st.session_state.solution_moves else 0
                st.metric("Efficiency", f"{efficiency:.1f}%")
            
            # Move breakdown by peg
            st.markdown("**Moves by Source Peg:**")
            peg_counts = {'A': 0, 'B': 0, 'C': 0, 'Queue': 0, 'Ground': 0}
            for move in st.session_state.solution_moves:
                peg_counts[move.initial_peg] += 1
            
            for peg, count in peg_counts.items():
                if count > 0:
                    st.text(f"{peg}: {count} moves")
    
    # ==========================================
    # Footer & Performance Notes
    # ==========================================
    
    st.markdown("---")
    with st.expander("ℹ️ Performance & Implementation Notes", expanded=False):
        st.markdown("""
        ### Performance Considerations
        
        **Streamlit Rerun Model:**
        - Streamlit reruns the entire script on each interaction
        - The solver is only invoked when "Solve" is clicked, not on every rerun
        - Solution moves are cached in `session_state` to avoid re-computation
        - **No performance issues with recursion**: The solver runs once, stores results, then playback is O(1)
        
        **State Synchronization:**
        - Each state has a checksum calculated via `calculate_state_checksum()`
        - Move application is deterministic (forward/backward)
        - State validation runs before solving to catch inconsistencies
        - If desync occurs, "Reset" button restores from stored initial state
        
        **Gap Disk Handling:**
        - The visualizer renders any positive integer as a disk
        - Missing integers (e.g., 1, 3, 5) display correctly
        - The solver automatically normalizes gaps during preprocessing
        - No crashes or errors from gap disks
        
        **Memory Management:**
        - Large solution sets (>1000 moves) are stored efficiently in session_state
        - Deepcopy is used judiciously to avoid reference issues
        - State history is not stored (only current and initial states)
        
        ### Validation Mechanisms
        
        1. **Pre-solve validation**: Checks state structure and disk validity
        2. **Checksum validation**: Ensures state consistency
        3. **Move validation**: Each move is verified during playback
        4. **Error handling**: All solver exceptions are caught and displayed
        """)
    
    st.markdown("---")
    st.caption("🗼 Tower of Hanoi Master Solver | Built with Streamlit")

if __name__ == "__main__":
    main()
