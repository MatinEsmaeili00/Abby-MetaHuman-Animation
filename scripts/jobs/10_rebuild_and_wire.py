import os, stat, sys, importlib, unreal
p = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_plugins_dir()) + "MetaHumanAnatomyLayers/Content/Python"
if p not in sys.path: sys.path.insert(0, p)
import anatomy_layers.build as b; importlib.reload(b)
b.build_all()
for path in b.ANATOMY_MESHES:
    m = unreal.load_asset(path)
    print(path.split('/')[-1], "skeleton", m.skeleton.get_path_name(),
          "on disk:", unreal.EditorAssetLibrary.does_asset_exist(m.skeleton.get_path_name().split('.')[0]))
BP = "/Game/MetaHumans/MH_CH_Abby5/BP_MH_CH_Abby8"
f = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_content_dir()) + "MetaHumans/MH_CH_Abby5/BP_MH_CH_Abby8.uasset"
if not os.access(f, os.W_OK):
    os.chmod(f, os.stat(f).st_mode | stat.S_IWUSR)
b.wire_blueprint(BP)
print("done")
