# Support Matrix

This repository owns registry/config evidence for the migrated Unitree tasks.
The current automated gate checks registry bootstrap, owner YAML inventory,
Hydra composition through UniLab's runner entrypoints, task-owned kernels, and
cold-path asset staging. It does not claim a new full training run.

| Registry task | MuJoCo | Motrix | Drake |
| --- | --- | --- | --- |
| `UnitreeA2JoystickFlat` | Registered | - | - |
| `UnitreeGo1JoystickFlat` | Registered | Registered | Registered |
| `UnitreeGo1JoystickRough` | Registered | Registered | - |
| `UnitreeGo2FootStand` | Registered | Registered | Registered |
| `UnitreeGo2JoystickRough` | Registered | Registered | - |
| `UnitreeGo2WJoystickFlat` | Registered | Registered | Registered |
| `UnitreeGo2WJoystickRough` | Registered | Registered | - |
| `UnitreeG1Walk23DofFlat` | Registered | Registered | - |
| `UnitreeG1Walk23DofRough` | Registered | Registered | - |
| `UnitreeG1MotionTrackingDeploy` | Registered | Registered | - |
| `UnitreeG1MotionTracking23Dof` | Registered | Registered | - |
| `UnitreeG1MotionTracking23DofDeploy` | Registered | Registered | - |
| `UnitreeG1MotionTrackingSAC23Dof` | Registered | Registered | - |
| `UnitreeG1BoxTracking23Dof` | Registered | Registered | - |
| `UnitreeG1ClimbTracking` | Registered | Registered | - |
| `UnitreeG1ClimbTracking23Dof` | Registered | Registered | - |
| `UnitreeG1FlipTracking23Dof` | Registered | Registered | - |
| `UnitreeG1FlipTrackingSAC23Dof` | Registered | Registered | - |
| `UnitreeG1WallFlipTracking` | Registered | Registered | - |
| `UnitreeG1WallFlipTracking23Dof` | Registered | Registered | - |
| `UnitreeG1WallFlipTrackingSAC` | Registered | Registered | - |
| `UnitreeG1WallFlipTrackingSAC23Dof` | Registered | Registered | - |
| `UnitreeG1WBTObs23Dof` | Registered | Registered | - |

An entry is `Registered` when both the registry backend factory and at least one
algorithm owner YAML exist for that path. The CI composition test covers every
algorithm/task owner directory listed in `src/unitree_rl_unilab/conf/`.

G1 Hydra bases and profile-specific manager terms are owned in this repository.
UniLab remains the source for the Manager-Based runtime and cross-robot common
terms; those dependencies are consumed through the public package interface.
Robot meshes and textures are committed to this repository rather than resolved
from UniLab's robot asset hub.
