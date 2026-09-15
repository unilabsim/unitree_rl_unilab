"""Thin CLI that routes Unitree owner configs into UniLab training entrypoints."""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections.abc import Sequence
from importlib.resources import files
from pathlib import Path

_SUPPORTED_ALGOS = {
    "ppo": "unilab.scripts.train_rsl_rl",
    "appo": "unilab.scripts.train_appo",
    "sac": "unilab.scripts.train_sac",
    "td3": "unilab.scripts.train_td3",
    "flashsac": "unilab.scripts.train_flashsac",
}
_RESERVED_OVERRIDES = {"algo", "task", "training.sim_backend", "training.play_only"}


def _config_dir(algo: str) -> Path:
    resource = files("unitree_rl_unilab").joinpath("conf").joinpath(algo).joinpath("task")
    return Path(str(resource))


def _override_key(override: str) -> str:
    key = override.split("=", 1)[0].strip()
    return key.lstrip("+~")


def build_command(
    mode: str,
    *,
    algo: str,
    task: str,
    sim: str,
    overrides: Sequence[str] = (),
) -> list[str]:
    if algo not in _SUPPORTED_ALGOS:
        choices = ", ".join(sorted(_SUPPORTED_ALGOS))
        raise SystemExit(f"unsupported algo={algo!r}; choose one of: {choices}")
    reserved = [item for item in overrides if _override_key(item) in _RESERVED_OVERRIDES]
    if reserved:
        raise SystemExit(f"route-defining overrides must use CLI flags: {', '.join(reserved)}")
    task_dir = _config_dir(algo) / task
    owner = task_dir / f"{sim}.yaml"
    fallback = None
    if not owner.is_file() and mode == "eval":
        fallback = next(
            (
                path
                for path in sorted(task_dir.glob("*.yaml"))
                if path.is_file() and path.stem != "base"
            ),
            None,
        )
        if fallback is None:
            raise SystemExit(f"No owner config exists for algo={algo}, task={task}: {owner}")
    elif not owner.is_file():
        raise SystemExit(f"No owner config exists for algo={algo}, task={task}, sim={sim}: {owner}")

    selected = fallback if fallback is not None else owner
    relative_task = selected.relative_to(_config_dir(algo)).as_posix()
    generated = [f"task={relative_task.removesuffix('.yaml')}"]
    if fallback is not None:
        generated.extend((f"training.sim_backend={sim}", "training.play_only=true"))
    if mode == "eval":
        generated.append("training.play_only=true")
    return [
        sys.executable,
        "-m",
        _SUPPORTED_ALGOS[algo],
        "--config-dir",
        str(_config_dir(algo).parent),
        *generated,
        *overrides,
    ]


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="unitree-rl")
    commands = parser.add_subparsers(dest="mode", required=True)
    for mode in ("train", "eval"):
        command = commands.add_parser(mode)
        command.add_argument("--algo", required=True, choices=sorted(_SUPPORTED_ALGOS))
        command.add_argument("--task", required=True)
        command.add_argument("--sim", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args, overrides = _parser().parse_known_args(argv)
    command = build_command(
        args.mode,
        algo=args.algo,
        task=args.task,
        sim=args.sim,
        overrides=overrides,
    )
    return subprocess.run(command, check=False).returncode


__all__ = ["build_command", "main"]
