# Job 60: in PIE, run speed paused at a few gait phases; measure where the head sits relative to the neck base with
# the neck correction at 0 and at NECK degrees (the anim instance's NeckUprightAtRun). + = head forward of the neck.
# NOTE: the pose is read in the same call that sets the time, i.e. one frame late. For exact numbers set the time in one
# bridge call and read the sockets in the next (that's how the table in docs/04 was measured).
import math
import unreal

NECK = __NECK__
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
pawn = unreal.GameplayStatics.get_player_controller(world, 0).get_controlled_pawn()
quiet = unreal.PropertyAccessChangeNotifyMode.NEVER
pawn.set_editor_property("speed", 0.95, quiet)
body = [c for c in pawn.get_components_by_class(unreal.SkeletalMeshComponent) if c.get_name() == "Body"][0]
ai = body.get_anim_instance()
ai.set_editor_property("neck_upright_at_run", float(NECK), quiet)
ai.set_editor_property("neck_upright_at_jog", float(NECK) / 2.0, quiet)
tl = pawn.get_component_by_class(unreal.AnimationTimelineComp)
tl.pause()
tl.set_normalized_time(float(__PHASE__))
n = body.get_socket_location("neck_01")
h = body.get_socket_location("head")
p = body.get_socket_location("pelvis")
lat = body.get_socket_location("upperarm_l") - body.get_socket_location("upperarm_r")
up = unreal.Vector(0, 0, 1)
f = body.get_right_vector()          # MetaHuman meshes face +Y of the mesh component
v = h - n
print("neck %+5.1f deg | phase %.2f | blend %.2f | correction %s | head pitch (neck->head from vertical) %+.1f deg" % (
    NECK, tl.get_normalized_time(), ai.get_editor_property("blend_speed"), ai.get_editor_property("neck_correction"),
    math.degrees(math.atan2(v.dot(f), v.dot(up)))))
