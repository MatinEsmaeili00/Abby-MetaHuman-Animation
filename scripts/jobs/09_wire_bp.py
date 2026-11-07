import os, stat, sys, importlib, unreal
p = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_plugins_dir()) + "MetaHumanAnatomyLayers/Content/Python"
if p not in sys.path: sys.path.insert(0, p)
import anatomy_layers.build as b; importlib.reload(b)
BP = "/Game/MetaHumans/MH_CH_Abby5/BP_MH_CH_Abby8"
f = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_content_dir()) + "MetaHumans/MH_CH_Abby5/BP_MH_CH_Abby8.uasset"
sc = unreal.SourceControl
print("source control enabled", sc.is_enabled(), "available", sc.is_available())
if sc.is_enabled() and sc.is_available():
    st = sc.query_file_state(f)
    print("p4 state: controlled", st.is_source_controlled, "checked out", st.is_checked_out, "can checkout", st.can_check_out)
    if st.is_source_controlled and not st.is_checked_out and st.can_check_out:
        print("checkout", sc.check_out_file(f))
if not os.access(f, os.W_OK):
    os.chmod(f, os.stat(f).st_mode | stat.S_IWUSR)
    print("made writable (run 'p4 reconcile' later to open it for edit)")
b.wire_blueprint(BP)
sds = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
lib = unreal.SubobjectDataBlueprintFunctionLibrary
bp = unreal.load_asset(BP)
for h in sds.k2_gather_subobject_data_for_blueprint(bp):
    d = sds.k2_find_subobject_data_from_handle(h)
    o = lib.get_object(d)
    if isinstance(o, unreal.SkeletalMeshComponent):
        par = lib.get_object(sds.k2_find_subobject_data_from_handle(lib.get_parent_handle(d))) if lib.get_parent_handle(d) else None
        print(str(lib.get_variable_name(d)), "mesh", o.skeletal_mesh_asset.get_name() if o.skeletal_mesh_asset else None,
              "parent", par.get_name() if par else None, "tags", [str(t) for t in o.component_tags])
