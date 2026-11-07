# Job 56: create the DA_MuscleAtlas_UpperBody data asset (UMuscleAtlas) from the labelled samples + the info text.
import json
import unreal

EAL = unreal.EditorAssetLibrary
TOOLS = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_plugins_dir()) + "MetaHumanAnatomyLayers/Tools/muscle_atlas/"
PATH = "/MetaHumanAnatomyLayers/Anatomy/Data/DA_MuscleAtlas_UpperBody"
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(), "stop PIE first"

samples = json.load(open(TOOLS + "muscle_atlas_samples.json"))
info = json.load(open(TOOLS + "muscle_info.json"))

if EAL.does_asset_exist(PATH):
    atlas = unreal.load_asset(PATH)
else:
    f = unreal.DataAssetFactory()
    f.set_editor_property("data_asset_class", unreal.MuscleAtlas)
    folder, name = PATH.rsplit("/", 1)
    atlas = unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, folder, unreal.MuscleAtlas, f)

muscles = []
for key in sorted(samples, key=lambda k: samples[k]["id"]):
    base, side = key.rsplit("_", 1)
    text = info[base]
    m = unreal.MuscleInfo()
    m.set_editor_property("id", samples[key]["id"])
    m.set_editor_property("key", key)
    m.set_editor_property("name", text["name"])
    m.set_editor_property("side", "Left" if side == "l" else "Right")
    m.set_editor_property("region", text["region"])
    m.set_editor_property("function", text["function"])
    m.set_editor_property("running", text["running"])
    m.set_editor_property("injury", text["injury"])
    m.set_editor_property("samples", [unreal.MuscleSample(bone=b, offset=unreal.Vector(x, y, z)) for b, x, y, z in samples[key]["samples"]])
    muscles.append(m)
atlas.set_editor_property("muscles", muscles)
print("atlas:", atlas.get_path_name(), "muscles:", len(muscles), "samples:", sum(len(m.samples) for m in muscles),
      "saved", EAL.save_loaded_asset(atlas, only_if_is_dirty=False))
print([(m.id, str(m.name), str(m.side)) for m in muscles][:6])
