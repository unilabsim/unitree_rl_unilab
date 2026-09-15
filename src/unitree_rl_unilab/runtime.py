"""Picklable Unitree environment factory wrappers."""

from __future__ import annotations

from typing import Any

from unilab.envs import make_manager_based_rl_env

from .assets import prepare_task_config


def make_unitree_manager_env(
    cfg: Any,
    num_envs: int = 1,
    backend_type: str = "mujoco",
) -> Any:
    """Resolve task assets before delegating to UniLab's manager runtime."""
    prepare_task_config(cfg)
    return make_manager_based_rl_env(cfg, num_envs=num_envs, backend_type=backend_type)


__all__ = [
    "make_unitree_manager_env",
]
