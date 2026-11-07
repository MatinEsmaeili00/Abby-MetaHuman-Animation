# Job 47: final posture fix. Retarget pose "Upright" = UprightSpine_B (torso auto-align offsets removed, pelvis kept
# so the legs don't change) + clavicles pitch +4 deg (cancels the ~3 deg extra shoulder drop the retarget added).
# Retarget walk / jog / run with it, copy the L/R foot-sync markers from the _Sync clips (same frames), measure.
import unreal

EAL = unreal.EditorAssetLibrary
AL = unreal.AnimationLibrary
DIR = "/Game/Abby_Animation/Posture"
T = unreal.RetargetSourceOrTarget.TARGET
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(), "stop PIE first"

rtg = unreal.load_asset(DIR + "/RTG_Mixamo_To_Abby_Posture")
c = unreal.IKRetargeterController.get_controller(rtg)
if "Upright" not in [str(p) for p in c.get_retarget_poses(T)]:
    c.duplicate_retarget_pose("UprightSpine_B", "Upright", T)
c.set_current_retarget_pose("Upright", T)
for b in ("clavicle_l", "clavicle_r"):
    c.set_rotation_offset_for_retarget_pose_bone(b, unreal.Rotator(pitch=4.0).quaternion(), T)
print("Upright pose offsets:", {b: [round(v, 1) for v in (lambda r: (r.roll, r.pitch, r.yaw))(c.get_rotation_offset_for_retarget_pose_bone(b, T).rotator())]
                                for b in ("pelvis", "spine_01", "spine_02", "spine_03", "spine_04", "clavicle_l", "clavicle_r", "upperarm_l")})
print("RTG saved", EAL.save_loaded_asset(rtg, only_if_is_dirty=False))

inputs = unreal.IKRetargetBatchOperationInputs()
inputs.assets_to_retarget = [EAL.find_asset_data(p) for p in ["/Game/Animation2/Walking_Anim", "/Game/Animation2/Jogging", "/Game/Animation2/Running__2_"]]
inputs.source_mesh = unreal.load_asset("/Game/Animation2/Walking")
inputs.target_mesh = unreal.load_asset("/Game/MetaHumans/MH_CH_Abby5/Body/SKM_MH_CH_Abby5_BodyMesh")
inputs.ik_retarget_asset = rtg
inputs.target_path = DIR
inputs.use_source_path = False
inputs.prefix = "Abby_"
inputs.suffix = "_Upright"
inputs.include_referenced_assets = False
inputs.overwrite_existing_files = True
out = [str(a.package_name) for a in unreal.IKRetargetBatchOperation.run_batch_retarget(inputs)]
print("retargeted:", out)

# foot-sync markers: same source frames, so the marker times carry over 1:1
for new_path, old_path in zip(sorted(out), sorted(["/Game/Abby_Animation/Enhanced/AbbyJog_Sync", "/Game/Abby_Animation/Enhanced/AbbyRun_Sync",
                                                   "/Game/Abby_Animation/Enhanced/AbbyWalk_Sync"])):
    new, old = unreal.load_asset(new_path), unreal.load_asset(old_path)
    assert abs(new.get_play_length() - old.get_play_length()) < 1e-3, (new_path, old_path)
    if "FootSync" not in [str(n) for n in AL.get_animation_notify_track_names(new)]:
        AL.add_animation_notify_track(new, "FootSync")
    if not AL.get_animation_sync_markers(new):
        for m in AL.get_animation_sync_markers(old):
            AL.add_animation_sync_marker(new, m.marker_name, m.time, "FootSync")
    print(new_path.split("/")[-1], "<- markers of", old_path.split("/")[-1], [(str(m.marker_name), round(m.time, 3)) for m in AL.get_animation_sync_markers(new)],
          "saved", EAL.save_loaded_asset(new, only_if_is_dirty=False))
