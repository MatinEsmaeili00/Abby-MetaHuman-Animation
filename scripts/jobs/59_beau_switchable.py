# Job 59: Beau's Body plays ABP_Beau_Timeline; Up / Down cycles Abby -> Beau -> skeleton model.
import unreal
EAL = unreal.EditorAssetLibrary
SDS = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
LIB = unreal.SubobjectDataBlueprintFunctionLibrary
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(), "stop PIE first"

bp = unreal.load_asset("/Game/MadisonTesting/BeauMHCharacter/BP_Beau_Pawn")
abp = unreal.load_asset("/Game/MadisonTesting/BeauMHCharacter/Animation/ABP_Beau_Timeline").generated_class()
for h in SDS.k2_gather_subobject_data_for_blueprint(bp):
    d = SDS.k2_find_subobject_data_from_handle(h)
    if str(LIB.get_variable_name(d)) == "Body":
        body = LIB.get_object(d)
        body.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT)
        body.set_editor_property("anim_class", abp)
        print("Beau Body anim class ->", body.get_editor_property("anim_class").get_name())
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
print("BP_Beau_Pawn saved", EAL.save_loaded_asset(bp, only_if_is_dirty=False))

pc_bp = unreal.load_asset("/Game/Blueprints/BP_PlayerController")
pc = unreal.get_default_object(pc_bp.generated_class())
pc.set_editor_property("switchable_pawn_classes", [
    unreal.load_asset("/Game/MetaHumans/MH_CH_Abby5/BP_MH_CH_Abby8").generated_class(),
    bp.generated_class(),
    unreal.load_asset("/Game/Blueprints/BP_SkeletonModel").generated_class()])
unreal.BlueprintEditorLibrary.compile_blueprint(pc_bp)
print("switchable:", [c.get_name() for c in pc.get_editor_property("switchable_pawn_classes")], "saved", EAL.save_loaded_asset(pc_bp, only_if_is_dirty=False))
