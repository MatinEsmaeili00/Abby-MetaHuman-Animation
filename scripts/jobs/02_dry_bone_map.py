import sys, importlib, unreal
p = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_plugins_dir()) + "MetaHumanAnatomyLayers/Content/Python"
if p not in sys.path: sys.path.insert(0, p)
import anatomy_layers.build as b; importlib.reload(b)
emil = unreal.load_asset(b.SOURCE_EMIL + "/Meshes/SKM_Emil_upperBodyMuscles")
body = unreal.load_asset(b.DEFAULT_METAHUMAN_BODY)
m = b.compute_bone_map(emil, body)
for k in sorted(m): print(f"{k:24s} -> {m[k]}")
ap = b._global_positions(emil); mp = b._global_positions(body)
for a, mm in [("pelvis","pelvis"),("head","head"),("humerus_l","upperarm_l"),("ulna_l","lowerarm_l"),("hand_l","hand_l"),("femur_l","thigh_l"),("tibia_l","calf_l"),("ankle_l","foot_l"),("ball_l","ball_l")]:
    print(f"{a:10s} emil {ap[a]}   abby {mp[mm]}")
