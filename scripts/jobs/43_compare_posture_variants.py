# Job 43: compare posture of the Mixamo source, the current Abby clips (_Sync) and the two upright-spine variants.
# Posture numbers are reported as change from each skeleton's own rest pose (so a naturally curved MetaHuman spine
# and a straight Mixamo spine are compared fairly). Also checks legs (stride, toe height) and arms didn't change.
import math
import unreal

AP = unreal.AnimPoseExtensions
W = unreal.AnimPoseSpaces.WORLD
OPTS = unreal.AnimPoseEvaluationOptions()
UP = unreal.Vector(0, 0, 1)
MH = dict(pelvis="pelvis", mid="spine_03", neck="neck_01", head="head", ua_l="upperarm_l", ua_r="upperarm_r",
          foot_l="foot_l", foot_r="foot_r", ball_l="ball_l", ball_r="ball_r", hand_l="hand_l", hand_r="hand_r", thigh_l="thigh_l")
MX = dict(pelvis="Hips", mid="Spine1", neck="Neck", head="Head", ua_l="LeftArm", ua_r="RightArm",
          foot_l="LeftFoot", foot_r="RightFoot", ball_l="LeftToeBase", ball_r="RightToeBase", hand_l="LeftHand", hand_r="RightHand", thigh_l="LeftUpLeg")


def frame(get, b):
    p, m, n, h = get(b["pelvis"]), get(b["mid"]), get(b["neck"]), get(b["head"])
    ul, ur = get(b["ua_l"]), get(b["ua_r"])
    lat = (ul - ur).normal()
    fwd = UP.cross(lat).normal()
    if fwd.dot(h - n) + fwd.dot(get(b["ball_l"]) - get(b["foot_l"])) < 0:
        fwd = fwd * -1.0
    L = (n - p).length()
    lean = math.degrees(math.atan2((n - p).dot(fwd), (n - p).dot(UP)))
    a1 = math.degrees(math.atan2((m - p).dot(fwd), (m - p).dot(UP)))
    a2 = math.degrees(math.atan2((n - m).dot(fwd), (n - m).dot(UP)))
    bend = a2 - a1                                  # + = upper back rounded forward relative to lower back
    sh = (ul + ur) * 0.5
    drop = (n.z - sh.z) / L
    head_fwd = (h - n).dot(fwd) / L
    leg = (get(b["thigh_l"]) - get(b["foot_l"])).length() or 1.0
    reach = [(get(b[k]) - p).dot(fwd) / leg for k in ("foot_l", "foot_r")]
    ball = min(get(b["ball_l"]).z, get(b["ball_r"]).z)
    hands = [(get(b["hand_l"]) - p).dot(fwd) / L, (get(b["hand_r"]) - p).dot(fwd) / L]
    return dict(lean=lean, bend=bend, drop=drop, head=head_fwd, reach=reach, ball=ball, hands=hands)


def rest(mesh, b):
    mod = unreal.SkeletonModifier()
    mod.set_skeletal_mesh(unreal.load_asset(mesh))
    return frame(lambda x: mod.get_bone_transform(x, True).translation, b)


def anim(path, b):
    a = unreal.load_asset(path)
    n = unreal.AnimationLibrary.get_num_frames(a)
    L = a.get_play_length()
    rows = [frame(lambda x, pose=AP.get_anim_pose_at_time(a, L * i / max(n - 1, 1), OPTS): AP.get_bone_pose(pose, x, W).translation, b)
            for i in range(n)]
    avg = lambda k: sum(r[k] for r in rows) / len(rows)
    reach = [v for r in rows for v in r["reach"]]
    hands = [v for r in rows for v in r["hands"]]
    return dict(lean=avg("lean"), bend=avg("bend"), drop=avg("drop"), head=avg("head"),
                stride=max(reach) - min(reach), ball=min(r["ball"] for r in rows), hands=max(hands) - min(hands))


R_MX = rest("/Game/Animation2/Walking", MX)
R_MH = rest("/Game/MetaHumans/MH_CH_Abby5/Body/SKM_MH_CH_Abby5_BodyMesh", MH)
print("rest  Mixamo: lean %+.1f bend %+.1f drop %.3f | Abby: lean %+.1f bend %+.1f drop %.3f" % (
    R_MX["lean"], R_MX["bend"], R_MX["drop"], R_MH["lean"], R_MH["bend"], R_MH["drop"]))
print("%-22s %8s %10s %10s %9s %8s %9s %8s" % ("clip", "lean", "Δbend", "Δdrop", "head fwd", "stride", "toe min", "arm swing"))
for gait, src, cur in [("Walking_Anim", "/Game/Animation2/Walking_Anim", "/Game/Abby_Animation/Enhanced/AbbyWalk_Sync"),
                       ("Jogging", "/Game/Animation2/Jogging", "/Game/Abby_Animation/Enhanced/AbbyJog_Sync"),
                       ("Running__2_", "/Game/Animation2/Running__2_", "/Game/Abby_Animation/Enhanced/AbbyRun_Sync")]:
    rows = [("Mixamo " + gait, anim(src, MX), R_MX), ("Abby now", anim(cur, MH), R_MH)]
    for k in ("A", "B"):
        rows.append(("Abby variant " + k, anim(f"/Game/Abby_Animation/Posture/Abby_{gait}_{k}", MH), R_MH))
    for name, s, r in rows:
        print("%-22s %+7.1f° %+9.1f° %+10.3f %+9.3f %8.2f %8.1fcm %9.2f" % (
            name, s["lean"], s["bend"] - r["bend"], s["drop"] - r["drop"], s["head"], s["stride"], s["ball"], s["hands"]))
    print()
