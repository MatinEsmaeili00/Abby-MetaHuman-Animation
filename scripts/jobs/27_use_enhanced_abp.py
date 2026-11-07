import unreal
EAL = unreal.EditorAssetLibrary
BP = "/Game/MetaHumans/MH_CH_Abby5/BP_MH_CH_Abby8"
bp = unreal.load_asset(BP)
abp_class = unreal.load_class(None, "/Game/Abby_Animation/Enhanced/ABP_Abby_Enhanced.ABP_Abby_Enhanced_C")
sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem); lib = unreal.SubobjectDataBlueprintFunctionLibrary
for h in sds.k2_gather_subobject_data_for_blueprint(bp):
    d = sds.k2_find_subobject_data_from_handle(h)
    if str(lib.get_variable_name(d)) == "Body":
        body = lib.get_object(d)
        print("Body anim class before:", body.get_editor_property("anim_class"))
        body.set_editor_property("anim_class", abp_class)
        print("Body anim class after:", body.get_editor_property("anim_class"))
        break
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
EAL.save_loaded_asset(bp, only_if_is_dirty=False)
