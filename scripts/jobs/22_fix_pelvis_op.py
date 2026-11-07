import unreal
EAL = unreal.EditorAssetLibrary
rtg = unreal.load_asset("/Game/Abby_Animation/Fixed/RTG_Mixamo_To_Abby_Fixed")
c = unreal.IKRetargeterController.get_controller(rtg)
ops = [str(c.get_op_name(i)) for i in range(c.get_num_retarget_ops())]
pc = c.get_op_controller(ops.index("Pelvis Motion"))
print("pelvis bones before:", pc.get_source_pelvis_bone(), pc.get_target_pelvis_bone())
pc.set_source_pelvis_bone("Hips"); pc.set_target_pelvis_bone("pelvis")
print("pelvis bones after:", pc.get_source_pelvis_bone(), pc.get_target_pelvis_bone())
fk = c.get_op_controller(ops.index("Retarget FK Chains")).get_settings()
print("FK chains:", len(fk.get_editor_property("chains_to_retarget")))
EAL.save_loaded_asset(rtg, only_if_is_dirty=False)
inputs = unreal.IKRetargetBatchOperationInputs()
inputs.assets_to_retarget = [EAL.find_asset_data(p) for p in ["/Game/Animation2/Walking_Anim", "/Game/Animation2/Jogging", "/Game/Animation2/Running__2_"]]
inputs.source_mesh = unreal.load_asset("/Game/Animation2/Walking")
inputs.target_mesh = unreal.load_asset("/Game/MetaHumans/MH_CH_Abby5/Body/SKM_MH_CH_Abby5_BodyMesh")
inputs.ik_retarget_asset = rtg; inputs.target_path = "/Game/Abby_Animation/Fixed"
inputs.prefix = "Abby_"; inputs.suffix = "_Fixed"; inputs.include_referenced_assets = False; inputs.overwrite_existing_files = True
for a in unreal.IKRetargetBatchOperation.run_batch_retarget(inputs):
    EAL.save_asset(str(a.package_name), only_if_is_dirty=False)
