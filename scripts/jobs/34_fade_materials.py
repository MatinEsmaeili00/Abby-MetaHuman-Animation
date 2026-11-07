# Job 34: give the plugin's anatomy materials the same "Fade" (1 = visible, 0 = gone) dither parameter the
# MetaHuman skin/eye/teeth/hair materials already have, and add an always-invisible M_Anatomy_Hidden.
import unreal

MEL = unreal.MaterialEditingLibrary
EAL = unreal.EditorAssetLibrary
MATS = "/MetaHumanAnatomyLayers/Anatomy/Materials"
DITHER = "/Engine/Functions/Engine_MaterialFunctions02/Utility/DitherTemporalAA"

dither_fn = unreal.load_asset(DITHER)
print("dither fn:", dither_fn)


def has_fade(mat):
    return "Fade" in [str(n) for n in MEL.get_scalar_parameter_names(mat)]


def add_fade(path):
    mat = unreal.load_asset(path)
    if has_fade(mat):
        print(path, "already has Fade")
        return
    mat.set_editor_property("blend_mode", unreal.BlendMode.BLEND_MASKED)
    p = MEL.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -700, 700)
    p.set_editor_property("parameter_name", "Fade")
    p.set_editor_property("default_value", 1.0)
    p.set_editor_property("group", "Anatomy")
    d = MEL.create_material_expression(mat, unreal.MaterialExpressionMaterialFunctionCall, -450, 700)
    d.set_material_function(dither_fn)
    ok1 = MEL.connect_material_expressions(p, "", d, "Alpha Threshold")
    ok2 = MEL.connect_material_property(d, "", unreal.MaterialProperty.MP_OPACITY_MASK)
    MEL.recompile_material(mat)
    EAL.save_loaded_asset(mat, only_if_is_dirty=False)
    print(path, "-> masked + Fade", ok1, ok2, "params:", [str(n) for n in MEL.get_scalar_parameter_names(mat)])


add_fade(f"{MATS}/M_Anatomy_Muscle")
add_fade(f"{MATS}/M_Anatomy_BlockColour")

# Invisible material used for slots that have no Fade/Opacity parameter (e.g. the MetaHuman eye occlusion shell)
HID = f"{MATS}/M_Anatomy_Hidden"
if not EAL.does_asset_exist(HID):
    mat = unreal.AssetToolsHelpers.get_asset_tools().create_asset("M_Anatomy_Hidden", MATS, unreal.Material, unreal.MaterialFactoryNew())
    mat.set_editor_property("blend_mode", unreal.BlendMode.BLEND_MASKED)
    c = MEL.create_material_expression(mat, unreal.MaterialExpressionConstant, -300, 200)
    c.set_editor_property("r", 0.0)
    MEL.connect_material_property(c, "", unreal.MaterialProperty.MP_OPACITY_MASK)
    mat.set_editor_property("two_sided", True)
    mat.set_editor_property("used_with_skeletal_mesh", True)
    MEL.recompile_material(mat)
    EAL.save_loaded_asset(mat, only_if_is_dirty=False)
    print("created", HID)
else:
    print(HID, "exists")

# make sure the masked versions are flagged for skinned meshes
for path in (f"{MATS}/M_Anatomy_Muscle", f"{MATS}/M_Anatomy_BlockColour", HID):
    m = unreal.load_asset(path)
    print(path, "blend:", m.get_editor_property("blend_mode"), "skel:", m.get_editor_property("used_with_skeletal_mesh"))

# Is the editor-only UCPP_WBP_SpeedSlider class used by any asset?
ar = unreal.AssetRegistryHelpers.get_asset_registry()
f = unreal.ARFilter(class_paths=[unreal.TopLevelAssetPath("/Script/MetaHumanTest", "CPP_WBP_SpeedSlider")], recursive_classes=True)
print("assets of class CPP_WBP_SpeedSlider:", [str(a.package_name) for a in ar.get_assets(f)])
