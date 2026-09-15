"""Compose every migrated owner slug through the published UniLab entrypoint."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from omegaconf import OmegaConf
from unilab.base import registry
from unilab.base.config_adapter import BackendAdapter
from unilab.base.config_materialization import apply_cfg_overrides
from unilab.envs import ManagerBasedRlEnvCfg

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = ROOT / "src" / "unitree_rl_unilab"
SOURCE_ROOT = ROOT / "src"
SCRIPTS = {
    "ppo": "unilab.scripts.train_rsl_rl",
    "appo": "unilab.scripts.train_appo",
    "sac": "unilab.scripts.train_sac",
    "td3": "unilab.scripts.train_td3",
    "flashsac": "unilab.scripts.train_flashsac",
}


def _owner_choice() -> list[tuple[str, str, str]]:
    choices: list[tuple[str, str, str]] = []
    for algo in SCRIPTS:
        for task_dir in sorted((PACKAGE_ROOT / "conf" / algo / "task").iterdir()):
            if not task_dir.is_dir():
                continue
            owners = sorted(
                path.stem
                for path in task_dir.glob("*.yaml")
                if path.stem in {"mujoco", "motrix", "drake"}
            )
            if owners:
                choices.append((algo, task_dir.name, owners[0]))
    return choices


def _compose_owner(algo: str, slug: str, backend: str):
    env = os.environ.copy()
    source = str(SOURCE_ROOT)
    python_path = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{source}{os.pathsep}{python_path}" if python_path else source
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            SCRIPTS[algo],
            "--config-dir",
            str(PACKAGE_ROOT / "conf" / algo),
            "--config-name",
            "config",
            f"task={slug}/{backend}",
            "--cfg",
            "job",
            "--resolve",
        ],
        check=True,
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )
    return OmegaConf.create(result.stdout)


@pytest.mark.parametrize(
    ("algo", "slug", "backend"),
    _owner_choice(),
    ids=[f"{algo}-{slug}-{backend}" for algo, slug, backend in _owner_choice()],
)
def test_owner_composes_with_unilab_runner(algo: str, slug: str, backend: str) -> None:
    owner_path = PACKAGE_ROOT / "conf" / algo / "task" / slug / f"{backend}.yaml"
    expected = yaml.safe_load(owner_path.read_text(encoding="utf-8"))["training"]["task_name"]
    cfg = _compose_owner(algo, slug, backend)

    assert cfg.training.task_name == expected
    assert cfg.training.sim_backend == backend
    model_file = str(cfg.env.scene.model_file)
    assert (
        model_file.startswith("src/unitree_rl_unilab/assets/")
        or model_file == ("src/unilab/assets/robots/g1/scene_flat.xml")
        or model_file == ("src/unilab/assets/robots/go2/scene_flat.xml")
    )


def test_go2_footstand_materializes_target_owned_manager_terms() -> None:
    registry.ensure_registries(("unitree_rl_unilab.tasks",))
    owner = _compose_owner("ppo", "unitree_go2_footstand", "mujoco")
    cfg = registry.materialize_env_config("UnitreeGo2FootStand")
    assert isinstance(cfg, ManagerBasedRlEnvCfg)
    override = BackendAdapter(owner, root_dir=ROOT).build_task_env_cfg_override()
    apply_cfg_overrides(cfg, override)

    assert cfg.observations["policy"].terms["frame"].func.__module__ == (
        "unitree_rl_unilab.tasks.go2"
    )
    assert cfg.actions["joint_pos"].__module__ == "unitree_rl_unilab.tasks.go2"
    assert cfg.terminations["footstand"].func.__module__ == "unitree_rl_unilab.tasks.go2"


def test_g1_profiles_materialize_target_owned_manager_terms() -> None:
    registry.ensure_registries(("unitree_rl_unilab.tasks",))

    walk_owner = _compose_owner("ppo", "unitree_g1_23dof_walk_flat", "mujoco")
    walk_cfg = registry.materialize_env_config("UnitreeG1Walk23DofFlat")
    assert isinstance(walk_cfg, ManagerBasedRlEnvCfg)
    apply_cfg_overrides(
        walk_cfg, BackendAdapter(walk_owner, root_dir=ROOT).build_task_env_cfg_override()
    )
    assert walk_cfg.commands["twist"].__module__ == "unitree_rl_unilab.tasks.g1.manager_terms"
    assert (
        walk_cfg.rewards["feet_phase"].func.__module__ == "unitree_rl_unilab.tasks.g1.manager_terms"
    )

    box_owner = _compose_owner("ppo", "unitree_g1_23dof_box_tracking", "mujoco")
    box_cfg = registry.materialize_env_config("UnitreeG1BoxTracking23Dof")
    assert isinstance(box_cfg, ManagerBasedRlEnvCfg)
    apply_cfg_overrides(
        box_cfg, BackendAdapter(box_owner, root_dir=ROOT).build_task_env_cfg_override()
    )
    assert box_cfg.commands["motion"].__module__ == (
        "unitree_rl_unilab.tasks.motion_tracking.g1.manager_terms"
    )
    assert box_cfg.rewards["object_global_ref_position_error_exp"].func.__module__ == (
        "unitree_rl_unilab.tasks.motion_tracking.g1.manager_terms"
    )
