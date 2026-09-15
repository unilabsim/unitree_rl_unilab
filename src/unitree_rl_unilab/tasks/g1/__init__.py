"""Unitree G1 production locomotion registrations."""

from unilab.base import registry
from unilab.envs import ManagerBasedRlEnvCfg

from .manager_terms import make_unitree_g1_walk_env

registry.register_env_config("UnitreeG1Walk23DofFlat", ManagerBasedRlEnvCfg)
registry.register_env("UnitreeG1Walk23DofFlat", make_unitree_g1_walk_env, sim_backend="mujoco")
registry.register_env("UnitreeG1Walk23DofFlat", make_unitree_g1_walk_env, sim_backend="motrix")

registry.register_env_config("UnitreeG1Walk23DofRough", ManagerBasedRlEnvCfg)
registry.register_env("UnitreeG1Walk23DofRough", make_unitree_g1_walk_env, sim_backend="mujoco")
registry.register_env("UnitreeG1Walk23DofRough", make_unitree_g1_walk_env, sim_backend="motrix")

__all__: list[str] = []
