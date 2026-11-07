# MetaHuman Anatomy Layers (UE 5.8 plugin)

Muscle and skeleton layers that follow a MetaHuman body's animation. There's no extra Anim Blueprint and no per-frame cost.

## How it works

The Chaos Flesh "Emil" anatomy meshes use anatomical limb bone names (`humerus`, `ulna`, `femur`, `tibia`, `ankle`). MetaHuman bodies use `upperarm`, `lowerarm`, `thigh`, `calf`, `foot`. This plugin ships copies of the anatomy meshes with those limb bones **renamed to MetaHuman names**. Twist bones are paired by their measured position along each limb; for example, Emil `ulna_twist_01` maps to MetaHuman `lowerarm_twist_02`, so a name-based guess would have been wrong.

With matching bone names, the anatomy meshes use **Leader Pose** on the MetaHuman `Body`, just like the face and clothing. They then:

- follow any animation on the body: Anim BP, Sequencer, LiveLink, mocap;
- take the body's proportions, so the muscles and bones sit inside the skin;
- cost nothing extra at runtime (no extra pose evaluation).

## Contents

| Asset | What |
|---|---|
| `/MetaHumanAnatomyLayers/Anatomy/Meshes/SKM_Anatomy_Muscles_UpperBody` | Upper-body muscle mesh (MetaHuman bone names) |
| `/MetaHumanAnatomyLayers/Anatomy/Meshes/SKM_Anatomy_Skeleton_UpperBody` | Upper-body skeleton (bones) mesh |
| `/MetaHumanAnatomyLayers/Anatomy/Meshes/SKM_Anatomy_Muscles_UpperBody_Skeleton` | Their shared Skeleton asset |
| `/MetaHumanAnatomyLayers/Anatomy/Materials`, `/Textures` | Self-contained copies of the muscle and bone materials |
| `Content/Python/anatomy_layers/build.py` | Editor tools: `build_all()` re-creates the meshes from an anatomy source; `wire_blueprint()` attaches the layers to a MetaHuman Blueprint |

Nothing in `Anatomy/` references `/Game`, so the folder works in any project.

## Use it in another project

1. Copy `Plugins/MetaHumanAnatomyLayers/` into the other project's `Plugins/` folder, then enable it under Edit → Plugins.
2. In your MetaHuman Blueprint, add two **Skeletal Mesh** components **as children of `Body`**:
   - Skeletal Mesh Asset: `SKM_Anatomy_Muscles_UpperBody` / `SKM_Anatomy_Skeleton_UpperBody`
   - Anim Class: empty; Use Bounds From Leader Pose Component: on
3. Leader Pose: the stock MetaHuman construction script (`EnableMasterPose` on Body's children) sets it automatically. Otherwise call **Set Leader Pose Component (Body)** on both in BeginPlay or the construction script.

With Python enabled, step 2 is one call:

```python
from anatomy_layers import build
build.wire_blueprint("/Game/MetaHumans/MyHuman/BP_MyHuman")   # creates or updates MuscleMesh + SkeletonMesh under Body
```

## Rebuild from source

`build.build_all(metahuman_body="/Game/MetaHumans/<Name>/Body/SKM_<Name>_BodyMesh")` exports the Emil anatomy meshes to ASCII FBX, renames the bones in the file (so the new Skeleton gets MetaHuman names from the start), re-imports them into this plugin and re-points the materials. It needs the Chaos Flesh example content (`/Game/ExampleContent/5_5_ChaosFlesh`) in the project.

## Known limits

- These are **upper-body** anatomy meshes (the Emil example covers the torso, arms and upper legs).
- Emil is a larger male anatomy, so some muscles poke slightly through a smaller body's skin unless the skin is faded or translucent.
- Emil's finger bones are a little longer than a typical MetaHuman's, so fingertips can poke out.
