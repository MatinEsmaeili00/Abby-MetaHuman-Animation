import sys, importlib, unreal
p = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_plugins_dir()) + "MetaHumanAnatomyLayers/Content/Python"
if p not in sys.path: sys.path.insert(0, p)
import anatomy_layers.build as b; importlib.reload(b)
EAL = unreal.EditorAssetLibrary
b.build_all()
ar = unreal.AssetRegistryHelpers.get_asset_registry()
opts = unreal.AssetRegistryDependencyOptions(include_soft_package_references=True, include_hard_package_references=True)
for a in EAL.list_assets("/MetaHumanAnatomyLayers/Anatomy", recursive=True):
    pkg = a.split(".")[0]
    deps = [str(d) for d in (ar.get_dependencies(pkg, opts) or []) if str(d).startswith("/Game")]
    print("GAME-DEPS" if deps else "self-contained", pkg, deps)
for path in b.ANATOMY_MESHES:
    m = unreal.load_asset(path)
    names = [str(n) for n in b._modifier_for(m).get_all_bone_names()]
    print(path.split('/')[-1], len(names), "skeleton", m.skeleton.get_path_name(),
          "MH limb:", [n for n in names if n.endswith("_l") and any(k in n for k in ("upperarm","lowerarm","thigh","calf","foot"))])
    print("   materials:", [(str(sm.material_slot_name), sm.material_interface.get_path_name() if sm.material_interface else None) for sm in m.materials])
