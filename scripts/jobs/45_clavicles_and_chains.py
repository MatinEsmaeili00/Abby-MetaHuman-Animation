# Job 45: clavicle elevation (shoulders up/down) relative to rest, source vs current vs variant B,
# plus the retargeter's chain mapping / FK settings for spine, neck and clavicles.
import math
import unreal

AP = unreal.AnimPoseExtensions
W = unreal.AnimPoseSpaces.WORLD
OPTS = unreal.AnimPoseEvaluationOptions()


def elev(get, cl, ua, nk):
    v = get(ua) - get(cl)
    return math.degrees(math.atan2(v.z, math.hypot(v.x, v.y)))


def anim_elev(path, b):
    a = unreal.load_asset(path)
    n = unreal.AnimationLibrary.get_num_frames(a)
    vals = []
    for i in range(n):
        pose = AP.get_anim_pose_at_time(a, a.get_play_length() * i / max(n - 1, 1), OPTS)
        g = lambda x: AP.get_bone_pose(pose, x, W).translation
        vals.append((elev(g, b[0], b[1], b[4]) + elev(g, b[2], b[3], b[4])) / 2)
    return sum(vals) / len(vals)


def rest_elev(mesh, b):
    m = unreal.SkeletonModifier()
    m.set_skeletal_mesh(unreal.load_asset(mesh))
    g = lambda x: m.get_bone_transform(x, True).translation
    return (elev(g, b[0], b[1], b[4]) + elev(g, b[2], b[3], b[4])) / 2


MH = ("clavicle_l", "upperarm_l", "clavicle_r", "upperarm_r", "neck_01")
MX = ("LeftShoulder", "LeftArm", "RightShoulder", "RightArm", "Neck")
rmx = rest_elev("/Game/Animation2/Walking", MX)
rmh = rest_elev("/Game/MetaHumans/MH_CH_Abby5/Body/SKM_MH_CH_Abby5_BodyMesh", MH)
print("clavicle elevation at rest: Mixamo %+.1f°, Abby %+.1f° (change from rest below; - = shoulders lower)" % (rmx, rmh))
for g, src, cur, b in [("Walking_Anim", "/Game/Animation2/Walking_Anim", "/Game/Abby_Animation/Enhanced/AbbyWalk_Sync", "/Game/Abby_Animation/Posture/Abby_Walking_Anim_B"),
                       ("Jogging", "/Game/Animation2/Jogging", "/Game/Abby_Animation/Enhanced/AbbyJog_Sync", "/Game/Abby_Animation/Posture/Abby_Jogging_B"),
                       ("Running__2_", "/Game/Animation2/Running__2_", "/Game/Abby_Animation/Enhanced/AbbyRun_Sync", "/Game/Abby_Animation/Posture/Abby_Running__2__B")]:
    print("%-13s Mixamo %+5.1f°  Abby now %+5.1f°  variant B %+5.1f°" % (g, anim_elev(src, MX) - rmx, anim_elev(cur, MH) - rmh, anim_elev(b, MH) - rmh))

rtg = unreal.load_asset("/Game/Abby_Animation/Posture/RTG_Mixamo_To_Abby_Posture")
c = unreal.IKRetargeterController.get_controller(rtg)
for chain in ["Spine", "Neck", "Head", "LeftClavicle", "RightClavicle"]:
    try:
        print(chain, "<-", c.get_source_chain(chain))
    except Exception as e:
        print(chain, "n/a", e)
try:
    for s in c.get_all_chain_settings():
        print(" ", s)
except Exception as e:
    print("chain settings n/a:", e)
