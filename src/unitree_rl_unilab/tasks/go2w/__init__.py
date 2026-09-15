"""Unitree Go2W task registrations."""

from unilab.base import registry
from unilab.envs import ManagerBasedRlEnvCfg

from ...runtime import make_unitree_manager_env

registry.register_env_config("UnitreeGo2WJoystickFlat", ManagerBasedRlEnvCfg)
registry.register_env("UnitreeGo2WJoystickFlat", make_unitree_manager_env, sim_backend="mujoco")
registry.register_env("UnitreeGo2WJoystickFlat", make_unitree_manager_env, sim_backend="motrix")
registry.register_env("UnitreeGo2WJoystickFlat", make_unitree_manager_env, sim_backend="drake")

registry.register_env_config("UnitreeGo2WJoystickRough", ManagerBasedRlEnvCfg)
registry.register_env("UnitreeGo2WJoystickRough", make_unitree_manager_env, sim_backend="mujoco")
registry.register_env("UnitreeGo2WJoystickRough", make_unitree_manager_env, sim_backend="motrix")

__all__: list[str] = []
