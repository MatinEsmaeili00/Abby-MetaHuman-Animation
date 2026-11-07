# Job 44: side-by-side posture check in the editor world (temporary actors, not saved):
# current clip vs the Upright clip, for walk and run, frozen at the same source time (needs Simulate to evaluate).
# TIME_FRACTION is substituted before running; run with "cleanup" to remove the actors.
import unreal

TIME_FRACTION = __T__
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
body = unreal.load_asset("/Game/MetaHumans/MH_CH_Abby5/Body/SKM_MH_CH_Abby5_BodyMesh")
pairs = [("CMP_Walk_Now", "/Game/Abby_Animation/Enhanced/AbbyWalk_Sync", 600),
         ("CMP_Walk_Upright", "/Game/Abby_Animation/Posture/Abby_Walking_Anim_Upright", 700),
         ("CMP_Run_Now", "/Game/Abby_Animation/Enhanced/AbbyRun_Sync", 850),
         ("CMP_Run_Upright", "/Game/Abby_Animation/Posture/Abby_Running__2__Upright", 950)]
for a in eas.get_all_level_actors():
    if a.get_actor_label().startswith("CMP_"):
        eas.destroy_actor(a)
if TIME_FRACTION >= 0:
    for label, path, y in pairs:
        anim = unreal.load_asset(path)
        a = eas.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(1500, y, 0), unreal.Rotator(0, 0, 0))
        a.set_actor_label(label)
        comp = a.skeletal_mesh_component
        comp.set_skeletal_mesh_asset(body)
        comp.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE)
        comp.override_animation_data(anim, True, True, anim.get_play_length() * TIME_FRACTION, 0.0)
        comp.set_update_animation_in_editor(True)
        print("spawned", label, path)
