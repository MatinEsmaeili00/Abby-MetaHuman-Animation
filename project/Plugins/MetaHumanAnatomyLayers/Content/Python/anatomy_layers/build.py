"""Build anatomy layers (muscles / skeleton) that follow a MetaHuman body through Leader Pose.

Anatomy meshes such as the Chaos Flesh "Emil" example use anatomical limb bone names (humerus, ulna,
femur, tibia, ankle). Leader Pose matches bones *by name*, so this module:

1. copies the anatomy materials and textures into this plugin and re-points them at each other;
2. round-trips the anatomy meshes through FBX into this plugin with their **own new skeleton**,
   so nothing references /Game content (the plugin can be dropped into any project);
3. renames the limb bones to MetaHuman names. Twist bones are paired with MetaHuman twist bones by
   their measured position along the limb, not by guessing from names;
4. optionally wires the layers into a MetaHuman Blueprint (child of Body, Leader Pose = Body).

Run inside the Unreal Editor (Python):
    from anatomy_layers import build
    build.build_all()
    build.wire_blueprint("/Game/MetaHumans/MH_CH_Abby5/BP_MH_CH_Abby8")
"""
import os

import unreal

PLUGIN_MOUNT = "/MetaHumanAnatomyLayers"
DEST_DIR = PLUGIN_MOUNT + "/Anatomy"
MESH_DIR = DEST_DIR + "/Meshes"

SOURCE_EMIL = "/Game/ExampleContent/5_5_ChaosFlesh/Characters/Emil"
# Materials / textures: plain duplicates, re-pointed at each other afterwards.
MATERIAL_COPIES = {
    SOURCE_EMIL + "/Materials/M_Emil_MSS_Msl_Top1": DEST_DIR + "/Materials/M_Anatomy_Muscle",
    SOURCE_EMIL + "/Materials/M_blockColour1": DEST_DIR + "/Materials/M_Anatomy_BlockColour",
    SOURCE_EMIL + "/Materials/Mi_bone1": DEST_DIR + "/Materials/MI_Anatomy_Bone",
    SOURCE_EMIL + "/Textures/T_Emil_MSS_Muscle_Top_Mask1": DEST_DIR + "/Textures/T_Anatomy_Muscle_Mask",
    SOURCE_EMIL + "/Textures/T_cylinder_depth1": DEST_DIR + "/Textures/T_Anatomy_CylinderDepth",
}
# Meshes: (source mesh, new asset name). The first one creates the shared skeleton.
MESH_SOURCES = [
    (SOURCE_EMIL + "/Meshes/SKM_Emil_upperBodyMuscles", "SKM_Anatomy_Muscles_UpperBody"),
    (SOURCE_EMIL + "/Meshes/SKM_skeleton_upper_body", "SKM_Anatomy_Skeleton_UpperBody"),
]
ANATOMY_MESHES = [f"{MESH_DIR}/{name}" for _, name in MESH_SOURCES]
DEFAULT_METAHUMAN_BODY = "/Game/MetaHumans/MH_CH_Abby5/Body/SKM_MH_CH_Abby5_BodyMesh"

# Anatomy limb bone -> MetaHuman bone ({s} = l / r)
CORE_MAP = {
    "humerus_{s}": "upperarm_{s}",
    "ulna_{s}": "lowerarm_{s}",
    "femur_{s}": "thigh_{s}",
    "tibia_{s}": "calf_{s}",
    "ankle_{s}": "foot_{s}",
}
# Twist groups: (anatomy parent, anatomy child, anatomy twists, MH parent, MH child, MH twists)
TWIST_GROUPS = [
    ("humerus_{s}", "ulna_{s}", ["humerus_{s}_twist_01", "humerus_{s}_twist_02"],
     "upperarm_{s}", "lowerarm_{s}", ["upperarm_twist_01_{s}", "upperarm_twist_02_{s}"]),
    ("ulna_{s}", "hand_{s}", ["ulna_{s}_twist_00", "ulna_{s}_twist_01", "ulna_{s}_twist_02"],
     "lowerarm_{s}", "hand_{s}", ["lowerarm_twist_01_{s}", "lowerarm_twist_02_{s}"]),
    ("femur_{s}", "tibia_{s}", ["femur_twist_01_{s}", "femur_twist_02_{s}"],
     "thigh_{s}", "calf_{s}", ["thigh_twist_01_{s}", "thigh_twist_02_{s}"]),
]

EAL = unreal.EditorAssetLibrary


def _obj_path(package_path):
    return f"{package_path}.{package_path.rsplit('/', 1)[-1]}"


def _temp_dir():
    d = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()),
                     "MetaHumanAnatomyLayers")
    os.makedirs(d, exist_ok=True)
    return d


# ------------------------------------------------------------------------------------- materials
def copy_materials(copies=None, overwrite=False):
    """Duplicate materials/textures into the plugin and re-point references between the copies."""
    copies = copies or MATERIAL_COPIES
    for src, dst in copies.items():
        if EAL.does_asset_exist(dst):
            if not overwrite:
                continue
            EAL.delete_asset(dst)
        if not EAL.duplicate_asset(src, dst):
            raise RuntimeError(f"duplicate failed: {src} -> {dst}")
        print(f"copied {src} -> {dst}")
    remap = {_obj_path(s): unreal.load_asset(d) for s, d in copies.items()}

    def mapped(obj):
        return remap.get(obj.get_path_name()) if obj else None

    for dst in copies.values():
        asset = unreal.load_asset(dst)
        if isinstance(asset, unreal.MaterialInstanceConstant):
            parent = mapped(asset.get_editor_property("parent"))
            if parent:
                unreal.MaterialEditingLibrary.set_material_instance_parent(asset, parent)
            for tp in asset.get_editor_property("texture_parameter_values"):
                new = mapped(tp.parameter_value)
                if new:
                    unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(
                        asset, tp.parameter_info.name, new)
            unreal.MaterialEditingLibrary.update_material_instance(asset)
        elif isinstance(asset, unreal.Material):
            _repoint_material_textures(asset, mapped)
        EAL.save_loaded_asset(asset, only_if_is_dirty=False)
    return mapped


def _repoint_material_textures(material, mapped):
    mel = unreal.MaterialEditingLibrary
    changed = False
    for node in mel.get_material_expressions(material) or []:
        if isinstance(node, unreal.MaterialExpressionTextureBase):
            new = mapped(node.get_editor_property("texture"))
            if new:
                node.set_editor_property("texture", new)
                changed = True
    if changed:
        mel.recompile_material(material)
    print(f"material {material.get_name()}: textures {[t.get_name() for t in mel.get_used_textures(material)]}")


# ---------------------------------------------------------------------------------- mesh import
def export_fbx(mesh, filename, ascii=True):
    task = unreal.AssetExportTask()
    task.object = mesh
    task.filename = filename
    task.automated = True
    task.prompt = False
    task.replace_identical = True
    task.exporter = unreal.SkeletalMeshExporterFBX()
    opts = unreal.FbxExportOption()
    opts.set_editor_property("ascii", ascii)
    task.options = opts
    if not unreal.Exporter.run_asset_export_task(task):
        raise RuntimeError(f"FBX export failed for {mesh.get_path_name()}")
    return filename


def rename_bones_in_ascii_fbx(src_file, dst_file, bone_map):
    """Rename FBX nodes ("Model::x", "NodeAttribute::x", "SubDeformer::x", ...) in an ASCII FBX file.

    Renaming before import means the new Skeleton asset is created with MetaHuman names from the start.
    Editing names afterwards would need a skeleton merge, which Unreal only allows interactively.
    """
    import re
    with open(src_file, "r", encoding="utf-8", errors="surrogateescape") as f:
        text = f.read()
    if not text.lstrip().startswith(";"):
        raise RuntimeError(f"{src_file} is not an ASCII FBX")
    counts = {}

    def repl(m):
        old = m.group(2)
        new = bone_map.get(old)
        if new is None:
            return m.group(0)
        counts[old] = counts.get(old, 0) + 1
        return f"{m.group(1)}{new}{m.group(3)}"

    text = re.sub(r'(::)([A-Za-z0-9_]+)(")', repl, text)
    missing = [n for n in bone_map if n not in counts]
    with open(dst_file, "w", encoding="utf-8", errors="surrogateescape") as f:
        f.write(text)
    print(f"renamed {len(counts)} bones in {os.path.basename(dst_file)}" + (f" (not found: {missing})" if missing else ""))
    return counts


def import_fbx(filename, folder, name, skeleton=None):
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
    if skeleton is not None:
        options.skeleton = skeleton
    task = unreal.AssetImportTask()
    task.filename = filename
    task.destination_path = folder
    task.destination_name = name
    task.replace_existing = True
    task.automated = True
    task.save = True
    task.options = options
    task.factory = unreal.FbxFactory()
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    mesh = unreal.load_asset(f"{folder}/{name}")
    if not isinstance(mesh, unreal.SkeletalMesh):
        raise RuntimeError(f"import failed: {filename} -> {folder}/{name}")
    return mesh


def import_meshes(material_map, bone_map, overwrite=False):
    skeleton = None
    meshes = []
    for src_path, name in MESH_SOURCES:
        dst = f"{MESH_DIR}/{name}"
        if EAL.does_asset_exist(dst) and not overwrite:
            mesh = unreal.load_asset(dst)
        else:
            src = unreal.load_asset(src_path)
            raw = export_fbx(src, os.path.join(_temp_dir(), name + "_source.fbx"))
            fbx = os.path.join(_temp_dir(), name + ".fbx")
            rename_bones_in_ascii_fbx(raw, fbx, bone_map)
            mesh = import_fbx(fbx, MESH_DIR, name, skeleton)
            # restore the original material slots, pointing at the plugin copies
            src_mats = src.get_editor_property("materials")
            mats = mesh.get_editor_property("materials")
            for i, m in enumerate(mats):
                if i < len(src_mats):
                    new = material_map(src_mats[i].material_interface)
                    m.material_interface = new or src_mats[i].material_interface
                    m.material_slot_name = src_mats[i].material_slot_name
            mesh.set_editor_property("materials", mats)
            EAL.save_loaded_asset(mesh, only_if_is_dirty=False)
            print(f"imported {name} (skeleton {mesh.skeleton.get_path_name()})")
        if skeleton is None:
            skeleton = mesh.skeleton
        meshes.append(mesh)
    return meshes


# ------------------------------------------------------------------------------------- bone map
def _global_positions(mesh):
    mod = unreal.SkeletonModifier()
    mod.set_skeletal_mesh(mesh)
    return {str(n): mod.get_bone_transform(n, True).translation for n in mod.get_all_bone_names()}


def _fraction(p, a, b):
    ab = b - a
    denom = ab.dot(ab)
    return (p - a).dot(ab) / denom if denom > 1e-6 else 0.0


def compute_bone_map(anatomy_mesh, metahuman_mesh, verbose=True):
    """Return {anatomy_bone: metahuman_bone} for every anatomy bone that needs renaming."""
    a_pos = _global_positions(anatomy_mesh)
    m_pos = _global_positions(metahuman_mesh)
    result = {}
    for side in ("l", "r"):
        for a, m in CORE_MAP.items():
            a, m = a.format(s=side), m.format(s=side)
            if a in a_pos and m in m_pos and a != m:
                result[a] = m
        for a_par, a_child, a_tw, m_par, m_child, m_tw in TWIST_GROUPS:
            a_par, a_child, m_par, m_child = (x.format(s=side) for x in (a_par, a_child, m_par, m_child))
            a_tw = [x.format(s=side) for x in a_tw if x.format(s=side) in a_pos]
            m_tw = [x.format(s=side) for x in m_tw if x.format(s=side) in m_pos]
            if not (a_tw and m_tw and all(b in a_pos for b in (a_par, a_child))
                    and all(b in m_pos for b in (m_par, m_child))):
                continue
            ta = {x: _fraction(a_pos[x], a_pos[a_par], a_pos[a_child]) for x in a_tw}
            tm = {x: _fraction(m_pos[x], m_pos[m_par], m_pos[m_child]) for x in m_tw}
            used_a, used_m = set(), set()
            for _, x, y in sorted((abs(ta[x] - tm[y]), x, y) for x in ta for y in tm):
                if x in used_a or y in used_m:
                    continue
                used_a.add(x)
                used_m.add(y)
                result[x] = y
                if verbose:
                    print(f"  twist {x} (t={ta[x]:.2f}) -> {y} (t={tm[y]:.2f})")
    clash = set(result.values()) & (set(a_pos) - set(result))
    if clash:
        raise RuntimeError(f"rename would clash with existing anatomy bones: {sorted(clash)}")
    return result


def rename_bones(mesh, bone_map):
    mod = unreal.SkeletonModifier()
    mod.set_skeletal_mesh(mesh)
    existing = {str(n) for n in mod.get_all_bone_names()}
    todo = {a: m for a, m in bone_map.items() if a in existing}
    if not todo:
        print(f"{mesh.get_name()}: already renamed")
        return 0
    if not mod.rename_bones(list(todo.keys()), list(todo.values())):
        raise RuntimeError(f"rename_bones failed on {mesh.get_name()}")
    if not mod.commit_skeleton_to_skeletal_mesh():
        raise RuntimeError(f"commit failed on {mesh.get_name()}")
    EAL.save_loaded_asset(mesh, only_if_is_dirty=False)
    print(f"{mesh.get_name()}: renamed {len(todo)} bones")
    return len(todo)


# ---------------------------------------------------------------------------------------- build
def build_all(metahuman_body=DEFAULT_METAHUMAN_BODY, overwrite=False):
    material_map = copy_materials(overwrite=overwrite)
    bone_map = compute_bone_map(unreal.load_asset(MESH_SOURCES[0][0]), unreal.load_asset(metahuman_body))
    meshes = import_meshes(material_map, bone_map, overwrite=overwrite)
    for mesh in meshes:
        names = {str(n) for n in unreal.SkeletonModifier.get_all_bone_names(_modifier_for(mesh))}
        leftover = sorted(set(bone_map) & names)
        if leftover:
            raise RuntimeError(f"{mesh.get_name()} still has anatomical names: {leftover}")
    return bone_map


def _modifier_for(mesh):
    mod = unreal.SkeletonModifier()
    mod.set_skeletal_mesh(mesh)
    return mod


# ------------------------------------------------------------------------------------ blueprint
def wire_blueprint(bp_path, layers=None, body_name="Body"):
    """Point anatomy components at the plugin meshes, parent them to Body and let Leader Pose drive them.

    layers: {component variable name: mesh path}. Missing components are created under Body.
    The stock MetaHuman construction script (EnableMasterPose on Body's children) sets Leader Pose.
    """
    layers = layers or {"MuscleMesh": ANATOMY_MESHES[0], "SkeletonMesh": ANATOMY_MESHES[1]}
    bp = unreal.load_asset(bp_path)
    sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    lib = unreal.SubobjectDataBlueprintFunctionLibrary

    def handles():
        out = {}
        for h in sds.k2_gather_subobject_data_for_blueprint(bp):
            data = sds.k2_find_subobject_data_from_handle(h)
            out[str(lib.get_variable_name(data))] = (h, lib.get_object(data))
        return out

    hs = handles()
    if body_name not in hs:
        raise RuntimeError(f"{bp_path} has no component named {body_name}")
    body_h = hs[body_name][0]
    for comp_name, mesh_path in layers.items():
        if comp_name not in hs:
            params = unreal.AddNewSubobjectParams(parent_handle=body_h, new_class=unreal.SkeletalMeshComponent,
                                                  blueprint_context=bp)
            new_h, fail = sds.add_new_subobject(params)
            if not fail.is_empty():
                raise RuntimeError(f"add component failed: {fail}")
            sds.rename_subobject(new_h, unreal.Text(comp_name))
            hs = handles()
        sds.attach_subobject(body_h, hs[comp_name][0])
        comp = handles()[comp_name][1]
        comp.set_editor_property("skeletal_mesh_asset", unreal.load_asset(mesh_path))
        comp.set_editor_property("anim_class", None)
        comp.set_editor_property("use_bounds_from_leader_pose_component", True)
        comp.set_editor_property("relative_location", unreal.Vector(0, 0, 0))
        comp.set_editor_property("relative_rotation", unreal.Rotator(0, 0, 0))
        comp.set_editor_property("relative_scale3d", unreal.Vector(1, 1, 1))
        print(f"{comp_name}: {mesh_path} under {body_name}")
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    EAL.save_loaded_asset(bp, only_if_is_dirty=False)
    return True
