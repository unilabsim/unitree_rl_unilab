# unitree_rl_unilab

Unitree production RL task owners for the [UniLab](https://github.com/unilabsim/UniLab)
Manager-Based runtime. This package owns the concrete A2, Go1, Go2, Go2W, and
G1 production variants migrated from UniLab; UniLab continues to own managers,
common MDP terms, simulation backends, training runners, Hydra materialization,
and the retained G1 reference tasks.

## Install

The coordinated baseline is UniLab 1.3.0 with MuJoCo:

```bash
uv pip install -e .
```

Motrix and Drake remain optional backend extras in UniLab. Install the
corresponding `unilab[motrix]` or `unilab[drake]` extra before selecting those
owners.

The package and `uv.lock` resolve UniLab and UniRL exclusively from public
package indexes. Do not add a local path source for either upstream repository.

Installing this package also registers the `unilab.tasks` entry point. Registry
names are prefixed with `Unitree` to avoid global conflicts. For example,
`UnitreeGo2JoystickRough` replaces the former core name `Go2JoystickRough`.

## Train and evaluate

```bash
unitree-rl train --algo ppo --task unitree_go2_joystick_rough --sim mujoco -- \
  training.no_play=true
unitree-rl eval --algo ppo --task unitree_go2_joystick_rough --sim mujoco -- \
  algo.load_run=-1
```

The thin CLI delegates to UniLab's PPO/APPO/SAC/TD3/FlashSAC entrypoints and
only contributes this package's Hydra owner tree. It does not copy runners,
learners, collectors, or IPC.

## Assets

Robot XML, scene metadata, meshes, and textures are committed directly to this
repository and packaged with the wheel. Motion profiles remain cold-path
Hugging Face assets. Packaged robot files are staged into a writable cache only
when environment construction needs a filesystem path; set
`UNITREE_RL_UNILAB_CACHE` to override that cache directory.

## Migration scope

This repository owns the migrated task families:

- `unitree_a2_joystick_flat`
- `unitree_go1_joystick_{flat,rough}`
- `unitree_go2_footstand`
- `unitree_go2_joystick_rough`
- `unitree_go2w_joystick_{flat,rough}`
- `unitree_quadruped_joystick_rough` (shared owner family)
- `unitree_g1_23dof_*`
- `unitree_g1_walk_rough`
- `unitree_g1_climb_tracking`
- `unitree_g1_motion_tracking_deploy`
- `unitree_g1_wall_flip_tracking`

The corresponding 24 registry IDs are `Unitree`-prefixed and all 86 original
algorithm owner YAML files are included. G1 algorithm trees also carry local
`base.yaml` families for 29-DoF walk, motion tracking, and flip profiles, so
downstream developers can inspect and tune an entire Hydra owner without
reading the UniLab repository. The packaged config tree therefore contains 97
YAML files: 86 migrated runnable owners plus 11 local G1 base files.

G1 profile-specific manager terms are also owned here. This is deliberate:
Unitree users are expected to iterate on robot-specific command, reward, and
termination behavior in this repository. UniLab continues to own the
Manager-Based runtime and genuinely cross-robot common terms; the local G1
fork imports those public APIs instead of copying them. Keep that boundary
intact when adding new terms.

Checkpoint directories intentionally use the new registry names; old
core-named checkpoints require an explicit run-directory selection and are a
breaking migration boundary.

See [SUPPORT.md](SUPPORT.md) for the current downstream evidence boundary.
