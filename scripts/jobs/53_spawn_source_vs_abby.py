# Job 53: Mixamo source run vs Abby's run, side by side at the same source time (Simulate to evaluate).
# Labels CMP_*; run with T < 0 to remove them.
import unreal
T_FRACTION = __T__
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for a in eas.get_all_level_actors():
    if a.get_actor_label().startswith("CMP_"):
        eas.destroy_actor(a)
if T_FRACTION >= 0:
    for label, mesh, anim, y in [("CMP_Src_Run", "/Game/Animation2/Walking", "/Game/Animation2/Running__2_", 700),
                                 ("CMP_Abby_Run", "/Game/MetaHumans/MH_CH_Abby5/Body/SKM_MH_CH_Abby5_BodyMesh", "/Game/Abby_Animation/Posture/Abby_Running__2__Upright", 820),
                                 ("CMP_Src_Jog", "/Game/Animation2/Walking", "/Game/Animation2/Jogging", 980),
                                 ("CMP_Abby_Jog", "/Game/MetaHumans/MH_CH_Abby5/Body/SKM_MH_CH_Abby5_BodyMesh", "/Game/Abby_Animation/Posture/Abby_Jogging_Upright", 1100)]:
        a = eas.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(1500, y, 0), unreal.Rotator(0, 0, 0))
        a.set_actor_label(label)
        comp = a.skeletal_mesh_component
        comp.set_skeletal_mesh_asset(unreal.load_asset(mesh))
        comp.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE)
        an = unreal.load_asset(anim)
        comp.override_animation_data(an, True, True, an.get_play_length() * T_FRACTION, 0.0)
        print("spawned", label)
