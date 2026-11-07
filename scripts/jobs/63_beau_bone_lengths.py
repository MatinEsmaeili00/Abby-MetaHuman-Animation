# Job 63: Beau's retargeted clips came out with every bone ~15-20% short and neck_02 / head at ~0 length (his head sat
# on his shoulders; neck_01 and head at the same spot). Bake his own reference bone lengths back in: for every bone
# track except root and pelvis, translation = Beau's ref-pose local translation; rotation and scale stay animated.
# (Same result as "Skeleton" translation retargeting, but only for Beau's clips; the skeleton is shared with Abby.)
import unreal

AL = unreal.AnimationLibrary
EAL = unreal.EditorAssetLibrary
ROOT = "/Game/MadisonTesting/BeauMHCharacter"
BODY = ROOT + "/Unpacked/Beau/Body/SKM_MHC_Beau_BodyMesh"
CLIPS = [ROOT + "/Animation/Beau_Walking_Anim_Upright", ROOT + "/Animation/Beau_Jogging_Upright", ROOT + "/Animation/Beau_Running__2__Upright"]
KEEP = {"root", "pelvis"}
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(), "stop PIE first"

mod = unreal.SkeletonModifier()
mod.set_skeletal_mesh(unreal.load_asset(BODY))
for path in CLIPS:
    a = unreal.load_asset(path)
    names = [str(n) for n in AL.get_animation_track_names(a)]
    dm = a.get_editor_property("data_model_interface")
    keys = dm.get_number_of_keys() if hasattr(dm, "get_number_of_keys") else AL.get_num_frames(a) + 1
    ref = {}
    for b in names:
        if b not in KEEP:
            try:
                ref[b] = mod.get_bone_transform(b, False).translation
            except Exception:
                pass
    frames = [AL.get_bone_poses_for_frame(a, names, f, False) for f in range(keys)]
    ctl = a.controller
    ctl.open_bracket(unreal.Text("Beau bone lengths"), False)
    fixed = 0
    for i, b in enumerate(names):
        if b not in ref:
            continue
        pos = [ref[b] for _ in range(keys)]
        rot = [frames[f][i].rotation for f in range(keys)]
        scl = [frames[f][i].scale3d for f in range(keys)]
        ctl.set_bone_track_keys(b, pos, rot, scl, False)
        fixed += 1
    ctl.close_bracket(False)
    h = AL.get_bone_pose_for_time(a, "head", 0.3, False).translation
    print(path.split("/")[-1], "keys", keys, "tracks fixed", fixed, "/", len(names), "head local", [round(h.x, 2), round(h.y, 2), round(h.z, 2)],
          "saved", EAL.save_loaded_asset(a, only_if_is_dirty=False))
