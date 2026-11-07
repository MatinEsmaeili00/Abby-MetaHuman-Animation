# Job 39: frame Abby full-body in PIE (spring arm out to 260 cm, pivot at chest height).
import unreal
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
pawn = unreal.GameplayStatics.get_player_controller(world, 0).get_controlled_pawn()
arm = pawn.get_component_by_class(unreal.SpringArmComponent)
if arm:
    arm.set_editor_property("target_arm_length", 260.0)
    arm.set_editor_property("relative_location", unreal.Vector(0, 0, 105))
    mc = pawn.get_component_by_class(unreal.CPP_MouseFunctionComp)
    if mc:
        mc.sync_from_current_spring_arm()
print(pawn.get_class().get_name(), "arm", arm.get_editor_property("target_arm_length") if arm else None)
