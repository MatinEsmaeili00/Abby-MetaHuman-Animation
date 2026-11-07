# Job 51: run-only retarget pose candidates (on top of "Upright"): stronger neck extension and a slightly more upright
# chest, to bring the running head/neck carriage back to the source's. Prints trunk lean, neck flex, head pitch.
import math
import unreal

EAL = unreal.EditorAssetLibrary
DIR = "/Game/Abby_Animation/Posture"
T = unreal.RetargetSourceOrTarget.TARGET
AP = unreal.AnimPoseExtensions
W = unreal.AnimPoseSpaces.WORLD
OPTS = unreal.AnimPoseEvaluationOptions()
UP = unreal.Vector(0, 0, 1)
CANDIDATES = {
    "c1": {"neck_01": -6.0, "neck_02": -4.0},
    "c2": {"neck_01": -6.0, "neck_02": -4.0, "spine_04": -3.0},
    "c3": {"neck_01": -8.0, "neck_02": -5.0, "spine_04": -3.0, "spine_05": -2.0},
}


def measure(path):
    a = unreal.load_asset(path)
    n = unreal.AnimationLibrary.get_num_frames(a)
    acc = [0.0, 0.0, 0.0]
    for i in range(n):
        p = AP.get_anim_pose_at_time(a, a.get_play_length() * i / max(n - 1, 1), OPTS)
        g = lambda x: AP.get_bone_pose(p, x, W).translation
        lat = (g("upperarm_l") - g("upperarm_r")).normal()
        fwd = UP.cross(lat).normal()
        if fwd.dot(g("ball_l") - g("foot_l")) < 0:
            fwd = fwd * -1.0
        ang = lambda v: math.degrees(math.atan2(v.dot(fwd), v.dot(UP)))
        lean = ang(g("neck_01") - g("pelvis"))
        back = ang(g("neck_01") - g("spine_04"))
        neck = ang(g("head") - g("neck_01"))
        acc[0] += lean / n
        acc[1] += (neck - back) / n
        acc[2] += neck / n
    return acc


rtg = unreal.load_asset(DIR + "/RTG_Mixamo_To_Abby_Posture")
c = unreal.IKRetargeterController.get_controller(rtg)
print("source run: lean +2.2, head pitch +1.5 | Upright+neck now:", ["%+.1f" % v for v in measure(DIR + "/Abby_Running__2__Posture")])
for key, offs in CANDIDATES.items():
    pose = "RunTest_" + key
    if pose not in [str(p) for p in c.get_retarget_poses(T)]:
        c.duplicate_retarget_pose("Upright", pose, T)
    c.set_current_retarget_pose(pose, T)
    for bone, yaw in offs.items():
        c.set_rotation_offset_for_retarget_pose_bone(bone, unreal.Rotator(yaw=yaw).quaternion(), T)
    inputs = unreal.IKRetargetBatchOperationInputs()
    inputs.assets_to_retarget = [EAL.find_asset_data("/Game/Animation2/Running__2_")]
    inputs.source_mesh = unreal.load_asset("/Game/Animation2/Walking")
    inputs.target_mesh = unreal.load_asset("/Game/MetaHumans/MH_CH_Abby5/Body/SKM_MH_CH_Abby5_BodyMesh")
    inputs.ik_retarget_asset = rtg
    inputs.target_path = DIR + "/RunTest"
    inputs.use_source_path = False
    inputs.prefix = "T_"
    inputs.suffix = "_" + key
    inputs.include_referenced_assets = False
    inputs.overwrite_existing_files = True
    path = str(unreal.IKRetargetBatchOperation.run_batch_retarget(inputs)[0].package_name)
    print(key, offs, "-> lean %+.1f  neck flex vs chest %+.1f  head pitch %+.1f" % tuple(measure(path)))
c.set_current_retarget_pose("Upright", T)
EAL.save_loaded_asset(rtg, only_if_is_dirty=False)
