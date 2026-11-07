# Job 32: what does the MetaHuman "Fade" scalar do? Trace it to the material output it drives.
import unreal

MEL = unreal.MaterialEditingLibrary
MATS = [
    "/Game/MetaHumans/Common/Lookdev_UHM/Skin/Materials/M_skin_unified_baked",
    "/Game/MetaHumans/Common/Materials/M_hair_v4",
    "/Game/MetaHumans/Common/Materials/M_Facial_Hair",
]
PROPS = [unreal.MaterialProperty.MP_OPACITY_MASK, unreal.MaterialProperty.MP_OPACITY,
         unreal.MaterialProperty.MP_BASE_COLOR]


def describe(e):
    n = e.get_class().get_name()
    extra = ""
    for p in ("parameter_name", "input_name", "function"):
        try:
            v = e.get_editor_property(p)
            extra += f" {p}={v.get_name() if hasattr(v, 'get_name') else v}"
        except Exception:
            pass
    return n + extra


def walk(e, depth=0, maxd=7, seen=None):
    seen = seen if seen is not None else set()
    if e is None or depth > maxd:
        return
    key = e.get_path_name()
    print("  " * depth + describe(e) + (" (seen)" if key in seen else ""))
    if key in seen:
        return
    seen.add(key)
    for i in MEL.get_inputs_for_material_expression(unreal.load_asset(MAT), e) if False else []:
        pass
    try:
        ins = MEL.get_inputs_for_material_expression(mat, e)
    except Exception as ex:
        ins = []
    for i in ins:
        walk(i, depth + 1, maxd, seen)


for MAT in MATS:
    mat = unreal.load_asset(MAT)
    print("=====", MAT, "blend:", mat.get_editor_property("blend_mode"),
          "dither_opacity_mask:", mat.get_editor_property("dither_opacity_mask") if hasattr(mat, "dither_opacity_mask") else "?")
    for prop in PROPS[:2]:
        node = MEL.get_material_property_input_node(mat, prop)
        print(" --", prop)
        walk(node)
    # scalar default
    try:
        print(" Fade default:", MEL.get_material_default_scalar_parameter_value(mat, "Fade"))
    except Exception as ex:
        print(" no Fade default", ex)
