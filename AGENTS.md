# unitree_rl_unilab Agent Guide

## Repository boundary

- This package depends on UniLab and UniRL only through public package indexes.
  Do not add local path/editable sources for either upstream repository.
- UniLab owns managers, the Manager-Based runtime, cross-robot MDP/common
  terms, backends, runners, IPC, Hydra materialization, and sim2sim checks.
- This repository owns Unitree task registrations, algorithm owner YAML, robot
  XML/mesh/texture assets, task-specific manager terms, tests, and support
  evidence.
- G1 Hydra bases and profile-specific G1 manager terms are intentionally local.
  Keep cross-robot reusable behavior in UniLab and import it through its public
  API rather than copying more common code into this fork.

## Validation

Use the smallest focused test first, then the full downstream gate:

```text
uv run pytest tests/test_package_contract.py -q
uv run pytest -q
uv run ruff format --check .
uv run ruff check .
uv run mypy src/unitree_rl_unilab
```

For docs or support claims, distinguish configured/config-composed evidence
from a completed training run. Do not promote an entry without evidence in this
repository.
