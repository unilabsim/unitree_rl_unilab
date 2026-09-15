"""Cold-path staging contract for package-owned Unitree assets."""

from __future__ import annotations

import sys
import types
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pytest

from unitree_rl_unilab.assets import _resolver as unitree_assets
from unitree_rl_unilab.tasks.go2w.manager_terms import compute_go2w_motor_ctrl


@dataclass
class _Scene:
    model_file: str


@dataclass
class _Command:
    params: dict[str, str]


@dataclass
class _TaskConfig:
    scene: _Scene
    commands: dict[str, _Command]


def test_compute_go2w_motor_ctrl_combines_leg_and_wheel_paths() -> None:
    policy_ctrl = np.zeros((2, 16), dtype=np.float32)
    policy_ctrl[:, 12:] = 4.0
    joint_pos = np.zeros((2, 16), dtype=np.float32)
    joint_vel = np.zeros((2, 16), dtype=np.float32)
    leg_kp = np.full(12, 40.0, dtype=np.float32)
    leg_kd = np.full(12, 2.0, dtype=np.float32)
    wheel_kd = np.full(4, 0.5, dtype=np.float32)
    lower = np.full(16, -10.0, dtype=np.float32)
    upper = np.full(16, 10.0, dtype=np.float32)
    out = np.empty((2, 16), dtype=np.float32)

    result = compute_go2w_motor_ctrl(
        policy_ctrl,
        joint_pos,
        joint_vel,
        leg_kp,
        leg_kd,
        wheel_kd,
        lower,
        upper,
        out,
    )

    assert result is out
    np.testing.assert_allclose(result[:, :12], 0.0)
    np.testing.assert_allclose(result[:, 12:], 2.0)


def test_stage_robot_copies_packaged_binary_assets(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("UNITREE_RL_UNILAB_CACHE", str(tmp_path))

    staged = unitree_assets._stage_robot("a2")

    assert (staged / "scene_flat.xml").is_file()
    assert (staged / "assets" / "a2" / "base_link.STL").is_file()


def test_stage_go2w_includes_shared_go2_meshes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("UNITREE_RL_UNILAB_CACHE", str(tmp_path))

    staged = unitree_assets._stage_robot("go2w")

    assert (staged / "go2w_mujoco.xml").is_file()
    assert (staged.parent / "go2" / "assets" / "base_0.obj").is_file()


def test_packaged_robot_models_load_with_committed_meshes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    mujoco = pytest.importorskip("mujoco")
    monkeypatch.setenv("UNITREE_RL_UNILAB_CACHE", str(tmp_path))
    expected_dimensions = {
        "a2": ("scene_flat.xml", 19, 12),
        "g1": ("scene_flat.xml", 36, 29),
        "go1": ("go1_mujoco.xml", 19, 12),
        "go2": ("go2_mujoco.xml", 19, 12),
        "go2w": ("go2w_mujoco.xml", 23, 16),
    }

    for robot, (filename, nq, nu) in expected_dimensions.items():
        model = mujoco.MjModel.from_xml_path(str(unitree_assets._stage_robot(robot) / filename))
        assert (robot, model.nq, model.nu) == (robot, nq, nu)


def test_prepare_task_config_resolves_scene_and_motion_paths(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("UNITREE_RL_UNILAB_CACHE", str(tmp_path))

    monkeypatch.setattr(
        unitree_assets, "_resolve_motion_file", lambda value: f"/tmp/motions/{value}"
    )
    cfg = _TaskConfig(
        scene=_Scene(model_file="src/unitree_rl_unilab/assets/robots/a2/scene_flat.xml"),
        commands={"motion": _Command(params={"motion_file": "motions/g1/example.npz"})},
    )

    unitree_assets.prepare_task_config(cfg)

    assert str(tmp_path) in cfg.scene.model_file
    assert cfg.scene.model_file.endswith("/robots/a2/scene_flat.xml")
    assert cfg.commands["motion"].params["motion_file"] == "/tmp/motions/motions/g1/example.npz"


def test_motion_profiles_resolve_into_downstream_cache(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("UNITREE_RL_UNILAB_CACHE", str(tmp_path))

    def fake_snapshot_download(**kwargs):
        local_dir = Path(kwargs["local_dir"])
        filename = next(iter(kwargs["allow_patterns"]))
        target = local_dir / filename
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"npz")
        return str(local_dir)

    fake_huggingface = types.SimpleNamespace(snapshot_download=fake_snapshot_download)
    monkeypatch.setitem(sys.modules, "huggingface_hub", fake_huggingface)

    resolved = unitree_assets._resolve_motion_file("motions/g1/example.npz")

    assert resolved == str(tmp_path / "hosted" / "motions" / "g1" / "example.npz")
    assert Path(resolved).read_bytes() == b"npz"
