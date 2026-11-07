# Job 33: quick look test of the MetaHuman "Fade" (dither) parameter on the placed Abby8 in the editor world.
# FADE is substituted before running. Nothing is saved; reset with FADE = 1.
import unreal

FADE = __FADE__
LEVEL_ACTORS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
abby = [a for a in LEVEL_ACTORS if a.get_class().get_name() == "BP_MH_CH_Abby8_C"][0]
print("actor:", abby.get_actor_label(), abby.get_actor_location())

for comp in abby.get_components_by_class(unreal.PrimitiveComponent):
    name = comp.get_name()
    if name in ("MuscleMesh", "SkeletonMesh"):
        comp.set_visibility(FADE < 1.0)
        continue
    if not (isinstance(comp, unreal.SkeletalMeshComponent) or comp.get_class().get_name() == "GroomComponent"):
        continue
    n = comp.get_num_materials()
    changed = 0
    for i in range(n):
        if FADE >= 1.0:
            continue
        mid = comp.create_dynamic_material_instance(i)
        if mid:
            mid.set_scalar_parameter_value("Fade", FADE)
            changed += 1
    if FADE >= 1.0 and isinstance(comp, unreal.MeshComponent):
        comp.set_editor_property("override_materials", [])
    print(name, "materials:", n, "faded:", changed)

# frame the camera on her
loc = abby.get_actor_location()
cam = unreal.Vector(loc.x + 260, loc.y + 0, loc.z + 120)
rot = unreal.MathLibrary.find_look_at_rotation(cam, unreal.Vector(loc.x, loc.y, loc.z + 100))
unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(cam, rot)
print("camera", cam, rot)
