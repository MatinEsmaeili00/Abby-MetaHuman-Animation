import unreal
EAL = unreal.EditorAssetLibrary; AL = unreal.AnimationLibrary
AP = unreal.AnimPoseExtensions; W = unreal.AnimPoseSpaces.WORLD
ENH = "/Game/Abby_Animation/Enhanced"
SRC = {"AbbyWalk_Sync": "/Game/Abby_Animation/New/AbbyWalking_Anim",
       "AbbyJog_Sync": "/Game/Abby_Animation/New/AbbyJogging",
       "AbbyRun_Sync": "/Game/Abby_Animation/New/AbbyRunning__2_"}
if not EAL.does_directory_exist(ENH): EAL.make_directory(ENH)
opts = unreal.AnimPoseEvaluationOptions()
anims = {}
for name, src in SRC.items():
    dst = f"{ENH}/{name}"
    if not EAL.does_asset_exist(dst): EAL.duplicate_asset(src, dst)
    a = unreal.load_asset(dst); anims[name] = a
    AL.remove_all_animation_sync_markers(a)
    if "FootSync" not in [str(t) for t in AL.get_animation_notify_track_names(a)]:
        AL.add_animation_notify_track(a, "FootSync")
    n = AL.get_num_frames(a); L = a.get_play_length(); dt = L / max(n - 1, 1)
    # sample densely; a foot is at mid-stance when its forward offset from the pelvis crosses 0 going backward
    steps = n * 4
    prev = None; marks = []
    for i in range(steps + 1):
        t = L * i / steps
        pose = AP.get_anim_pose_at_time(a, t, opts)
        pel = AP.get_bone_pose(pose, "pelvis", W).translation
        cur = {s: AP.get_bone_pose(pose, f"foot_{s}", W).translation.y - pel.y for s in ("l", "r")}
        if prev:
            for s in ("l", "r"):
                if prev[s] > 0 >= cur[s]:
                    tc = t - (L / steps) * (cur[s] / (cur[s] - prev[s]))
                    marks.append((s.upper(), max(0.0, min(L, tc))))
        prev = cur
    for m, t in marks:
        AL.add_animation_sync_marker(a, m, t, "FootSync")
    EAL.save_loaded_asset(a, only_if_is_dirty=False)
    print(f"{name}: {L:.3f}s markers {[(m, round(t, 3)) for m, t in marks]}")

# 1D blend space over Speed (0..1, the slider range)
BS = f"{ENH}/BS_Abby_Locomotion"
skel = unreal.load_asset("/Game/MetaHumans/MH_CH_Abby5/Body/SKM_MH_CH_Abby5_BodyMesh").skeleton
if not EAL.does_asset_exist(BS):
    f = unreal.BlendSpaceFactory1D(); f.set_editor_property("target_skeleton", skel)
    unreal.AssetToolsHelpers.get_asset_tools().create_asset("BS_Abby_Locomotion", ENH, unreal.BlendSpace1D, f)
bs = unreal.load_asset(BS)
print("BS editable props:", [p for p in ("blend_parameters", "sample_data", "interpolation_param", "axis_to_scale_animation", "target_weight_interpolation_speed_per_sec") if True])
for p in ("blend_parameters", "sample_data", "interpolation_param"):
    try:
        v = bs.get_editor_property(p); print("  can read", p, type(v).__name__)
    except Exception as e:
        print("  cannot read", p, str(e)[:120])
