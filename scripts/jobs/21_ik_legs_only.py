import unreal
EAL = unreal.EditorAssetLibrary
T = unreal.RetargetSourceOrTarget.TARGET
rtg = unreal.load_asset("/Game/Abby_Animation/Fixed/RTG_Mixamo_To_Abby_Fixed")
c = unreal.IKRetargeterController.get_controller(rtg)
ops = [str(c.get_op_name(i)) for i in range(c.get_num_retarget_ops())]
for opname, prop in [("Retarget IK Goals", "chains_to_retarget"), ("Floor Constraint", "chains_to_affect"), ("Run IK Rig", "chains")]:
    oc = c.get_op_controller(ops.index(opname)); st = oc.get_settings()
    items = list(st.get_editor_property(prop))
    if items and not isinstance(items[0], (str, unreal.Name)):
        bools = [k for k in dir(items[0]) if not k.startswith("_") and isinstance(getattr(items[0], k, None), bool)]
        print(opname, "bool fields:", bools)
        new = []
        for it in items:
            leg = "Leg" in str(it.get_editor_property("target_chain_name"))
            for k in bools:
                if k.startswith("enable"):
                    it.set_editor_property(k, leg)
            new.append(it)
        st.set_editor_property(prop, new)
    else:
        keep = [x for x in items if "Leg" in str(x)]
        st.set_editor_property(prop, keep)
    oc.set_settings(st)
    v = oc.get_settings().get_editor_property(prop)
    print(opname, "->", [(str(x.get_editor_property("target_chain_name")), {k: getattr(x, k) for k in dir(x) if k.startswith("enable")}) if not isinstance(x, (str, unreal.Name)) else str(x) for x in v])
EAL.save_loaded_asset(rtg, only_if_is_dirty=False)
inputs = unreal.IKRetargetBatchOperationInputs()
inputs.assets_to_retarget = [EAL.find_asset_data(p) for p in ["/Game/Animation2/Walking_Anim", "/Game/Animation2/Jogging", "/Game/Animation2/Running__2_"]]
inputs.source_mesh = unreal.load_asset("/Game/Animation2/Walking")
inputs.target_mesh = unreal.load_asset("/Game/MetaHumans/MH_CH_Abby5/Body/SKM_MH_CH_Abby5_BodyMesh")
inputs.ik_retarget_asset = rtg; inputs.target_path = "/Game/Abby_Animation/Fixed"
inputs.prefix = "Abby_"; inputs.suffix = "_Fixed"; inputs.include_referenced_assets = False; inputs.overwrite_existing_files = True
for a in unreal.IKRetargetBatchOperation.run_batch_retarget(inputs):
    EAL.save_asset(str(a.package_name), only_if_is_dirty=False)
