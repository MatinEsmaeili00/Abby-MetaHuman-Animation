# Job 50: neck fix. In the Upright clips Abby's head sits ~2-4 deg further forward than the Mixamo source
# (run: neck base -> head +5.3 deg vs +1.5 deg). Add a small neck extension to the "Upright" retarget pose
# (neck_01 yaw -3, neck_02 yaw -2; + yaw = flex forward on MetaHuman spine/neck bones), retarget into *_Posture
# clips, copy the foot-sync markers, and print the neck numbers (job 49 metric).
import math
import unreal

EAL = unreal.EditorAssetLibrary
AL = unreal.AnimationLibrary
DIR = "/Game/Abby_Animation/Posture"
T = unreal.RetargetSourceOrTarget.TARGET
NECK = {"neck_01": -3.0, "neck_02": -2.0}
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(), "stop PIE first"

rtg = unreal.load_asset(DIR + "/RTG_Mixamo_To_Abby_Posture")
c = unreal.IKRetargeterController.get_controller(rtg)
c.set_current_retarget_pose("Upright", T)
for bone, yaw in NECK.items():
    c.set_rotation_offset_for_retarget_pose_bone(bone, unreal.Rotator(yaw=yaw).quaternion(), T)
print("RTG saved", EAL.save_loaded_asset(rtg, only_if_is_dirty=False))

inputs = unreal.IKRetargetBatchOperationInputs()
inputs.assets_to_retarget = [EAL.find_asset_data(p) for p in ["/Game/Animation2/Walking_Anim", "/Game/Animation2/Jogging", "/Game/Animation2/Running__2_"]]
inputs.source_mesh = unreal.load_asset("/Game/Animation2/Walking")
inputs.target_mesh = unreal.load_asset("/Game/MetaHumans/MH_CH_Abby5/Body/SKM_MH_CH_Abby5_BodyMesh")
inputs.ik_retarget_asset = rtg
inputs.target_path = DIR
inputs.use_source_path = False
inputs.prefix = "Abby_"
inputs.suffix = "_Posture"
inputs.include_referenced_assets = False
inputs.overwrite_existing_files = True
out = sorted(str(a.package_name) for a in unreal.IKRetargetBatchOperation.run_batch_retarget(inputs))
for new_path, old_path in zip(out, [DIR + "/Abby_Jogging_Upright", DIR + "/Abby_Running__2__Upright", DIR + "/Abby_Walking_Anim_Upright"]):
    new, old = unreal.load_asset(new_path), unreal.load_asset(old_path)
    if "FootSync" not in [str(n) for n in AL.get_animation_notify_track_names(new)]:
        AL.add_animation_notify_track(new, "FootSync")
    if not AL.get_animation_sync_markers(new):
        for m in AL.get_animation_sync_markers(old):
            AL.add_animation_sync_marker(new, m.marker_name, m.time, "FootSync")
    print(new_path.split("/")[-1], "markers", len(AL.get_animation_sync_markers(new)), "saved", EAL.save_loaded_asset(new, only_if_is_dirty=False))
