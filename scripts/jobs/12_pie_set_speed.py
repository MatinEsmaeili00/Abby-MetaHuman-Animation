import unreal
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
print("game world:", world.get_name() if world else None)
abbys = [a for a in unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Pawn) if "Abby8" in a.get_class().get_name()]
for a in abbys:
    a.set_editor_property("speed", 0.85)
    body = [c for c in a.get_components_by_class(unreal.SkeletalMeshComponent) if c.get_name() == "Body"][0]
    for c in a.get_components_by_class(unreal.SkeletalMeshComponent):
        leader = c.get_editor_property("leader_pose_component")
        print(c.get_name(), "mesh", c.skeletal_mesh_asset.get_name() if c.skeletal_mesh_asset else None,
              "leader", leader.get_name() if leader else None, "visible", c.is_visible())
    print(a.get_name(), "speed", a.get_editor_property("speed"), "anim", body.get_anim_instance().get_class().get_name() if body.get_anim_instance() else None)
