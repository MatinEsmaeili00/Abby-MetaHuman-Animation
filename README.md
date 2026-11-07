# Abby MetaHuman: Anatomy Layers + Running Animation

Work log and assets for making **every layer of `BP_MH_CH_Abby8`** follow the same walk / jog / run animation: MetaHuman body, face, hair, Chaos Flesh muscle mesh and skeleton mesh. It also covers fixing and improving Abby's retargeted animations.

- **Progress:** [TODO.md](TODO.md)
- **Findings:** [docs/01-investigation.md](docs/01-investigation.md)

## What's in this repo

The full Unreal project (~7 GB of MetaHuman, scan and example content) stays in Perforce. This repo mirrors only:

| Path | What |
|---|---|
| `project/MetaHumanTest.uproject`, `project/Config/`, `project/Source/` | Project file, config and C++ (the Android File Server token is redacted) |
| `project/Content/…` | Only the `.uasset` files this work creates or changes (listed in `tools/tracked_assets.txt`) |
| `scripts/` | Unreal Editor Python scripts that build the IK Rigs and Retargeter |
| `docs/` | Findings and before/after screenshots |

To refresh the mirror from the Perforce workspace, run `tools/sync_from_project.sh`.

To use the changed assets, copy `project/Content/...` over the same paths in your project, with the editor closed.

Engine: Unreal Engine 5.8 (macOS).
