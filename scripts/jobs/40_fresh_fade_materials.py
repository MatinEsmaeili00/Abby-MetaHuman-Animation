# Job 40: masking added to the Emil-derived muscle/bone materials never clipped (even a constant-0 Opacity Mask
# on a duplicate), while a material built from scratch clips fine. So:
#  - put M_Anatomy_Muscle / M_Anatomy_BlockColour back to Opaque (as they came from the Emil example),
#  - build M_Anatomy_MuscleFade from scratch (muscle red + tendon mask + dithered Fade), used only while fading,
#  - M_Anatomy_Hidden gets the hair-strands usage flag (it also lands on facial-hair groom slots).
import importlib
import unreal
from anatomy_layers import build
importlib.reload(build)

EAL = unreal.EditorAssetLibrary
MEL = unreal.MaterialEditingLibrary
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(), "stop PIE first"

for p in ["/MetaHumanAnatomyLayers/Anatomy/Materials/M_Anatomy_Muscle", "/MetaHumanAnatomyLayers/Anatomy/Materials/M_Anatomy_BlockColour"]:
    m = unreal.load_asset(p)
    m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_OPAQUE)
    MEL.recompile_material(m)
    print(p.split("/")[-1], "->", m.get_editor_property("blend_mode"), "saved", EAL.save_loaded_asset(m, only_if_is_dirty=False))

hidden = build.create_hidden_material()
print("hidden: hair strands usage", hidden.get_editor_property("used_with_hair_strands"))

fade = build.create_muscle_fade_material(overwrite=False)
orig = unreal.load_asset("/MetaHumanAnatomyLayers/Anatomy/Materials/M_Anatomy_Muscle")
# match the original's colours (its muscle colour is multiplied by ~8.5 by a depth texture term)
mc = MEL.get_material_default_vector_parameter_value(orig, "muscle_COLOR")
tc = MEL.get_material_default_vector_parameter_value(orig, "Tendons_COLOR")
for e in MEL.get_material_expressions(fade):
    if isinstance(e, unreal.MaterialExpressionVectorParameter):
        n = str(e.get_editor_property("parameter_name"))
        if n == "muscle_COLOR":
            e.set_editor_property("default_value", unreal.LinearColor(min(mc.r * 8.5, 1), min(mc.g * 8.5, 1), min(mc.b * 8.5, 1), 1))
        elif n == "Tendons_COLOR":
            e.set_editor_property("default_value", unreal.LinearColor(tc.r, tc.g, tc.b, 1))
MEL.recompile_material(fade)
print("muscle fade:", fade.get_path_name(), "saved", EAL.save_loaded_asset(fade, only_if_is_dirty=False),
      "colors", MEL.get_material_default_vector_parameter_value(fade, "muscle_COLOR"), MEL.get_material_default_vector_parameter_value(fade, "Tendons_COLOR"))
