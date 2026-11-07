# Job 38: linear dither (clip 0.5) on the plugin's Fade materials + the x-ray ghost material.
# (Re-run: the first attempt saved while PIE was running, which Unreal silently refuses.)
import importlib
import unreal
from anatomy_layers import build
importlib.reload(build)

EAL = unreal.EditorAssetLibrary
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(), "stop PIE first: saving is blocked during PIE"
for p in build.FADE_MATERIALS:
    m = unreal.load_asset(p)
    m.set_editor_property("opacity_mask_clip_value", 0.5)
    unreal.MaterialEditingLibrary.recompile_material(m)
    print(p.split("/")[-1], "clip", m.get_editor_property("opacity_mask_clip_value"), "saved", EAL.save_loaded_asset(m, only_if_is_dirty=False))
x = build.create_xray_material()
print(x.get_path_name(), "saved", EAL.save_loaded_asset(x, only_if_is_dirty=False))
