# Job 61: PIE test of the muscle picker: aim a ray from the camera at a muscle's sample points, hover, then select.
import unreal
KEY = "__KEY__"
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
pc = unreal.GameplayStatics.get_player_controller(world, 0)
pawn = pc.get_controlled_pawn()
picker = pawn.get_component_by_class(unreal.AnatomyPickerComp)
atlas = unreal.load_asset("/MetaHumanAnatomyLayers/Anatomy/Data/DA_MuscleAtlas_UpperBody")
mm = [c for c in pawn.get_components_by_class(unreal.SkeletalMeshComponent) if c.get_name() == "MuscleMesh"][0]
info = [m for m in atlas.get_editor_property("muscles") if str(m.key) == KEY][0]
pts = [mm.get_bone_transform(s.bone).transform_location(s.offset) for s in info.samples]
c = unreal.Vector(sum(p.x for p in pts) / len(pts), sum(p.y for p in pts) / len(pts), sum(p.z for p in pts) / len(pts))
# nearest sample to the centroid = a point on the muscle surface
target = min(pts, key=lambda p: (p - c).length())
cam = unreal.GameplayStatics.get_player_camera_manager(world, 0).get_camera_location()
print("picking active:", picker.is_picking_active(), "| target", KEY, "id", info.id)
picker.update_hover(cam, (target - cam).normal())
hl = [c for c in pawn.get_components_by_class(unreal.SkeletalMeshComponent) if c.get_name() == "MuscleHighlight"]
print("hovered:", picker.get_hovered_muscle(), "| highlight copy visible:", hl[0].is_visible() if hl else None)
ok = picker.select_hovered()
ok_info = picker.get_muscle_info(picker.get_selected_muscle())
print("selected:", picker.get_selected_muscle(), ok, ok_info)
