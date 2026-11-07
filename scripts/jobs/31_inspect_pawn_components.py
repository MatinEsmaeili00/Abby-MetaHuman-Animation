# Job 31: list BP_MH_CH_Abby8 components (class, parent, tags, mesh, materials) and look for "Fade" params.
import unreal

EAL = unreal.EditorAssetLibrary
SDS = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
BP_PATH = "/Game/MetaHumans/MH_CH_Abby5/BP_MH_CH_Abby8"

bp = EAL.load_asset(BP_PATH)
handles = SDS.k2_gather_subobject_data_for_blueprint(bp)
seen_mats = {}
for h in handles:
    data = unreal.SubobjectDataBlueprintFunctionLibrary.get_data(h)
    obj = unreal.SubobjectDataBlueprintFunctionLibrary.get_object(data)
    if obj is None:
        continue
    name = unreal.SubobjectDataBlueprintFunctionLibrary.get_variable_name(data)
    parent = None
    if isinstance(obj, unreal.SceneComponent):
        ap = obj.get_attach_parent()
        parent = ap.get_name() if ap else None
    line = f"{name} [{obj.get_class().get_name()}] parent={parent}"
    try:
        tags = list(obj.get_editor_property("component_tags"))
        if tags:
            line += f" tags={[str(t) for t in tags]}"
    except Exception:
        pass
    if isinstance(obj, unreal.SkeletalMeshComponent):
        m = obj.get_editor_property("skeletal_mesh_asset")
        line += f" mesh={m.get_name() if m else None} anim_class={obj.get_editor_property('anim_class')} mode={obj.get_editor_property('animation_mode')}"
        if m:
            for i, sm in enumerate(m.get_editor_property("materials")):
                mi = sm.get_editor_property("material_interface")
                if mi:
                    seen_mats[mi.get_path_name()] = mi
                    line += f"\n      slot{i} {sm.get_editor_property('material_slot_name')}: {mi.get_name()}"
        ov = obj.get_editor_property("override_materials")
        if any(ov):
            line += f"\n      overrides: {[o.get_name() if o else None for o in ov]}"
    elif isinstance(obj, unreal.StaticMeshComponent):
        m = obj.get_editor_property("static_mesh")
        line += f" mesh={m.get_name() if m else None}"
    elif obj.get_class().get_name() == "GroomComponent":
        g = obj.get_editor_property("groom_asset")
        line += f" groom={g.get_name() if g else None}"
    elif isinstance(obj, unreal.SpringArmComponent):
        line += f" arm={obj.get_editor_property('target_arm_length')} rel={obj.get_editor_property('relative_location')} rot={obj.get_editor_property('relative_rotation')}"
    print(line)

print("\n=== material parents + Fade-like params")
for path, mi in seen_mats.items():
    base = mi
    chain = [mi.get_name()]
    while isinstance(base, unreal.MaterialInstance):
        base = base.get_editor_property("parent")
        chain.append(base.get_name() if base else None)
    names = []
    try:
        names = [str(n) for n in unreal.MaterialEditingLibrary.get_scalar_parameter_names(mi)]
    except Exception:
        pass
    tex = []
    try:
        tex = [str(n) for n in unreal.MaterialEditingLibrary.get_texture_parameter_names(mi)]
    except Exception:
        pass
    blend = base.get_editor_property("blend_mode") if isinstance(base, unreal.Material) else None
    print(" -> ".join(chain), "| blend:", blend)
    fades = [n for n in names if "fade" in n.lower() or "opac" in n.lower()]
    print("     fade/opacity scalars:", fades)
    print("     textures:", tex[:12])
