# Job 36: wire the slider work into the project assets.
#  - BP_MH_CH_Abby8: AnatomyView component (via the plugin's wire_blueprint), Body Anim Class = ABP_Abby_Timeline
#  - BP_PlayerController: SwitchablePawnClasses = [BP_MH_CH_Abby8, BP_SkeletonModel]
#  - BP_SpeedSlider: MaxSpeed 100 -> 1 (the Anim BP expects 0..1)
import importlib
import unreal

from anatomy_layers import build
importlib.reload(build)

EAL = unreal.EditorAssetLibrary
SDS = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
LIB = unreal.SubobjectDataBlueprintFunctionLibrary
ABBY = "/Game/MetaHumans/MH_CH_Abby5/BP_MH_CH_Abby8"

# 1) anatomy layers + AnatomyView component
build.wire_blueprint(ABBY)

# 2) Body runs the timeline-driven locomotion Anim BP
bp = unreal.load_asset(ABBY)
abp_class = unreal.load_asset("/Game/Abby_Animation/Enhanced/ABP_Abby_Timeline").generated_class()
for h in SDS.k2_gather_subobject_data_for_blueprint(bp):
    data = SDS.k2_find_subobject_data_from_handle(h)
    obj = LIB.get_object(data)
    name = str(LIB.get_variable_name(data))
    if name == "Body":
        obj.set_editor_property("anim_class", abp_class)
        print("Body anim class ->", obj.get_editor_property("anim_class").get_name())
    if isinstance(obj, unreal.AnatomyViewComp):
        print("AnatomyView layers:", [(str(l.layer_name), [str(k) for k in l.component_names_or_tags]) for l in obj.get_editor_property("layers")])
    if isinstance(obj, unreal.AnimationTimelineComp):
        print("Timeline: mode", obj.get_editor_property("drive_mode"), "clip", obj.get_editor_property("animation_sequence").get_name())
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
EAL.save_loaded_asset(bp, only_if_is_dirty=False)

# 3) pawns the Up / Down buttons cycle through
pc_bp = unreal.load_asset("/Game/Blueprints/BP_PlayerController")
pc = unreal.get_default_object(pc_bp.generated_class())
pc.set_editor_property("switchable_pawn_classes", [
    bp.generated_class(),
    unreal.load_asset("/Game/Blueprints/BP_SkeletonModel").generated_class(),
])
print("SwitchablePawnClasses:", [c.get_name() for c in pc.get_editor_property("switchable_pawn_classes")])
print("Widgets:", pc.get_editor_property("speed_slider_widget").get_name(), pc.get_editor_property("timeline_widget_class").get_name(),
      pc.get_editor_property("anatomy_view_switcher_widget_class").get_name(), pc.get_editor_property("pawn_switcher_widget_class").get_name())
unreal.BlueprintEditorLibrary.compile_blueprint(pc_bp)
EAL.save_loaded_asset(pc_bp, only_if_is_dirty=False)

# 4) speed slider range 0..1
ss_bp = unreal.load_asset("/Game/Blueprints/BP_SpeedSlider")
ss = unreal.get_default_object(ss_bp.generated_class())
ss.set_editor_property("max_speed", 1.0)
unreal.BlueprintEditorLibrary.compile_blueprint(ss_bp)
EAL.save_loaded_asset(ss_bp, only_if_is_dirty=False)
print("SpeedSlider MaxSpeed:", ss.get_editor_property("max_speed"))

# 5) the widget Blueprints recompile against the new C++ parents
for w in ["/Game/Widget/WB_AmationTimeline", "/Game/Widget/WB_AnatomyViewSwitcher", "/Game/Widget/WB_PawnSwitcher"]:
    wb = unreal.load_asset(w)
    unreal.BlueprintEditorLibrary.compile_blueprint(wb)
    EAL.save_loaded_asset(wb, only_if_is_dirty=False)
    print("compiled", w)
