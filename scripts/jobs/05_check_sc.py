import unreal
sc = unreal.SourceControl
print("enabled", sc.is_enabled(), "available", sc.is_available(), "provider", sc.current_provider())
f = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_content_dir()) + "MetaHumans/MH_CH_Abby5/BP_MH_CH_Abby8.uasset"
st = sc.query_file_state(f)
for k in ["is_valid","is_unknown","can_check_in","can_check_out","is_checked_out","is_current","is_source_controlled","is_added","is_deleted","is_ignored","can_edit","is_modified","checked_out_other"]:
    try: print(k, st.get_editor_property(k))
    except Exception as e: pass
