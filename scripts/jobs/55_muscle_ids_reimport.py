# Job 55: muscle atlas, editor side.
#  1) re-import SKM_Anatomy_Muscles_UpperBody from the FBX whose vertex colours carry the muscle ID (R = id / 255),
#     keeping its skeleton and material slots;
#  2) convert every muscle's sample points (FBX space) to offsets relative to their bone in the mesh's ref pose
#     (UE component space), so the runtime can place them on the animated bones for hover / click picking.
import json
import unreal

EAL = unreal.EditorAssetLibrary
SAVED = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()) + "MetaHumanAnatomyLayers/"
LABELS = "__LABELS__"
MESH = "/MetaHumanAnatomyLayers/Anatomy/Meshes/SKM_Anatomy_Muscles_UpperBody"
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(), "stop PIE first"

mesh = unreal.load_asset(MESH)
skeleton = mesh.skeleton
DEFAULT_MAT = unreal.load_asset("/MetaHumanAnatomyLayers/Anatomy/Materials/M_Anatomy_Muscle")
mats = [(m.material_interface or DEFAULT_MAT, m.material_slot_name) for m in mesh.get_editor_property("materials")]

options = unreal.FbxImportUI()
options.automated_import_should_detect_type = False
options.import_mesh = True
options.import_as_skeletal = True
options.mesh_type_to_import = unreal.FBXImportType.FBXIT_SKELETAL_MESH
options.original_import_type = unreal.FBXImportType.FBXIT_SKELETAL_MESH
options.import_materials = False
options.import_textures = False
options.import_animations = False
options.create_physics_asset = False
options.skeleton = skeleton
options.skeletal_mesh_import_data.set_editor_property("vertex_color_import_option", unreal.VertexColorImportOption.REPLACE)
task = unreal.AssetImportTask()
task.filename = SAVED + "SKM_Anatomy_Muscles_UpperBody_ids.fbx"
task.destination_path = MESH.rsplit("/", 1)[0]
task.destination_name = MESH.rsplit("/", 1)[1]
task.replace_existing = True
task.automated = True
task.save = False
task.options = options
task.factory = unreal.FbxFactory()
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

mesh = unreal.load_asset(MESH)
assert mesh.skeleton == skeleton, "skeleton changed!"
out = []
for i, m in enumerate(mesh.get_editor_property("materials")):
    if i < len(mats):
        m = unreal.SkeletalMaterial(material_interface=mats[i][0], material_slot_name=mats[i][1], uv_channel_data=m.uv_channel_data)
    elif not m.material_interface:  # the re-import can add slots back (the FBX has 2 material sections), empty
        m = unreal.SkeletalMaterial(material_interface=DEFAULT_MAT, material_slot_name=m.material_slot_name, uv_channel_data=m.uv_channel_data)
    out.append(m)
mesh.set_editor_property("materials", out)
print("re-imported", MESH, "skeleton kept:", mesh.skeleton.get_name(), "materials:", [x.material_interface.get_name() for x in out],
      "saved", EAL.save_loaded_asset(mesh, only_if_is_dirty=False))

# ---- samples -> bone-relative offsets in UE space -------------------------------------------------------------
data = json.load(open(LABELS))
mod = unreal.SkeletonModifier()
mod.set_skeletal_mesh(mesh)
ref = {}


def bone_xf(name):
    if name not in ref:
        ref[name] = mod.get_bone_transform(name, True)
    return ref[name]


# axis map FBX -> UE: test the candidates on the bone positions
cands = {"x,-y,z": lambda p: unreal.Vector(p[0], -p[1], p[2]), "x,y,z": lambda p: unreal.Vector(p[0], p[1], p[2]),
         "-x,y,z": lambda p: unreal.Vector(-p[0], p[1], p[2]), "-x,-y,z": lambda p: unreal.Vector(-p[0], -p[1], p[2])}
errs = {}
for key, f in cands.items():
    e = 0.0
    for b in ("pelvis", "head", "hand_l", "hand_r", "clavicle_l", "lowerarm_r"):
        e += (f(data["bones"][b]) - bone_xf(b).translation).length()
    errs[key] = e
best = min(errs, key=errs.get)
print("axis map errors:", {k: round(v, 2) for k, v in errs.items()}, "->", best)
fmap = cands[best]

atlas = {}
for key, items in data["samples"].items():
    pts = []
    for s in items:
        if not s["bone"]:
            continue
        local = bone_xf(s["bone"]).inverse_transform_location(fmap(s["p"]))
        pts.append([s["bone"], round(local.x, 2), round(local.y, 2), round(local.z, 2)])
    atlas[key] = dict(id=data["ids"][key], samples=pts)
json.dump(atlas, open(SAVED + "muscle_atlas_samples.json", "w"))
print("muscles:", len(atlas), "samples:", sum(len(v["samples"]) for v in atlas.values()), "->", SAVED + "muscle_atlas_samples.json")
