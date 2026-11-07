import unreal
w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
for a in unreal.GameplayStatics.get_all_actors_of_class(w, unreal.Pawn):
    if "Abby8" in a.get_class().get_name():
        a.set_editor_property("speed", SPEED)
        body = [c for c in a.get_components_by_class(unreal.SkeletalMeshComponent) if c.get_name() == "Body"][0]
        ai = body.get_anim_instance()
        p = body.get_socket_location("pelvis"); h = body.get_socket_location("hand_r"); f = body.get_socket_location("foot_l")
        print(f"speed->{SPEED}  blend {ai.get_editor_property('BlendSpeed'):.2f}  pelvis z {p.z:.1f} (ref 87.4)  hand_r ({h.x-420:.1f},{h.y-80:.1f},{h.z:.1f})  foot_l z {f.z:.1f}")
