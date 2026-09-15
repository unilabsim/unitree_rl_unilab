"""Unitree Go1 task registrations."""

from unilab.base import registry
from unilab.envs import ManagerBasedRlEnvCfg

from ..runtime import make_unitree_manager_env

registry.register_env_config("UnitreeGo1JoystickFlat", ManagerBasedRlEnvCfg)
registry.register_env("UnitreeGo1JoystickFlat", make_unitree_manager_env, sim_backend="mujoco")
registry.register_env("UnitreeGo1JoystickFlat", make_unitree_manager_env, sim_backend="motrix")
registry.register_env("UnitreeGo1JoystickFlat", make_unitree_manager_env, sim_backend="drake")

registry.register_env_config("UnitreeGo1JoystickRough", ManagerBasedRlEnvCfg)
registry.register_env("UnitreeGo1JoystickRough", make_unitree_manager_env, sim_backend="mujoco")
registry.register_env("UnitreeGo1JoystickRough", make_unitree_manager_env, sim_backend="motrix")

__all__: list[str] = []
