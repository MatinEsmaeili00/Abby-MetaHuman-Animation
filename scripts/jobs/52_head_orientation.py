# Job 52: head orientation (where the face points) relative to rest, source vs Abby: + = face tilted down.
import math
import unreal
AP = unreal.AnimPoseExtensions
W = unreal.AnimPoseSpaces.WORLD
OPTS = unreal.AnimPoseEvaluationOptions()


def face_pitch(rot_rest, rot_now, fwd_rest):
    d = rot_now.rotate_vector(rot_rest.unrotate_vector(fwd_rest))
    return math.degrees(math.atan2(-d.z, math.hypot(d.x, d.y)))


def run(mesh, anim, head, fwd):
    m = unreal.SkeletonModifier()
    m.set_skeletal_mesh(unreal.load_asset(mesh))
    rest = m.get_bone_transform(head, True).rotation
    a = unreal.load_asset(anim)
    n = unreal.AnimationLibrary.get_num_frames(a)
    vals = [face_pitch(rest, AP.get_bone_pose(AP.get_anim_pose_at_time(a, a.get_play_length() * i / max(n - 1, 1), OPTS), head, W).rotation, fwd) for i in range(n)]
    return sum(vals) / n, min(vals), max(vals)


FWD = unreal.Vector(0, 1, 0)   # both characters face +Y in their rest pose
for g, src, cur, new in [("walk", "/Game/Animation2/Walking_Anim", "/Game/Abby_Animation/Posture/Abby_Walking_Anim_Upright", "/Game/Abby_Animation/Posture/Abby_Walking_Anim_Posture"),
                         ("jog", "/Game/Animation2/Jogging", "/Game/Abby_Animation/Posture/Abby_Jogging_Upright", "/Game/Abby_Animation/Posture/Abby_Jogging_Posture"),
                         ("run", "/Game/Animation2/Running__2_", "/Game/Abby_Animation/Posture/Abby_Running__2__Upright", "/Game/Abby_Animation/Posture/Abby_Running__2__Posture")]:
    s = run("/Game/Animation2/Walking", src, "Head", FWD)
    u = run("/Game/MetaHumans/MH_CH_Abby5/Body/SKM_MH_CH_Abby5_BodyMesh", cur, "head", FWD)
    p = run("/Game/MetaHumans/MH_CH_Abby5/Body/SKM_MH_CH_Abby5_BodyMesh", new, "head", FWD)
    print("%-4s face down vs rest (avg/min/max): Mixamo %+5.1f %+5.1f %+5.1f | Abby Upright %+5.1f %+5.1f %+5.1f | +neck %+5.1f %+5.1f %+5.1f" % (g, *s, *u, *p))
