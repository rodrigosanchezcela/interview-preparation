# Interview Preparation Tool

A comprehensive tool to help prepare for technical interviews.

## Features

- 🎯 Structured interview question management
- 📚 Track progress and learning
- 💡 Practice coding problems
- 📊 Analytics and insights

## Installation

```bash
# Install dependencies with uv
uv sync

# Or install in development mode
uv pip install -e ".[dev]"
```

## Usage

```bash
# Run the CLI tool
interview-prep

# Or use as a Python module
python -m interview_prep
```

## Development

```bash
# Install development dependencies
uv sync --extra dev

# Run tests
pytest
```

## Project Structure

```
interview-preparation/
├── src/
│   └── interview_prep/
│       ├── __init__.py
│       ├── config.py          # Configuration management
│       └── utils/             # Utility functions
├── tests/                     # Test suite
├── docs/                      # Documentation
├── data/                      # Data files
├── scripts/                   # Utility scripts
└── pyproject.toml            # Project configuration
```

## License

MIT
