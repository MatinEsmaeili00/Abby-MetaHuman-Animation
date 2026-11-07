# Job 41: posture of the Mixamo source vs Abby's retargeted walk / jog / run (and both rest poses).
# Trunk lean = angle of pelvis->neck from vertical in the walking direction (+ = leaning forward).
# Upper-back bend = angle between pelvis->mid-spine and mid-spine->neck (+ = rounded forward).
# Shoulder drop = how far the upper arms sit below the neck base, as a fraction of torso length.
# Shoulder / head forward = how far in front of the pelvis->neck line they sit, as a fraction of torso length.
import math
import unreal

AP = unreal.AnimPoseExtensions
W = unreal.AnimPoseSpaces.WORLD
OPTS = unreal.AnimPoseEvaluationOptions()

MH = dict(pelvis="pelvis", mid="spine_03", neck="neck_01", head="head", ua_l="upperarm_l", ua_r="upperarm_r", cl_l="clavicle_l", cl_r="clavicle_r")
MX = dict(pelvis="Hips", mid="Spine1", neck="Neck", head="Head", ua_l="LeftArm", ua_r="RightArm", cl_l="LeftShoulder", cl_r="RightShoulder")
UP = unreal.Vector(0, 0, 1)


def ang(a, b):
    return math.degrees(math.acos(max(-1.0, min(1.0, a.normal().dot(b.normal())))))


def measure(get, b):
    p, m, n, h = get(b["pelvis"]), get(b["mid"]), get(b["neck"]), get(b["head"])
    ul, ur = get(b["ua_l"]), get(b["ua_r"])
    lat = (ul - ur).normal()
    fwd = UP.cross(lat).normal()          # walking direction (perpendicular to shoulders, horizontal)
    if fwd.dot((h - n)) < 0 and fwd.dot(m - p) < 0:
        fwd = fwd * -1.0
    trunk = n - p
    L = trunk.length()
    lean = math.degrees(math.atan2(trunk.dot(fwd), trunk.dot(UP)))
    bend = ang(m - p, n - m) * (1 if (n - m).dot(fwd) > (m - p).normal().dot(fwd) * (n - m).length() else -1)
    sh = (ul + ur) * 0.5
    drop = (n.z - sh.z) / L
    sh_fwd = (sh - p).dot(fwd) / L - (n - p).dot(fwd) / L
    head_fwd = (h - n).dot(fwd) / L
    return lean, bend, drop, sh_fwd, head_fwd


def anim_stats(path, b):
    anim = unreal.load_asset(path)
    n = unreal.AnimationLibrary.get_num_frames(anim)
    length = anim.get_play_length()
    rows = []
    for i in range(n):
        pose = AP.get_anim_pose_at_time(anim, length * i / max(n - 1, 1), OPTS)
        rows.append(measure(lambda x: AP.get_bone_pose(pose, x, W).translation, b))
    avg = [sum(r[k] for r in rows) / len(rows) for k in range(5)]
    return avg


def ref_stats(mesh_path, b):
    mod = unreal.SkeletonModifier()
    mod.set_skeletal_mesh(unreal.load_asset(mesh_path))
    return measure(lambda x: mod.get_bone_transform(x, True).translation, b)


def fmt(name, v):
    return "%-28s lean %+6.1f°  upper-back bend %+6.1f°  shoulder drop %.3f  shoulders fwd %+.3f  head fwd %+.3f" % (name, *v)


print(fmt("REST Mixamo", ref_stats("/Game/Animation2/Walking", MX)))
print(fmt("REST Abby", ref_stats("/Game/MetaHumans/MH_CH_Abby5/Body/SKM_MH_CH_Abby5_BodyMesh", MH)))
for src, dst in [("/Game/Animation2/Walking_Anim", "/Game/Abby_Animation/Enhanced/AbbyWalk_Sync"),
                 ("/Game/Animation2/Jogging", "/Game/Abby_Animation/Enhanced/AbbyJog_Sync"),
                 ("/Game/Animation2/Running__2_", "/Game/Abby_Animation/Enhanced/AbbyRun_Sync")]:
    print(fmt("Mixamo " + src.split("/")[-1], anim_stats(src, MX)))
    print(fmt("Abby   " + dst.split("/")[-1], anim_stats(dst, MH)))
