# Job 57: AnatomyPicker on Abby8 (via the plugin's wire_blueprint) + WB_MuscleInfo on the controller.
import importlib
import unreal
from anatomy_layers import build
importlib.reload(build)
EAL = unreal.EditorAssetLibrary
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(), "stop PIE first"

build.wire_blueprint("/Game/MetaHumans/MH_CH_Abby5/BP_MH_CH_Abby8")

pc_bp = unreal.load_asset("/Game/Blueprints/BP_PlayerController")
pc = unreal.get_default_object(pc_bp.generated_class())
pc.set_editor_property("muscle_info_widget_class", unreal.load_asset("/Game/Widget/WB_MuscleInfo").generated_class())
unreal.BlueprintEditorLibrary.compile_blueprint(pc_bp)
print("controller muscle widget:", pc.get_editor_property("muscle_info_widget_class").get_name(), "saved", EAL.save_loaded_asset(pc_bp, only_if_is_dirty=False))
