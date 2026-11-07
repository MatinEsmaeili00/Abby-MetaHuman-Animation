# Job 46: which retarget-pose rotation axis raises each clavicle? Retarget the run with +5 deg on one axis at a
# time (on top of the UprightSpine_B pose) and measure each side's clavicle elevation change.
import math
import unreal

EAL = unreal.EditorAssetLibrary
DIR = "/Game/Abby_Animation/Posture"
T = unreal.RetargetSourceOrTarget.TARGET
rtg = unreal.load_asset(DIR + "/RTG_Mixamo_To_Abby_Posture")
c = unreal.IKRetargeterController.get_controller(rtg)
AP = unreal.AnimPoseExtensions
W = unreal.AnimPoseSpaces.WORLD
OPTS = unreal.AnimPoseEvaluationOptions()


def side_elev(path):
    a = unreal.load_asset(path)
    n = unreal.AnimationLibrary.get_num_frames(a)
    out = [0.0, 0.0]
    for i in range(n):
        pose = AP.get_anim_pose_at_time(a, a.get_play_length() * i / max(n - 1, 1), OPTS)
        g = lambda x: AP.get_bone_pose(pose, x, W).translation
        for k, (cl, ua) in enumerate((("clavicle_l", "upperarm_l"), ("clavicle_r", "upperarm_r"))):
            v = g(ua) - g(cl)
            out[k] += math.degrees(math.atan2(v.z, math.hypot(v.x, v.y))) / n
    return out


def retarget(suffix):
    inputs = unreal.IKRetargetBatchOperationInputs()
    inputs.assets_to_retarget = [EAL.find_asset_data("/Game/Animation2/Running__2_")]
    inputs.source_mesh = unreal.load_asset("/Game/Animation2/Walking")
    inputs.target_mesh = unreal.load_asset("/Game/MetaHumans/MH_CH_Abby5/Body/SKM_MH_CH_Abby5_BodyMesh")
    inputs.ik_retarget_asset = rtg
    inputs.target_path = DIR + "/AxisTest"
    inputs.use_source_path = False
    inputs.prefix = "T_"
    inputs.suffix = "_" + suffix
    inputs.include_referenced_assets = False
    inputs.overwrite_existing_files = True
    out = unreal.IKRetargetBatchOperation.run_batch_retarget(inputs)
    return str(out[0].package_name)


base = side_elev(DIR + "/Abby_Running__2__B")
print("B: elevation L %+.2f R %+.2f" % tuple(base))
if "AxisTest" not in [str(p) for p in c.get_retarget_poses(T)]:
    c.duplicate_retarget_pose("UprightSpine_B", "AxisTest", T)
c.set_current_retarget_pose("AxisTest", T)
for axis in ("roll", "pitch", "yaw"):
    for b in ("clavicle_l", "clavicle_r"):
        c.set_rotation_offset_for_retarget_pose_bone(b, unreal.Rotator(**{axis: 5.0}).quaternion(), T)
    e = side_elev(retarget(axis))
    print("%-5s +5: L %+.2f R %+.2f  (change L %+.2f R %+.2f)" % (axis, e[0], e[1], e[0] - base[0], e[1] - base[1]))
for b in ("clavicle_l", "clavicle_r"):
    c.set_rotation_offset_for_retarget_pose_bone(b, unreal.Quat(), T)
c.set_current_retarget_pose("UprightSpine_B", T)
EAL.save_loaded_asset(rtg, only_if_is_dirty=False)
