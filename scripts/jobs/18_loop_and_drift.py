import unreal, math
AP = unreal.AnimPoseExtensions; W = unreal.AnimPoseSpaces.WORLD; LOC = unreal.AnimPoseSpaces.LOCAL
opts = unreal.AnimPoseEvaluationOptions()
def check(path, pelvis, bones):
    anim = unreal.load_asset(path); n = unreal.AnimationLibrary.get_num_frames(anim); L = anim.get_play_length()
    p0 = AP.get_anim_pose_at_frame(anim, 0, opts); pN = AP.get_anim_pose_at_frame(anim, n - 1, opts); p1 = AP.get_anim_pose_at_frame(anim, 1, opts)
    def rotdiff(a, b):
        tot = 0
        for bn in bones:
            qa = AP.get_bone_pose(a, bn, LOC).rotation; qb = AP.get_bone_pose(b, bn, LOC).rotation
            d = abs(qa.x*qb.x + qa.y*qb.y + qa.z*qb.z + qa.w*qb.w); tot += math.degrees(2 * math.acos(min(1.0, d)))
        return tot / len(bones)
    pel0 = AP.get_bone_pose(p0, pelvis, W).translation; pelN = AP.get_bone_pose(pN, pelvis, W).translation
    ys = [AP.get_bone_pose(AP.get_anim_pose_at_frame(anim, i, opts), pelvis, W).translation for i in range(n)]
    span = max(v.y for v in ys) - min(v.y for v in ys); spanx = max(v.x for v in ys) - min(v.x for v in ys)
    print(f"{path.split('/')[-1]:28s} frames {n:3d} len {L:.3f}s | first-vs-last avg bone diff {rotdiff(p0, pN):5.2f} deg, frame0-vs-1 {rotdiff(p0, p1):5.2f} deg"
          f" | pelvis drift first->last ({pelN.x-pel0.x:+.1f},{pelN.y-pel0.y:+.1f}) span y {span:.1f} x {spanx:.1f}")
MHB = ["pelvis","spine_03","upperarm_l","upperarm_r","lowerarm_l","lowerarm_r","thigh_l","thigh_r","calf_l","calf_r","foot_l","foot_r"]
MXB = ["Hips","Spine1","LeftArm","RightArm","LeftForeArm","RightForeArm","LeftUpLeg","RightUpLeg","LeftLeg","RightLeg","LeftFoot","RightFoot"]
for p in ["/Game/Animation2/Walking_Anim","/Game/Animation2/Jogging","/Game/Animation2/Running__2_"]: check(p, "Hips", MXB)
for p in ["/Game/Abby_Animation/New/AbbyWalking_Anim","/Game/Abby_Animation/New/AbbyJogging","/Game/Abby_Animation/New/AbbyRunning__2_","/Game/Abby_Animation/New2/Jogging_InTime"]: check(p, "pelvis", MHB)
