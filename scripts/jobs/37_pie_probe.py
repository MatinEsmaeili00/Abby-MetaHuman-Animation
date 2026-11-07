# Job 37: probe the running PIE session: possessed pawn, its components, widgets, and the slider state.
# ACTION is substituted before running: "status", "depth:<0..1>", "layer:<i>", "play", "pause", "reverse",
# "time:<0..1>", "speed:<0..1>", "switch:<+1|-1>".
import unreal

ACTION = "__ACTION__"

world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
pc = unreal.GameplayStatics.get_player_controller(world, 0)
pawn = pc.get_controlled_pawn() if pc else None
print("world:", world.get_name() if world else None, "| pc:", pc.get_class().get_name() if pc else None,
      "| pawn:", pawn.get_class().get_name() if pawn else None)

anat = pawn.get_component_by_class(unreal.AnatomyViewComp) if pawn else None
tl = pawn.get_component_by_class(unreal.AnimationTimelineComp) if pawn else None

kind, _, arg = ACTION.partition(":")
if kind == "depth" and anat:
    anat.set_reveal_depth(float(arg), False)
elif kind == "layer" and anat:
    anat.show_layer(int(arg))
elif kind == "play" and tl:
    tl.play_forward()
elif kind == "pause" and tl:
    tl.pause()
elif kind == "reverse" and tl:
    tl.play_reverse()
elif kind == "time" and tl:
    tl.pause()
    tl.set_normalized_time(float(arg))
elif kind == "speed" and pawn:
    pawn.set_editor_property("speed", float(arg), unreal.PropertyAccessChangeNotifyMode.NEVER)  # no construction-script rerun
elif kind == "switch" and pc:
    pc.switch_pawn(int(arg))
    pawn = pc.get_controlled_pawn()
    print("now possessing:", pawn.get_class().get_name() if pawn else None)
    anat = pawn.get_component_by_class(unreal.AnatomyViewComp) if pawn else None
    tl = pawn.get_component_by_class(unreal.AnimationTimelineComp) if pawn else None

if anat:
    print("anatomy depth %.3f | opacities %s" % (anat.get_reveal_depth(), [round(anat.get_layer_opacity(i), 2) for i in range(anat.get_num_layers())]))
    for c in pawn.get_components_by_class(unreal.MeshComponent):
        if c.get_name() in ("Body", "Face", "MuscleMesh", "SkeletonMesh", "Hair"):
            m = c.get_material(0)
            print("   %-12s visible=%s mat0=%s" % (c.get_name(), c.is_visible(), m.get_name() if m else None))
if tl:
    body = [c for c in pawn.get_components_by_class(unreal.SkeletalMeshComponent) if c.get_name() == "Body"][0]
    ai = body.get_anim_instance()
    print("timeline t=%.3f state=%s cycle=%.3fs scrub=%s | anim=%s" % (tl.get_normalized_time(), tl.get_play_state(), tl.get_cycle_length(),
          tl.can_scrub(), ai.get_class().get_name() if ai else None))
    if isinstance(ai, unreal.CPP_LocomotionAnimInstance):
        g = ai.get_editor_property
        print("   phase=%.3f cycle#=%d blend=%.2f walk=%.3f jog=%.3f run=%.3f a1=%.2f a2=%.2f" % (
            g("phase"), g("cycle_index"), g("blend_speed"), g("walk_time"), g("jog_time"), g("run_time"), g("walk_jog_alpha"), g("jog_run_alpha")))

lib = getattr(unreal, "WidgetBlueprintLibrary", None)
if lib:
    widgets = lib.get_all_widgets_of_class(world, unreal.UserWidget, True)
    for w in widgets:
        if w.get_class().get_name() in ("WB_AmationTimeline_C", "WB_AnatomyViewSwitcher_C", "BP_SpeedSlider_C", "WB_PawnSwitcher_C"):
            print("   %-26s enabled=%s" % (w.get_class().get_name(), w.get_is_enabled()))
