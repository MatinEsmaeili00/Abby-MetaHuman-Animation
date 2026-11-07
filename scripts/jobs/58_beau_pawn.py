# Job 58: make Beau (assembled from /Game/MadisonTesting/BeauMHCharacter/MHC_Beau) a second switchable person.
#  - BP_Beau_Pawn: copy of the assembled BP_Beau (kept outside "Unpacked" so a re-assembly doesn't overwrite it),
#    reparented to ACPP_AbbyCharacter (a Pawn with Speed), plus spring arm + camera, mouse / timeline components,
#    anatomy layers + Anatomy View + Anatomy Picker (plugin wire_blueprint)
#  - walk / jog / run retargeted onto his body with the same "Upright" retarget pose, foot-sync markers copied
#  - ABP_Beau_Timeline (parent UCPP_LocomotionAnimInstance, metahuman_base_skel); AnimGraph is built through MCP
#  - controller: SwitchablePawnClasses = [Abby8, Beau, SkeletonModel]
import importlib
import unreal
from anatomy_layers import build
importlib.reload(build)

EAL = unreal.EditorAssetLibrary
AL = unreal.AnimationLibrary
SDS = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
LIB = unreal.SubobjectDataBlueprintFunctionLibrary
ROOT = "/Game/MadisonTesting/BeauMHCharacter"
SRC_BP = ROOT + "/Unpacked/Beau/BP_Beau"
BP = ROOT + "/BP_Beau_Pawn"
BODY = ROOT + "/Unpacked/Beau/Body/SKM_MHC_Beau_BodyMesh"
ANIM_DIR = ROOT + "/Animation"
assert not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world(), "stop PIE first"

# 1) pawn blueprint
if not EAL.does_asset_exist(BP):
    EAL.duplicate_asset(SRC_BP, BP)
bp = unreal.load_asset(BP)
if not isinstance(unreal.get_default_object(bp.generated_class()), unreal.CPP_AbbyCharacter):
    unreal.BlueprintEditorLibrary.reparent_blueprint(bp, unreal.CPP_AbbyCharacter)
print("BP_Beau_Pawn parent:", [c.__name__ for c in type(unreal.get_default_object(bp.generated_class())).__mro__[:3]])


def handles():
    out = {}
    for h in SDS.k2_gather_subobject_data_for_blueprint(bp):
        d = SDS.k2_find_subobject_data_from_handle(h)
        out[str(LIB.get_variable_name(d))] = (h, LIB.get_object(d))
    return out


def add(name, cls, parent_name=None):
    hs = handles()
    if name in hs:
        return hs[name][1]
    parent = hs[parent_name][0] if parent_name else SDS.k2_gather_subobject_data_for_blueprint(bp)[0]
    new_h, fail = SDS.add_new_subobject(unreal.AddNewSubobjectParams(parent_handle=parent, new_class=cls, blueprint_context=bp))
    if not fail.is_empty():
        raise RuntimeError(f"add {name}: {fail}")
    SDS.rename_subobject(new_h, unreal.Text(name))
    return handles()[name][1]


arm = add("SpringArm", unreal.SpringArmComponent, "Root")
arm.set_editor_property("target_arm_length", 260.0)
arm.set_editor_property("relative_location", unreal.Vector(0, 0, 105))
arm.set_editor_property("relative_rotation", unreal.Rotator(roll=0.0, pitch=-5.0, yaw=-90.0))
arm.set_editor_property("do_collision_test", False)
add("Camera", unreal.CameraComponent, "SpringArm")
add("CPP_MouseFunctionComp", unreal.CPP_MouseFunctionComp)
add("AnimationTimelineComp", unreal.AnimationTimelineComp)
unreal.BlueprintEditorLibrary.compile_blueprint(bp)
EAL.save_loaded_asset(bp, only_if_is_dirty=False)

# anatomy layers + Anatomy View + Anatomy Picker
build.wire_blueprint(BP)

# 2) clips on Beau's skeleton (same retargeter / Upright pose as Abby)
rtg = unreal.load_asset("/Game/Abby_Animation/Posture/RTG_Mixamo_To_Abby_Posture")
ctl = unreal.IKRetargeterController.get_controller(rtg)
ctl.set_current_retarget_pose("Upright", unreal.RetargetSourceOrTarget.TARGET)
if not EAL.does_directory_exist(ANIM_DIR):
    EAL.make_directory(ANIM_DIR)
inputs = unreal.IKRetargetBatchOperationInputs()
inputs.assets_to_retarget = [EAL.find_asset_data(p) for p in ["/Game/Animation2/Walking_Anim", "/Game/Animation2/Jogging", "/Game/Animation2/Running__2_"]]
inputs.source_mesh = unreal.load_asset("/Game/Animation2/Walking")
inputs.target_mesh = unreal.load_asset(BODY)
inputs.ik_retarget_asset = rtg
inputs.target_path = ANIM_DIR
inputs.use_source_path = False
inputs.prefix = "Beau_"
inputs.suffix = "_Upright"
inputs.include_referenced_assets = False
inputs.overwrite_existing_files = True
clips = sorted(str(a.package_name) for a in unreal.IKRetargetBatchOperation.run_batch_retarget(inputs))
P = "/Game/Abby_Animation/Posture/"
for new_path, old_path in zip(clips, [P + "Abby_Jogging_Upright", P + "Abby_Running__2__Upright", P + "Abby_Walking_Anim_Upright"]):
    new, old = unreal.load_asset(new_path), unreal.load_asset(old_path)
    if "FootSync" not in [str(n) for n in AL.get_animation_notify_track_names(new)]:
        AL.add_animation_notify_track(new, "FootSync")
    if not AL.get_animation_sync_markers(new):
        for m in AL.get_animation_sync_markers(old):
            AL.add_animation_sync_marker(new, m.marker_name, m.time, "FootSync")
    print(new_path.split("/")[-1], "skeleton", new.get_editor_property("skeleton").get_name(), "markers", len(AL.get_animation_sync_markers(new)),
          "saved", EAL.save_loaded_asset(new, only_if_is_dirty=False))

# 3) Anim BP for Beau (graph built through MCP afterwards)
ABP = ANIM_DIR + "/ABP_Beau_Timeline"
body = unreal.load_asset(BODY)
if not EAL.does_asset_exist(ABP):
    f = unreal.AnimBlueprintFactory()
    f.set_editor_property("target_skeleton", body.skeleton)
    f.set_editor_property("parent_class", unreal.CPP_LocomotionAnimInstance)
    f.set_editor_property("preview_skeletal_mesh", body)
    unreal.AssetToolsHelpers.get_asset_tools().create_asset("ABP_Beau_Timeline", ANIM_DIR, unreal.AnimBlueprint, f)
abp = unreal.load_asset(ABP)
unreal.BlueprintEditorLibrary.compile_blueprint(abp)
cdo = unreal.get_default_object(abp.generated_class())
by_gait = {("Walking" if "Walking" in c else "Jogging" if "Jogging" in c else "Running"): unreal.load_asset(c) for c in clips}
cdo.set_editor_property("walk_anim", by_gait["Walking"])
cdo.set_editor_property("jog_anim", by_gait["Jogging"])
cdo.set_editor_property("run_anim", by_gait["Running"])
print("ABP:", abp.get_path_name(), "saved", EAL.save_loaded_asset(abp, only_if_is_dirty=False))
print("clips:", clips)
