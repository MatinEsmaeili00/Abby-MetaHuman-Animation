# Job 64: Beau's neck correction. Measured in PIE at run speed (job 60 style, two-step so the pose is evaluated):
#   head forward of vertical, no correction: Abby 26..36 deg, Beau 9..15 deg (after job 63 fixed his bone lengths)
#   with 17 deg: Abby 10..19 deg, Beau -1.5..-7 deg (leaning back) -> Beau gets 8 (run) / 7 (jog), Abby keeps 17 / 14.
import unreal
EAL = unreal.EditorAssetLibrary
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(), "stop PIE first"
abp = unreal.load_asset("/Game/MadisonTesting/BeauMHCharacter/Animation/ABP_Beau_Timeline")
cdo = unreal.get_default_object(abp.generated_class())
cdo.set_editor_property("neck_upright_at_run", 8.0)
cdo.set_editor_property("neck_upright_at_jog", 7.0)
unreal.BlueprintEditorLibrary.compile_blueprint(abp)
cdo = unreal.get_default_object(abp.generated_class())
print("Beau neck run/jog:", cdo.get_editor_property("neck_upright_at_run"), cdo.get_editor_property("neck_upright_at_jog"),
      "saved", EAL.save_loaded_asset(abp, only_if_is_dirty=False))
