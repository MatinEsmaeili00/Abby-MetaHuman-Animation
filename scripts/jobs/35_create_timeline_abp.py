# Job 35: create ABP_Abby_Timeline (parent UCPP_LocomotionAnimInstance) and set its gait clips.
# The AnimGraph is wired afterwards through the MCP Blueprint tools (see docs/03-ui-sliders.md).
import unreal

EAL = unreal.EditorAssetLibrary
ENH = "/Game/Abby_Animation/Enhanced"
ABP = f"{ENH}/ABP_Abby_Timeline"
BODY = "/Game/MetaHumans/MH_CH_Abby5/Body/SKM_MH_CH_Abby5_BodyMesh"

if not EAL.does_asset_exist(ABP):
    body = unreal.load_asset(BODY)
    f = unreal.AnimBlueprintFactory()
    f.set_editor_property("target_skeleton", body.skeleton)
    f.set_editor_property("parent_class", unreal.CPP_LocomotionAnimInstance)
    f.set_editor_property("preview_skeletal_mesh", body)
    unreal.AssetToolsHelpers.get_asset_tools().create_asset("ABP_Abby_Timeline", ENH, unreal.AnimBlueprint, f)

abp = unreal.load_asset(ABP)
unreal.BlueprintEditorLibrary.compile_blueprint(abp)
cdo = unreal.get_default_object(abp.generated_class())
cdo.set_editor_property("walk_anim", unreal.load_asset(f"{ENH}/AbbyWalk_Sync"))
cdo.set_editor_property("jog_anim", unreal.load_asset(f"{ENH}/AbbyJog_Sync"))
cdo.set_editor_property("run_anim", unreal.load_asset(f"{ENH}/AbbyRun_Sync"))
EAL.save_loaded_asset(abp, only_if_is_dirty=False)
print("ABP:", abp.get_path_name(), "parent ok:", isinstance(cdo, unreal.CPP_LocomotionAnimInstance))
print("walk/jog/run:", cdo.get_editor_property("walk_anim").get_name(), cdo.get_editor_property("jog_anim").get_name(), cdo.get_editor_property("run_anim").get_name())
