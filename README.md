# Real-World Tower of Hanoi Simulation

A comprehensive experimental framework for studying the Tower of Hanoi problem under real-world conditions with environmental alterations and illegal state resolution strategies.

## Project Overview

This project simulates the classic Tower of Hanoi puzzle with "real-world" complications:
- **Environmental Alterations**: Random perturbations that introduce illegal states
- **Multiple Resolution Strategies**: Different algorithms for handling illegal states
- **Comprehensive Data Collection**: Detailed logging of every simulation run

## Experimental Design

### Five Experimental Factors

1. **Factor A - Disk Count**: Number of disks (3, 5, 7, 9)
2. **Factor B - Target Alteration Percentage**: Rate of environmental interference (0%, 10%, 20%, 30%)
3. **Factor C - Illegal Formation Handler**: Strategy for fixing stacking violations
   - `deepest`: Resolve deepest violation first
   - `bubble`: Resolve top-most violation first
   - `buffer`: Use ground as temporary buffer
4. **Factor D - Ground Handler**: Strategy for placing disks from ground back on pegs
   - `best-fit`: Place on peg with closest larger disk
   - `first-available`: Place on first legal peg
5. **Factor E - Duplicate Handler**: Strategy for handling duplicate disks
   - `keep`: Allow duplicates and solve with them
   - `discard`: Remove duplicate instances

### Total Combinations
- 4 × 4 × 3 × 2 × 2 = **384 unique combinations**
- With 10 replications each = **3,840 total simulation runs**

## Installation

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Running the Full Experiment

```bash
python run_experiment.py
```

This will:
1. Read configuration from `config.json`
2. Generate all 384 experimental combinations
3. Run 10 replications per combination
4. Save results to `data/results.csv`
5. Save detailed logs to `data/raw_move_logs/`

### Configuration

Edit `config.json` to customize:
- Number of replications per combination
- Timeout factor for unsolvable cases
- Visualizer settings (enable/disable, speed)
- Experimental factor levels

### Visualization

The built-in ASCII visualizer shows real-time simulation progress:
- Current state of all three pegs
- Disks on the ground
- Move count and alteration count

## Data Analysis

Use the included R Markdown file for comprehensive analysis:

```r
# In R or RStudio
rmarkdown::render("analysis.Rmd")
```

This generates:
- Descriptive statistics
- Multi-factor ANOVA
- Interaction plots
- Visualizations of all factor effects

## Project Structure

```
real_world_hanoi/
├── config.json                  # Experimental design parameters
├── run_experiment.py            # Main entry point
├── requirements.txt             # Python dependencies
├── analysis.Rmd                 # R Markdown analysis file
├── data/
│   ├── results.csv             # Aggregated experimental results
│   └── raw_move_logs/          # Detailed move-by-move logs
├── src/
│   ├── __init__.py
│   ├── environment.py          # State management and alterations
│   ├── hanoi_solver.py         # Pure recursive algorithm
│   ├── illegal_state_handlers.py  # Resolution strategies
│   ├── simulation_runner.py   # Single simulation orchestration
│   ├── data_logger.py          # CSV output handler
│   └── visualizer.py           # ASCII visualization
└── tests/
    ├── __init__.py
    ├── test_environment.py
    ├── test_hanoi_solver.py
    └── test_illegal_state_handlers.py
```

## Output Data Schema

Each row in `results.csv` contains:
- Unique run ID and timestamp
- All five factor values
- Solvability flag
- Total moves (or NULL if unsolvable)
- Alteration and illegal state counts
- Actual alteration percentage
- Path to detailed move log

## Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_environment.py

# Run with coverage
python -m pytest --cov=src tests/
```

## License

MIT License

## Authors

Research Team - 2025
