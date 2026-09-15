"""Package, registry, and owner-config boundary for the Unitree migration."""

from __future__ import annotations

import importlib
import re
from pathlib import Path

import pytest
import yaml
from unilab.base import registry

from unitree_rl_unilab.cli import build_command
from unitree_rl_unilab.tasks import __unilab_registry_modules__

ROOT = Path(__file__).resolve().parents[1]
CONF_ROOT = ROOT / "src" / "unitree_rl_unilab" / "conf"

EXPECTED_TASKS = {
    "UnitreeA2JoystickFlat": {"mujoco"},
    "UnitreeGo1JoystickFlat": {"mujoco", "motrix", "drake"},
    "UnitreeGo1JoystickRough": {"mujoco", "motrix"},
    "UnitreeGo2FootStand": {"mujoco", "motrix", "drake"},
    "UnitreeGo2JoystickRough": {"mujoco", "motrix"},
    "UnitreeGo2WJoystickFlat": {"mujoco", "motrix", "drake"},
    "UnitreeGo2WJoystickRough": {"mujoco", "motrix"},
    "UnitreeG1Walk23DofFlat": {"mujoco", "motrix"},
    "UnitreeG1Walk23DofRough": {"mujoco", "motrix"},
    "UnitreeG1WalkRough": {"mujoco", "motrix"},
    "UnitreeG1MotionTrackingDeploy": {"mujoco", "motrix"},
    "UnitreeG1MotionTracking23Dof": {"mujoco", "motrix"},
    "UnitreeG1MotionTracking23DofDeploy": {"mujoco", "motrix"},
    "UnitreeG1MotionTrackingSAC23Dof": {"mujoco", "motrix"},
    "UnitreeG1BoxTracking23Dof": {"mujoco", "motrix"},
    "UnitreeG1ClimbTracking": {"mujoco", "motrix"},
    "UnitreeG1ClimbTracking23Dof": {"mujoco", "motrix"},
    "UnitreeG1FlipTracking23Dof": {"mujoco", "motrix"},
    "UnitreeG1FlipTrackingSAC23Dof": {"mujoco", "motrix"},
    "UnitreeG1WallFlipTracking": {"mujoco", "motrix"},
    "UnitreeG1WallFlipTracking23Dof": {"mujoco", "motrix"},
    "UnitreeG1WallFlipTrackingSAC": {"mujoco", "motrix"},
    "UnitreeG1WallFlipTrackingSAC23Dof": {"mujoco", "motrix"},
    "UnitreeG1WBTObs23Dof": {"mujoco", "motrix"},
}

EXPECTED_SLUGS = {
    "unitree_a2_joystick_flat",
    "unitree_go1_joystick_flat",
    "unitree_go1_joystick_rough",
    "unitree_go2_footstand",
    "unitree_go2_joystick_rough",
    "unitree_go2w_joystick_flat",
    "unitree_go2w_joystick_rough",
    "unitree_quadruped_joystick_rough",
    "unitree_g1_23dof_box_tracking",
    "unitree_g1_23dof_climb_tracking",
    "unitree_g1_23dof_flip_tracking",
    "unitree_g1_23dof_motion_tracking",
    "unitree_g1_23dof_motion_tracking_deploy",
    "unitree_g1_23dof_walk_flat",
    "unitree_g1_23dof_walk_rough",
    "unitree_g1_23dof_wall_flip_tracking",
    "unitree_g1_23dof_wbt_obs",
    "unitree_g1_climb_tracking",
    "unitree_g1_motion_tracking_deploy",
    "unitree_g1_walk_rough",
    "unitree_g1_wall_flip_tracking",
}

BASE_FAMILY_SLUGS = {
    "unitree_g1_walk_flat",
    "unitree_g1_motion_tracking",
    "unitree_g1_flip_tracking",
}


@pytest.fixture(autouse=True)
def _register_unitree_tasks():
    registry.ensure_registries(("unitree_rl_unilab.tasks",))


def test_registry_bootstrap_and_backends_match_migration_scope() -> None:
    assert __unilab_registry_modules__ == (
        "unitree_rl_unilab.tasks.a2",
        "unitree_rl_unilab.tasks.go1",
        "unitree_rl_unilab.tasks.go2",
        "unitree_rl_unilab.tasks.go2w",
        "unitree_rl_unilab.tasks.g1",
        "unitree_rl_unilab.tasks.motion_tracking.g1",
    )
    metadata = registry.list_registered_envs()
    unitree_names = {name for name in metadata if name.startswith("Unitree")}
    assert unitree_names == set(EXPECTED_TASKS)
    for name, expected_backends in EXPECTED_TASKS.items():
        assert set(metadata[name]["available_backends"]) == expected_backends


def test_owner_config_inventory_is_complete_and_namespaced() -> None:
    owner_files = sorted(CONF_ROOT.glob("*/task/*/*.yaml"))
    assert len(owner_files) == 97
    assert {path.parent.name for path in owner_files} == EXPECTED_SLUGS | BASE_FAMILY_SLUGS

    declared_names: set[str] = set()
    for path in owner_files:
        value = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        task_name = (value.get("training") or {}).get("task_name")
        if task_name is not None:
            declared_names.add(task_name)
        text = path.read_text(encoding="utf-8")
        assert "src/unilab/assets/" not in text
        assert "- /task/g1_" not in text
        assert "func: unilab.tasks.locomotion.g1.manager_terms" not in text
        assert "_target_: unilab.tasks.locomotion.g1.manager_terms" not in text
        assert "func: unilab.tasks.motion_tracking.g1.manager_terms" not in text
        assert "_target_: unilab.tasks.motion_tracking.g1.manager_terms" not in text
    assert declared_names == set(EXPECTED_TASKS)


def test_all_package_owned_config_targets_are_importable() -> None:
    references = set()
    pattern = re.compile(r"(?:func|_target_): (unitree_rl_unilab\.[A-Za-z0-9_.]+)")
    for path in CONF_ROOT.glob("*/task/*/*.yaml"):
        references.update(pattern.findall(path.read_text(encoding="utf-8")))

    assert references
    for reference in sorted(references):
        module_name, _, attribute = reference.rpartition(".")
        module = importlib.import_module(module_name)
        assert getattr(module, attribute) is not None


def test_cli_routes_external_owner_configs_into_unilab_runners() -> None:
    command = build_command(
        "train",
        algo="ppo",
        task="unitree_go2_joystick_rough",
        sim="mujoco",
        overrides=["training.no_play=true"],
    )

    assert "unilab.scripts.train_rsl_rl" in command
    assert "--config-dir" in command
    assert "task=unitree_go2_joystick_rough/mujoco" in command
    assert "training.no_play=true" in command
