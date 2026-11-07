# MetaHuman Anatomy Layers (UE 5.8 plugin)

Muscle and skeleton layers that follow a MetaHuman body's animation with no extra Anim Blueprint and no per-frame cost.

## How it works

The Chaos Flesh "Emil" anatomy meshes use anatomical limb bone names (`humerus`, `ulna`, `femur`, `tibia`, `ankle`). MetaHuman bodies use `upperarm`, `lowerarm`, `thigh`, `calf`, `foot`. This plugin ships copies of the anatomy meshes with their limb bones **renamed to MetaHuman names**. Twist bones are matched by their measured position along each limb.

With every bone name matching, the anatomy meshes can use **Leader Pose** on the MetaHuman `Body`, exactly like the face and clothing do. They then:

- follow any animation on the body: Anim BP, sequencer, LiveLink, mocap;
- take the body's proportions, so the muscles and bones sit inside the skin;
- cost nothing extra at runtime (no extra pose evaluation).

## Contents

| Path | What |
|---|---|
| `Content/Anatomy/` | `SKM_Anatomy_Muscles_UpperBody`, `SKM_Anatomy_Skeleton_UpperBody`, their skeleton, materials and textures (self-contained, no `/Game` references) |
| `Content/Python/anatomy_layers/` | Editor tools: `build_meshes()` (re-create the renamed meshes from any anatomy source) and `wire_blueprint()` (attach the layers to a MetaHuman Blueprint) |

## Use it in another project

1. Copy `Plugins/MetaHumanAnatomyLayers/` into the other project's `Plugins/` folder and enable it.
2. In your MetaHuman Blueprint, add two Skeletal Mesh components **as children of `Body`**, using `SKM_Anatomy_Muscles_UpperBody` and `SKM_Anatomy_Skeleton_UpperBody`. Leave Anim Class empty.
   The stock MetaHuman construction script (`EnableMasterPose` on Body's children) then sets Leader Pose automatically. Or call **Set Leader Pose Component (Body)** yourself.
3. Optional, with Python enabled:
   ```python
   from anatomy_layers import build
   build.wire_blueprint("/Game/MetaHumans/MyHuman/BP_MyHuman")
   ```
