import unreal, runpy
EAL = unreal.EditorAssetLibrary
T = unreal.RetargetSourceOrTarget.TARGET
rtg = unreal.load_asset("/Game/Abby_Animation/Fixed/RTG_Mixamo_To_Abby_Fixed")
c = unreal.IKRetargeterController.get_controller(rtg)
c.set_current_retarget_pose("Aligned_To_Mixamo_TPose", T)
# Feet: both rest poses stand flat-footed, so map rest foot -> rest foot (no direction alignment)
for b in ["foot_l", "foot_r", "ball_l", "ball_r"]:
    c.set_rotation_offset_for_retarget_pose_bone(b, unreal.Quat(0, 0, 0, 1), T)
c.set_root_offset_in_retarget_pose(unreal.Vector(0, 0, 0), T)
EAL.save_loaded_asset(rtg, only_if_is_dirty=False)
inputs = unreal.IKRetargetBatchOperationInputs()
inputs.assets_to_retarget = [EAL.find_asset_data(p) for p in ["/Game/Animation2/Walking_Anim", "/Game/Animation2/Jogging", "/Game/Animation2/Running__2_"]]
inputs.source_mesh = unreal.load_asset("/Game/Animation2/Walking")
inputs.target_mesh = unreal.load_asset("/Game/MetaHumans/MH_CH_Abby5/Body/SKM_MH_CH_Abby5_BodyMesh")
inputs.ik_retarget_asset = rtg
inputs.target_path = "/Game/Abby_Animation/Fixed"
inputs.prefix = "Abby_"; inputs.suffix = "_Fixed"
inputs.include_referenced_assets = False; inputs.overwrite_existing_files = True
for a in unreal.IKRetargetBatchOperation.run_batch_retarget(inputs):
    EAL.save_asset(str(a.package_name), only_if_is_dirty=False)
    print("re-retargeted", a.package_name)
