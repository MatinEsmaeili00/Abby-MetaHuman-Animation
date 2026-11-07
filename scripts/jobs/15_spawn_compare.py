import unreal
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
body = unreal.load_asset("/Game/MetaHumans/MH_CH_Abby5/Body/SKM_MH_CH_Abby5_BodyMesh")
pairs = [("CMP_Old_Run", "/Game/Abby_Animation/New/AbbyRunning__2_", unreal.Vector(900, 0, 0)),
         ("CMP_Fixed_Run", "/Game/Abby_Animation/Fixed/Abby_Running__2__Fixed", unreal.Vector(1100, 0, 0))]
for label, anim_path, loc in pairs:
    for a in eas.get_all_level_actors():
        if a.get_actor_label() == label:
            eas.destroy_actor(a)
    a = eas.spawn_actor_from_class(unreal.SkeletalMeshActor, loc, unreal.Rotator(0, 0, 0))
    a.set_actor_label(label)
    comp = a.skeletal_mesh_component
    comp.set_skeletal_mesh_asset(body)
    comp.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE)
    comp.override_animation_data(unreal.load_asset(anim_path), True, True, 0.0, 1.0)
    print("spawned", label, anim_path)
