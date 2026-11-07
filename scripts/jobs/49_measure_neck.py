# Job 49: neck / head posture of the Mixamo source vs Abby's Upright clips, as change from each rest pose.
# Neck flex = angle of the neck (neck base -> head) relative to the upper back (chest -> neck base), + = bent forward.
# Head pitch = angle of neck base -> head from vertical in the walking direction, + = head forward / down.
import math
import unreal

AP = unreal.AnimPoseExtensions
W = unreal.AnimPoseSpaces.WORLD
OPTS = unreal.AnimPoseEvaluationOptions()
UP = unreal.Vector(0, 0, 1)
MH = dict(chest="spine_04", neck="neck_01", head="head", ua_l="upperarm_l", ua_r="upperarm_r", foot="foot_l", ball="ball_l")
MX = dict(chest="Spine2", neck="Neck", head="Head", ua_l="LeftArm", ua_r="RightArm", foot="LeftFoot", ball="LeftToeBase")


def frame(get, b):
    c, n, h = get(b["chest"]), get(b["neck"]), get(b["head"])
    lat = (get(b["ua_l"]) - get(b["ua_r"])).normal()
    fwd = UP.cross(lat).normal()
    if fwd.dot(get(b["ball"]) - get(b["foot"])) < 0:
        fwd = fwd * -1.0
    a_back = math.degrees(math.atan2((n - c).dot(fwd), (n - c).dot(UP)))
    a_neck = math.degrees(math.atan2((h - n).dot(fwd), (h - n).dot(UP)))
    return a_neck - a_back, a_neck


def rest(mesh, b):
    m = unreal.SkeletonModifier()
    m.set_skeletal_mesh(unreal.load_asset(mesh))
    return frame(lambda x: m.get_bone_transform(x, True).translation, b)


def anim(path, b):
    a = unreal.load_asset(path)
    n = unreal.AnimationLibrary.get_num_frames(a)
    rows = [frame(lambda x, p=AP.get_anim_pose_at_time(a, a.get_play_length() * i / max(n - 1, 1), OPTS): AP.get_bone_pose(p, x, W).translation, b) for i in range(n)]
    return [sum(r[k] for r in rows) / n for k in range(2)]


rx = rest("/Game/Animation2/Walking", MX)
rh = rest("/Game/MetaHumans/MH_CH_Abby5/Body/SKM_MH_CH_Abby5_BodyMesh", MH)
print("rest: Mixamo neck flex %+.1f head pitch %+.1f | Abby neck flex %+.1f head pitch %+.1f" % (*rx, *rh))
for g, src, up in [("walk", "/Game/Animation2/Walking_Anim", "/Game/Abby_Animation/Posture/Abby_Walking_Anim_Upright"),
                   ("jog", "/Game/Animation2/Jogging", "/Game/Abby_Animation/Posture/Abby_Jogging_Upright"),
                   ("run", "/Game/Animation2/Running__2_", "/Game/Abby_Animation/Posture/Abby_Running__2__Upright")]:
    s, u = anim(src, MX), anim(up, MH)
    print("%-4s Δneck flex: Mixamo %+5.1f  Abby %+5.1f   |  head pitch: Mixamo %+5.1f (Δ%+5.1f)  Abby %+5.1f (Δ%+5.1f)" % (
        g, s[0] - rx[0], u[0] - rh[0], s[1], s[1] - rx[1], u[1], u[1] - rh[1]))

rtg = unreal.load_asset("/Game/Abby_Animation/Posture/RTG_Mixamo_To_Abby_Posture")
c = unreal.IKRetargeterController.get_controller(rtg)
T = unreal.RetargetSourceOrTarget.TARGET
print("Upright pose neck/head offsets:", {b: [round(v, 1) for v in (lambda r: (r.roll, r.pitch, r.yaw))(c.get_rotation_offset_for_retarget_pose_bone(b, T).rotator())] for b in ("spine_05", "neck_01", "neck_02", "head")})
