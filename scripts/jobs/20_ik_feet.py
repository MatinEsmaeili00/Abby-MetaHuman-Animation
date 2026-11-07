import unreal
EAL = unreal.EditorAssetLibrary
T = unreal.RetargetSourceOrTarget.TARGET
rtg = unreal.load_asset("/Game/Abby_Animation/Fixed/RTG_Mixamo_To_Abby_Fixed")
c = unreal.IKRetargeterController.get_controller(rtg)
c.set_current_retarget_pose("Default Pose", T)
if "Aligned_To_Mixamo_TPose" in [str(p) for p in c.get_retarget_poses(T)]:
    c.remove_retarget_pose("Aligned_To_Mixamo_TPose", T)
ops = lambda: [str(c.get_op_name(i)) for i in range(c.get_num_retarget_ops())]
if "Retarget IK Goals" not in ops(): c.add_retarget_op("/Script/IKRig.IKRetargetIKChainsOp")
if "Floor Constraint" not in ops(): c.add_retarget_op("/Script/IKRig.IKRetargetFloorConstraintOp")
for i, n in enumerate(ops()):
    if n in ("Run IK Rig", "Retarget IK Goals", "Floor Constraint"):
        c.set_retarget_op_enabled(i, True)
        c.run_op_initial_setup(i)
print("ops:", [(n, c.get_retarget_op_enabled(i)) for i, n in enumerate(ops())])
i_ik = ops().index("Retarget IK Goals")
oc = c.get_op_controller(i_ik); st = oc.get_settings()
chains = list(st.get_editor_property("chains_to_retarget"))
if chains:
    print("IK chain fields:", [k for k in dir(chains[0]) if not k.startswith("_") and not callable(getattr(chains[0], k, None))])
out = []
for ch in chains:
    name = str(ch.get_editor_property("target_chain_name"))
    ch.set_editor_property("enable_ik", "Leg" in name)
    out.append(ch)
st.set_editor_property("chains_to_retarget", out); oc.set_settings(st)
print("IK chains:", [(str(ch.get_editor_property("target_chain_name")), ch.get_editor_property("enable_ik")) for ch in oc.get_settings().get_editor_property("chains_to_retarget")])
i_fl = ops().index("Floor Constraint"); fs = c.get_op_controller(i_fl).get_settings()
print("floor settings:", {k: str(getattr(fs, k))[:120] for k in dir(fs) if not k.startswith("_") and not callable(getattr(fs, k, None))})
EAL.save_loaded_asset(rtg, only_if_is_dirty=False)
inputs = unreal.IKRetargetBatchOperationInputs()
inputs.assets_to_retarget = [EAL.find_asset_data(p) for p in ["/Game/Animation2/Walking_Anim", "/Game/Animation2/Jogging", "/Game/Animation2/Running__2_"]]
inputs.source_mesh = unreal.load_asset("/Game/Animation2/Walking")
inputs.target_mesh = unreal.load_asset("/Game/MetaHumans/MH_CH_Abby5/Body/SKM_MH_CH_Abby5_BodyMesh")
inputs.ik_retarget_asset = rtg; inputs.target_path = "/Game/Abby_Animation/Fixed"
inputs.prefix = "Abby_"; inputs.suffix = "_Fixed"; inputs.include_referenced_assets = False; inputs.overwrite_existing_files = True
for a in unreal.IKRetargetBatchOperation.run_batch_retarget(inputs):
    EAL.save_asset(str(a.package_name), only_if_is_dirty=False)
