import unreal
EAL = unreal.EditorAssetLibrary
ENH = "/Game/Abby_Animation/Enhanced"
ABP = f"{ENH}/ABP_Abby_Enhanced"
if not EAL.does_asset_exist(ABP):
    skel = unreal.load_asset("/Game/MetaHumans/MH_CH_Abby5/Body/SKM_MH_CH_Abby5_BodyMesh").skeleton
    f = unreal.AnimBlueprintFactory()
    f.set_editor_property("target_skeleton", skel)
    f.set_editor_property("parent_class", unreal.AnimInstance)
    f.set_editor_property("preview_skeletal_mesh", unreal.load_asset("/Game/MetaHumans/MH_CH_Abby5/Body/SKM_MH_CH_Abby5_BodyMesh"))
    unreal.AssetToolsHelpers.get_asset_tools().create_asset("ABP_Abby_Enhanced", ENH, unreal.AnimBlueprint, f)
abp = unreal.load_asset(ABP)
print("created", abp.get_path_name())
EAL.save_loaded_asset(abp, only_if_is_dirty=False)
