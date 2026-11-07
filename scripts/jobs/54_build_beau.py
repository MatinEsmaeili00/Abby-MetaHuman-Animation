# Job 54: assemble Beau (MetaHuman Character in /Game/MadisonTesting) into a playable Blueprint.
import time
import unreal

S = unreal.get_editor_subsystem(unreal.MetaHumanCharacterEditorSubsystem)
mhc = unreal.load_asset("/Game/MadisonTesting/BeauMHCharacter/MHC_Beau")
print("open for edit:", S.try_add_object_to_edit(mhc), "| can build:", S.can_build_meta_human(mhc, True))
p = unreal.MetaHumanCharacterEditorBuildParameters()
p.set_editor_property("pipeline_type", unreal.MetaHumanDefaultPipelineType.CINEMATIC)
p.set_editor_property("name_override", "Beau")
t = time.time()
S.build_meta_human(mhc, p)
print("build finished in %.0fs" % (time.time() - t))
ar = unreal.AssetRegistryHelpers.get_asset_registry()
for folder in ["/Game/MetaHumans/Beau", "/Game/MadisonTesting"]:
    assets = unreal.EditorAssetLibrary.list_assets(folder, recursive=True)
    print(folder, len(assets), [a for a in assets if "BP_" in a or "Body" in a.split("/")[-1]][:20])
