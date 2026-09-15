"""Unitree G1 motion-profile registrations."""

from unilab.base import registry
from unilab.envs import ManagerBasedRlEnvCfg

from ....runtime import make_unitree_manager_env

UNITREE_G1_MOTION_TASKS = (
    "UnitreeG1MotionTrackingDeploy",
    "UnitreeG1MotionTracking23Dof",
    "UnitreeG1MotionTracking23DofDeploy",
    "UnitreeG1MotionTrackingSAC23Dof",
    "UnitreeG1BoxTracking23Dof",
    "UnitreeG1ClimbTracking",
    "UnitreeG1ClimbTracking23Dof",
    "UnitreeG1FlipTracking23Dof",
    "UnitreeG1FlipTrackingSAC23Dof",
    "UnitreeG1WallFlipTracking",
    "UnitreeG1WallFlipTracking23Dof",
    "UnitreeG1WallFlipTrackingSAC",
    "UnitreeG1WallFlipTrackingSAC23Dof",
    "UnitreeG1WBTObs23Dof",
)

for _task_name in UNITREE_G1_MOTION_TASKS:
    registry.register_env_config(_task_name, ManagerBasedRlEnvCfg)
    registry.register_env(_task_name, make_unitree_manager_env, sim_backend="mujoco")
    registry.register_env(_task_name, make_unitree_manager_env, sim_backend="motrix")

__all__ = ["UNITREE_G1_MOTION_TASKS"]
