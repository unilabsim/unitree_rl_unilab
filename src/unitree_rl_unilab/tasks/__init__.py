"""Explicit registry bootstrap for Unitree production tasks."""

__unilab_registry_modules__ = (
    "unitree_rl_unilab.tasks.a2",
    "unitree_rl_unilab.tasks.go1",
    "unitree_rl_unilab.tasks.go2",
    "unitree_rl_unilab.tasks.go2w",
    "unitree_rl_unilab.tasks.g1",
    "unitree_rl_unilab.tasks.motion_tracking.g1",
)

__all__ = ["__unilab_registry_modules__"]
