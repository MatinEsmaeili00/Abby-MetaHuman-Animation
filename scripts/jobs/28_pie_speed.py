import sys, unreal
speed = 0.25
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Pawn):
    if "Abby8" in a.get_class().get_name():
        a.set_editor_property("speed", speed)
        body = [c for c in a.get_components_by_class(unreal.SkeletalMeshComponent) if c.get_name() == "Body"][0]
        ai = body.get_anim_instance()
        print(a.get_name(), "pawn speed", round(a.get_editor_property("speed"), 2), "anim", ai.get_class().get_name(),
              "blend speed", round(ai.get_editor_property("BlendSpeed"), 3))
