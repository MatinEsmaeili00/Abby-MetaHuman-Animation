# Job 48: ABP_Abby_Timeline uses the Upright clips (evaluator nodes were rebuilt through MCP; here the class
# defaults that UCPP_LocomotionAnimInstance reads for cycle lengths and sync markers).
import unreal
EAL = unreal.EditorAssetLibrary
P = "/Game/Abby_Animation/Posture/"
abp = unreal.load_asset("/Game/Abby_Animation/Enhanced/ABP_Abby_Timeline")
cdo = unreal.get_default_object(abp.generated_class())
cdo.set_editor_property("walk_anim", unreal.load_asset(P + "Abby_Walking_Anim_Upright"))
cdo.set_editor_property("jog_anim", unreal.load_asset(P + "Abby_Jogging_Upright"))
cdo.set_editor_property("run_anim", unreal.load_asset(P + "Abby_Running__2__Upright"))
unreal.BlueprintEditorLibrary.compile_blueprint(abp)
print("saved", EAL.save_loaded_asset(abp, only_if_is_dirty=False),
      [cdo.get_editor_property(k).get_name() for k in ("walk_anim", "jog_anim", "run_anim")])
