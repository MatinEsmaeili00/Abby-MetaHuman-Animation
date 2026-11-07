import unreal
AP = unreal.AnimPoseExtensions
W = unreal.AnimPoseSpaces.WORLD
def measure(path):
    anim = unreal.load_asset(path)
    n = unreal.AnimationLibrary.get_num_frames(anim)
    L = anim.get_play_length()
    opts = unreal.AnimPoseEvaluationOptions()
    rows = []
    for i in range(n):
        t = L * i / max(n - 1, 1)
        pose = AP.get_anim_pose_at_time(anim, t, opts)
        g = lambda b: AP.get_bone_pose(pose, b, W).translation
        sp, cl, cr, hl, hr = g("spine_04"), g("clavicle_l"), g("clavicle_r"), g("hand_l"), g("hand_r")
        # lateral axis = clavicle_r -> clavicle_l direction; 0 = spine centerline, +/-1 = shoulder width/2
        ax = (cl - cr); half = ax.length() / 2; ax = ax / ax.length()
        lat_l = (hl - sp).dot(ax) / half      # left hand should stay > 0
        lat_r = -(hr - sp).dot(ax) / half     # right hand should stay > 0
        fwd_l = (hl - sp); fwd_r = (hr - sp)
        rows.append((lat_l, lat_r))
    mn_l = min(r[0] for r in rows); mn_r = min(r[1] for r in rows)
    cross = sum(1 for r in rows if r[0] < 0.25 or r[1] < 0.25)
    print(f"{path.split('/')[-1]:32s} frames {n:3d}  min lateral L {mn_l:+.2f}  R {mn_r:+.2f}  frames with a hand inside 25% of midline: {cross}/{n}")
for p in ["/Game/Abby_Animation/New/AbbyWalking_Anim", "/Game/Abby_Animation/Fixed/Abby_Walking_Anim_Fixed",
          "/Game/Abby_Animation/New/AbbyJogging", "/Game/Abby_Animation/Fixed/Abby_Jogging_Fixed",
          "/Game/Abby_Animation/New/AbbyRunning__2_", "/Game/Abby_Animation/Fixed/Abby_Running__2__Fixed"]:
    measure(p)
