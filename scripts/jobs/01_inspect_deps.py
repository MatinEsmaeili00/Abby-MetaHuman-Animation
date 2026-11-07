import unreal, os
ar = unreal.AssetRegistryHelpers.get_asset_registry()
opts = unreal.AssetRegistryDependencyOptions(include_soft_package_references=True, include_hard_package_references=True, include_searchable_names=False, include_soft_management_references=False, include_hard_management_references=False)
roots = ["/Game/ExampleContent/5_5_ChaosFlesh/Characters/Emil/Meshes/SKM_Emil_upperBodyMuscles",
         "/Game/ExampleContent/5_5_ChaosFlesh/Characters/Emil/Meshes/SKM_skeleton_upper_body"]
seen, stack = set(), list(roots)
while stack:
    p = stack.pop()
    if p in seen: continue
    seen.add(p)
    for d in ar.get_dependencies(p, opts) or []:
        d = str(d)
        if d.startswith("/Game/"):
            stack.append(d)
proj = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_content_dir())
for p in sorted(seen):
    f = os.path.join(proj, p[len("/Game/"):] + ".uasset")
    sz = os.path.getsize(f) if os.path.exists(f) else -1
    cls = unreal.EditorAssetLibrary.find_asset_data(p).asset_class_path.asset_name
    print(f"{p}  [{cls}]  {sz/1e6:.2f} MB")
for r in roots:
    m = unreal.load_asset(r)
    print(r.split('/')[-1], "skeleton:", m.skeleton.get_path_name(), "phys:", m.physics_asset.get_path_name() if m.physics_asset else None)
    for i, sm in enumerate(m.materials):
        print("   slot", i, sm.material_slot_name, sm.material_interface.get_path_name() if sm.material_interface else None)
