import unreal
AP = unreal.AnimPoseExtensions; W = unreal.AnimPoseSpaces.WORLD
opts = unreal.AnimPoseEvaluationOptions()
def stats(path, b):  # b: bone names dict
    anim = unreal.load_asset(path); n = unreal.AnimationLibrary.get_num_frames(anim); L = anim.get_play_length()
    lat, fwd, footz, ballz, pelz = [], [], [], [], []
    for i in range(n):
        pose = AP.get_anim_pose_at_time(anim, L * i / max(n - 1, 1), opts)
        g = lambda x: AP.get_bone_pose(pose, b[x], W).translation
        ul, ur, hl, hr, sp = g("ua_l"), g("ua_r"), g("hand_l"), g("hand_r"), g("spine")
        ax = ul - ur; w = ax.length(); ax = ax / w
        lat += [(hl - sp).dot(ax) / (w / 2), -(hr - sp).dot(ax) / (w / 2)]
        footz += [g("foot_l").z, g("foot_r").z]; ballz += [g("ball_l").z, g("ball_r").z]; pelz.append(g("pelvis").z)
    sc = 1.0
    print(f"{path.split('/')[-1]:30s} hands lateral (1 = shoulder): min {min(lat):+.2f} mean {sum(lat)/len(lat):+.2f} | "
          f"foot z min {min(footz):6.1f} | ball z min {min(ballz):6.1f} max {max(ballz):6.1f} | pelvis z {min(pelz):6.1f}..{max(pelz):6.1f}")
MH = dict(ua_l="upperarm_l", ua_r="upperarm_r", hand_l="hand_l", hand_r="hand_r", spine="spine_04", foot_l="foot_l", foot_r="foot_r", ball_l="ball_l", ball_r="ball_r", pelvis="pelvis")
MX = dict(ua_l="LeftArm", ua_r="RightArm", hand_l="LeftHand", hand_r="RightHand", spine="Spine2", foot_l="LeftFoot", foot_r="RightFoot", ball_l="LeftToeBase", ball_r="RightToeBase", pelvis="Hips")
for src, old, fix in [("/Game/Animation2/Walking_Anim", "/Game/Abby_Animation/New/AbbyWalking_Anim", "/Game/Abby_Animation/Fixed/Abby_Walking_Anim_Fixed"),
                      ("/Game/Animation2/Jogging", "/Game/Abby_Animation/New/AbbyJogging", "/Game/Abby_Animation/Fixed/Abby_Jogging_Fixed"),
                      ("/Game/Animation2/Running__2_", "/Game/Abby_Animation/New/AbbyRunning__2_", "/Game/Abby_Animation/Fixed/Abby_Running__2__Fixed")]:
    stats(src, MX); stats(old, MH); stats(fix, MH); print()
m = unreal.SkeletonModifier(); m.set_skeletal_mesh(unreal.load_asset("/Game/MetaHumans/MH_CH_Abby5/Body/SKM_MH_CH_Abby5_BodyMesh"))
print("Abby ref: ball_l z", round(m.get_bone_transform("ball_l", True).translation.z, 2), "foot_l z", round(m.get_bone_transform("foot_l", True).translation.z, 2))
m.set_skeletal_mesh(unreal.load_asset("/Game/Animation2/Walking"))
print("Mixamo ref: toe z", round(m.get_bone_transform("LeftToeBase", True).translation.z, 2), "foot z", round(m.get_bone_transform("LeftFoot", True).translation.z, 2))
