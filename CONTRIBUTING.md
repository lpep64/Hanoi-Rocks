# Contributing to Hanoi-Algorithms

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Process](#development-process)
- [Submitting Changes](#submitting-changes)
- [Code Standards](#code-standards)
- [Testing](#testing)

## Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## Getting Started

### Prerequisites
- Python 3.8 or higher
- Git

### Setting Up Development Environment

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/[your-org]/Hanoi-Algorithms.git
   cd Hanoi-Algorithms
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -e ".[dev]"  # Install package in editable mode + dev tools
   ```

4. **Run tests to verify setup**
   ```bash
   pytest tests/
   ```

## Development Process

### Branching Strategy

- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `hotfix/*` - Emergency fixes for production

### Creating a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### Making Changes

1. Make your changes in your feature branch
2. Add tests for any new functionality
3. Ensure all tests pass
4. Update documentation as needed
5. Follow the code style guidelines

## Submitting Changes

### Pull Request Process

1. **Update your branch with the latest changes**
   ```bash
   git checkout main
   git pull origin main
   git checkout feature/your-feature-name
   git rebase main
   ```

2. **Run tests and linting**
   ```bash
   pytest tests/
   black hanoi/ tests/
   flake8 hanoi/ tests/
   ```

3. **Commit your changes**
   - Use clear, descriptive commit messages
   - Follow conventional commit format:
     ```
     feat: add new ground resolution algorithm
     fix: resolve memory leak in BFS solver
     docs: update API documentation for solver flags
     test: add integration tests for duplicate handling
     ```

4. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request**
   - Provide a clear title and description
   - Reference any related issues
   - Ensure all CI checks pass
   - Request review from maintainers

### Pull Request Guidelines

- **Title**: Use a clear, concise title that describes the change
- **Description**: Include:
  - What changed and why
  - How to test the changes
  - Any breaking changes
  - Screenshots (if applicable)
- **Size**: Keep PRs focused and reasonably sized
- **Tests**: Include tests for new features or bug fixes
- **Documentation**: Update relevant documentation

## Code Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some modifications:

- **Line Length**: 100 characters (not 79)
- **Formatting**: Use `black` for automatic formatting
- **Imports**: Organized in groups (stdlib, third-party, local)
- **Type Hints**: Use type hints for all public functions
- **Docstrings**: Use Google-style docstrings

### Example Code

```python
from typing import List, Dict, Optional


def solve_hanoi(
    state: List[List[int]], 
    flags: Dict[str, str]
) -> List[Move]:
    """
    Solve Tower of Hanoi puzzle with given configuration.
    
    Args:
        state: Initial configuration [Peg A, Peg B, Peg C, Queue, Ground]
        flags: Configuration dictionary for solver behavior
        
    Returns:
        List of Move objects representing the solution
        
    Raises:
        UnsolvableStateError: If the puzzle cannot be solved
        InvalidStateError: If the input state is malformed
    """
    # Implementation here
    pass
```

### Documentation Standards

- **README**: Keep README.md up-to-date with new features
- **Docstrings**: All public functions, classes, and modules
- **Comments**: Explain complex logic, not obvious code
- **Type Hints**: Use throughout for better IDE support

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=hanoi tests/

# Run specific test file
pytest tests/test_solver_integration.py

# Run specific test
pytest tests/test_core.py::test_basic_hanoi
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use descriptive test names
- Include both positive and negative test cases
- Aim for >80% code coverage

### Test Structure

```python
import pytest
from hanoi_final_flag import solve_hanoi, UnsolvableStateError


def test_basic_three_disk_solution():
    """Test basic 3-disk Tower of Hanoi solution."""
    state = [[3, 2, 1], [], [], [], []]
    flags = {
        'target_peg': 2,
        'duplicate_strategy': 'discard',
        'ground_strategy': 'greedy_3',
        'illegal_resolution': 'bfs_3peg'
    }
    
    moves = solve_hanoi(state, flags)
    
    assert len(moves) == 7  # 2^3 - 1 moves
    assert moves[0].disk == 1
    assert moves[-1].destination_peg == 'C'


def test_unsolvable_state_raises_error():
    """Test that unsolvable states raise appropriate errors."""
    state = [[], [], [], [], []]  # Empty state
    flags = {'target_peg': 2}
    
    with pytest.raises(UnsolvableStateError):
        solve_hanoi(state, flags)
```

## Project Structure

```
project-name/
├── hanoi/              # Core library package
│   ├── core/          # Core solving logic
│   ├── illegal/       # Illegal state resolution
│   ├── base/          # Research baseline algorithms
│   └── utils/         # Helper functions
├── tests/             # Test suite
├── statistical_analysis/  # Research experiments
├── docs/              # Additional documentation
└── examples/          # Usage examples
```

## Questions or Issues?

- **Bug Reports**: Use GitHub Issues with the bug template
- **Feature Requests**: Use GitHub Issues with the feature template
- **Questions**: Start a GitHub Discussion
- **Security Issues**: Email [security@your-org.com]

## Recognition

Contributors will be recognized in:
- GitHub contributors page
- CHANGELOG.md for significant contributions
- README.md for major features

Thank you for contributing!
