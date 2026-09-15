"""Cold-path asset ownership for Unitree tasks.

Robot XML, meshes, and textures are package assets in this repository.  This
module stages those packaged files into a writable cache when needed, resolves
motion profiles into the same cache, and leaves step/reset untouched.  It is
deliberately called only from environment factories.
"""

from __future__ import annotations

import dataclasses
import hashlib
import os
import shutil
from collections.abc import MutableMapping
from importlib.resources import as_file, files
from pathlib import Path
from typing import Any, Sequence

_PATH_FIELD_NAMES = frozenset(
    {
        "model_file",
        "visual_model_file",
        "fragment_files",
        "source_model_file",
        "ground_texture_file",
        "motion_file",
    }
)
_UNITREE_ASSET_PREFIX = "src/unitree_rl_unilab/assets/"
_HF_MOTIONS_REPO_ID = "unilabsim/unilab-motions"
_HF_REPO_TYPE = "dataset"
_UNITREE_ROBOT_DEPENDENCIES: dict[str, tuple[str, ...]] = {
    # go2w XML points its meshdir at ../go2/assets.
    "go2w": ("go2",),
}


def _cache_root() -> Path:
    configured = os.environ.get("UNITREE_RL_UNILAB_CACHE", "").strip()
    if configured:
        return Path(configured).expanduser().resolve()
    return Path.home() / ".cache" / "unitree_rl_unilab"


def _directory_fingerprint(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(p for p in path.rglob("*") if p.is_file()):
        relative = item.relative_to(path).as_posix().encode()
        digest.update(relative)
        with item.open("rb") as source:
            while chunk := source.read(1024 * 1024):
                digest.update(chunk)
    return digest.hexdigest()[:20]


def _stage_robot(robot: str) -> Path:
    """Stage packaged robot metadata and binaries, then return its cache path."""
    resource = files("unitree_rl_unilab").joinpath("assets")
    with as_file(resource) as source_root:
        robots_root = source_root / "robots"
        robot_names = (robot, *_UNITREE_ROBOT_DEPENDENCIES.get(robot, ()))
        sources = tuple(robots_root / name for name in robot_names)
        missing = [str(source) for source in sources if not source.is_dir()]
        if missing:
            raise FileNotFoundError(f"Unitree task asset directories are incomplete: {missing}")

        destination_root = _cache_root() / _directory_fingerprint(robots_root) / "robots"
        for source in sources:
            destination = destination_root / source.name
            if destination.exists():
                continue
            temporary = destination.with_name(f".{destination.name}.{os.getpid()}.tmp")
            if temporary.exists():
                shutil.rmtree(temporary)
            temporary.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(source, temporary)
            try:
                temporary.replace(destination)
            except OSError:
                if not destination.exists():
                    raise
                shutil.rmtree(temporary)
        return destination_root / robot


def _resolve_motion_file(path_value: str) -> str:
    normalized = path_value.replace("\\", "/")
    if not normalized.startswith("motions/"):
        raise ValueError(f"Unitree motion path must start with 'motions/': {path_value}")
    supplied = Path(normalized)
    if supplied.is_absolute() and supplied.is_file():
        return str(supplied.resolve())

    local_root = _cache_root() / "hosted"
    target = local_root / normalized
    if target.is_file():
        return str(target)
    try:
        from huggingface_hub import snapshot_download
    except ImportError as exc:
        raise ImportError(
            f"Unitree motion '{normalized}' is not cached. Install huggingface_hub "
            "to download it automatically."
        ) from exc
    snapshot_download(
        repo_id=_HF_MOTIONS_REPO_ID,
        repo_type=_HF_REPO_TYPE,
        allow_patterns=[normalized],
        local_dir=str(local_root),
    )
    if not target.is_file():
        raise FileNotFoundError(f"Unitree motion download incomplete; missing {target}")
    return str(target)


def _resolve_external_path(path_value: str) -> str | list[str]:
    supplied = Path(path_value)
    normalized = path_value.replace("\\", "/")
    marker = "/src/unitree_rl_unilab/assets/"
    relative: Path | None = None
    if normalized.startswith(_UNITREE_ASSET_PREFIX):
        relative = Path(normalized[len(_UNITREE_ASSET_PREFIX) :])
    elif supplied.is_absolute() and marker in normalized:
        relative = Path(normalized.split(marker, 1)[1])
    elif not supplied.is_absolute() and (Path.cwd() / supplied).is_file():
        current = (Path.cwd() / supplied).resolve().as_posix()
        if marker in current:
            relative = Path(current.split(marker, 1)[1])

    if relative is not None and relative.parts and relative.parts[0] == "robots":
        staged_root = _stage_robot(relative.parts[1])
        return str((staged_root / Path(*relative.parts[2:])).resolve())
    if relative is not None:
        raise FileNotFoundError(f"Unitree task asset is outside robots metadata: {path_value}")
    if supplied.is_absolute() and supplied.is_file():
        return str(supplied.resolve())
    raise FileNotFoundError(f"Unitree task asset not found: {path_value}")


def _resolve_path_value(value: str | Sequence[str]) -> str | list[str]:
    if isinstance(value, str):
        path_value = value
    else:
        values: list[str] = []
        for item in value:
            if not isinstance(item, str):
                raise TypeError(f"Path sequences must contain strings, got {type(item).__name__}")
            resolved = _resolve_path_value(item)
            if not isinstance(resolved, str):
                raise TypeError("Nested path sequences are not supported")
            values.append(resolved)
        return values
    normalized = path_value.replace("\\", "/")
    if normalized.startswith(_UNITREE_ASSET_PREFIX):
        resolved = _resolve_external_path(path_value)
    elif normalized.startswith("motions/"):
        resolved = _resolve_motion_file(path_value)
    else:
        raise ValueError(f"Path is not owned by unitree_rl_unilab: {path_value}")
    return resolved if isinstance(resolved, str) else list(resolved)


def _resolve_paths(value: Any) -> None:
    if isinstance(value, MutableMapping):
        for key, item in value.items():
            if key in _PATH_FIELD_NAMES and isinstance(item, (str, list, tuple)):
                value[key] = _resolve_path_value(item)
            else:
                _resolve_paths(item)
        return
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        for field in dataclasses.fields(value):
            item = getattr(value, field.name)
            if field.name in _PATH_FIELD_NAMES and isinstance(item, (str, list, tuple)):
                object.__setattr__(value, field.name, _resolve_path_value(item))
            else:
                _resolve_paths(item)


def prepare_task_config(cfg: Any) -> None:
    """Resolve all Unitree-owned scene, texture, and motion paths in *cfg*."""
    _resolve_paths(cfg)


__all__ = ["prepare_task_config"]
