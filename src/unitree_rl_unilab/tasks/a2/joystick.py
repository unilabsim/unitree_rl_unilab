"""Hydra-owned A2 flat Manager-Based production registration."""

from unilab.base import registry
from unilab.envs import ManagerBasedRlEnvCfg

from ...runtime import make_unitree_manager_env

registry.register_env_config("UnitreeA2JoystickFlat", ManagerBasedRlEnvCfg)
registry.register_env("UnitreeA2JoystickFlat", make_unitree_manager_env, sim_backend="mujoco")
