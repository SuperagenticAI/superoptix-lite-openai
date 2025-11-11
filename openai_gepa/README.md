# Test_Openai_Project Agent System

An autonomous agent system for openai_gepa tasks.

## Installation

```bash
# Using uv (recommended)
uv sync
uv run python -m openai_gepa

# Or using pip
pip install -e .
```

## Project Structure

```
openai_gepa/
├── openai_gepa/
│   ├── agents/
│   │   └── playbook/     # Agent playbooks directory
│   ├── teams/
│   ├── servers/
│   ├── knowledge/
│   ├── memory/
│   ├── tools/
│   └── guardrails/
    ├── protocols/
│   ├── evals/
│   └── optimizers/
├── .env                # Environment variables
├── .gitignore          # Git ignore file
├── .pre-commit-config.yaml  # Pre-commit hooks configuration
├── pyproject.toml      # Project metadata and dependencies (uv-compatible)
├── README.md           # Project documentation
    ├── .super                # SuperOptiX project metadata
├── tests/
│   ├── conftest.py
│   └── test_agents.py
└── ...
```

## Running Tests

```bash
pytest tests/
```

## License

MIT
